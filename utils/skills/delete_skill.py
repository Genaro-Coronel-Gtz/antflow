#!/usr/bin/env python3
"""
Eliminar una skill de la base de datos por su ID
"""
import sys
import os

# Agregar el directorio del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from .skill_manager import SkillManager
from utils.core.translator import t

def delete_skill(skill_id: str) -> bool:
    """Elimina una skill de la base de datos por su ID"""
    try:
        if not skill_id or not skill_id.strip():
            print("❌ El ID de la skill no puede estar vacío")
            return False
        
        skill_id = skill_id.strip()
        
        # Inicializar el manager
        manager = SkillManager()
        manager._init_collection()
        
        if manager.table is None:
            print("❌ No se pudo conectar a la base de datos")
            return False
        
        # Verificar que la skill existe
        available_skills = manager.get_available_skills()
        if skill_id not in available_skills:
            print(f"❌ {t('skill_not_found')}")
            print(f"📋 Skills disponibles: {', '.join(available_skills)}")
            return False
        
        # Contar chunks antes de eliminar
        df = manager.table.to_pandas()
        chunks_to_delete = len(df[df['skill_id'] == skill_id])
        
        print(f"🔍 Skill encontrada: '{skill_id}'")
        print(f"📊 Chunks a eliminar: {chunks_to_delete}")
        
        # Eliminar todos los chunks con ese skill_id
        manager.table.delete(where=f"skill_id = '{skill_id}'")
        
        print(f"✅ {t('skill_deleted_successfully')}")
        print(f"🗑️ {chunks_to_delete} chunks eliminados de la base de datos")
        
        # Mostrar skills restantes
        remaining_skills = manager.get_available_skills()
        if remaining_skills:
            print(f"📋 Skills restantes: {', '.join(remaining_skills)}")
        else:
            print("📋 No quedan skills en la base de datos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error eliminando skill '{skill_id}': {e}")
        import traceback
        traceback.print_exc()
        return False

def list_available_skills():
    """Lista las skills disponibles en la base de datos"""
    try:
        manager = SkillManager()
        skills = manager.get_available_skills()
        
        if not skills:
            print("📋 No hay skills en la base de datos")
            return []
        
        print(f"\n📋 Skills disponibles en la base de datos:")
        for i, skill in enumerate(skills, 1):
            print(f"  {i}. {skill}")
        
        return skills
        
    except Exception as e:
        print(f"❌ Error listando skills: {e}")
        return []

if __name__ == "__main__":
    print("🗑️ UTILIDAD PARA ELIMINAR SKILLS")
    print("=" * 50)
    
    # Mostrar skills disponibles
    available_skills = list_available_skills()
    
    if not available_skills:
        print("\n❌ No hay skills para eliminar")
        sys.exit(1)
    
    print(f"\n💡 Para eliminar una skill específica:")
    print(f"   python -m utils.skills.delete_skill <skill_id>")
    print(f"   Ejemplo: python -m utils.skills.delete_skill rails")
    
    # Si se proporcionó argumento, eliminar esa skill
    if len(sys.argv) > 1:
        skill_id = sys.argv[1]
        success = delete_skill(skill_id)
        sys.exit(0 if success else 1)
    else:
        print(f"\n⚠️ Debes proporcionar el ID de la skill a eliminar")
        sys.exit(1)
