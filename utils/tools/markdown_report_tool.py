import os
from smolagents import Tool
from mdutils.mdutils import MdUtils
from .utils import write_log, safe_path

class MarkdownReportTool(Tool):
    name = "markdown_report"
    description = "Genera reportes técnicos en Markdown con Índice de Contenidos (TOC) automático. Ideal para arquitecturas y planes."
    inputs = {
        "filename": {"type": "string", "description": "Nombre del archivo (sin .md)."},
        "title": {"type": "string", "description": "Título principal (H1) del reporte."},
        "with_toc": {"type": "boolean", "description": "Si es True, genera un índice de contenidos al inicio.", "nullable": True},
        "structure": {
            "type": "object", 
            "description": "Lista de diccionarios: [{'action': 'header', 'level': 2, 'text': 'Sección'}, {'action': 'text', 'text': 'Detalle'}]"
        }
    }
    output_type = "string"

    def forward(self, filename: str, title: str, structure: list, with_toc: bool = True):
        path = safe_path(f"{filename}.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # 1. Inicializar el archivo
        md_file = MdUtils(file_name=path, title=title)

        try:
            # 2. Procesar la estructura decidida por la IA
            for item in structure:
                action = item.get("action")
                
                if action == "header":
                    md_file.new_header(level=item.get("level", 2), title=item.get("text"))
                elif action == "text":
                    md_file.new_paragraph(item.get("text"))
                elif action == "list":
                    md_file.new_list(item.get("items"), marked_with=item.get("marker", "-"))
                elif action == "table":
                    header = item.get("header", [])
                    data = item.get("data", [])
                    cols = len(header) if header else 3  # Default 3 columnas si no hay header
                    
                    # Calcular filas correctamente: longitud de data / cols
                    if data:
                        rows = len(data) // cols
                        if len(data) % cols != 0:
                            rows += 1  # Añadir fila extra si hay remainder
                    else:
                        rows = 1  # Mínimo 1 fila si no hay datos
                    
                    # Construir texto para la tabla: header + data
                    table_text = header + data
                    md_file.new_table(columns=cols, rows=rows, text=table_text)
                elif action == "code":
                    md_file.insert_code(item.get("code"), language=item.get("lang", "python"))

            # 3. Insertar el Índice de Contenidos (TOC) al principio si se solicita
            # MdUtils lo inserta inteligentemente después del título
            if with_toc:
                try:
                    md_file.create_toc()  # Método correcto en mdutils
                except AttributeError:
                    # Si create_toc no existe, usar create_index como fallback
                    try:
                        md_file.create_index(depth=2)
                    except AttributeError:
                        # Si no existe ninguno, continuar sin TOC
                        pass 

            # 4. Guardar físicamente
            md_file.create_md_file()
            
            write_log(self.name, path, f"Markdown report generated")
            return f" Report '{filename}.md' with Index generated in {path}"
            
        except Exception as e:
            return f" Error in builder markdown report: {str(e)}"