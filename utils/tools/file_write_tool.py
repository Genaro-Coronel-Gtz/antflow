import os
import json
from pathlib import Path
from smolagents import Tool
from .utils import write_log, safe_path

class FileWriteTool(Tool):
    name = "file_writer"
    description = "Escribe archivos DENTRO del proyecto. Crea carpetas automáticamente. Soporta JSON, YAML, y archivos de texto con caracteres especiales."
    inputs = {
        "path": {"type": "string", "description": "Ruta relativa al archivo", "nullable": True}, 
        "content": {"type": "string", "description": "Contenido del archivo", "nullable": True}
    }
    output_type = "string"

    def forward(self, path: str = None, content: str = None):
        if not path:
            return "❌ Error: Ruta vacía."
        
        target = safe_path(path)
        
        try:
            # Preparar el contenido sin modificarlo
            safe_content = content if content is not None else ""
            
            # Crear directorios padre si no existen
            target_path = Path(target)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir el archivo con UTF-8 y manejo explícito de newlines
            # newline='' preserva los saltos de línea originales (\n, \r\n, etc.)
            with open(target_path, "w", encoding="utf-8", newline='') as f:
                f.write(safe_content)
            
            # Validación opcional para JSON
            if target.endswith('.json') and safe_content.strip():
                try:
                    json.loads(safe_content)
                except json.JSONDecodeError as je:
                    return f"⚠️ Archivo guardado pero JSON inválido en línea {je.lineno}: {je.msg}"
            
            # Validación opcional para YAML (si tienes PyYAML instalado)
            if target.endswith(('.yml', '.yaml')) and safe_content.strip():
                try:
                    import yaml
                    yaml.safe_load(safe_content)
                except ImportError:
                    pass  # PyYAML no instalado, skip validación
                except yaml.YAMLError as ye:
                    return f"⚠️ Archivo guardado pero YAML inválido: {ye}"
            
            write_log(self.name, path, f"Guardado en {target}")
            
            # Información adicional útil
            file_size = target_path.stat().st_size
            return f"✅ Archivo guardado en: {path} ({file_size} bytes)"
            
        except PermissionError:
            return f"❌ Error: Sin permisos para escribir en {path}"
        except UnicodeEncodeError as e:
            return f"❌ Error de codificación: El contenido tiene caracteres que no se pueden codificar: {e}"
        except OSError as e:
            return f"❌ Error del sistema al escribir {path}: {str(e)}"
        except Exception as e:
            return f"❌ Error inesperado al escribir {path}: {type(e).__name__}: {str(e)}"