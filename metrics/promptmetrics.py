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
Apart from the ollama metrics, the class contains functions for making queries and function for csv appending
"""
import time

from ollama import chat, ChatResponse, Client, GenerateResponse
from utils.llm_utils import client_default_ollama as cd_ollama
from llama_cpp import Llama
import csv
from dataclasses import dataclass, field
@dataclass
class PromptMetrics:
    # Indentifies tne prompt answer relative to the rest
    start_timestamp:int  # nanoseconds
    finish_timestamp:int  # nanoseconds
    model:str
    total_duration:int
    prompt_eval_count:int
    prompt_eval_duration:int
    eval_count:int
    load_duration :int
    answer: str
    prompt_id: int = field(default=-1)
    # NOTE lantency in tokesn per second has been omitted since it can be derivated
    #and thus calculated later, the formula is(according to ollama documentation):
    # eval_count / eval_duration * 10^9.
    #(tough it could beimplemented by a get factory )

    #Pseudo constructors

    @staticmethod
    def ollama_pseudoconstructor(starting_timestamp:int,finish_timestamp:int,prompt_answer:GenerateResponse,prompt_id:int= -1)-> 'PromptMetrics':
        """
        Pseudo Constructor for the prompt_metrics class
        """

        model:str = prompt_answer.model
        total_duration:int = prompt_answer.total_duration
        prompt_eval_count:int = prompt_answer.prompt_eval_count
        prompt_eval_duration:int= prompt_answer.prompt_eval_duration
        eval_count:int = prompt_answer.eval_count
        load_duration:int= prompt_answer.load_duration
        answer: str = prompt_answer.response
        return PromptMetrics(starting_timestamp, finish_timestamp, model, total_duration,
                             prompt_eval_count, prompt_eval_duration, eval_count, load_duration, answer, prompt_id)
    @staticmethod
    def llama_cpp_pseudoconstructor()-> 'PromptMetrics':
        """
       PSeudo  Constructor for the prompt_metrics class
         NOTE: WIP, the parameters are for placeholder purposes
        """
        #TODO :
        pass

    #Query related functions
    @staticmethod
    def query_ollama(prompt:str, model:str, client:Client=cd_ollama ,prompt_id:int= -1,keep_alive=1) -> 'PromptMetrics':
        """
        Queries the ollama API and returns a prompt_metrics object
        """
        #TODO: añadir paramaetro por defecto a client
        start= time.time_ns()
        response: GenerateResponse = client.generate(prompt=prompt, model=model, keep_alive=keep_alive)
        finish = time.time_ns()
        print(response.message.content)
        return PromptMetrics.ollama_pseudoconstructor(start, finish, response, prompt_id)
    def query_llama_cpp(self, prompt:str, model:str, client:Llama ,prompt_id:int= -1) -> 'PromptMetrics':
        """
        Queries the llama_cpp API and returns a prompt_metrics object
        NOTE: WIP, the parameters are for placeholder purposes
        """
        #TODO: investiga más a fondo como funciona llama_cpp que se te está convirtiendo el código en spaghetti code
        pass



   #CSV related functions
    #TODO: investigate further to use logs instead of csv
    @staticmethod
    def csv_header()-> list[str]:
        return ['start_timestamp', 'finish_timestamp', 'model', 'total_duration',
                'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'load_duration','answer','prompt_id']

    @staticmethod
    def create_csv_file(filename: str):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(PromptMetrics.csv_header())
            file.flush()

    def append_to_csv(self,filepath)-> list[str]:
        """
        Converts the object to a CSV line
        """
        row = [getattr(self, attr) for attr in PromptMetrics.csv_header()]
        with open(filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)
            file.flush()
        return row




