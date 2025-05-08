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
import csv
from ollama import chat, ChatResponse, Client, GenerateResponse
from utils.llama_utils import LLamaPerfomanceMetrics as lpm
from utils.llm_utils import client_default_ollama as cd_ollama
from llama_cpp import Llama
from dataclasses import dataclass, field
from threading import Event
@dataclass
class PromptMetrics:
    start_timestamp:int  # nanoseconds
    finish_timestamp:int  # nanoseconds
    model:str
    total_duration:int
    prompt_eval_count:int
    prompt_eval_duration:int
    eval_count:int
    eval_duration:int
    load_duration :int
    #answer: str
    prompt_id: int = field(default=-1)# Indentifies tne prompt answer relative to the rest
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
        eval_duration:int = prompt_answer.eval_duration
        load_duration:int= prompt_answer.load_duration
        #answer: str = prompt_answer.response
        return PromptMetrics(starting_timestamp, finish_timestamp, model, total_duration,
                             prompt_eval_count, prompt_eval_duration, eval_count, eval_duration,load_duration, prompt_id)
    @staticmethod
    def llama_cpp_pseudoconstructor(starting_timestamp:int,finish_timestamp:int, Perf:lpm,model:str, prompt_id:int= -1)-> 'PromptMetrics':
        """
       PSeudo  Constructor for the prompt_metrics class
    
        """
        total_duration = starting_timestamp - finish_timestamp #TODO check for better solutions later
        prompt_eval_count:int = Perf.n_p_eval
        prompt_eval_duration:int= Perf.t_p_eval_ns
        eval_count:int = Perf.n_eval
        eval_duration:int = Perf.t_eval_ns
        load_duration:int= Perf.t_load_ns
        return PromptMetrics(starting_timestamp, finish_timestamp, model,total_duration,prompt_eval_count,prompt_eval_duration,eval_count,eval_duration,load_duration,prompt_id)
        

    #Query and prompt related functions
    @staticmethod
    def query_ollama(prompt:str, model:str, client:Client=cd_ollama ,prompt_id:int= -1,keep_alive='2m') -> 'PromptMetrics':
        """
        Queries the ollama API and returns a prompt_metrics object
        """
        
        start= time.time_ns()
        response: GenerateResponse = client.generate(prompt=prompt, model=model, keep_alive=keep_alive)
        finish = time.time_ns()
        return PromptMetrics.ollama_pseudoconstructor(start, finish, response, prompt_id)

    @staticmethod
    def query_ollama_with_event(prompt:str, model:str,event:Event,client:Client=cd_ollama, prompt_id:int= -1,keep_alive='2m') -> 'PromptMetrics':
        """
        Queries the ollama API and returns a prompt_metrics object
        """
        event.set()
        start= time.time_ns()
        response: GenerateResponse = client.generate(prompt=prompt, model=model, keep_alive=keep_alive)
        finish = time.time_ns()
        event.clear()
        return PromptMetrics.ollama_pseudoconstructor(start, finish, response, prompt_id)
    
    def unload_model_ollama( model:str, client:Client=cd_ollama):
        """
        Sends an empty prompt with  zeroed keepalive
        """
        response: GenerateResponse = client.generate(prompt='', model=model, keep_alive=0)
        

    @staticmethod
    def query_llama_cpp(prompt:str, llm:Llama ,modelName:str="",prompt_id:int=-1) -> 'PromptMetrics':
        """
        Queries the llama_cpp API and returns a prompt_metrics object, The llm given as a parameter should be already configured as desired
        inculding the rperformance options
        NOTE: WIP, the parameters are for placeholder purposes
        """
        start= time.time_ns()
        #We query the machine
        response= llm(prompt)
        finish = time.time_ns()
        
        return  PromptMetrics.llama_cpp_pseudoconstructor(start,finish, lpm.pseudoconstructor(llm),modelName,prompt_id)

   #CSV related functions
    #TODO: investigate further to use logs instead of csv
    @staticmethod
    def csv_header()-> list[str]:
        """
        Returns a CSV--like header 
        """
        return ['prompt_id','start_timestamp', 'finish_timestamp', 'model', 'total_duration',
                'prompt_eval_count', 'prompt_eval_duration', 'eval_count', 'eval_duration', 'load_duration']

    @staticmethod
    def create_csv_file(filename: str):
        """
        Creates a CSV and appendst the header 
        """
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
    @staticmethod
    def ollama_query_and_save(prompt: str, model: str, filepath: str, client: Client = cd_ollama, prompt_id: int = -1, keep_alive: int = 1):
        """
        Unifies the Queries the ollama API and saves the result to a CSV file
        Useful for threads
        """
        PromptMetrics.query_ollama(prompt, model, client, prompt_id, keep_alive).append_to_csv(filepath)

    @staticmethod
    def ollama_query_and_save_with_event(prompt: str, model:str, filepath: str, event: Event, client: Client = cd_ollama, prompt_id: int = -1, keep_alive: int = 1):
        """
        Unifies the Queries the ollama API and saves the result to a CSV file
        Useful for threads
        """
        PromptMetrics.query_ollama_with_event(prompt,model,event,client,prompt_id,keep_alive).append_to_csv(filepath)
    


