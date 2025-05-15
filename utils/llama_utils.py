from dataclasses import dataclass
from llama_cpp import Llama, llama_perf_context
import time
"""
   Prompt relatade data/metrics providedby llama 
   Converted to nanoseconds from miliseconds to make the comparisons with ollama easier
"""
@dataclass
class LLamaPerfomanceMetrics: 
    t_start_ns: int # este creo que no lo utilizamos en ollama 
    t_load_ns: int
    t_p_eval_ns: int
    t_eval_ns: int
    n_p_eval:int
    n_eval:int

    @staticmethod
    def pseudoconstructor(llm:Llama)-> 'LLamaPerfomanceMetrics':
        """
        Placeholder description 
        """
        param = llama_perf_context(llm.ctx)
        # TODO check if its is necesary to  reset  the perf context 
        # it seesm that the only thing that remains unchanged across generations 
        #is the load time  
        #also it seem that llama doenst use all all the cores al least with the orca model
        #
        t_start_ns =  param.t_start_ms * 1e6
        t_load_ns= param.t_load_ms *1e6
        t_p_eval_ns = param.t_p_eval_ms *1e6
        t_eval_ns = param.t_eval_ms*1e6
        return  LLamaPerfomanceMetrics(t_start_ns,t_load_ns, t_p_eval_ns, t_eval_ns, param.n_p_eval, param.n_eval)



