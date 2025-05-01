"""
THis class measures the following hardware metrics
1. Temperature
2. CPU Frecuency.
3. CPU Voltage
4.CPU Throttling (as a bit field converted to integer)
5.CPU usage.
6. Mamory and swap usage of the whole pi and process
7. Fan usage (in RPM) try cached if it cannot find a fan
8. NOt implemented, power consumtion-> aparently it cannot be done reliably by software
"""
import csv
import os
import subprocess
import time
import psutil 
from threading import Thread, Lock, Event
class HardwareMetrics:
    def __init__(self,prompt_id=-1):
        self.timestamp = time.time_ns();# nanoseconds
        self.prompt_id = prompt_id;
        # temperatura  CPU
        cmd_output = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8")
        self.temperature = float(cmd_output.split("=")[1][:-3])
        # frecuecia
        cmd_output = subprocess.check_output(["vcgencmd", "measure_clock", "arm"]).decode("utf-8")
        self.frequency = int(cmd_output.split("=")[1], 16)
        # voltaje cpu
        cmd_output = subprocess.check_output(["vcgencmd", "measure_volts", "core"]).decode("utf-8")
        self.voltage = float(cmd_output.split("=")[1][:-2])
        # trhottling
        cmd_output = subprocess.check_output(["vcgencmd", "get_throttled"]).decode("utf-8")
        self.throttling = int(cmd_output.strip().split("=")[1].split("\"")[0], 16)
        #memoria y swap
        """"
        VCGENCMD should not  be used in this case
        https://raspberrypi.stackexchange.com/questions/108993/what-exactly-does-vcgencmd-get-mem-arm-display
       shouldbe read directly from /proc/meminfo but i think psutils does that anyways
        """

        #units in bytes
        # ram w/o swap
        mem =  psutil.virtual_memory();
        self.mem_total= mem.total;
        self.mem_used  = mem.used;
        self.mem_percent= mem.percent;

        try:
            pid = os.getpid()
            process = psutil.Process(pid)
            self.mem_pid = process.memory_info().rss;
            self.cpu_usage_pid = process.cpu_percent();
        except:
            self.mem_pid = -1;
            self.cpu_usage_pid=-1;

            # swap
        swap = psutil.swap_memory();
        self.swap_total = swap.total;
        self.swap_used = swap.used;
        self.swap_percent = swap.percent;
        #https://www.raspberrypi.com/documentation/computers/config_txt.html#overclocking-options
        #https://psutil.readthedocs.io/en/latest/#system-related-functions
    #OJO: puede serbloqueante, si no tiene si le indicamos un intervalo.
        #
        self.cpu_usage = psutil.cpu_percent();
        
        try: 
            if psutil.sensors_fans():
                self.fan_speed = psutil.sensors_fans()['pwmfan'][0].current
            else:
                self.fan_speed = -1
        except:
            self.fan_speed = -1
               


    def update(self):
        """Update the metrics with the current values."""
        #TODO 
        pass

    
    @staticmethod
    def csv_header()->list[str]:
        # Not ideal, it doesn change if we add new metrics

        return ['timestamp', 'prompt_id', 'temperature', 'frequency', 'voltage', 'throttling',
                'mem_total', 'mem_used', 'mem_percent', 'mem_pid', 'cpu_usage_pid',
                'swap_total', 'swap_used', 'swap_percent', 'cpu_usage', 'fan_speed']
    @staticmethod  
    def create_csv_file(filename: str):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(HardwareMetrics.csv_header())
            file.flush()
        
        

    def append_to_csv_file(self,filepath: str):
        row= [getattr(self, attr) for attr in HardwareMetrics.csv_header()]
        with open(filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)
            file.flush()
        return row
    @staticmethod
    def update_and_save(filepath:str,event:Event, prompt_id:int=-1): 
        while not event.is_set(): #TODO mejorar  update 
            HardwareMetrics(prompt_id).append_to_csv_file(filepath)
            # TODO Frecuencia Configurable
            if not event.is_set():
                time.sleep(1)
            else: break
    

