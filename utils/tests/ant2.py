import time
import sys
import os

# --- Sprites Miniatura (Estilo Bloque Compacto) ---
# Cada línea representa la parte superior (▀) y la inferior (▄) del cuerpo.

# Frame A: Patas abiertas
MINI_HORMIGA_A = [
    r"  █ █  ",  # Antenas
    r" ▀█▄█▀ ",  # Cabeza y Tórax
    r" ▀███▀ ",  # Abdomen y Patas
    r"  ▀ ▀  "   # Patas traseras
]

# Frame B: Patas cerradas (movimiento)
MINI_HORMIGA_B = [
    r"  █ █  ",  # Antenas
    r" ▄█▀█▄ ",  # Cabeza y Tórax
    r" ▄███▄ ",  # Abdomen y Patas
    r"  █ █  "   # Patas traseras
]

def animar_mini():
    # Detectar dimensiones de la terminal
    try:
        columnas = os.get_terminal_size().columns
        filas = os.get_terminal_size().lines
    except OSError:
        columnas, filas = 80, 24

    pos_x = 0
    derecha = True
    frame_count = 0
    linea_v = filas // 2 - 2

    # Ocultar cursor y limpiar pantalla
    sys.stdout.write("\033[?25l\033[2J")

    try:
        while True:
            # Alternar frames para el caminar
            sprite = MINI_HORMIGA_A if frame_count % 2 == 0 else MINI_HORMIGA_B
            
            # Usar \033[H para volver al inicio sin parpadear
            output = "\033[H" + "\n" * linea_v
            
            for linea in sprite:
                # Si va a la izquierda, invertimos el sprite
                dibujo = linea if derecha else linea[::-1]
                
                margen = " " * pos_x
                # \033[K borra rastro a la derecha
                output += f"{margen}{dibujo}\033[K\n"

            sys.stdout.write(output)
            sys.stdout.flush()

            # Lógica de movimiento
            ancho_h = len(sprite[0])
            if derecha:
                pos_x += 1
                if pos_x + ancho_h >= columnas - 1:
                    derecha = False
            else:
                pos_x -= 1
                if pos_x <= 0:
                    derecha = True

            frame_count += 1
            time.sleep(0.06) # Un poco más rápida porque es pequeña

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\033[0m\n")
        print("Mini hormiga guardada.")

if __name__ == "__main__":
    animar_mini()