import argparse

from clients.llama_model import LlamaModels
from clients.ollama_client import OllamaClient
from utils.configuration import PROMPT_LIST as PL, DESCRIPTION as DESC

parser = argparse.ArgumentParser(description=DESC)
parser.add_argument('procedencia', type=str, choices=["ollama", "llama_gguf"],
                    help="Option to indicate the procendency of the model.It can be ollama or llama_gguf")
parser.add_argument("name_or_path", type=str,
                    help="Ollama: Name of the model, llama_gguf: absolute path of the model")


def test_ollama():
    #OllamaClient.test("orca-mini:3b", PL)
    pass


def test_llama():
    #fichero = "/home/user1/MonitorSystem/models/q4_0-orca-mini-3b.gguf"
    #LlamaModels.test_model_gguf(fichero, PL)
    pass


if __name__ == "__main__":
    test_llama()
    test_ollama()
