#!/usr/bin/env python3
import os
import sys

# 1. Configurar el PATH de forma absoluta para evitar el error de "relative import"
# Determinamos la raíz del proyecto (dos niveles arriba de utils/tests/)
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(current_dir, '..', '..'))

if root_path not in sys.path:
    sys.path.insert(0, root_path)

# 2. Importaciones Absolutas (Sin puntos)
try:
    from utils.skills.skill_manager import SkillManager
    from utils.tools.search_skill_db_tool import SearchSkillDBTool
    from utils.core.config_loader import get_project_hash
    print(f"✅ Módulos cargados correctamente desde: {root_path}")
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("\n💡 Tip: Verifica que no tengas 'from ..' en tus archivos de tools o utils.")
    print("Cambia los imports a absolutos, ej: 'from utils.skills.skill_manager import ...'")
    sys.exit(1)

def main():
    print("\n" + "🚀" * 15)
    print("  DEBUGGER SKILL MANAGER + TOOL TEST")
    print("🚀" * 15)

    # Configuración del hash (mostrar el hash que se usará)
    project_hash = get_project_hash()
    print(f"🔑 Using project_hash: {project_hash}")
    
    try:
        # Instanciar SkillManager (ahora obtiene project_hash internamente)
        manager = SkillManager()
        # Instanciar Tool (la que usa el Agente) - obtiene project_hash automáticamente
        search_tool = SearchSkillDBTool()
    except Exception as e:
        print(f"💥 Error al instanciar componentes: {e}")
        return

    # Mostrar skills actuales
    skills = manager.get_available_skills()
    print(f"\n📋 Colección: {manager.collection_name}")
    print(f"📋 Skills detectadas: {skills}")

    # Opción de Reset e Ingesta
    if input("\n♻️  ¿Deseas RESETEAR la DB e INGESTAR un archivo? (s/n): ").lower() == 's':
        manager.reset_db()
        file_path = input("📄 Ruta al archivo (ej: skills/fastapi_impl.py): ").strip()
        skill_name = input("🎯 Nombre de la skill (ej: fastapi): ").strip()
        
        if not os.path.exists(file_path):
            print(f"❌ El archivo '{file_path}' no existe.")
        else:
            manager.ingest_skill(file_path, skill_name)
            skills = manager.get_available_skills()

    if not skills:
        print("📭 No hay skills disponibles. Abortando búsqueda.")
        return

    # --- PRUEBA DE BÚSQUEDA ---
    query = input("\n🔍 ¿Qué quieres buscar? (ej: 'router', 'auth'): ").strip()
    skill_to_test = input(f"🎯 Elige una skill de la lista {skills}: ").strip()

    print("\n" + "─" * 50)
    print("🧪 PRUEBA 1: BÚSQUEDA DIRECTA (Manager)")
    print("─" * 50)
    
    raw_results = manager.search_skills(query, [skill_to_test], top_k=3)
    
    if raw_results:
        for i, res in enumerate(raw_results, 1):
            print(f"   [{i}] Score: {res['score']:.4f} | Skill: {res['skill']}")
            print(f"       Texto: {res['text'][:100]}...\n")
    else:
        print("📭 No se encontraron resultados en el Manager.")

    print("\n" + "─" * 50)
    print("🧪 PRUEBA 2: BÚSQUEDA VÍA TOOL (Formato Agente)")
    print("─" * 50)
    
    # Aquí probamos el método forward que llamará smolagents
    try:
        tool_output = search_tool.forward(query=query, skill_filter=skill_to_test, top_k=3)
        print("Salida que recibirá el LLM:")
        print("-" * 30)
        print(tool_output)
        print("-" * 30)
    except Exception as e:
        print(f"❌ Error al ejecutar la Tool: {e}")

    # PRUEBA DE ESTADO (ENABLE/DISABLE)
    if input("\n⚙️  ¿Deseas probar DESACTIVAR esta skill? (s/n): ").lower() == 's':
        print(f"🚫 Desactivando '{skill_to_test}'...")
        manager.set_skill_enabled(skill_to_test, False)
        
        # Verificación
        check = manager.get_enabled_skills()
        print(f"✅ Skills habilitadas ahora: {check}")
        
        res_hidden = manager.search_skills(query, [skill_to_test])
        if not res_hidden:
            print("🎯 Confirmado: La búsqueda ya no devuelve resultados de esta skill.")
        else:
            print("⚠️ Advertencia: La skill sigue devolviendo resultados.")

        # Restaurar
        manager.set_skill_enabled(skill_to_test, True)
        print(f"🔄 Skill '{skill_to_test}' reactivada.")

if __name__ == "__main__":
    main()