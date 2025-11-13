#!/bin/bash
# Script para iniciar la aplicación web del Sistema de Priorización

echo "🎯 Sistema de Priorización de Proyectos Sociales"
echo "=================================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo "❌ Error: No se encuentra app.py"
    echo "Por favor ejecuta este script desde la carpeta del proyecto:"
    echo "cd /Users/juanpablotovar/Desktop/claude_code/sistema-priorizacion-proyectos"
    exit 1
fi

echo "✅ Verificando dependencias..."

# Verificar que streamlit está instalado
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit no está instalado"
    echo "Instalando streamlit..."
    pip3 install streamlit plotly pandas openpyxl reportlab
fi

echo "✅ Todo listo!"
echo ""
echo "🚀 Iniciando aplicación..."
echo "La aplicación se abrirá en tu navegador en unos segundos..."
echo ""
echo "📱 URL: http://localhost:8501"
echo ""
echo "🛑 Para detener la aplicación, presiona Ctrl+C"
echo "=================================================="
echo ""

# Iniciar streamlit sin la pregunta del email
export STREAMLIT_EMAIL=""
streamlit run app.py
