import threading
import time

from metrics.hardware_metrics import HardwareMetrics as hm
from metrics.promptmetrics import PromptMetrics as pm
from utils.ollama_utils import ollama_model_checker
from utils.prompt_parser import InstructionFollowingParser as ifps
OLLAMA_MODEL_LIST = ["llama3.2:latest"]
PROMPT_MODEL_LIST = ifps.get_instruc_eval_prompts()[0:2]


def main():
    #Comprobamos que los modelos existan y si no los descargamos
    ollama_model_checker(OLLAMA_MODEL_LIST)
    # comprobamos que el laa lista de promptos no esté vacia
    if len(PROMPT_MODEL_LIST) == 0:
        print("The prompt list is empty, exiting the program")
        raise
    for model in OLLAMA_MODEL_LIST:
        #Creamos los csv
        current_time = time.time_ns()
        prompt_metric_filepath =f"results/prompt_metrics_{current_time}_{model}.csv"
        # hardware_metric_filepath =f"results/hardware_metrics_{current_time}_{model}.csv"
        pm.create_csv_file(prompt_metric_filepath)
        # hm.create_csv_file(hardware_metric_filepath)
        for i in range (len(PROMPT_MODEL_LIST)):
            # de forma paralela alimentamos el prompts y medimos el hardware

            # en un hilo daemon guardo los resultados de la medicion del hardware
            # alimento el prompt en este hilo
            prompt_thread = threading.Thread(
                target=pm.ollama_query_and_save,
                args=(PROMPT_MODEL_LIST[i], model, i,prompt_metric_filepath),
            )
            prompt_thread.start()
            prompt_thread.join()


if __name__ == "__main__":
    main()



