# Agent Script - Binario Build

## 📦 Construcción del Binario

Este documento explica cómo construir y distribuir el binario de Agent Script usando PyInstaller.

## 🛠️ Requisitos

- Python 3.11+
- macOS/Linux/Windows
- ~2GB de espacio libre para el build

## 🚀 Construcción Automática

### Script de Build

Usa el script automatizado para construir el binario:

```bash
./build_binary.sh
```

Este script:
1. ✅ Limpia builds anteriores
2. ✅ Crea entorno virtual limpio
3. ✅ Instala todas las dependencias
4. ✅ Construye el binario con PyInstaller
5. ✅ Copia archivos críticos
6. ✅ Crea paquete de distribución
7. ✅ Realiza tests de validación

### Resultados

El script genera:
- **Binario**: `dist/agent-script/agent-script` (~86MB)
- **Paquete**: `dist/agent-script-{OS}-{ARCH}.tar.gz` (~311MB)
- **Script launcher**: `dist/agent-script/run.sh`

## 📋 Uso del Binario

### Descomprimir y Ejecutar

```bash
# Descomprimir
cd dist
tar -xzf agent-script-Darwin-arm64.tar.gz  # o Linux-x86_64.tar.gz
cd agent-script

# Ejecutar
./agent-script --help

# O usar el launcher
./run.sh --help
```

### Modos Disponibles

```bash
# Interfaz TUI (recomendado)
./agent-script --tui

# Modo terminal (simple)
./agent-script --agent
```

## 🏗️ Construcción Manual

Si prefieres construir manualmente:

### 1. Preparación

```bash
# Limpiar
rm -rf build/ dist/ __pycache__/

# Entorno virtual
python -m venv build-env
source build-env/bin/activate

# Dependencias
pip install pip-tools
pip-compile requirements.in --strip-extras
pip-sync
pip install pyinstaller
```

### 2. Build con PyInstaller

```bash
# Modo directory (recomendado)
pyinstaller --clean \
    --name agent-script \
    --console \
    --windowed \
    --workpath build \
    --distpath dist \
    --add-data ".scriptty:.scriptty" \
    app.py
```

### 3. Post-build

```bash
# Copiar archivos críticos
cp -r build-env/lib/python3.11/site-packages/litellm dist/agent-script/_internal/
cp -r build-env/lib/python3.11/site-packages/smolagents dist/agent-script/_internal/
cp -r .scriptty dist/agent-script/

# Test
cd dist/agent-script && ./agent-script --help
```

## 📁 Estructura del Binario

```
agent-script/
├── agent-script          # Ejecutable principal (86MB)
├── run.sh               # Script de lanzamiento
├── .scriptty/           # Datos de configuración
│   ├── config.json
│   ├── subagentes.json
│   ├── prompt.md
│   ├── subagents/
│   ├── skills/
│   └── skills_db/
└── _internal/           # Dependencias de Python
    ├── Python runtime
    ├── librerías nativas
    ├── litellm/
    ├── smolagents/
    └── ...
```

## 🔧 Configuración

El binario incluye toda la configuración en la carpeta `.scriptty/`:

### Archivos de Configuración

- **config.json**: Configuración principal (modelo, proveedor, tema)
- **subagentes.json**: Configuración de subagentes
- **tools_config.json**: Herramientas habilitadas

### Personalización

Puedes editar estos archivos después de descomprimir:

```bash
# Cambiar modelo
nano .scriptty/config.json

# Agregar skills
cp mi_skill.md .scriptty/skills/
```

## 🌍 Multiplataforma

### macOS

```bash
# Build para macOS (Intel/Apple Silicon)
./build_binary.sh

# Resultado: agent-script-Darwin-arm64.tar.gz (Apple Silicon)
#         agent-script-Darwin-x86_64.tar.gz (Intel)
```

### Linux

```bash
# Build para Linux
./build_binary.sh

# Resultado: agent-script-Linux-x86_64.tar.gz
```

### Windows

```powershell
# Build para Windows
.\build_binary.ps1

# Resultado: agent-script-Windows-x86_64.zip
```

## 🚨 Problemas Comunes

### 1. Error: "No module named 'litellm'"

**Solución**: Copiar módulos manualmente:
```bash
cp -r build-env/lib/python3.11/site-packages/litellm dist/agent-script/_internal/
```

### 2. Error: "FileNotFoundError: .scriptty/..."

**Solución**: Copiar carpeta de datos:
```bash
cp -r .scriptty dist/agent-script/
```

### 3. Error: Permiso denegado

**Solución**: Dar permisos de ejecución:
```bash
chmod +x dist/agent-script/agent-script
chmod +x dist/agent-script/run.sh
```

### 4. Error en macOS: "damaged app"

**Solución**: Permitir ejecución:
```bash
xattr -d com.apple.quarantine dist/agent-script/agent-script
```

## 📊 Tamaños y Rendimiento

### Tamaños de Archivos

| Componente | Tamaño |
|------------|--------|
| Ejecutable principal | ~86MB |
| Paquete completo | ~311MB |
| Dependencias Python | ~200MB |
| Modelos ML | ~100MB |
| Datos de configuración | ~1MB |

### Rendimiento

- **Arranque en frío**: ~3-5 segundos
- **Uso de memoria**: ~200-500MB
- **Espacio en disco**: ~311MB descomprimido

## 🔄 Actualización del Binario

Para actualizar el binario a una nueva versión:

1. **Actualizar código fuente**
2. **Reconstruir binario**:
   ```bash
   ./build_binary.sh
   ```
3. **Distribuir nuevo paquete**

Los datos de usuario en `.scriptty/` se preservan.

## 🚀 Distribución

### Opciones de Distribución

1. **GitHub Releases**: Subir `.tar.gz`
2. **Direct Download**: Servir archivo binario
3. **Package Manager**: Crear paquete para Homebrew/apt

### Notas de Versión

Incluir en cada release:
- Versión del agente
- Cambios importantes
- Requisitos del sistema
- Instrucciones de instalación

## 📝 Licencia

El binario mantiene la misma licencia que el proyecto fuente.

## 🆘 Soporte

Para problemas con el binario:

1. Revisar [BUILD_README.md](BUILD_README.md)
2. Abrir issue en GitHub
3. Incluir sistema operativo y arquitectura
4. Proporcionar logs de error

---

**Construido con ❤️ usando PyInstaller**
