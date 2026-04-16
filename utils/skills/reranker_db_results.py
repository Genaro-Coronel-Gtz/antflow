#!/usr/bin/env python3
"""
Reranker de resultados de búsqueda vectorial usando FlashRank
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Estructura para resultados de búsqueda"""
    text: str
    skill_id: str
    score: float
    metadata: str = ""
    _distance: Optional[float] = None  # Para compatibilidad con LanceDB


class VectorialReranker:
    """Reranker de resultados de búsqueda vectorial usando FlashRank"""
    
    def __init__(self, top_k: int = 3):
        """
        Inicializa el reranker
        
        Args:
            top_k: Número de resultados a devolver después del reranking
        """
        self.top_k = top_k
        self.ranker = None
        self._init_ranker()
    
    def _init_ranker(self):
        """Inicializa FlashRank con manejo de errores"""
        try:
            from flashrank import Ranker
            from flashrank import RerankRequest
            self.ranker = Ranker()
            print("✅ FlashRank inicializado correctamente")
        except ImportError:
            print("⚠️ FlashRank no instalado. Usando fallback a ordenamiento por score.")
            self.ranker = None
        except Exception as e:
            print(f"❌ Error inicializando FlashRank: {e}")
            self.ranker = None
    
    def rerank_results(
        self, 
        query: str, 
        results: List[Dict[str, Any]]
    ) -> Tuple[List[SearchResult], List[Dict[str, Any]]]:
        """
        Rerankea los resultados de búsqueda vectorial
        
        Args:
            query: Consulta original del usuario
            results: Resultados crudos de la búsqueda vectorial
            
        Returns:
            Tuple con (resultados_rerankeados, resultados_crudos_rerankeados)
        """
        if not results:
            return [], []
        
        # Convertir a estructura SearchResult
        search_results = self._convert_to_search_results(results)
        
        # Si FlashRank no está disponible, usar fallback
        if self.ranker is None:
            return self._fallback_rerank(query, search_results), results[:self.top_k]
        
        try:
            # Importar RerankRequest aquí para asegurar que esté disponible
            from flashrank import RerankRequest
            
            # Preparar datos para FlashRank usando RerankRequest
            passages = [
                {"id": str(i), "text": result.text}
                for i, result in enumerate(search_results)
            ]
            
            # Crear RerankRequest
            rerank_request = RerankRequest(query=query, passages=passages)
            
            # Ejecutar reranking con el método correcto
            reranked_docs = self.ranker.rerank(rerank_request)
            
            # Convertir resultados rerankeados
            reranked_results = []
            reranked_raw = []
            
            for doc in reranked_docs[:self.top_k]:
                idx = int(doc["id"])
                original_result = search_results[idx]
                
                # Actualizar score con el ranking de FlashRank
                reranked_result = SearchResult(
                    text=original_result.text,
                    skill_id=original_result.skill_id,
                    score=doc["score"],  # Nuevo score de FlashRank
                    metadata=original_result.metadata,
                    _distance=original_result._distance
                )
                
                reranked_results.append(reranked_result)
                reranked_raw.append({
                    "text": original_result.text,
                    "skill_id": original_result.skill_id,
                    "score": doc["score"],
                    "metadata": original_result.metadata,
                    "_distance": original_result._distance
                })
            
            return reranked_results, reranked_raw
            
        except Exception as e:
            print(f"❌ Error en reranking con FlashRank: {e}")
            return self._fallback_rerank(query, search_results), results[:self.top_k]
    
    def _convert_to_search_results(self, results: List[Dict[str, Any]]) -> List[SearchResult]:
        """
        Convierte resultados crudos a estructura SearchResult
        
        Args:
            results: Resultados crudos de la búsqueda vectorial
            
        Returns:
            Lista de SearchResult
        """
        search_results = []
        
        for result in results:
            # Manejar diferentes estructuras de resultados
            text = result.get('text', result.get('content', ''))
            skill_id = result.get('skill_id', result.get('id', 'unknown'))
            score = result.get('score', 0.0)
            
            # VALIDACIÓN CRÍTICA: Ignorar resultados con texto vacío o None
            if not text or text is None:
                continue
                
            # Para LanceDB, el score puede estar en _distance
            if '_distance' in result:
                # Convertir distancia a similitud (más cercano = más alto)
                distance = result['_distance']
                score = 1.0 / (1.0 + distance) if distance > 0 else 1.0
            
            metadata = result.get('metadata', '{}')
            
            search_result = SearchResult(
                text=text,
                skill_id=skill_id,
                score=score,
                metadata=metadata,
                _distance=result.get('_distance')
            )
            
            search_results.append(search_result)
        
        return search_results
    
    def _fallback_rerank(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        """
        Fallback cuando FlashRank no está disponible
        Usa ordenamiento por score original
        
        Args:
            query: Consulta original (no usado en fallback)
            results: Resultados a rerankear
            
        Returns:
            Resultados ordenados por score
        """
        # Ordenar por score descendente
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        return sorted_results[:self.top_k]
    
    def format_reranked_context(self, results: List[SearchResult]) -> str:
        """
        Formatea los resultados rerankeados para el prompt
        
        Args:
            results: Resultados rerankeados
            
        Returns:
            String formateado para el prompt
        """
        if not results:
            return "No se encontró contexto relevante en las skills activas."
        
        context_parts = []
        context_parts.append("--- CONTEXTO DE SKILLS RECUPERADO (RERANKEADO) ---")
        
        for i, result in enumerate(results, 1):
            skill_name = result.skill_id
            text = result.text
            score = result.score
            
            context_parts.append(
                f"### {i}. Skill: {skill_name} (Score: {score:.3f})\n"
                f"Contenido: {text}\n"
            )
        
        context_parts.append("--- FIN DEL CONTEXTO ---\n")
        
        return "\n".join(context_parts)
    
    def get_ranking_stats(self, original_results: List[Dict[str, Any]], 
                         reranked_results: List[SearchResult]) -> Dict[str, Any]:
        """
        Genera estadísticas del reranking
        
        Args:
            original_results: Resultados originales de búsqueda
            reranked_results: Resultados después del reranking
            
        Returns:
            Diccionario con estadísticas
        """
        return {
            "total_original": len(original_results),
            "total_reranked": len(reranked_results),
            "top_k": self.top_k,
            "flashrank_available": self.ranker is not None,
            "average_score": sum(r.score for r in reranked_results) / len(reranked_results) if reranked_results else 0,
            "skills_found": list(set(r.skill_id for r in reranked_results))
        }


# Instancia global para fácil acceso
_reranker_instance = None

def get_reranker(top_k: int = 3) -> VectorialReranker:
    """
    Obtiene una instancia del reranker (singleton)
    
    Args:
        top_k: Número de resultados a devolver
        
    Returns:
        Instancia de VectorialReranker
    """
    global _reranker_instance
    if _reranker_instance is None or _reranker_instance.top_k != top_k:
        _reranker_instance = VectorialReranker(top_k=top_k)
    return _reranker_instance


def rerank_skills_context(query: str, results: List[Dict[str, Any]], 
                         top_k: int = 3) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    """
    Función de conveniencia para rerankear contexto de skills
    
    Args:
        query: Consulta del usuario
        results: Resultados de búsqueda vectorial
        top_k: Número de resultados a devolver
        
    Returns:
        Tuple con (contexto_formateado, resultados_rerankeados, estadísticas)
    """
    reranker = get_reranker(top_k)
    reranked_results, reranked_raw = reranker.rerank_results(query, results)
    
    # Formatear contexto
    context = reranker.format_reranked_context(reranked_results)
    
    # Generar estadísticas
    stats = reranker.get_ranking_stats(results, reranked_results)
    
    return context, reranked_raw, stats


if __name__ == "__main__":
    # Test del reranker
    print("🧪 Test del VectorialReranker")
    
    # Datos de prueba
    test_query = "cómo crear una API REST con Python"
    test_results = [
        {
            "text": "Para crear una API REST con Python puedes usar Flask o FastAPI. Flask es más simple mientras FastAPI es más moderno y rápido.",
            "skill_id": "python_api",
            "score": 0.85,
            "_distance": 0.15
        },
        {
            "text": "Python es un lenguaje de programación versátil que se usa para desarrollo web, ciencia de datos y automatización.",
            "skill_id": "python_basics", 
            "score": 0.75,
            "_distance": 0.25
        },
        {
            "text": "FastAPI es un framework moderno para crear APIs con Python que incluye validación automática y documentación Swagger.",
            "skill_id": "fastapi_guide",
            "score": 0.90,
            "_distance": 0.10
        },
        {
            "text": "Las bases de datos relacionales usan SQL para consultar datos y son ideales para aplicaciones estructuradas.",
            "skill_id": "database_basics",
            "score": 0.60,
            "_distance": 0.40
        }
    ]
    
    reranker = get_reranker(top_k=3)
    reranked_results, reranked_raw = reranker.rerank_results(test_query, test_results)
    
    print("\n📊 Resultados rerankeados:")
    for i, result in enumerate(reranked_results, 1):
        print(f"{i}. {result.skill_id} (Score: {result.score:.3f})")
        print(f"   {result.text[:100]}...")
    
    print(f"\n📈 Estadísticas: {reranker.get_ranking_stats(test_results, reranked_results)}")
    
    print(f"\n📝 Contexto formateado:")
    print(reranker.format_reranked_context(reranked_results))
