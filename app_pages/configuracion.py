"""Página de configuración del sistema."""
import streamlit as st


def show():
    """Muestra la página de configuración."""
    st.markdown("<h1 class='main-header'>⚙️ Configuración del Sistema</h1>",
                unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### Configura criterios, pesos y preferencias del sistema")

    # Sección 1: Pesos de criterios por defecto
    st.markdown("#### 🎯 Pesos de Criterios por Defecto")

    st.info("💡 Estos pesos se usarán como valores por defecto en las evaluaciones")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        peso_impacto = st.slider(
            "Impacto Social",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['impacto_social'],
            step=0.05,
            key="config_impacto"
        )

    with col2:
        peso_sostenibilidad = st.slider(
            "Sostenibilidad",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['sostenibilidad'],
            step=0.05,
            key="config_sostenibilidad"
        )

    with col3:
        peso_ods = st.slider(
            "Alineación ODS",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['alineacion_ods'],
            step=0.05,
            key="config_ods"
        )

    with col4:
        peso_capacidad = st.slider(
            "Capacidad Org.",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['capacidad_org'],
            step=0.05,
            key="config_capacidad"
        )

    suma_pesos = peso_impacto + peso_sostenibilidad + peso_ods + peso_capacidad

    if abs(suma_pesos - 1.0) > 0.01:
        st.error(f"❌ La suma de pesos debe ser 1.0. Actual: {suma_pesos:.2f}")
    else:
        st.success(f"✅ Suma de pesos: {suma_pesos:.2f}")

    # Sección 2: ODS Prioritarios
    st.markdown("---")
    st.markdown("#### 🎯 ODS Prioritarios de la Organización")

    ods_prioritarios = st.multiselect(
        "Selecciona los ODS que son prioritarios para tu organización",
        options=[
            "ODS 1", "ODS 2", "ODS 3", "ODS 4", "ODS 5", "ODS 6",
            "ODS 7", "ODS 8", "ODS 9", "ODS 10", "ODS 11", "ODS 12",
            "ODS 13", "ODS 14", "ODS 15", "ODS 16", "ODS 17"
        ],
        default=st.session_state.configuracion['ods_prioritarios']
    )

    # Sección 3: Estrategia por defecto
    st.markdown("---")
    st.markdown("#### 🎲 Estrategia de Evaluación por Defecto")

    estrategia_default = st.radio(
        "¿Qué estrategia usar por defecto?",
        options=["ponderado", "umbral"],
        format_func=lambda x: "Scoring Ponderado" if x == "ponderado" else "Scoring con Umbrales",
        index=0 if st.session_state.configuracion['estrategia'] == 'ponderado' else 1,
        horizontal=True
    )

    # Sección 4: Información del sistema
    st.markdown("---")
    st.markdown("#### 📊 Información del Sistema")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Proyectos Registrados", len(st.session_state.proyectos))

    with col2:
        if len(st.session_state.proyectos) > 0:
            presupuesto_total = sum(p.presupuesto_total for p in st.session_state.proyectos)
            st.metric("Presupuesto Total", f"${presupuesto_total / 1e6:.1f}M")
        else:
            st.metric("Presupuesto Total", "$0")

    with col3:
        if len(st.session_state.proyectos) > 0:
            beneficiarios_total = sum(p.beneficiarios_totales for p in st.session_state.proyectos)
            st.metric("Beneficiarios Totales", f"{beneficiarios_total:,}")
        else:
            st.metric("Beneficiarios Totales", "0")

    # Botones de acción
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("💾 Guardar Configuración", type="primary", use_container_width=True):
            # Guardar en session state
            st.session_state.configuracion['criterios']['impacto_social'] = peso_impacto
            st.session_state.configuracion['criterios']['sostenibilidad'] = peso_sostenibilidad
            st.session_state.configuracion['criterios']['alineacion_ods'] = peso_ods
            st.session_state.configuracion['criterios']['capacidad_org'] = peso_capacidad
            st.session_state.configuracion['ods_prioritarios'] = ods_prioritarios
            st.session_state.configuracion['estrategia'] = estrategia_default

            st.success("✅ Configuración guardada exitosamente")

    with col2:
        if st.button("🔄 Restaurar Valores por Defecto", use_container_width=True):
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
            st.success("✅ Valores restaurados")
            st.rerun()

    # Gestión de datos
    st.markdown("---")
    st.markdown("#### 🗑️ Gestión de Datos")

    with st.expander("⚠️ Zona de Peligro"):
        st.warning("Las siguientes acciones son irreversibles")

        if st.button("🗑️ Eliminar Todos los Proyectos", type="secondary"):
            if st.session_state.proyectos:
                st.session_state.proyectos = []
                st.success("Todos los proyectos han sido eliminados")
                st.rerun()
            else:
                st.info("No hay proyectos para eliminar")

    # Información técnica
    st.markdown("---")

    with st.expander("🔧 Información Técnica"):
        st.markdown("""
        ### Sistema de Priorización de Proyectos Sociales

        **Versión:** 1.0.0
        **Arquitectura:** Principios SOLID
        **Framework:** Streamlit

        #### Criterios de Evaluación

        1. **Impacto Social**: Evalúa beneficiarios, alcance geográfico y duración
        2. **Sostenibilidad Financiera**: Analiza diversificación de fondos e ingresos propios
        3. **Alineación ODS**: Mide contribución a Objetivos de Desarrollo Sostenible
        4. **Capacidad Organizacional**: Evalúa experiencia, equipo y trayectoria

        #### Estrategias de Evaluación

        - **Scoring Ponderado**: Calcula score final como suma ponderada de criterios
        - **Scoring con Umbrales**: Aplica umbrales mínimos por criterio

        #### Tecnologías

        - Python 3.11+
        - Streamlit para UI
        - Plotly para visualizaciones
        - Pandas para análisis de datos
        """)
