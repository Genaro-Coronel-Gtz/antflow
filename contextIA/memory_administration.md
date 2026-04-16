# Memory Administration Guide

## Overview

Este documento describe la administración y gestión de memoria en el sistema de IA de Scriptty/AntFlow.

## Sistema de Memoria

### Arquitectura

El sistema de memoria mantiene un máximo de **10 mensajes** distribuidos de la siguiente manera:

```
Total: 10 mensajes
├── 1 system prompt (siempre presente, más reciente si hay varios)
└── 9 mensajes de conversación (más nuevos)
```

### Componentes

#### 1. AgentMemory (`utils/memory/memory_agent.py`)

Gestiona el almacenamiento y recuperación de mensajes.

**Métodos clave:**

- `add_message(role, content)`: Añade mensaje y aplica recorte automático
- `get_history()`: Retorna todos los mensajes en memoria
- `get_conversation_history()`: Retorna solo mensajes user/assistant
- `load_from_file()`: Carga mensajes desde archivo markdown
- `save_to_file()`: Guarda mensajes en archivo markdown

#### 2. PromptContext (`utils/memory/prompt_context.py`)

Maneja el registro de prompts para depuración y contexto.

**Métodos clave:**

- `save_prompt_context()`: Guarda prompt completo antes de enviar al modelo
- `cleanup_logs()`: Limpia archivos de log según configuración

## Flujo de Memoria

### 1. Inicialización

```python
# Al iniciar la aplicación
agent_memory = AgentMemory()  # Carga memory.md si existe
```

### 2. Primer Mensaje

```python
if not agent_memory.get_history():
    agent_memory.initialize_with_system_prompt(system_prompt)
```

### 3. Mensajes Subsecuentes

```python
agent_memory.add_message("user", query)
agent_memory.add_message("assistant", response)
```

### 4. Gestión de Límite

Cuando se excede el límite de 10 mensajes:

```python
if len(self.messages) > self.max_messages:
    system_messages = [msg for msg in self.messages if msg["role"] == "system"]
    other_messages = [msg for msg in self.messages if msg["role"] != "system"]
    
    if system_messages:
        self.messages = [system_messages[-1]] + other_messages[-(self.max_messages-1):]
    else:
        self.messages = other_messages[-self.max_messages:]
```

## Construcción del Prompt

### Lógica Actual

```python
# SIEMPRE incluir system prompt + 9 mensajes más nuevos
system_msg = next((msg for msg in full_history if msg["role"] == "system"), None)
conversation_history = agent_memory.get_conversation_history()[-9:]  # 9 mensajes más nuevos

# Construir prompt final
if system_msg:
    full_prompt = f"{system_msg['content']}\n\n{conversation_context}USER QUESTION: {user_query}"
else:
    full_prompt = f"{conversation_context}USER QUESTION: {user_query}"
```

### Comportamiento Adaptativo

- **<10 mensajes:** Usa todos los disponibles
- **=10 mensajes:** Usa exactamente 9 de conversación + 1 system
- **>10 mensajes:** Usa system + últimos 9 de conversación

## Archivos de Memoria

### memory.md

Almacena el historial completo de mensajes en formato markdown.

**Estructura:**
```markdown
# 🧠 Memoria del Agente AI

**Última actualización:** 2026-04-01 16:30:18

**Total de mensajes:** 2

---

## 1. ⚙️ SYSTEM

**Timestamp:** N/A

```
[contenido del system prompt]
```

---

## 2. 👤 USER

**Timestamp:** 2026-04-01T16:30:18.842163

```
[contenido del mensaje del usuario]
```

---
```

### context.md

Registra todos los prompts enviados al modelo para depuración.

**Estructura:**
```markdown
## 🕒 Interacción: 2026-04-01 16:30:18 [PRE-ENVÍO]

### 👤 Prompt Original del Usuario:
> [mensaje del usuario]

### ⚙️ System Prompt:
```
[system prompt utilizado]
```

### 🚀 PROMPT FINAL COMPLETO (enviado al modelo):
================================================================================
```
[prompt completo enviado al modelo]
```
================================================================================
```

## Configuración

### Variables Relevantes

- `start_app_clean_files`: Controla si se borran archivos al iniciar (default: false)
- `max_messages_memory`: Límite de mensajes en memoria (default: 10)

### Configuración en config.json

```json
{
  "start_app_clean_files": false,
  "max_messages_memory": 10
}
```

## Problemas Resueltos

### 1. Pérdida de Mensajes al Reiniciar

**Problema:** `load_from_file()` tenía parseo imperfecto que no cargaba todos los mensajes.

**Solución:** Implementación de parseo robusto por secciones usando `---` como separador.

### 2. System Prompt No se Enviaba en Conversaciones Existentes

**Problema:** System prompt solo se enviaba en `len(full_history) <= 2`.

**Solución:** Modificar lógica para SIEMPRE incluir system prompt + 9 mensajes más nuevos.

### 3. Sobrescritura de Archivo

**Problema:** `save_to_file()` sobrescribía con solo mensajes en memoria.

**Solución:** Mejorar `load_from_file()` para cargar TODOS los mensajes antes de guardar.

## Best Practices

### 1. Mantenimiento de Memoria

- El sistema maneja automáticamente el recorte de mensajes
- No se requiere intervención manual
- Los mensajes más antiguos se eliminan automáticamente

### 2. Depuración

- Revisar `memory.md` para ver estado actual de memoria
- Revisar `context.md` para ver prompts enviados al modelo
- Usar `/memory-stats` para ver estadísticas

### 3. Configuración

- Mantener `start_app_clean_files` en `false` para persistencia
- Ajustar `max_messages_memory` según necesidades de tokens
- Monitorear tamaño de archivos para evitar crecimiento excesivo

## Comandos Útiles

### Limpiar Memoria

```bash
# Desde la aplicación
/clear-memory

# Manualmente
rm .scriptty/memory.md
```

### Ver Estadísticas

```bash
# Desde la aplicación
/memory-stats

# Manualmente
cat .scriptty/memory.md | grep "Total de mensajes"
```

### Ver Contexto

```bash
# Ver prompts enviados
cat .scriptty/context.md

# Ver última interacción
tail -50 .scriptty/context.md
```

## Troubleshooting

### Problema: Memoria se pierde al reiniciar

**Causa:** `start_app_clean_files` está en `true`.

**Solución:**
```json
{
  "start_app_clean_files": false
}
```

### Problema: System prompt duplicado

**Causa:** `load_from_file()` no carga system prompt existente.

**Solución:** Revisar parseo en `load_from_file()`.

### Problema: Mensajes faltantes

**Causa:** Parseo incorrecto en `load_from_file()`.

**Solución:** Verificar formato de `memory.md` y separadores `---`.

## Consideraciones de Rendimiento

### Tokens

- System prompt: ~2000 tokens
- Mensaje de conversación promedio: ~100 tokens
- Total por request: ~2000 + 900 = ~2900 tokens

### Almacenamiento

- `memory.md`: Crecimiento limitado por recorte automático
- `context.md`: Crecimiento continuo, requiere limpieza periódica

### Recomendaciones

- Monitorear uso de tokens según modelo utilizado
- Limpiar `context.md` periódicamente si crece demasiado
- Considerar compresión de mensajes antiguos si es necesario

## Futuras Mejoras

1. **Compresión de Memoria:** Implementar resumen de mensajes antiguos
2. **Memoria Vectorial:** Usar embeddings para búsqueda semántica
3. **Memoria Persistente:** Base de datos para mejor escalabilidad
4. **Memoria Episódica:** Separar conversaciones por temas
5. **Memoria a Largo Plazo:** Almacenar información importante indefinidamente

---

**Última actualización:** 2026-04-01  
**Versión:** 1.0  
**Autor:** Sistema de Administración de Memoria
