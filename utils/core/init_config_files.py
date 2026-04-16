#!/usr/bin/env python3
"""
Inicialización de archivos de configuración del proyecto
"""
import os
import shutil
import json
import hashlib
from pathlib import Path
from utils.core.translator import t

def get_resources_path():
    import sys
    """Retorna el path correcto a resources/ según el entorno de ejecución"""
    if getattr(sys, 'frozen', False):
        # Ejecutando desde binario PyInstaller
        return os.path.join(sys._MEIPASS, 'resources')
    else:
        # Ejecutando desde source
        return 'resources'

def create_empty_file(file_path):
    """Crea un archivo vacío si no existe"""
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")  # Archivo vacío
        return True
    return False

def copy_from_resources(src_filename, dest_path):
    """Copia un archivo desde resources/ al destino"""
    src_path = os.path.join(get_resources_path(), src_filename)
    if os.path.exists(src_path):
        try:
            shutil.copy2(src_path, dest_path)
            return True
        except Exception as e:
            print(t("error_copying_file").format(src_filename=src_filename, error=e))
            return False
    else:
        print(t("source_file_not_found").format(src_path=src_path))
        return False

def create_empty_files(directory, filenames):
    """Crea múltiples archivos vacíos en un directorio"""
    created = []
    for filename in filenames:
        file_path = os.path.join(directory, filename)
        if create_empty_file(file_path):
            created.append(filename)
    return created

def copy_file(src_path, dest_path):
    """Copia un archivo de origen a destino"""
    try:
        shutil.copy2(src_path, dest_path)
        return True
    except Exception as e:
        print(t("error_copying_file_general").format(error=e))
        return False

def copy_directory_from_resources(src_dirname, dest_path):
    """Copia todo un directorio desde resources/ al destino"""
    src_path = os.path.join(get_resources_path(), src_dirname)
    if os.path.exists(src_path):
        try:
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(src_path, dest_path)
            return True
        except Exception as e:
            print(t("error_copying_directory").format(src_dirname=src_dirname, error=e))
            return False
    else:
        print(t("source_directory_not_found").format(src_path=src_path))
        return False

def generate_project_hash():
    from datetime import datetime
    """Genera un hash único basado en el path del proyecto"""
    project_path = os.getcwd()
    # Usar MD5 del path del proyecto + timestamp para unicidad
    hash_input = f"{project_path}_{datetime.now().strftime('%Y%m%d')}"
    return hashlib.md5(hash_input.encode()).hexdigest()[:8]

def update_config_with_hash(config_path):
    """Actualiza el archivo de configuración con el project_hash"""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Generar hash si no existe o está vacío
        if not config.get("project_hash"):
            config["project_hash"] = generate_project_hash()
            
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return config["project_hash"]
        
        return config.get("project_hash")
    except Exception as e:
        print(t("error_updating_config_hash").format(error=e))
        return generate_project_hash()

def update_config_with_subagents_flag(config_path, use_subagents_prompt):
    """Actualiza el archivo de configuración con enable_subagents según use_subagents_prompt"""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Establecer enable_subagents según use_subagents_prompt
        config["enable_subagents"] = use_subagents_prompt
            
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        return True
    except Exception as e:
        print(t("error_updating_config_subagents").format(e=e))
        return False

def initialize_project_files(theme_manager, use_subagents_prompt=False, config_type="ollama"):
    """Inicializa todos los archivos necesarios en .antflow
    
    Args:
        theme_manager: Gestor de temas para imprimir mensajes
        use_subagents_prompt: Si True, usa contenido de SYSTEM_PROMPT_SUBAGENTS.md para prompt.md
        config_type: Tipo de configuración ("ollama" o "openrouter")
    """
    antflow_dir = ".antflow"
    
    try:
        # Crear directorio .antflow si no existe
        os.makedirs(antflow_dir, exist_ok=True)
        os.makedirs(os.path.join(antflow_dir, "skills"), exist_ok=True)
        
        # 1. Crear archivos vacíos
        create_empty_files(antflow_dir, [
            "antflow.log",
            "memory.md",
            "errors.log",
            "context.md"
        ])
        
         
        # NOTA: Docker necesita esta estructura base para poder crear colecciones
        
        # 2. Copiar archivos desde resources/
        # Determinar el archivo de configuración fuente
        config_source_file = f"config_{config_type}.json"
        resource_files = ["subagents.json", "antflow.ignore","tools_config.json"]
        
        # Primero copiar el archivo de configuración específico
        config_dest_path = os.path.join(antflow_dir, "config.json")
        copy_from_resources(config_source_file, config_dest_path)
        
        # Actualizar config con project_hash
        project_hash = update_config_with_hash(config_dest_path)
        theme_manager.print_info_text(t("project_hash_info").format(project_hash=project_hash))
        
        # Actualizar config con enable_subagents según use_subagents_prompt
        update_config_with_subagents_flag(config_dest_path, use_subagents_prompt)
        subagents_status = t("subagents_status").format(status="habilitados" if use_subagents_prompt else "deshabilitados")
        theme_manager.print_info_text(subagents_status)
        
        # Luego copiar los otros archivos
        for file in resource_files:
            dest_path = os.path.join(antflow_dir, file)
            copy_from_resources(file, dest_path)
        
        # 3. Copiar prompt.md según el comando
        system_prompt_path = os.path.join(antflow_dir, "prompt.md")
        if not os.path.exists(system_prompt_path):
            if config_type == 'ollama':
                copy_from_resources("SYSTEM_PROMPT_OLLAMA.md", system_prompt_path)
            else:
                if use_subagents_prompt:
                    # Copiar desde resources/SYSTEM_PROMPT_SUBAGENTS.md
                    copy_from_resources("SYSTEM_PROMPT_SUBAGENTS.md", system_prompt_path)
                else:
                    # Copiar desde resources/SYSTEM_PROMPT.md
                    copy_from_resources("SYSTEM_PROMPT.md", system_prompt_path)
        
        # 4. Copiar directorio subagents desde resources/
        subagents_dest_dir = os.path.join(antflow_dir, "subagents")
        copy_directory_from_resources("subagents", subagents_dest_dir)
        
        # 5. Crear directorio skills (vacío)
        skills_dir = os.path.join(antflow_dir, "skills")
        os.makedirs(skills_dir, exist_ok=True)
        
        # 6. Mostrar resumen simplificado
        theme_manager.print_header(t("initialization_completed"), t("initialization_completed"))
        theme_manager.print_info_text(t("config_files_created"))
        if config_type == "openrouter":
            theme_manager.print_info_text(t("openrouter_api_key_hint"))
        
    except Exception as e:
        theme_manager.print_error_text(t("initialization_error").format(error=e))
        return False
    
    return True
