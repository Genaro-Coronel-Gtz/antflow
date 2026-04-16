#!/usr/bin/env python3
"""
Animación de hormigas múltiples - izquierda a derecha con colores AntFlow
"""

import os
import sys
import time

# Color del tema AntFlow
ANTFLOW_CYAN = "\033[38;2;111;232;224m"  # #6FE8E0
RESET = "\033[0m"

# Fotogramas simples (solo caracteres, sin colores)

Ant1_chars = "'▀/▀/▀["
Ant2_chars = "'▀|▀|▀[";
Ant3_chars = "'▀\\▀\\▀[";

Ant1_chars_r = "]▀\\▀\\▀'"
Ant2_chars_r = "]▀|▀|▀'";
Ant3_chars_r = "]▀/▀/▀'";

# Ant1_chars = "'o/o/O{"
# Ant2_chars = "'o|o|O{";
# Ant3_chars = "'o\\o\\O{";

# # Fotogramas para hormigas yendo de derecha a izquierda (invertidos)
# Ant1_chars_r = "}O\\o\\o'"
# Ant2_chars_r = "O|o|o'";
#Ant3_chars_r = "{O/o/o'";

class Hormiga:
    def __init__(self, start_delay=0):
        self.start_delay = start_delay
        self.frame = 0
        self.active = False
        self.direction = "left_to_right"  # Comienza yendo de izquierda a derecha
        
    def update(self, current_frame, col):
        # Activar hormiga después del delay
        if current_frame >= self.start_delay:
            self.active = True
            
        if self.active:
            # Seleccionar fotograma según el ciclo y dirección
            if self.direction == "left_to_right":
                if self.frame % 3 == 0:
                    sprite = Ant1_chars
                elif self.frame % 3 == 1:
                    sprite = Ant2_chars
                else:
                    sprite = Ant3_chars
                    
                # Calcular posición (movimiento de izquierda a derecha)
                current_pos_x = self.frame % (col + 10)
                
                # Si pasa el borde derecho, cambiar dirección
                if current_pos_x > col - 5:
                    self.direction = "right_to_left"
                    self.frame = 0  # Reiniciar frame para sincronizar
                    
            else:  # right_to_left
                if self.frame % 3 == 0:
                    sprite = Ant1_chars_r
                elif self.frame % 3 == 1:
                    sprite = Ant2_chars_r
                else:
                    sprite = Ant3_chars_r
                    
                # Calcular posición (movimiento de derecha a izquierda)
                current_pos_x = (col - 10 - self.frame) % (col + 10)
                
                # Si pasa el borde izquierdo, cambiar dirección
                if current_pos_x < 0:
                    self.direction = "left_to_right"
                    self.frame = 0  # Reiniciar frame para sincronizar
            
            self.frame += 1
            return sprite, current_pos_x
        return "", None

def animar_hormiga_simple():
    try:
        col = os.get_terminal_size().columns
        fil = os.get_terminal_size().lines
    except OSError:
        col, fil = 80, 24

    # Crear una sola hormiga
    hormiga = Hormiga(start_delay=0)
    current_frame = 0
    
    # Ocultar cursor y limpiar pantalla
    sys.stdout.write("\033[?25l\033[2J")

    try:
        while True:
            # Construir salida con la hormiga en una línea
            output = "\033[H"  # Mover cursor al inicio
            output += "\033[" + str(fil // 2) + "B"  # Mover a línea central
            
            # Crear línea vacía
            line = [' '] * col
            
            # Colocar la hormiga en su posición
            sprite, pos_x = hormiga.update(current_frame, col)
            if sprite and pos_x is not None:
                for i, char in enumerate(sprite):
                    if pos_x + i < col:
                        line[pos_x + i] = char
            
            # Construir línea con colores
            colored_line = ""
            for char in line:
                if char != ' ':
                    colored_line += f"{ANTFLOW_CYAN}{char}{RESET}"
                else:
                    colored_line += " "
            
            output += colored_line + "\033[K"
            
            # Limpiar resto de líneas
            for _ in range(fil - (fil // 2) - 1):
                output += "\033[K\033[1B"  # Limpiar línea y mover hacia abajo

            sys.stdout.write(output)
            sys.stdout.flush()

            current_frame += 1
            time.sleep(0.15)

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\033[0m\n")

if __name__ == "__main__":
    animar_hormiga_simple()
