"""Página de inicio de la aplicación."""
import streamlit as st


def show():
    """Muestra la página de inicio."""
    st.markdown("<h1 class='main-header'>🎯 Sistema de Priorización de Proyectos Sociales</h1>",
                unsafe_allow_html=True)

    st.markdown("---")

    # Introducción
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Bienvenido al Sistema de Priorización")
        st.markdown("""
        Esta herramienta te permite:

        - ✅ **Formular proyectos sociales** con información estructurada
        - 📊 **Evaluar y priorizar** proyectos según criterios definidos
        - 📈 **Visualizar métricas** de impacto y sostenibilidad
        - 📄 **Generar reportes** profesionales para toma de decisiones
        - ⚙️ **Configurar criterios** personalizados según necesidades

        ---

        #### 🚀 Cómo empezar

        1. **Nuevo Proyecto**: Registra proyectos en el sistema
        2. **Evaluar Cartera**: Compara y prioriza proyectos
        3. **Dashboard**: Visualiza métricas agregadas
        4. **Configuración**: Ajusta criterios y pesos
        """)

    with col2:
        st.markdown("### 📊 Resumen Rápido")

        # Métricas
        num_proyectos = len(st.session_state.proyectos)

        st.metric("Proyectos Registrados", num_proyectos)

        if num_proyectos > 0:
            # Calcular presupuesto total
            presupuesto_total = sum(p.presupuesto_total for p in st.session_state.proyectos)
            beneficiarios_total = sum(p.beneficiarios_totales for p in st.session_state.proyectos)

            st.metric("Presupuesto Total", f"${presupuesto_total:,.0f}")
            st.metric("Beneficiarios Totales", f"{beneficiarios_total:,}")
        else:
            st.info("👆 Comienza registrando tu primer proyecto")

    # Sección de características
    st.markdown("---")
    st.markdown("### ⚡ Características Principales")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        #### 🎯 Priorización Inteligente

        Sistema de scoring basado en:
        - Impacto social
        - Sostenibilidad financiera
        - Alineación con ODS
        - Capacidad organizacional
        """)

    with col2:
        st.markdown("""
        #### 📊 Múltiples Estrategias

        Elige cómo evaluar:
        - Scoring ponderado
        - Umbrales mínimos
        - Comparación directa
        - Análisis de cartera
        """)

    with col3:
        st.markdown("""
        #### 🛠️ Totalmente Configurable

        Personaliza según tu organización:
        - Criterios propios
        - Pesos ajustables
        - ODS prioritarios
        - Umbrales personalizados
        """)

    # Principios SOLID
    st.markdown("---")

    with st.expander("🏗️ Arquitectura del Sistema (Principios SOLID)"):
        st.markdown("""
        Este sistema está construido siguiendo los **Principios SOLID** de diseño de software:

        - **S** - Single Responsibility: Cada criterio tiene una sola responsabilidad
        - **O** - Open/Closed: Extensible sin modificar código existente
        - **L** - Liskov Substitution: Criterios intercambiables
        - **I** - Interface Segregation: Interfaces mínimas y focalizadas
        - **D** - Dependency Inversion: Sistema depende de abstracciones

        Esto garantiza:
        - ✅ Fácil mantenimiento
        - ✅ Extensibilidad sin romper funcionalidad
        - ✅ Código limpio y testeable
        - ✅ Adaptabilidad a nuevos requerimientos
        """)

    # Guía rápida
    st.markdown("---")

    with st.expander("📖 Guía Rápida de Uso"):
        st.markdown("""
        #### 1. Registrar un Proyecto

        Ve a **"➕ Nuevo Proyecto"** y completa el formulario con:
        - Información básica (nombre, organización, descripción)
        - Datos financieros (presupuesto, duración)
        - Indicadores de impacto
        - ODS vinculados

        #### 2. Evaluar Cartera

        En **"📊 Evaluar Cartera"**:
        - Selecciona proyectos a comparar
        - Elige estrategia de evaluación
        - Visualiza ranking y scores
        - Exporta resultados

        #### 3. Análisis Visual

        El **"📈 Dashboard"** te muestra:
        - Distribución por ODS
        - Métricas agregadas
        - Comparaciones visuales
        - Tendencias de la cartera

        #### 4. Personalización

        En **"⚙️ Configuración"**:
        - Ajusta pesos de criterios
        - Define ODS prioritarios
        - Configura umbrales
        - Guarda configuraciones
        """)
