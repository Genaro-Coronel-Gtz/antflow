#!/usr/bin/env python3
"""
Inicialización de la base de datos de skills
"""
from .skill_manager import SkillManager
from utils.core.translator import t
import sys
import os

# Agregar el directorio del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def init_database():
    """Inicializa la base de datos usando el método de SkillManager"""
    print(t("db_initializing"))
    
    try:
        manager = SkillManager()
        
        # Usar el método _init_collection() que ya existe en SkillManager
        manager._init_collection()
        
        if manager.enabled and manager.q_client is not None:
            print(t("db_initialized_success"))
            
            # Verificar cuántos registros hay
            try:
                skills = manager.get_available_skills()
                print(t("db_table_records").format(count=len(skills)))
                
                if len(skills) > 0:
                    print(t("db_skills_found").format(skills=list(skills)))
                else:
                    print(t("db_table_empty"))
                    
            except Exception as e:
                print(t("db_content_verify_error").format(error=e))
                
            return True
        else:
            print(t("db_table_init_error"))
            return False
            
    except Exception as e:
        print(t("db_init_general_error").format(error=e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
