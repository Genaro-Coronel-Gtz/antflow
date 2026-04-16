#!/usr/bin/env python3
"""
Context Manager para SkillManager
Proporciona manejo automático de recursos con cleanup garantizado
"""
from typing import Optional
from utils.skills.skill_manager import SkillManager
from utils.core.config_loader import get_enable_skills
from utils.core.translator import t

class SkillManagerContext:
    """Context manager para SkillManager con cleanup automático"""
    
    def __init__(self):
        self.skill_manager: Optional[SkillManager] = None
        
    def __enter__(self) -> Optional[SkillManager]:
        """Crea el SkillManager al entrar al contexto"""
        if not get_enable_skills():
            return None
            
        try:
            self.skill_manager = SkillManager()
            return self.skill_manager
        except Exception as e:
            print(t("skill_context_error_creating").format(error=e))
            return None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Limpia recursos automáticamente al salir del contexto"""
        if self.skill_manager:
            try:
                self.skill_manager.cleanup()
            except Exception as e:
                print(t("skill_context_cleanup_error").format(error=e))
        # No suprimir excepciones
        return False

# Función de conveniencia para uso rápido
def with_skill_manager(func):
    """Decorator para ejecutar función con SkillManager automático"""
    def wrapper(*args, **kwargs):
        with SkillManagerContext() as sm:
            return func(sm, *args, **kwargs)
    return wrapper

# Ejemplo de uso:
# 
# # Opción 1: Context Manager directo
# with SkillManagerContext() as skill_manager:
#     if skill_manager:
#         skills = skill_manager.get_available_skills()
#         # ... usar el skill_manager
# # Cleanup automático al salir del with
#
# # Opción 2: Decorator
# @with_skill_manager
# def process_skills(skill_manager, query):
#     if skill_manager:
#         return skill_manager.search_skills(query, [])
#     return []
