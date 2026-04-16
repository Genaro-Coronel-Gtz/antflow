#!/usr/bin/env python3
"""
Verificar skills disponibles en la base de datos - versión corregida
"""
import sys
import os
import numpy as np

# Agregar el directorio del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from .skill_manager import SkillManager

def check_skills():
    """Verifica las skills disponibles con información básica"""
    print("🔍 Verificando skills disponibles...")
    
    try:
        # Instanciamos el manager
        manager = SkillManager()
        
        # LLAMADA CORRECTA: Usamos el método que ya tienes en tu clase
        manager._init_collection()
        
        if not (manager.enabled and manager.q_client is not None):
            print("❌ No se pudo conectar a la base de datos o no hay skills disponibles.")
            return False
        
        # Obtener todos los datos mediante el método correcto
        skills = manager.get_available_skills()
        
        if len(skills) == 0:
            print("❌ La base de datos está vacía")
            return False
        
        print(f"\n📊 REGISTROS DE SKILLS ENCONTRADOS")
        print("=" * 60)
        
        # Agrupar por skill_id para mostrar un resumen limpio
        for skill_id in skills:
            # Verificamos si está habilitada (esto usa tu método existente)
            enabled_list = manager.get_enabled_skills()
            status = "✅ Activo" if skill_id in enabled_list else "❌ Inactivo"
            
            print(f"\n🎯 Skill: {skill_id}")
            print(f"📊 Estado: {status}")
            
            # Mostrar información básica
            print(f"📝 Skill ID: {skill_id}")
            print(f"🔍 Disponible en base de datos: Sí")
            
            print("-" * 60)
        
        print(f"\n✅ Total de skills únicas: {len(skills)}")
        print(f"✅ Total de fragmentos disponibles: {len(skills)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_skills()