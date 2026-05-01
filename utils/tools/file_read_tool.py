import os
import json
from pathlib import Path
from smolagents import Tool
from .utils import write_log, safe_path

class FileReadTool(Tool):
    name = "file_reader"
    description = "Lee archivos de texto con soporte para caracteres especiales, JSON, YAML. Limita archivos grandes automáticamente."
    inputs = {
        "path": {"type": "string", "description": "Ruta del archivo", "nullable": True},
        "max_size_mb": {"type": "number", "description": "Tamaño máximo en MB (default: 10)", "nullable": True}
    }
    output_type = "string"

    def forward(self, path: str = None, max_size_mb: float = 10):
        if not path:
            return "❌ Error: Ruta vacía."
        
        target = safe_path(path)
        max_size_bytes = int(max_size_mb * 1024 * 1024)
        
        # Validaciones
        if not os.path.exists(target):
            return f"❌ Error: El archivo '{path}' no existe."
        
        if not os.path.isfile(target):
            return f"❌ Error: '{path}' no es un archivo."
        
        file_size = os.path.getsize(target)
        
        # Protección contra archivos muy grandes
        if file_size > max_size_bytes:
            return f"❌ Error: Archivo demasiado grande ({file_size / 1024 / 1024:.2f} MB). Máximo permitido: {max_size_mb} MB"
        
        try:
            # Detectar encoding automáticamente
            content, encoding_used = self._read_with_encoding(target)
            
            # Estadísticas
            lines = content.count('\n') + 1
            chars = len(content)
            
            # Validación de formato
            validation_msg = self._validate_format(path, content)
            
            write_log(self.name, path, f"Lectura exitosa ({file_size} bytes)")
            
            # Si el archivo es muy grande, mostrar preview
            if chars > 50000:
                preview = content[:25000] + "\n\n[... CONTENIDO TRUNCADO ...]\n\n" + content[-25000:]
                truncated_msg = f"\n⚠️ Archivo grande: mostrando primeros y últimos 25,000 caracteres"
            else:
                preview = content
                truncated_msg = ""
            
            return f"""--- CONTENIDO DE {path} ---
[Tamaño: {self._format_size(file_size)} | Líneas: {lines} | Caracteres: {chars} | Encoding: {encoding_used}{validation_msg}]{truncated_msg}

{preview}"""
            
        except PermissionError:
            return f"❌ Error: Sin permisos para leer '{path}'"
        except Exception as e:
            return f"❌ Error al leer '{path}': {type(e).__name__}: {str(e)}"
    
    def _read_with_encoding(self, filepath):
        """Intenta leer con diferentes encodings"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                return content, encoding
            except UnicodeDecodeError:
                continue
        
        # Último recurso: binario con reemplazo
        with open(filepath, 'rb') as f:
            raw = f.read()
        content = raw.decode('utf-8', errors='replace')
        return content, 'utf-8 (con reemplazo)'
    
    def _validate_format(self, path, content):
        """Valida JSON y YAML"""
        if not content.strip():
            return ""
        
        # Validar JSON
        if path.endswith('.json'):
            try:
                json.loads(content)
                return " | ✅ JSON válido"
            except json.JSONDecodeError as e:
                return f" | ⚠️ JSON inválido (L{e.lineno}:{e.colno})"
        
        # Validar YAML
        if path.endswith(('.yml', '.yaml')):
            try:
                import yaml
                yaml.safe_load(content)
                return " | ✅ YAML válido"
            except ImportError:
                return ""
            except yaml.YAMLError as e:
                error_str = str(e).split('\n')[0][:60]
                return f" | ⚠️ YAML inválido: {error_str}"
        
        return ""
    
    def _format_size(self, size_bytes):
        """Formatea el tamaño del archivo"""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / 1024 / 1024:.2f} MB"