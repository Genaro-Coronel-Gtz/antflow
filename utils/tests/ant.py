import time
import sys
import os

# --- Sprites de Perfil Lateral (Vistas Derecha e Izquierda) ---
# Hechos en una sola línea para maximizar la pequeñez y claridad.
# Utilizamos caracteres de bloque fino y puntuación para los detalles.

# Hacia la DERECHA -> (Cabeza al frente)
DERECHA_A = [
    r" ,--.==##=- ", # Antenas, Cabeza (==), Tórax (##), Patas/Abdomen (=)
    r"  /\\  ||   "  # Patas delanteras/medias (Posición 1)
]

DERECHA_B = [
    r" ,--.==##=- ", # Antenas, Cuerpo igual
    r"  ||  /\\   "  # Patas medias/traseras (Posición 2 - Movimiento)
]

# Hacia la IZQUIERDA <- (Espejo de la derecha)
IZQUIERDA_A = [
    r" -=##==.--, ", # Abdomen/Patas (=), Tórax (##), Cabeza (==), Antenas
    r"   ||  /\\  "  # Patas delanteras/medias (Posición 1)
]

IZQUIERDA_B = [
    r" -=##==.--, ", # Abdomen/Patas (=), Cuerpo igual
    r"  /\\  ||   "  # Patas medias/traseras (Posición 2 - Movimiento)
]

def animar_perfil():
    # Dimensiones de la terminal
    try:
        col = os.get_terminal_size().columns
        fil = os.get_terminal_size().lines
    except OSError:
        col, fil = 80, 24

    pos_x = 0
    derecha = True
    frame_count = 0
    
    # Centrado vertical (un poco más arriba)
    linea_v = fil // 2 - 1

    # Ocultar cursor y limpiar pantalla
    sys.stdout.write("\033[?25l\033[2J")

    try:
        while True:
            # Seleccionar set de sprites según dirección y frame
            if derecha:
                sprite = DERECHA_A if frame_count % 2 == 0 else DERECHA_B
            else:
                sprite = IZQUIERDA_A if frame_count % 2 == 0 else IZQUIERDA_B
            
            # \033[H vuelve al inicio para evitar parpadeo
            output = "\033[H" + "\n" * linea_v
            
            for linea in sprite:
                margen = " " * pos_x
                # \033[K borra rastro anterior a la derecha
                output += f"{margen}{linea}\033[K\n"

            sys.stdout.write(output)
            sys.stdout.flush()

            # Lógica de movimiento
            ancho_h = len(sprite[0])
            if derecha:
                pos_x += 1
                if pos_x + ancho_h >= col - 1:
                    derecha = False
                    frame_count = 0 # Reiniciar ciclo de patas al girar
            else:
                pos_x -= 1
                if pos_x <= 0:
                    derecha = True
                    frame_count = 0 # Reiniciar ciclo de patas al girar

            frame_count += 1
            time.sleep(0.06) 

    except KeyboardInterrupt:
        # Restaurar terminal
        sys.stdout.write("\033[?25h\033[0m\n")
        print("\nHormigas de perfil lateral detenidas.")

if __name__ == "__main__":
    animar_perfil()