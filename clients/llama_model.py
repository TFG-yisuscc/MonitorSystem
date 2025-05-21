import time
import os 

from threading import Event
from llama_cpp import Llama, llama_perf_context,llama_perf_context_reset
from metrics.promptmetrics import PromptMetrics
from utils.llamaperformancemetrics import LLamaPerfomanceMetrics

class LlamaModels(Llama):
    def get_name(self):
        ruta = self.model_path;
        name = os.path.basename(ruta)
        #lo dejo con la extensión del archivo a proposito
        return name 
    def get_performance_metrics(self):
            param = llama_perf_context(self.ctx)
        # TODO check if its is necesary to  reset  the perf context 
        # it seesm that the only thing that remains unchanged across generations 
        #is the load time  
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
    def query_event_save(self,prompt:str,event:Event,filepath, prompt_id=-1): 
        self.query_event(prompt:str,event:Event,prompt_id).append_to_csv(filepath)

        




