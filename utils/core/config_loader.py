#!/usr/bin/env python3
"""
Cargador de configuración desde .antflow/config.json
Reemplaza el uso de variables de entorno (.env)
"""

import os
import json
from typing import Any, Optional

# Cache para evitar leer el archivo múltiples veces
_config_cache = None

def load_config() -> dict:
    """
    Carga la configuración desde .antflow/config.json
    
    Returns:
        dict: Configuración cargada
    """
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    config_path = os.path.join(".antflow", "config.json")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            _config_cache = json.load(f)
        return _config_cache
    except FileNotFoundError:
        # Valores por defecto si no existe el archivo
        _config_cache = {
            "provider": "Ollama",
            "api_base_url": "http://localhost:11434",
            "open_router_api_key": None,
            "model": "qwen2.5-coder:7b-instruct-q4_K_M",
            "max_steps": 30,
            "theme": "dracula",
            "repo_mapper_route": ".",
            "enable_animations": True,
            "generate_prompt_context_file": True,
            "show_pet": True,
            "memory_subagents_persistent": False,
            "agent_verbosity_level": -1,
            "enable_skills": False,
            "enable_subagents": True,
            "qdrant_port": 6333,
            "qdrant_host": "localhost",
            "project_hash": "",
            "main_agent_name": "Orquestador",
            "start_app_clean_files": False,
            "max_messages_memory": 50,
            "language": "es",
            "debugger": False,
            "num_ctx": 4096,
            "temperature": 0.1,
        }
        return _config_cache
    except json.JSONDecodeError:
        raise ValueError(f"Error al leer el archivo de configuración: {config_path}")

def get_config_value(key: str, default: Any = None) -> Any:
    """
    Obtiene un valor de la configuración
    
    Args:
        key: Clave de configuración
        default: Valor por defecto si no existe
        
    Returns:
        Any: Valor de configuración
    """
    config = load_config()
    return config.get(key, default)

def get_agent_verbosity_level() -> int:
    """Obtiene el nivel de verbosidad del agente"""
    return get_config_value("agent_verbosity_level", -1)

def get_generate_prompt_context_file() -> bool:
    """Obtiene si se debe generar el archivo de contexto del prompt"""
    return get_config_value("generate_prompt_context_file", True)

def get_memory_subagents_persistent() -> bool:
    """Obtiene si se debe persistir la memoria de los subagentes"""
    return get_config_value("memory_subagents_persistent", False)

def get_enable_skills() -> bool:
    """Obtiene si las skills están habilitadas"""
    return get_config_value("enable_skills", False)

def get_project_hash() -> str:
    """Obtiene el hash del proyecto"""
    return get_config_value("project_hash", "")

def get_enabled_subagents() -> bool:
    """Obtiene si los subagentes están habilitados"""
    return get_config_value("enable_subagents", True)

def get_qdrant_host() -> str:
    """Obtiene el host de Qdrant"""
    return get_config_value("qdrant_host", "localhost")

def get_qdrant_port() -> int:
    """Obtiene el puerto de Qdrant"""
    return get_config_value("qdrant_port", 6333)

def get_main_agent_name() -> str:
    """Obtiene el nombre del agente principal"""
    return get_config_value("main_agent_name", "Orquestador")

def get_start_app_clean_files() -> bool:
    """Obtiene si se deben limpiar los archivos al iniciar la app"""
    return get_config_value("start_app_clean_files", False)

def get_max_messages_memory() -> int:
    """Obtiene el número máximo de mensajes en memoria"""
    return int(get_config_value("max_messages_memory", 50))

# Funciones específicas para mapeo de variables
def get_provider() -> str:
    """Obtiene el proveedor configurado"""
    return get_config_value("provider", "Ollama")

def get_api_base() -> str:
    """Obtiene la URL base de la API"""
    return get_config_value("api_base_url", "http://localhost:11434")

def get_openrouter_api_key() -> Optional[str]:
    """Obtiene la API key de OpenRouter"""
    return get_config_value("open_router_api_key")

def get_model_id() -> str:
    """Obtiene el ID del modelo"""
    return get_config_value("model", None)

def get_max_steps() -> int:
    """Obtiene el número máximo de pasos"""
    return int(get_config_value("max_steps", 30))

def get_theme() -> str:
    """Obtiene el tema configurado"""
    return get_config_value("theme", "dracula")

def get_project_base() -> str:
    """Obtiene el directorio base del proyecto"""
    return os.getcwd()

def get_enable_debugger() -> bool:
    """Obtiene si el modo debugger está habilitado"""
    return get_config_value("debugger", False)

def get_num_ctx() -> int:
    """Obtiene el número máximo de contextos"""
    return int(get_config_value("num_ctx", 4096))

def get_temperature() -> float:
    """Obtiene la temperatura del modelo"""
    return float(get_config_value("temperature", 0.1))

def reload_config():
    """Recarga la configuración desde el archivo"""
    global _config_cache
    _config_cache = None
    load_config()
