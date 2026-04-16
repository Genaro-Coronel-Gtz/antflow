#!/usr/bin/env python3
"""
Estilos centralizados para toda la aplicación
Usado por ColoredLogger y main.py
"""

import json
import os
import sys
from prompt_toolkit.styles import Style
from enum import Enum
from utils.core.config_loader import get_theme

# ==============================
# ENUMS PARA ESTILOS SEGUROS
# ==============================

class UI(Enum):
    """Estilos de interfaz de usuario"""
    separator = "separator"
    input_prefix = "input-prefix"
    log_area = "log-area"
    hint_text = "hint-text"
    animation_shadow = "animation.shadow"
    animation_medium = "animation.medium"
    animation_solid = "animation.solid"
    tool_name = "tool_name"
    thinking = "thinking"
    toolbar_left = "toolbar-left"
    toolbar_right = "toolbar-right"
    toolbar_bg = "toolbar-bg"
    skill_input_prefix = "skill.input-prefix"
    text_area = "text-area"
    text_area_focused = "text-area focused"
    text_area_prompt = "text-area.prompt"
    cursor_line = "cursor-line"
    button = "button"
    button_focused = "button.focused"
    button_arrow = "button.arrow"
    banner = "banner"

class LOGS(Enum):
    """Estilos de logging"""
    header = "header"
    success = "success"
    error = "error"
    warning = "warning"
    info = "info"
    user = "user"
    prompt = "prompt"
    agent = "agent"
    command = "command"
    thinking = "thinking"
    border = "border"
    tool_name = "tool_name"
    subtitle = "subtitle"
    comment = "comment"
    foreground = "foreground"
    separator_line = "separator_line"
    animation_shadow = "animation_shadow"
    animation_medium = "animation_medium"
    animation_solid = "animation_solid"
    panel_title = "panel_title"
    panel_border = "panel_border"
    separator = "separator"
    command_name = "command_name"
    command_desc = "command_desc"
    default = "default"
    dim = "dim"
    subagent = "subagent"
    notice = "notice"
    accent = "accent"
    fail = "fail"
    fail_dim = "fail_dim"
    succes_dim = "succes_dim"
    succes_strong = "succes_strong"


default_colors = {
                    "header": "#6EB3F3",
                    "success": "#6BE995",
                    "error": "#FF8585",
                    "warning": "#FFC163",
                    "info": "#2E8BEF",
                    "user": "#D8E3EA",
                    "prompt": "#1E5FB8",
                    "agent": "#D8F4F0",
                    "command": "#8FEBE4",
                    "thinking": "#60A5FA",
                    "border": "#1D77DD",
                    "tool_name": "#ADFFC0",
                    "subtitle": "#6C9BB0",
                    "comment": "#AFEEE8",
                    "foreground": "#B8D4F0",
                    "separator_line": "#DDD6FE ",
                    "animation_shadow": "#1E293B",
                    "animation_medium": "#8EC7F5",
                    "animation_solid": "#6FE8E0",
                    "panel_title": "#CFF1EC",
                    "panel_border": "#6EB3F3",
                    "separator": "#7BA8C4",
                    "command_name": "#5FD5CC",
                    "command_desc": "#8AB5D8",
                    "default": "#C9D6E2",
                    "dim": "#B8D4F0",
                    "subagent": "#8CF4AA",
                    "notice": "#FFDD9B",
                    "accent": "#A78BFA",
                    "fail": "#FF9F9F",
                    "fail_dim": "#FFB9B9",
                    "succes_dim": "#ADFFC0",
                    "succes_strong": "#39C56B"
                }


# ==============================
# CONFIGURACIÓN DE TEMAS
# ==============================
def load_theme(theme_name):
    """Carga un tema desde el archivo JSON correspondiente"""
    # Obtener la ruta base de manera más robusta
    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
        # Estamos ejecutando como binario compilado
        base_path = sys._MEIPASS
        theme_path = os.path.join(base_path, "utils", "themes", "custom", f"{theme_name}.json")
    else:
        # Estamos ejecutando como script normal
        base_path = os.path.dirname(os.path.abspath(__file__))
        theme_path = os.path.join(base_path, "custom", f"{theme_name}.json")
    
    try:
        with open(theme_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Advertencia: No se encontró el tema '{theme_name}' en {theme_path}")
        # Retornar tema por defecto si no se encuentra el archivo
        return default_colors

    except json.JSONDecodeError as e:
        print(f"Error al decodificar el tema '{theme_name}': {e}")
        return {}

# Cargar el tema desde la configuración
theme_selected = get_theme()
current_theme = load_theme(theme_selected)

# ==============================
# ESTILOS DE LOGGING
# ==============================
LOG_STYLES = {}

# Cargar estilos desde el tema actual
for log_key in LOGS:
    key_name = log_key.value
    if key_name in current_theme:
        LOG_STYLES[key_name] = current_theme[key_name]
    else:
        # Valores por defecto si no están en el tema
        default_values = default_colors

        LOG_STYLES[key_name] = default_values.get(key_name, "#ffffff")

# ==============================
# ESTILOS DE UI
# ==============================
UI_STYLES = {
    UI.separator.value:        "bg:#333333",
    UI.input_prefix.value:     "bold ansicyan",
    UI.log_area.value:         "",
    UI.hint_text.value:        "italic #7BA8C4",
    UI.animation_shadow.value: "#A78BFA",
    UI.animation_medium.value: "#A78BFA",
    UI.animation_solid.value:  "#A78BFA",
    UI.tool_name.value:        "bold #ADFFC0",
    UI.thinking.value:         "italic #60A5FA",
    UI.toolbar_left.value:     "#FFDD9B",
    UI.toolbar_right.value:    "bold #ADFFC0",
    UI.toolbar_bg.value:       "bg:#1E293B",
    UI.banner.value:           "bg:#1E293B",

    # Inputs del skill dialog
    UI.skill_input_prefix.value:    f"bg:#1E293B #2E8BEF",
    UI.text_area.value:              f"bg:#1E293B #B8D4F0",
    UI.text_area_focused.value:      f"bg:#1E293B #B8D4F0",
    UI.text_area_prompt.value:       f"bg:#1E293B #2E8BEF",
    UI.cursor_line.value:            f"bg:#1E293B",

    # Botones
    UI.button.value:                 "bg:#1E293B #B8D4F0",
    UI.button_focused.value:         "bg:#6FE8E0 bold #1E293B",
    UI.button_arrow.value:           "#6FE8E0",
}

# ==============================
# ESTILOS COMPLETOS COMBINADOS
# ==============================
ALL_STYLES = {
    **UI_STYLES,
    **LOG_STYLES,
}

# Función para obtener el Style de prompt_toolkit
def get_app_style():
    """Retorna el objeto Style configurado para la aplicación"""
    return Style.from_dict(ALL_STYLES)

# ==============================
# CONSTANTES DE COLOR
# ==============================
class Colors:
    """Constantes de color para fácil referencia"""
    CYAN = "#6FE8E0"
    GREEN = "#6BE995"
    RED = "#FF8585"
    ORANGE = "#FFC163"
    PURPLE = "#A78BFA"
    WHITE = "#B8D4F0"
    BLUE = "#2E8BEF"
    GRAY = "#94A3B8"
    PINK = "#FF9F9F"
    DARK_BG = "#1E293B"
    MEDIUM_BG = "#1E293B"

# ==============================
# TEMAS PREDEFINIDOS
# ==============================
class ThemePresets:
    """Temas predefinidos para diferentes componentes"""
    
    @staticmethod
    def get_skill_dialog_theme():
        """Tema para el diálogo de skills"""
        return {
            "background": Colors.MEDIUM_BG,
            "text": Colors.WHITE,
            "border": Colors.BLUE,
            "button": Colors.GRAY,
            "button_focused": Colors.PURPLE,
            "input": Colors.BLUE,
        }
    
    @staticmethod
    def get_command_dialog_theme():
        """Tema para el diálogo de comandos"""
        return {
            "background": Colors.DARK_BG,
            "text": Colors.WHITE,
            "border": Colors.GREEN,
            "header": Colors.CYAN,
            "command": Colors.GREEN,
        }
