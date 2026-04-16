#!/usr/bin/env python3
"""
Test unitario para verificar el funcionamiento de get_skills_full y get_skills_documents
"""
import sys
import os
from typing import List, Dict, Any

# Agregar el path del proyecto para importar utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.skills.skill_manager import SkillManager
from utils.skills.search_in_skills import get_skills_documents, get_skills_context


def test_get_skills_full():
    """Test para verificar get_skills_full con diferentes skills activas"""
    print("🧪 Testeando get_skills_full()...")
    
    manager = SkillManager()
    
    # Test 1: Sin skills activas
    print("\n1. Test sin skills activas:")
    result = manager.get_skills_full([])
    print(f"   Resultado: {len(result)} documentos")
    assert result == [], f"Esperado [], got {result}"
    print("   ✅ Pasó")
    
    # Test 2: Con skills activas (si existen)
    print("\n2. Test con skills activas:")
    available_skills = manager.get_available_skills()
    print(f"   Skills disponibles: {available_skills}")
    
    if available_skills:
        # Tomar las primeras 2 skills para el test
        test_skills = available_skills[:2]
        print(f"   Testeando con skills: {test_skills}")
        
        result = manager.get_skills_full(test_skills)
        print(f"   Documentos encontrados: {len(result)}")
        
        # Verificar que todos los documentos pertenecen a las skills activas
        for doc in result:
            skill_id = doc.get('skill_id')
            assert skill_id in test_skills, f"Documento con skill_id {skill_id} no está en skills activas"
            assert 'text' in doc, "Documento no tiene campo 'text'"
            assert doc['text'].strip(), "Documento tiene texto vacío"
        
        print("   ✅ Pasó")
    else:
        print("   ⚠️  No hay skills disponibles para test completo")
    
    # Test 3: Skill inexistente
    print("\n3. Test con skill inexistente:")
    result = manager.get_skills_full(['skill_inexistente'])
    print(f"   Resultado: {len(result)} documentos")
    assert result == [], f"Esperado [], got {result}"
    print("   ✅ Pasó")


def test_get_skills_documents():
    """Test para verificar get_skills_documents formateo correcto"""
    print("\n🧪 Testeando get_skills_documents()...")
    
    # Test 1: Sin skills activas
    print("\n1. Test sin skills activas:")
    result = get_skills_documents([])
    print(f"   Resultado: '{result[:50]}...'")
    assert result == "", f"Esperado string vacío, got '{result}'"
    print("   ✅ Pasó")
    
    # Test 2: Con skills activas (si existen)
    print("\n2. Test con skills activas:")
    manager = SkillManager()
    available_skills = manager.get_available_skills()
    
    if available_skills:
        test_skills = available_skills[:2]
        print(f"   Testeando con skills: {test_skills}")
        
        result = get_skills_documents(test_skills)
        print(f"   Longitud del resultado: {len(result)} caracteres")
        
        # Verificar formato del resultado
        assert "=== CONTENIDO COMPLETO DE SKILLS ===" in result, "Falta encabezado principal"
        assert "=== FIN CONTENIDO SKILLS ===" in result, "Fita pie de página"
        
        for skill_id in test_skills:
            assert f"--- SKILL: {skill_id.upper()} ---" in result, f"Falta encabezado para skill {skill_id}"
            assert f"--- FIN SKILL ---" in result, "Fita fin de skill"
        
        print("   ✅ Pasó")
    else:
        print("   ⚠️  No hay skills disponibles para test completo")
    
    # Test 3: Skills inexistentes
    print("\n3. Test con skills inexistentes:")
    result = get_skills_documents(['skill_inexistente'])
    print(f"   Resultado: '{result}'")
    assert "No se encontraron documentos para las skills activas." in result, "Mensaje de no encontrado incorrecto"
    print("   ✅ Pasó")


def test_comparison_chunk_vs_full():
    """Test comparativo entre chunking y full documents"""
    print("\n🧪 Test comparativo chunk vs full...")
    
    manager = SkillManager()
    available_skills = manager.get_available_skills()
    
    if len(available_skills) >= 2:
        test_skills = available_skills[:2]
        test_query = "test query"
        
        print(f"   Skills: {test_skills}")
        print(f"   Query: '{test_query}'")
        
        # Obtener resultados con chunking
        chunk_context, chunk_results, chunk_stats = get_skills_context(test_query, test_skills, top_k=3)
        
        # Obtener resultados con full documents
        full_context = get_skills_documents(test_skills)
        
        print(f"   Chunk context length: {len(chunk_context)} caracteres")
        print(f"   Full context length: {len(full_context)} caracteres")
        print(f"   Chunk results: {len(chunk_results)} documentos")
        print(f"   Chunk stats: {chunk_stats}")
        
        # Verificar que ambos retornen contenido
        assert chunk_context or full_context, "Ambos métodos retornaron contenido vacío"
        
        print("   ✅ Pasó")
    else:
        print("   ⚠️  No hay suficientes skills para test comparativo")


def main():
    """Ejecutar todos los tests"""
    print("🚀 Iniciando tests de retrieve_skills.py\n")
    
    try:
        test_get_skills_full()
        test_get_skills_documents()
        test_comparison_chunk_vs_full()
        
        print("\n✅ Todos los tests pasaron exitosamente!")
        
    except AssertionError as e:
        print(f"\n❌ Falló un test: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
