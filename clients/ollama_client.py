"""
Placeholder description
"""
import time
import ollama
from datetime import datetime
from threading import Event, Thread
from dataclasses import dataclass, field
from ollama import GenerateResponse, Client,
from metrics.hardware_metrics import HardwareMetrics
from utils.configuration import client_default_ollama as cdo
from metrics.prompt_metrics import PromptMetrics

@dataclass
class OllamaClient(Client):
    client: Client = field(default=cdo)

    def query(self, prompt: str, model: str, prompt_id: int = -1, keep_alive='2m') -> PromptMetrics:
        """
        Queries the ollama API and returns a prompt_metrics object
        """

        start = time.time_ns()
        response: GenerateResponse = self.client.generate(prompt=prompt, model=model, keep_alive=keep_alive)
        finish = time.time_ns()
        return PromptMetrics.ollama_pseudoconstructor(start, finish, response, prompt_id)

    def query_event(self, prompt: str, model: str, event: Event, prompt_id: int = -1, keep_alive='2m') -> PromptMetrics:
        start = time.time_ns()
        event.set()
        response: GenerateResponse = self.client.generate(prompt=prompt, model=model, keep_alive=keep_alive)
        finish = time.time_ns()
        event.clear()
        return PromptMetrics.ollama_pseudoconstructor(start, finish, response, prompt_id)

    def query_save(self, prompt: str, model: str, filepath: str, prompt_id: int = -1, keep_alive='2m'):
        """
        Unifies the Queries the ollama API and saves the result to a CSV file
        Useful for threads
        """
        OllamaClient.query(self, prompt, model, prompt_id, keep_alive).append_to_csv(filepath)

    def query_event_save(self, prompt: str, model: str, filepath: str, event: Event, prompt_id=-1, keep_alive='2m'):
        """
        Unifies the Queries the ollama API and saves the result to a CSV file
        Useful for threads
        """
        OllamaClient.query_event(self, prompt, model, event, prompt_id, keep_alive).append_to_csv(filepath)

    def unload_model(self, model_name: str):
        #TODO mejorarlo para que cerciore que se descarga en memoria
         aux = self.client.generate(prompt='', model=model_name, keep_alive=0)

    @staticmethod
    def test(model_name:str, prompt_list:list[str],time_between_prompts:float=0,freq:float=1):
        #TODO Check if it works
        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
        prompt_metric_filepath = f"results/ollama_prompt_metrics_{current_time}_{model_name}.csv"
        hardware_metric_filepath = f"results/ollama_hardware_metrics_{current_time}_{model_name}.csv"
        cliente = OllamaClient()
        for i in range(len(prompt_list)):
            prompt = prompt_list[i]
            evento = Event()
            prompt_thread = Thread(target=cliente.query_event_save, args=(prompt, model_name, evento, prompt_metric_filepath, i))
            hardware_thread = Thread(target=HardwareMetrics.update_and_save, args=(hardware_metric_filepath, evento,i,freq))
            hardware_thread.start()
            prompt_thread.start()
            prompt_thread.join()
            hardware_thread.join()
            if len(prompt_list) -1 ==  i:
                cliente.unload_model(model_name)
            else:
                time.sleep(time_between_prompts)

    @staticmethod
    def ollama_model_checker(model_name:str):
        """
        Checks if the model is downloaded
        """
        #por cada elemento compruebo si ollama lo tiene idescargado y si no lo descargo
        model_name = model_name.strip()
        try:
            ollama.show(model_name)
        except ollama.ResponseError as e:
            print(f"Model {model_name} not found, downloading...")
            try:
                ollama.pull(model_name)
            except ollama.ResponseError as e:
                print(e)
                print(f"The model {model_name} could not be downloaded,check for typos or for internet connection")
                print("Exiting the program")
                raise
            else:
                print(f"The model {model_name} has been succesfully downloaded")
        else:
            print(f"Model {model_name} already downloaded")
