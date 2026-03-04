# Ejecución paralela de medidas en C++

Este documento explica cómo trasladar el patrón de paralelismo que usa el proyecto
en Python (`threading.Thread` + `threading.Event`) a su equivalente en C++ moderno
(C++11/17/20).

---

## 1. El patrón que usa el proyecto en Python

Por cada prompt del bucle de test se lanzan **dos hilos en paralelo**:

| Hilo | Qué hace |
|------|----------|
| `prompt_thread` | Envía el prompt al modelo y guarda las métricas de respuesta |
| `hardware_thread` | Muestrea el hardware periódicamente mientras el modelo genera |

La sincronización entre ellos se hace con un **`threading.Event`**:

```python
evento = Event()

# El hilo de prompt activa el evento justo antes de llamar al modelo
# y lo desactiva cuando termina → hardware_thread sabe cuándo medir.
prompt_thread  = Thread(target=cliente.query_event_save,
                        args=(prompt, model_name, prompt_log, evento, i, -1))
hardware_thread = Thread(target=HardwareMetrics.update_and_save,
                         kwargs={'logger': hw_log, 'event': evento, ...})

hardware_thread.start()
prompt_thread.start()
prompt_thread.join()
hardware_thread.join()
```

El bucle de hardware (`update_and_save`) espera a que el evento esté activo y
luego muestrea hasta que se desactiva:

```python
def update_and_save(logger, event, ...):
    HardwareMetrics(...)      # muestra de "calentamiento"
    event.wait()              # espera a que el prompt empiece
    while event.is_set():
        HardwareMetrics(...).append_to_csv_file(logger)
        time.sleep(freq)
```

---

## 2. Equivalencias Python → C++

| Python | C++ |
|--------|-----|
| `threading.Thread(target=f, args=(...))` | `std::thread t(f, arg1, arg2, ...)` |
| `thread.start()` | El hilo arranca al construirse |
| `thread.join()` | `t.join()` |
| `threading.Event` | `std::atomic<bool>` |
| `event.set()` | `event.store(true)` |
| `event.clear()` | `event.store(false)` |
| `event.is_set()` | `event.load()` |
| `event.wait()` | spin-loop + `std::this_thread::sleep_for` |
| `time.sleep(freq)` | `std::this_thread::sleep_for(std::chrono::duration<float>(freq))` |
| Proteger el logger con GIL | `std::mutex` + `std::lock_guard` en cada escritura |

---

## 3. Estructura en C++

### 3.1 El "evento" → `std::atomic<bool>`

```cpp
#include <atomic>

std::atomic<bool> event{false};  // shared between both threads
```

`std::atomic<bool>` es lock-free, seguro para leer y escribir desde hilos
distintos sin necesidad de mutex adicional.

### 3.2 El hilo de hardware (`update_and_save`)

```cpp
#include <thread>
#include <chrono>
#include <atomic>

void updateAndSave(MetricLogger& logger,
                   std::atomic<bool>& event,
                   Engine mode, int promptId, float freqSec) {

    // Muestra de calentamiento (igual que en Python)
    HardwareMetrics warmup(mode, promptId);

    // Esperar a que el prompt empiece (equivale a event.wait())
    while (!event.load()) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    // Muestrear mientras el evento esté activo
    while (event.load()) {
        HardwareMetrics(mode, promptId).appendToCsvFile(logger);
        std::this_thread::sleep_for(
            std::chrono::duration<float>(freqSec));
    }
}
```

### 3.3 El hilo de prompt (`query_event_save`)

```cpp
void queryEventSave(const std::string& prompt,
                    const std::string& model,
                    MetricLogger& logger,
                    std::atomic<bool>& event,
                    int promptId) {

    // Activar el evento ANTES de llamar al modelo
    event.store(true);

    auto start  = std::chrono::high_resolution_clock::now();
    auto resp   = generate(prompt, model);           // llamada bloqueante
    auto finish = std::chrono::high_resolution_clock::now();

    // Desactivar el evento para que el hilo de hardware se detenga
    event.store(false);

    PromptMetrics::fromOllama(toNs(start), toNs(finish), resp, promptId)
        .appendToCsv(logger);
}
```

### 3.4 El bucle principal (equivalente al `for` en `test()`)

```cpp
#include <thread>

for (int i = 0; i < (int)promptList.size(); ++i) {
    std::atomic<bool> event{false};

    // Crear los dos hilos (arrancan inmediatamente al construirse)
    std::thread hwThread([&]() {
        updateAndSave(hwLog, event, Engine::OLLAMA, i, freq);
    });
    std::thread promptThread([&]() {
        queryEventSave(promptList[i], modelName, promptLog, event, i);
    });

    // Esperar a que ambos terminen
    promptThread.join();
    hwThread.join();

    // Pausa entre prompts
    if (i < (int)promptList.size() - 1) {
        std::this_thread::sleep_for(
            std::chrono::duration<float>(timeBetweenPrompts));
    }
}
```

---

## 4. Logger thread-safe

El logger necesita protección porque **ambos hilos escriben en el mismo fichero**.
En Python el GIL lo hace automáticamente; en C++ hay que añadir un `std::mutex`:

```cpp
class MetricLogger {
    std::ofstream m_file;
    std::mutex    m_mutex;
public:
    void info(const std::string& jsonLine) {
        std::lock_guard<std::mutex> lock(m_mutex);   // bloqueo automático
        m_file << jsonLine << "\n";
        m_file.flush();
    }
};
```

---

## 5. Resumen del flujo completo

```
main loop (prompt i)
│
├─► std::thread hwThread  ──────────────────────────────────────────►
│       spin-wait (event==false)                                      │
│       ←── event = true ─────────────────────────────────────────── │
│       sample → log  (cada freq segundos)                            │
│       sample → log                                                  │
│       ←── event = false ────────────────────────────────────────── │
│       termina                                                        │
│                                                                      │
└─► std::thread promptThread ─────────────────────────────────────►
        event.store(true)
        [genera respuesta del modelo  ← bloqueante]
        event.store(false)
        guarda PromptMetrics → log
        termina

main: promptThread.join() → hwThread.join() → siguiente prompt
```

---

## 6. Cabeceras necesarias

```cpp
#include <thread>       // std::thread
#include <atomic>       // std::atomic<bool>
#include <mutex>        // std::mutex, std::lock_guard
#include <chrono>       // std::chrono::*, std::this_thread::sleep_for
#include <functional>   // std::ref (para pasar referencias a hilos)
```

Compilar con al menos **C++11** (`-std=c++11`) y enlazar con `-lpthread` en Linux/Raspberry Pi.
