#!/usr/bin/env python3
"""
Sistema de temas para la terminal
"""

# Importar todos los temas disponibles
from .dracula import dracula_theme
from .tokyo_night import tokyo_night_theme
from .basic import basic_theme
from .antflow import antflow_theme

# Diccionario de temas disponibles
THEMES = {
    "dracula": dracula_theme,
    "tokyo_night": tokyo_night_theme,
    "basic": basic_theme,
    "antflow": antflow_theme,
}


def get_theme(theme_name: str):
    """
    Obtiene un tema por nombre
    
    Args:
        theme_name: Nombre del tema
        
    Returns:
        Theme de Rich
    """
    return THEMES.get(theme_name.lower(), dracula_theme)


def list_available_themes() -> list:
    """
    Lista todos los temas disponibles
    
    Returns:
        Lista de nombres de temas
    """
    return list(THEMES.keys())


# Exportar componentes principales
__all__ = ['get_theme', 'list_available_themes', 'THEMES']
