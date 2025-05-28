from utils.prompt_parser import PromptParser as ifp
from ollama import Client


# -----Argparser configuration-----
DESCRIPTION = """

            """



# -------Configuración relacionada con los parámetros hardware----

# Configuración relativa a los Prompts

PROMPT_LIST = ifp.get_instruc_eval_prompts()[0:3]#todo re append the first prompt  at the end
#-------Configuración relacionada con ollama-------
#OLLAMA_MODEL_LIST =["phi4-mini:latest","deepseek-r1:1.5b","llama3.2:latest ","gemma3:1b","mistral"]

# Create a default client for ollama
client_default_ollama= Client(
  
  headers={'x-some-header': 'some-value'}
)





