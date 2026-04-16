#!/usr/bin/env python3
"""
Gestor de contexto de prompts para el agente
"""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from utils.core.translator import t
from utils.core.config_loader import get_generate_prompt_context_file, get_start_app_clean_files

class PromptContext:
    """Maneja el registro de prompts para depuración (guardado ANTES de enviar al modelo)"""
    
    def __init__(self, output_file: str = ".antflow/context.md"):
        self.output_file = output_file
        # Crear directorio .antflow si no existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        # Limpiar archivos de logs al iniciar
        self.cleanup_logs()
        # Reiniciamos el archivo cada vez que se instancia la app
        self.clear_file()
    
    def cleanup_logs(self):
        """Limpia el contenido de archivos de log al iniciar la aplicación"""
        # Verificar si está habilitada la limpieza de archivos
        if not get_start_app_clean_files():
            return  # No hacer nada si está deshabilitado
            
        # Crear directorio .antflow si no existe
        os.makedirs(".antflow", exist_ok=True)
        
        log_files = [
            ".antflow/memory.md",
            ".antflow/context.md", 
            ".antflow/antflow.log",
            ".antflow/errors.log"
        ]
        
        for file_path in log_files:
            try:
                if os.path.exists(file_path):
                    # Para todos los archivos, dejarlos completamente vacíos
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write("")
                    # print(f"🧹 Limpiado: {file_path}")
            except Exception as e:
                print(t("prompt_context_clean_error").format(file_path=file_path, error=e))
    
    def clear_file(self):
        """Limpia el archivo de contexto si está habilitado"""
        if not get_start_app_clean_files():
            return  # No hacer nada si está deshabilitado
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write("")

    def save_prompt_context(self, 
                          user_text: str,
                          enabled_skills: List[str],
                          active_skills_ids: List[str],
                          skills_search_results: List[Dict[str, Any]],
                          skills_context: str,
                          final_prompt: str,
                          system_prompt: str,
                          search_stats: Dict[str, Any] = None) -> bool:
        """Guarda el prompt completo que se enviará al modelo (para debug) - Simplificado sin skills"""
        
        generate_prompt_context = get_generate_prompt_context_file()
        if not generate_prompt_context:
            return False

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(f"\n## 🕒 Interacción: {timestamp} [PRE-ENVÍO]\n")
                f.write(f"\n### 👤 Prompt Original del Usuario:\n> {user_text}\n")
                
                # System Prompt
                f.write(f"\n### ⚙️ System Prompt:\n")
                f.write(f"```\n{system_prompt}\n```\n")
                
                # Prompt Final Completo
                f.write(f"\n### 🚀 PROMPT FINAL COMPLETO (enviado al modelo):\n")
                f.write("=" * 80 + "\n")
                f.write(f"```\n{final_prompt}\n```\n")
                f.write("=" * 80 + "\n")
                f.write(f"**🎯 Longitud total del prompt:** {len(final_prompt)} caracteres\n")
                f.write("---\n\n")
            
            return True
        except Exception as e:
            print(t("prompt_context_save_error").format(error=e))
            return False
