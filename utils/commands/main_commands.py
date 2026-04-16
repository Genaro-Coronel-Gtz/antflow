"""Comandos principales de la aplicación refactorizados desde main.py"""

from utils.skills.skill_manager import SkillManager
from utils.core.lazy_loader import LazyLoader
from utils.core.translator import t
from utils.themes.styles import get_app_style, UI, LOGS


# Variables globales que se necesitan desde main.py
logger = None
skill_manager_instance = None
human_control = None
app = None


def init_commands(logger_instance, skill_manager, human_ctrl, app_instance):
    """Inicializa las variables globales necesarias para los comandos"""
    global logger, skill_manager_instance, human_control, app
    logger = logger_instance
    skill_manager_instance = skill_manager
    human_control = human_ctrl
    app = app_instance


def list_skills(skill_manager: SkillManager):
    try:
        # Usar el manager dual (funciona con LanceDB y Qdrant)
        available_skills = skill_manager.get_available_skills()
        enabled_skills = skill_manager.get_enabled_skills()
        
        if not available_skills:
            logger.append(t("no_skills_db"))
            return
        
        logger.append(f"\n{t('total_skills').format(count=len(available_skills))}")
        logger.append(f"{t('active_skills').format(count=len(enabled_skills))}\n")
        
        for skill_name in sorted(available_skills):
            status = t("skill_status_enabled_display") if skill_name in enabled_skills else t("skill_status_disabled_display")
            skill_line = f"{skill_name:<20}"
            log_status = LOGS.success if status == t("skill_status_enabled_display") else LOGS.error
            logger.append(skill_line, log_status)
        
    except Exception as e:
        logger.append(t("error_listing_skills").format(error=e))


def enable_skill(skill_manager: SkillManager, skill_name: str):
    """Habilita una skill específica sin preguntar al usuario"""
    try:
        # Obtener todas las skills disponibles
        available_skills = skill_manager.get_available_skills()
        enabled_skills = skill_manager.get_enabled_skills()
        
        # Validar que la skill exista
        if skill_name not in available_skills:
            logger.append(t("skill_not_exists").format(skill_name=skill_name))
            return
        
        # Validar que esté deshabilitada
        if skill_name in enabled_skills:
            logger.append(t("skill_already_enabled").format(skill_name=skill_name))
            return
        
        # Habilitar la skill
        success = skill_manager.set_skill_enabled(skill_name, True)
        
        if success:
            logger.append(t("skill_enabled_success").format(skill_name=skill_name), LOGS.success)
            logger.append(t("total_active_skills").format(count=len(enabled_skills) + 1), LOGS.success)
        else:
            logger.append(t("skill_enable_error").format(skill_name=skill_name), LOGS.error)
        
    except Exception as e:
        logger.append(t("skill_enable_general_error").format(error=e))


def disable_skill(skill_manager: SkillManager, skill_name: str):
    """Deshabilita una skill específica sin preguntar al usuario"""
    try:
        # Obtener skills activas
        enabled_skills = skill_manager.get_enabled_skills()
        
        # Validar que la skill exista y esté activa
        if skill_name not in enabled_skills:
            # Verificar si existe pero ya está deshabilitada
            available_skills = skill_manager.get_available_skills()
            if skill_name in available_skills:
                logger.append(t("skill_already_disabled").format(skill_name=skill_name))
            else:
                logger.append(t("skill_not_exists").format(skill_name=skill_name))
            return
        
        # Deshabilitar la skill
        success = skill_manager.set_skill_enabled(skill_name, False)
        
        if success:
            logger.append(t("skill_disabled_success").format(skill_name=skill_name), LOGS.success)
            logger.append(t("total_active_skills_after").format(count=len(enabled_skills) - 1), LOGS.success)
        else:
            logger.append(t("skill_disable_error").format(skill_name=skill_name), LOGS.error)
        
    except Exception as e:
        logger.append(t("skill_disable_general_error").format(error=e))


def confirm_delete_skill(skill_id: str):
    """Confirma la eliminación de una skill"""
    human_control["is_waiting"] = True
    human_control["source"] = "delete_confirm"
    human_control["metadata"] = {"skill_id": skill_id}
    
    logger.append(t("skill_delete_warning").format(skill_id=skill_id))
    logger.append(t("skill_delete_confirm_prompt"), LOGS.warning)
    app.invalidate()
    return # Salimos, el flujo se detiene aquí hasta que el usuario escriba algo


def delete_skill(skill_id: str):
    """Elimina una skill desde el modo agente"""
    try:
        # Lazy loading de la función de eliminación
        try:
            delete_skill_module = LazyLoader.import_module('utils.skills.delete_skill')
            delete_skill = delete_skill_module.delete_skill
        except ImportError:
            # Fallback para ejecución desde binario - importación directa
            from utils.skills import delete_skill
            delete_skill = delete_skill.delete_skill
        
        # Eliminar la skill
        success = skill_manager_instance.delete_skill(skill_id)
        
        if success:
            logger.append(t("skill_delete_success_msg").format(skill_id=skill_id), LOGS.success)
        else:
            logger.append(t("skill_delete_error_msg").format(skill_id=skill_id), LOGS.error)
        
    except KeyboardInterrupt:
        logger.append(t("skill_delete_cancelled_keyboard"), LOGS.warning)
    except Exception as e:
        logger.append(t("skill_delete_general_error").format(error=e), LOGS.error)


def logg_memory_stats():
    from utils.memory.memory_agent import agent_memory
    """Muestra estadísticas de memoria"""
    stats = agent_memory.get_stats()
    logger.append(t("memory_stats_title"))
    logger.append(t("memory_total_messages").format(count=stats['total_messages']))
    logger.append(t("memory_user_messages").format(count=stats['user_messages']))
    logger.append(t("memory_agent_messages").format(count=stats['assistant_messages']))
    logger.append(t("memory_system_messages").format(count=stats['system_messages']))
    logger.append(t("memory_max_limit").format(limit=stats['max_messages']))
    logger.append(t("memory_file").format(file=stats['memory_file']))


def clear_session():
    from os import path, listdir
    """Limpia todos los archivos de logs, contexto y memoria"""
    files_to_clear = [
        ".antflow/context.md",
        ".antflow/project_status.md",
        ".antflow/antflow.log",
        ".antflow/errors.log"
    ]
    
    # Limpiar archivos individuales
    for file_path in files_to_clear:
        try:
            if path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write("")
                logger.append(f"Cleared: {path.basename(file_path)}", LOGS.success)
        except Exception as e:
            logger.append(f"Error clearing {file_path}: {e}", LOGS.error)

    from time import sleep
    sleep(1)
    clear_agent_memory()

    # Limpiar todos los archivos en logs/subagents/
    logs_dir = ".antflow/logs/subagents"
    if path.exists(logs_dir):
        try:
            for filename in listdir(logs_dir):
                file_path = path.join(logs_dir, filename)
                try:
                    with open(file_path, 'w') as f:
                        f.write("")
                    logger.append(f"Cleared: logs/subagents/{filename}", LOGS.success)
                except Exception as e:
                    logger.append(f"Error clearing {file_path}: {e}", LOGS.error)
        except Exception as e:
            logger.append(f"Error accessing logs directory: {e}", LOGS.error)


def clear_agent_memory():
    """Limpia la memoria del agente"""
    from utils.memory.memory_agent import agent_memory
    agent_memory.clear()
    #logger.append("Agent memory cleared", LOGS.success)
