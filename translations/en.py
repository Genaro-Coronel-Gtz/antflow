#!/usr/bin/env python3
"""
English translations
"""

# app.py - User prompts and messages
prompt = "\n > "

# app.py - System messages
exiting = "\nExiting agent mode..."
returning_to_commands = "\n Returning to main commands..."

# app.py - Commands and help
all_commands_title = "All available commands"
all_commands_subtitle = "Complete list of system commands"
available_commands = "Available commands:"
command_column_title = "Command"
description_column_title = "Description"
command_usage_delete_skill = "Usage: /delete-skill <skill_id>"
command_usage_enable_skill = "Usage: /enable-skill <skill_name>"
command_usage_disable_skill = "Usage: /disable-skill <skill_name>"
memory_cleared = "Agent memory cleared"
memory_stats_title = "Memory Statistics"
memory_stats_subtitle = "Current status of agent memory"

# app.py - Command descriptions
cmd_version = "Show application version"
cmd_init = "Initialize project files (.antflow) [ollama|openrouter]"
cmd_init_subagents = "Initialize files with subagent prompts [ollama|openrouter]"
cmd_skill = "Add new skill to system"
cmd_list_skills = "List all skills and their status"
cmd_enable_skill = "Enable specific skill"
cmd_disable_skill = "Disable specific skill"
cmd_delete_skill = "Delete skill from system"
cmd_memory_stats = "Show memory statistics"
cmd_clear_memory = "Clear memory file"
cmd_clear_all = "Clear all files (memory, logs, context, errors)"
cmd_back = "Return to main commands"
cmd_exit = "Exit the program"
cmd_stop_agent_proccess = "Stop agent process"

# header.py - Main commands
commands_help = "Show all available commands"
exit_help = "Exit the program"

# header.py - Headers
main_commands = "Main commands:"
project_path = "Project path"

# General - Other messages
version_info = "Version:"
welcome = "Welcome to AntFlow"

# utils/skills/skill_manager.py - Skills management
skills_disabled = "Skills disabled in configuration"
skill_not_found = "Skill not found"
skill_added_successfully = "Skill added successfully"
skill_already_exists = "Skill already exists"
skill_enabled = "Skill enabled"
skill_disabled = "Skill disabled"
skill_deleted_successfully = "Skill deleted successfully"
no_skills_available = "No skills available"
skills_list_title = "Available skills:"
skills_list_subtitle = "List of all skills and their activation status"
total_skills = "Total skills: {count}"
active_skills = "Active skills: {count}"
no_skills_db = "No skills in database"
skill_status_enabled_display = "Enabled"
skill_status_disabled_display = "Disabled"
error_listing_skills = "Error listing skills: {error}"

# utils/skills/skill_context.py - Context Manager
skill_context_error_creating = "Error creating SkillManager: {error}"
skill_context_cleanup_error = "Error in context manager cleanup: {error}"

# app.py - Signal handling and cleanup
signal_terminating_processes = "Terminating child processes..."
signal_cleanup_error = "Error in cleanup: {error}"
signal_exiting_gracefully = "Exiting gracefully..."

# utils/skills/skill_manager.py - Cleanup messages
cleanup_embedding_completed = "Embedding model cleanup completed"
cleanup_ranker_completed = "Ranker model cleanup completed"
cleanup_qdrant_completed = "Qdrant client cleanup completed"
cleanup_gc_completed = "Garbage collection completed"
cleanup_error = "Error in cleanup: {error}"

# utils/skills/skill_manager.py - Device detection
using_mps_device = "Using MPS (Apple Silicon) for embeddings"
using_cuda_device = "Using CUDA (NVIDIA) for embeddings"
using_cpu_device = "Using CPU for embeddings"

# utils/skills/add_skill.py - Context manager usage
add_skill_skills_disabled = "Error: Skills disabled"
skill_status_enabled = "Enabled"
skill_status_disabled = "Disabled"

# utils/skills/add_skill.py - Add skills
skill_name_prompt = "Skill name:"
skill_description_prompt = "Skill description:"
skill_content_prompt = "Skill content (end with 'END' on new line):"
skill_added_confirmation = "Skill '{name}' added correctly"

# utils/skills/delete_skill.py - Delete skills
skill_delete_confirm = "Are you sure to delete skill '{name}'? (y/n)"
skill_delete_cancelled = "Deletion cancelled"
skill_delete_success = "Skill '{name}' deleted successfully"
skill_delete_error = "Error deleting skill"

# utils/skills/init_db.py - Database initialization
db_initializing = "Initializing skills database..."
db_initialized_successfully = "Database initialized successfully"
db_already_exists = "Database already exists"

# utils/skills/reset_db.py - Database reset
db_reset_warning = "Are you sure to reset the database? This will delete all skills (y/n)"
db_reset_cancelled = "Reset cancelled"
db_reset_success = "Database reset successfully"

# utils/memory/memory_agent.py - Memory management
memory_loading = "Loading memory..."
memory_loaded_successfully = "Memory loaded successfully"
memory_saving = "Saving memory..."
memory_saved_successfully = "Memory saved successfully"
memory_clearing = "Clearing memory..."
memory_cleared_successfully = "Memory cleared successfully"

# utils/core/init_config_files.py - Configuration initialization
config_initializing = "Initializing configuration files..."
config_initialized_successfully = "Configuration files initialized successfully"
config_already_exists = "Configuration files already exist"

# utils/models/models_manager.py - Models management
model_loading = "Loading model..."
model_loaded_successfully = "Model loaded successfully"
model_not_found = "Model not found"
model_error = "Error loading model"

# app.py - Additional messages
tokens_used = "Tokens used: {total} (input: {input}, output: {output})"
duration = "Duration: {duration:.2f}s"
interruption_detected = "Interruption detected. Exiting..."
eof_detected = "End of input detected. Exiting..."
error_occurred = "Error: {error}"
skills_list_title = "Skills List"
skills_list_subtitle = "Current status of all available skills"
no_skills_db = "No skills available in database"
total_skills = "Total skills: {count}"
active_skills = "Active skills: {count}"
skill_status_enabled_display = "enabled"
skill_status_disabled_display = "disabled"
error_listing_skills = "Error listing skills: {error}"

# app.py - Function delete_skill_from_agent
skill_delete_warning = "You are about to delete the skill: {skill_id}"
skill_delete_confirm_prompt = "Confirm deletion? (y/n):"
skill_delete_cancelled_user = "Operation cancelled"
skill_delete_success_msg = "Skill '{skill_id}' deleted successfully"
skill_delete_error_msg = "Error deleting skill '{skill_id}'"
skill_delete_cancelled_keyboard = "Operation cancelled by user"
skill_delete_general_error = "Error deleting skill: {error}"

# app.py - Commands /init and /init-subagents
invalid_config_type = "Invalid configuration type: {config_type}"
init_usage = "Use: /init [ollama|openrouter]"
init_subagents_usage = "Use: /init-subagents [ollama|openrouter]"

# app.py - Command /skill
skill_added_success_msg = "Skill added successfully"
skill_add_error_msg = "Error adding skill"

# app.py - Memory messages
memory_total_messages = "Total messages: {count}"
memory_user_messages = "User messages: {count}"
memory_agent_messages = "Agent messages: {count}"
memory_system_messages = "System messages: {count}"
memory_max_limit = "Max limit: {limit}"
memory_file = "Memory file: {file}"

# app.py - Agent messages
agent_label = "Agent:"

# app.py - Return to menu message
returning_to_main_menu = "Returning to main menu..."

# app.py - Functions enable_skill_direct and disable_skill_direct
skill_not_exists = "The skill '{skill_name}' does not exist"
skill_already_enabled = "The skill '{skill_name}' is already enabled"
skill_enabled_success = "Skill '{skill_name}' enabled successfully"
skill_enable_error = "Error enabling skill '{skill_name}'"
skill_enable_general_error = "Error enabling skill: {error}"
total_active_skills = "Total active skills: {count}"
skill_already_disabled = "The skill '{skill_name}' is already disabled"
skill_disabled_success = "Skill '{skill_name}' disabled successfully"
skill_disable_error = "Error disabling skill '{skill_name}'"
skill_disable_general_error = "Error disabling skill: {error}"
total_active_skills_after = "Remaining active skills: {count}"

# app.py - Command line arguments (argparse)
argparse_description = "AntFlow - Open source agentic framework"
argparse_version_help = "Show application version"
argparse_agent_help = "Open agent in terminal mode"
argparse_init_help = "Initialize project. Formats: -i[ollama|openrouter] or --init [ollama|openrouter] (default: ollama)"
argparse_init_subagents_help = "Initialize project with subagents. Formats: -s[ollama|openrouter] or --init-subagents [ollama|openrouter] (default: ollama)"
argparse_error_command = "must provide one of the commands: -a/--agent, -i/--init, -s/--init-subagents"

# app.py - Initialization and finalization messages
project_init_success_subagents = "Project initialized correctly with subagent prompt"
project_init_success = "Project initialized correctly"
antflow_folder_created = ".antflow folder created with configuration files"
exiting_program = "Exiting program..."
main_loop_error = "Error: {error}"

# app.py - Additional messages found
return_false_exit = "Indicate that it should exit the program"
return_to_main_commands = "Return to main commands"
default_config_type = "ollama"  # comment, don't translate
animation_type_bar = "bar"  # comment, don't translate

# agent.py - Agent messages
agent_memory_cleared_reloaded = "Agent memory cleared and tools reloaded"

# utils/themes/theme_manager.py - Theme manager messages
theme_not_found = "Theme '{theme_name}' not found. Available themes: {available_themes}"
special_commands_title = "Special commands:"

# utils/core/init_config_files.py - Initialization messages
error_copying_file = "Error copying {src_filename}: {error}"
source_file_not_found = "Source file not found: {src_path}"
error_copying_file_general = "Error copying file: {error}"
error_copying_directory = "Error copying directory {src_dirname}: {error}"
source_directory_not_found = "Source directory not found: {src_path}"
error_updating_config_hash = "Error updating config with hash: {error}"
error_updating_config_subagents = "Error updating config with enable_subagents: {e}"
project_hash_info = "Project Hash: {project_hash}"
subagents_status = "Subagents {status}"
initialization_completed = "Initialization Completed"
config_files_created = "Configuration files created in: .antflow"
openrouter_api_key_hint = "To use OpenRouter, update the API key in config.json"
initialization_error = "Error initializing: {error}"

# utils/skills/skill_manager.py - Skills management
error_downloading_ranker = "Error downloading ranker model: {error}"
qdrant_connection_error = "Qdrant connection error: {error}"
flashrank_warning = "Warning Flashrank: {error}. Using fallback without rerank."
collection_created = "Collection '{collection_name}' created."
processing_skill = "Processing skill '{skill_name}'..."
vectorizing_progress = "  -> Vectorizing {current}/{total}..."
chunks_ingested = "\n {count} chunks ingested correctly."
search_error = " Search error: {error}"
no_points_found = "No points found for skill '{skill_id}'"
regenerating_vector = "Regenerating vector for point {point_id}..."
skill_status_updated = "Skill '{skill_id}' {status} correctly"
error_updating_skill = "Error updating skill {skill_id}: {error}"
error_get_available = "Error get_available: {error}"
error_get_enabled = "Error get_enabled: {error}"
error_get_skills_full = "Error in get_skills_full: {error}"
skill_deleted_qdrant = "Skill '{skill_id}' deleted from Qdrant."
error_deleting_skill = "Error deleting skill: {error}"

# utils/skills/init_db.py - Database initialization
db_initializing = "Initializing database..."
db_initialized_success = "Database initialized successfully"
db_table_records = "The table has {count} records"
db_skills_found = "Skills found: {skills}"
db_table_empty = "The table is empty, ready to receive skills"
db_content_verify_error = "Could not verify content: {error}"
db_table_init_error = "Could not initialize the table"
db_init_general_error = "Error: {error}"

# utils/skills/reset_db.py - Database reset
db_resetting = "Resetting skills database (Qdrant)..."
db_skills_disabled = "Skills are disabled. Cannot reset the database."
db_manager_disabled = "SkillManager is not enabled"
db_reset_success = "Skills database reset successfully"
db_reset_note = "Note: The Qdrant collection has been deleted and recreated"
db_reset_error = "Error resetting the database: {error}"

# utils/memory/memory_agent.py - Memory management
memory_cleared = "Agent memory cleared"
memory_save_error = "Error saving memory: {error}"
memory_load_error = "Error loading memory: {error}"
memory_initialized = "Memory initialized"

# utils/memory/prompt_context.py - Prompt context
prompt_context_clean_error = "Could not clean {file_path}: {error}"
prompt_context_save_error = "Error saving prompt context: {error}"

# utils/models/models_manager.py - Models management
ollama_models_error = "Error getting Ollama models: {error}"
openrouter_models_error = "Error getting OpenRouter models: {error}"

# utils/skills/skill_manager.py - Qdrant connection verification
qdrant_skills_disabled = "Skills disabled - Qdrant not required"
qdrant_connection_success = "Qdrant connection successful at {host}:{port}"
qdrant_connection_error = "Cannot connect to Qdrant at {host}:{port}\n\nSolutions:\n1. Start Qdrant: docker-compose up -d\n2. Or disable skills in config.json: 'enable_skills': false"
qdrant_timeout_error = "Timeout connecting to Qdrant at {host}:{port}\n\nVerify that Qdrant is running and accessible."
qdrant_server_error = "Qdrant responds but there is an error: {error}\n\nVerify that Qdrant is functioning correctly."
qdrant_unexpected_error = "Unexpected error connecting to Qdrant: {error}\n\nHost: {host}, Port: {port}"
qdrant_config_error_title = "Qdrant configuration error:"
qdrant_config_error_message = "The application cannot continue without a valid Qdrant connection."

# app.py - Commands dialog
commands_show_list = "Show this list"
commands_dialog_title = "\n Available Commands \n\n\n"
commands_close_hint = "\n  Esc · Enter to close"

# app.py - Skill dialog
skill_dialog_title = "  New Skill"
skill_name_label = "  Skill name"
skill_path_label = "  Path to .md file"
skill_navigation_hint = "  Tab to navigate · Esc to cancel"
skill_accept_button = "  Accept  "
skill_cancel_button = "  Cancel  "

# app.py - Skill messages
skill_validation_error = "[!] Operation cancelled: empty name or path."
skill_creating = "[~] Creating skill '{name}' from {path} ..."
skill_registered_success = "[✓] Skill '{name}' registered successfully."
skill_chunks_processed = "[~] Chunks processed: {count}"
skill_unknown_error = "Unknown error"
skill_creation_error = "[✗] Error creating skill: {error}"

# app.py - Status and toolbar
status_ready = "Ready"
toolbar_hint = "F1 commands  |  F2 new skill  |  Ctrl+Q exit  |  PageUp/Down scroll"

# app.py - Human validation
agent_request_validation = "Agent request validation"
human_response = "The human responded: {response}"
validation_error = "Validation error: {error}"
validation_handler_error = "Error in handle_human_validation_request: {error}"

# app.py - Banner
banner_provider_label = "Provider: "
banner_model_label = "Model: "
banner_unknown_provider_model = "AntFlow - Provider: Unknown | Model: Unknown"

# app.py - Command error messages
error_enable_skill_usage = "[ERROR] Usage: /enable-skill <skill_name>"
error_disable_skill_usage = "[ERROR] Usage: /disable-skill <skill_name>"
error_delete_skill_usage = "[ERROR] Usage: /delete-skill <skill_name>"
error_run_usage = "[ERROR] Usage: /run <query>"
error_unknown_command = "[ERROR] Unknown command: {cmd}  —  type /commands"

# app.py - Status messages
status_lines_in_buffer = "[STATUS] Lines in buffer: {count}"

# app.py - System messages
system_ready_message = "[~] System ready. Type something and press Enter."

# app.py - Error messages
command_processing_error = "[✗] Error processing command: {error}"
