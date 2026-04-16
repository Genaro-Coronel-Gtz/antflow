#!/usr/bin/env python3
"""
Animación para el agente pensante usando Rich
"""

import time
import threading
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.panel import Panel
from rich.align import Align


class ThinkingAnimation:
    """Animación de pensamiento usando Rich"""
    
    def __init__(self, console: Optional[Console] = None, style: str = "thinking"):
        """
        Inicializa la animación
        
        Args:
            console: Consola Rich (opcional)
            style: Estilo para el texto
        """
        self.console = console or Console()
        self.style = style
        self.is_running = False
        self.live = None
        self.progress = None
        self.task_id = None
        
    def start(self):
        """Inicia la animación"""
        if not self.is_running:
            self.is_running = True
            self._start_animation()
    
    def stop(self):
        """Detiene la animación"""
        if self.is_running:
            self.is_running = False
            if self.live:
                self.live.stop()
            if self.progress:
                self.progress.stop()
    
    def _start_animation(self):
        """Inicia la animación de Rich"""
        # Crear progress con animación
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn(f"[{self.style}] Agent working..."),
            console=self.console,
            transient=True,  # Desaparece al terminar
            refresh_per_second=10,
        )
        
        self.task_id = self.progress.add_task("thinking", total=None)
        self.progress.start()
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


class BarAnimation:
    """Animación de barra con caracteres usando Rich"""
    
    def __init__(self, console: Optional[Console] = None, bar_width: int = 40, delay: float = 0.1):
        """
        Inicializa la animación de barra
        
        Args:
            console: Consola Rich (opcional)
            bar_width: Ancho de la barra
            delay: Tiempo entre frames
        """
        self.console = console or Console()
        self.bar_width = bar_width
        self.delay = delay
        self.is_running = False
        self.live = None
        self.thread = None
        
        # Caracteres para la animación
        self.chars = ['░', '▒', '█']
        self.position = 0
        self.direction = 1  # 1 para derecha, -1 para izquierda
    
    def start(self):
        """Inicia la animación"""
        if not self.is_running:
            self.is_running = True
            self._start_animation()
    
    def stop(self):
        """Detiene la animación"""
        if self.is_running:
            self.is_running = False
            if self.live:
                self.live.stop()
            if self.thread:
                self.thread.join(timeout=0.5)
    
    def _create_bar_table(self) -> Table:
        """Crea la tabla con la barra de animación y herramienta al extremo derecho"""
        table = Table(show_header=False, box=None, padding=0, expand=True)
        table.add_column(justify="left", ratio=1)  # Columna izquierda que expande
        table.add_column(justify="right")  # Columna derecha fija
        
        # Crear barra
        bar = [' '] * self.bar_width
        bar[self.position] = self.chars[1]  # ▒ para la posición actual
        
        # Agregar sombras
        if self.direction == 1:  # Moviendo derecha
            if self.position > 0:
                bar[self.position - 1] = self.chars[0]  # ░ sombra izquierda
            if self.position < self.bar_width - 1:
                bar[self.position + 1] = self.chars[2]  # █ sombra derecha
        else:  # Moviendo izquierda
            if self.position > 0:
                bar[self.position - 1] = self.chars[2]  # █ sombra izquierda
            if self.position < self.bar_width - 1:
                bar[self.position + 1] = self.chars[0]  # ░ sombra derecha
        
        # Construir texto con colores
        bar_text = Text()
        for i, char in enumerate(bar):
            if char == self.chars[0]:  # ░
                bar_text.append(char, style="animation.shadow")
            elif char == self.chars[1]:  # ▒
                bar_text.append(char, style="animation.medium")
            elif char == self.chars[2]:  # █
                bar_text.append(char, style="animation.solid")
            else:
                bar_text.append(char)
        
        # Obtener estado actual de la herramienta
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
        except:
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
        left_text = f"[thinking]El agente está pensando... [{bar_text}]"
        right_text = f"[tool_name]{agent_info}{tool_info}"
        
        table.add_row(left_text, right_text)
        return table
    
    def _animate(self):
        """Función de animación en hilo separado"""
        while self.is_running:
            # Actualizar posición
            if self.direction == 1:
                self.position += 1
                if self.position >= self.bar_width - 1:
                    self.position = self.bar_width - 1
                    self.direction = -1
            else:
                self.position -= 1
                if self.position <= 0:
                    self.position = 0
                    self.direction = 1
            
            # Actualizar live display
            if self.live:
                self.live.update(self._create_bar_table())
            
            time.sleep(self.delay)
    
    def _start_animation(self):
        """Inicia la animación con Live"""
        self.live = Live(
            self._create_bar_table(),
            console=self.console,
            refresh_per_second=10,
            transient=True
        )
        
        self.live.start()
        
        # Iniciar animación en hilo separado
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# Función de conveniencia para crear animación
def create_thinking_animation(animation_type: str = "spinner", **kwargs):
    """
    Crea una animación de pensamiento
    
    Args:
        animation_type: Tipo de animación ("spinner" o "bar")
        **kwargs: Argumentos adicionales para la animación
    
    Returns:
        Instancia de animación
    """
    if animation_type == "bar":
        return BarAnimation(**kwargs)
    else:
        return ThinkingAnimation(**kwargs)
