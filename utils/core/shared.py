#!/usr/bin/env python3
"""
Funciones compartidas para el sistema de agentes
"""

import os
import json
from smolagents import LiteLLMModel
from utils.core.config_loader import get_provider, get_openrouter_api_key, get_api_base, get_model_id, get_max_steps, get_project_base, get_temperature, get_num_ctx

PROJECT_BASE = get_project_base()
MODEL_ID = get_model_id()
PROVIDER = get_provider()
OPENROUTER_API_KEY = get_openrouter_api_key()
API_BASE = get_api_base()
TEMPERATURE = get_temperature()
NUM_CTX = get_num_ctx()

def create_model():
    provider_lower = PROVIDER.lower()
    if provider_lower == "openrouter":
        return LiteLLMModel(
            model_id=f"openrouter/{MODEL_ID}",
            model_kwargs={
                "num_ctx": NUM_CTX,
                "temperature": TEMPERATURE,
            },
            api_key=OPENROUTER_API_KEY,
            drop_params=True,
        )
    return LiteLLMModel(
        model_id=f"ollama/{MODEL_ID}", 
        api_base=API_BASE, 
        model_kwargs={
            "num_ctx": NUM_CTX,
            "temperature": TEMPERATURE, # Flexibilidad para diseño de software
        }
    )

def create_custom_model(model_id: str, num_ctx: int = 4096, temperature: float = 0.5,):
    """
    Crea un modelo LiteLLMModel con un ID específico.
    
    Args:
        model_id: ID del modelo (ej: "stepfun/step-3.5-flash:free")
    
    Returns:
        LiteLLMModel: Instancia del modelo configurado
    """
    provider_lower = PROVIDER.lower()
    if provider_lower == "openrouter":
        return LiteLLMModel(
            model_id=f"openrouter/{model_id}",
            model_kwargs={
                "num_ctx": num_ctx,
                "temperature": temperature,
            },
            api_key=OPENROUTER_API_KEY,
            drop_params=True,
        )
    return LiteLLMModel(
        model_id=f"ollama/{model_id}",
        api_base=API_BASE,
        model_kwargs={
            "num_ctx": num_ctx,
            "temperature": temperature, # Flexibilidad para diseño de software
        }
    )

def load_enabled_tools():
    try:
        from ..tools import RepoMapTool, FileWriteTool, FileReadTool, TerminalTool,MarkdownReportTool, SearchTool, ProjectStatusTool, SearchSkillDBTool, CodeFormatterTool, HumanValidationTool
        tool_classes = {
            "RepoMapTool": RepoMapTool, "FileWriteTool": FileWriteTool,
            "FileReadTool": FileReadTool, "TerminalTool": TerminalTool,
            "SearchTool": SearchTool, "MarkdownReportTool": MarkdownReportTool,
            "ProjectStatusTool": ProjectStatusTool, "SearchSkillDBTool": SearchSkillDBTool, 
            "CodeFormatterTool": CodeFormatterTool, "HumanValidationTool": HumanValidationTool
        }
        if os.path.exists(".antflow/tools_config.json"):
            with open(".antflow/tools_config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tools_config = config.get("tools", {})
            enabled_tools = []
            for t_id, t_info in tools_config.items():
                if t_info.get("enabled", True) and t_id in tool_classes:
                    enabled_tools.append(tool_classes[t_id]())
            return enabled_tools
        return [RepoMapTool(), FileWriteTool(), TerminalTool(), FileReadTool(), SearchTool(), MarkdownReportTool(), ProjectStatusTool(), SearchSkillDBTool(), CodeFormatterTool(), HumanValidationTool()]
    except Exception:
        from ..tools import RepoMapTool, FileWriteTool, FileReadTool, TerminalTool, SearchTool, MarkdownReportTool, ProjectStatusTool, SearchSkillDBTool, CodeFormatterTool, HumanValidationTool
        return [RepoMapTool(), FileWriteTool(), TerminalTool(), FileReadTool(), SearchTool(), MarkdownReportTool(), ProjectStatusTool(), SearchSkillDBTool(), CodeFormatterTool(), HumanValidationTool()]