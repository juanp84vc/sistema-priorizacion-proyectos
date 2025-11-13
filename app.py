"""
Aplicación Web para Sistema de Priorización de Proyectos Sociales.
Usando Streamlit para interface gráfica.

Ejecutar con: streamlit run app.py
"""
import streamlit as st
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Importar páginas
from app_pages import home, nuevo_proyecto, buscar_proyectos, evaluar_cartera, dashboard, configuracion

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Priorización de Proyectos",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'proyectos' not in st.session_state:
    st.session_state.proyectos = []
if 'configuracion' not in st.session_state:
    st.session_state.configuracion = {
        'criterios': {
            'impacto_social': 0.4,
            'sostenibilidad': 0.3,
            'alineacion_ods': 0.2,
            'capacidad_org': 0.1
        },
        'ods_prioritarios': ['ODS 1', 'ODS 2', 'ODS 3', 'ODS 4', 'ODS 5'],
        'estrategia': 'ponderado'
    }

# Sidebar - Menú de navegación
with st.sidebar:
    st.markdown("### 🎯 Sistema de Priorización")
    st.markdown("---")

    # Logo o imagen (opcional)
    st.markdown("#### Menú Principal")

    menu_option = st.radio(
        "Selecciona una opción:",
        ["🏠 Inicio", "➕ Nuevo Proyecto", "🔍 Buscar y Editar",
         "📊 Evaluar Cartera", "📈 Dashboard", "⚙️ Configuración"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(f"**Proyectos registrados:** {len(st.session_state.proyectos)}")

    if len(st.session_state.proyectos) > 0:
        ultimo = st.session_state.proyectos[-1]
        st.markdown(f"*Último proyecto:*  \n{ultimo.nombre[:30]}...")

# Routing a las diferentes páginas
if menu_option == "🏠 Inicio":
    home.show()
elif menu_option == "➕ Nuevo Proyecto":
    nuevo_proyecto.show()
elif menu_option == "🔍 Buscar y Editar":
    buscar_proyectos.show()
elif menu_option == "📊 Evaluar Cartera":
    evaluar_cartera.show()
elif menu_option == "📈 Dashboard":
    dashboard.show()
elif menu_option == "⚙️ Configuración":
    configuracion.show()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "Sistema de Priorización de Proyectos Sociales | "
    "Desarrollado siguiendo Principios SOLID"
    "</div>",
    unsafe_allow_html=True
)
