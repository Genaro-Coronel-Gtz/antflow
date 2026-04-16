#!/usr/bin/env python3
"""
Herramienta para formatear código con sintaxis resaltada usando Rich Console
"""
import sys
from smolagents import Tool
from .utils import write_log
from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.formatters import TerminalFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

class CodeFormatterTool(Tool):
    name = "code_formatter"
    description = "Formatea código con sintaxis resaltada y colores para mejor visualización en terminal usando Rich Console"
    inputs = {
        "code": {"type": "string", "description": "El código a formatear"},
        "language": {"type": "string", "description": "Lenguaje del código (python, javascript, bash, etc.). Si no se especifica, intentará adivinarlo.", "nullable": True}
    }
    output_type = "string"

    def forward(self, code: str, language: str = "auto"):
        if not code or not code.strip():
            return "Error: No se proporcionó código para formatear."
        
        console = Console()
        
        if not PYGMENTS_AVAILABLE:
            # Si pygments no está disponible, mostrar con Rich Console sintaxis highlighting
            try:
                syntax = Syntax(code, lexer=language or 'auto', theme="default")
                console.print(f"Código ({language or 'auto-detectado'}):")
                console.print(syntax)
            except Exception as e:
                write_log(self.name, f"code: {code[:50]}...", f"Error con Rich Console: {str(e)}")
                return f"```{language if language != 'auto' else ''}\n{code}\n```"
        
        try:
            # Usar pygments para formateo tradicional
            # Determinar el lexer
            if language and language != "auto":
                try:
                    lexer = get_lexer_by_name(language.lower())
                except:
                    lexer = guess_lexer(code)
            else:
                lexer = guess_lexer(code)
            
            # Formatear para terminal con pygments
            formatter = TerminalFormatter()
            formatted_code = highlight(code, lexer, formatter)
            
            # Agregar encabezado con Rich Console
            header = Text(f"Code [{lexer.name}]", style="bold cyan")
            console.print(header)
            
            # Mostrar código formateado con pygments
            console.print(Text(formatted_code))
            
            write_log(self.name, f"language: {lexer.name}, code_length: {len(code)} \n{formatted_code}", "code_formatter_tool")
            
            # Devolver el código formateado en lugar de mensaje genérico
            return formatted_code
            
        except Exception as e:
            # Si falla, mostrar código original con mensaje de error
            console.print("Error formateando código:")
            console.print(Text(code, style="dim red"))
            write_log(self.name, f"code: {code[:50]}...", f"Error formateando: {str(e)}")
            return f"Error al formatear: {str(e)}"
