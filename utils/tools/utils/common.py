import os
import datetime
import threading
import time
from typing import Dict, Any

PROJECT_BASE = os.getcwd()

# Variable global para la herramienta actual
current_tool = {"name": None, "status": "idle"}

# Variable global para el subagente actual
current_subagent = {"name": None, "status": "idle"}

# Para manejar concurrencia en subagentes
subagent_lock = threading.Lock()

# Para manejar timeout automático
tool_timeout_thread = None
tool_timeout_lock = threading.Lock()

def notify_tool_usage(tool_name: str, status: str = "using"):
    """
    Notifica qué herramienta está usando el agente
    
    Args:
        tool_name: Nombre de la herramienta
        status: 'using', 'completed', 'failed', 'idle'
    """
    global current_tool, tool_timeout_thread
    
    with tool_timeout_lock:
        current_tool = {
            "name": tool_name,
            "status": status
        }
        
        # Si es "using", programar cambio automático a "completed" después de 2 segundos
        if status == "using":
            # Cancelar timeout anterior si existe
            if tool_timeout_thread and tool_timeout_thread.is_alive():
                return  # Ya hay un timeout en proceso
            
            # Crear nuevo timeout
            tool_timeout_thread = threading.Thread(
                target=_schedule_completion,
                args=(tool_name,),
                daemon=True
            )
            tool_timeout_thread.start()

def _schedule_completion(tool_name: str):
    """
    Programa el cambio automático a "completed" después de 2 segundos
    """
    time.sleep(2.0)  # Esperar 2 segundos
    
    with tool_timeout_lock:
        # Solo cambiar si la herramienta sigue siendo la misma y está en "using"
        if current_tool["name"] == tool_name and current_tool["status"] == "using":
            current_tool["status"] = "completed"

def get_current_tool() -> dict:
    """Retorna la herramienta actual en uso"""
    global current_tool
    with tool_timeout_lock:
        return current_tool.copy()

def notify_subagent_usage(subagent_name: str, status: str = "active"):
    """
    Notifica qué subagente está usando el agente
    
    Args:
        subagent_name: Nombre del subagente
        status: 'active', 'idle'
    """
    global current_subagent
    with subagent_lock:
        current_subagent = {
            "name": subagent_name,
            "status": status
        }

def get_current_subagent() -> dict:
    """Retorna el subagente actual en uso"""
    global current_subagent
    with subagent_lock:
        return current_subagent.copy()

def safe_path(path):
    """Función de seguridad para validar rutas dentro del proyecto"""
    if not path or path == "/": 
        return PROJECT_BASE
    # Eliminamos cualquier intento de ruta absoluta que envíe el modelo para forzar relativa
    clean_path = path.replace(PROJECT_BASE, "").lstrip("/")
    full_path = os.path.abspath(os.path.join(PROJECT_BASE, clean_path))
    
    if not full_path.startswith(PROJECT_BASE):
        return PROJECT_BASE
    return full_path

def write_log(tool_name, inputs, output):
    """
    Función para registrar auditoría de herramientas
    AHORA TAMBIÉN notifica el uso en tiempo real SIN cambiar estado inmediatamente
    """
    # 1. Notificar que la herramienta está en uso (el timeout manejará el cambio automático)
    notify_tool_usage(tool_name, "using")
    
    # 2. Escribir log como antes
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subagent_name = current_subagent.get('name') if isinstance(current_subagent, dict) else str(current_subagent) if current_subagent else 'None'
    log_entry = f" [{'='*10} {timestamp} [{subagent_name}] - [{tool_name}] {'='*10}]\n INPUTS: {inputs}\n OUTPUT: {output}\n\n"
    with open(".antflow/antflow.log", "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    # 3. Si hay error, cambiar estado inmediatamente a "failed"
    if "❌ Error" in str(output):
        notify_tool_usage(tool_name, "failed")
    # NOTA: No cambiar a "completed" aquí, el timeout lo hará automáticamente
