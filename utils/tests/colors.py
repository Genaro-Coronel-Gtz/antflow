#!/usr/bin/env python3
"""
Script para mostrar los colores de AntFlow con Rich
"""

import sys
import os
from rich.console import Console
from rich.text import Text

def get_antflow_colors():
    """Obtiene los colores del tema AntFlow desde el archivo de configuración"""
    
    # Colores definidos manualmente según el tema antflow.py
    colors_antflow = [
        ("Header", "#6FE8E0"),  # AntFlow Cyan
        ("Success", "#4FC3D9"),  # AntFlow Aqua
        ("Error", "#FF6B35"),   # Naranja para errores
        ("Warning", "#FFA500"),  # Naranja para warnings
        ("Info", "#2E8BEF"),    # AntFlow Blue
        ("User", "#1E5FB8"),    # AntFlow Deep Blue
        ("Prompt", "#1E5FB8"),  # AntFlow Deep Blue
        ("Agent", "#4FC3D9"),   # AntFlow Aqua
        ("Command", "#6FE8E0"),  # AntFlow Cyan
        ("Thinking", "#2E8BEF"), # AntFlow Blue
        ("Border", "#1E5FB8"),   # AntFlow Deep Blue
        ("Tool Name", "#6FE8E0"),  # AntFlow Cyan
        ("Subtitle", "#C9D6E2"),  # Soft Text
        ("Comment", "#163A73"),   # Hex Glow
        ("Foreground", "#C9D6E2"), # Soft Text
        ("Separator Line", "#163A73"), # Hex Glow
        ("Animation Shadow", "#163A73"), # Hex Glow
        ("Animation Medium", "#2E8BEF"), # AntFlow Blue
        ("Animation Solid", "#6FE8E0"), # AntFlow Cyan
        ("Panel Title", "#6FE8E0"),   # AntFlow Cyan
        ("Panel Border", "#1E5FB8"),  # AntFlow Deep Blue
        ("Separator", "#163A73"),    # Hex Glow
        ("Command Name", "#6FE8E0"),  # AntFlow Cyan
        ("Command Desc", "#C9D6E2"),  # Soft Text
    ]
    
    return colors_antflow

def show_colors():
    """Muestra todos los colores de AntFlow con sus códigos HEX"""
    
    console = Console()
    colors = get_antflow_colors()
    
    if not colors:
        console.print("No se pudieron cargar los colores del tema AntFlow.")
        return
    
    console.print("\n🎨 AntFlow Color Palette\n")
    
    for name, hex_color in colors:
        # Usar markup de Rich directamente
        console.print(f"[{hex_color}]{name}[/{hex_color}] - {hex_color}")
    
    console.print()

if __name__ == "__main__":
    show_colors()
