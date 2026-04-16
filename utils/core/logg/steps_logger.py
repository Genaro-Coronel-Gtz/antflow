"""Módulo para logging de archivos de subagentes"""

import os
from datetime import datetime
from smolagents import Tool, CodeAgent, ActionStep
from utils.core.config_loader import get_provider
from utils.themes.styles import LOGS
import re


def get_code_from_context(content: str):
    """Extrae bloques de código del contenido y devuelve content sin código y el código separado"""
    code = ""
    
    # Buscar bloques de código con ```
    pattern = r'```(?:\w+)?\n([\s\S]*?)\n```'
    matches = re.findall(pattern, content)
    
    if matches:
        # Extraer el primer bloque de código encontrado
        code = matches[0].strip()
        
        # Eliminar todos los bloques de código del contenido
        content_without_code = re.sub(pattern, '', content)
        content = content_without_code.strip()
    
    return content, code


def update_ui_logs_subagent(text: str, step_number: int):
    """Envía los logs del subagente al logger global de main.py"""
    try:
        # Intentar obtener el logger global del módulo centralizado
        try:
            from utils.core.logg.ui_logger import get_ui_logger
            ui_logger = get_ui_logger()
            
            if ui_logger and ui_logger.is_available():
                # Limitar el texto para evitar muy largas
                max_length = 700
                content = text if len(text) <= max_length else text[:max_length] + "..."
                
                # Formatear mensaje para el logger
                title = f"Step {step_number}: Reasoning"
                content, code = get_code_from_context(content)
               
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

                subagent = {}

                try:
                    from utils.tools.utils.common import get_current_subagent
                    subagent = get_current_subagent()
                except Exception as e:
                    subagent = {"name": None}
                
                subagent_name = subagent.get("name", "Agent")

                step = f"[{subagent_name}]: {title} - [Time]: {timestamp} \n"
                # Enviar mensajes al logger global con prefijos apropiados
                ui_logger.append("-" * 80, LOGS.command_desc)
                ui_logger.append(step, LOGS.thinking)
                ui_logger.append(content, LOGS.foreground)
                if code:
                    ui_logger.append(code, "code")
                
                return
                
        except ImportError:
            # Si no podemos importar el módulo, no hacer nada
            pass
            
    except Exception as e:
        # Si hay error, intentar con el logger global
        try:
            from utils.core.logg.ui_logger import get_ui_logger
            ui_logger = get_ui_logger()
            if ui_logger and ui_logger.is_available():
                ui_logger.append(f"[_subagent_] Step {step_number}: {str(text)[:100]}...")
        except:
            pass  # Silencioso si no funciona


def logg_step(step: ActionStep, agent: CodeAgent):
    """Tu logger de pasos que ya funciona"""
    
    os.makedirs(".antflow/logs/subagents", exist_ok=True)
    log_path = f".antflow/logs/subagents/{agent.name.lower().replace(' ', '_')}.log"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"\n--- SUBAGENT STEP: [{step.step_number}]---\n")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        f.write(f"Time stamp: {timestamp}\n")
        f.write("\n")

        if step.model_output and get_provider() == "Ollama":
            f.write(f"Reasoning: {step.model_output}\n")
            update_ui_logs_subagent(step.model_output, step.step_number)
            
        # Acceder al reasoning_content del model_output_message
        if step.model_output_message:
            raw = step.model_output_message.raw
            if raw:
                try:
                    reasoning_content = raw.choices[0].message.reasoning_content
                    if get_provider() == "OpenRouter":
                        f.write(f"Reasoning: {reasoning_content}\n")
                        update_ui_logs_subagent(reasoning_content, step.step_number)
                except (AttributeError, IndexError):
                    reasoning_content = None

            
        # Tool calls desde model_output_message.raw
        if step.model_output_message and step.model_output_message.raw:
            raw = step.model_output_message.raw
            if raw.choices and raw.choices[0].message.tool_calls:
                tool_calls = raw.choices[0].message.tool_calls
                f.write(f"Tool calls ({len(tool_calls)}):\n")
                for i, tool_call in enumerate(tool_calls, 1):
                    f.write(f"  {i}. {tool_call.function.name}: {tool_call.function.arguments[:100]}\n")
                    update_ui_logs_subagent(f" Tool Calling - {i}. {tool_call.function.name}: {tool_call.function.arguments[:100]}", step.step_number)
                    if not (tool_call.function.name in ["python_interpreter", "final_answer"]):
                        f.write(f"---------------------------------\n")
                        f.write(f"only tool: {tool_call.function.name}\n")
                
        # Code Action
        code_action = getattr(step, 'code_action', '...')
        if code_action and len(code_action) > 500:
            code_action = code_action[:500] + "..."
            f.write(f"---------------------------------\n")
            f.write(f"Code action: {code_action}\n")


        observations = getattr(step, 'observations', '...')
        if observations and len(observations) > 500:
            observations = observations[:500] + "..."
            f.write(f"---------------------------------\n")
            f.write(f"Observations: {observations}\n")
        
       
        
        # Cost information from model_output_message
        if step.model_output_message and step.model_output_message.raw and get_provider() == "OpenRouter":
            raw = step.model_output_message.raw
            if hasattr(raw, 'usage') and raw.usage:
                usage = raw.usage
                f.write(f"---------------------------------\n")
                f.write("Cost Information:\n")
                
                # Basic cost info
                if hasattr(usage, 'cost'):
                    f.write(f"  Total Cost: {usage.cost}\n")
                if hasattr(usage, 'is_byok'):
                    f.write(f"  Is BYOK: {usage.is_byok}\n")
                
                # Cost details
                if hasattr(usage, 'cost_details') and usage.cost_details:
                    cost_details = usage.cost_details
                    f.write(f"  Upstream Inference Cost: {cost_details.get('upstream_inference_cost', 'N/A')}\n")
                    f.write(f"  Upstream Prompt Cost: {cost_details.get('upstream_inference_prompt_cost', 'N/A')}\n")
                    f.write(f"  Upstream Completions Cost: {cost_details.get('upstream_inference_completions_cost', 'N/A')}\n")
                
                # Token usage details
                if hasattr(usage, 'completion_tokens_details') and usage.completion_tokens_details:
                    comp_details = usage.completion_tokens_details
                    f.write("  Completion Tokens Details:\n")
                    f.write(f"    Reasoning Tokens: {getattr(comp_details, 'reasoning_tokens', 'N/A')}\n")

                
                if hasattr(usage, 'prompt_tokens_details') and usage.prompt_tokens_details:
                    prompt_details = usage.prompt_tokens_details
                    f.write("  Prompt Tokens Details:\n")
                    f.write(f"    Cached Tokens: {getattr(prompt_details, 'cached_tokens', 'N/A')}\n")
                    f.write(f"    Cache Write Tokens: {getattr(prompt_details, 'cache_write_tokens', 'N/A')}\n")

        token_usage = getattr(step, 'token_usage', '...')
        if token_usage:
            f.write(f"Token usage: Input tokens : {token_usage.input_tokens}, Output tokens : {token_usage.output_tokens}, Total tokens : {token_usage.total_tokens}\n ")   
            f.write("=" * 150 + "\n")
