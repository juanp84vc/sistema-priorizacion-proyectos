"""Página para buscar, filtrar y editar proyectos."""
import streamlit as st
import sys
from pathlib import Path

# Agregar src al path si no está
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto
from models.municipios_colombia import obtener_municipios, obtener_todos_departamentos
from servicios.recomendador import RecomendadorProyectos
from database.db_manager import get_db_manager


def formatear_numero(numero: float, decimales: int = 2) -> str:
    """Formatea un número con punto para miles y coma para decimales."""
    if numero is None:
        return "0,00"

    formato = f"{{:,.{decimales}f}}"
    numero_formateado = formato.format(numero)

    numero_formateado = numero_formateado.replace(",", "TEMP")
    numero_formateado = numero_formateado.replace(".", ",")
    numero_formateado = numero_formateado.replace("TEMP", ".")

    return numero_formateado


def filtrar_proyectos(proyectos, filtros):
    """
    Filtra proyectos según los criterios especificados.

    Args:
        proyectos: Lista de proyectos a filtrar
        filtros: Diccionario con los criterios de filtrado

    Returns:
        Lista de proyectos filtrados
    """
    resultado = proyectos.copy()

    # Filtro por búsqueda de texto
    if filtros.get('busqueda'):
        busqueda = filtros['busqueda'].lower()
        resultado = [p for p in resultado if
                    busqueda in p.nombre.lower() or
                    busqueda in p.id.lower() or
                    busqueda in p.organizacion.lower()]

    # Filtro por organización
    if filtros.get('organizacion') and filtros['organizacion'] != "Todas":
        resultado = [p for p in resultado if p.organizacion == filtros['organizacion']]

    # Filtro por departamento
    if filtros.get('departamento') and filtros['departamento'] != "Todos":
        resultado = [p for p in resultado if filtros['departamento'] in p.departamentos]

    # Filtro por ODS
    if filtros.get('ods'):
        resultado = [p for p in resultado if
                    any(ods in p.ods_vinculados for ods in filtros['ods'])]

    # Filtro por área geográfica
    if filtros.get('area') and filtros['area'] != "Todas":
        resultado = [p for p in resultado if p.area_geografica.value == filtros['area']]

    # Filtro por estado
    if filtros.get('estado') and filtros['estado'] != "Todos":
        resultado = [p for p in resultado if p.estado.value == filtros['estado']]

    # Filtro por rango de presupuesto
    if filtros.get('presupuesto_min') is not None:
        resultado = [p for p in resultado if p.presupuesto_total >= filtros['presupuesto_min']]

    if filtros.get('presupuesto_max') is not None:
        resultado = [p for p in resultado if p.presupuesto_total <= filtros['presupuesto_max']]

    return resultado


def mostrar_formulario_edicion(proyecto, idx):
    """Muestra el formulario para editar un proyecto existente."""
    st.markdown(f"### ✏️ Editando: {proyecto.nombre}")
    st.markdown("---")

    # Inicializar valores por defecto del proyecto
    if 'edit_departamentos' not in st.session_state:
        st.session_state.edit_departamentos = proyecto.departamentos.copy()
    if 'edit_municipios' not in st.session_state:
        st.session_state.edit_municipios = proyecto.municipios.copy() if proyecto.municipios else []

    # Selectores de ubicación fuera del formulario
    st.markdown("#### 🌍 Ubicación")
    col_dept, col_muni = st.columns(2)

    with col_dept:
        departamentos_edit = st.multiselect(
            "Departamentos *",
            options=obtener_todos_departamentos(),
            default=st.session_state.edit_departamentos,
            key=f"edit_dept_{idx}"
        )
        st.session_state.edit_departamentos = departamentos_edit

    with col_muni:
        municipios_disponibles = []
        if departamentos_edit:
            for dept in departamentos_edit:
                munis = obtener_municipios(dept)
                municipios_disponibles.extend(munis)
            municipios_disponibles = sorted(list(set(municipios_disponibles)))

        municipios_edit = st.multiselect(
            "Municipios",
            options=municipios_disponibles,
            default=[m for m in st.session_state.edit_municipios if m in municipios_disponibles],
            disabled=len(departamentos_edit) == 0,
            key=f"edit_muni_{idx}"
        )
        st.session_state.edit_municipios = municipios_edit

    st.markdown("---")

    # Formulario de edición
    with st.form(f"edit_form_{idx}"):
        st.markdown("#### 📋 Información Básica")

        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Nombre del Proyecto *", value=proyecto.nombre)
            organizacion = st.text_input("Organización *", value=proyecto.organizacion)

        with col2:
            proyecto_id = st.text_input("ID del Proyecto *", value=proyecto.id, disabled=True)
            poblacion = st.text_input("Población Objetivo *", value=proyecto.poblacion_objetivo)

        descripcion = st.text_area("Descripción *", value=proyecto.descripcion, height=100)

        st.markdown("#### 🌍 Alcance y Temporal")

        col1, col2, col3 = st.columns(3)

        with col1:
            area_geografica = st.selectbox(
                "Área Geográfica *",
                options=["urbana", "rural", "periurbana", "nacional"],
                index=["urbana", "rural", "periurbana", "nacional"].index(proyecto.area_geografica.value)
            )

        with col2:
            duracion_meses = st.number_input(
                "Duración (meses) *",
                min_value=1,
                max_value=120,
                value=proyecto.duracion_meses,
                step=1
            )

        with col3:
            presupuesto = st.number_input(
                "Presupuesto Total ($) *",
                min_value=0.0,
                value=float(proyecto.presupuesto_total),
                step=1000.0,
                format="%.2f"
            )

        st.markdown("#### 👥 Beneficiarios")

        col1, col2 = st.columns(2)

        with col1:
            beneficiarios_directos = st.number_input(
                "Beneficiarios Directos *",
                min_value=0,
                value=proyecto.beneficiarios_directos,
                step=10
            )

        with col2:
            beneficiarios_indirectos = st.number_input(
                "Beneficiarios Indirectos *",
                min_value=0,
                value=proyecto.beneficiarios_indirectos,
                step=10
            )

        st.markdown("#### 🎯 ODS y Estado")

        col1, col2 = st.columns(2)

        with col1:
            ods_vinculados = st.multiselect(
                "ODS vinculados",
                options=[f"ODS {i}" for i in range(1, 18)],
                default=proyecto.ods_vinculados
            )

        with col2:
            estado = st.selectbox(
                "Estado del Proyecto",
                options=["propuesta", "en_evaluacion", "aprobado", "en_ejecucion", "finalizado", "rechazado"],
                index=["propuesta", "en_evaluacion", "aprobado", "en_ejecucion", "finalizado", "rechazado"].index(proyecto.estado.value)
            )

        st.markdown("#### 📊 Indicadores de Capacidad")

        col1, col2 = st.columns(2)

        with col1:
            años_exp = st.number_input(
                "Años de experiencia",
                min_value=0,
                max_value=100,
                value=int(proyecto.indicadores_impacto.get('años_experiencia', 0)),
                step=1
            )

            proyectos_exitosos = st.number_input(
                "Proyectos exitosos previos",
                min_value=0,
                max_value=1000,
                value=int(proyecto.indicadores_impacto.get('proyectos_exitosos', 0)),
                step=1
            )

        with col2:
            equipo_calificado = st.slider(
                "% Equipo calificado",
                min_value=0.0,
                max_value=1.0,
                value=float(proyecto.indicadores_impacto.get('equipo_calificado', 0.0)),
                step=0.05,
                format="%.0f%%"
            )

            fuentes_financiamiento = st.number_input(
                "Fuentes de financiamiento",
                min_value=1,
                max_value=20,
                value=int(proyecto.indicadores_impacto.get('fuentes_financiamiento', 1)),
                step=1
            )

        ingresos_propios = st.slider(
            "% Ingresos propios",
            min_value=0.0,
            max_value=100.0,
            value=float(proyecto.indicadores_impacto.get('ingresos_propios_pct', 0.0)),
            step=5.0,
            format="%.0f%%"
        )

        # Botones
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            guardar = st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True)

        with col2:
            cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)

    # Procesar formulario
    if guardar:
        # Validaciones
        if not nombre or not organizacion or not poblacion or not descripcion:
            st.error("❌ Completa todos los campos obligatorios (*)")
            return False

        if len(ods_vinculados) == 0:
            st.error("❌ Selecciona al menos un ODS")
            return False

        if len(departamentos_edit) == 0:
            st.error("❌ Selecciona al menos un departamento")
            return False

        try:
            # Actualizar proyecto
            proyecto.nombre = nombre
            proyecto.organizacion = organizacion
            proyecto.descripcion = descripcion
            proyecto.beneficiarios_directos = beneficiarios_directos
            proyecto.beneficiarios_indirectos = beneficiarios_indirectos
            proyecto.duracion_meses = duracion_meses
            proyecto.presupuesto_total = presupuesto
            proyecto.ods_vinculados = ods_vinculados
            proyecto.area_geografica = AreaGeografica(area_geografica)
            proyecto.poblacion_objetivo = poblacion
            proyecto.departamentos = departamentos_edit
            proyecto.municipios = municipios_edit
            proyecto.estado = EstadoProyecto(estado)
            proyecto.indicadores_impacto = {
                'años_experiencia': años_exp,
                'equipo_calificado': equipo_calificado,
                'proyectos_exitosos': proyectos_exitosos,
                'fuentes_financiamiento': fuentes_financiamiento,
                'ingresos_propios_pct': ingresos_propios
            }

            # Guardar en base de datos
            db = get_db_manager()
            if db.actualizar_proyecto(proyecto):
                # Recargar proyectos desde BD
                st.session_state.proyectos = db.obtener_todos_proyectos()
                st.success(f"✅ Proyecto '{nombre}' actualizado exitosamente!")
            else:
                st.error(f"❌ Error al actualizar el proyecto en la base de datos.")
                return False

            # Limpiar estado de edición
            if 'edit_departamentos' in st.session_state:
                del st.session_state.edit_departamentos
            if 'edit_municipios' in st.session_state:
                del st.session_state.edit_municipios
            if 'proyecto_en_edicion' in st.session_state:
                del st.session_state.proyecto_en_edicion

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al actualizar: {str(e)}")
            return False

    if cancelar:
        # Limpiar estado de edición
        if 'edit_departamentos' in st.session_state:
            del st.session_state.edit_departamentos
        if 'edit_municipios' in st.session_state:
            del st.session_state.edit_municipios
        if 'proyecto_en_edicion' in st.session_state:
            del st.session_state.proyecto_en_edicion
        st.rerun()

    return False


def show():
    """Muestra la página de búsqueda y gestión de proyectos."""
    st.markdown("<h1 class='main-header'>🔍 Buscar y Gestionar Proyectos</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # Verificar que hay proyectos
    if len(st.session_state.proyectos) == 0:
        st.info("📋 No hay proyectos registrados aún. Ve a 'Nuevo Proyecto' para crear uno.")
        return

    # Si hay un proyecto en edición, mostrar solo el formulario de edición
    if 'proyecto_en_edicion' in st.session_state:
        idx = st.session_state.proyecto_en_edicion
        if idx < len(st.session_state.proyectos):
            proyecto = st.session_state.proyectos[idx]
            mostrar_formulario_edicion(proyecto, idx)
            return

    # Panel de filtros
    st.markdown("### 🔎 Filtros de Búsqueda")

    with st.expander("Mostrar/Ocultar Filtros", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            busqueda = st.text_input(
                "🔍 Buscar por nombre, ID u organización",
                placeholder="Ej: Educación, PROY-001, Fundación..."
            )

            # Obtener lista de organizaciones únicas
            organizaciones = sorted(list(set(p.organizacion for p in st.session_state.proyectos)))
            organizacion_filtro = st.selectbox(
                "🏢 Organización",
                options=["Todas"] + organizaciones
            )

        with col2:
            departamento_filtro = st.selectbox(
                "📍 Departamento",
                options=["Todos"] + obtener_todos_departamentos()
            )

            area_filtro = st.selectbox(
                "🌍 Área Geográfica",
                options=["Todas", "urbana", "rural", "periurbana", "nacional"]
            )

        with col3:
            ods_filtro = st.multiselect(
                "🎯 ODS",
                options=[f"ODS {i}" for i in range(1, 18)]
            )

            estado_filtro = st.selectbox(
                "📊 Estado",
                options=["Todos", "propuesta", "en_evaluacion", "aprobado", "en_ejecucion", "finalizado", "rechazado"]
            )

        col4, col5 = st.columns(2)

        with col4:
            presupuesto_min = st.number_input(
                "💰 Presupuesto mínimo",
                min_value=0.0,
                value=0.0,
                step=10000.0,
                format="%.0f"
            )

        with col5:
            presupuesto_max = st.number_input(
                "💰 Presupuesto máximo",
                min_value=0.0,
                value=0.0,
                step=10000.0,
                format="%.0f",
                help="0 = sin límite"
            )

    # Aplicar filtros
    filtros = {
        'busqueda': busqueda,
        'organizacion': organizacion_filtro,
        'departamento': departamento_filtro,
        'ods': ods_filtro,
        'area': area_filtro,
        'estado': estado_filtro,
        'presupuesto_min': presupuesto_min if presupuesto_min > 0 else None,
        'presupuesto_max': presupuesto_max if presupuesto_max > 0 else None
    }

    proyectos_filtrados = filtrar_proyectos(st.session_state.proyectos, filtros)

    # Mostrar resultados
    st.markdown("---")
    st.markdown(f"### 📋 Resultados ({len(proyectos_filtrados)} proyectos encontrados)")

    if len(proyectos_filtrados) == 0:
        st.warning("No se encontraron proyectos con los filtros seleccionados.")
        return

    # Opciones de ordenamiento
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"**Total encontrados:** {len(proyectos_filtrados)} de {len(st.session_state.proyectos)} proyectos")

    with col2:
        ordenar_por = st.selectbox(
            "Ordenar por:",
            options=["Nombre", "Presupuesto (mayor)", "Presupuesto (menor)", "Beneficiarios (más)", "Beneficiarios (menos)"]
        )

    # Ordenar proyectos
    if ordenar_por == "Presupuesto (mayor)":
        proyectos_filtrados.sort(key=lambda p: p.presupuesto_total, reverse=True)
    elif ordenar_por == "Presupuesto (menor)":
        proyectos_filtrados.sort(key=lambda p: p.presupuesto_total)
    elif ordenar_por == "Beneficiarios (más)":
        proyectos_filtrados.sort(key=lambda p: p.beneficiarios_totales, reverse=True)
    elif ordenar_por == "Beneficiarios (menos)":
        proyectos_filtrados.sort(key=lambda p: p.beneficiarios_totales)
    else:  # Nombre
        proyectos_filtrados.sort(key=lambda p: p.nombre)

    # Mostrar proyectos
    for proyecto in proyectos_filtrados:
        # Encontrar el índice real en la lista de proyectos
        idx = st.session_state.proyectos.index(proyecto)

        with st.expander(f"**{proyecto.nombre}** - {proyecto.organizacion} (ID: {proyecto.id})"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                **Presupuesto:** ${formatear_numero(proyecto.presupuesto_total, 0)}
                **Beneficiarios:** {formatear_numero(proyecto.beneficiarios_totales, 0)}
                **Costo/Beneficiario:** ${formatear_numero(proyecto.presupuesto_por_beneficiario)}
                """)

            with col2:
                st.markdown(f"""
                **Duración:** {formatear_numero(proyecto.duracion_años, 1)} años
                **Área:** {proyecto.area_geografica.value}
                **Estado:** {proyecto.estado.value}
                """)

            with col3:
                st.markdown(f"""
                **Departamentos:** {', '.join(proyecto.departamentos)}
                **ODS:** {', '.join(proyecto.ods_vinculados[:3])}{'...' if len(proyecto.ods_vinculados) > 3 else ''}
                """)

            st.markdown("**Descripción:**")
            st.markdown(proyecto.descripcion[:200] + "..." if len(proyecto.descripcion) > 200 else proyecto.descripcion)

            # Botones de acción
            st.markdown("---")
            col_edit, col_delete, col_space = st.columns([1, 1, 2])

            with col_edit:
                if st.button(f"✏️ Editar", key=f"edit_btn_{idx}", use_container_width=True):
                    st.session_state.proyecto_en_edicion = idx
                    st.session_state.edit_departamentos = proyecto.departamentos.copy()
                    st.session_state.edit_municipios = proyecto.municipios.copy() if proyecto.municipios else []
                    st.rerun()

            with col_delete:
                if st.button(f"🗑️ Eliminar", key=f"delete_btn_{idx}", type="secondary", use_container_width=True):
                    proyecto_eliminado = st.session_state.proyectos.pop(idx)
                    st.success(f"✅ Proyecto '{proyecto_eliminado.nombre}' eliminado")
                    st.rerun()
