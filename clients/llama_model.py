import time
import os
from datetime import datetime
from threading import Event, Thread
from llama_cpp import Llama, llama_perf_context,llama_perf_context_reset
from metrics.prompt_metrics import PromptMetrics
from metrics.hardware_metrics import HardwareMetrics
from metrics.llama_performance_metrics import LLamaPerfomanceMetrics

class LlamaModels(Llama):
    def get_name(self):
        name=""
        try:
            ruta = self.model_path;
            name = os.path.basename(ruta)
            #lo dejo con la extensión del archivo a proposito
        except:
            name = self.model_name
        return name

    def get_performance_metrics(self):
            param = llama_perf_context(self.ctx)
        # TODO check if its is necesary to  reset  the perf context 
        # it seesm that the only thing that remains unchanged across generations 
        #is the load time -> if you reset the performance model it changes
        #also it seem that llama doenst use all all the cores al least with the orca model
        #
            t_start_ns =  param.t_start_ms * 1e6
            t_load_ns= param.t_load_ms *1e6
            t_p_eval_ns = param.t_p_eval_ms *1e6
            t_eval_ns = param.t_eval_ms*1e6
            n_p_eval = param.n_p_eval
            n_eval = param.n_eval
            llama_perf_context_reset(self.ctx)

            return  LLamaPerfomanceMetrics(t_start_ns,t_load_ns, t_p_eval_ns, t_eval_ns, n_p_eval, n_eval)
    
    def query(self,prompt:str,prompt_id=-1):
        llama_perf_context_reset(self.ctx)
        start= time.time_ns()
        #We query the machine
        response= self(prompt)
        finish = time.time_ns()
        return  PromptMetrics.llama_cpp_pseudoconstructor(start, finish, self.get_performance_metrics(), self.get_name(), prompt_id)
    
    def query_event(self,prompt:str,event:Event, prompt_id=-1)-> PromptMetrics:
        #limpiaos el contexto de rendimiento
        llama_perf_context_reset(self.ctx)
        event.set()
        #so the time is a bit more accurate
        start= time.time_ns()
        #We query the machine
        response= self(prompt)
        finish = time.time_ns()
        event.clear()
        return  PromptMetrics.llama_cpp_pseudoconstructor(start, finish, self.get_performance_metrics(), self.get_name(), prompt_id)

    def query_event_save(self, prompt: str, event: Event, filepath:str,prompt_id=-1):
        #TODO perhaps in a future t will be modified so
        self.query_event(prompt, event, prompt_id).append_to_csv(filepath)

    @staticmethod
    def test_model_gguf(model_path:str, prompt_list:list[str],time_between_prompts:float=0,freq:float=1):
        #TODO: Check if it works
        modelo = LlamaModels(model_path=model_path)
        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
        prompt_metric_filepath =f"results/llama_prompt_metrics_{current_time}_{modelo.get_name()}.csv"
        hardware_metric_filepath =f"results/llama_hardware_metrics_{current_time}_{modelo.get_name()}.csv"
        HardwareMetrics.create_csv_file(hardware_metric_filepath)
        PromptMetrics.create_csv_file(prompt_metric_filepath)
        for i in range(len(prompt_list)):
            prompt = prompt_list[i]
            evento = Event()
            prompt_thread = Thread(target=modelo.query_event_save, args=(prompt, evento, prompt_metric_filepath, i))
            hardware_thread = Thread(target=HardwareMetrics.update_and_save, args=(hardware_metric_filepath, evento,i,freq))
            hardware_thread.start()
            prompt_thread.start()
            prompt_thread.join()
            hardware_thread.join()
            if len(prompt_list) -1 ==  i:
                modelo.close()
            else:
                time.sleep(time_between_prompts)
    
    @staticmethod
    def test_model_pretrained(model_name:str,rspositoryID:str, prompt_list:list[str],time_between_prompts:float=0,freq:float=1):
        modelo = LlamaModels.from_pretrained(
        repo_id="Qwen/Qwen2-0.5B-Instruct-GGUF",
        filename="*q8_0.gguf",
        verbose=True
        )
        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
        prompt_metric_filepath =f"results/llama_pretrained_prompt_metrics_{current_time}_{modelo.get_name()}.csv"
        hardware_metric_filepath =f"results/llama_pretrained_hardware_metrics_{current_time}_{modelo.get_name()}.csv"
        HardwareMetrics.create_csv_file(hardware_metric_filepath)
        PromptMetrics.create_csv_file(prompt_metric_filepath)
        for i in range(len(prompt_list)):
            prompt = prompt_list[i]
            evento = Event()
            prompt_thread = Thread(target=modelo.query_event_save, args=(prompt, evento, prompt_metric_filepath, i))
            hardware_thread = Thread(target=HardwareMetrics.update_and_save, args=(hardware_metric_filepath, evento,i,freq))
            hardware_thread.start()
            prompt_thread.start()
            prompt_thread.join()
            hardware_thread.join()
            if len(prompt_list) -1 ==  i:
                modelo.close()
            else:
                time.sleep(time_between_prompts)

        




