from dataclasses import dataclass
from llama_cpp import Llama, llama_perf_context
@dataclass
class LLamaPerfomanceMetrics: 
    #TODO: Deberia convertir las metricas de llama a nanosegundos o las metricas de ollama a milisegundos
    # me decanto por lo último
    #TODO ¿Deberia extender la clase o no? 
    t_start_ms:float # este creo que no lo utilizamos en ollama 
    t_load_ms: float
    t_p_eval_ms: float
    t_eval_ms: float
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
        return  LLamaPerfomanceMetrics(param.t_start_ms,param.t_load_ms, param.t_p_eval_ms,param.t_eval_ms,param.n_p_eval,param.n_eval)



