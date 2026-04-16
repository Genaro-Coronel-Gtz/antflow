import time
import sys
import os

# --- SPRITES DE ALTA DEFINICIÓN (CP437) ---
# Cuerpo fijo: Cabeza(O), Tórax(█), Cintura(·), Abdomen(Θ)
# Variables: Antenas(°, ⁿ, º) y Patas(╯, ╰, ┘, └)

# --- SECUENCIA DERECHA ---
DER_1 = [
    r"   °   °    ", # Antenas abiertas
    r"  ⁿO=█·ΘΘ>  ", # Cuerpo robusto
    r"  ╯  ╰  ╯   "  # Paso 1: Apoyo trasero y delantero
]

DER_2 = [
    r"    º º     ", # Antenas hacia adelante
    r"  ⁿO=█·ΘΘ>  ", 
    r"   ┘ └ ┘    "  # Paso 2: Empuje (cambio de ángulo)
]

# --- SECUENCIA IZQUIERDA ---
IZQ_1 = [
    r"    °   °   ",
    r"  <ΘΘ·█=Oⁿ  ",
    r"     ╰  ╯ ╰ "
]

IZQ_2 = [
    r"     º º    ",
    r"  <ΘΘ·█=Oⁿ  ",
    r"    └ ┘ └   "
]

def animar_hormiga_pro():
    try:
        col, fil = os.get_terminal_size().columns, os.get_terminal_size().lines
    except OSError:
        col, fil = 80, 24

    pos_x = 0
    derecha = True
    frame_idx = 0
    linea_v = fil // 2 - 2

    # Color Marrón Rojizo (ANSI 124) y ocultar cursor
    sys.stdout.write("\033[?25l\033[2J\033[38;5;124m")

    try:
        while True:
            # Alternamos entre Frame 1 y Frame 2 para el ciclo de caminata
            if derecha:
                sprite = DER_1 if frame_idx % 2 == 0 else DER_2
            else:
                sprite = IZQ_1 if frame_idx % 2 == 0 else IZQ_2
            
            # Dibujado con escape ANSI para evitar "ghosting"
            output = "\033[H" + "\n" * linea_v
            
            for linea in sprite:
                margen = " " * pos_x
                # \033[K limpia el final de la línea actual
                output += f"{margen}{linea}\033[K\n"

            sys.stdout.write(output)
            sys.stdout.flush()

            # Lógica de movimiento
            ancho_h = 12
            if derecha:
                pos_x += 1
                if pos_x + ancho_h >= col - 2:
                    derecha = False
            else:
                pos_x -= 1
                if pos_x <= 2:
                    derecha = True

            frame_idx += 1
            # 0.1s es el "sweet spot" para que el ojo humano vea movimiento y no parpadeo
            time.sleep(0.1)

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\033[0m\n")
        print("Hormiga guardada con éxito.")

if __name__ == "__main__":
    animar_hormiga_pro()