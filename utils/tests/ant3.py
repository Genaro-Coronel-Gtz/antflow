import time
import sys
import os

# --- Sprites de Hormiga con Abdomen Realista ---
# Estructura: Antenas finas, cabeza con ojos, tórax con "joroba" y abdomen ovoide segmentado.

# Hacia la DERECHA ->
DER_1 = [
    r"     \  /     ", # Antenas
    r"     (00)     ", # Cabeza con ojos
    r" ◄───[⬢]──⬮⬮⬯", # Mandíbulas(◄), Tórax([⬢]), Abdomen segmentado(⬮⬮⬯)
    r"    ╯ ╰  ╯    "  # Patas traseras y medias
]

DER_2 = [
    r"     /  \     ", # Antenas vibrando
    r"     (oo)     ", # Cabeza
    r" ◄───[⬢]──⬮⬮⬯", # Cuerpo igual
    r"    / \  /    "  # Movimiento de patas
]

# Hacia la IZQUIERDA <-
IZQ_1 = [
    r"     \  /     ",
    r"     (00)     ",
    r"⬯⬮⬮──[⬢]───► ",
    r"    ╰  ╯ ╰    "
]

IZQ_2 = [
    r"     /  \     ",
    r"     (oo)     ",
    r"⬯⬮⬮──[⬢]───► ",
    r"    \  / \    "
]

def animar_hormiga_realista():
    try:
        col = os.get_terminal_size().columns
        fil = os.get_terminal_size().lines
    except OSError:
        col, fil = 80, 24

    pos_x = 0
    derecha = True
    frame = 0
    linea_v = fil // 2 - 2

    # Color Marrón/Negro y ocultar cursor
    sys.stdout.write("\033[?25l\033[2J\033[38;5;94m")

    try:
        while True:
            sprite = (DER_1 if frame % 2 == 0 else DER_2) if derecha else (IZQ_1 if frame % 2 == 0 else IZQ_2)
            
            output = "\033[H" + "\n" * linea_v
            for l in sprite:
                margen = " " * pos_x
                output += f"{margen}{l}\033[K\n"

            sys.stdout.write(output)
            sys.stdout.flush()

            ancho_h = 16
            if derecha:
                pos_x += 1
                if pos_x + ancho_h >= col - 1:
                    derecha = False
            else:
                pos_x -= 1
                if pos_x <= 0:
                    derecha = True

            frame += 1
            time.sleep(0.08)

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\033[0m\n")
        print("Hormiga realista guardada.")

if __name__ == "__main__":
    animar_hormiga_realista()