#from metrics.VGENMetrics import *
#from metrics.mpstatMetrics import *
import subprocess
import threading
from utils.prompt_parser import InstructionFollowingParser as ifps
from metrics.hardware_metrics import HardwareMetrics as hm 
from utils.LLM_functions import query_llm as query 
from metrics.prompt_metrics import prompt_metrics as pm
import time
import csv

MODEL = "deepseek-r1:1.5b"
FREQ =0.5 #in seconds 
# obtenemos los prompts 
list_prompt = ifps.get_instruc_eval_prompts()[0:3]
#Filenames of archives
current_time = time.time_ns()
PROMPT_METRIC_FILEPATH =f"results/prompt_metrics_{current_time}_{MODEL}_{FREQ}.csv"
HARDWARE_METRIC_FILEPATH =f"results/hardware_metrics_{current_time}_{MODEL}_{FREQ}.csv"
#creamos los csv 
hm.create_csv_file(HARDWARE_METRIC_FILEPATH);
pm.create_csv_file(PROMPT_METRIC_FILEPATH);

#intento malo de commparticion de variables
prompt_actual = -1


# creamos las funciones
def mesuring_hardware(): 
    while True: 
        hm(prompt_actual).append_to_csv_file(HARDWARE_METRIC_FILEPATH);
        time.sleep(FREQ)

def feeding_prompts(): 
    for i in range(len(list_prompt)): 
        prompt_actual = i
        query(MODEL,list_prompt[i],i).append_to_csv(PROMPT_METRIC_FILEPATH)
        
    


def main(): 
    metric_thread = threading.Thread(target=mesuring_hardware,daemon=True); 
    feeding_thread = threading.Thread(target=feeding_prompts); 
    metric_thread.start()
    feeding_thread.start(); 
    feeding_thread.join()
if __name__ == "__main__": 
    main()