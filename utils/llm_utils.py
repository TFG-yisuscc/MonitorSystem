import time
from ollama import chat, ChatResponse, Client


# Create a default lient for ollama
client_default_ollama= Client(
  #host='http://raspberrypi2.local:11434',
  headers={'x-some-header': 'some-value'}
)
# Create a default client for llama_cpp




