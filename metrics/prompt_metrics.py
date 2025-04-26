"""
This class contains the following metrics  relative to prompts
1. Starting timestampt
2. Prompt answer.
3. Finishing timestamp
4. Values from ollama:
4.0 total_duration: time spent generating the response
 4.1load_duration: time spent in nanoseconds loading the model
4.2prompt_eval_count: number of tokens in the prompt
4.3 prompt_eval_duration: time spent in nanoseconds evaluating the prompt
4.4 eval_count: number of tokens in the response
4.5 eval_duration: time in nanoseconds spent generating the response
Necesito calcular la latencia de respuesta, ¿Como lo interpreto?:
A) tiempo que se tarda en generar el primer token de respuesta desde que se envía el prompt-
> se podria deducir de esta forma? Finish-Start - load_duration. o bien usando eval duration
B) Tiempo total que se tarda en generar la respuesta al completo,
desde que se envía el prompt hasta que se envia el último token de respuesta-> fácil de medir
"""
from ollama import chat, ChatResponse, Client
import csv
class prompt_metrics:
    def __init__(self,starting_timestamp,finish_timestamp,prompt_answer:ChatResponse,prompt_id= -1):
        """
        Constructor for ollama
        """

        self.prompt_id = prompt_id;  # Indentifies tne prompt answer relative to the rest
        self.start_timestamp = starting_timestamp;# nanoseconds
        self.finish_timestamp = finish_timestamp;# nanoseconds
        self.model= prompt_answer.model;
        self.total_duration = prompt_answer.total_duration;
        self.prompt_eval_count = prompt_answer.prompt_eval_count;
        self.prompt_eval_duration = prompt_answer.prompt_eval_duration;
        self.eval_count = prompt_answer.eval_count;
        self.load_duration = prompt_answer.load_duration;
        #self.answer:str= prompt_answer.message.content;
    #TODO :Consider implementing an update method 
   
    @staticmethod
    def csv_header()-> list[str]:
        return ['prompt_id', 'start_timestamp', 'finish_timestamp', 'model', 'total_duration',
                'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'load_duration']

    @staticmethod
    def create_csv_file(filename: str):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(prompt_metrics.csv_header())
            file.flush()

    def append_to_csv(self,filepath)->str:  
        """
        Converts the object to a CSV line
        """
        row = [getattr(self, attr) for attr in prompt_metrics.csv_header()]
        with open(filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)
            file.flush()
        return row 




