# Sistema de Temas para Terminal - Guía Completa

## 📋 Tabla de Contenidos

- [Overview](#overview)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Temas Disponibles](#temas-disponibles)
- [Configuración](#configuración)
- [Uso Básico](#uso-básico)
- [Crear un Nuevo Tema](#crear-un-nuevo-tema)
- [Implementación Detallada](#implementación-detallada)
- [Referencia de Estilos](#referencia-de-estilos)
- [Troubleshooting](#troubleshooting)

---

## 🎨 Overview

El sistema de temas utiliza la librería **Rich** para proporcionar una experiencia visual profesional y personalizable en la terminal. Cada tema define colores y estilos específicos para diferentes componentes de la interfaz.

### Características Principales

- ✅ **Múltiples temas predefinidos**: Dracula, Tokyo Night, Basic
- ✅ **Configuración vía `.env`**: Cambio de tema sin modificar código
- ✅ **Animaciones con colores**: Spinner y barra animada
- ✅ **Componentes Rich**: Panels, tables, borders con estilos
- ✅ **Compatibilidad total**: Código antiguo sigue funcionando
- ✅ **Detección automática**: Adapta colores a capacidades de la terminal

---

## 🏗️ Arquitectura del Sistema

```
utils/
├── themes/                      # 📁 Carpeta de temas
│   ├── __init__.py              # Importador central
│   ├── dracula.py               # 🩸 Tema Dracula
│   ├── tokyo_night.py           # 🌙 Tema Tokyo Night  
│   └── basic.py                 # ⚪ Tema Básico
├── theme_manager.py             # 🎛️ Gestor central de temas
├── animation.py                 # 🎬 Animaciones Rich
└── colors.py                    # 🎨 Compatibilidad con código antiguo
```

### Flujo de Trabajo

1. **Carga**: `theme_manager.py` lee la variable `THEME` del `.env`
2. **Importación**: `themes/__init__.py` importa todos los temas disponibles
3. **Selección**: Se selecciona el tema correspondiente o fallback a `dracula`
4. **Aplicación**: Rich aplica los estilos a todos los componentes

---

## 🎭 Temas Disponibles

### 🩸 Dracula Theme
**Paleta de colores vibrantes y oscuros**

```python
"header": "bright_cyan"      # Títulos principales
"success": "bright_green"     # Mensajes de éxito
"error": "bright_red"         # Mensajes de error
"warning": "bright_yellow"   # Advertencias
"user": "bright_magenta"      # Entrada de usuario
"agent": "bright_green"       # Respuestas del agente
"thinking": "bright_cyan"     # Animación de pensamiento
"border": "bright_magenta"    # Bordes de panels
```

### 🌙 Tokyo Night Theme
**Paleta moderna y suave**

```python
"header": "blue"               # Títulos principales
"success": "green"             # Mensajes de éxito
"error": "red"                 # Mensajes de error
"warning": "yellow"           # Advertencias
"user": "magenta"             # Entrada de usuario
"agent": "green"              # Respuestas del agente
"thinking": "cyan"             # Animación de pensamiento
"border": "magenta"           # Bordes de panels
```

### ⚪ Basic Theme
**Paleta estándar ANSI (máxima compatibilidad)**

```python
"header": "cyan"               # Títulos principales
"success": "green"             # Mensajes de éxito
"error": "red"                 # Mensajes de error
"warning": "yellow"           # Advertencias
"user": "magenta"             # Entrada de usuario
"agent": "green"              # Respuestas del agente
"thinking": "cyan"             # Animación de pensamiento
"border": "magenta"           # Bordes de panels
```

---

## ⚙️ Configuración

### Configurar tema en `.env`

```bash
# .env
THEME=dracula      # Tema por defecto
# THEME=tokyo_night # Tema moderno
# THEME=basic       # Máxima compatibilidad
```

### Cambio dinámico de tema

```python
import os
from utils.themes.theme_manager import theme_manager

# Cambiar tema en tiempo de ejecución
os.environ["THEME"] = "tokyo_night"
theme_manager.reload_theme()
```

---

## 🚀 Uso Básico

### Importaciones estándar

```python
from utils.themes.theme_manager import theme_manager, console
from utils.themes.animation import create_thinking_animation
```

### Componentes principales

```python
# Encabezado con panel
theme_manager.print_header("Título", "Subtítulo opcional")

# Mensajes con colores
theme_manager.print_success_text("✅ Operación exitosa")
theme_manager.print_error_text("❌ Error detectado")
theme_manager.print_warning_text("⚠️ Advertencia")
theme_manager.print_info_text("ℹ️ Información")

# Separadores
theme_manager.print_separator("─", 60)

# Animaciones
with create_thinking_animation("spinner", console=console):
    # Código que se ejecuta mientras la animación corre
    time.sleep(2)
```

### Compatibilidad con código antiguo

```python
from utils.colors import DraculaTheme, success, error

# Sigue funcionando sin cambios
DraculaTheme.print_header("Título", "Subtítulo")
print(success("Texto verde"))
print(error("Texto rojo"))
```

---

## 🛠️ Crear un Nuevo Tema

### Paso 1: Crear archivo del tema

Crea un nuevo archivo en `utils/themes/` con el nombre del tema:

```bash
# Ejemplo para tema "ocean"
touch utils/themes/ocean.py
```

### Paso 2: Definir el tema

```python
# utils/themes/ocean.py
#!/usr/bin/env python3
"""
Tema Ocean para terminal - Paleta de colores marinos
"""

from rich.theme import Theme
from rich.style import Style


ocean_theme = Theme({
    # Estilos principales
    "header": Style(color="bright_blue", bold=True),
    "success": Style(color="bright_green"),
    "error": Style(color="bright_red"),
    "warning": Style(color="bright_yellow"),
    "info": Style(color="bright_blue"),
    "user": Style(color="bright_cyan"),
    "agent": Style(color="bright_blue"),
    "command": Style(color="bright_yellow"),
    "thinking": Style(color="bright_cyan"),
    "border": Style(color="bright_blue"),
    
    # Estilos secundarios
    "subtitle": Style(color="white", dim=True),
    "comment": Style(color="grey50"),
    "foreground": Style(color="white"),
    
    # Estilos para animación
    "animation.shadow": Style(color="grey50"),
    "animation.medium": Style(color="bright_cyan"),
    "animation.solid": Style(color="bright_blue"),
    
    # Estilos para componentes
    "panel.title": Style(color="bright_blue", bold=True),
    "panel.border": Style(color="bright_blue"),
    "separator": Style(color="grey50"),
    
    # Estilos para comandos
    "command.name": Style(color="bright_yellow"),
    "command.desc": Style(color="white"),
})
```

### Paso 3: Registrar el tema

Edita `utils/themes/__init__.py` para importar el nuevo tema:

```python
# utils/themes/__init__.py
# Importar todos los temas disponibles
from .dracula import dracula_theme
from .tokyo_night import tokyo_night_theme
from .basic import basic_theme
from .ocean import ocean_theme  # ← NUEVA LÍNEA

# Diccionario de temas disponibles
THEMES = {
    "dracula": dracula_theme,
    "tokyo_night": tokyo_night_theme,
    "basic": basic_theme,
    "ocean": ocean_theme,  # ← NUEVA LÍNEA
}
```

### Paso 4: Probar el tema

```python
# Test rápido
import os
os.environ["THEME"] = "ocean"
from utils.themes.theme_manager import theme_manager

print(f"Tema actual: {theme_manager.get_theme_name()}")
theme_manager.print_header("Test Ocean Theme", "Paleta de colores marinos")
theme_manager.print_success_text("✅ Ocean theme funcionando!")
```

### Paso 5: Actualizar documentación

Agrega el tema a `.env.example` y a esta documentación:

```bash
# .env.example
# Tema de colores: dracula, tokyo_night, basic, ocean
THEME=dracula
```

---

## 🔧 Implementación Detallada

### Estructura de un tema

Cada tema debe definir estos estilos obligatorios:

```python
{
    # Estilos principales (requeridos)
    "header": Style(...),        # Títulos principales
    "success": Style(...),       # Mensajes de éxito
    "error": Style(...),         # Mensajes de error
    "warning": Style(...),      # Advertencias
    "info": Style(...),          # Información
    "user": Style(...),          # Entrada de usuario
    "agent": Style(...),         # Respuestas del agente
    "command": Style(...),      # Comandos
    "thinking": Style(...),     # Animación de pensamiento
    "border": Style(...),        # Bordes
    
    # Estilos secundarios (recomendados)
    "subtitle": Style(...),      # Subtítulos
    "comment": Style(...),       # Comentarios
    "foreground": Style(...),    # Texto principal
    
    # Estilos de animación (requeridos)
    "animation.shadow": Style(...),   # Sombra de animación
    "animation.medium": Style(...),   # Color medio
    "animation.solid": Style(...),    # Color sólido
    
    # Estilos de componentes (requeridos)
    "panel.title": Style(...),   # Títulos de panels
    "panel.border": Style(...),  # Bordes de panels
    "separator": Style(...),     # Separadores
    
    # Estilos de comandos (requeridos)
    "command.name": Style(...),  # Nombres de comandos
    "command.desc": Style(...),  # Descripciones de comandos
}
```

### Colores Rich disponibles

Rich soporta estos colores principales:

**Colores básicos**: `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`
**Colores brillantes**: `bright_black`, `bright_red`, `bright_green`, `bright_yellow`, `bright_blue`, `bright_magenta`, `bright_cyan`, `bright_white`
**Colores de 256 bits**: `\033[38;5;{numero}m`
**Colores RGB**: `\033[38;2;{r};{g};{b}m`

### Estilos adicionales

```python
Style(
    color="bright_red",      # Color del texto
    bgcolor="black",         # Color de fondo
    bold=True,               # Negrita
    dim=True,                # Atenuado
    italic=True,             # Cursiva
    underline=True,          # Subrayado
    blink=True,              # Parpadeo
    reverse=True,            # Invertir colores
    strike=True,             # Tachado
)
```

---

## 📚 Referencia de Estilos

### Estilos por componente

| Componente | Uso | Ejemplo |
|------------|-----|---------|
| `header` | Títulos principales | `theme_manager.print_header()` |
| `success` | Mensajes positivos | `theme_manager.print_success_text()` |
| `error` | Mensajes de error | `theme_manager.print_error_text()` |
| `warning` | Advertencias | `theme_manager.print_warning_text()` |
| `info` | Información general | `theme_manager.print_info_text()` |
| `user` | Entrada de usuario | `theme_manager.user_input()` |
| `agent` | Respuestas del agente | `theme_manager.print_agent_text()` |
| `command` | Comandos del sistema | `theme_manager.print_command_text()` |
| `thinking` | Animación de pensamiento | `create_thinking_animation()` |
| `border` | Bordes de panels | `Panel(border_style="border")` |

### Estilos de animación

| Estilo | Uso | Caracteres |
|--------|-----|------------|
| `animation.shadow` | Sombra detrás del movimiento | `░` |
| `animation.medium` | Carácter principal del movimiento | `▒` |
| `animation.solid` | Rastro del movimiento | `█` |

---

## 🔍 Troubleshooting

### Problemas Comunes

#### 1. Tema no se carga

**Síntomas**: Se usa el tema por defecto (dracula)
**Causa**: Nombre del tema incorrecto en `.env` o no registrado
**Solución**:
```bash
# Verificar temas disponibles
python -c "from utils.themes import list_available_themes; print(list_available_themes())"

# Asegurar que el tema esté registrado en themes/__init__.py
# Verificar que el nombre en .env coincida exactamente
```

#### 2. Colores no se muestran

**Síntomas**: Texto sin color o con caracteres extraños
**Causa**: Terminal no soporta colores ANSI
**Solución**:
```bash
# Usar tema basic (solo colores ANSI estándar)
THEME=basic

# O verificar capacidades de la terminal
echo $TERM
```

#### 3. Import error

**Síntomas**: `ImportError: cannot import name 'get_theme'`
**Causa**: Estructura de archivos incorrecta
**Solución**:
```bash
# Verificar estructura
ls -la utils/themes/
# Debe existir __init__.py y todos los archivos de temas

# Verificar imports en themes/__init__.py
```

#### 4. Animación no funciona

**Síntomas**: Animación se congela o no muestra colores
**Causa**: Problemas con threading o consola Rich
**Solución**:
```python
# Usar animación spinner (más simple)
create_thinking_animation("spinner", console=console)

# O verificar que la consola se pase correctamente
```

### Debug y Testing

#### Verificar sistema completo

```python
#!/usr/bin/env python3
"""
Debug del sistema de temas
"""

from utils.themes.theme_manager import theme_manager
from utils.themes import list_available_themes

def debug_themes():
    print("🔍 Debug del sistema de temas")
    print(f"Tema actual: {theme_manager.get_theme_name()}")
    print(f"Temas disponibles: {list_available_themes()}")
    
    # Probar estilos
    theme_manager.print_success_text("✅ Success test")
    theme_manager.print_error_text("❌ Error test")
    theme_manager.print_warning_text("⚠️ Warning test")
    
    # Probar animación
    from utils.animation import create_thinking_animation
    with create_thinking_animation("spinner", console=theme_manager.console):
        import time
        time.sleep(1)

if __name__ == "__main__":
    debug_themes()
```

#### Verificar tema específico

```python
# Test individual de un tema
from rich.console import Console
from utils.themes.ocean import ocean_theme

console = Console(theme=ocean_theme)
console.print("✅ Ocean theme test", style="header")
```

---

## 🎯 Mejores Prácticas

### Diseño de Temas

1. **Consistencia**: Usa una paleta coherente de colores
2. **Contraste**: Asegura buena legibilidad en diferentes terminales
3. **Accesibilidad**: Considera daltonismo y preferencias del usuario
4. **Significado**: Usa colores que transmitan el propósito (rojo=error, verde=éxito)

### Nomenclatura

- **Archivos**: `snake_case` (ej: `dark_pro_theme.py`)
- **Variables**: `snake_case` (ej: `dark_pro_theme`)
- **Nombres**: Descriptivos y únicos (ej: `ocean`, `forest`, `sunset`)

### Testing

1. Prueba el tema en diferentes terminales
2. Verifica la legibilidad con fondos claros y oscuros
3. Testea todos los componentes (header, error, warning, etc.)
4. Verifica las animaciones

---

## 📈 Evolución del Sistema

### Historial

- **v1.0**: Sistema ANSI básico con códigos manuales
- **v2.0**: Sistema de registro automático con clases abstractas
- **v3.0**: **Sistema actual con Rich** - Profesional y modular

### Futuras Mejoras

- [ ] Temas dinámicos (cambio sin reiniciar)
- [ ] Soporte para themes personalizados por usuario
- [ ] Integración con temas del sistema operativo
- [ ] Editor visual de temas
- [ ] Exportación/importación de temas

---

## 🤝 Contribución

Para contribuir con un nuevo tema:

1. **Crea el tema** siguiendo la guía [Crear un Nuevo Tema](#crear-un-nuevo-tema)
2. **Testea** en diferentes terminales
3. **Documenta** los colores y su propósito
4. **Envía** el PR con descripción del tema

### Requisitos para temas nuevos

- ✅ Completitud: Todos los estilos requeridos
- ✅ Consistencia: Paleta coherente
- ✅ Legibilidad: Buen contraste
- ✅ Originalidad: Diseño único
- ✅ Documentación: Descripción del propósito

---

**¡Gracias por usar el sistema de temas! 🎨**

Para más ayuda o reportar issues, consulta el repositorio del proyecto.
