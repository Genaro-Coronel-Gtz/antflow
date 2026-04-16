#!/usr/bin/env python3
"""
Tema AntFlow para terminal
"""

from rich.theme import Theme
from rich.style import Style


antflow_theme = Theme({
    # Estilos principales con la paleta AntFlow
    "header": Style(color="#6FE8E0", bold=True),  # AntFlow Cyan
    "success": Style(color="#4FC3D9"),  # AntFlow Aqua
    "error": Style(color="#FF6B35"),  # Naranja para errores (contraste)
    "warning": Style(color="#FFA500"),  # Naranja para warnings
    "info": Style(color="#2E8BEF"),  # AntFlow Blue
    "user": Style(color="#1E5FB8"),  # AntFlow Deep Blue
    "prompt": Style(color="#1E5FB8"),  # AntFlow Deep Blue
    "agent": Style(color="#4FC3D9"),  # AntFlow Aqua
    "command": Style(color="#6FE8E0"),  # AntFlow Cyan
    "thinking": Style(color="#2E8BEF"),  # AntFlow Blue
    "border": Style(color="#1E5FB8"),  # AntFlow Deep Blue
    "tool_name": Style(color="#6FE8E0", bold=True),  # AntFlow Cyan
    
    # Estilos secundarios
    "subtitle": Style(color="#C9D6E2", dim=True),  # Soft Text
    "comment": Style(color="#163A73"),  # Hex Glow
    "foreground": Style(color="#C9D6E2"),  # Soft Text
    "separator_line": Style(color="#163A73", dim=False),  # Hex Glow
    
    # Estilos para animación
    "animation.shadow": Style(color="#163A73"),  # Hex Glow
    "animation.medium": Style(color="#2E8BEF"),  # AntFlow Blue
    "animation.solid": Style(color="#6FE8E0"),  # AntFlow Cyan
    
    # Estilos para componentes
    "panel.title": Style(color="#6FE8E0", bold=True),  # AntFlow Cyan
    "panel.border": Style(color="#1E5FB8"),  # AntFlow Deep Blue
    "separator": Style(color="#163A73"),  # Hex Glow
    
    # Estilos para comandos
    "command.name": Style(color="#6FE8E0"),  # AntFlow Cyan
    "command.desc": Style(color="#C9D6E2"),  # Soft Text
})
