#!/usr/bin/env python3
"""
Tema Básico (fallback) para terminal
"""

from rich.theme import Theme
from rich.style import Style


basic_theme = Theme({
    "header": Style(color="cyan", bold=True),
    "success": Style(color="green"),
    "error": Style(color="red"),
    "warning": Style(color="yellow"),
    "info": Style(color="blue"),
    "user": Style(color="magenta"),
    "agent": Style(color="green"),
    "command": Style(color="yellow"),
    "thinking": Style(color="cyan"),
    "border": Style(color="magenta"),
    "tool_name": Style(color="yellow", bold=True),  # Naranja tipo amarillo
    "separator_line": Style(color="magenta", dim=True),  # Línea suave delgada
    "subtitle": Style(color="white", dim=True),
    "comment": Style(color="grey50"),
    "foreground": Style(color="white"),
    "animation.shadow": Style(color="grey50"),
    "animation.medium": Style(color="cyan"),
    "animation.solid": Style(color="magenta"),
    "panel.title": Style(color="cyan", bold=True),
    "panel.border": Style(color="magenta"),
    "separator": Style(color="grey50"),
    "command.name": Style(color="yellow"),
    "command.desc": Style(color="white"),
})
