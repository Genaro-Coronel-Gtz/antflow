#!/usr/bin/env python3
"""
Step Logger para CodeAgent
Solo maneja la notificación del subagente (CodeAgent)
Las herramientas individuales se encargan de su propio logging
"""

from utils.tools.utils.common import notify_subagent_usage
from smolagents import ActionStep, CodeAgent
from utils.core.logg.steps_logger import logg_step


def agent_step_callback(step: ActionStep, agent: CodeAgent):
    """
    Callback para notificar cuándo el CodeAgent está activo
    
    Args:
        step: Paso ejecutado por el agente
        agent: Instancia del agente
    """
    try:
        # Notificar que el CodeAgent está activo (como si fuera un subagente)
        agent_name = getattr(agent, 'name', 'CodeAgent')
        notify_subagent_usage(agent_name, "active")

        # Llamar al logger de subagentes para registrar el paso
        logg_step(step, agent)
        
        # Las herramientas individuales se encargan de su propio logging
        # No necesitamos hacer nada más aquí
                
    except Exception as e:
        # Si falla la notificación, no interrumpir la ejecución del agente
        try:
            # Log mínimo para depuración
            from utils.tools.utils.common import write_log
            write_log("step_logger_error", "code_agent_step_logger", f"Error en notificación: {str(e)}")
        except:
            pass  # Silenciar completamente si todo falla
