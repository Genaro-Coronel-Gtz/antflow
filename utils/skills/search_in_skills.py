#!/usr/bin/env python3
import os
from typing import List, Dict, Any, Tuple
from .skill_manager import SkillManager
from .reranker_db_results import rerank_skills_context


def get_skills_documents(active_skills: List[str]) -> str:
    """
    Obtiene todos los documentos de las skills activas y los formatea como texto.
    Retorna un string con todo el contenido de las skills activas.
    """
    if not active_skills:
        return ""
    
    manager = SkillManager()
    documents = manager.get_skills_full(active_skills)
    
    if not documents:
        return "No se encontraron documentos para las skills activas."
    
    # Agrupar documentos por skill_id para mejor organización
    skills_content = {}
    for doc in documents:
        skill_id = doc.get('skill_id', 'unknown')
        text = doc.get('text', '').strip()
        
        if text and skill_id in active_skills:
            if skill_id not in skills_content:
                skills_content[skill_id] = []
            skills_content[skill_id].append(text)
    
    # Formatear como texto legible para el prompt
    formatted_context = "=== CONTENIDO COMPLETO DE SKILLS ===\n\n"
    
    for skill_id in active_skills:
        if skill_id in skills_content:
            formatted_context += f"--- SKILL: {skill_id.upper()} ---\n"
            for chunk in skills_content[skill_id]:
                formatted_context += f"{chunk}\n\n"
            formatted_context += "--- FIN SKILL ---\n\n"
    
    formatted_context += "=== FIN CONTENIDO SKILLS ==="
    
    return formatted_context

def get_skills_context(user_query: str, active_skills: List[str], top_k: int = 3) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    """
    Realiza la búsqueda vectorial, aplica reranking y formatea el contexto para el prompt.
    Retorna (contexto_string, resultados_rerankeados, estadísticas)
    """
    if not active_skills:
        return "", [], {"total_original": 0, "total_reranked": 0, "top_k": top_k, "flashrank_available": False}

    manager = SkillManager()
    # Realizar la búsqueda en la base de datos vectorial
    # La lista de resultados contiene: text, skill_id, score, etc.
    results = manager.search_skills(user_query, active_skills)

    if not results:
        return "No se encontró contexto relevante en las skills activas.", [], {"total_original": 0, "total_reranked": 0, "top_k": top_k, "flashrank_available": False}

    # Aplicar reranking con FlashRank
    skills_context, reranked_results, stats = rerank_skills_context(
        query=user_query,
        results=results,
        top_k=top_k
    )

    return skills_context, reranked_results, stats