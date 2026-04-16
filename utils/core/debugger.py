from os import environ
from logging import getLogger, disable, ERROR
from sys import maxsize, stdout, stderr

class SafeStdout:
    def write(self, msg): 
        if 'LiteLLM' not in msg and 'INFO:' not in msg:
            stdout.write(msg)
    def flush(self): 
        stdout.flush()


def _turn_off_logs():
    environ["LITELLM_LOG"] = "ERROR"
    environ["LITELLM_DEBUG"] = "false"
    environ["LITELLM_CACHE"] = "false"
    environ["LITELLM_DROP_PARAMS"] = "true"
    environ['TQDM_DISABLE'] = '1' 

    disable(maxsize)
    getLogger("litellm").setLevel(ERROR)
    getLogger("smolagents").setLevel(ERROR)

    stdout = SafeStdout()
    stderr = SafeStdout()


def _turn_off_logs_based_on_config():
    """Desactiva logs basado en la configuración del debugger"""
    from .config_loader import get_enable_debugger
    
    if not get_enable_debugger():
        _turn_off_logs()
    else:
        # Si el debugger está deshabilitado, no hacer nada
        pass


