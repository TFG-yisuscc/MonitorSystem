"""
Placeholder description
"""
import ollama
from ollama import *
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



client_default_ollama= Client(
  #host='http://raspberrypi2.local:11434',
  headers={'x-some-header': 'some-value'}
)