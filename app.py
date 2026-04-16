import asyncio
import os
import argparse
import sys
import threading
import signal
import concurrent.futures
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import (
    HSplit, VSplit, Window, Float, FloatContainer, ConditionalContainer
)
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.filters import Condition
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Button, TextArea, Label, Box
from utils.core.translator import t
from utils.themes.colored_logger import ColoredLogger
from utils.core.logg.ui_logger import set_ui_logger
from utils.themes.animation_buffer import get_animation_buffer, set_toolbar_callback
from utils.themes.styles import get_app_style, UI, LOGS
from utils.core.lazy_loader import LazyLoader
from utils.skills.skill_manager import SkillManager, verify_qdrant_connection
from utils.core.shared import create_model, load_enabled_tools
from utils.core.event_bus import event_bus
from utils.core.agent import clear_agent_memory, run_agent_task
from utils.commands.main_commands import (
    init_commands, list_skills, enable_skill, disable_skill,
    confirm_delete_skill, delete_skill, logg_memory_stats, clear_session
)

skill_manager_instance = None


# ════════════════════════════════════════════════════════════════════════════
# CANCELLATION TOKEN — hilo-seguro, compartido entre asyncio y threads
# ════════════════════════════════════════════════════════════════════════════

class CancellationToken:
    """
    Token thread-safe para cancelar operaciones que corren en hilos secundarios.
    run_agent_task puede chequearlo con .is_cancelled() en puntos de control.
    """
    def __init__(self):
        self._cancelled = threading.Event()

    def cancel(self):
        self._cancelled.set()

    def is_cancelled(self) -> bool:
        return self._cancelled.is_set()

    def reset(self):
        self._cancelled.clear()


# Token global — se reutiliza entre ejecuciones del agente
_agent_cancellation_token = CancellationToken()

# Executor dedicado para el agente (nos permite hacer shutdown limpio)
_agent_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=1,
    thread_name_prefix="antflow-agent",
)


# Variable global para manejo de cierre limpio
shutdown_event = asyncio.Event()
shutdown_requested = False

# Mecanismo para capturar validación humana sin bloquear la UI
human_control = {
    "is_waiting": False,
    "source": None,
    "value": None,
    "sync_event": threading.Event(),
    "metadata": {}
}


def wait_for_human_input():
    human_control["sync_event"].clear()
    human_control["is_waiting"] = True
    human_control["sync_event"].wait()
    human_control["is_waiting"] = False
    return human_control["value"]


def handle_human_validation_request(message):
    """
    Maneja las solicitudes de validación humana desde el sistema de eventos
    """
    try:
        # Seteamos el origen para el handler
        human_control["source"] = "agent"
        
        logger.append("\n" + "─"*50)
        logger.append(t("agent_request_validation"), LOGS.warning)
        logger.append(f" {message}", LOGS.notice)
        logger.append("─"*50 + "\n")

        # Bloqueo del hilo del agente
        user_response = wait_for_human_input()
        
        return t("human_response").format(response=user_response)
    except Exception as e:
        print(t("validation_handler_error").format(error=e))
        return t("validation_error").format(error=str(e))


# ── Banner ────────────────────────────────────────────────────────────────────

def get_banner():
    try:
        try:
            from utils.core.config_loader import get_provider, get_model_id
            provider = get_provider()
            model    = get_model_id()
        except Exception:
            provider = "Unknown"
            model    = "Unknown"

        return [
            ("class:header",   "[AntFlow]"),
            ("",               " " * 45),
            ("class:subtitle",     t("banner_provider_label")),
            ("class:separator", f"{provider}"),
            ("",               " | "),
            ("class:subtitle",     t("banner_model_label")),
            ("class:separator", f"{model}"),
        ]
    except Exception:
        return [("class:header", t("banner_unknown_provider_model"))]


# ── Buffers principales ───────────────────────────────────────────────────────

log_buffer   = Buffer(name="logs", read_only=True)
input_buffer = Buffer(name="input", multiline=True)
logger       = ColoredLogger()


# ════════════════════════════════════════════════════════════════════════════
# DIALOG: /commands
# ════════════════════════════════════════════════════════════════════════════

commands_dialog_visible = {"value": False}
DIALOG_BG = "bg:#1E293B"


def show_commands_dialog():
    commands_dialog_visible["value"] = True
    app.invalidate()


def hide_commands_dialog():
    commands_dialog_visible["value"] = False
    app.layout.focus(input_buffer)
    app.invalidate()


def get_commands_dialog_content():
    all_commands = {
        "/version":        t("cmd_version"),
        "/init":           t("cmd_init"),
        "/init-subagents": t("cmd_init_subagents"),
        "/stop":           t("stop_agent_proccess"),
        "/skill":          t("cmd_skill"),
        "/list-skills":    t("cmd_list_skills"),
        "/enable-skill":   t("cmd_enable_skill"),
        "/disable-skill":  t("cmd_disable_skill"),
        "/delete-skill":   t("cmd_delete_skill"),
        "/memory-stats":   t("cmd_memory_stats"),
        "/clear-memory":   t("cmd_clear_memory"),
        "/clear-session":  t("cmd_clear_all"),
        "/commands":       t("commands_show_list"),
        "/back":           t("cmd_back"),
        "/exit":           t("cmd_exit"),
    }
    result = [(f"{DIALOG_BG} bold #6FE8E0", t("commands_dialog_title"))]
    for cmd, desc in all_commands.items():
        result.append((f"{DIALOG_BG} bold #6BE995", f"  {cmd:<20}"))
        result.append((f"{DIALOG_BG} #B8D4F0",      f"{desc}\n"))
    result.append((f"{DIALOG_BG} italic #2E8BEF", t("commands_close_hint")))
    return result


# ════════════════════════════════════════════════════════════════════════════
# DIALOG: /skill
# ════════════════════════════════════════════════════════════════════════════

skill_dialog_visible = {"value": False}

skill_name_input = TextArea(
    height=1, multiline=False,
    style=f"{DIALOG_BG} #B8D4F0",
    prompt=[("class:skill.input-prefix", "> ")],
)
skill_path_input = TextArea(
    height=1, multiline=False,
    style=f"{DIALOG_BG} #B8D4F0",
    prompt=[("class:skill.input-prefix", "> ")],
)


def show_skill_dialog():
    skill_name_input.text = ""
    skill_path_input.text = ""
    skill_dialog_visible["value"] = True
    app.layout.focus(skill_name_input)
    app.invalidate()


def hide_skill_dialog():
    skill_dialog_visible["value"] = False
    app.layout.focus(input_buffer)
    app.invalidate()


def on_skill_accept():
    name = skill_name_input.text.strip()
    path = skill_path_input.text.strip()
    hide_skill_dialog()

    if not name or not path:
        logger.append(t("skill_validation_error"))
        return

    asyncio.create_task(_execute_skill(name, path))


async def _execute_skill(name: str, path: str):
    logger.append(t("skill_creating").format(name=name, path=path))
    try:
        from utils.skills.add_skill import add_skill_ui
        result = add_skill_ui(name, path)
        #logger.append(str(result))
        if result.get("success"):
            logger.append(t("skill_registered_success").format(name=name))
            if result.get("chunks_processed"):
                logger.append(t("skill_chunks_processed").format(count=result['chunks_processed']))
        else:
            error_msg = result.get("error", t("skill_unknown_error"))
            logger.append(t("skill_creation_error").format(error=error_msg), LOGS.error)
    except Exception as e:
        logger.append(t("skill_creation_error").format(error=e), LOGS.error)
    app.invalidate()


# ════════════════════════════════════════════════════════════════════════════
# CLEANUP — garbage collector para Qdrant, executor y memoria del agente
# ════════════════════════════════════════════════════════════════════════════

def cleanup_at_exit():
    """
    Cleanup robusto:
      1. Cancela cualquier tarea de agente en curso (token thread-safe)
      2. Hace shutdown del executor sin esperar hilos colgados
      3. Limpia skill_manager si existe
    """
    global skill_manager_instance

    # 1. Señalar cancelación al hilo del agente
    _agent_cancellation_token.cancel()

    # 2. Apagar el executor: cancel_futures=True descarta tareas pendientes en
    #    la cola; wait=False evita bloquear el hilo principal si el hilo del
    #    agente está colgado en I/O (p. ej. esperando respuesta de Qdrant).
    try:
        _agent_executor.shutdown(wait=False, cancel_futures=True)
    except TypeError:
        # Python < 3.9 no soporta cancel_futures
        _agent_executor.shutdown(wait=False)
    except Exception:
        pass

    # 3. Limpiar skill manager
    if skill_manager_instance:
        try:
            skill_manager_instance.cleanup()
        except Exception:
            pass


btn_accept = Button(t("skill_accept_button"), handler=on_skill_accept)
btn_cancel = Button(t("skill_cancel_button"), handler=hide_skill_dialog)


def _skill_dialog_window():
    return HSplit([
        Window(height=1, style=f"{DIALOG_BG}"),
        Window(height=2, style=f"{DIALOG_BG}",
               content=FormattedTextControl(
                   text=[(f"{DIALOG_BG} bold #6FE8E0", t("skill_dialog_title"))]),),
        Window(height=1, style=f"{DIALOG_BG}",
               content=FormattedTextControl(
                   text=[(f"{DIALOG_BG} #6C9BB0", "  " + "─" * 40)])),
        Window(height=1, style=f"{DIALOG_BG}",
               content=FormattedTextControl(
                   text=[(f"{DIALOG_BG} #6FE8E0", t("skill_name_label"))]),),
        Box(body=skill_name_input, padding=0, padding_left=2,
            padding_right=2, style=f"{DIALOG_BG}"),
        Window(height=1, style=f"{DIALOG_BG}"),
        Window(height=1, style=f"{DIALOG_BG}",
               content=FormattedTextControl(
                   text=[(f"{DIALOG_BG} #6FE8E0", t("skill_path_label"))]),),
        Box(body=skill_path_input, padding=0, padding_left=2,
            padding_right=2, style=f"{DIALOG_BG}"),
        Window(height=1, style=f"{DIALOG_BG}"),
        Window(height=1, style=f"{DIALOG_BG}",
               content=FormattedTextControl(
                   text=[(f"{DIALOG_BG} #6C9BB0", "  " + "─" * 40)])),
        Window(height=1, style=f"{DIALOG_BG}",
               content=FormattedTextControl(
                   text=[(f"{DIALOG_BG} italic #2E8BEF",
                          t("skill_navigation_hint"))]),),
        VSplit([
            Window(style=f"{DIALOG_BG}"),
            Box(body=btn_accept, padding=0, padding_left=1,
                style=f"{DIALOG_BG}"),
            Box(body=btn_cancel, padding=0, padding_left=1,
                padding_right=2, style=f"{DIALOG_BG}"),
        ], height=1, style=f"{DIALOG_BG}"),
        Window(height=1, style=f"{DIALOG_BG}"),
    ], style=f"{DIALOG_BG}")


# ════════════════════════════════════════════════════════════════════════════
# AGENTE — con CancellationToken y executor dedicado
# ════════════════════════════════════════════════════════════════════════════

agent_running = False
# agent_cancel_event ya no es necesario; usamos _agent_cancellation_token


def _scroll_log_to_bottom():
    try:
        from prompt_toolkit.document import Document
        buf = logger.buffer
        new_pos = len(buf.text)
        if buf.cursor_position != new_pos:
            logger._escribiendo = True
            try:
                buf.set_document(
                    Document(text=buf.text, cursor_position=new_pos),
                    bypass_readonly=True,
                )
            finally:
                logger._escribiendo = False
    except Exception:
        pass

async def stop_agent():
    """Cancela el agente en curso de forma ordenada."""
    global agent_running

    if agent_running:
        logger.append("[!] Stopping agent process...", LOGS.warning)
        _agent_cancellation_token.cancel()
        agent_running = False
        logger.append("[!] Agent process stopped", LOGS.success)
    else:
        logger.append("[!] No agent process to stop", LOGS.warning)


async def run_agent(query: str):
    """
    Ejecuta run_agent_task en el executor dedicado.
    Pasa el CancellationToken para que el agente pueda cooperar en la cancelación.

    NOTA: run_agent_task debe aceptar un kwarg `cancellation_token` (o un
    argumento posicional adicional). Si tu implementación actual no lo acepta
    todavía, el token igual funciona para el shutdown porque el executor se
    cierra en cleanup_at_exit(); simplemente añade el soporte gradualmente.
    """
    global agent_running

    try:
        loop = asyncio.get_event_loop()

        # Resetear el token antes de cada ejecución (por si hubo una cancelación previa)
        _agent_cancellation_token.reset()
        agent_running = True

        # Envolver run_agent_task para inyectar el token sin romper la firma actual.
        # Si run_agent_task ya acepta cancellation_token como kwarg, pásalo directamente.
        def _task_wrapper():
            try:
                # Intenta pasar el token; si la firma no lo soporta, llama sin él.
                try:
                    return run_agent_task(query, cancellation_token=_agent_cancellation_token)
                except TypeError:
                    return run_agent_task(query)
            except Exception as exc:
                raise exc

        future = loop.run_in_executor(_agent_executor, _task_wrapper)

        try:
            response_text, response_info = await asyncio.wait_for(
                future,
                timeout=None,  # Sin timeout -> 300
            )
        except asyncio.CancelledError:
            logger.append("[!] Agent process cancelled")
            _agent_cancellation_token.cancel()
            #clear_agent_memory()
            return

        logger.append("-" * 80, LOGS.command_desc)
        logger.append("\n")
        logger.append(f"[Agent]: {response_text}", LOGS.agent)
        logger.append("\n")

        stats = ""
        if response_info:
            if "token_usage" in response_info and response_info["token_usage"]:
                token_usage = response_info["token_usage"]
                if hasattr(token_usage, "total_tokens"):
                    stats += f"Tokens : {token_usage.total_tokens} - "
            if "timing" in response_info and response_info["timing"]:
                timing = response_info["timing"]
                if hasattr(timing, "total_time"):
                    stats += f"Time: {timing.total_time:.2f}s - "
                if hasattr(timing, "duration"):
                    stats += f"Time: {timing.duration:.2f}s - "
            if "state" in response_info and response_info["state"]:
                stats += f"State: {response_info['state']} "

        if stats:
            logger.append(f"{stats} \n", LOGS.animation_medium)

    except Exception as e:
        logger.append(f"[✗] Error in agent: {str(e)}", LOGS.error)
        logger.append("[✗] Check .antflow/errors.log for more details", LOGS.error)
    finally:
        agent_running = False


# ════════════════════════════════════════════════════════════════════════════
# PROCESADOR DE COMANDOS
# ════════════════════════════════════════════════════════════════════════════

async def process_command_async(text: str):
    from time import sleep
    try:
        await asyncio.sleep(0.01)
        start_animation()
        _scroll_log_to_bottom() 

        if text.startswith("/"):
            parts = text.split(maxsplit=1)
            cmd  = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            match cmd:
                case "/clear":
                    logger.clear()

                case "/commands":
                    show_commands_dialog()

                case "/list-skills":
                    list_skills(skill_manager_instance)

                case "/skill":
                    show_skill_dialog()

                case "/enable-skill":
                    if args:
                        enable_skill(skill_manager_instance, args)
                    else:
                        logger.append(t("error_enable_skill_usage"), LOGS.error)

                case "/disable-skill":
                    if args:
                        disable_skill(skill_manager_instance, args)
                    else:
                        logger.append(t("error_disable_skill_usage"), LOGS.error)

                case "/delete-skill":
                    if args:
                        confirm_delete_skill(args)
                    else:
                        logger.append(t("error_delete_skill_usage"), LOGS.error)

                case "/memory-stats":
                    logg_memory_stats()

                case "/clear-memory":
                    clear_agent_memory()

                case "/clear-session":
                    clear_session()
                
                case "/stop":
                    await stop_agent()

                case "/exit":
                    cleanup_at_exit()
                    sleep(1)
                    app.exit()

                case "/back":
                    logger.clear()
                    logger.append(t("system_ready_message"), LOGS.info)
                    logger.append("─" * 10)

                case "/status":
                    total_lines = len(logger.buffer.document.lines)
                    logger.append(t("status_lines_in_buffer").format(count=total_lines), LOGS.info)

                case "/run":
                    if args:
                        await run_agent(args)
                    else:
                        logger.append(t("error_run_usage"))

                case _:
                    logger.append(
                        t("error_unknown_command").format(cmd=cmd)
                    )
        else:
            await run_agent(text)

    except Exception as e:
        logger.append(t("command_processing_error").format(error=str(e)))
    finally:
        stop_animation()
        if app:
            app.invalidate()


def handle_command(text: str):
    asyncio.create_task(process_command_async(text))


# ════════════════════════════════════════════════════════════════════════════
# TOOLBAR
# ════════════════════════════════════════════════════════════════════════════

status             = {"text": t("status_ready")}
toolbar_left_text  = ""
toolbar_right_text = ""


def update_toolbar_from_animation(left_text: str, right_text: str):
    global toolbar_left_text, toolbar_right_text
    toolbar_left_text  = left_text
    toolbar_right_text = right_text
    if app:
        app.invalidate()


def get_toolbar_text():
    global toolbar_left_text, toolbar_right_text

    if toolbar_left_text and toolbar_right_text:
        left_clean  = toolbar_left_text.replace("[thinking]", "").replace("[tool_name]", "")
        right_clean = toolbar_right_text.replace("[thinking]", "").replace("[tool_name]", "")

        if "[" in left_clean and "]" in left_clean:
            start = left_clean.find("[")
            end   = left_clean.find("]", start)
            if start != -1 and end != -1:
                animation_part = left_clean[start + 1:end]
                formatted_parts = []
                for char in animation_part:
                    if char == "░":
                        formatted_parts.append(("class:animation.shadow", char))
                    elif char == "▒":
                        formatted_parts.append(("class:animation.medium", char))
                    elif char == "█":
                        formatted_parts.append(("class:animation.solid", char))
                    else:
                        formatted_parts.append(("", char))

                before_text = left_clean[:start]
                after_text  = left_clean[end + 1:]
                parts_list  = [("class:toolbar-left", before_text)]
                parts_list.extend(formatted_parts)
                parts_list.append(("class:toolbar-left", after_text))
                parts_list.append(("", "  "))
                parts_list.append(("class:toolbar-right", right_clean))
                return parts_list

        return [
            ("class:toolbar-left",  left_clean),
            ("", "  "),
            ("class:toolbar-right", right_clean),
        ]

    return [
        ("class:hint-text",
         t("toolbar_hint"))
    ]


# ════════════════════════════════════════════════════════════════════════════
# ESTILOS
# ════════════════════════════════════════════════════════════════════════════

style = get_app_style()


# ════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ════════════════════════════════════════════════════════════════════════════

def create_layout():
    main_content = HSplit([
        Window(
            height=1,
            dont_extend_height=True,
            style="class:separator",
            content=FormattedTextControl(text=get_banner),
        ),
        #Window(height=1, style="class:separator", dont_extend_height=True),
        Window(
            height=1,
            style="class:separator",
            dont_extend_height=True,
            content=FormattedTextControl(text=lambda: [("class:separator_line", "─" * 200)]),
        ),
        Window(
            content=BufferControl(buffer=logger.buffer, lexer=logger.lexer),
            wrap_lines=True,
            style="class:log-area",
            allow_scroll_beyond_bottom=True,
        ),
        Window(height=1, style="class:separator", dont_extend_height=True),
        #Window(height=1, dont_extend_height=True),
        Window(
            height=1,
            style="class:separator",
            dont_extend_height=True,
            content=FormattedTextControl(text=lambda: [("class:separator_line", "─" * 200)]),
        ),
        Window(
            height=lambda: min(
                max(input_buffer.text.count("\n") + 1, 1) + 1,
                3
            ),
            dont_extend_height=True,
            content=BufferControl(
                buffer=input_buffer,
                focusable=True,
                preview_search=False,
            ),
            wrap_lines=True,
            get_line_prefix=lambda lineno, wrap_count: (
                [("class:input-prefix", "> ")] if lineno == 0 and wrap_count == 0 else
                [("", "  ")]  
            ),
        ),
        Window(height=1, style="class:separator", dont_extend_height=True),
        Window(
            height=1,
            dont_extend_height=True,
            style="class:toolbar-bg",
            content=FormattedTextControl(text=lambda: get_toolbar_text()),
        ),
    ])

    commands_float = Float(
        content=ConditionalContainer(
            content=Window(
                width=62, height=22,
                style=f"{DIALOG_BG} #B8D4F0",
                content=FormattedTextControl(
                    text=get_commands_dialog_content,
                    focusable=True,
                ),
            ),
            filter=Condition(lambda: commands_dialog_visible["value"]),
        ),
        xcursor=False, ycursor=False,
    )

    skill_float = Float(
        content=ConditionalContainer(
            content=Box(
                body=_skill_dialog_window(),
                width=50, height=14, padding=0,
                style=f"{DIALOG_BG}",
            ),
            filter=Condition(lambda: skill_dialog_visible["value"]),
        ),
        xcursor=False, ycursor=False,
    )

    return Layout(
        FloatContainer(
            content=main_content,
            floats=[commands_float, skill_float],
        )
    )


layout = create_layout()


# ════════════════════════════════════════════════════════════════════════════
# KEY BINDINGS
# ════════════════════════════════════════════════════════════════════════════

kb = KeyBindings()


@kb.add("tab", filter=Condition(lambda: skill_dialog_visible["value"]))
def skill_tab(event):
    focus_next(event)


@kb.add("s-tab", filter=Condition(lambda: skill_dialog_visible["value"]))
def skill_shift_tab(event):
    focus_previous(event)


@kb.add("enter")
def handle_enter(event):
    if commands_dialog_visible["value"]:
        hide_commands_dialog()
        return

    if skill_dialog_visible["value"]:
        return

    text = input_buffer.text.strip()
    if text:
        if human_control["is_waiting"]:
            source = human_control["source"]

            if source == "agent":
                human_control["value"] = text
                human_control["sync_event"].set()
                input_buffer.reset()
                return

            elif source == "delete_confirm":
                skill_id = human_control["metadata"]["skill_id"]
                if text in ["yes", "y", "si", "s"]:
                    delete_skill(skill_id)
                else:
                    logger.append(t("skill_delete_cancelled_user"))

                human_control["is_waiting"] = False
                human_control["source"] = None
                input_buffer.reset()
                app.invalidate()
                return

        logger.append(f"» {text}")
        _scroll_log_to_bottom()
        input_buffer.reset()
        if app:
            app.invalidate()
        asyncio.create_task(process_command_async(text))


@kb.add("escape")
def handle_escape(event):
    if commands_dialog_visible["value"]:
        hide_commands_dialog()
        return
    if skill_dialog_visible["value"]:
        hide_skill_dialog()


@kb.add("f1")
def open_commands_f1(event):
    show_commands_dialog()


@kb.add("f2")
def open_skill_f2(event):
    show_skill_dialog()


@kb.add("c-c")
@kb.add("c-q")
def handle_exit(event):
    """
    Ctrl+C / Ctrl+Q desde la UI de prompt_toolkit.
    Hace cleanup completo antes de salir para garantizar que Qdrant
    y el executor queden liberados.
    """
    cleanup_at_exit()
    event.app.exit()


@kb.add("pageup")
def scroll_up(event):
    event.app.layout.focus(logger.buffer)
    logger.buffer.cursor_up(count=10)
    event.app.layout.focus(input_buffer)


@kb.add("pagedown")
def scroll_down(event):
    event.app.layout.focus(logger.buffer)
    logger.buffer.cursor_down(count=10)
    event.app.layout.focus(input_buffer)


# ════════════════════════════════════════════════════════════════════════════
# APP
# ════════════════════════════════════════════════════════════════════════════

app = Application(
    layout=layout,
    key_bindings=kb,
    style=style,
    full_screen=True,
    mouse_support=True,
)

app.layout.focus(input_buffer)
logger.set_app(app)


# ════════════════════════════════════════════════════════════════════════════
# ANIMACIÓN
# ════════════════════════════════════════════════════════════════════════════

def start_animation():
    try:
        get_animation_buffer().start_animation()
    except Exception as e:
        print(f"Error iniciando animación: {e}")


def stop_animation():
    try:
        global toolbar_left_text, toolbar_right_text
        get_animation_buffer().stop_animation()
        toolbar_left_text  = ""
        toolbar_right_text = ""
        if app:
            app.invalidate()
    except Exception as e:
        print(f"Error deteniendo animación: {e}")


# ════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

def parse_arguments():
    try:
        from utils.core.translator import t
    except ImportError:
        def t(key):
            fallbacks = {
                "argparse_description":           "AntFlow - Open source agentic framework",
                "argparse_version_help":          "Show application version",
                "argparse_agent_help":            "Open agent in terminal mode",
                "argparse_init_help":             "Initialize project.",
                "argparse_init_subagents_help":   "Initialize project with subagents.",
            }
            return fallbacks.get(key, key)

    parser = argparse.ArgumentParser(description=t("argparse_description"))
    group  = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-v", "--version",         action="store_true", help=t("argparse_version_help"))
    group.add_argument("-a", "--agent",           action="store_true", help=t("argparse_agent_help"))
    group.add_argument("-i", "--init",            nargs='?', const="ollama",
                       choices=["ollama", "openrouter"], default=None,
                       help=t("argparse_init_help"))
    group.add_argument("-s", "--init-subagents",  nargs='?', const="ollama",
                       choices=["ollama", "openrouter"], default=None,
                       help=t("argparse_init_subagents_help"))
    return parser.parse_args()


def handle_version():
    try:
        from utils.themes.header import create_antflow_banner
        create_antflow_banner()
    except ImportError:
        print("AntFlow - Open source agentic framework")
        print("Version: 1.0.0")
    sys.exit(0)


def handle_init_commands(args):
    try:
        from utils.themes.theme_manager import theme_manager
        from utils.themes.common import clear_console
        from utils.core.init_config_files import initialize_project_files
        from utils.core.translator import t
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        sys.exit(1)

    config_type    = None
    use_subagents  = False

    if args.init is not None:
        config_type   = args.init
        use_subagents = False
    elif getattr(args, 'init_subagents') is not None:
        config_type   = getattr(args, 'init_subagents')
        use_subagents = True

    clear_console()
    initialize_project_files(theme_manager, use_subagents_prompt=use_subagents,
                              config_type=config_type)

    if use_subagents:
        theme_manager.print_success_text(t("project_init_success_subagents"))
    else:
        theme_manager.print_success_text(t("project_init_success"))
    theme_manager.print_info_text(t("antflow_folder_created"))
    sys.exit(0)


def main():
    import multiprocessing
    multiprocessing.freeze_support() 

    args = parse_arguments()

    if args.version:
        handle_version()

    if args.init is not None or getattr(args, 'init_subagents') is not None:
        handle_init_commands(args)

    if args.agent:
        try:
            asyncio.run(run())
            return
        except ImportError as e:
            print(f"Error importing required modules for agent mode: {e}")
            sys.exit(1)

    if not any([args.version, args.agent,
                args.init is not None,
                getattr(args, 'init_subagents') is not None]):
        try:
            asyncio.run(run())
            return
        except ImportError as e:
            print(f"Error importing required modules: {e}")
            sys.exit(1)


def init_skill_manager():
    global skill_manager_instance
    from atexit import register

    from utils.core.config_loader import get_enable_skills
    if not get_enable_skills():
        class MockSkillManager:
            def get_available_skills(self): return []
            def get_enabled_skills(self):   return []
            def set_skill_enabled(self, *args): return False
            def cleanup(self): pass
        skill_manager_instance = MockSkillManager()
    else:
        skill_manager_class    = LazyLoader.import_class('utils.skills.skill_manager', 'SkillManager')
        skill_manager_instance = skill_manager_class()

    register(cleanup_at_exit)


async def validate_qdrant():
    try:
        is_valid, message = verify_qdrant_connection()
        if not is_valid:
            print(f"\n{t('qdrant_config_error_title')}")
            print(f"{message}")
            print(f"\n{t('qdrant_config_error_message')}")
            sys.exit(1)
    except Exception as e:
        print(f"\nError verificando conexión a Qdrant: {str(e)}")
        print(f"\n{t('qdrant_config_error_message')}")
        sys.exit(1)


async def run():
    await validate_qdrant()

    app.layout.focus(input_buffer)
    set_ui_logger(logger)
    set_toolbar_callback(update_toolbar_from_animation)
    init_skill_manager()
    init_commands(logger, skill_manager_instance, human_control, app)
    
    # Configurar sistema de eventos para validación humana
    event_bus.subscribe("human_validation_request", handle_human_validation_request)

    try:
        await app.run_async()
    except asyncio.CancelledError:
        print("\n\n[!] Closing application...")
    except SystemExit:
        raise
    finally:
        cleanup_at_exit()


# ════════════════════════════════════════════════════════════════════════════
# SIGNAL HANDLER — Ctrl+C desde la terminal (fuera de prompt_toolkit)
# ════════════════════════════════════════════════════════════════════════════

def signal_handler(signum, frame):
    """
    Maneja SIGINT / SIGTERM con cleanup garantizado.

    Flujo:
      1. Marca shutdown para evitar re-entradas.
      2. Señala cancelación al token del agente → el hilo coopera y sale.
      3. Cierra el executor (sin esperar hilos colgados).
      4. Limpia memoria / Qdrant.
      5. Cierra prompt_toolkit.
      6. Si en 2 s nada respondió, fuerza os._exit(0).
    """
    global shutdown_requested, agent_running

    if shutdown_requested:
        # Segunda señal: salida brutal inmediata
        os._exit(1)

    shutdown_requested = True

    # ── 1. Cancelar agente ────────────────────────────────────────────────
    _agent_cancellation_token.cancel()
    agent_running = False

    # ── 2. Shutdown del executor (no bloquea) ─────────────────────────────
    try:
        _agent_executor.shutdown(wait=False, cancel_futures=True)
    except TypeError:
        _agent_executor.shutdown(wait=False)
    except Exception:
        pass

    try:
        if skill_manager_instance:
            skill_manager_instance.cleanup()
    except Exception:
        pass

    # ── 4. Cerrar la app de prompt_toolkit ───────────────────────────────
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.call_soon_threadsafe(app.exit)
    except Exception:
        pass

    # ── 5. Watchdog: si en 2 s el proceso no salió, forzar ───────────────
    def _watchdog():
        import time
        time.sleep(2)
        os._exit(0)

    threading.Thread(target=_watchdog, daemon=True).start()


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()  # ← aquí también
    
    signal.signal(signal.SIGINT,  signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        main()
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")
        sys.exit(1)