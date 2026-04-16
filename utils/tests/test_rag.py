#!/usr/bin/env python3
"""
Tests unitarios para el módulo RAG híbrido de skills.
Prueba la ingestión, búsqueda híbrida y re-ranking.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.skills.skill_manager import SkillManager


class TestRAGSkills(unittest.TestCase):
    """Suite de tests para el sistema RAG híbrido de skills"""

    def setUp(self):
        """Configuración antes de cada test"""
        # Crear directorio temporal para test
        self.test_db_path = tempfile.mkdtemp()
        self.manager = SkillManager()

        # Crear archivo de prueba
        self.test_content = """
        # Guía de Python para Principiantes

        ## Instalación
        Para instalar Python, ve a python.org y descarga la versión más reciente.
        Ejecuta el instalador y sigue las instrucciones.

        ## Variables
        Las variables en Python se declaran asignando valores:
        nombre = "Juan"
        edad = 25

        ## Funciones
        def saludar(nombre):
            return f"Hola, {nombre}!"

        ## Errores Comunes
        - Indentación incorrecta
        - Olvidar comillas en strings
        - Usar variables no definidas
        """

        self.test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
        self.test_file.write(self.test_content)
        self.test_file.close()

    def tearDown(self):
        """Limpieza después de cada test"""
        # Cerrar conexiones si es necesario
        # LanceDB no tiene método close explícito
        if hasattr(self.manager, 'db') and self.manager.db:
            pass  # No hacer nada, LanceDB maneja automáticamente

        # Eliminar archivo temporal
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)

        # Eliminar DB temporal (opcional, para debug comentar)
        import shutil
        if os.path.exists(self.test_db_path):
            shutil.rmtree(self.test_db_path)

    def test_ingestion(self):
        """Prueba la ingestión de una skill"""
        result = self.manager.ingest_skill(self.test_file.name, "python_basics")

        self.assertTrue(result["success"])
        self.assertGreater(result["chunks_processed"], 0)

        # Verificar que se guardó
        skills = self.manager.get_available_skills()
        self.assertIn("python_basics", skills)

    def test_hybrid_search(self):
        """Prueba la búsqueda híbrida"""
        # Ingestar primero
        self.manager.ingest_skill(self.test_file.name, "python_basics")

        # Buscar
        results = self.manager.search_hybrid("instalar python", ["python_basics"], top_k=5)

        self.assertIsInstance(results, list)
        if results:  # Si hay resultados
            self.assertIn("text", results[0])
            self.assertIn("skill_id", results[0])

    def test_reranking(self):
        """Prueba el re-ranking"""
        # Ingestar
        self.manager.ingest_skill(self.test_file.name, "python_basics")

        # Obtener candidatos
        candidates = self.manager.search_hybrid("funciones python", ["python_basics"], top_k=10)

        if candidates:
            # Re-rank
            reranked = self.manager.rerank_results("funciones python", candidates, top_k=3)

            self.assertIsInstance(reranked, list)
            self.assertLessEqual(len(reranked), 3)

    def test_embedding_generation(self):
        """Prueba la generación de embeddings"""
        text = "Hola mundo"
        embedding = self.manager._generate_embedding(text)

        self.assertIsInstance(embedding, list)
        self.assertEqual(len(embedding), 384)  # Dimensión de all-MiniLM-L6-v2

    def test_text_splitting(self):
        """Prueba el splitting de texto"""
        chunks = self.manager._split_text(self.test_content)

        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

        # Verificar que los chunks tienen overlap
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 550)  # chunk_size + algo de overlap


if __name__ == "__main__":
    unittest.main()