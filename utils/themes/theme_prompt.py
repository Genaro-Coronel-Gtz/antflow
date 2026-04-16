#!/usr/bin/env python3
"""
Gestor de estilos de prompt según el tema de AntFlow
"""

from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from utils.core.config_loader import get_theme, get_provider, get_model_id
import datetime
import shutil


def get_status_tool_bar():
    try:
        from ..tools.utils.common import get_current_tool, get_current_subagent
        current = get_current_tool()
        if current["name"]:
            status_emoji = {
                "using": "🔧",
                "completed": "✅", 
                "failed": "❌",
                "idle": "⚡"
            }.get(current["status"], "⚡")
            tool_info = f"{status_emoji} {current['name']}"
        else:
            tool_info = "⚡ Thinking"
        
        # Obtener estado actual del subagente
        try:
            current_subagent = get_current_subagent()
        except Exception as e:
            current_subagent = {"name": None}
        
        # Construir info del agente
        agent_info = ""
        if current_subagent["name"]:
            agent_info = f"{current_subagent['name']} -- "
        
        # Agregar a la tabla: texto y barra a la izquierda, herramienta a la derecha
        if agent_info and tool_info:
            text = f"[tool_name]{agent_info}{tool_info}"
        else:
            text = ""
        
        return text
    except Exception as e:
        return "Agent"


def get_prompt_style():
    """Obtiene el estilo del prompt según el tema configurado"""
    current_theme = get_theme()
    
    # Definir estilos según el tema
    theme_styles = {
        'antflow': {
            'prompt': 'bold fg:#4FC3D9',
            'bottom-toolbar': 'noinherit bg:default',
            'antflow-bar': 'fg:#3e92ed bg:default noinherit',
        },
        'dracula': {
            'prompt': 'bold fg:#50fa7b',
            'bottom-toolbar': 'noinherit bg:default',
            'antflow-bar': 'fg:#50fa7b bg:default noinherit',
        },
        'default': {
            'prompt': 'bold fg:#00ff00',
            'bottom-toolbar': 'noinherit bg:default',
            'antflow-bar': 'fg:#00ff00 bg:default noinherit',
        }
    }
    
    style_config = theme_styles.get(current_theme, theme_styles['default'])
    return Style.from_dict(style_config)


def get_themed_prompt(prompt_text="> "):
    """Devuelve una función de prompt con el estilo del tema actual"""
    style = get_prompt_style()
    
    def themed_prompt():
        return prompt(prompt_text, style=style)
    
    return themed_prompt


def prompt_input(prompt_text="> "):
    """Obtiene entrada con información a la derecha y transparencia real"""
    
    def bottom_toolbar():
        model = get_model_id()
        provider = get_provider()
        texto_info = f"Provider: [{provider}] - Model: [{model}] "

        columns, _ = shutil.get_terminal_size()

        agent_tool = get_status_tool_bar()
        # Calculamos los espacios pero NO les daremos tu clase de estilo
        espacios_blancos = columns - len(texto_info + agent_tool + "   ")
        margen_derecha = " " * max(0, espacios_blancos)
        

        return [
            ('', '\n\n'),
            ('', margen_derecha),
            ('class:antflow-bar', f"{texto_info} - {agent_tool}"),
        ]

    style = get_prompt_style()

    # return prompt(
    #     prompt_text, 
    #     style=style, 
    #     bottom_toolbar=bottom_toolbar,
    # )

    return prompt(prompt_text, style=style)
    
def get_current_theme_name():
    """Obtiene el nombre del tema actual"""
    return get_theme()


def get_theme_colors():
    """Obtiene los colores del tema actual para referencia"""
    theme_colors = {
        'antflow': {
            'primary': '#6FE8E0',      # AntFlow Cyan
            'secondary': '#4FC3D9',    # AntFlow Aqua
            'accent': '#2E8BEF',       # AntFlow Blue
            'background': '#0B1320',   # Background Dark
            'surface': '#163A73',      # Hex Glow
        },
        'dracula': {
            'primary': '#50fa7b',      # Dracula Green
            'secondary': '#8be9fd',    # Dracula Cyan
            'accent': '#ff79c6',       # Dracula Pink
            'background': '#282a36',   # Dracula Background
            'surface': '#44475a',      # Dracula Current Line
        },
        'default': {
            'primary': '#00ff00',      # Classic Green
            'secondary': '#ffffff',    # White
            'accent': '#ffff00',       # Yellow
            'background': '#000000',   # Black
            'surface': '#333333',      # Gray
        }
    }
    
    current_theme = get_theme()
    return theme_colors.get(current_theme, theme_colors['default'])
