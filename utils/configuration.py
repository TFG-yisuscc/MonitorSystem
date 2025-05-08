from utils.prompt_parser import InstructionFollowingParser as ifp 

# -------Configuración relacionada con los parámetros hardware----
FRECUENCY:float= 0.5
TIME_BETWEEN_PROMPTS = 10.0 # in seconds 
TIME_BETWEEN_MODELS = 3.0 *60   # three minutes should sufice since the "default" keep alive is 2 min 

# Configuración relativa a los Prompts

PROMPT_LIST = ifp.get_instruc_eval_prompts()[0:3]
#-------Configuración relacionada con ollama-------
#OLLAMA_MODEL_LIST =["phi4-mini:latest","deepseek-r1:1.5b","llama3.2:latest ","gemma3:1b","mistral"]
OLLAMA_MODEL_LIST =["gemma3:1b"]





