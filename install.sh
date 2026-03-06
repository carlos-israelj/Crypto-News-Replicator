#!/bin/bash

# Script de instalación para Crypto News Replicator

echo "======================================"
echo "  Crypto News Replicator - Instalación"
echo "======================================"
echo ""

# Verificar Python
echo "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python $PYTHON_VERSION encontrado ✓"
echo ""

# Crear entorno virtual
echo "Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate || . venv/Scripts/activate

# Instalar dependencias
echo "Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Instalar Playwright browsers
echo ""
echo "Instalando navegadores de Playwright..."
playwright install chromium

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo ""
    echo "Creando archivo .env desde plantilla..."
    cp .env.example .env
    echo "⚠ IMPORTANTE: Edita el archivo .env y agrega tus API keys"
fi

echo ""
echo "======================================"
echo "  Instalación completada ✓"
echo "======================================"
echo ""
echo "Próximos pasos:"
echo "1. Edita el archivo .env y agrega tus API keys"
echo "2. Activa el entorno virtual:"
echo "   source venv/bin/activate  (Linux/Mac)"
echo "   venv\\Scripts\\activate     (Windows)"
echo "3. Ejecuta el script principal:"
echo "   python main.py"
echo ""
