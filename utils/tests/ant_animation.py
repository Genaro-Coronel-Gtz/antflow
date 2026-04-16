import time
import sys
import os

# --- Definición de Micro-Hormigas Texturizadas ---
# Usamos caracteres variados para diferenciar cabeza, tórax, abdomen y patas.

# --- OPCIÓN 1: La "Obrera Clásica" (Sombreado con #) ---
HORMIGA_OBRERA = [
    r" \^/ ", # Antenas curvadas
    r" (###)"  # Cabeza '(' con abdomen texturizado '###'
]
ANIM_OBRERA = [
    r" \!/ ", # Antenas vibrando
    r" -###-" # Patas laterales sugeridas '-'
]

# --- OPCIÓN 2: La "Guerrera" (Más grande, con ganchos) ---
HORMIGA_GUERRERA = [
    r" ~o~ ", # Antenas con puntas (o)
    r"{[^^^]}" # Tórax robusto '[', abdomen curvado '^^^'
]
ANIM_GUERRERA = [
    r" ~+~ ", # Antenas vibrando (+)
    r" <[^^^]>" # Patas laterales/ganchos sugeridos '<', '>'
]

# --- OPCIÓN 3: La "Minimalista con Ojos" (Muy compacta) ---
HORMIGA_OJOS = [
    r"  ..  ", # Antenas muy finas (..)
    r" (oo)<"  # Cabeza con ojos (oo), abdomen con punta '<'
]
ANIM_OJOS = [
    r"  ::  ", # Antenas vibrando (::)
    r"=(oo)-" # Patas sugeridas '=', '-'
]

# Elegimos una opción predeterminada
MICRO_A = HORMIGA_OBRERA
MICRO_B = ANIM_OBRERA

def animar_micro_textura():
    # Detectar dimensiones de la terminal
    try:
        col = os.get_terminal_size().columns
        fil = os.get_terminal_size().lines
    except OSError:
        col, fil = 80, 24

    pos_x = 0
    derecha = True
    frame_count = 0
    # Centrado vertical (pero un poco más arriba para que se vea bien)
    linea_v = fil // 2 - 1

    # Ocultar cursor y limpiar pantalla
    sys.stdout.write("\033[?25l\033[2J")

    try:
        while True:
            # Alternar frames para el efecto de movimiento
            sprite = MICRO_A if frame_count % 2 == 0 else MICRO_B
            
            # \033[H vuelve al inicio para evitar parpadeo
            output = "\033[H" + "\n" * linea_v
            
            for l in sprite:
                # Si va a la izquierda, invertimos los caracteres de dirección
                if not derecha:
                    # Inversión manual de caracteres de dirección
                    d = l[::-1].replace('(', '<<').replace(')', '>>').replace('<<', ')').replace('>>', '(')
                    d = d.replace('<', '>><<').replace('>', '<<>>').replace('>><<', '>').replace('<<>>', '<')
                else:
                    d = l
                
                margen = " " * pos_x
                # \033[K borra rastro anterior a la derecha
                output += f"{margen}{d}\033[K\n"

            sys.stdout.write(output)
            sys.stdout.flush()

            # Lógica de rebote y dirección
            ancho_h = len(sprite[0])
            if derecha:
                pos_x += 1
                if pos_x + ancho_h >= col - 1:
                    derecha = False
            else:
                pos_x -= 1
                if pos_x <= 0:
                    derecha = True

            frame_count += 1
            time.sleep(0.05) # Las micro-hormigas son rápidas

    except KeyboardInterrupt:
        # Restaurar terminal
        sys.stdout.write("\033[?25h\033[0m\n")
        print("\nMicro-hormigas texturizadas detenidas.")

if __name__ == "__main__":
    animar_micro_textura()