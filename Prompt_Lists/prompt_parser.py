import json
class InstructionFollowingParser:
    """
  Clase para analizar un archivo JSON que contiene los promts del paper 
  Instruction-Following Evaluation for Large Language Models
    """
    @staticmethod
    def get_prompts():
       
        lista_prompts = []
        ruta_fichero = "Prompt_Lists/instruction_following_eval_promt.jsonl"
        with open(ruta_fichero,'r', encoding='utf-8')as fichero : 
            for l in fichero:
                try:
                    # Cargamos el JSON
                    # y extraemos el prompt
                    # y lo añadimos a la lista
                    lista_prompts.append(json.loads(l).get('prompt'))
                except json.decoder.JSONDecodeError as e :
                    print("Error en el fichero: ", e)
        return lista_prompts