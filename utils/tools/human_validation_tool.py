from smolagents import Tool
from utils.core.event_bus import event_bus

class HumanValidationTool(Tool):
    name = "human_validation"
    description = (
        "Obligatorio: Úsalo después de escribir el plan.md para obtener la aprobación del humano. "
        "También úsalo si tienes una duda crítica que impide el desarrollo."
    )
    inputs = {
        "message": {
            "type": "string", 
            "description": "Resumen del plan o pregunta específica para el usuario."
        }
    }
    output_type = "string"

    def forward(self, message: str) -> str:
        try:
            # Publicar evento en lugar de importar directamente
            response = event_bus.publish_sync("human_validation_request", message)
            
            if response:
                return f"El humano respondió: {response}"
            else:
                return "No se recibió respuesta del humano"
                
        except Exception as e:
            return f"Error en la herramienta human_validation: {str(e)}"
