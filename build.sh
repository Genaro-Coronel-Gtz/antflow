#!/bin/bash

# Script de construcción del binario Agent Script
# Uso: ./build_binary.sh

set -e

echo "🔨 Construyendo Agent Script Binary..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "app.py" ] || [ ! -d ".antflow" ]; then
    log_error "Ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

# Limpieza previa
log_info "Limpiando builds anteriores..."
rm -rf build/ dist/ __pycache__/ .pytest_cache/
find . -name "*.pyc" -delete 2>/dev/null || true

# Crear entorno virtual
log_info "Creando entorno virtual..."
if [ ! -d "build-env" ]; then
    python -m venv build-env
fi

source build-env/bin/activate

# Instalar dependencias
log_info "Instalando dependencias..."
pip install pip-tools --quiet
pip-compile requirements.in --strip-extras --quiet
pip-sync --quiet

# Instalar PyInstaller
log_info "Instalando PyInstaller..."
pip install pyinstaller --quiet

# Construir binario usando el spec file
log_info "Construyendo binario con PyInstaller usando antflow.spec..."

pyinstaller --clean antflow.spec

# Copiar archivos críticos que PyInstaller no incluye
log_info "Copiando archivos críticos..."

# Copiar módulos importantes
mkdir -p dist/antflow/_internal/litellm
mkdir -p dist/antflow/_internal/smolagents
mkdir -p dist/antflow/_internal/transformers
mkdir -p dist/antflow/_internal/sentence_transformers
mkdir -p dist/antflow/_internal/tiktoken
mkdir -p dist/antflow/_internal/tiktoken_ext

# Copiar archivos específicos si existen
if [ -f "build-env/lib/python3.11/site-packages/litellm/model_prices_and_context_window_backup.json" ]; then
    cp build-env/lib/python3.11/site-packages/litellm/model_prices_and_context_window_backup.json \
       dist/antflow/_internal/litellm/
fi

# Copiar módulos completos para evitar problemas
cp -r build-env/lib/python3.11/site-packages/litellm/* \
      dist/antflow/_internal/litellm/ 2>/dev/null || true
cp -r build-env/lib/python3.11/site-packages/smolagents/* \
      dist/antflow/_internal/smolagents/ 2>/dev/null || true
cp -r build-env/lib/python3.11/site-packages/tiktoken_ext/* \
      dist/antflow/_internal/tiktoken_ext/ 2>/dev/null || true

# Copiar fuentes de PyFiglet para evitar errores de fuentes faltantes
log_info "Copiando fuentes de PyFiglet..."

# Crear directorio para fuentes
mkdir -p dist/antflow/_internal/pyfiglet/fonts

# Copiar todas las fuentes de PyFiglet
if [ -d "build-env/lib/python3.11/site-packages/pyfiglet/fonts" ]; then
    cp -r build-env/lib/python3.11/site-packages/pyfiglet/fonts/* \
          dist/antflow/_internal/pyfiglet/fonts/
    log_info "Fuentes de PyFiglet copiadas exitosamente"
else
    log_info "No se encontró el directorio de fuentes de PyFiglet"
fi

# Copiar el archivo __init__.py de fonts si existe
if [ -f "build-env/lib/python3.11/site-packages/pyfiglet/fonts/__init__.py" ]; then
    cp build-env/lib/python3.11/site-packages/pyfiglet/fonts/__init__.py \
       dist/antflow/_internal/pyfiglet/fonts/
fi

# Copiar también el módulo pyfiglet principal para asegurar compatibilidad
if [ -d "build-env/lib/python3.11/site-packages/pyfiglet" ]; then
    cp -r build-env/lib/python3.11/site-packages/pyfiglet/* \
          dist/antflow/_internal/pyfiglet/ 2>/dev/null || true
    log_info "Módulo PyFiglet copiado completamente"
fi

# NOTA: No copiar .antflow ya que se genera con --init

# Crear script de lanzamiento
log_info "Creando script de lanzamiento..."
cat > dist/antflow/run.sh << 'EOF'
#!/bin/bash
# Script de lanzamiento para Antflow

# Obtener el directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Ejecutar desde el directorio del binario
cd "$SCRIPT_DIR"
./antflow "$@"
EOF

chmod +x dist/antflow/run.sh

# Crear paquete
log_info "Creando paquete de distribución..."
PKG_NAME="antflow-$(uname -s)-$(uname -m)"
cd dist

# Crear archivo tar.gz
tar -czf "${PKG_NAME}.tar.gz" antflow/
log_success "Paquete creado: ${PKG_NAME}.tar.gz"

# Mostrar información del binario
echo
log_info "Información del binario:"
ls -lh antflow/antflow
echo
log_info "Información del paquete:"
ls -lh "${PKG_NAME}.tar.gz"
echo

# Testing básico
log_info "Realizando test básico..."
cd antflow
if ./antflow --help > /dev/null 2>&1; then
    log_success "✅ Binario funcional - Test de ayuda pasado"
else
    log_error "❌ Binario no funcional - Error en test de ayuda"
    exit 1
fi
cd ..

log_success "🎉 Construcción completada exitosamente!"
echo
log_info "Para usar:"
echo "  cd dist"
echo "  tar -xzf ${PKG_NAME}.tar.gz"
echo "  cd antflow"
echo "  ./antflow --init  # Primera ejecución para generar .antflow"
echo "  ./antflow --help"
echo
log_info "O usar el script de lanzamiento:"
echo "  ./run.sh --help"
