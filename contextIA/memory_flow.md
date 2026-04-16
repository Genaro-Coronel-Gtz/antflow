# Sistema de Memoria del Agente AI

## Overview

Este documento describe cómo funciona el sistema de memoria de Scriptty, su arquitectura y comportamiento actual.

## Arquitectura del Sistema

### Componentes Principales

1. **AgentMemory** (`utils/memory/memory_agent.py`)
   - Clase principal que gestiona toda la memoria
   - Maneja operaciones de guardar/cargar
   - Implementa truncamiento automático

2. **Archivo de Memoria** (`.antflow/memory.md`)
   - Almacenamiento persistente en formato markdown
   - Formato legible para humanos
   - Contiene todo el historial de conversación

3. **Configuración** (`.antflow/config.json`)
   - `max_messages_memory`: Límite de mensajes a mantener
   - Valor por defecto: 50 mensajes

## Flujo de Datos

### Guardado de Mensajes

```
Mensaje del Usuario -> add_message() -> 
  [Validación] -> 
  [Truncamiento si es necesario] -> 
  save_to_file() -> 
  Archivo Markdown
```

### Carga de Memoria

```
Inicio de Aplicación -> AgentMemory() -> 
  load_from_file() -> 
  Parseo Markdown -> 
  [Aplicar truncamiento si es necesario] -> 
  Memoria en RAM
```

## Comportamiento del Truncamiento

### Lógica de Truncamiento

Cuando el número de mensajes excede `max_messages_memory`:

1. **Siempre mantiene el system prompt**
2. **Mantiene los mensajes más recientes**
3. **Elimina los mensajes más antiguos**

### Implementación Actual

```python
if len(self.messages) > self.max_messages:
    # Mantener siempre el mensaje system si existe
    system_messages = [msg for msg in self.messages if msg["role"] == "system"]
    other_messages = [msg for msg in self.messages if msg["role"] != "system"]
    
    # Mantener el system message y los max_messages-1 mensajes más recientes
    if system_messages:
        recent_others = other_messages[-(self.max_messages-1):]
        self.messages = [system_messages[0]] + recent_others
    else:
        self.messages = other_messages[-self.max_messages:]
```

### Ejemplo con max_messages = 3

**Estado inicial:**
```
['system', 'user', 'assistant'] (3 mensajes)
```

**Añadir nuevo mensaje:**
```
['system', 'user', 'assistant', 'user'] (4 mensajes)
```

**Después del truncamiento:**
```
['system', 'assistant', 'user'] (3 mensajes)
```

El system prompt siempre se mantiene, y se conservan los 2 mensajes más recientes.

## Formato del Archivo

### Estructura Markdown

```markdown
# Memoria del Agente AI

**Última actualización:** 2026-04-10 09:24:00

**Total de mensajes:** 3

---

## 1. emoji SYSTEM

**Timestamp:** 2026-04-10T09:24:00.000000

```
Contenido del system prompt
```

---

## 2. emoji USER

**Timestamp:** 2026-04-10T09:24:01.000000

```
Mensaje del usuario
```

---

## 3. emoji ASSISTANT

**Timestamp:** 2026-04-10T09:24:02.000000

```
Respuesta del asistente
```

---
```

### Emojis Utilizados

- **System**: `emoji` (configurado en el código)
- **User**: `emoji` (configurado en el código)
- **Assistant**: `emoji` (configurado en el código)

## Métodos Principales

### AgentMemory.add_message(role, content)
- **role**: 'system', 'user', o 'assistant'
- **content**: Texto del mensaje
- **función**: Añade mensaje y aplica truncamiento si es necesario

### AgentMemory.get_history()
- **retorno**: Lista completa de mensajes
- **uso**: Para el agente AI

### AgentMemory.get_conversation_history()
- **retorno**: Solo mensajes user/assistant
- **uso**: Para mostrar conversación al usuario

### AgentMemory.clear()
- **función**: Limpia toda la memoria
- **acción**: Elimina mensajes y guarda archivo vacío

## Configuración Recomendada

### Para Diferentes Casos de Uso

1. **Pruebas/Desarrollo**: 3-10 mensajes
   - Permite ver truncamiento rápidamente
   - Ideal para debugging

2. **Uso Regular**: 20-50 mensajes
   - Buen balance entre contexto y rendimiento
   - Valor por defecto recomendado

3. **Proyectos Complejos**: 100+ mensajes
   - Máximo contexto para proyectos largos
   - Requiere más memoria RAM

## Comandos Disponibles

### /memory-stats
Muestra estadísticas actuales de la memoria:
- Total de mensajes
- Mensajes por tipo
- Límite configurado
- Ubicación del archivo

### /clear-session
Limpia toda la memoria y archivos relacionados:
- Elimina memoria del agente
- Limpia archivos de logs
- Reinicia sesión completamente

## Persistencia de Sesión

### Comportamiento

1. **Durante la sesión**: Los mensajes se guardan inmediatamente
2. **Al salir**: La memoria persiste en el archivo
3. **Al volver a entrar**: Se carga automáticamente el historial completo
4. **Truncamiento**: Se aplica al cargar si excede el límite

### Garantías

- **System prompt siempre se mantiene**
- **Mensajes más recientes se preservan**
- **No hay pérdida de datos entre sesiones**

## Tests

### Ubicación
`utils/tests/memory/test_memory_simple.py`

### Escenarios Probados

1. **Operaciones básicas**
   - Añadir mensajes
   - Guardar en archivo
   - Cargar desde archivo

2. **Persistencia de sesión**
   - Crear instancia, añadir mensajes
   - Destruir instancia
   - Crear nueva instancia
   - Verificar carga correcta

3. **Truncamiento**
   - Forzar límite de mensajes
   - Verificar system prompt se mantiene
   - Comprobar orden correcto

### Ejecución de Tests

```bash
cd /Users/genaro_coronel/Lab/Scriptty
source venv/bin/activate
python utils/tests/memory/test_memory_simple.py
```

## Mejores Prácticas

### Para Usuarios

1. **Configurar límite adecuado** según el tipo de proyecto
2. **Usar /memory-stats** para monitorear el estado
3. **Usar /clear-session** para empezar fresh cuando sea necesario
4. **Monitorear tamaño del archivo** `.antflow/memory.md`

### Para Desarrolladores

1. **Siempre usar métodos de AgentMemory**
2. **No manipular directamente self.messages**
3. **Validar formato de mensajes antes de añadir**
4. **Probar truncamiento con diferentes límites**

## Características Clave

### Robustez

- **Manejo de errores**: Recuperación automática si falla guardado
- **Validación**: Verificación de integridad de datos
- **Persistencia**: Garantizada entre sesiones

### Rendimiento

- **Truncamiento eficiente**: Solo cuando es necesario
- **Guardado inmediato**: Sin pérdida de datos
- **Carga optimizada**: Parseo robusto del markdown

### Flexibilidad

- **Configurable**: Límite ajustable via config.json
- **Extensible**: Fácil de añadir nuevos tipos de mensajes
- **Compatible**: Funciona con diferentes flujos de trabajo

## Resumen

El sistema de memoria de Scriptty es robusto, persistente y eficiente. Mantiene automáticamente el contexto relevante, preserva siempre el system prompt, y garantiza la persistencia entre sesiones. Está diseñado para ser transparente al usuario mientras proporciona herramientas útiles para desarrolladores.
