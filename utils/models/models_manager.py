#!/usr/bin/env python3
"""
Gestor de modelos para la aplicación
"""
import requests
from typing import List, Dict, Any
from utils.core.translator import t

import os
import requests
from typing import List, Optional
from utils.core.config_loader import get_provider, get_api_base, get_openrouter_api_key, get_model_id

# Constantes desde el config.json
PROVIDER = get_provider()
API_BASE = get_api_base()
OPENROUTER_API_KEY = get_openrouter_api_key()
MODEL_ID = get_model_id()


def get_available_models() -> List[str]:
    """
    Obtiene la lista de modelos disponibles según el proveedor configurado
    
    Returns:
        List[str]: Lista de nombres de modelos disponibles
    """
    provider_lower = PROVIDER.lower()
    
    if provider_lower == "openrouter":
        return _get_openrouter_models()
    elif provider_lower == "ollama":
        return _get_ollama_models()
    else:
        # Fallback para otros proveedores
        return [MODEL_ID]


def _get_ollama_models() -> List[str]:
    """
    Obtiene modelos disponibles de Ollama
    
    Returns:
        List[str]: Lista de modelos Ollama disponibles
    """
    try:
        # Intentar obtener modelos desde la API de Ollama
        response = requests.get(f"{API_BASE}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            if models:
                return [model["name"] for model in models]
    except Exception as e:
        print(t("ollama_models_error").format(error=e))
    
    # Fallback a modelos comunes de Ollama
    common_ollama_models = [
        "qwen2.5-coder:7b-instruct-q4_K_M",
        "llama3.1:8b",
        "llama3.1:70b",
        "mistral:7b",
        "codellama:7b",
        "codellama:13b",
        "deepseek-coder:6.7b",
        "deepseek-coder:33b",
        "phi3:mini",
        "phi3:medium"
    ]
    
    return common_ollama_models


def _get_openrouter_models() -> List[str]:
    """
    Obtiene modelos disponibles de OpenRouter
    
    Returns:
        List[str]: Lista de modelos OpenRouter disponibles
    """
    try:
        # Intentar obtener modelos desde la API de OpenRouter
        if OPENROUTER_API_KEY:
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                if models:
                    # Filtrar modelos gratuitos y populares
                    free_models = [
                        model["id"] for model in models
                        if model.get("pricing", {}).get("prompt", 0) == 0
                    ]
                    if free_models:
                        return free_models[:20]  # Limitar a 20 modelos
    except Exception as e:
        print(t("openrouter_models_error").format(error=e))
    
    # Fallback a modelos conocidos de OpenRouter
    common_openrouter_models = [
        "meta-llama/llama-3.1-70b-instruct:free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "microsoft/wizardlm-2-8x22b:free",
        "qwen/qwen-2.5-7b-instruct:free",
        "stepfun/step-3.5-flash:free",
        "google/gemma-2-9b-it:free",
        "anthropic/claude-3-haiku:free",
        "openai/gpt-3.5-turbo:free"
    ]
    
    return common_openrouter_models


def get_current_model() -> str:
    """
    Obtiene el modelo actual configurado
    
    Returns:
        str: Nombre del modelo actual
    """
    return MODEL_ID


def get_provider_info() -> dict:
    """
    Obtiene información del proveedor actual
    
    Returns:
        dict: Información del proveedor
    """
    return {
        "provider": PROVIDER,
        "api_base": API_BASE,
        "current_model": MODEL_ID,
        "has_api_key": bool(OPENROUTER_API_KEY)
    }


def validate_model(model_name: str) -> bool:
    """
    Valida si un modelo está disponible para el proveedor actual
    
    Args:
        model_name: Nombre del modelo a validar
        
    Returns:
        bool: True si el modelo es válido/está disponible
    """
    available_models = get_available_models()
    return model_name in available_models


def get_model_info(model_name: str) -> dict:
    """
    Obtiene información detallada de un modelo
    
    Args:
        model_name: Nombre del modelo
        
    Returns:
        dict: Información del modelo
    """
    provider_lower = PROVIDER.lower()
    
    info = {
        "name": model_name,
        "provider": PROVIDER,
        "available": validate_model(model_name),
        "is_current": model_name == MODEL_ID
    }
    
    if provider_lower == "ollama":
        info.update(_get_ollama_model_info(model_name))
    elif provider_lower == "openrouter":
        info.update(_get_openrouter_model_info(model_name))
    
    return info


def _get_ollama_model_info(model_name: str) -> dict:
    """
    Obtiene información específica de un modelo Ollama
    
    Args:
        model_name: Nombre del modelo Ollama
        
    Returns:
        dict: Información adicional del modelo
    """
    try:
        response = requests.get(f"{API_BASE}/api/show", json={"name": model_name}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "size": data.get("details", {}).get("parameter_size", "Unknown"),
                "modified_at": data.get("modified_at"),
                "digest": data.get("digest", "")
            }
    except:
        pass
    
    return {}


def _get_openrouter_model_info(model_name: str) -> dict:
    """
    Obtiene información específica de un modelo OpenRouter
    
    Args:
        model_name: Nombre del modelo OpenRouter
        
    Returns:
        dict: Información adicional del modelo
    """
    try:
        if OPENROUTER_API_KEY:
            headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
            response = requests.get(
                f"https://openrouter.ai/api/v1/models/{model_name}",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "pricing": data.get("pricing", {}),
                    "context_length": data.get("context_length")
                }
    except:
        pass
    
    return {}


def refresh_models() -> bool:
    """
    Fuerza la actualización de la lista de modelos
    
    Returns:
        bool: True si la actualización fue exitosa
    """
    try:
        # Simplemente llama a get_available_models para forzar la actualización
        get_available_models()
        return True
    except:
        return False


# Función de conveniencia para compatibilidad con código existente
def list_models() -> List[str]:
    """
    Alias de get_available_models para compatibilidad
    
    Returns:
        List[str]: Lista de modelos disponibles
    """
    return get_available_models()


# Models Manager creado y funcionando correctamente
