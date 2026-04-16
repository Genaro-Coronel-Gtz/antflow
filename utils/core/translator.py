#!/usr/bin/env python3
"""
Sistema de traducciones para internacionalización
"""

import importlib
import sys
import os
from utils.core.config_loader import load_config


class Translator:
    """Gestor de traducciones para internacionalización"""
    
    def __init__(self):
        self.config = load_config()
        self.lang = self.config.get('language', 'es')
        self.translations = self._load_translations()
    
    def _load_translations(self):
        """Carga el módulo de traducciones según el idioma configurado"""
        try:
            return importlib.import_module(f'translations.{self.lang}')
        except ImportError:
            # Si estamos en PyInstaller, intentar agregar el path
            if hasattr(sys, '_MEIPASS'):
                translations_path = os.path.join(sys._MEIPASS, 'translations')
                if translations_path not in sys.path:
                    sys.path.insert(0, translations_path)
                try:
                    return importlib.import_module(f'translations.{self.lang}')
                except ImportError:
                    pass
            
            # Fallback al español si no existe el idioma
            try:
                return importlib.import_module('translations.es')
            except ImportError:
                return None
    
    def t(self, key):
        """Obtiene la traducción para una clave"""
        if self.translations:
            return getattr(self.translations, key, key)
        return key


# Instancia global del traductor
_translator = Translator()
t = _translator.t
