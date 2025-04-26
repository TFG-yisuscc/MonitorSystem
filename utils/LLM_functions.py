import time

from ollama import chat, ChatResponse, Client
from metrics.prompt_metrics import prompt_metrics as pm


client = Client(
  #host='http://raspberrypi2.local:11434',
  headers={'x-some-header': 'some-value'}
)

def query_llm(modelo,prompt, prompt_id)-> pm:
    start= time.time_ns()
    response: ChatResponse = client.chat(model=modelo, messages=[
      {
        'role': 'user',
        'content': prompt,
      },
    ])
    finish = time.time_ns()
    print(response.message.content)
    return pm(start,finish,response,prompt_id)

