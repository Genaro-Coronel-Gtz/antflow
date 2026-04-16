from smolagents import ToolCallingAgent, PromptTemplates
from utils.core.shared import create_model, load_enabled_tools

class Subagent(ToolCallingAgent):
    """
    Clase base para subagentes configurables dinámicamente via JSON.
    Hereda de ToolCallingAgent para ser compatible con agentes gestionados.
    """
    
    def __init__(self, prompt: str, model_id: str = None, max_steps: int = 30, verbosity_level: int = 0,
     add_base_tools: bool = False, name: str = "", description: str = "", step_callbacks: list = None,
     num_ctx: int = 4096, temperature: float = 0.5):
        """
        Inicializa el subagente con configuración personalizada.
        
        Args:
            prompt: Prompt especializado para el subagente.
            model_id: ID específico del modelo para este subagente (opcional).
            max_steps: Máximo número de pasos.
            verbosity_level: Nivel de verbosidad.
            add_base_tools: Si añadir herramientas base adicionales.
            name: Nombre del subagente (requerido para agentes gestionados).
            description: Descripción del subagente (requerida para agentes gestionados).
        """
        self.custom_prompt = prompt
        
        # Crear el modelo específico si se proporciona, sino usar el global
        if model_id:
            from utils.core.shared import create_custom_model
            model = create_custom_model(model_id, num_ctx=num_ctx, temperature=temperature)
        else:
            from utils.core.shared import create_model
            model = create_model()
        
        # Crear un agente temporal para obtener los templates por defecto
        temp_agent = ToolCallingAgent(
            tools=load_enabled_tools(),
            model=model
        )
        
        # Copiar los templates por defecto y modificar solo el system_prompt
        prompt_templates = PromptTemplates(
            system_prompt=prompt,
            planning=temp_agent.prompt_templates['planning'],
            managed_agent=temp_agent.prompt_templates['managed_agent'],
            final_answer=temp_agent.prompt_templates['final_answer']
        )
        
        # Inicializar ToolCallingAgent padre con prompt_templates
        super().__init__(
            tools=load_enabled_tools(),
            model=model,
            prompt_templates=prompt_templates,
            max_steps=max_steps,
            verbosity_level=verbosity_level,
            add_base_tools=add_base_tools,
            step_callbacks=step_callbacks
        )
        
        # Asignar atributos requeridos para agentes gestionados
        self.name = name
        self.description = description
    
    def get_system_prompt(self):
        """Devuelve el prompt personalizado del subagente."""
        return self.custom_prompt