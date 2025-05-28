import argparse
import os
from clients.llama_model import LlamaModels
from clients.ollama_client import OllamaClient
from utils.configuration import PROMPT_LIST as PL, DESCRIPTION as DESC

parser = argparse.ArgumentParser(description=DESC)
parser.add_argument('source', type=str, choices=["ollama", "llama_gguf", "llama_pretrained"],
                    help="Option to indicate the procendency of the model.It can be ollama, llama_gguf or llama_pretrained")
parser.add_argument("name_or_path", type=str,
                    help="Ollama: Name of the model, llama_gguf: absolute path of the model, llama_pretrained:filename")
parser.add_argument("-r","--pretrained_repo",type=str, help="Huggingface repository id , only requrired when using llama_pretrained")
parser.add_argument("-f","--frequency", type=float, default=1,help="Frequency of hardware measurements")
parser.add_argument("-t","--tbp", type=float, default=0,help="Wait time between prompts")



if __name__ == "__main__":
    arguments = parser.parse_args()
    if arguments.source == "llama_pretrained" and (not arguments.pretrained_repo or arguments.pretrained_repo ==""):
        parser.error("--pretrained_repo is required when source is llama_pretrained")
    if arguments.source == "ollama":
        OllamaClient.test(arguments.name_or_path,PL ,arguments.tbp, arguments.frequency)
    elif arguments.source == "llama_gguf":
        if os.path.isfile(arguments.name_or_path) and arguments.name_or_path.endswith(".gguf"):
            LlamaModels.test_model_gguf(arguments.name_or_path,PL,arguments.tbp,arguments.frequency)
        else:
            raise  FileNotFoundError("File not found or not appropriate")
    elif arguments.source == "llama_pretrained": 
        LlamaModels.test_model_pretrained(arguments.name_or_path, arguments.pretrained_repo, PL, arguments.tbp, arguments.frequency)



