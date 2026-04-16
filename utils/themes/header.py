from utils.tools.utils.common import safe_path
from .common import clear_console
from rich.table import Table
from utils.themes.theme_manager import theme_manager, console
from utils.core.translator import t

# Versión de la aplicación
VERSION = "v1.0.0-beta"

def banner():
    return """
           .           .
          oOO.        dOO '
            ,k.      ol
             .xlxokld;                    .:;;
            :xo.    :kd.           ':. ..;':'c
            d: .dxO: .x'          '' ,.
     .oOc.  d: .kOO: .x'   .dd;   .'
        x,  :kd'   .:dd.   d;    .,
        dl.    ;xlOl.     ;k;  .::,           ,::'
          ,ol cd' .ld ,kc .  .,',.:..  ..  '  :.';
      ,oloc.  c:   .d. .: olll        ,. ,.
 ...'l:    ': cl   ;o.';     .d;'..    .'
               .o.c;    :            ..
           ,lc..o'l, :o;.    .'     ..
        ;o:.  'lc';l:.  ' cl.   . ';.
        c.  :;  .:.  'l.   c'    .' '.
        c.  :::x' .:c:o.   c'        '
       .l.  :,  .;.  .c.   c,          ..'.'
      ,,    :c';. .,c;l.    .;.          ','
             .;:' .,:'
                .,.

"""

def crate_info_head():
    # Comandos principales simplificados
    main_commands = {
        "/commands": t("commands_help"),
        "/exit": t("exit_help")
    }
    
    commands = ""
    for cmd, desc in main_commands.items():
         commands += f"  [foreground]{cmd:<15}[/foreground] - [agent]{desc}[/agent]\n"
    
    

    table = Table(show_header=False, show_edge=False, box=None, padding=0, expand=True)
    table.add_column("commands", justify="left", style="white", width=60)
    table.add_column("project", justify="right", style="white", ratio=1)
    
    # Una sola fila con dos columnas
    table.add_row(
        theme_manager.info_text(" ") + "\n" + commands,
        theme_manager.info_text(t("project_path")) + "\n" + theme_manager.command_text(f"  {safe_path('.')}")
    )
        
    theme_manager.print_separator_line()
    console.print(table)
    theme_manager.print_separator_line()


def create_banner():
    clear_console()
    from pyfiglet import figlet_format
    # Texto en figlet (todo minúsculas)
    banner = figlet_format("AntFlow", font="cyberlarge")
    
    # Aplicar colores degradados (línea por línea)
    colored_lines = []
    colors = ["#6FE8E0", "#4FC3D9", "#2E8BEF", "#1E5FB8"]
    
    for i, line in enumerate(banner.split('\n')):
        if line.strip():
            color = colors[min(i, len(colors)-1)]
            colored_lines.append(f"[{color}]{line}[/{color}]")
    
    console.print('\n')
    console.print('\n'.join(colored_lines), justify="center")
    console.print('\n')
    theme_manager.print_legend("Open Source Agentic Framework")
    theme_manager.print_version(f"{VERSION}")


def create_antflow_banner():
    clear_console()
    from pyfiglet import figlet_format
    
    # Obtener ASCII art manteniendo espacios exactos (sin strip)
    ascii_art_raw = banner()
    ascii_art_lines = ascii_art_raw.split('\n')
    
    # Eliminar solo líneas vacías al inicio y final, pero mantener espacios internos
    while ascii_art_lines and not ascii_art_lines[0].strip():
        ascii_art_lines.pop(0)
    while ascii_art_lines and not ascii_art_lines[-1].strip():
        ascii_art_lines.pop()
    
    figlet_text = figlet_format("AntFlow", font="cyberlarge").strip().split('\n')
    
    # Calcular dimensiones
    ascii_height = len(ascii_art_lines)
    figlet_height = len(figlet_text)
    
    # Calcular espacio para centrar verticalmente el figlet
    total_height = ascii_height  # Usar la altura del ASCII art como referencia
    
    # Espacio arriba para centrar el figlet (solo necesitamos padding arriba)
    if figlet_height < ascii_height:
        padding_top = (ascii_height - figlet_height) // 2
    else:
        padding_top = 0
    
    # Crear tabla sin bordes para centrado automático
    table = Table(show_header=False, show_edge=False, box=None, padding=0)
    table.add_column("ascii", justify="left", style="white", width=60)  # left para mantener formato ASCII
    table.add_column("spacing", justify="center", width=4)
    table.add_column("figlet", justify="center", style="white", width=60)
    
    # Colores para el degradado
    colors = ["#6FE8E0", "#4FC3D9", "#2E8BEF", "#1E5FB8"]
    
    # Agregar filas con centrado vertical
    for i in range(total_height):
        # ASCII art line con colores degradados proporcionales
        if i < len(ascii_art_lines):
            ascii_line = ascii_art_lines[i]
            if ascii_line.strip():
                # Calcular color proporcional a la posición en el ASCII art
                ascii_color_index = int((i / ascii_height) * len(colors))
                color = colors[min(ascii_color_index, len(colors)-1)]
                ascii_line = f"[{color}]{ascii_line}[/{color}]"
        else:
            ascii_line = ""
        
        # Espacio entre columnas
        spacing = ""
        
        # Figlet line con padding y colores proporcionales
        if i < padding_top:
            figlet_line = ""
        elif i < padding_top + figlet_height:
            figlet_index = i - padding_top
            original_line = figlet_text[figlet_index]
            if original_line.strip():
                # Calcular color proporcional a la posición en el figlet
                figlet_color_index = int((figlet_index / figlet_height) * len(colors))
                color = colors[min(figlet_color_index, len(colors)-1)]
                original_line = f"{' '}{original_line}"
                figlet_line = f"[{color}]{original_line}[/{color}]"
            else:
                figlet_line = original_line
        else:
            figlet_line = ""
        
        table.add_row(ascii_line, spacing, figlet_line)

    
    # Crear console y centrar la tabla
    #console = Console()
    
    # Centrar la tabla en la terminal
    console.print(table, justify="center")
    theme_manager.print_legend("Open Source Agentic Framework")
    theme_manager.print_version(f"{VERSION}")
    
    # Retornar string vacío para compatibilidad (ya se imprimió)
    return ""
