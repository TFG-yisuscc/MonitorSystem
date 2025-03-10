import subprocess


#this class stores metrics related to CPU atribbutes
class VCGENMetrics:
    #constructor 
    def __init__(self):
        #temperatura  CPU
        cmd_output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
        self.temperature = float(cmd_output.split("=")[1][:-3]) #TODO comprobar que funciona 
        #frecuecia
        cmd_output = subprocess.check_output(["vcgencmd", "measure_clock", "arm"]).decode("utf-8")
        self.frequency = int(cmd_output.split("=")[1])
        #voltaje cpu
        cmd_output = subprocess.check_output(["vcgencmd", "measure_volts", "core"]).decode("utf-8")
        self.voltage = float(cmd_output.split("=")[1][:-2])
        # trhottling
        cmd_output = subprocess.check_output(["vcgencmd", "get_throttled"]).decode("utf-8")
        self.throttling = int(cmd_output.strip().split("=")[1].split("\"")[0],16)
        #memoria
        cmd_output = subprocess.check_output(["vcgencmd", "get_mem", "arm"]).decode("utf-8")
        self.memory = int(cmd_output.split("=")[1][:-1])
# to string
    def __str__(self):
        return f"Temperature: {self.temperature}, Frequency: {self.frequency}, Voltage: {self.voltage}, Throttling: {self.throttling}, Memory: {self.memory}"
# update
    def update(self):
            #temperatura  CPU
        cmd_output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
        self.temperature = float(cmd_output.split("=")[1][:-3]) #TODO comprobar que funciona 
        #frecuecia
        cmd_output = subprocess.check_output(["vcgencmd", "measure_clock", "arm"]).decode("utf-8")
        self.frequency = int(cmd_output.split("=")[1])
        #voltaje cpu
        cmd_output = subprocess.check_output(["vcgencmd", "measure_volts", "core"]).decode("utf-8")
        self.voltage = float(cmd_output.split("=")[1][:-2])
        # trhottling
        cmd_output = subprocess.check_output(["vcgencmd", "get_throttled"]).decode("utf-8")
        self.throttling = int(cmd_output.split("=")[1])
        #memoria
        cmd_output = subprocess.check_output(["vcgencmd", "get_mem", "arm"]).decode("utf-8")
        self.memory = int(cmd_output.split("=")[1][:-1])

