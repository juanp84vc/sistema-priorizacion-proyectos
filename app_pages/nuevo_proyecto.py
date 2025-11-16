"""Página para crear nuevos proyectos."""
import streamlit as st
import sys
from pathlib import Path

# Agregar src al path si no está
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto
from models.municipios_colombia import MUNICIPIOS_POR_DEPARTAMENTO, obtener_municipios, obtener_todos_departamentos
from servicios.recomendador import RecomendadorProyectos
from database.db_manager import get_db_manager
from ui.componentes_pdet import SelectorSectoresPDET


def formatear_numero(numero: float, decimales: int = 2) -> str:
    """
    Formatea un número con punto para miles y coma para decimales.

    Args:
        numero: Número a formatear
        decimales: Cantidad de decimales a mostrar

    Returns:
        str: Número formateado (ej: 1.234.567,89)
    """
    if numero is None:
        return "0,00"

    # Formatear con decimales
    formato = f"{{:,.{decimales}f}}"
    numero_formateado = formato.format(numero)

    # Intercambiar punto y coma (de formato US a formato europeo/latinoamericano)
    numero_formateado = numero_formateado.replace(",", "TEMP")
    numero_formateado = numero_formateado.replace(".", ",")
    numero_formateado = numero_formateado.replace("TEMP", ".")

    return numero_formateado


def show():
    """Muestra el formulario de nuevo proyecto."""
    st.markdown("<h1 class='main-header'>➕ Nuevo Proyecto</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Inicializar estado para controlar el reinicio del formulario
    if 'proyecto_guardado' not in st.session_state:
        st.session_state.proyecto_guardado = False

    # Botón para limpiar formulario
    col_title, col_clear = st.columns([3, 1])
    with col_title:
        st.markdown("### Información del Proyecto")
    with col_clear:
        if st.button("🔄 Limpiar Formulario", use_container_width=True):
            # Limpiar los selectores de ubicación
            if 'departamentos_multiselect' in st.session_state:
                del st.session_state.departamentos_multiselect
            if 'municipios_multiselect' in st.session_state:
                del st.session_state.municipios_multiselect
            st.session_state.proyecto_guardado = False
            st.rerun()

    # Selectores de ubicación FUERA del formulario para permitir actualización dinámica
    st.markdown("#### 🌍 Selección de Ubicación")
    st.caption("Selecciona primero los departamentos, luego podrás elegir los municipios específicos")

    col_dept, col_muni = st.columns(2)

    with col_dept:
        departamentos_selected = st.multiselect(
            "Departamentos donde se ejecutará *",
            options=obtener_todos_departamentos(),
            help="Selecciona uno o más departamentos",
            key="departamentos_multiselect"
        )

    with col_muni:
        # Selector dinámico de municipios basado en departamentos seleccionados
        municipios_disponibles = []
        if departamentos_selected:
            for dept in departamentos_selected:
                munis = obtener_municipios(dept)
                municipios_disponibles.extend(munis)
            # Eliminar duplicados y ordenar
            municipios_disponibles = sorted(list(set(municipios_disponibles)))

        municipios_selected = st.multiselect(
            "Municipios donde se ejecutará",
            options=municipios_disponibles,
            help="Selecciona los municipios específicos (opcional)",
            disabled=len(departamentos_selected) == 0,
            key="municipios_multiselect"
        )

    # NUEVO: Selector de sectores con puntajes PDET
    sectores_seleccionados = []
    puntajes_pdet = {}
    es_municipio_pdet = False

    if departamentos_selected and municipios_selected:
        # Usar primer departamento y municipio para el selector
        dept_principal = departamentos_selected[0] if isinstance(departamentos_selected, list) else departamentos_selected
        muni_principal = municipios_selected[0] if isinstance(municipios_selected, list) else municipios_selected

        # Renderizar selector de sectores con puntajes PDET
        selector = SelectorSectoresPDET()
        sectores_seleccionados, puntajes_pdet, es_municipio_pdet = selector.render(
            departamento=dept_principal,
            municipio=muni_principal,
            key="sectores_proyecto"
        )

    st.markdown("---")

    # Formulario
    with st.form("nuevo_proyecto_form"):
        # Sección 1: Información Básica
        st.markdown("#### 📋 Información Básica")

        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input(
                "Nombre del Proyecto *",
                placeholder="Ej: Educación Digital Rural"
            )
            organizacion = st.text_input(
                "Organización Ejecutora *",
                placeholder="Ej: Fundación TechRural"
            )

        with col2:
            proyecto_id = st.text_input(
                "ID del Proyecto *",
                placeholder="Ej: PROY-001"
            )
            poblacion = st.text_input(
                "Población Objetivo *",
                placeholder="Ej: Niños y jóvenes en zonas rurales"
            )

        descripcion = st.text_area(
            "Descripción del Proyecto *",
            placeholder="Describe brevemente el proyecto, sus objetivos y metodología...",
            height=100
        )

        # Sección 2: Información Geográfica y Temporal
        st.markdown("#### 🌍 Alcance Geográfico y Temporal")

        col1, col2, col3 = st.columns(3)

        with col1:
            area_geografica = st.selectbox(
                "Área Geográfica *",
                options=["urbana", "rural", "periurbana", "nacional"]
            )

        with col2:
            duracion_meses = st.number_input(
                "Duración (meses) *",
                min_value=1,
                max_value=120,
                value=24,
                step=1
            )

        with col3:
            presupuesto = st.number_input(
                "Presupuesto Total ($) *",
                min_value=0.0,
                value=100000.0,
                step=1000.0,
                format="%.2f"
            )

        # Sección 3: Beneficiarios
        st.markdown("#### 👥 Beneficiarios")

        col1, col2 = st.columns(2)

        with col1:
            beneficiarios_directos = st.number_input(
                "Beneficiarios Directos *",
                min_value=0,
                value=500,
                step=10
            )

        with col2:
            beneficiarios_indirectos = st.number_input(
                "Beneficiarios Indirectos *",
                min_value=0,
                value=1500,
                step=10
            )

        # Sección 4: Información Cualitativa de Criterios
        st.markdown("#### 📋 Información Adicional de Evaluación")
        st.caption("Información cualitativa que complementa la evaluación automática")

        # Criterio 1: Costo-Efectividad
        st.markdown("**Criterio 1: Costo-Efectividad**")
        col1, col2 = st.columns(2)

        with col1:
            sroi = st.number_input(
                "SROI (Retorno Social de la Inversión)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                help="Ratio que mide el retorno social de la inversión (ej: 3.5 significa que por cada peso invertido se generan 3.5 pesos de valor social)"
            )

        with col2:
            pertinencia_operacional = st.selectbox(
                "Pertinencia Operacional y Reputacional",
                options=["Alta", "Media", "Baja"],
                index=1,
                help="Evalúa la pertinencia del proyecto para las operaciones y reputación de GEB"
            )

        st.markdown("---")

        # Criterio 2: Relacionamiento con Stakeholders
        st.markdown("**Criterio 2: Relacionamiento con Stakeholders**")
        contribucion_stakeholders = st.selectbox(
            "Nivel de Contribución al Relacionamiento",
            options=["Alta", "Moderada", "Baja"],
            index=1,
            help="Evalúa el nivel de contribución al relacionamiento con stakeholders locales"
        )

        st.markdown("---")

        # Criterio 3: Probabilidad de Aprobación
        st.markdown("**Criterio 3: Probabilidad de Aprobación**")
        sectores_zomac = st.selectbox(
            "Alineación con Sectores Prioritarios",
            options=[
                "Top 2 sectores prioritarios ZOMAC/PDET",
                "Top 3 sectores ZOMAC/PDET",
                "Top 4 sectores ZOMAC/PDET",
                "Requiere esfuerzos de alineación",
                "No ZOMAC/PDET o no se alinea"
            ],
            index=2,
            help="Indica el nivel de alineación del proyecto con sectores prioritarios ZOMAC/PDET"
        )

        st.markdown("---")

        # Criterio 4: Riesgos de Ejecución
        st.markdown("**Criterio 4: Riesgos de Ejecución**")
        nivel_riesgos = st.selectbox(
            "Nivel de Riesgos",
            options=["Bajos y manejables", "Medios y manejables", "Altos pero mitigables", "Altos y complejos"],
            index=1,
            help="Evaluación cualitativa de los riesgos asociados a la ejecución del proyecto"
        )

        # Botones
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            submit = st.form_submit_button("✅ Guardar Proyecto", type="primary", use_container_width=True)

        with col2:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)

    # Procesar formulario
    if submit:
        # Validaciones
        if not nombre or not organizacion or not proyecto_id or not poblacion or not descripcion:
            st.error("❌ Por favor completa todos los campos obligatorios (*)")
            return

        if len(departamentos_selected) == 0:
            st.error("❌ Debes seleccionar al menos un departamento")
            return

        # Obtener gestor de base de datos
        db = get_db_manager()

        # Verificar que no exista un proyecto con el mismo ID
        if db.obtener_proyecto(proyecto_id) is not None:
            st.error(f"❌ Ya existe un proyecto con el ID '{proyecto_id}'. Por favor usa un ID diferente.")
            return

        # Crear proyecto
        try:
            proyecto = ProyectoSocial(
                id=proyecto_id,
                nombre=nombre,
                organizacion=organizacion,
                descripcion=descripcion,
                beneficiarios_directos=beneficiarios_directos,
                beneficiarios_indirectos=beneficiarios_indirectos,
                duracion_meses=duracion_meses,
                presupuesto_total=presupuesto,
                ods_vinculados=[],  # Campo mantenido para compatibilidad pero vacío
                area_geografica=AreaGeografica(area_geografica),
                poblacion_objetivo=poblacion,
                departamentos=departamentos_selected,
                municipios=municipios_selected,
                estado=EstadoProyecto.PROPUESTA,
                # NUEVO: Campos PDET
                sectores=sectores_seleccionados,
                puntajes_pdet=puntajes_pdet,
                tiene_municipios_pdet=es_municipio_pdet,
                puntaje_sectorial_max=max(puntajes_pdet.values()) if puntajes_pdet else None,
                indicadores_impacto={
                    # Información cualitativa de criterios
                    'sroi': sroi if sroi > 0 else 0.0,
                    'pertinencia_operacional': pertinencia_operacional,
                    'contribucion_stakeholders': contribucion_stakeholders,
                    'sectores_zomac': sectores_zomac,
                    'nivel_riesgos': nivel_riesgos,
                    # Valores por defecto para compatibilidad
                    'años_experiencia': 5,
                    'equipo_calificado': 0.8,
                    'proyectos_exitosos': 3,
                    'fuentes_financiamiento': 3,
                    'ingresos_propios_pct': 20.0
                }
            )

            # Guardar en base de datos
            if db.crear_proyecto(proyecto):
                # Actualizar session state con la lista completa desde BD
                st.session_state.proyectos = db.obtener_todos_proyectos()
                st.session_state.proyecto_guardado = True
                st.success(f"✅ Proyecto '{nombre}' creado exitosamente! Total de proyectos: {len(st.session_state.proyectos)}")
            else:
                st.error(f"❌ Error al guardar el proyecto en la base de datos.")
                return

            # Generar recomendaciones personalizadas
            recomendador = RecomendadorProyectos()
            recomendaciones = recomendador.analizar_proyecto(proyecto)
            # Para proyecto nuevo, usar score estimado base de 50
            score_estimado, mensaje_score = recomendador.generar_score_potencial(
                proyecto=proyecto,
                score_actual=50.0  # Score base para proyecto nuevo sin evaluar
            )

            # Mostrar score estimado
            st.info(f"📊 {mensaje_score}")

            # Mostrar recomendaciones en pestañas
            if any(recomendaciones.values()):
                st.markdown("### 💡 Recomendaciones para Optimizar el Proyecto")

                tabs = st.tabs(["⚠️ Críticas", "📈 Importantes", "✨ Opcionales", "✅ Fortalezas"])

                with tabs[0]:  # Críticas
                    if recomendaciones['criticas']:
                        st.markdown("**Aspectos que deben corregirse para mejorar significativamente:**")
                        for rec in recomendaciones['criticas']:
                            st.warning(rec)
                    else:
                        st.success("✅ No hay observaciones críticas")

                with tabs[1]:  # Importantes
                    if recomendaciones['importantes']:
                        st.markdown("**Mejoras que aumentarían considerablemente el puntaje:**")
                        for rec in recomendaciones['importantes']:
                            st.info(rec)
                    else:
                        st.success("✅ Los aspectos importantes están bien cubiertos")

                with tabs[2]:  # Opcionales
                    if recomendaciones['opcionales']:
                        st.markdown("**Optimizaciones adicionales:**")
                        for rec in recomendaciones['opcionales']:
                            st.markdown(f"- {rec}")
                    else:
                        st.info("No hay sugerencias opcionales en este momento")

                with tabs[3]:  # Fortalezas
                    if recomendaciones['fortalezas']:
                        st.markdown("**Aspectos destacados del proyecto:**")
                        for fortaleza in recomendaciones['fortalezas']:
                            st.success(fortaleza)
                    else:
                        st.info("Implementa las recomendaciones para desarrollar fortalezas")

            # Mostrar opciones después de guardar
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.info("💡 Puedes crear otro proyecto o ir a 'Dashboard' para ver todos tus proyectos")
            with col2:
                if st.button("➕ Crear Otro Proyecto", type="primary", key="crear_otro"):
                    # Limpiar selectores
                    if 'departamentos_multiselect' in st.session_state:
                        del st.session_state.departamentos_multiselect
                    if 'municipios_multiselect' in st.session_state:
                        del st.session_state.municipios_multiselect
                    st.session_state.proyecto_guardado = False
                    st.rerun()

            # Mostrar resumen
            with st.expander("📋 Ver Resumen del Proyecto", expanded=True):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    **ID:** {proyecto.id}
                    **Nombre:** {proyecto.nombre}
                    **Organización:** {proyecto.organizacion}
                    **Duración:** {formatear_numero(proyecto.duracion_años, 1)} años
                    **Presupuesto:** ${formatear_numero(proyecto.presupuesto_total)}
                    """)

                with col2:
                    st.markdown(f"""
                    **Beneficiarios Totales:** {formatear_numero(proyecto.beneficiarios_totales, 0)}
                    **Costo por beneficiario:** ${formatear_numero(proyecto.presupuesto_por_beneficiario)}
                    **Área:** {proyecto.area_geografica.value}
                    **ODS:** {', '.join(proyecto.ods_vinculados)}
                    """)

        except ValueError as e:
            st.error(f"❌ Error al crear proyecto: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")

    if cancel:
        st.info("Operación cancelada")

    # Mostrar proyectos existentes
    if len(st.session_state.proyectos) > 0:
        st.markdown("---")
        st.markdown("### 📚 Proyectos Registrados")

        # Inicializar la lista de proyectos a eliminar si no existe
        if 'proyectos_a_eliminar' not in st.session_state:
            st.session_state.proyectos_a_eliminar = []

        for idx, proyecto in enumerate(st.session_state.proyectos):
            with st.expander(f"**{idx + 1}. {proyecto.nombre}** - {proyecto.organizacion}"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"""
                    **ID:** {proyecto.id}
                    **Duración:** {formatear_numero(proyecto.duracion_años, 1)} años
                    **Presupuesto:** ${formatear_numero(proyecto.presupuesto_total)}
                    """)

                with col2:
                    st.markdown(f"""
                    **Beneficiarios:** {formatear_numero(proyecto.beneficiarios_totales, 0)}
                    **Área:** {proyecto.area_geografica.value}
                    **Estado:** {proyecto.estado.value}
                    """)

                with col3:
                    st.markdown(f"""
                    **Departamentos:**
                    {', '.join(proyecto.departamentos)}
                    """)

                    if proyecto.municipios:
                        st.markdown(f"""
                        **Municipios:**
                        {', '.join(proyecto.municipios)}
                        """)

                # Botón para eliminar proyecto
                st.markdown("---")
                if st.button(f"🗑️ Eliminar Proyecto", key=f"delete_{proyecto.id}_{idx}", type="secondary"):
                    st.session_state.proyectos_a_eliminar.append(idx)
                    st.rerun()

        # Eliminar proyectos marcados
        if st.session_state.proyectos_a_eliminar:
            db = get_db_manager()
            # Eliminar en orden inverso para no afectar los índices
            for idx in sorted(st.session_state.proyectos_a_eliminar, reverse=True):
                if idx < len(st.session_state.proyectos):
                    proyecto_eliminado = st.session_state.proyectos[idx]
                    # Eliminar de la base de datos
                    if db.eliminar_proyecto(proyecto_eliminado.id):
                        st.success(f"✅ Proyecto '{proyecto_eliminado.nombre}' eliminado correctamente")
                    else:
                        st.error(f"❌ Error al eliminar proyecto '{proyecto_eliminado.nombre}'")
            # Recargar proyectos desde BD
            st.session_state.proyectos = db.obtener_todos_proyectos()
            st.session_state.proyectos_a_eliminar = []
