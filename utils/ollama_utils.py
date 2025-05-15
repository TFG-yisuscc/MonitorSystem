"""
Placeholder description
"""
from threading import Event
import ollama
from ollama import *
import time
from utils.configuration import client_default_ollama as cdo
from metrics.promptmetrics import PromptMetrics 
from dataclasses import dataclass, field

@dataclass
class ollamaClient(Client):
    client:Client = field(default=cdo)

    def query_ollama(self, prompt:str, model:str ,prompt_id:int= -1,keep_alive='2m') -> PromptMetrics:
        """
        Queries the ollama API and returns a prompt_metrics object
        """
        
        start= time.time_ns()
        response: GenerateResponse = self.client.generate(prompt=prompt, model=model, keep_alive=keep_alive)
        finish = time.time_ns()
        return PromptMetrics.ollama_pseudoconstructor(start, finish, response, prompt_id)
    def query_ollama_with_event(self, prompt:str, model:str,event:Event,prompt_id:int= -1,keep_alive='2m')-> PromptMetrics:
        
        start= time.time_ns()
        event.set()
        response: GenerateResponse = self.client.generate(prompt=prompt, model=model, keep_alive=keep_alive)
        finish = time.time_ns()
        event.clear()
        return PromptMetrics.ollama_pseudoconstructor(start,finish,response,prompt_id)
    
    def ollama_query_and_save(self,prompt: str, model: str, filepath: str, prompt_id: int = -1, keep_alive='2m'):
        """
        Unifies the Queries the ollama API and saves the result to a CSV file
        Useful for threads
        """
        ollamaClient.query_ollama(self,prompt, model, prompt_id, keep_alive).append_to_csv(filepath)
      
    def ollama_query_and_save_with_event(self,prompt: str, model:str, filepath: str, event: Event, prompt_id = -1, keep_alive='2m'):
        """
        Unifies the Queries the ollama API and saves the result to a CSV file
        Useful for threads
        """
        ollamaClient.query_ollama_with_event(self,prompt,model,event,prompt_id,keep_alive).append_to_csv(filepath)
    def unload_model(self,model:str): 
        self.client.generate(prompt='', model=model, keep_alive=0)

def ollama_model_checker(model_list: list[str]):
    """
    Checks if the model is in the list of models
    """
    # si  esta vacia-> no se susa ollama
    if len(model_list) == 0:
        return
    # si tiene elementos

    #por cada elemento compruebo si ollama lo tiene idescargado y si no lo descargo
    for model in model_list:
        model= model.strip()
        try:
            ollama.show(model)
        except ollama.ResponseError as e:
            print(f"Model {model} not found, downloading...")
            try:
                ollama.pull(model)
            except ollama.ResponseError as e:
                print(e)
                print(f"The model {model} could not be downloaded,check for typos or for internet connection")
                print("Exiting the program")
                raise
            else:
                print(f"The model {model} has been succesfully downloaded")
        else:
            print(f"Model {model} already downloaded")
