import os
import json
from smolagents import Tool, CodeAgent, ActionStep
from .base_subagent import Subagent
from utils.tools.utils.common import notify_subagent_usage
from utils.core.config_loader import get_memory_subagents_persistent, get_model_id
from datetime import datetime
from utils.core.config_loader import get_provider
from utils.core.logg.steps_logger import logg_step



# ActionStep(
#     step_number: int,
#     timing: Timing,
#     model_input_messages: list[ChatMessage] | None = None,
#     tool_calls: list[ToolCall] | None = None,
#     error: AgentError | None = None,
#     model_output_message: ChatMessage | None = None,
#     model_output: str | list[dict[str, Any]] | None = None,
#     code_action: str | None = None,
#     observations: str | None = None,
#     observations_images: list[PIL.Image.Image] | None = None,
#     action_output: Any = None,
#     token_usage: TokenUsage | None = None,
#     is_final_answer: bool = False
# )



# Creamos nuestro propio "ManagedAgent". 
# Esto hace EXACTAMENTE lo mismo que el original: 
# envolver un agente para que otro lo use.
class SubagentWrapper(Tool):
    def __init__(self, agent, name, description):
        super().__init__()
        self.agent = agent
        self.name = name
        self.description = description
        # Definimos inputs solo para validación del framework
        self.inputs = {
            "task": {"type": "string", "description": "La tarea específica para este subagente"}
        }
        self.output_type = "string"

    def forward(self, task: str) -> str:
        notify_subagent_usage(self.name, "active")
        
        memory_persisten_subagents = get_memory_subagents_persistent()

        if memory_persisten_subagents:
        
            # --- NUEVA LÓGICA DE PERSISTENCIA ---
            state_path = ".antflow/project_status.md"
            current_context = ""
            if os.path.exists(state_path):
                with open(state_path, "r", encoding="utf-8") as f:
                    current_context = f.read()
            
            # Enriquecemos la tarea con el contexto histórico
            enriched_task = f"""
            ESTADO PREVIO DEL PROYECTO:
            {current_context if current_context else "No hay pasos previos."}
            
            TU TAREA ACTUAL:
            {task}
            
            INSTRUCCIÓN: Al terminar o avanzar significativamente, usa 'project_status_manager' 
            para dejar un reporte de lo que hiciste para el siguiente agente.
            """
        else:
            enriched_task = task
        
        try:
            return self.agent.run(enriched_task)
        finally:
            notify_subagent_usage(None, "idle")
    
    def __call__(self, *args, **kwargs):
        """
        El método __call__ es invocado por el orquestador. 
        Simplemente lo redirigimos al motor de validación de la clase Tool.
        """
        # Si smolagents intenta pasar el 'task' como argumento posicional
        if args and not kwargs.get('task'):
            kwargs['task'] = args[0]
            
        # Llamamos al __call__ de la clase base Tool, que validará los inputs
        # y finalmente ejecutará nuestro método 'forward'.
        return super().__call__(**kwargs)

def stop_live_display():
    """Limpia el área de texto cuando termina sin afectar el banner"""
    global _text_lines, _first_update
    
    try:
        # Limpiar solo el área de texto, no el banner
        print("\033[4A", end="")  # Mover 4 líneas arriba
        for _ in range(4):
            print("\033[K", end="")  # Limpiar línea
            print("\033[1B", end="")  # Mover abajo
        
        _text_lines = []
        _first_update = True
            
    except:
        pass

                    
def load_enabled_agents():
    """Carga los agentes y los devuelve envueltos como herramientas gestionadas."""
    # Imports fuera del try para identificar errores de importación
    from utils.core.config_loader import get_enabled_subagents
    if not get_enabled_subagents():
        return []
    
    # Solo el JSON dentro del try
    try:
        if not os.path.exists(".antflow/subagents.json"): 
            return []
        with open(".antflow/subagents.json", "r") as f:
            config = json.load(f)["subagentes"]
    except Exception as e:
        print(f" Error leyendo JSON: {e}")
        return []
    
    # El resto del procesamiento fuera del try principal
    final_agents = []
    for a_id, info in config.items():
        if info.get("enabled", True):
            # Cargar el prompt desde el archivo .md
            prompt_file = info["prompt"]
            prompt_path = os.path.join(".antflow/subagents", prompt_file)
            
            if os.path.exists(prompt_path):
                with open(prompt_path, "r", encoding="utf-8") as pf:
                    prompt_content = pf.read().strip()
            else:
                print(f"Advertencia: No se encuentra el archivo de prompt {prompt_path}")
                continue
            
            # 1. Instancia tu clase base (ToolCallingAgent)
            # Preparar parámetros dinámicamente
            subagent_params = {
                "prompt": prompt_content,
                "name": info.get("name", a_id),
                "description": info["description"],
                "step_callbacks": [logg_step],
                "verbosity_level": info.get("verbosity_level", -1)
            }
            
   
            if info.get("model") is not None:
                # Si el modelo esta configurado en subagentes.json, usar esos parametros
                subagent_params["model_id"] = info.get("model")
                subagent_params["num_ctx"] = info.get("num_ctx", 4096)
                subagent_params["temperature"] = info.get("temperature", 0.5)
            else:
                #Toma el mismo modelo del agente principal
                subagent_params["model_id"] = get_model_id()

            
            sub_inst = Subagent(**subagent_params)
            
            # 2. Envolverlo en nuestro Wrapper
            # El CodeAgent principal lo aceptará en managed_agents o en tools
            wrapped = SubagentWrapper(sub_inst, sub_inst.name, sub_inst.description)
            final_agents.append(wrapped)
    
    return final_agents
