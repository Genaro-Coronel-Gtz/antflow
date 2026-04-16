#!/usr/bin/env python3
"""
Tema Dracula para terminal
"""

from rich.theme import Theme
from rich.style import Style


dracula_theme = Theme({
    # Estilos principales
    "header": Style(color="bright_cyan", bold=True),
    "success": Style(color="bright_green"),
    "error": Style(color="bright_red"),
    "warning": Style(color="bright_yellow"),
    "info": Style(color="bright_blue"),
    "user": Style(color="bright_magenta"),
    "agent": Style(color="cyan"),
    "command": Style(color="bright_green"),
    "thinking": Style(color="bright_cyan"),
    "border": Style(color="bright_magenta"),
    "tool_name": Style(color="bright_yellow", bold=True),  # Naranja tipo amarillo brillante
    "separator_line": Style(color="bright_magenta", dim=True),  # Línea suave delgada
    
    # Estilos secundarios
    "subtitle": Style(color="white", dim=True),
    "comment": Style(color="grey50"),
    "foreground": Style(color="bright_magenta"),
    
    # Estilos para animación
    "animation.shadow": Style(color="grey50"),
    "animation.medium": Style(color="bright_cyan"),
    "animation.solid": Style(color="bright_magenta"),
    
    # Estilos para componentes
    "panel.title": Style(color="bright_cyan", bold=True),
    "panel.border": Style(color="bright_magenta"),
    "separator": Style(color="grey50"),
    
    # Estilos para comandos
    "command.name": Style(color="bright_yellow"),
    "command.desc": Style(color="white"),
})
