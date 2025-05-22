
from clients.ollama_client import OllamaClient
from clients.llama_model import LlamaModels
from utils.configuration import PROMPT_LIST as PL



def test_ollama():
    OllamaClient.test("orca-mini:3b",PL)


           
def test_llama():
    fichero = "/home/user1/MonitorSystem/models/q4_0-orca-mini-3b.gguf"   
    LlamaModels.test_model_gguf(fichero,PL)



            
        
           


if __name__ == "__main__":
    test_llama()
    test_ollama()
    



