from threading import Thread, Event
from datetime import datetime
from metrics.hardware_metrics import HardwareMetrics as hm
from metrics.promptmetrics import PromptMetrics as pm
from utils.ollama_utils import ollama_model_checker,ollamaClient
from utils.configuration import client_default_ollama as cdo 
from utils.configuration import TIME_BETWEEN_MODELS as tbm, TIME_BETWEEN_PROMPTS as tbp, OLLAMA_MODEL_LIST as oml, PROMPT_LIST as pl
import time


def main_ollama():
    #Comprobamos que los modelos existan y si no los descargamos
    ollama_model_checker(oml)
    # comprobamos que el laa lista de promptos no esté vacia
    if len(pl) == 0:
        print("The prompt list is empty, exiting the program")
        raise
    for model in oml:
        
        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
        prompt_metric_filepath =f"results/ollama_prompt_metrics_ollama_{current_time}_{model}.csv"
        hardware_metric_filepath =f"results/ollama_hardware_metrics_ollama_{current_time}_{model}.csv"
        pm.create_csv_file(prompt_metric_filepath)
        hm.create_csv_file(hardware_metric_filepath)
        oc = ollamaClient()
        
        for i in range (len(pl)):
           
            # de forma paralela alimentamos el prompts y medimos el hardware

            # en un hilo daemon guardo los resultados de la medicion del hardware
            # alimento el prompt en este hilo
           

            event = Event()
            prompt_thread = Thread(
                target=oc.ollama_query_and_save_with_event,
                args=(pl[i], model,prompt_metric_filepath,event,i)
            )
            hardware_thread = Thread(
                target= hm.update_and_save,
                args=(hardware_metric_filepath,event,i),
                daemon=True
            )
            prompt_thread.start()
            hardware_thread.start()
            prompt_thread.join()
            hardware_thread.join()
            if i == (len(pl)-1):
                #eliminamos el modelo de la memoria
                oc.unload_model(model)
                print("moddelo descargado de la memoria")
            time.sleep(tbp)
        time.sleep(tbm)
           
            
            

            
        
           


if __name__ == "__main__":
    main_ollama();



