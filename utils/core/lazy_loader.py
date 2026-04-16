#!/usr/bin/env python3
"""
Sistema de Lazy Loading para optimizar el rendimiento de la aplicación.
Carga módulos solo cuando se necesitan, evitando importaciones pesadas al inicio.
"""

import importlib
import sys
from typing import Any, Dict, Optional


class LazyLoader:
    """
    Gestor de importaciones perezosas (lazy loading) para mejorar el rendimiento.
    
    Cachea los módulos importados para evitar importaciones repetidas
    y solo carga cuando explícitamente se solicita.
    """
    
    _cache: Dict[str, Any] = {}
    
    @classmethod
    def import_module(cls, module_name: str) -> Any:
        #print("Loading", module_name, "...")
        """
        Importa un módulo con cache para evitar importaciones repetidas
        
        Args:
            module_name: Nombre del módulo a importar
            
        Returns:
            Módulo importado o lanza ImportError si falla
        """
        if module_name not in cls._cache:
            try:
                cls._cache[module_name] = importlib.import_module(module_name)
            except ImportError as e:
                print(f"❌ Error importando {module_name}: {e}")
                raise
        return cls._cache[module_name]
    
    @classmethod
    def import_class(cls, module_path: str, class_name: str) -> Any:
        """
        Importa una clase específica de un módulo
        
        Args:
            module_path: Ruta del módulo (ej: 'utils.skills.skill_manager')
            class_name: Nombre de la clase (ej: 'SkillManager')
            
        Returns:
            Clase importada o lanza ImportError
        """
        try:
            module = cls.import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            print(f"❌ Error importando {class_name} desde {module_path}: {e}")
            raise
    
    @classmethod
    def get_cache_info(cls) -> Dict[str, str]:
        """
        Retorna información sobre los módulos cacheados
        
        Returns:
            Diccionario con nombres de módulos y su estado
        """
        return {
            name: "cached" if name in cls._cache else "not_cached"
            for name in cls._cache
        }
    
    @classmethod
    def clear_cache(cls) -> None:
        """
        Limpia la cache de módulos (útil para pruebas o recargas)
        """
        cls._cache.clear()
        print("🧹 Cache de módulos limpiada")


def lazy_import(module_name: str) -> Any:
    """
    Función de conveniencia para importar módulos perezosamente
    
    Args:
        module_name: Nombre del módulo a importar
        
    Returns:
        Módulo importado
    """
    return LazyLoader.import_module(module_name)


def lazy_class(module_path: str, class_name: str) -> Any:
    """
    Función de conveniencia para importar clases perezosamente
    
    Args:
        module_path: Ruta del módulo
        class_name: Nombre de la clase
        
    Returns:
        Clase importada
    """
    return LazyLoader.import_class(module_path, class_name)
