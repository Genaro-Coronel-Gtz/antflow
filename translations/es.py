#!/usr/bin/env python3
"""
Traducciones en español
"""

# app.py - Prompts y mensajes de usuario
prompt = "\n > "

# app.py - Mensajes del sistema
exiting = "\nSaliendo del modo agente..."
returning_to_commands = "\n Volviendo a comandos principales..."

# app.py - Comandos y ayuda
all_commands_title = "Todos los comandos disponibles"
all_commands_subtitle = "Lista completa de comandos del sistema"
available_commands = "Comandos disponibles:"
command_column_title = "Comando"
description_column_title = "Descripción"
command_usage_delete_skill = "Uso: /delete-skill <skill_id>"
command_usage_enable_skill = "Uso: /enable-skill <nombre_skill>"
command_usage_disable_skill = "Uso: /disable-skill <nombre_skill>"
memory_cleared = "Memoria del agente limpiada"
memory_stats_title = "Estadísticas de Memoria"
memory_stats_subtitle = "Estado actual de la memoria del agente"

# app.py - Descripciones de comandos
cmd_version = "Mostrar versión de la aplicación"
cmd_init = "Inicializar archivos del proyecto (.antflow) [ollama|openrouter]"
cmd_init_subagents = "Inicializar archivos con prompt de subagentes [ollama|openrouter]"
cmd_skill = "Agregar nueva skill al sistema"
cmd_list_skills = "Listar todas las skills y su estado"
cmd_enable_skill = "Habilitar skill específica"
cmd_disable_skill = "Deshabilitar skill específica"
cmd_delete_skill = "Eliminar skill del sistema"
cmd_memory_stats = "Mostrar estadísticas de memoria"
cmd_clear_memory = "Limpiar archivo de memoria"
cmd_clear_all = "Limpiar todos los archivos (memoria, logs, contexto, errores)"
cmd_back = "Volver a comandos principales"
cmd_exit = "Salir del programa"
cmd_stop_agent_proccess = "Detener proceso del agente"

# header.py - Comandos principales
commands_help = "Mostrar todos los comandos disponibles"
exit_help = "Salir del programa"

# header.py - Encabezados
main_commands = "Comandos principales:"
project_path = "Ruta del proyecto"

# General - Otros mensajes
version_info = "Versión:"
welcome = "Bienvenido a AntFlow"

# utils/skills/skill_manager.py - Gestión de skills
skills_disabled = "Skills deshabilitadas en configuración"
skill_not_found = "Skill no encontrada"
skill_added_successfully = "Skill agregada exitosamente"
skill_already_exists = "La skill ya existe"
skill_enabled = "Skill habilitada"
skill_disabled = "Skill deshabilitada"
skill_deleted_successfully = "Skill eliminada exitosamente"
no_skills_available = "No hay skills disponibles"
skills_list_title = "Skills disponibles:"
skills_list_subtitle = "Lista de todas las skills y su estado de activación"
total_skills = "Total de skills: {count}"
active_skills = "Skills activas: {count}"
no_skills_db = "No hay skills en la base de datos"
skill_status_enabled_display = "Habilitada"
skill_status_disabled_display = "Deshabilitada"
error_listing_skills = "Error listando skills: {error}"

# utils/skills/skill_context.py - Context Manager
skill_context_error_creating = "Error creando SkillManager: {error}"
skill_context_cleanup_error = "Error en cleanup del context manager: {error}"

# app.py - Manejo de señales y cleanup
signal_terminating_processes = "Terminando procesos hijos..."
signal_cleanup_error = "Error en cleanup: {error}"
signal_exiting_gracefully = "Saliendo gracefully..."

# utils/skills/skill_manager.py - Cleanup messages
cleanup_embedding_completed = "Embedding model cleanup completado"
cleanup_ranker_completed = "Ranker model cleanup completado"
cleanup_qdrant_completed = "Qdrant client cleanup completado"
cleanup_gc_completed = "Garbage collection completado"
cleanup_error = "Error en cleanup: {error}"

# utils/skills/skill_manager.py - Device detection
using_mps_device = "Usando MPS (Apple Silicon) para embeddings"
using_cuda_device = "Usando CUDA (NVIDIA) para embeddings"
using_cpu_device = "Usando CPU para embeddings"

# utils/skills/add_skill.py - Context manager usage
add_skill_skills_disabled = "Error: Skills deshabilitadas"
skill_status_enabled = "Habilitada"
skill_status_disabled = "Deshabilitada"

# utils/skills/add_skill.py - Agregar skills
skill_name_prompt = "Nombre de la skill:"
skill_description_prompt = "Descripción de la skill:"
skill_content_prompt = "Contenido de la skill (terminar con 'END' en nueva línea):"
skill_added_confirmation = "Skill '{name}' agregada correctamente"

# utils/skills/delete_skill.py - Eliminar skills
skill_delete_confirm = "¿Estás seguro de eliminar la skill '{name}'? (s/n)"
skill_delete_cancelled = "Eliminación cancelada"
skill_delete_success = "Skill '{name}' eliminada correctamente"
skill_delete_error = "Error al eliminar la skill"

# utils/skills/init_db.py - Inicialización de base de datos
db_initializing = "Inicializando base de datos de skills..."
db_initialized_successfully = "Base de datos inicializada correctamente"
db_already_exists = "La base de datos ya existe"

# utils/skills/reset_db.py - Reset de base de datos
db_reset_warning = "¿Estás seguro de resetear la base de datos? Esto eliminará todas las skills (s/n)"
db_reset_cancelled = "Reset cancelado"
db_reset_success = "Base de datos reseteada correctamente"

# utils/memory/memory_agent.py - Gestión de memoria
memory_loading = "Cargando memoria..."
memory_loaded_successfully = "Memoria cargada correctamente"
memory_saving = "Guardando memoria..."
memory_saved_successfully = "Memoria guardada correctamente"
memory_clearing = "Limpiando memoria..."
memory_cleared_successfully = "Memoria limpiada correctamente"

# utils/core/init_config_files.py - Inicialización de configuración
config_initializing = "Inicializando archivos de configuración..."
config_initialized_successfully = "Archivos de configuración inicializados correctamente"
config_already_exists = "Los archivos de configuración ya existen"

# utils/models/models_manager.py - Gestión de modelos
model_loading = "Cargando modelo..."
model_loaded_successfully = "Modelo cargado correctamente"
model_not_found = "Modelo no encontrado"
model_error = "Error al cargar el modelo"

# app.py - Mensajes adicionales
tokens_used = "Tokens usados: {total} (input: {input}, output: {output})"
duration = "Duración: {duration:.2f}s"
interruption_detected = "Interrupción detectada. Saliendo..."
eof_detected = "Fin de entrada detectado. Saliendo..."
error_occurred = "Error: {error}"
skills_list_title = "Listado de Skills"
skills_list_subtitle = "Estado actual de todas las skills disponibles"
no_skills_db = "No hay skills disponibles en la base de datos"
total_skills = "Total de skills: {count}"
active_skills = "Skills activas: {count}"
skill_status_enabled_display = "enabled"
skill_status_disabled_display = "disabled"
error_listing_skills = "Error listando skills: {error}"

# app.py - Función delete_skill_from_agent
skill_delete_warning = "Estás por eliminar la skill: {skill_id}"
skill_delete_confirm_prompt = "¿Confirmar eliminación? (s/n):"
skill_delete_cancelled_user = "Operación cancelada"
skill_delete_success_msg = "Skill '{skill_id}' eliminada correctamente"
skill_delete_error_msg = "Error eliminando la skill '{skill_id}'"
skill_delete_cancelled_keyboard = "Operación cancelada por el usuario"
skill_delete_general_error = "Error eliminando skill: {error}"

# app.py - Comandos /init y /init-subagents
invalid_config_type = "Tipo de configuración no válido: {config_type}"
init_usage = "Usa: /init [ollama|openrouter]"
init_subagents_usage = "Usa: /init-subagents [ollama|openrouter]"

# app.py - Comando /skill
skill_added_success_msg = "Skill agregada exitosamente"
skill_add_error_msg = "Error al agregar la skill"

# app.py - Mensajes de memoria
memory_total_messages = "Total de mensajes: {count}"
memory_user_messages = "Mensajes de usuario: {count}"
memory_agent_messages = "Mensajes del agente: {count}"
memory_system_messages = "Mensajes del sistema: {count}"
memory_max_limit = "Límite máximo: {limit}"
memory_file = "Archivo de memoria: {file}"

# app.py - Mensajes de agente
agent_label = "Agente:"

# app.py - Mensaje de vuelta al menú
returning_to_main_menu = "Volviendo al menú principal..."

# app.py - Funciones enable_skill_direct y disable_skill_direct
skill_not_exists = "La skill '{skill_name}' no existe"
skill_already_enabled = "La skill '{skill_name}' ya está habilitada"
skill_enabled_success = "Skill '{skill_name}' habilitada correctamente"
skill_enable_error = "Error habilitando la skill '{skill_name}'"
skill_enable_general_error = "Error habilitando skill: {error}"
total_active_skills = "Skills activas totales: {count}"
skill_already_disabled = "La skill '{skill_name}' ya está deshabilitada"
skill_disabled_success = "Skill '{skill_name}' deshabilitada correctamente"
skill_disable_error = "Error deshabilitando la skill '{skill_name}'"
skill_disable_general_error = "Error deshabilitando skill: {error}"
total_active_skills_after = "Skills activas restantes: {count}"

# app.py - Argumentos de línea de comandos (argparse)
argparse_description = "AntFlow - Open source agentic framework"
argparse_version_help = "Mostrar versión de la aplicación"
argparse_agent_help = "Abrir el agente en modo terminal"
argparse_init_help = "Inicializar el proyecto. Formatos: -i[ollama|openrouter] o --init [ollama|openrouter] (default: ollama)"
argparse_init_subagents_help = "Inicializar el proyecto con subagentes. Formatos: -s[ollama|openrouter] o --init-subagents [ollama|openrouter] (default: ollama)"
argparse_error_command = "debe proporcionar uno de los comandos: -a/--agent, -i/--init, -s/--init-subagents"

# app.py - Mensajes de inicialización y finalización
project_init_success_subagents = "Proyecto inicializado correctamente con prompt de subagentes"
project_init_success = "Proyecto inicializado correctamente"
antflow_folder_created = "Carpeta .antflow creada con archivos de configuración"
exiting_program = "Saliendo del programa..."
main_loop_error = "Error: {error}"

# app.py - Mensajes adicionales encontrados
return_false_exit = "Indicar que debe salir del programa"
return_to_main_commands = "Volver a comandos principales"
default_config_type = "ollama"  # comentario, no traducir
animation_type_bar = "bar"  # comentario, no traducir

# agent.py - Mensajes del agente
agent_memory_cleared_reloaded = "Memoria del agente limpiada y herramientas recargadas"

# utils/themes/theme_manager.py - Mensajes del gestor de temas
theme_not_found = "Tema '{theme_name}' no encontrado. Temas disponibles: {available_themes}"
special_commands_title = " Comandos especiales:"

# utils/core/init_config_files.py - Mensajes de inicialización
error_copying_file = "Error copiando {src_filename}: {error}"
source_file_not_found = "No se encontró el archivo fuente: {src_path}"
error_copying_file_general = "Error copiando archivo: {error}"
error_copying_directory = "Error copiando directorio {src_dirname}: {error}"
source_directory_not_found = "No se encontró el directorio fuente: {src_path}"
error_updating_config_hash = "Error actualizando config con hash: {error}"
error_updating_config_subagents = "Error actualizando config con enable_subagents: {e}"
project_hash_info = " Project Hash: {project_hash}"
subagents_status = "Subagentes {status}"
initialization_completed = "Inicialización Completada"
config_files_created = " Archivos de configuración creados en: .antflow"
openrouter_api_key_hint = " Para usar OpenRouter, actualiza la API key en config.json"
initialization_error = " Error al inicializar: {error}"

# utils/skills/skill_manager.py - Gestión de skills
error_downloading_ranker = "Error downloading ranker model: {error}"
qdrant_connection_error = "Error conexión Qdrant: {error}"
flashrank_warning = "Warning Flashrank: {error}. Usando fallback sin rerank."
collection_created = "Colección '{collection_name}' creada."
processing_skill = "Procesando skill '{skill_name}'..."
vectorizing_progress = "  -> Vectorizando {current}/{total}..."
chunks_ingested = "\n {count} chunks ingestados correctamente."
search_error = " Error búsqueda: {error}"
no_points_found = "No se encontraron puntos para la skill '{skill_id}'"
regenerating_vector = "Regenerando vector para punto {point_id}..."
skill_status_updated = "Skill '{skill_id}' {status} correctamente"
error_updating_skill = "Error actualizando skill {skill_id}: {error}"
error_get_available = "Error get_available: {error}"
error_get_enabled = "Error get_enabled: {error}"
error_get_skills_full = "Error en get_skills_full: {error}"
skill_deleted_qdrant = "Skill '{skill_id}' eliminada de Qdrant."
error_deleting_skill = "Error eliminando skill: {error}"

# utils/skills/init_db.py - Inicialización de base de datos
db_initializing = " Inicializando base de datos..."
db_initialized_success = " Base de datos inicializada correctamente"
db_table_records = " La tabla tiene {count} registros"
db_skills_found = " Skills encontradas: {skills}"
db_table_empty = " La tabla está vacía, lista para recibir skills"
db_content_verify_error = "No se pudo verificar contenido: {error}"
db_table_init_error = "No se pudo inicializar la tabla"
db_init_general_error = "Error: {error}"

# utils/skills/reset_db.py - Reset de base de datos
db_resetting = "Reiniciando base de datos de skills (Qdrant)..."
db_skills_disabled = "Las skills están deshabilitadas. No se puede resetear la base de datos."
db_manager_disabled = "SkillManager no está habilitado"
db_reset_success = "Base de datos de skills reseteada correctamente"
db_reset_note = "Nota: La colección Qdrant ha sido eliminada y recreada"
db_reset_error = "Error reseteando la base de datos: {error}"

# utils/memory/memory_agent.py - Gestión de memoria
memory_cleared = "Memoria del agente limpiada"
memory_save_error = "Error guardando memoria: {error}"
memory_load_error = "Error cargando memoria: {error}"
memory_initialized = "Memoria inicializada"

# utils/memory/prompt_context.py - Contexto de prompts
prompt_context_clean_error = "No se pudo limpiar {file_path}: {error}"
prompt_context_save_error = "Error guardando prompt context: {error}"

# utils/models/models_manager.py - Gestión de modelos
ollama_models_error = "Error obteniendo modelos de Ollama: {error}"
openrouter_models_error = "Error obteniendo modelos de OpenRouter: {error}"

# utils/skills/skill_manager.py - Verificación de conexión Qdrant
qdrant_skills_disabled = "Skills deshabilitadas - no se requiere Qdrant"
qdrant_connection_success = "Conexión a Qdrant exitosa en {host}:{port}"
qdrant_connection_error = "No se puede conectar a Qdrant en {host}:{port}\n\nSoluciones:\n1. Inicia Qdrant: docker-compose up -d\n2. O deshabilita skills en config.json: 'enable_skills': false"
qdrant_timeout_error = "Timeout al conectar a Qdrant en {host}:{port}\n\nVerifica que Qdrant esté corriendo y accesible."
qdrant_server_error = "Qdrant responde pero hay un error: {error}\n\nVerifica que Qdrant esté funcionando correctamente."
qdrant_unexpected_error = "Error inesperado al conectar a Qdrant: {error}\n\nHost: {host}, Puerto: {port}"
qdrant_config_error_title = "Error de configuración de Qdrant:"
qdrant_config_error_message = "La aplicación no puede continuar sin una conexión válida a Qdrant."

# app.py - Diálogo de comandos
commands_show_list = "Muestra este listado"
commands_dialog_title = "\n Comandos disponibles \n\n\n"
commands_close_hint = "\n  Esc · Enter para cerrar"

# app.py - Diálogo de skill
skill_dialog_title = "  Nueva Skill"
skill_name_label = "  Nombre de la skill"
skill_path_label = "  Ruta del archivo .md"
skill_navigation_hint = "  Tab para navegar · Esc para cancelar"
skill_accept_button = "  Aceptar  "
skill_cancel_button = "  Cancelar  "

# app.py - Mensajes de skill
skill_validation_error = "[!] Operación cancelada: nombre o ruta vacíos."
skill_creating = "[~] Creating skill '{name}' from {path} ..."
skill_registered_success = "[✓] Skill '{name}' registered successfully."
skill_chunks_processed = "[~] Chunks processed: {count}"
skill_unknown_error = "Unknown error"
skill_creation_error = "[✗] Error creating skill: {error}"

# app.py - Estado y toolbar
status_ready = "Listo"
toolbar_hint = "F1 comandos  |  F2 nueva skill  |  Ctrl+Q salir  |  PageUp/Down scroll"

# app.py - Validación humana
agent_request_validation = "Agent request validation"
human_response = "El humano respondió: {response}"
validation_error = "Error en validación: {error}"
validation_handler_error = "Error en handle_human_validation_request: {error}"

# app.py - Banner
banner_provider_label = "Provider: "
banner_model_label = "Model: "
banner_unknown_provider_model = "AntFlow - Provider: Unknown | Model: Unknown"

# app.py - Mensajes de error de comandos
error_enable_skill_usage = "[ERROR] Uso: /enable-skill <skill_name>"
error_disable_skill_usage = "[ERROR] Uso: /disable-skill <skill_name>"
error_delete_skill_usage = "[ERROR] Uso: /delete-skill <skill_name>"
error_run_usage = "[ERROR] Uso: /run <query>"
error_unknown_command = "[ERROR] Comando desconocido: {cmd}  —  escribe /commands"

# app.py - Mensajes de estado
status_lines_in_buffer = "[STATUS] Líneas en buffer: {count}"

# app.py - Mensajes del sistema
system_ready_message = "[~] Sistema listo. Escribe algo y presiona Enter."

# app.py - Mensajes de error
command_processing_error = "[✗] Error procesando comando: {error}"
