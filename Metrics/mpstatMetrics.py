import  subprocess
import json

class mpstatMetrics:
    def __init__(self):
        resultado = json.loads(subprocess.check_output(['mpstat','-o','JSON']).decode("utf-8"))
        idle_value = resultado["sysstat"]["hosts"][0]["statistics"][0]["cpu-load"][0]["idle"]
        self.idle = idle_value
    def update(self):
        resultado = json.loads(subprocess.check_output(['mpstat', '-o', 'JSON']).decode("utf-8"))
        idle_value = resultado["sysstat"]["hosts"][0]["statistics"][0]["cpu-load"][0]["idle"]
        self.idle = idle_value
    def __str__(self):
        return f"Idle: {self.idle}"