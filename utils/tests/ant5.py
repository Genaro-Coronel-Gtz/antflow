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
    def __init__(self, start_delay=0, position_index=0, direction="left_to_right"):
        self.start_delay = start_delay
        self.position_index = position_index
        self.base_offset = position_index * 30  # Espacio entre hormigas
        self.direction = direction
        self.frame = 0
        self.active = False
        
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
                    
                # Calcular posición (movimiento + offset base)
                current_pos_x = (self.frame + self.base_offset) % (col + 20)  # Ciclo más largo
                
                # Si pasa el borde derecho, simular que viene por la izquierda
                if current_pos_x > col - 5:
                    current_pos_x = current_pos_x - col - 20
                    
            else:  # right_to_left
                if self.frame % 3 == 0:
                    sprite = Ant1_chars_r
                elif self.frame % 3 == 1:
                    sprite = Ant2_chars_r
                else:
                    sprite = Ant3_chars_r
                    
                # Calcular posición (movimiento inverso + offset base)
                current_pos_x = (col - 10 - (self.frame + self.base_offset)) % (col + 20)
                
                # Si pasa el borde izquierdo, simular que viene por la derecha
                if current_pos_x < 0:
                    current_pos_x = current_pos_x + col + 20
            
            self.frame += 1
            return sprite, current_pos_x
        return "", None

def animar_hormigas_multiples(num_hormigas=4):
    try:
        col = os.get_terminal_size().columns
        fil = os.get_terminal_size().lines
    except OSError:
        col, fil = 80, 24

    # Crear hormigas para ambas direcciones
    hormigas = []
    delay_between = 5  # frames de delay entre hormigas
    
    # Hormigas yendo de izquierda a derecha (línea superior)
    for i in range(num_hormigas):
        delay = i * delay_between
        position_index = i
        hormigas.append(Hormiga(delay, position_index, "left_to_right"))
    
    # Hormigas yendo de derecha a izquierda (línea inferior)
    for i in range(num_hormigas):
        delay = i * delay_between
        position_index = i
        hormigas.append(Hormiga(delay, position_index, "right_to_left"))
    
    current_frame = 0
    
    # Ocultar cursor y limpiar pantalla
    sys.stdout.write("\033[?25l\033[2J")

    try:
        while True:
            # Primera línea: hormigas yendo de izquierda a derecha
            output = "\033[H"  # Mover cursor al inicio
            output += "\033[" + str(fil // 2 - 1) + "B"  # Mover a línea superior
            
            # Crear línea vacía
            line1 = [' '] * col
            
            # Colocar hormigas izquierda a derecha
            for i in range(num_hormigas):
                sprite, pos_x = hormigas[i].update(current_frame, col)
                if sprite and pos_x is not None:
                    for j, char in enumerate(sprite):
                        if pos_x + j < col:
                            line1[pos_x + j] = char
            
            # Construir línea con colores
            colored_line1 = ""
            for char in line1:
                if char != ' ':
                    colored_line1 += f"{ANTFLOW_CYAN}{char}{RESET}"
                else:
                    colored_line1 += " "
            
            output += colored_line1 + "\033[K"
            
            # Segunda línea: hormigas yendo de derecha a izquierda (2 líneas abajo)
            output += "\033[2B"  # Mover 2 líneas abajo
            
            # Crear línea vacía
            line2 = [' '] * col
            
            # Colocar hormigas derecha a izquierda
            for i in range(num_hormigas):
                sprite, pos_x = hormigas[num_hormigas + i].update(current_frame, col)
                if sprite and pos_x is not None:
                    for j, char in enumerate(sprite):
                        if pos_x + j < col:
                            line2[pos_x + j] = char
            
            # Construir línea con colores
            colored_line2 = ""
            for char in line2:
                if char != ' ':
                    colored_line2 += f"{ANTFLOW_CYAN}{char}{RESET}"
                else:
                    colored_line2 += " "
            
            output += colored_line2 + "\033[K"
            
            # Limpiar resto de líneas
            for _ in range(fil - (fil // 2 + 1)):
                output += "\033[K\033[1B"  # Limpiar línea y mover hacia abajo

            sys.stdout.write(output)
            sys.stdout.flush()

            current_frame += 1
            time.sleep(0.15)

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\033[0m\n")

if __name__ == "__main__":
    # Configurable: cambiar este número para más o menos hormigas
    num_hormigas = 5
    animar_hormigas_multiples(num_hormigas)
