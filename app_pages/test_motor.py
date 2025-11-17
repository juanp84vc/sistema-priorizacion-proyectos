"""Página de prueba para validar Motor Arquitectura C."""
import streamlit as st
import sys
from pathlib import Path

# Agregar src al path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models.proyecto import ProyectoSocial, AreaGeografica
from scoring.motor_arquitectura_c import (
    MotorScoringArquitecturaC,
    calcular_score_proyecto
)


def show():
    """Muestra la página de prueba del motor."""
    st.markdown("<h1 class='main-header'>🧪 Test Motor Arquitectura C</h1>",
                unsafe_allow_html=True)
    st.markdown("---")

    st.info("""
    **Propósito:** Validar que el Motor de Scoring Arquitectura C está funcionando correctamente.

    **Arquitectura C:**
    - SROI: 40% (dominante)
    - Stakeholders: 25%
    - Probabilidad Aprobación: 20%
    - Riesgos: 15%

    **Total:** 100% ✅
    """)

    st.markdown("---")

    # Tabs para diferentes proyectos de prueba
    tab1, tab2, tab3 = st.tabs([
        "🟢 Proyecto Ideal",
        "🟡 Proyecto Promedio",
        "🔴 Proyecto Alto Riesgo"
    ])

    with tab1:
        st.subheader("Proyecto Ideal: Alto SROI + PDET + Bajo Riesgo")

        proyecto_ideal = ProyectoSocial(
            id="TEST-IDEAL-001",
            nombre="Acueducto Rural Comunitario - Zona PDET",
            organizacion="Aguas para Todos",
            descripcion="Construcción de acueducto comunitario en zona rural PDET",
            presupuesto_total=450_000_000,
            beneficiarios_directos=2500,
            beneficiarios_indirectos=10000,
            duracion_meses=18,
            ods_vinculados=["ODS 6", "ODS 3"],
            area_geografica=AreaGeografica.RURAL,
            poblacion_objetivo="Comunidades rurales",
            departamentos=["ANTIOQUIA"],
            municipios=["ABEJORRAL"],
            sectores=["alcantarillado"],

            # SROI excelente
            indicadores_impacto={'sroi': 4.8},

            # PDET
            tiene_municipios_pdet=True,
            puntajes_pdet={"alcantarillado": 10},
            puntaje_sectorial_max=10,

            # Stakeholders: Alta pertinencia
            pertinencia_operacional=5,
            mejora_relacionamiento=5,
            en_corredor_transmision=True,
            stakeholders_involucrados=[
                'autoridades_locales',
                'lideres_comunitarios',
                'comunidades_indigenas'
            ],

            # Riesgos: Muy bajos
            riesgo_tecnico_probabilidad=1,
            riesgo_tecnico_impacto=2,
            riesgo_social_probabilidad=1,
            riesgo_social_impacto=1,
            riesgo_financiero_probabilidad=2,
            riesgo_financiero_impacto=2,
            riesgo_regulatorio_probabilidad=1,
            riesgo_regulatorio_impacto=1,
            duracion_estimada_meses=18
        )

        if st.button("🚀 Calcular Score - Proyecto Ideal", key="btn_ideal"):
            with st.spinner("Calculando score..."):
                motor = MotorScoringArquitecturaC()
                resultado = motor.calcular_score(proyecto_ideal, detallado=True)

                mostrar_resultado(resultado)

    with tab2:
        st.subheader("Proyecto Promedio: Buen SROI + NO-PDET + Riesgo Medio")

        proyecto_promedio = ProyectoSocial(
            id="TEST-PROM-001",
            nombre="Educación Urbana",
            organizacion="Educación para Todos",
            descripcion="Programa educativo en zona urbana",
            presupuesto_total=300_000_000,
            beneficiarios_directos=1500,
            beneficiarios_indirectos=5000,
            duracion_meses=24,
            ods_vinculados=["ODS 4"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Estudiantes urbanos",
            departamentos=["CUNDINAMARCA"],
            municipios=["BOGOTÁ"],

            # SROI bueno
            indicadores_impacto={'sroi': 3.2},

            # NO PDET
            tiene_municipios_pdet=False,

            # Stakeholders medios
            pertinencia_operacional=3,
            mejora_relacionamiento=4,
            stakeholders_involucrados=['autoridades_locales', 'academia'],

            # Riesgos moderados
            riesgo_tecnico_probabilidad=2,
            riesgo_tecnico_impacto=3,
            riesgo_social_probabilidad=2,
            riesgo_social_impacto=2,
            riesgo_financiero_probabilidad=3,
            riesgo_financiero_impacto=3,
            riesgo_regulatorio_probabilidad=2,
            riesgo_regulatorio_impacto=2,
            duracion_estimada_meses=24
        )

        if st.button("🚀 Calcular Score - Proyecto Promedio", key="btn_promedio"):
            with st.spinner("Calculando score..."):
                motor = MotorScoringArquitecturaC()
                resultado = motor.calcular_score(proyecto_promedio, detallado=True)

                mostrar_resultado(resultado)

    with tab3:
        st.subheader("Proyecto Alto Riesgo: SROI Medio + Riesgos Críticos")

        proyecto_riesgo = ProyectoSocial(
            id="TEST-RISK-001",
            nombre="Megaproyecto de Infraestructura",
            organizacion="Constructor S.A.",
            descripcion="Proyecto complejo con muchos riesgos",
            presupuesto_total=2_000_000_000,  # 2B - penalización
            beneficiarios_directos=5000,
            beneficiarios_indirectos=20000,
            duracion_meses=48,  # 4 años - penalización
            ods_vinculados=["ODS 9"],
            area_geografica=AreaGeografica.NACIONAL,
            poblacion_objetivo="Población nacional",
            departamentos=["ANTIOQUIA", "CUNDINAMARCA", "VALLE DEL CAUCA"],
            municipios=["MEDELLÍN", "BOGOTÁ", "CALI"],
            sectores=["via"],

            # SROI medio
            indicadores_impacto={'sroi': 2.8},

            # PDET
            tiene_municipios_pdet=True,
            puntajes_pdet={"via": 8},
            puntaje_sectorial_max=8,

            # Stakeholders
            pertinencia_operacional=4,
            mejora_relacionamiento=3,
            en_corredor_transmision=True,

            # Riesgos CRÍTICOS
            riesgo_tecnico_probabilidad=5,
            riesgo_tecnico_impacto=5,  # Nivel 25 - CRÍTICO
            riesgo_social_probabilidad=4,
            riesgo_social_impacto=5,  # Nivel 20 - CRÍTICO
            riesgo_financiero_probabilidad=5,
            riesgo_financiero_impacto=4,  # Nivel 20 - CRÍTICO
            riesgo_regulatorio_probabilidad=4,
            riesgo_regulatorio_impacto=4,  # Nivel 16 - ALTO
            duracion_estimada_meses=48
        )

        if st.button("🚀 Calcular Score - Proyecto Alto Riesgo", key="btn_riesgo"):
            with st.spinner("Calculando score..."):
                motor = MotorScoringArquitecturaC()
                resultado = motor.calcular_score(proyecto_riesgo, detallado=True)

                mostrar_resultado(resultado)

    # Sección de prueba personalizada
    st.markdown("---")
    st.subheader("🎛️ Prueba Personalizada")

    with st.expander("Crear proyecto personalizado"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Datos Básicos**")
            nombre_custom = st.text_input("Nombre proyecto", "Mi Proyecto Custom")
            presupuesto_custom = st.number_input("Presupuesto ($)", min_value=1_000_000, value=500_000_000, step=10_000_000)
            beneficiarios_custom = st.number_input("Beneficiarios directos", min_value=10, value=1000, step=100)

            st.write("**SROI (40%)**")
            sroi_custom = st.slider("SROI", 0.5, 10.0, 3.5, 0.1)

            st.write("**Stakeholders (25%)**")
            pertinencia_custom = st.select_slider(
                "Pertinencia Operacional",
                options=[1, 2, 3, 4, 5],
                value=3
            )
            relacionamiento_custom = st.select_slider(
                "Mejora Relacionamiento",
                options=[1, 2, 3, 4, 5],
                value=3
            )

        with col2:
            st.write("**Probabilidad (20%)**")
            es_pdet_custom = st.checkbox("Municipio PDET", value=False)

            st.write("**Riesgos (15%)**")
            st.caption("Nivel = Probabilidad × Impacto")

            col_r1, col_r2 = st.columns(2)
            with col_r1:
                riesgo_tec_prob = st.slider("Técnico - Prob.", 1, 5, 2)
                riesgo_soc_prob = st.slider("Social - Prob.", 1, 5, 2)
            with col_r2:
                riesgo_tec_imp = st.slider("Técnico - Imp.", 1, 5, 2)
                riesgo_soc_imp = st.slider("Social - Imp.", 1, 5, 2)

            col_r3, col_r4 = st.columns(2)
            with col_r3:
                riesgo_fin_prob = st.slider("Financiero - Prob.", 1, 5, 2)
                riesgo_reg_prob = st.slider("Regulatorio - Prob.", 1, 5, 2)
            with col_r4:
                riesgo_fin_imp = st.slider("Financiero - Imp.", 1, 5, 2)
                riesgo_reg_imp = st.slider("Regulatorio - Imp.", 1, 5, 2)

        if st.button("🚀 Calcular Score - Custom", type="primary"):
            proyecto_custom = ProyectoSocial(
                id="TEST-CUSTOM-001",
                nombre=nombre_custom,
                organizacion="Test Org",
                descripcion="Proyecto de prueba personalizado",
                presupuesto_total=presupuesto_custom,
                beneficiarios_directos=beneficiarios_custom,
                beneficiarios_indirectos=beneficiarios_custom * 3,
                duracion_meses=12,
                ods_vinculados=["ODS 1"],
                area_geografica=AreaGeografica.URBANA,
                poblacion_objetivo="Test",
                departamentos=["ANTIOQUIA"],
                municipios=["ABEJORRAL" if es_pdet_custom else "BOGOTÁ"],

                # SROI
                indicadores_impacto={'sroi': sroi_custom},

                # PDET
                tiene_municipios_pdet=es_pdet_custom,
                puntajes_pdet={"alcantarillado": 10} if es_pdet_custom else {},
                puntaje_sectorial_max=10 if es_pdet_custom else 0,

                # Stakeholders
                pertinencia_operacional=pertinencia_custom,
                mejora_relacionamiento=relacionamiento_custom,
                stakeholders_involucrados=['autoridades_locales'],

                # Riesgos
                riesgo_tecnico_probabilidad=riesgo_tec_prob,
                riesgo_tecnico_impacto=riesgo_tec_imp,
                riesgo_social_probabilidad=riesgo_soc_prob,
                riesgo_social_impacto=riesgo_soc_imp,
                riesgo_financiero_probabilidad=riesgo_fin_prob,
                riesgo_financiero_impacto=riesgo_fin_imp,
                riesgo_regulatorio_probabilidad=riesgo_reg_prob,
                riesgo_regulatorio_impacto=riesgo_reg_imp,
                duracion_estimada_meses=12
            )

            with st.spinner("Calculando score..."):
                motor = MotorScoringArquitecturaC()
                resultado = motor.calcular_score(proyecto_custom, detallado=True)

                mostrar_resultado(resultado)


def mostrar_resultado(resultado):
    """Muestra el resultado del scoring de forma visual."""

    # Header con score total
    score_color = "#22c55e" if resultado.score_total >= 80 else "#eab308" if resultado.score_total >= 60 else "#ef4444"

    st.markdown(f"""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px; margin: 20px 0;'>
        <h2 style='color: white; margin: 0;'>SCORE TOTAL</h2>
        <h1 style='color: white; font-size: 5em; margin: 10px 0;'>{resultado.score_total:.1f}</h1>
        <h3 style='color: white; margin: 0;'>{resultado.nivel_prioridad}</h3>
    </div>
    """, unsafe_allow_html=True)

    # Desglose por criterio
    st.subheader("📊 Desglose por Criterio (Arquitectura C)")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "SROI (40%)",
            f"{resultado.score_sroi:.0f}/100",
            f"{resultado.contribucion_sroi:.1f} pts",
            help="Social Return on Investment - Criterio dominante"
        )
        st.progress(resultado.score_sroi / 100)

    with col2:
        st.metric(
            "Stakeholders (25%)",
            f"{resultado.score_stakeholders:.0f}/100",
            f"{resultado.contribucion_stakeholders:.1f} pts",
            help="Pertinencia operacional y relacionamiento"
        )
        st.progress(resultado.score_stakeholders / 100)

    with col3:
        st.metric(
            "Probabilidad (20%)",
            f"{resultado.score_probabilidad:.0f}/100",
            f"{resultado.contribucion_probabilidad:.1f} pts",
            help="Probabilidad de aprobación (PDET/ZOMAC)"
        )
        st.progress(resultado.score_probabilidad / 100)

    with col4:
        st.metric(
            "Riesgos (15%)",
            f"{resultado.score_riesgos:.0f}/100",
            f"{resultado.contribucion_riesgos:.1f} pts",
            help="Evaluación de riesgos (scoring inverso)"
        )
        st.progress(resultado.score_riesgos / 100)

    # Validación de suma
    st.markdown("---")
    suma_contribuciones = (
        resultado.contribucion_sroi +
        resultado.contribucion_stakeholders +
        resultado.contribucion_probabilidad +
        resultado.contribucion_riesgos
    )

    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        st.metric("Suma Contribuciones", f"{suma_contribuciones:.2f}")
    with col_v2:
        st.metric("Score Total", f"{resultado.score_total:.2f}")
    with col_v3:
        diferencia = abs(suma_contribuciones - resultado.score_total)
        st.metric("Diferencia", f"{diferencia:.4f}",
                 delta="✅ OK" if diferencia < 0.01 else "❌ ERROR")

    # Alertas
    if resultado.alertas:
        st.markdown("### ⚠️ Alertas")
        for alerta in resultado.alertas:
            if "RECHAZADO" in alerta or "🚫" in alerta:
                st.error(alerta)
            elif "⚠️" in alerta:
                st.warning(alerta)
            else:
                st.info(alerta)

    # Recomendaciones
    if resultado.recomendaciones:
        st.markdown("### 💡 Recomendaciones")
        for rec in resultado.recomendaciones:
            if "✅" in rec:
                st.success(rec)
            else:
                st.info(rec)

    # Detalles técnicos
    with st.expander("🔍 Detalles Técnicos"):
        st.json({
            "score_total": resultado.score_total,
            "nivel_prioridad": resultado.nivel_prioridad,
            "scores_individuales": {
                "sroi": resultado.score_sroi,
                "stakeholders": resultado.score_stakeholders,
                "probabilidad": resultado.score_probabilidad,
                "riesgos": resultado.score_riesgos
            },
            "contribuciones": {
                "sroi_40pct": resultado.contribucion_sroi,
                "stakeholders_25pct": resultado.contribucion_stakeholders,
                "probabilidad_20pct": resultado.contribucion_probabilidad,
                "riesgos_15pct": resultado.contribucion_riesgos
            },
            "metadata": {
                "version_arquitectura": resultado.version_arquitectura,
                "fecha_calculo": resultado.fecha_calculo.isoformat()
            }
        })
