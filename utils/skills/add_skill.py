#!/usr/bin/env python3
"""
Agregar una skill a la base de datos desde un archivo markdown
"""
import sys
import os

# Agregar el directorio del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from .skill_manager import SkillManager
from .skill_context import SkillManagerContext
from utils.tools.utils.common import safe_path
from utils.core.translator import t

def add_skill_ui(skill_name: str, filename: str):
    """Agrega una skill desde un archivo markdown usando parámetros directos"""
    try:
        # Validar parámetros
        if not skill_name:
            return {"success": False, "error": "El nombre de la skill no puede estar vacío"}
        
        if not filename:
            return {"success": False, "error": "El nombre del archivo no puede estar vacío"}
        
        # Asegurar que tenga extensión .md
        if not filename.endswith('.md'):
            filename += '.md'
        
        # Construir la ruta completa al archivo usando safe_path
        skills_dir = safe_path(".antflow/skills")
        file_path = os.path.join(skills_dir, filename)
        
        # Verificar que el archivo exista
        if not os.path.exists(file_path):
            return {"success": False, "error": f"No se encontró el archivo: {file_path}"}
        
        # Ingestar la skill usando context manager
        with SkillManagerContext() as manager:
            if not manager:
                return {"success": False, "error": "Skills deshabilitadas"}
            
            result = manager.skill_ingest(file_path, skill_name)
            
            if result.get("success"):
                return {
                    "success": True, 
                    "skill_name": skill_name,
                    "filename": filename,
                    "chunks_processed": result.get('chunks_processed', 0)
                }
            else:
                return {
                    "success": False, 
                    "error": result.get('error', 'Error desconocido')
                }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_available_skills():
    """Lista los archivos .md disponibles en el directorio skills"""
    skills_dir = safe_path(".antflow/skills")
    
    if not os.path.exists(skills_dir):
        print(f" El directorio '.antflow/skills' no existe: {skills_dir}")
        return []
    
    md_files = [f for f in os.listdir(skills_dir) if f.endswith('.md')]
    
    if not md_files:
        print(" No se encontraron archivos .md en el directorio '.antflow/skills/'")
        return []
    
    print(f"\n Archivos .md disponibles en '.antflow/skills/':")
    for i, file in enumerate(md_files, 1):
        print(f"  {i}. {file}")
    
    return md_files

if __name__ == "__main__":
    print(" UTILIDAD PARA AGREGAR SKILLS")
    print("=" * 50)
    
    # Mostrar archivos disponibles
    available_files = list_available_skills()
    
    if available_files:
        print(f"\n Puedes usar cualquiera de los archivos listados arriba")
    
    print(f"\n El script buscar los archivos en: .antflow/skills/")
    print(f" Solo necesitas proporcionar el nombre del archivo (ej: rails.md)")
    
    # Agregar skill
    success = add_skill()
    
    if success:
        print(f"\n !Skill agregada exitosamente!")
    else:
        print(f"\n No se pudo agregar la skill")
    
    sys.exit(0 if success else 1)
