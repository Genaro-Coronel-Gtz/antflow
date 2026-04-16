from smolagents import Tool, DuckDuckGoSearchTool
from .utils import write_log

class SearchTool(Tool):
    name = "search_tool"
    description = "Busca información en internet sobre temas actuales, documentación o dudas técnicas."
    inputs = {
        "query": {
            "type": "string", 
            "description": "La consulta de búsqueda para realizar en internet.",
            "nullable": True  # <--- ESTO ES LO QUE FALTABA
        }
    }
    output_type = "string"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.internal_search = DuckDuckGoSearchTool()

    def forward(self, query: str = None):
        if not query: 
            return "❌ Error: Consulta de búsqueda vacía."
        
        try:
            results = self.internal_search(query)
            write_log(self.name, query, "Búsqueda web completada con éxito")
            return f"--- RESULTADOS DE BÚSQUEDA PARA: {query} ---\n{results}"
        
        except Exception as e:
            error_msg = f"❌ Error en la búsqueda: {str(e)}"
            write_log(self.name, query, error_msg)
            return error_msg