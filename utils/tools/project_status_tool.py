import os
import datetime
import json
import re
from smolagents import Tool

class ProjectStatusTool(Tool):
    name = "project_status_tool"
    description = "Lee o actualiza el archivo de estado del proyecto (.md). Formato simple: action='update' con content corto y sin markdown complejo."
    inputs = {
        "action": {"type": "string", "description": " 'read' para ver el progreso o 'update' para añadir un hito."},
        "content": {"type": "string", "description": "Descripción del avance en texto plano (ej: 'Plan completado'). Sin markdown complejo.", "nullable": True}
    }
    output_type = "string"

    def __init__(self, state_file=".antflow/project_status.md"):
        super().__init__()
        self.state_file = state_file

    def _sanitize_content(self, content):
        """Sanitiza el contenido para evitar problemas de parsing"""
        if not content:
            return None
            
        # Eliminar markdown complejo que puede causar problemas
        content = re.sub(r'[#*`_\[\]]+', '', content)
        # Reemplazar comillas que pueden romper JSON
        content = content.replace('"', "'")
        # Limitar longitud para evitar problemas
        content = content[:200] + "..." if len(content) > 200 else content
        return content.strip()

    def forward(self, action: str, content: str = None):
        if action == "read":
            if not os.path.exists(self.state_file):
                return "# Estado del Proyecto\nNo hay registros aún."
            with open(self.state_file, "r", encoding="utf-8") as f:
                return f.read()
        
        elif action == "update":
            # Sanitizar el contenido para evitar problemas de JSON
            content = self._sanitize_content(content)
            if not content: 
                return "❌ Error: Contenido vacío después de sanitización."
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            # Usamos formato simple sin markdown complejo
            entry = f"\n\n--- \n> **{timestamp}**: {content}"
            
            with open(self.state_file, "a", encoding="utf-8") as f:
                f.write(entry)
            return f"✅ Estado actualizado: {content}"