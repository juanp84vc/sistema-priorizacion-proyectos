"""
Página para crear nuevos proyectos con Arquitectura C completa.
Incluye matriz PDET de 362 municipios y cálculo automático de score.
"""
import streamlit as st
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Agregar src al path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Imports del modelo
from models.proyecto import ProyectoSocial, AreaGeografica

# Motor de scoring Arquitectura C
from scoring.motor_arquitectura_c import calcular_score_proyecto

# Repositorio PDET
from database.matriz_pdet_repository import MatrizPDETRepository

# Database manager
from database.db_manager import get_db_manager


# ============================================================================
# INICIALIZACION
# ============================================================================

@st.cache_resource
def get_pdet_repository():
    """Obtiene instancia del repositorio PDET (cached)"""
    return MatrizPDETRepository()


@st.cache_resource
def get_db():
    """Obtiene instancia del database manager (cached)"""
    return get_db_manager()


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def limpiar_session_state():
    """Limpia los datos del formulario del session state"""
    keys_to_delete = [
        'datos_basicos',
        'criterios',
        'ultimo_resultado',
        'ultimo_proyecto',
        # Campos del formulario
        'form_nombre',
        'form_organizacion',
        'form_presupuesto',
        'form_beneficiarios_directos',
        'form_beneficiarios_indirectos',
        'form_duracion',
        'form_descripcion',
        'form_departamento',
        'form_municipio'
    ]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]


def formatear_numero(numero: float, decimales: int = 2) -> str:
    """Formatea número con separadores de miles"""
    if numero is None:
        return "0"
    return f"{numero:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ============================================================================
# SECCION 1: DATOS BASICOS
# ============================================================================

def seccion_datos_basicos() -> Optional[Dict]:
    """Sección de datos básicos del proyecto - SIN FORM para permitir reactividad"""

    repo_pdet = get_pdet_repository()

    st.subheader("📋 Información General")

    st.markdown("Complete los datos básicos del proyecto. Los campos marcados con * son obligatorios.")

    # Inicializar session_state si no existe
    if 'form_nombre' not in st.session_state:
        st.session_state.form_nombre = ""
    if 'form_organizacion' not in st.session_state:
        st.session_state.form_organizacion = "ENLAZA GEB"
    if 'form_presupuesto' not in st.session_state:
        st.session_state.form_presupuesto = 500_000_000
    if 'form_beneficiarios_directos' not in st.session_state:
        st.session_state.form_beneficiarios_directos = 1000
    if 'form_beneficiarios_indirectos' not in st.session_state:
        st.session_state.form_beneficiarios_indirectos = 4000
    if 'form_duracion' not in st.session_state:
        st.session_state.form_duracion = 12
    if 'form_descripcion' not in st.session_state:
        st.session_state.form_descripcion = ""
    if 'form_departamento' not in st.session_state:
        st.session_state.form_departamento = "Seleccionar..."
    if 'form_municipio' not in st.session_state:
        st.session_state.form_municipio = "Seleccionar..."

    # Campos básicos
    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input(
            "Nombre del Proyecto *",
            value=st.session_state.form_nombre,
            placeholder="Ej: Alcantarillado Rural Abejorral",
            help="Nombre descriptivo del proyecto",
            key="input_nombre"
        )
        st.session_state.form_nombre = nombre

        organizacion = st.text_input(
            "Organización Ejecutora *",
            value=st.session_state.form_organizacion,
            help="Entidad responsable de ejecutar el proyecto",
            key="input_organizacion"
        )
        st.session_state.form_organizacion = organizacion

        presupuesto = st.number_input(
            "Presupuesto Total ($) *",
            min_value=0,
            value=st.session_state.form_presupuesto,
            step=10_000_000,
            format="%d",
            help="Presupuesto total en pesos colombianos",
            key="input_presupuesto"
        )
        st.session_state.form_presupuesto = presupuesto

    with col2:
        beneficiarios_directos = st.number_input(
            "Beneficiarios Directos *",
            min_value=0,
            value=st.session_state.form_beneficiarios_directos,
            step=100,
            help="Número de personas directamente beneficiadas",
            key="input_beneficiarios_directos"
        )
        st.session_state.form_beneficiarios_directos = beneficiarios_directos

        beneficiarios_indirectos = st.number_input(
            "Beneficiarios Indirectos",
            min_value=0,
            value=st.session_state.form_beneficiarios_indirectos,
            step=100,
            help="Número de personas indirectamente beneficiadas",
            key="input_beneficiarios_indirectos"
        )
        st.session_state.form_beneficiarios_indirectos = beneficiarios_indirectos

        duracion = st.number_input(
            "Duración Estimada (meses) *",
            min_value=1,
            max_value=60,
            value=st.session_state.form_duracion,
            help="Tiempo estimado de ejecución del proyecto",
            key="input_duracion"
        )
        st.session_state.form_duracion = duracion

    descripcion = st.text_area(
        "Descripción del Proyecto",
        value=st.session_state.form_descripcion,
        placeholder="Describa brevemente el proyecto, sus objetivos y alcance...",
        height=100,
        key="input_descripcion"
    )
    st.session_state.form_descripcion = descripcion

    st.markdown("---")
    st.subheader("📍 Ubicación")

    # Obtener lista de departamentos únicos
    departamentos_disponibles = repo_pdet.get_departamentos()

    col1, col2 = st.columns(2)

    with col1:
        # Calcular índice para el selector
        try:
            if st.session_state.form_departamento in departamentos_disponibles:
                dept_index = sorted(departamentos_disponibles).index(st.session_state.form_departamento) + 1
            else:
                dept_index = 0
        except:
            dept_index = 0

        departamento = st.selectbox(
            "Departamento *",
            options=["Seleccionar..."] + sorted(departamentos_disponibles),
            index=dept_index,
            help="Departamento donde se ejecutará el proyecto",
            key="input_departamento"
        )
        st.session_state.form_departamento = departamento

    with col2:
        # CLAVE: Ahora SÍ funciona porque NO está dentro de form
        if departamento and departamento != "Seleccionar...":
            # Obtener municipios del departamento seleccionado
            municipios_dpto = repo_pdet.get_municipios_por_departamento(departamento)

            municipio = st.selectbox(
                "Municipio *",
                options=["Seleccionar..."] + sorted(municipios_dpto),
                help="Municipio donde se ejecutará el proyecto",
                key="input_municipio"
            )
            st.session_state.form_municipio = municipio
        else:
            st.selectbox(
                "Municipio *",
                options=["Primero seleccione departamento"],
                disabled=True,
                key="input_municipio_disabled"
            )
            municipio = "Seleccionar..."
            st.session_state.form_municipio = municipio

    # Detectar automáticamente si es PDET
    es_pdet = False
    puntajes_sectores = {}

    if municipio and municipio != "Seleccionar...":
        es_pdet = repo_pdet.es_municipio_pdet(municipio, departamento)

        if es_pdet:
            st.success(f"✅ **{municipio}** es municipio PDET - Elegible para Obras por Impuestos")
            puntajes_sectores = repo_pdet.get_puntajes_sectores(municipio, departamento)

            # Mostrar sectores disponibles
            if puntajes_sectores:
                with st.expander("📋 Ver puntajes sectoriales PDET"):
                    sectores_ordenados = sorted(
                        puntajes_sectores.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    for sector, puntaje in sectores_ordenados:
                        st.write(f"- **{sector.title()}:** {puntaje}/10 {'⭐' * (puntaje // 2)}")
        else:
            st.warning(f"⚠️ **{municipio}** NO es municipio PDET")
            st.caption("Score Probabilidad de Aprobación = 0")

    st.markdown("---")

    # Botón para continuar (fuera de form)
    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("✅ Continuar a Criterios", type="primary", use_container_width=True):
            # Validar campos requeridos
            errores = []

            if not nombre or nombre.strip() == "":
                errores.append("El nombre del proyecto es requerido")
            if not organizacion or organizacion.strip() == "":
                errores.append("La organización es requerida")
            if presupuesto <= 0:
                errores.append("El presupuesto debe ser mayor a 0")
            if beneficiarios_directos <= 0:
                errores.append("Los beneficiarios directos deben ser mayor a 0")
            if departamento == "Seleccionar...":
                errores.append("Debe seleccionar un departamento")
            if municipio == "Seleccionar...":
                errores.append("Debe seleccionar un municipio")

            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                # Guardar en session_state
                st.session_state.datos_basicos = {
                    'nombre': nombre,
                    'organizacion': organizacion,
                    'descripcion': descripcion,
                    'presupuesto': presupuesto,
                    'beneficiarios_directos': beneficiarios_directos,
                    'beneficiarios_indirectos': beneficiarios_indirectos,
                    'duracion': duracion,
                    'departamento': departamento,
                    'municipio': municipio,
                    'es_pdet': es_pdet,
                    'puntajes_sectores': puntajes_sectores
                }

                st.success("✅ Datos básicos guardados. Continúe a la pestaña 'Criterios de Evaluación'")
                st.balloons()

    # Retornar datos si ya están en session_state
    return st.session_state.get('datos_basicos', None)


# ============================================================================
# SECCION 2: CRITERIOS DE EVALUACION
# ============================================================================

def seccion_criterios_evaluacion(datos_basicos: Dict) -> Optional[Dict]:
    """Sección de criterios de evaluación - 4 criterios de Arquitectura C"""

    st.markdown(f"""
    ### Proyecto: {datos_basicos['nombre']}
    **Municipio:** {datos_basicos['municipio']}, {datos_basicos['departamento']}
    **PDET:** {'✅ Sí' if datos_basicos['es_pdet'] else '❌ No'}
    """)

    st.markdown("---")

    # ========== CRITERIO 1: SROI (40%) ==========
    st.markdown("## 📊 Criterio 1: SROI - Social Return on Investment (40%)")

    st.markdown("""
    **SROI mide cuánto valor social se genera por cada peso invertido.**

    - SROI < 1.0: Destruye valor social ❌
    - SROI 1.0-2.0: Retorno bajo
    - SROI 2.0-3.0: Retorno medio
    - SROI ≥ 3.0: Retorno alto ✅
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        sroi = st.number_input(
            "SROI Estimado *",
            min_value=0.0,
            max_value=20.0,
            value=3.0,
            step=0.1,
            help="Valor social generado / Inversión realizada"
        )

    with col2:
        if sroi < 1.0:
            st.error("⚠️ SROI < 1.0\nDestruye valor")
        elif sroi < 2.0:
            st.warning("📊 Retorno Bajo")
        elif sroi < 3.0:
            st.info("📈 Retorno Medio")
        else:
            st.success("⭐ Retorno Alto")

    if sroi > 7.0:
        st.warning("⚠️ SROI muy alto (>7.0). Verifique metodología de cálculo.")

    st.markdown("---")

    # ========== CRITERIO 2: PROBABILIDAD APROBACION (20%) ==========
    st.markdown("## 🎯 Criterio 2: Probabilidad de Aprobación (20%)")

    sector_seleccionado = None
    puntaje_sector = 0

    if datos_basicos['es_pdet']:
        st.success("✅ Municipio PDET - Elegible para Obras por Impuestos")

        st.markdown("**Seleccione el sector del proyecto:**")
        st.caption("Los puntajes muestran la prioridad sectorial oficial del municipio (1-10)")

        sectores_disponibles = datos_basicos['puntajes_sectores']

        if sectores_disponibles:
            # Ordenar por puntaje descendente
            sectores_ordenados = sorted(
                sectores_disponibles.items(),
                key=lambda x: x[1],
                reverse=True
            )

            sector_seleccionado = st.radio(
                "Sector *",
                options=[s[0] for s in sectores_ordenados],
                format_func=lambda x: f"{x.title()} (⭐ {sectores_disponibles[x]}/10)",
                help="Sector con mayor puntaje tiene mayor probabilidad de aprobación"
            )

            puntaje_sector = sectores_disponibles[sector_seleccionado]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Sector", sector_seleccionado.title())
            with col2:
                st.metric("Puntaje Sectorial", f"{puntaje_sector}/10")
            with col3:
                score_prob = (puntaje_sector / 10) * 100
                st.metric("Score Probabilidad", f"{score_prob:.0f}/100")
        else:
            st.warning("No hay datos de puntajes sectoriales para este municipio PDET")
    else:
        st.error("❌ Municipio NO-PDET - NO elegible para Obras por Impuestos")
        st.caption("**Score Probabilidad de Aprobación = 0**")
        st.info("💡 El proyecto puede compensar con alto SROI y buen perfil de Stakeholders")

    st.markdown("---")

    # ========== CRITERIO 3: STAKEHOLDERS (25%) ==========
    st.markdown("## 🤝 Criterio 3: Stakeholders (25%)")

    st.markdown("""
    Evalúa el relacionamiento con stakeholders y la pertinencia operacional para ENLAZA.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Pertinencia Operacional/Reputacional**")
        st.caption("¿Qué tan crítico es para operaciones de ENLAZA?")

        pertinencia = st.select_slider(
            "Nivel de Pertinencia *",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: {
                1: "1 - Nula",
                2: "2 - Baja",
                3: "3 - Media",
                4: "4 - Alta",
                5: "5 - Muy Alta"
            }[x],
            help="Evalúa criticidad para licencia social y operaciones"
        )

        if pertinencia >= 4:
            st.info(f"{'⭐' if pertinencia == 5 else '📊'} Proyecto {'crítico' if pertinencia == 5 else 'importante'} para operaciones")

    with col2:
        st.markdown("**Mejora del Relacionamiento**")
        st.caption("¿Cómo mejora relación con stakeholders?")

        relacionamiento = st.select_slider(
            "Nivel de Mejora *",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: {
                1: "1 - No aporta",
                2: "2 - Limitado",
                3: "3 - Moderado",
                4: "4 - Confianza",
                5: "5 - Sustancial"
            }[x],
            help="Evalúa impacto en percepción de ENLAZA"
        )

        if relacionamiento >= 4:
            st.info(f"{'⭐' if relacionamiento == 5 else '📊'} Mejora {'sustancial' if relacionamiento == 5 else 'significativa'}")

    corredor = st.checkbox(
        "✅ Proyecto ubicado en corredor de transmisión",
        help="Proyecto en zona con líneas de transmisión actuales o futuras"
    )

    st.markdown("**Stakeholders Involucrados**")
    st.caption("Seleccione los tipos de stakeholders clave:")

    col1, col2 = st.columns(2)

    stakeholders = []
    with col1:
        if st.checkbox("Autoridades municipales/departamentales", value=True):
            stakeholders.append('autoridades_locales')
        if st.checkbox("Líderes comunitarios/JAC"):
            stakeholders.append('lideres_comunitarios')
        if st.checkbox("Comunidades indígenas/étnicas"):
            stakeholders.append('comunidades_indigenas')
        if st.checkbox("Organizaciones sociales locales"):
            stakeholders.append('organizaciones_sociales')

    with col2:
        if st.checkbox("Sector privado local"):
            stakeholders.append('sector_privado')
        if st.checkbox("Academia/instituciones educativas"):
            stakeholders.append('academia')
        if st.checkbox("Medios de comunicación"):
            stakeholders.append('medios_comunicacion')

    if stakeholders:
        st.success(f"✅ {len(stakeholders)} tipo(s) de stakeholders seleccionados")
    else:
        st.warning("⚠️ No se han seleccionado stakeholders")

    st.markdown("---")

    # ========== CRITERIO 4: RIESGOS (15%) ==========
    st.markdown("## ⚠️ Criterio 4: Evaluación de Riesgos (15%)")

    st.markdown("""
    Evalúa riesgos en 4 dimensiones. **Score INVERSO**: más riesgo = menos puntos

    **Nivel de Riesgo** = Probabilidad × Impacto
    - 1-5: BAJO 🟢
    - 6-12: MEDIO 🟡
    - 13-20: ALTO 🟠
    - 21-25: CRÍTICO 🔴
    """)

    with st.expander("ℹ️ Guía de Evaluación"):
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("""
            **Probabilidad (1-5):**
            - 1: Muy baja (< 10%)
            - 2: Baja (10-30%)
            - 3: Media (30-50%)
            - 4: Alta (50-70%)
            - 5: Muy alta (> 70%)
            """)
        with col_g2:
            st.markdown("""
            **Impacto (1-5):**
            - 1: Insignificante
            - 2: Menor
            - 3: Moderado
            - 4: Mayor
            - 5: Catastrófico
            """)

    # Riesgo Técnico
    st.markdown("**1. Riesgo Técnico/Operacional**")
    st.caption("Complejidad técnica, recursos, experiencia")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        riesgo_tec_prob = st.slider("Probabilidad", 1, 5, 2, key="tec_prob")
    with col2:
        riesgo_tec_imp = st.slider("Impacto", 1, 5, 2, key="tec_imp")
    with col3:
        nivel_tec = riesgo_tec_prob * riesgo_tec_imp
        color = "🟢" if nivel_tec <= 5 else "🟡" if nivel_tec <= 12 else "🟠" if nivel_tec <= 20 else "🔴"
        st.metric("Nivel", f"{color} {nivel_tec}")

    # Riesgo Social
    st.markdown("**2. Riesgo Social/Comunitario**")
    st.caption("Aceptación comunitaria, conflictos sociales")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        riesgo_soc_prob = st.slider("Probabilidad", 1, 5, 2, key="soc_prob")
    with col2:
        riesgo_soc_imp = st.slider("Impacto", 1, 5, 2, key="soc_imp")
    with col3:
        nivel_soc = riesgo_soc_prob * riesgo_soc_imp
        color = "🟢" if nivel_soc <= 5 else "🟡" if nivel_soc <= 12 else "🟠" if nivel_soc <= 20 else "🔴"
        st.metric("Nivel", f"{color} {nivel_soc}")

    # Riesgo Financiero
    st.markdown("**3. Riesgo Financiero/Presupuestario**")
    st.caption("Desviaciones presupuestarias, sobrecostos")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        riesgo_fin_prob = st.slider("Probabilidad", 1, 5, 2, key="fin_prob")
    with col2:
        riesgo_fin_imp = st.slider("Impacto", 1, 5, 3, key="fin_imp")
    with col3:
        nivel_fin = riesgo_fin_prob * riesgo_fin_imp
        color = "🟢" if nivel_fin <= 5 else "🟡" if nivel_fin <= 12 else "🟠" if nivel_fin <= 20 else "🔴"
        st.metric("Nivel", f"{color} {nivel_fin}")

    # Riesgo Regulatorio
    st.markdown("**4. Riesgo Regulatorio/Legal**")
    st.caption("Permisos, licencias, cambios regulatorios")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        riesgo_reg_prob = st.slider("Probabilidad", 1, 5, 2, key="reg_prob")
    with col2:
        riesgo_reg_imp = st.slider("Impacto", 1, 5, 2, key="reg_imp")
    with col3:
        nivel_reg = riesgo_reg_prob * riesgo_reg_imp
        color = "🟢" if nivel_reg <= 5 else "🟡" if nivel_reg <= 12 else "🟠" if nivel_reg <= 20 else "🔴"
        st.metric("Nivel", f"{color} {nivel_reg}")

    # Resumen riesgos
    max_nivel = max(nivel_tec, nivel_soc, nivel_fin, nivel_reg)
    if max_nivel >= 20:
        st.error("🔴 **Uno o más riesgos CRÍTICOS detectados**")
    elif max_nivel >= 13:
        st.warning("🟠 **Uno o más riesgos ALTOS detectados**")
    elif max_nivel >= 6:
        st.info("🟡 **Perfil de riesgo MEDIO**")
    else:
        st.success("🟢 **Perfil de riesgo BAJO**")

    st.markdown("---")

    # Botón guardar criterios
    if st.button("✅ Guardar Criterios y Continuar a Revisión", type="primary", use_container_width=True):
        st.session_state.criterios = {
            'sroi': sroi,
            'sector_seleccionado': sector_seleccionado,
            'puntaje_sector': puntaje_sector,
            'pertinencia': pertinencia,
            'relacionamiento': relacionamiento,
            'corredor': corredor,
            'stakeholders': stakeholders,
            'riesgo_tec_prob': riesgo_tec_prob,
            'riesgo_tec_imp': riesgo_tec_imp,
            'riesgo_soc_prob': riesgo_soc_prob,
            'riesgo_soc_imp': riesgo_soc_imp,
            'riesgo_fin_prob': riesgo_fin_prob,
            'riesgo_fin_imp': riesgo_fin_imp,
            'riesgo_reg_prob': riesgo_reg_prob,
            'riesgo_reg_imp': riesgo_reg_imp
        }

        st.success("✅ Criterios guardados. Continúe a la pestaña 'Revisión y Cálculo'")
        st.rerun()

    return st.session_state.get('criterios', None)


# ============================================================================
# SECCION 3: REVISION Y CALCULO
# ============================================================================

def seccion_revision_calculo(datos_basicos: Dict, criterios: Dict):
    """Revisión final y cálculo de score con Motor Arquitectura C"""

    st.markdown("## 📊 Revisión y Cálculo de Score")

    st.info("""
    Revise la información del proyecto antes de calcular el score.
    El cálculo utiliza el **Motor Arquitectura C** con los siguientes pesos:
    - SROI: 40% (dominante)
    - Stakeholders: 25%
    - Probabilidad Aprobación: 20%
    - Riesgos: 15%
    """)

    # Resumen
    st.markdown("### Resumen del Proyecto")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        **📋 Datos Básicos:**
        - **Nombre:** {datos_basicos['nombre']}
        - **Organización:** {datos_basicos['organizacion']}
        - **Presupuesto:** ${formatear_numero(datos_basicos['presupuesto'], 0)} COP
        - **Beneficiarios:** {formatear_numero(datos_basicos['beneficiarios_directos'], 0)} directos
        - **Duración:** {datos_basicos['duracion']} meses
        - **Ubicación:** {datos_basicos['municipio']}, {datos_basicos['departamento']}
        - **PDET:** {'✅ Sí' if datos_basicos['es_pdet'] else '❌ No'}
        """)

    with col2:
        st.markdown(f"""
        **🎯 Criterios:**

        **SROI (40%):** {criterios['sroi']:.2f}

        **Probabilidad (20%):**
        {criterios['sector_seleccionado'].title() if criterios['sector_seleccionado'] else 'N/A'} ({criterios['puntaje_sector']}/10)

        **Stakeholders (25%):**
        - Pertinencia: {criterios['pertinencia']}/5
        - Relacionamiento: {criterios['relacionamiento']}/5
        - Corredor: {'✅' if criterios['corredor'] else '❌'}
        - Tipos: {len(criterios['stakeholders'])}

        **Riesgos (15%):**
        - Técnico: {criterios['riesgo_tec_prob']}×{criterios['riesgo_tec_imp']}={criterios['riesgo_tec_prob']*criterios['riesgo_tec_imp']}
        - Social: {criterios['riesgo_soc_prob']}×{criterios['riesgo_soc_imp']}={criterios['riesgo_soc_prob']*criterios['riesgo_soc_imp']}
        - Financiero: {criterios['riesgo_fin_prob']}×{criterios['riesgo_fin_imp']}={criterios['riesgo_fin_prob']*criterios['riesgo_fin_imp']}
        - Regulatorio: {criterios['riesgo_reg_prob']}×{criterios['riesgo_reg_imp']}={criterios['riesgo_reg_prob']*criterios['riesgo_reg_imp']}
        """)

    st.markdown("---")

    # Botón calcular
    col1, col2 = st.columns([2, 1])

    with col1:
        calcular = st.button(
            "🚀 Calcular Score con Motor Arquitectura C",
            type="primary",
            use_container_width=True
        )

    with col2:
        if st.button("🔄 Editar Datos", use_container_width=True):
            st.info("Regrese a las pestañas anteriores para editar")

    if calcular:
        with st.spinner("Calculando score..."):
            # Crear ProyectoSocial con TODOS los campos requeridos
            proyecto = ProyectoSocial(
                # Campos requeridos
                id=str(uuid.uuid4()),
                ods_vinculados=[],  # TODO: Agregar selector de ODS en futuras versiones

                # Datos básicos
                nombre=datos_basicos['nombre'],
                organizacion=datos_basicos['organizacion'],
                descripcion=datos_basicos['descripcion'],
                presupuesto_total=datos_basicos['presupuesto'],
                beneficiarios_directos=datos_basicos['beneficiarios_directos'],
                beneficiarios_indirectos=datos_basicos['beneficiarios_indirectos'],
                duracion_estimada_meses=datos_basicos['duracion'],
                duracion_meses=datos_basicos['duracion'],

                # Ubicación
                departamentos=[datos_basicos['departamento']],
                municipios=[datos_basicos['municipio']],
                area_geografica=AreaGeografica.RURAL,
                poblacion_objetivo="Comunidad local",

                # SROI
                indicadores_impacto={'sroi': criterios['sroi']},

                # Probabilidad (PDET)
                tiene_municipios_pdet=datos_basicos['es_pdet'],
                puntajes_pdet={criterios['sector_seleccionado']: criterios['puntaje_sector']} if criterios['sector_seleccionado'] else {},
                puntaje_sectorial_max=criterios['puntaje_sector'],
                sectores=[criterios['sector_seleccionado']] if criterios['sector_seleccionado'] else [],

                # Stakeholders
                pertinencia_operacional=criterios['pertinencia'],
                mejora_relacionamiento=criterios['relacionamiento'],
                en_corredor_transmision=criterios['corredor'],
                stakeholders_involucrados=criterios['stakeholders'],

                # Riesgos
                riesgo_tecnico_probabilidad=criterios['riesgo_tec_prob'],
                riesgo_tecnico_impacto=criterios['riesgo_tec_imp'],
                riesgo_social_probabilidad=criterios['riesgo_soc_prob'],
                riesgo_social_impacto=criterios['riesgo_soc_imp'],
                riesgo_financiero_probabilidad=criterios['riesgo_fin_prob'],
                riesgo_financiero_impacto=criterios['riesgo_fin_imp'],
                riesgo_regulatorio_probabilidad=criterios['riesgo_reg_prob'],
                riesgo_regulatorio_impacto=criterios['riesgo_reg_imp']
            )

            # Calcular score
            resultado = calcular_score_proyecto(proyecto)

        # Guardar en session state
        st.session_state.ultimo_resultado = resultado
        st.session_state.ultimo_proyecto = proyecto

        # Mostrar resultado
        mostrar_resultado(resultado, proyecto, datos_basicos)


def mostrar_resultado(resultado, proyecto, datos_basicos):
    """Muestra el resultado del cálculo de score"""

    st.success("✅ Score calculado exitosamente")

    st.markdown("---")
    st.markdown("## 🎯 Resultado Final")

    # Score total con gradiente
    if resultado.score_total >= 85:
        color_bg = "#22c55e"
        emoji = "🟢"
    elif resultado.score_total >= 70:
        color_bg = "#eab308"
        emoji = "🟡"
    elif resultado.score_total >= 50:
        color_bg = "#f97316"
        emoji = "🟠"
    else:
        color_bg = "#ef4444"
        emoji = "🔴"

    st.markdown(f"""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, {color_bg} 0%, {color_bg}dd 100%);
                border-radius: 15px; margin: 20px 0;'>
        <h1 style='color: white; margin: 0; font-size: 4em;'>{emoji} {resultado.score_total:.1f}</h1>
        <h2 style='color: white; margin: 10px 0;'>{resultado.nivel_prioridad}</h2>
    </div>
    """, unsafe_allow_html=True)

    # Desglose
    st.markdown("### 📊 Desglose por Criterio (Arquitectura C)")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**SROI (40%)**")
        st.metric(
            "Score",
            f"{resultado.score_sroi:.0f}/100",
            delta=f"{resultado.contribucion_sroi:.1f} pts"
        )
        st.progress(resultado.score_sroi / 100)

    with col2:
        st.markdown("**Stakeholders (25%)**")
        st.metric(
            "Score",
            f"{resultado.score_stakeholders:.0f}/100",
            delta=f"{resultado.contribucion_stakeholders:.1f} pts"
        )
        st.progress(resultado.score_stakeholders / 100)

    with col3:
        st.markdown("**Probabilidad (20%)**")
        st.metric(
            "Score",
            f"{resultado.score_probabilidad:.0f}/100",
            delta=f"{resultado.contribucion_probabilidad:.1f} pts"
        )
        st.progress(resultado.score_probabilidad / 100)

    with col4:
        st.markdown("**Riesgos (15%)**")
        st.metric(
            "Score",
            f"{resultado.score_riesgos:.0f}/100",
            delta=f"{resultado.contribucion_riesgos:.1f} pts"
        )
        st.progress(resultado.score_riesgos / 100)

    # Validación aritmética
    suma = resultado.contribucion_sroi + resultado.contribucion_stakeholders + resultado.contribucion_probabilidad + resultado.contribucion_riesgos
    st.caption(f"✅ Validación: {resultado.contribucion_sroi:.1f} + {resultado.contribucion_stakeholders:.1f} + {resultado.contribucion_probabilidad:.1f} + {resultado.contribucion_riesgos:.1f} = {suma:.1f}/100")

    # Alertas
    if resultado.alertas:
        st.markdown("---")
        st.markdown("### 🔔 Alertas")
        for alerta in resultado.alertas:
            if "RECHAZADO" in alerta or "CRÍTICO" in alerta:
                st.error(alerta)
            elif "ALTO" in alerta or "⚠️" in alerta:
                st.warning(alerta)
            else:
                st.info(alerta)

    # Recomendaciones
    if resultado.recomendaciones:
        st.markdown("### 💡 Recomendaciones")
        for rec in resultado.recomendaciones:
            st.info(rec)

    # Botones de acción
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💾 Guardar Proyecto", type="primary", use_container_width=True):
            db = get_db()
            try:
                db.guardar_proyecto(proyecto)
                st.session_state.proyectos.append(proyecto)
                st.success("✅ Proyecto guardado en la base de datos")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error al guardar: {str(e)}")

    with col2:
        if st.button("🔄 Nuevo Proyecto", use_container_width=True):
            limpiar_session_state()
            st.rerun()

    with col3:
        if st.button("📊 Ver en Cartera", use_container_width=True):
            st.info("Navegue al menú 'Evaluar Cartera' para ver el proyecto")


# ============================================================================
# FUNCION PRINCIPAL
# ============================================================================

def show():
    """Función principal de la página"""

    st.markdown("<h1 class='main-header'>➕ Nuevo Proyecto con Arquitectura C</h1>",
                unsafe_allow_html=True)
    st.markdown("---")

    st.info("""
    **Sistema de Priorización - Arquitectura C**

    Complete los 3 pasos para registrar un proyecto y calcular su score de priorización:
    1. **Datos Básicos** - Información general y ubicación
    2. **Criterios de Evaluación** - SROI, Stakeholders, Probabilidad y Riesgos
    3. **Revisión y Cálculo** - Verificación final y cálculo automático de score
    """)

    # Tabs para organizar el formulario
    tab1, tab2, tab3 = st.tabs([
        "📋 Paso 1: Datos Básicos",
        "🎯 Paso 2: Criterios de Evaluación",
        "📊 Paso 3: Revisión y Cálculo"
    ])

    with tab1:
        datos_basicos = seccion_datos_basicos()

        if not datos_basicos:
            st.info("👆 Complete el formulario arriba para continuar")

    with tab2:
        datos_basicos = st.session_state.get('datos_basicos', None)

        if datos_basicos:
            criterios = seccion_criterios_evaluacion(datos_basicos)
        else:
            st.warning("⚠️ Primero complete el Paso 1: Datos Básicos")
            criterios = None

    with tab3:
        datos_basicos = st.session_state.get('datos_basicos', None)
        criterios = st.session_state.get('criterios', None)

        if datos_basicos and criterios:
            seccion_revision_calculo(datos_basicos, criterios)
        else:
            st.warning("⚠️ Complete los pasos anteriores primero")
            if not datos_basicos:
                st.error("❌ Falta: Datos Básicos")
            if not criterios:
                st.error("❌ Falta: Criterios de Evaluación")

    # Botón para limpiar todo
    st.markdown("---")
    if st.button("🗑️ Limpiar Todo y Empezar de Nuevo"):
        limpiar_session_state()
        st.rerun()
