from Metrics.VGENMetrics import *
from Metrics.mpstatMetrics import *
from Prompt_Lists.prompt_parser import *
from LLM_functions import *
import time
import threading
import csv
try:
    import ollama
except ImportError:
    print("The 'ollama' module is not installed. Please install it in a virtual environment.")
    print("To create a virtual environment, run:")
    print("  python3 -m venv /path/to/venv")
    print("Activate the virtual environment and install the module with:")
    print("  /path/to/venv/bin/pip install ollama")
    exit(1)

m = mpstatMetrics()
v = VCGENMetrics()
prompts = InstructionFollowingParser.get_prompts()

# Función para guardar mediciones en un archivo CSV
def save_metrics_to_csv():
    with open('metrics.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Metric_M', 'Metric_V'])  # Encabezados del CSV
        while True:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            m.update()
            v.update()
            writer.writerow([timestamp, str(m), str(v)])
            file.flush()  # Asegurarse de que los datos se escriban inmediatamente
            time.sleep(1)

# Función para alimentar los prompts a ollama
def feed_prompts_to_ollama():
    model="gemma3:1b"
    query_iterator(model, prompts[0:5])


# Crear y ejecutar los hilos
metrics_thread = threading.Thread(target=save_metrics_to_csv, daemon=True)
prompts_thread = threading.Thread(target=feed_prompts_to_ollama)

metrics_thread.start()
prompts_thread.start()

prompts_thread.join()  # Esperar a que termine el hilo de prompts
