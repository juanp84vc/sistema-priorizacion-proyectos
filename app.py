"""
Aplicación Web para Sistema de Priorización de Proyectos Sociales.
Sistema ENLAZA GEB - Arquitectura C
Usando Streamlit para interface gráfica.

Ejecutar con: streamlit run app.py
"""
import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Importar páginas
from app_pages import home, nuevo_proyecto, buscar_proyectos, evaluar_cartera, dashboard, configuracion, historial_proyecto, asistente_ia, historial_ia, test_motor

# Importar gestor de base de datos
from database.db_manager import get_db_manager

# Importar estilos UI ejecutivos
try:
    from ui.estilos import EstilosUI
    UI_DISPONIBLE = True
except ImportError:
    UI_DISPONIBLE = False

# Configuración de la página
st.set_page_config(
    page_title="ENLAZA GEB | Sistema de Priorización",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar CSS personalizado moderno
def load_css():
    """Carga el archivo CSS personalizado."""
    css_file = Path(__file__).parent / "static" / "styles.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Aplicar estilos ejecutivos adicionales
    if UI_DISPONIBLE:
        EstilosUI.aplicar_estilos_ejecutivos()

load_css()

# Inicializar base de datos
@st.cache_resource
def init_database():
    """Inicializa la base de datos y retorna el gestor."""
    return get_db_manager()

db = init_database()

# Inicializar session state
if 'proyectos' not in st.session_state:
    # Cargar proyectos desde la base de datos
    st.session_state.proyectos = db.obtener_todos_proyectos()

if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = True

if 'configuracion' not in st.session_state:
    st.session_state.configuracion = {
        'criterios': {
            'costo_efectividad': 0.25,
            'stakeholders': 0.25,
            'probabilidad_aprobacion': 0.25,
            'riesgos': 0.25
        },
        'ods_prioritarios': ['ODS 1', 'ODS 2', 'ODS 3', 'ODS 4', 'ODS 5'],
        'estrategia': 'ponderado'
    }

# Inicializar gestor de historial
if 'gestor_historial' not in st.session_state:
    from servicios.gestor_historial import GestorHistorial
    st.session_state.gestor_historial = GestorHistorial()

# Sidebar - Menú de navegación ejecutivo
with st.sidebar:
    # Header del sidebar con logo
    st.markdown("""
    <div class="sidebar-logo-container">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚡</div>
        <h2 class="sidebar-titulo">ENLAZA GEB</h2>
        <p class="sidebar-subtitulo">Sistema de Priorización</p>
    </div>
    """, unsafe_allow_html=True)

    # Navegación principal
    st.markdown('<p style="color: #64748b; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; padding: 0 1rem; margin-bottom: 0.5rem;">Navegación Principal</p>', unsafe_allow_html=True)

    menu_option = st.radio(
        "Navegación:",
        ["📈 Dashboard", "📊 Evaluar Cartera", "➕ Nuevo Proyecto", "🔍 Buscar y Editar",
         "🧪 Test Motor", "📚 Historial", "🤖 Asistente IA",
         "📖 Historial IA", "🏠 Inicio", "⚙️ Configuración"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Métricas del sidebar con diseño ejecutivo
    st.markdown("""
    <div style="background: linear-gradient(145deg, rgba(14, 165, 233, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
         border: 1px solid rgba(14, 165, 233, 0.2); border-radius: 0.75rem;
         padding: 1rem; margin: 0.5rem;">
        <p style="font-size: 0.65rem; color: #64748b; margin: 0; text-transform: uppercase; letter-spacing: 0.05em;">
            Proyectos en Cartera
        </p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <h3 style="font-size: 2rem; font-weight: 700; margin: 0.25rem 0;
             background: linear-gradient(135deg, #0ea5e9 0%, #10b981 100%);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {len(st.session_state.proyectos)}
        </h3>
    """, unsafe_allow_html=True)

    if len(st.session_state.proyectos) > 0:
        ultimo = st.session_state.proyectos[-1]
        nombre_corto = ultimo.nombre[:22] + "..." if len(ultimo.nombre) > 22 else ultimo.nombre
        st.markdown(f'<p style="font-size: 0.7rem; color: #94a3b8; margin: 0.5rem 0 0 0;">Último: {nombre_corto}</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Versión del sistema
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-top: 1rem;">
        <p style="color: #475569; font-size: 0.65rem; margin: 0;">Arquitectura C v2.0</p>
        <p style="color: #334155; font-size: 0.6rem; margin: 0.25rem 0 0 0;">Valor Compartido</p>
    </div>
    """, unsafe_allow_html=True)

# Routing a las diferentes páginas
if menu_option == "🏠 Inicio":
    home.show()
elif menu_option == "➕ Nuevo Proyecto":
    nuevo_proyecto.show()
elif menu_option == "🔍 Buscar y Editar":
    buscar_proyectos.show()
elif menu_option == "📊 Evaluar Cartera":
    evaluar_cartera.show()
elif menu_option == "🧪 Test Motor":
    test_motor.show()
elif menu_option == "📚 Historial":
    historial_proyecto.show()
elif menu_option == "🤖 Asistente IA":
    asistente_ia.show()
elif menu_option == "📖 Historial IA":
    historial_ia.show()
elif menu_option == "📈 Dashboard":
    dashboard.show()
elif menu_option == "⚙️ Configuración":
    configuracion.show()

# Footer ejecutivo
st.markdown("""
<div class="footer-ejecutivo">
    <div class="footer-titulo">Sistema de Priorización ENLAZA GEB</div>
    <div class="footer-subtitulo">Valor Compartido | Arquitectura C | Principios SOLID</div>
</div>
""", unsafe_allow_html=True)
