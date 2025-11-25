"""
Aplicación Web para Sistema de Priorización de Proyectos Sociales.
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

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Priorización de Proyectos | Valor Compartido",
    page_icon="🎯",
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
    else:
        # Fallback CSS básico si no existe el archivo
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
            * { font-family: 'Inter', sans-serif; }
            .main { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); }
        </style>
        """, unsafe_allow_html=True)

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

# Sidebar - Menú de navegación
with st.sidebar:
    # Logo del sistema
    logo_path = Path(__file__).parent / "static" / "images" / "logo_sistema.png"
    if logo_path.exists():
        st.image(str(logo_path), width=80)
    
    st.markdown('<h2 class="text-gradient-primary" style="text-align: center; margin: 0.5rem 0;">Sistema de Priorización</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-bottom: 1rem;">Proyectos de Valor Compartido</p>', unsafe_allow_html=True)
    st.markdown("---")

    menu_option = st.radio(
        "Navegación:",
        ["🏠 Inicio", "➕ Nuevo Proyecto", "🔍 Buscar y Editar",
         "📊 Evaluar Cartera", "🧪 Test Motor", "📚 Historial", "🤖 Asistente IA",
         "📖 Historial IA", "📈 Dashboard", "⚙️ Configuración"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    
    # Métricas del sidebar con diseño mejorado
    st.markdown('<div class="glass-card" style="padding: 1rem; margin: 1rem 0;">', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">PROYECTOS REGISTRADOS</p>', unsafe_allow_html=True)
    st.markdown(f'<h3 class="text-gradient-primary" style="margin: 0.25rem 0;">{len(st.session_state.proyectos)}</h3>', unsafe_allow_html=True)
    
    if len(st.session_state.proyectos) > 0:
        ultimo = st.session_state.proyectos[-1]
        st.markdown(f'<p style="font-size: 0.75rem; color: #cbd5e1; margin-top: 0.5rem;">Último: {ultimo.nombre[:25]}...</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <p class='text-gradient-primary' style='font-weight: 600; font-size: 1rem; margin: 0;'>
            Sistema de Priorización de Proyectos Sociales
        </p>
        <p style='color: #94a3b8; font-size: 0.85rem; margin-top: 0.5rem;'>
            Valor Compartido • Desarrollado siguiendo Principios SOLID
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
