#!/usr/bin/env python3
"""
Logger con colores para la interfaz TUI
"""
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.filters import Condition
from .styles import LOG_STYLES, UI, LOGS

from prompt_toolkit.lexers import Lexer
from prompt_toolkit.lexers import PygmentsLexer
try:
    from pygments.lexers import get_lexer_by_name, guess_lexer
    from pygments.util import ClassNotFound
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

class LogLexer(Lexer):
    """Lexer que reconoce prefijos de logs y también formato de comandos usando estilos centralizados."""
    def __init__(self):
        # Ya no necesitamos prefix_style, usamos LOG_STYLES directamente
        pass
    
    def _get_code_lexer(self, code_text, language_hint=None):
        """Obtiene un lexer para el código usando Pygments"""
        if not PYGMENTS_AVAILABLE:
            return None
            
        try:
            # Si hay un hint de lenguaje, intentarlo primero
            if language_hint:
                try:
                    return get_lexer_by_name(language_hint)
                except ClassNotFound:
                    pass
            
            # Intentar adivinar el lexer basado en el contenido
            try:
                return guess_lexer(code_text)
            except ClassNotFound:
                # Por defecto usar Python para código que parece ser Python
                if any(keyword in code_text for keyword in ['def ', 'import ', 'from ', 'class ', 'print(', '#']):
                    return get_lexer_by_name('python')
                # Para otros casos, intentar con texto plano
                return get_lexer_by_name('text')
        except Exception:
            return None

    def lex_document(self, document):
        def get_line(lineno):
            line = document.lines[lineno]
            
            # 1. Detectar marcas especiales de estilo __STYLE__tipo__mensaje
            if line.startswith("__STYLE__"):
                parts = line.split("__", 3)  # Separar en: ['', 'STYLE', 'tipo', 'mensaje']
                if len(parts) >= 4:
                    msg_type = parts[2]
                    msg_content = parts[3]
                    
                    # Si es código, aplicar resaltado de sintaxis
                    if msg_type == "code":
                        return self._lex_code_line(msg_content)
                    
                    style_value = LOG_STYLES.get(msg_type, LOG_STYLES[LOGS.default.value])
                    # Devolver el valor del color directamente
                    return [(style_value, msg_content)]
            
            # 2. Detectar prefijos de tipo [tipo] - aplicar estilo a toda la línea (legacy)
            for msg_type, style_value in LOG_STYLES.items():
                prefix = f"[{msg_type}]"
                if line.startswith(prefix):
                    # Aplicar el estilo a toda la línea completa
                    return [(style_value, line)]
            
            # 3. Detectar comandos (/comando) - aplicar estilo a toda la línea
            command_style = LOG_STYLES.get("foreground", LOG_STYLES[LOGS.default.value])
            return [(command_style, line)]
            
            # 4. Detectar títulos (Headers) - líneas en mayúsculas o que contengan '==='
            if line.isupper() and len(line) > 3:
                header_style = LOG_STYLES.get("header", LOG_STYLES[LOGS.default.value])
                return [(header_style, line)]
            
            # 5. Líneas por defecto - aplicar estilo a toda la línea
            default_style = LOG_STYLES[LOGS.default.value]
            return [(default_style, line)]
            
        return get_line
    
    def _lex_code_line(self, code_line):
        """Aplica resaltado de sintaxis a una línea de código"""
        if not PYGMENTS_AVAILABLE:
            # Si Pygments no está disponible, usar estilo de código por defecto
            code_style = LOG_STYLES.get("thinking", LOG_STYLES[LOGS.default.value])
            return [(code_style, code_line)]
        
        try:
            # Intentar usar Pygments para resaltar la línea
            lexer = self._get_code_lexer(code_line)
            if lexer:
                # Convertir el lexer de Pygments al formato de prompt_toolkit
                pygments_lexer = PygmentsLexer(lexer)
                
                # Crear un documento temporal con solo esta línea
                from prompt_toolkit.document import Document
                temp_doc = Document(code_line)
                
                # Obtener los tokens formateados
                tokens = list(pygments_lexer.lex_document(temp_doc)(0))
                return tokens if tokens else [(LOG_STYLES.get("thinking", "#ffffff"), code_line)]
            else:
                # Si no se puede determinar el lexer, usar estilo por defecto
                code_style = LOG_STYLES.get("thinking", LOG_STYLES[LOGS.default.value])
                return [(code_style, code_line)]
        except Exception:
            # En caso de error, usar estilo por defecto
            code_style = LOG_STYLES.get("thinking", LOG_STYLES[LOGS.default.value])
            return [(code_style, code_line)]

class ColoredLogger:
    def __init__(self):
        self._escribiendo = False
        
        # Ahora sí, Condition convierte la lambda en un Filter válido
        self.buffer = Buffer(
            name="logs_buffer",
            read_only=True
        )
        
        self.app = None
        self.lexer = LogLexer()

    def set_app(self, app):
        self.app = app

    def append(self, msg: str, msg_type = LOGS.default):
        if isinstance(msg_type, (UI, LOGS)):
            msg_type_str = msg_type.value
        else:
            msg_type_str = str(msg_type)

        marked_msg = f"__STYLE__{msg_type_str}__{msg}"

        self._escribiendo = True
        try:
            current_text = self.buffer.text
            new_text = current_text + marked_msg + "\n"

            from prompt_toolkit.document import Document
            self.buffer.set_document(
                Document(text=new_text, cursor_position=len(new_text)),
                bypass_readonly=True,
            )
        finally:
            self._escribiendo = False

        if self.app:
            self.app.invalidate()

    def clear(self):
        self._escribiendo = True
        try:
            from prompt_toolkit.document import Document
            self.buffer.set_document(
                Document(text="", cursor_position=0),
                bypass_readonly=True,
            )
        finally:
            self._escribiendo = False
        if self.app:
            self.app.invalidate()