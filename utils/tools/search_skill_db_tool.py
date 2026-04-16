#!/usr/bin/env python3
from smolagents import Tool
from typing import Dict, Any, List, Optional
# IMPORTANTE: Usamos import absoluto para evitar errores en los tests
from utils.skills.skill_manager import SkillManager
from .utils.common import write_log

class SearchSkillDBTool(Tool):
    name = "search_skill_db"
    description = "Busca información específica en la base de datos de skills sobre implementaciones, patrones o documentación técnica."
    
    inputs = {
        "query": {
            "type": "string",
            "description": "Consulta de búsqueda para encontrar información relevante en las skills",
            "nullable": True  # Si es True, el forward DEBE tener = None
        },
        "skill_filter": {
            "type": "string", 
            "description": "Filtrar búsqueda a skills específicas (opcional, separadas por comas)",
            "nullable": True
        },
        "top_k": {
            "type": "integer",
            "description": "Número máximo de resultados a retornar (default: 5)",
            "nullable": True
        }
    }
    output_type = "string"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Validar si las skills están habilitadas antes de inicializar
        from ..core.config_loader import get_enable_skills
        if not get_enable_skills():
            self.skill_manager = None
        else:
            # SkillManager ahora obtiene el project_hash internamente
            self.skill_manager = SkillManager()

    def forward(self, query: str = None, skill_filter: str = None, top_k: int = 5) -> str:
        # Validar si las skills están habilitadas
        if self.skill_manager is None:
            return " Skills deshabilitadas. No se puede buscar en la base de datos de skills."
            
        # 1. Validar que el query no sea None (aunque sea nullable en la firma)
        if not query or not str(query).strip():
            return " Error: Debes proporcionar una consulta de búsqueda válida."
        
        try:
            # 2. Ajustar top_k
            max_results = int(top_k) if top_k else 5
            max_results = max(1, min(15, max_results))

            # 3. Obtener skills activas
            active_skills = self.skill_manager.get_enabled_skills()
            
            # 4. Aplicar filtro si existe
            if skill_filter and str(skill_filter).strip():
                filter_list = [s.strip().lower() for s in skill_filter.split(',')]
                active_skills = [s for s in active_skills if s.lower() in filter_list]
            
            if not active_skills:
                return " Error: No hay skills habilitadas que coincidan con el filtro."

            # 5. Búsqueda en el Manager
            results = self.skill_manager.search_skills(
                query=query.strip(), 
                active_skills_ids=active_skills,
                top_k=max_results
            )
            
            if not results:
                return f" No se encontró información para: '{query}'"

            # 6. Formatear para el Agente
            write_log(self.name, {"query": query}, {"results": results[:20]})
            return self._format_results(results)

        except Exception as e:
            error_msg = f" Error en la Tool: {str(e)}"
            # write_log(self.name, {"query": query}, error_msg) # Opcional si tienes el helper
            return error_msg

    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        formatted = f"**RESULTADOS DE SKILLS DB**\n\n"
        for i, res in enumerate(results, 1):
            skill_id = res.get('skill', 'desconocida')
            text = res.get('text', '').strip()
            score = res.get('score', 0)
            
            formatted += f"--- RESULTADO {i} (Skill: {skill_id} | Relevancia: {score:.2%}) ---\n"
            formatted += f"{text}\n\n"
        
        formatted += " Instrucción: Usa estos fragmentos para guiar tu implementación."
        return formatted