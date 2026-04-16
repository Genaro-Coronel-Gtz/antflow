# Sistema de Skills con VectorDB y Reranking FlashRank

## 🧠 Descripción

Sistema avanzado de gestión de habilidades usando búsqueda vectorial optimizada con LanceDB, embeddings de Ollama y reranking con FlashRank para máxima precisión contextual.

## 🚀 Características

- **VectorDB Optimizada**: LanceDB con índice IVF-PQ y métrica coseno
- **Embeddings**: Ollama API con modelo `nomic-embed-text`
- **Reranking Inteligente**: FlashRank para reordenar resultados por relevancia
- **Búsqueda Híbrida**: Filtrado durante consulta + umbral de distancia adaptable
- **Interfaz Textual**: Panel de skills con comandos `/enable-skill`, `/disable-skill`, `/list-skills`
- **Integración Total**: Contexto enriquecido inyectado automáticamente en el agente
- **Logs Detallados**: Estadísticas de búsqueda y reranking en `.scriptty/context.md`

## 📦 Instalación

```bash
pip install -r requirements.txt
# Incluir flashrank para reranking
pip install flashrank
```

## 🔧 Configuración

1. **Asegurar Ollama corriendo**:
```bash
ollama serve
```

2. **Instalar modelo de embeddings**:
```bash
ollama pull nomic-embed-text
```

3. **Verificar FlashRank** (opcional, fallback automático):
```bash
python -c "from flashrank import Ranker; print('✅ FlashRank disponible')"
```

## 🎮 Uso

### Comandos en Modo Terminal

- **`/skill`**: Agregar nueva skill al sistema
- **`/list-skills`**: Listar todas las skills y su estado (enabled/disabled)
- **`/enable-skill <nombre>`**: Habilitar una skill específica
- **`/disable-skill <nombre>`**: Deshabilitar una skill específica
- **`/back`**: Volver al menú principal
- **`/exit`**: Salir del programa

### Ejemplos de Comandos

```bash
# Listar skills disponibles
> /list-skills
📋 Skills disponibles:
  fast_api             ✅ enabled
  rails                ❌ disabled
  scrapling            ❌ disabled

# Habilitar una skill
> /enable-skill rails
✅ Skill 'rails' habilitada correctamente

# Deshabilitar una skill
> /disable-skill rails
✅ Skill 'rails' deshabilitada correctamente
```

### Flujo de Búsqueda Optimizado

Cuando se envía un mensaje, el sistema:

1. **Genera Embedding**: Convierte la query a vector
2. **Búsqueda Vectorial**: Busca en skills activas con filtro `WHERE`
3. **Filtro por Distancia**: Aplica umbral adaptable (0.6-0.8)
4. **Reranking con FlashRank**: Reordena resultados por relevancia semántica
5. **Selección Top-K**: Elige los 3 mejores resultados
6. **Inyección de Contexto**: Añade contexto enriquecido al prompt

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
📦 Sistema de Skills
├── 🔍 Búsqueda Vectorial Optimizada
│   ├── LanceDB con índice vectorial estándar
│   ├── Filtrado durante consulta (WHERE)
│   └── Umbral de distancia adaptable
├── 🎯 Reranking FlashRank
│   ├── Reordenación semántica
│   ├── Top-K selection (3 resultados)
│   └── Fallback automático si no está disponible
└── 📊 Estadísticas y Logs
    ├── Búsqueda stats
    ├── Reranking metrics
    └── Context tracking
```

### Flujo Detallado

```python
1. search_skills()
   ├─ Genera embedding: query → vector
   ├─ Filtra skills activas: WHERE skill_id IN (...)
   ├─ Búsqueda vectorial: table.search(vector).where(filter).limit(20)
   ├─ Aplica umbral: results[_distance] < threshold
   └─ Retorna 10-15 candidatos relevantes

2. get_skills_context()
   ├─ Recibe candidatos del paso 1
   ├─ Invoca reranker: VectorialReranker.rerank_results()
   ├─ FlashRank reordena por relevancia semántica
   └─ Selecciona top-3 resultados

3. Contexto Final
   ├─ Los 3 más relevantes
   ├─ Con scores de FlashRank
   └─ Inyectados en el prompt del agente
```

## 📁 Estructura de Archivos

```
Agent/
├── utils/
│   ├── skill_manager.py      # Gestor de VectorDB optimizado
│   ├── reranker_db_results.py  # Sistema de reranking FlashRank
│   ├── search_in_skills.py  # Búsqueda y contexto
│   └── prompt_context.py    # Logs detallados
├── app.py                   # Modo terminal con comandos
├── agent.py                 # Agente con silenciamiento de logs
├── tui.py                   # Interfaz textual
├── requirements.txt          # Dependencias (incluye flashrank)
├── .scriptty/skills_db/               # Base de datos LanceDB (se crea en el directorio actual)
└── .scriptty/context.md              # Logs de contexto y estadísticas
```

## 🎯 Reranking con FlashRank

### ¿Qué es FlashRank?

FlashRank es un reranker de alta velocidad que reordena resultados de búsqueda vectorial basándose en relevancia semántica real con la query del usuario.

### Configuración

```python
# En utils/reranker_db_results.py
class VectorialReranker:
    def __init__(self, top_k: int = 3):
        self.top_k = top_k
        self.ranker = None
        self._init_ranker()  # Inicializa FlashRank con fallback
```

### Proceso de Reranking

```python
# 1. Búsqueda vectorial inicial (15-20 resultados)
results = skill_manager.search_skills(query, active_skills)

# 2. Reranking con FlashRank
reranker = VectorialReranker(top_k=3)
reranked_results, stats = reranker.rerank_results(query, results)

# 3. Resultados finales
# - Los 3 más relevantes según FlashRank
# - Con scores de relevancia
# - Metadata detallada
```

### Estadísticas de Reranking

El sistema genera estadísticas detalladas:

```python
stats = {
    'total_original': 15,        # Resultados iniciales
    'total_reranked': 3,         # Después de FlashRank
    'top_k': 3,                  # Límite configurado
    'flashrank_available': True,  # Si FlashRank está activo
    'average_score': 0.847,      # Score promedio de los resultados
    'skills_found': ['fast_api'] # Skills que contribuyeron
}
```

## 🔧 Configuración Avanzada

### Ajustar Umbral de Distancia

```python
# En utils/skill_manager.py
def get_distance_threshold(self, query: str) -> float:
    query_length = len(query.strip())
    if query_length < 10:
        return 0.6  # Queries cortas: más flexibles
    elif query_length < 30:
        return 0.7  # Queries medias: balance
    else:
        return 0.8  # Queries largas: más estrictas
```

### Modificar Top-K del Reranker

```python
# En utils/reranker_db_results.py
reranker = VectorialReranker(top_k=5)  # Más resultados finales
```

### Cambiar Modelo de Embeddings

```python
# En utils/skill_manager.py
self.embedding_model = "nomic-embed-text"  # Modelo actual
# Alternativas: "all-MiniLM-L6-v2", "text-embedding-ada-002"
```

### Optimización de Índice Vectorial

```python
# Índice vectorial estándar con métrica coseno (automático)
self.table.create_index(
    vector_column_name="vector",
    index_type="vector",      # Tipo estándar soportado por LanceDB
    metric="cosine"         # Mejor para similitud semántica
)
```

## 📊 Métricas y Monitoreo

### Logs de Contexto

En `.scriptty/context.md` se registra:

```markdown
## 📊 Estadísticas de Búsqueda y Reranking
- **Total Original**: 15 resultados iniciales
- **Total Rerankeados**: 3 resultados finales
- **FlashRank Disponible**: ✅ Sí
- **Score Promedio**: 0.847
- **Skills Encontradas**: fast_api

## � Resultados Rerankeados
1. [Score: 0.891] fast_api - Crear API REST con FastAPI...
2. [Score: 0.834] fast_api - Configuración de rutas...
3. [Score: 0.716] fast_api - Manejo de errores...
```

### Estadísticas en Tiempo Real

```bash
# Verificar estado del sistema
python -c "
from utils.skills.skill_manager import SkillManager
from utils.skills.reranker_db_results import VectorialReranker

manager = SkillManager()
reranker = VectorialReranker()

print('📊 Skills disponibles:', len(manager.get_available_skills()))
print('🧠 Skills activas:', len(manager.get_enabled_skills()))
print('🎯 FlashRank disponible:', reranker.ranker is not None)
"
```

## 🎯 Ejemplos de Uso

### Skill Completa (ej: `fast_api.md`)

```markdown
# FastAPI - Guía Completa

## Creación de APIs REST

### Estructura Básica
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

### Manejo de Errores
```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id < 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
```
```

### Consulta del Usuario

```
Usuario: "¿Cómo creo una API REST con FastAPI y manejo errores?"

Proceso:
1. Embedding de la query
2. Búsqueda en skills activas (fast_api)
3. Filtrado por umbral de distancia
4. Reranking con FlashRank
5. Contexto final inyectado
```

## 🐛 Troubleshooting

### Error: "FlashRank no disponible"

```bash
# Instalar FlashRank
pip install flashrank

# Verificar instalación
python -c "from flashrank import Ranker; print('✅ FlashRank OK')"
```

### Error: "No se encontraron modelos de Ollama"

```bash
ollama list
# Si no hay modelos:
ollama pull nomic-embed-text
```

### Búsqueda devuelve pocos resultados

```python
# Ajustar umbral de distancia (más flexible)
def get_distance_threshold(self, query: str) -> float:
    return 0.5  # Más permissivo

# O aumentar límite de búsqueda
results = table.search(query_vector).where(filter).limit(30)
```

### Error: "El índice vectorial no funciona"

```bash
# Recrear índice (automático al iniciar)
# El sistema detectará y creará el índice optimizado
python -c "
from utils.skills.skill_manager import SkillManager
manager = SkillManager()
manager._init_db()  # Recreará el índice si es necesario
"
```

## 🚀 Mejores Prácticas

### Para Skills de Alta Calidad

1. **Estructura clara**: Headers ## y ### para organización
2. **Chunks balanceados**: 300-800 caracteres por sección
3. **Ejemplos prácticos**: Código funcional y explicado
4. **Contexto rico**: Incluir teoría y práctica

### Para Máxima Precisión

1. **Habilitar skills relevantes**: Solo las necesarias para la consulta
2. **Queries específicas**: Más detalle = mejores resultados
3. **Verificar logs**: Revisar `.scriptty/context.md` para ajustar
4. **Monitorear scores**: Buscar scores > 0.7 en reranking

## � Rendimiento y Optimización

### Métricas Esperadas

- **Búsqueda inicial**: 15-20 resultados en <100ms
- **Reranking**: Top-3 en <50ms (con FlashRank)
- **Contexto total**: <200ms incluyendo embeddings
- **Precisión**: 85%+ de relevancia con FlashRank

### Optimizaciones Implementadas

- ✅ **Índice vectorial estándar**: Búsquedas vectoriales más rápidas
- ✅ **Filtrado WHERE**: Menos datos procesados
- ✅ **Umbral adaptable**: Calidad sobre cantidad
- ✅ **Caching embeddings**: Evita recálculo
- ✅ **FlashRank**: Reranking ultra-rápido

## 🔄 Actualización y Mantenimiento

### Actualizar Skills Existentes

```bash
# Agregar nueva versión
> /skill
Nombre: fast_api_v2
Archivo: fast_api_v2.md

# Habilitar nueva versión
> /enable-skill fast_api_v2

# Deshabilitar antigua
> /disable-skill fast_api
```

### Mantenimiento de BD

```bash
# La BD se crea automáticamente en el directorio actual: ./.scriptty/skills_db/
# No requiere mantenimiento manual
# Los índices se crean/recuperan automáticamente
# Para reiniciar desde cero: rm -rf .scriptty/skills_db/
```

## 🤝 Contribuciones

1. Fork del proyecto
2. Crear feature branch
3. Añadir mejoras con tests
4. Pull request con documentación

## 📄 Licencia

MIT License

---

**🎯 Resultado**: Un sistema de skills de alta precisión con búsqueda vectorial optimizada y reranking inteligente para contexto máximo en las respuestas del agente.
