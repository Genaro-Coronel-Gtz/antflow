#!/usr/bin/env python3
"""
Reset de la base de datos de skills
"""
from .skill_manager import SkillManager
from utils.core.translator import t
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def reset_database():
    """Elimina y recrea la colección en Qdrant"""
    print(t("db_resetting"))
    
    try:
        # Verificar si las skills están habilitadas
        from utils.core.config_loader import get_enable_skills
        if not get_enable_skills():
            print(t("db_skills_disabled"))
            return False
        
        # Inicializar SkillManager
        manager = SkillManager()
        
        if not manager.enabled:
            print(t("db_manager_disabled"))
            return False
        
        # Usar el método reset_db() del SkillManager
        manager.reset_db()
        
        print(t("db_reset_success"))
        print(t("db_reset_note"))
        
        return True
        
    except Exception as e:
        print(t("db_reset_error").format(error=e))
        return False

if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)
