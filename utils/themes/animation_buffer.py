# utils/core/animation_buffer.py
"""Buffer dedicado para animación sin afectar otras áreas de la UI"""

import os
import sys
from typing import Optional, TextIO
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text
from datetime import datetime
from threading import Lock

class AnimationBuffer:
    """Buffer dedicado para animación que no afecta a stdout principal"""
    
    def __init__(self):
        self.console = Console(file=self._get_null_file(), width=80, height=1)
        self.live = None
        self.is_running = False
        self._lock = Lock()
        self._toolbar_callback = None
        
    def set_toolbar_callback(self, callback):
        """Establece función callback para actualizar la toolbar de main.py"""
        with self._lock:
            self._toolbar_callback = callback
        
    def _get_null_file(self) -> TextIO:
        """Retorna un archivo nulo para evitar impresión en stdout"""
        try:
            # En Unix/Linux
            return open(os.devnull, 'w')
        except AttributeError:
            # En Windows
            return open('nul', 'w')
    
    def start_animation(self):
        """Inicia la animación en el buffer dedicado"""
        with self._lock:
            if not self.is_running:
                self.is_running = True
                self._start_live_display()
    
    def stop_animation(self):
        """Detiene la animación"""
        with self._lock:
            if self.is_running:
                self.is_running = False
                if self.live:
                    self.live.stop()
                # Notificar que la animación se detuvo
                if self._toolbar_callback:
                    self._toolbar_callback(None, None)  # None para indicar que se detuvo
    
    def _start_live_display(self):
        """Inicia el display live con la animación"""
        try:
            # Crear tabla inicial para la animación
            table = self._create_animation_table()
            
            self.live = Live(
                table,
                console=self.console,
                refresh_per_second=10,
                transient=False,  # No desaparecer al terminar
                auto_refresh=False  # Control manual de actualización
            )
            self.live.start()
            
            # Iniciar actualización manual
            import threading
            self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self._update_thread.start()
            
        except Exception as e:
            print(f"Error iniciando animación en buffer: {e}")
    
    def _create_animation_table(self) -> Table:
        """Crea la tabla de animación para el buffer"""
        table = Table(show_header=False, box=None, padding=0, expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="right")
        
        # Animación simple
        bar_chars = ['░', '▒', '█']
        position = 0
        direction = 1
        bar_width = 20
        
        # Crear barra animada
        bar = [' '] * bar_width
        bar[position] = bar_chars[1]  # ▒ en posición actual
        
        # Agregar sombras
        if direction == 1:
            if position > 0:
                bar[position - 1] = bar_chars[0]  # ░ sombra izquierda
            if position < bar_width - 1:
                bar[position + 1] = bar_chars[2]  # █ sombra derecha
        
        # Construir texto con colores
        bar_text = Text()
        for i, char in enumerate(bar):
            if char == bar_chars[0]:
                bar_text.append(char, style="dim")
            elif char == bar_chars[1]:
                bar_text.append(char, style="bold")
            elif char == bar_chars[2]:
                bar_text.append(char, style="bold blue")
            else:
                bar_text.append(char)
        
        # Obtener información actual
        try:
            from ..tools.utils.common import get_current_tool, get_current_subagent
            current = get_current_tool()
            if current["name"]:
                status_emoji = {
                    "using": "[~]",
                    "completed": "[✓]", 
                    "failed": "[✗]",
                    "idle": "⚡"
                }.get(current["status"], "⚡")
                tool_info = f"{status_emoji} {current['name']}"
            else:
                tool_info = "⚡ Thinking"
        except:
            tool_info = "⚡ Thinking"
        
        try:
            current_subagent = get_current_subagent()
        except:
            current_subagent = {"name": None}
        
        # Construir textos
        agent_info = ""
        if current_subagent["name"]:
            agent_info = f"{current_subagent['name']} - "
        
        left_text = f"[{bar_text}]"
        right_text = f"{agent_info}{tool_info}"
        
        # Actualizar directamente la toolbar de main.py
        if self._toolbar_callback:
            self._toolbar_callback(left_text, right_text)
        
        table.add_row(left_text, right_text)
        return table
    
    def _update_loop(self):
        """Bucle de actualización de la animación"""
        import time
        
        position = 0
        direction = 1
        bar_width = 20
        
        while self.is_running:
            try:
                # Actualizar posición
                if direction == 1:
                    position += 1
                    if position >= bar_width - 1:
                        position = bar_width - 1
                        direction = -1
                else:
                    position -= 1
                    if position <= 0:
                        position = 0
                        direction = 1
                
                # Crear nueva tabla y actualizar
                table = self._create_animation_table_with_position(position, direction)
                if self.live:
                    self.live.update(table)
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error en bucle de animación: {e}")
                break
    
    def _create_animation_table_with_position(self, position: int, direction: int) -> Table:
        """Crea tabla con posición específica para evitar recálculos"""
        table = Table(show_header=False, box=None, padding=0, expand=True)
        table.add_column(justify="left", ratio=1)
        table.add_column(justify="right")
        
        bar_chars = ['░', '▒', '█']
        bar_width = 20
        
        # Crear barra con posición específica
        bar = [' '] * bar_width
        bar[position] = bar_chars[1]
        
        # Agregar sombras
        if direction == 1:
            if position > 0:
                bar[position - 1] = bar_chars[0]
            if position < bar_width - 1:
                bar[position + 1] = bar_chars[2]
        else:
            if position > 0:
                bar[position - 1] = bar_chars[2]
            if position < bar_width - 1:
                bar[position + 1] = bar_chars[0]
        
        # Construir texto
        bar_text = Text()
        for i, char in enumerate(bar):
            if char == bar_chars[0]:
                bar_text.append(char, style="dim")
            elif char == bar_chars[1]:
                bar_text.append(char, style="bold")
            elif char == bar_chars[2]:
                bar_text.append(char, style="bold blue")
            else:
                bar_text.append(char)
        
        # Reutilizar información existente
        try:
            from ..tools.utils.common import get_current_tool, get_current_subagent
            current = get_current_tool()
            if current["name"]:
                status_emoji = {
                    "using": "[~]",
                    "completed": "[✓]", 
                    "failed": "[✗]",
                    "idle": "⚡"
                }.get(current["status"], "⚡")
                tool_info = f"{status_emoji} {current['name']}"
            else:
                tool_info = "⚡ Thinking"
        except:
            tool_info = "⚡ Thinking"
        
        try:
            current_subagent = get_current_subagent()
        except:
            current_subagent = {"name": None}
        
        agent_info = ""
        if current_subagent["name"]:
            agent_info = f"{current_subagent['name']} - "
        
        left_text = f"[{bar_text}]"
        right_text = f"{agent_info}{tool_info}"
        
        # Actualizar directamente la toolbar de main.py
        if self._toolbar_callback:
            self._toolbar_callback(left_text, right_text)
        
        table.add_row(left_text, right_text)
        return table

# Instancia global única
_animation_buffer = AnimationBuffer()

def get_animation_buffer():
    """Retorna el buffer de animación global"""
    return _animation_buffer

def set_toolbar_callback(callback):
    """Establece el callback para la toolbar"""
    _animation_buffer.set_toolbar_callback(callback)
