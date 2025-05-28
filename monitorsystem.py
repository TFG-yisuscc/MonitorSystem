import argparse
import os
from clients.llama_model import LlamaModels
from clients.ollama_client import OllamaClient
from utils.configuration import PROMPT_LIST as PL, DESCRIPTION as DESC

parser = argparse.ArgumentParser(description=DESC)
parser.add_argument('procedencia', type=str, choices=["ollama", "llama_gguf"],
                    help="Option to indicate the procendency of the model.It can be ollama or llama_gguf")
parser.add_argument("name_or_path", type=str,
                    help="Ollama: Name of the model, llama_gguf: absolute path of the model")
parser.add_argument("-f","--frequency", type=float, default=1,help="Frequency of hardware measurements")
parser.add_argument("-t","--tbp", type=float, default=0,help="Wait time between prompts")



if __name__ == "__main__":
    arguments = parser.parse_args()
    if arguments.procedencia == "ollama":
        OllamaClient.test(arguments.name_or_path,PL ,0,arguments.tbp, arguments.frequency)
    elif arguments.procedencia == "llama_gguf":
        if os.path.isfile(arguments.name_or_path) and arguments.name_or_path.endswith(".gguf"):
            LlamaModels.test_model_gguf(arguments.name_or_path,PL,0,arguments.tbp,arguments.frequency)
        else:
            raise  FileNotFoundError("File not found or not appropriate")



