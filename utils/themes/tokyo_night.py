#!/usr/bin/env python3
"""
Tema Tokyo Night para terminal
"""

from rich.theme import Theme
from rich.style import Style


tokyo_night_theme = Theme({
    # Estilos principales con paleta Tokyo Night
    "header": Style(color="#7dcfff", bold=True),  # Clases/Atributos (cyan)
    "success": Style(color="#9ece6a"),  # Strings (verde)
    "error": Style(color="#f7768e"),  # Constantes/Números (rojo)
    "warning": Style(color="#e0af68"),  # Amarillo Tokyo Night
    "info": Style(color="#7aa2f7"),  # Funciones (azul)
    "user": Style(color="#bb9af7"),  # Variables/Operadores (púrpura)
    "agent": Style(color="#9ece6a"),  # Strings (verde)
    "command": Style(color="#7dcfff"),  # Clases/Atributos (cyan)
    "thinking": Style(color="#7aa2f7"),  # Funciones (azul)
    "border": Style(color="#bb9af7"),  # Variables/Operadores (púrpura)
    "tool_name": Style(color="#7dcfff", bold=True),  # Clases/Atributos (cyan)
    "separator_line": Style(color="#565f89", dim=True),  # Comentarios
    
    # Estilos secundarios
    "subtitle": Style(color="#565f89", dim=True),  # Comentarios
    "comment": Style(color="#565f89"),  # Comentarios
    "foreground": Style(color="#c0caf5"),  # Texto principal
    
    # Estilos para animación
    "animation.shadow": Style(color="#24283b"),  # Fondo alternativo
    "animation.medium": Style(color="#7aa2f7"),  # Funciones (azul)
    "animation.solid": Style(color="#7dcfff"),  # Clases/Atributos (cyan)
    
    # Estilos para componentes
    "panel.title": Style(color="#7dcfff", bold=True),  # Clases/Atributos (cyan)
    "panel.border": Style(color="#bb9af7"),  # Variables/Operadores (púrpura)
    "separator": Style(color="#565f89"),  # Comentarios
    
    # Estilos para comandos
    "command.name": Style(color="#7dcfff"),  # Clases/Atributos (cyan)
    "command.desc": Style(color="#c0caf5"),  # Texto principal
})
