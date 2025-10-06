import logging

def create_loggers(inferenceEngine:str,current_time:str,model_name:str ): 
         # Configurar el logger para las métricas de prompts
        prompt_log_filename = f"results/{inferenceEngine}_promptmetrics_{current_time}_{model_name.replace('_','-')}.jsonl"
        prompt_metric_log = logging.getLogger('prompt_metrics')
        prompt_metric_log.setLevel(logging.INFO)
        # Limpiar handlers existentes para evitar duplicados
        prompt_metric_log.handlers.clear()
        # Crear handler de archivo
        handler = logging.FileHandler(prompt_log_filename, mode='w')
        handler.setFormatter(logging.Formatter('%(message)s'))
        prompt_metric_log.addHandler(handler)

        hardware_log_filename = f"results/{inferenceEngine}_hardwaremetrics_{current_time}_{model_name}.jsonl"
        hardware_metric_log = logging.getLogger('hardware_metrics')
        hardware_metric_log.setLevel(logging.INFO)
        hardware_metric_log.handlers.clear()
        h_handler = logging.FileHandler(hardware_log_filename, mode='w')
        h_handler.setFormatter(logging.Formatter('%(message)s'))
        hardware_metric_log.addHandler(h_handler)
        return hardware_metric_log, prompt_metric_log