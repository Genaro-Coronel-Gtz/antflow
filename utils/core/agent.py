#!/usr/bin/env python3
from typing import List, Dict, Any
from utils.core.lazy_loader import LazyLoader
from utils.core.debugger import _turn_off_logs_based_on_config
from utils.core.translator import t

# Variable global para el manejador de señales
skill_manager_instance = None

# Desactivar logs basado en la configuración del debugger
_turn_off_logs_based_on_config()

# importar LiteLLM con lazy loading
litellm_module = LazyLoader.import_module('litellm')
litellm = litellm_module

# Configuración adicional de LiteLLM
litellm.set_verbose = False
litellm.suppress_debug_info = True
litellm.success_callback = []
litellm.failure_callback = []

# importar smolagents con lazy loading
smolagents_module = LazyLoader.import_module('smolagents')
LiteLLMModel = smolagents_module.LiteLLMModel
CodeAgent = smolagents_module.CodeAgent

# Importar sistema de memoria con lazy loading
from utils.memory.memory_agent import agent_memory
from utils.subagents.subagents_manager import load_enabled_agents
from utils.core.config_loader import get_provider, get_openrouter_api_key, get_api_base, get_model_id, get_max_steps, get_project_base, get_agent_verbosity_level, get_main_agent_name
from utils.core.agent_steps import agent_step_callback

# Constantes del sistema
AGENT_NAME = get_main_agent_name()
PROJECT_BASE = get_project_base()
MODEL_ID = get_model_id()
PROVIDER = get_provider()
OPENROUTER_API_KEY = get_openrouter_api_key()
API_BASE = get_api_base()
MAX_STEPS = get_max_steps()
VERBOSITY_LEVEL = get_agent_verbosity_level()

def load_system_prompt():
    from os import path
    """Carga el contenido de prompt.md"""
    try:
        if path.exists(".antflow/prompt.md"):
            with open(".antflow/prompt.md", "r", encoding="utf-8") as f:
                content = f.read()
            return content.replace("{PROJECT_BASE}", PROJECT_BASE)
        return f"Eres un Agente Arquitecto Senior. Directorio: {PROJECT_BASE}"
    except Exception as e:
        return f"Agente Arquitecto. Contexto: {PROJECT_BASE}"

# Variable global para el prompt
SYSTEM_PROMPT = load_system_prompt()

# Variable global para el contexto de prompts (lazy loading)
prompt_context = None

def get_prompt_context():
    """Obtiene la instancia de PromptContext (lazy loading)"""
    global prompt_context
    if prompt_context is None:
        from utils.memory.prompt_context import PromptContext  # Importación lazy
        prompt_context = PromptContext()
    return prompt_context

from utils.core.shared import create_model, load_enabled_tools

# Obtener las validaciones para respuestas finales (global)

# --- INICIALIZACIÓN DEL AGENTE ---
# El CodeAgent de smolagents usa argumentos posicionales para las herramientas y el modelo.

agent = CodeAgent(
    tools=load_enabled_tools(),
    managed_agents=load_enabled_agents(),
    model=create_model(),
    add_base_tools=True,
    max_steps=MAX_STEPS,
    verbosity_level=VERBOSITY_LEVEL,
    step_callbacks=[agent_step_callback],
)
# Asignamos un nombre al agente principal para logging
agent.name = AGENT_NAME


def run_agent_task(user_query: str, cancellation_token=None) -> str:
    from sys import stderr
    """
    Ejecuta la tarea con memoria de conversación optimizada
    """
    # ── Helper inline ─────────────────────────────────────────────────────
    def _cancelled():
        return cancellation_token is not None and cancellation_token.is_cancelled()
    # ─────────────────────────────────────────────────────────────────────

    log_file = open(".antflow/errors.log", "a", encoding="utf-8")
    audit_file = open(".antflow/antflow.log", "a", encoding="utf-8")
    original_stderr = stderr
    stderr = log_file

    try:
        from datetime import datetime
        audit_file.write(f"[{datetime.now().isoformat()}] TAREA INICIADA: {user_query[:100]}...\n")

        # Chequeo temprano — antes de tocar memoria o archivos
        if _cancelled():
            return "", {}

        if not agent_memory.get_history():
            current_system_instructions = load_system_prompt()
            agent_memory.initialize_with_system_prompt(current_system_instructions)

        agent_memory.add_message("user", user_query)
        full_history = agent_memory.get_history()

        from utils.core.config_loader import get_max_messages_memory
        max_messages = get_max_messages_memory()
        conversation_limit = max_messages - 1

        system_msg = next((msg for msg in full_history if msg["role"] == "system"), None)
        conversation_history = agent_memory.get_conversation_history()[-conversation_limit:]

        conversation_context = ""
        for msg in conversation_history:
            if msg["role"] == "user":
                conversation_context += f"USER: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                conversation_context += f"ASSISTANT: {msg['content']}\n\n"

        full_prompt = f"{system_msg['content']}\n\n{conversation_context}" if system_msg else conversation_context

        get_prompt_context().save_prompt_context(
            user_text=user_query,
            enabled_skills=[],
            active_skills_ids=[],
            skills_search_results=[],
            skills_context="",
            final_prompt=full_prompt,
            system_prompt=load_system_prompt(),
            search_stats={}
        )

        # Chequeo justo antes de la llamada costosa al LLM
        if _cancelled():
            return "", {}

        response = agent.run(full_prompt, return_full_result=True)

        # Chequeo después — por si fue cancelado mientras el LLM respondía
        if _cancelled():
            return "", {}

        assistant_response = str(response.output)
        token_usage = response.token_usage
        timing = response.timing

        agent_memory.add_message("assistant", assistant_response)
        audit_file.write(f"[{datetime.now().isoformat()}] TAREA COMPLETADA\n\n")

        return assistant_response, {
            "token_usage": token_usage,
            "timing": timing,
            "state": response.state
        }

    except Exception as e:
        error_msg = f"\n FATAL ERROR: {str(e)}\n"
        log_file.write(error_msg)
        audit_file.write(f"[{datetime.now().isoformat()}] ERROR: {str(e)}\n\n")
        return f" El agente se detuvo: {str(e)}. Revisa .antflow/errors.log para más detalles.", ""

    finally:
        log_file.flush()
        stderr = original_stderr
        log_file.close()
        audit_file.close()

def clear_agent_memory():
    """Limpia la memoria del agente"""
    global agent_memory
    agent_memory.clear()
