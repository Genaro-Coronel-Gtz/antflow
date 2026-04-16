#!/usr/bin/env python3
"""
Gestor de temas Rich para la aplicación
"""
import os
from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.style import Style
from rich.theme import Theme
from rich.text import Text
from utils.themes import get_theme, list_available_themes
from utils.core.translator import t
# Intentar importar dotenv, si no está disponible, usar variables de entorno directamente
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False


class ThemeManager:
    """Gestor central de temas Rich"""
    
    def __init__(self):
        # Cargar tema desde .env
        self.console = self._create_console()
        self.current_theme_name = self._get_theme_name()
    
    def _get_theme_name(self) -> str:
        """Obtiene el nombre del tema desde variables de entorno"""
        # Cargar .env si está disponible
        if HAS_DOTENV:
            load_dotenv()
        
        from utils.core.config_loader import get_theme
        theme_name = get_theme().lower()
        available_themes = list_available_themes()
        
        if theme_name not in available_themes:
            print(t("theme_not_found").format(theme_name=theme_name, available_themes=available_themes))
            theme_name = "dracula"
        
        return theme_name
    
    def _create_console(self) -> Console:
        """Crea una consola Rich con el tema configurado"""
        theme_name = self._get_theme_name()
        theme = get_theme(theme_name)
        
        return Console(
            theme=theme,
            file=None,  # Usar stdout por defecto
            force_terminal=True,  # Forzar modo terminal
            legacy_windows=False,  # No usar modo legacy de Windows
            no_color=False,  # Permitir colores
            width=None,  # Ancho automático
            color_system="auto",  # Detectar automáticamente
        )
    
    def get_console(self) -> Console:
        """Devuelve la consola Rich actual"""
        return self.console
    
    def get_theme_name(self) -> str:
        """Devuelve el nombre del tema actual"""
        return self.current_theme_name
    
    def reload_theme(self):
        """Recarga el tema desde variables de entorno"""
        self.current_theme_name = self._get_theme_name()
        self.console = self._create_console()
        return self.console
    
    def list_available_themes(self) -> list:
        """Lista todos los temas disponibles"""
        return list_available_themes()
    
    def print_header(self, title: str, subtitle: str = ""):
        """Imprime un encabezado con estilo Rich"""
        from rich.panel import Panel
        from rich.text import Text
        
        # Crear el contenido del panel
        if subtitle:
            content = Text()
            content.append(title, style="header")
            content.append("\n")
            content.append(subtitle, style="subtitle")
        else:
            content = Text(title, style="header")
        
        # Crear el panel
        panel = Panel(
            content,
            border_style="border",
            padding=(1, 2),
            expand=False
        )
        
        # Limpiar pantalla y mostrar panel
        self.console.clear()
        self.console.print(panel)
    
    def print_command_help(self, commands: dict):
        """Imprime ayuda de comandos con estilo Rich"""
        from rich.table import Table
        from rich.columns import Columns
        
        # Calcular el ancho máximo de los comandos
        max_cmd_width = max(len(f"  {cmd}") for cmd in commands.keys())
        max_cmd_width = max(max_cmd_width, 15)  # Mínimo 15 caracteres
        
        # Crear tabla para comandos con ancho dinámico y padding
        table = Table(show_header=False, box=None, padding=(0, 1))  # Padding horizontal
        table.add_column(style="command.name", width=max_cmd_width)
        table.add_column(style="command.desc", ratio=1)  # La segunda columna ocupa el resto
        
        for cmd, desc in commands.items():
            table.add_row(f"  {cmd}", desc)
        
        self.console.print(t("special_commands_title"))
        self.console.print(table)
        self.console.print()
        self.print_separator()
    
    def print_separator(self, char: str = "─", length: int = 150):
        """Imprime un separador con estilo Rich"""
        separator = char * length
        self.console.print(separator, style="separator")
    
    def clear_screen(self):
        """Limpia la pantalla de la terminal"""
        self.console.clear()
    
    # Métodos de conveniencia para colores (sin markup)
    def header(self, text: str) -> str:
        return text  # Rich manejará los colores automáticamente
    
    def success(self, text: str) -> str:
        return text
    
    def error(self, text: str) -> str:
        return text
    
    def warning(self, text: str) -> str:
        return text
    
    def info(self, text: str) -> str:
        return text
    
    def user_input(self, text: str) -> str:
        return text
    
    def agent_output(self, text: str) -> str:
        return text
    
    def command(self, text: str) -> str:
        return text
    
    def thinking(self, text: str) -> str:
        return text

    def command_text(self, text: str) -> str:
        """Retorna texto con estilo command"""
        return f"[agent]{text}[/agent]"
    
    def info_text(self, text: str) -> str:
        """Retorna texto con estilo info"""
        return f"[foreground]{text}[/foreground]"
    
    def prompt(self, text: str):
        """Imprime prompt sin salto de línea"""
        return f"[prompt]{text}[/prompt]"
    
    # Métodos que usan la consola Rich directamente
    def print_header_text(self, text: str):
        """Imprime texto con estilo header"""
        self.console.print(text, style="header")
    
    def print_success_text(self, text: str):
        """Imprime texto con estilo success"""
        self.console.print(text, style="success")
    
    def print_error_text(self, text: str):
        """Imprime texto con estilo error"""
        self.console.print(text, style="error")
    
    def print_warning_text(self, text: str):
        """Imprime texto con estilo warning"""
        self.console.print(text, style="warning")
    
    def exit_system_message(self, text: str):
        """Imprime mensaje de salida del sistema"""
        self.console.print(text, style="success")
    
    def print_info_text(self, text: str):
        """Imprime texto con estilo info"""
        self.console.print(text, style="info")
    
    def print_user_text(self, text: str):
        """Imprime texto con estilo user"""
        self.console.print(text, style="user")
    
    def print_agent_text(self, text: str):
        """Imprime texto con estilo agent"""
        self.console.print(text, style="agent")
    
    def print_command_text(self, text: str):
        """Imprime texto con estilo command"""
        self.console.print(text, style="command")
    
    def print_thinking_text(self, text: str):
        """Imprime texto con estilo thinking"""
        self.console.print(text, style="thinking")
    
    def print_tool_name_text(self, text: str):
        """Imprime texto con estilo tool_name"""
        self.console.print(text, style="tool_name")
    
    def print_separator_line(self):
        """Imprime una línea separadora suave"""
        self.console.rule(style="separator_line")
    
    def print_legend(self, text: str):
        """Imprime texto con estilo legend"""
        self.console.print(text, style="command", justify="center")

    def print_version(self, text: str):
        """Imprime texto con estilo legend"""
        self.console.print(text, style="info", justify="center")

    def print_title_step(self, text: str):
        """Imprime título de step con estilo command usando Text"""
        title_text = Text(text, style="command")
        self.console.print(title_text)

    def print_content_step(self, text: str):
        """Imprime contenido de step con estilo prompt usando Text"""
        content_text = Text(text, style="foreground")
        self.console.print(content_text)
    

# Instancia global del gestor de temas Rich
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """Obtiene la instancia global del gestor de temas Rich"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager

# Instancia global para fácil acceso
theme_manager = get_theme_manager()
console = theme_manager.get_console()

# Para compatibilidad con el sistema antiguo
current_theme = theme_manager
