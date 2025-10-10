import time
import os
import logging
from datetime import datetime
from threading import Event, Thread
from llama_cpp import Llama, llama_perf_context,llama_perf_context_reset
from metrics.prompt_metrics import PromptMetrics
from metrics.hardware_metrics import HardwareMetrics
from metrics.llama_performance_metrics import LLamaPerfomanceMetrics
from utils.metric_logger import create_loggers
from utils.Inference_engines import Engine

class LlamaModels(Llama):
    def get_name(self):
        name=""
        try:
            ruta = self.model_path
            name = os.path.basename(ruta)
            #lo dejo con la extensión del archivo a proposito
        except Exception:
            name = "Unknown"
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
        answer = self(prompt)
        finish = time.time_ns()
        return  PromptMetrics.llama_cpp_pseudoconstructor(start, finish, self.get_performance_metrics(), self.get_name(),answer, prompt_id)
    
    def query_event(self,prompt:str,event:Event, prompt_id=-1)-> PromptMetrics:
        #limpiaos el contexto de rendimiento
        llama_perf_context_reset(self.ctx)
        event.set()
        #so the time is a bit more accurate
        start= time.time_ns()
        #We query the machine
        answer= self(prompt)
        print(answer)
        finish = time.time_ns()
        event.clear()

        return  PromptMetrics.llama_cpp_pseudoconstructor(start, finish, self.get_performance_metrics(),self.get_name(),answer, prompt_id)

    def query_event_save(self, prompt: str, event: Event, prompt_log:logging.Logger,prompt_id=-1):
        #TODO perhaps in a future t will be modified so
        self.query_event(prompt, event, prompt_id).append_to_csv(prompt_log)

    @staticmethod
    def test_model_gguf(model_path:str, prompt_list:list[str],time_between_prompts:float=0,freq:float=1):

        modelo = LlamaModels(model_path=model_path)
        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
        hardware_metric_log, prompt_metric_log = create_loggers(Engine.LLAMA.name,current_time,model_name=modelo.get_name())
        for i in range(len(prompt_list)):
            prompt = prompt_list[i]
            evento = Event()
            prompt_thread = Thread(target=modelo.query_event_save, args=(prompt, evento, prompt_metric_log, i))
            hardware_thread = Thread(target=HardwareMetrics.update_and_save, args=(hardware_metric_log, evento,i,freq))
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
            repo_id=rspositoryID,
            filename=model_name,
            verbose=True
        )
        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M")
        hardware_metric_log, prompt_metric_log = create_loggers(Engine.LLAMA.name,current_time,model_name=modelo.get_name())
        for i in range(len(prompt_list)):
            prompt = prompt_list[i]
            evento = Event()
            prompt_thread = Thread(target=modelo.query_event_save, args=(prompt, evento, prompt_metric_log, i))
            hardware_thread = Thread(target=HardwareMetrics.update_and_save, kwargs={
                                            'logger': hardware_metric_log,
                                            'event': evento,
                                            'mode':Engine.LLAMA,
                                            'prompt_id': i,
                                            'freq': freq})
            hardware_thread.start()
            prompt_thread.start()
            prompt_thread.join()
            hardware_thread.join()
            if len(prompt_list) -1 ==  i:
                modelo.close()
            else:
                time.sleep(time_between_prompts)

        




