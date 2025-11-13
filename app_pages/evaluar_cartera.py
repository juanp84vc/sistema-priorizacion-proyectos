"""Página para evaluar y priorizar cartera de proyectos."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Agregar src al path si no está
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from criterios import (
    CostoEfectividadCriterio,
    ContribucionStakeholdersCriterio,
    ProbabilidadAprobacionCriterio,
    RiesgosCriterio
)
from estrategias import ScoringPonderado, ScoringUmbral
from servicios import SistemaPriorizacionProyectos, ExportadorResultados, RecomendadorProyectos


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
    """Muestra la página de evaluación de cartera."""
    st.markdown("<h1 class='main-header'>📊 Evaluar Cartera de Proyectos</h1>",
                unsafe_allow_html=True)
    st.markdown("---")

    # Verificar que hay proyectos
    if len(st.session_state.proyectos) == 0:
        st.warning("⚠️ No hay proyectos registrados. Ve a 'Nuevo Proyecto' para agregar proyectos.")
        return

    # Configuración de evaluación
    st.markdown("### ⚙️ Configuración de Evaluación")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Selección de proyectos
        st.markdown("#### Selecciona proyectos a evaluar")

        todos_proyectos = {f"{p.id} - {p.nombre}": p for p in st.session_state.proyectos}

        proyectos_seleccionados = st.multiselect(
            "Proyectos",
            options=list(todos_proyectos.keys()),
            default=list(todos_proyectos.keys()),
            label_visibility="collapsed"
        )

    with col2:
        # Estrategia
        estrategia_tipo = st.selectbox(
            "Estrategia de Evaluación",
            options=["Scoring Ponderado", "Scoring con Umbrales"]
        )

    # Configuración de criterios
    st.markdown("#### 🎯 Pesos de Criterios")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        peso_costo = st.slider(
            "Costo-Efectividad",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['costo_efectividad'],
            step=0.05
        )

    with col2:
        peso_stakeholders = st.slider(
            "Stakeholders",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['stakeholders'],
            step=0.05
        )

    with col3:
        peso_probabilidad = st.slider(
            "Prob. Aprobación",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['probabilidad_aprobacion'],
            step=0.05
        )

    with col4:
        peso_riesgos = st.slider(
            "Riesgos",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['riesgos'],
            step=0.05
        )

    # Validar suma de pesos
    suma_pesos = peso_costo + peso_stakeholders + peso_probabilidad + peso_riesgos

    if abs(suma_pesos - 1.0) > 0.01:
        st.error(f"❌ La suma de pesos debe ser 1.0. Actual: {suma_pesos:.2f}")
        return

    st.success(f"✅ Suma de pesos: {suma_pesos:.2f}")

    # Configuración de umbrales (si aplica)
    umbrales = None
    if estrategia_tipo == "Scoring con Umbrales":
        with st.expander("🎯 Configurar Umbrales Mínimos"):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                umbral_costo = st.number_input(
                    "Costo-Efectividad",
                    min_value=0.0,
                    max_value=100.0,
                    value=40.0,
                    step=5.0
                )

            with col2:
                umbral_stakeholders = st.number_input(
                    "Stakeholders",
                    min_value=0.0,
                    max_value=100.0,
                    value=35.0,
                    step=5.0
                )

            with col3:
                umbral_probabilidad = st.number_input(
                    "Prob. Aprobación",
                    min_value=0.0,
                    max_value=100.0,
                    value=45.0,
                    step=5.0
                )

            with col4:
                umbral_riesgos = st.number_input(
                    "Riesgos",
                    min_value=0.0,
                    max_value=100.0,
                    value=60.0,
                    step=5.0
                )

            umbrales = {
                "Relación Costo-Efectividad": umbral_costo,
                "Contribución al Relacionamiento con Stakeholders": umbral_stakeholders,
                "Probabilidad de Aprobación Gubernamental": umbral_probabilidad,
                "Evaluación de Riesgos": umbral_riesgos
            }

    # Botón evaluar
    st.markdown("---")

    if st.button("🚀 Evaluar Proyectos", type="primary", use_container_width=True):
        if not proyectos_seleccionados:
            st.warning("Selecciona al menos un proyecto")
            return

        # Crear criterios
        criterios = [
            CostoEfectividadCriterio(peso=peso_costo),
            ContribucionStakeholdersCriterio(peso=peso_stakeholders),
            ProbabilidadAprobacionCriterio(peso=peso_probabilidad),
            RiesgosCriterio(peso=peso_riesgos)
        ]

        # Crear estrategia
        if estrategia_tipo == "Scoring Ponderado":
            estrategia = ScoringPonderado()
        else:
            estrategia = ScoringUmbral(umbrales_minimos=umbrales)

        # Crear sistema
        sistema = SistemaPriorizacionProyectos(
            criterios=criterios,
            estrategia=estrategia
        )

        # Evaluar proyectos seleccionados
        proyectos_eval = [todos_proyectos[key] for key in proyectos_seleccionados]

        with st.spinner("Evaluando proyectos..."):
            reporte = sistema.generar_reporte(proyectos_eval)

        # Mostrar resultados
        st.markdown("---")
        st.markdown("## 📈 Resultados de Evaluación")

        # Métricas resumen
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Proyectos Evaluados",
                reporte['total_proyectos']
            )

        with col2:
            st.metric(
                "Score Máximo",
                formatear_numero(reporte['estadisticas']['score_maximo'], 1)
            )

        with col3:
            st.metric(
                "Score Promedio",
                formatear_numero(reporte['estadisticas']['score_promedio'], 1)
            )

        with col4:
            st.metric(
                "Alta Prioridad",
                reporte['estadisticas']['proyectos_alta_prioridad']
            )

        # Ranking
        st.markdown("### 🏆 Ranking de Proyectos")

        # Crear DataFrame
        df_ranking = pd.DataFrame(reporte['ranking'])

        # Agregar colores según score
        def score_color(score):
            if score >= 80:
                return '🟢'
            elif score >= 60:
                return '🟡'
            else:
                return '🔴'

        df_ranking['Indicador'] = df_ranking['score'].apply(score_color)

        # Formatear score para visualización
        df_ranking_display = df_ranking.copy()
        df_ranking_display['score_formateado'] = df_ranking_display['score'].apply(lambda x: formatear_numero(x, 2))

        # Mostrar tabla
        st.dataframe(
            df_ranking_display[['Indicador', 'posicion', 'proyecto_nombre', 'score_formateado', 'recomendacion']],
            column_config={
                "Indicador": st.column_config.TextColumn(""),
                "posicion": st.column_config.NumberColumn("Posición", format="%d"),
                "proyecto_nombre": st.column_config.TextColumn("Proyecto"),
                "score_formateado": st.column_config.TextColumn("Score"),
                "recomendacion": st.column_config.TextColumn("Recomendación")
            },
            hide_index=True,
            use_container_width=True
        )

        # Gráfico de barras
        fig = px.bar(
            df_ranking,
            x='proyecto_nombre',
            y='score',
            color='score',
            color_continuous_scale='RdYlGn',
            title='Scores por Proyecto',
            labels={'proyecto_nombre': 'Proyecto', 'score': 'Score'},
            text='score'
        )

        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(showlegend=False, height=500)

        st.plotly_chart(fig, use_container_width=True)

        # Detalles por proyecto
        st.markdown("### 📋 Detalles por Proyecto")

        # Evaluar cada proyecto para mostrar detalles
        resultados_detallados = [sistema.evaluar_proyecto(p) for p in proyectos_eval]

        for resultado in resultados_detallados:
            # Determinar color del score
            score_color = "🟢" if resultado.score_final >= 80 else "🟡" if resultado.score_final >= 60 else "🔴"

            with st.expander(f"{score_color} **{resultado.proyecto_nombre}** - Score: {formatear_numero(resultado.score_final)}"):
                # Header con score prominente
                col_header1, col_header2 = st.columns([1, 2])

                with col_header1:
                    # Score final grande y prominente
                    score_color_class = "#22c55e" if resultado.score_final >= 80 else "#eab308" if resultado.score_final >= 60 else "#ef4444"
                    st.markdown(f"""
                    <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
                        <h4 style='margin: 0; color: #4b5563;'>Puntaje Final</h4>
                        <h1 style='margin: 10px 0; color: {score_color_class}; font-size: 4em;'>{formatear_numero(resultado.score_final, 1)}</h1>
                        <p style='margin: 0; color: #6b7280;'>{resultado.recomendacion}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col_header2:
                    # Gráfico radar prominente
                    criterios_nombres = list(resultado.detalle_criterios.keys())
                    scores = [resultado.detalle_criterios[c]['score_base'] for c in criterios_nombres]

                    fig_radar = go.Figure()

                    fig_radar.add_trace(go.Scatterpolar(
                        r=scores,
                        theta=criterios_nombres,
                        fill='toself',
                        name=resultado.proyecto_nombre,
                        fillcolor='rgba(59, 130, 246, 0.5)',
                        line=dict(color='rgb(59, 130, 246)', width=2)
                    ))

                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100],
                                showticklabels=True,
                                ticks='outside'
                            )
                        ),
                        showlegend=False,
                        height=350,
                        margin=dict(l=80, r=80, t=40, b=40)
                    )

                    st.plotly_chart(fig_radar, use_container_width=True)

                st.markdown("---")

                # Desglose por criterio con mejor visualización
                st.markdown("#### 📊 Desglose Detallado por Criterio")

                for criterio, detalle in resultado.detalle_criterios.items():
                    col_a, col_b, col_c = st.columns([2, 1, 1])

                    with col_a:
                        # Barra de progreso visual
                        score_pct = detalle['score_base']
                        st.markdown(f"**{criterio}**")
                        st.progress(score_pct / 100)

                    with col_b:
                        st.metric(
                            "Score Base",
                            formatear_numero(detalle['score_base'], 1),
                            help=f"Score sin ponderar (0-100)"
                        )

                    with col_c:
                        st.metric(
                            f"Ponderado ({formatear_numero(detalle['peso'] * 100, 0)}%)",
                            formatear_numero(detalle['score_ponderado'], 2),
                            help=f"Score multiplicado por peso ({formatear_numero(detalle['peso'] * 100, 1)}%)"
                        )

                # Observaciones
                if resultado.observaciones:
                    st.markdown("---")
                    st.markdown("#### 💡 Observaciones")
                    for obs in resultado.observaciones:
                        st.info(f"• {obs}")

                # Recomendaciones para optimizar el proyecto
                st.markdown("---")
                st.markdown("#### 🎯 Estrategias de Optimización del Proyecto")

                # Obtener el proyecto completo
                proyecto_completo = next((p for p in proyectos_eval if p.id == resultado.proyecto_id), None)

                if proyecto_completo:
                    try:
                        # Crear recomendador
                        recomendador = RecomendadorProyectos()

                        # Verificar versión del módulo
                        if hasattr(recomendador, '__module__'):
                            import servicios.recomendador as rec_module
                            if hasattr(rec_module, '__version__'):
                                st.caption(f"🔧 Recomendador v{rec_module.__version__}")

                        # Generar recomendaciones
                        recomendaciones = recomendador.analizar_proyecto(
                            proyecto_completo,
                            resultado.detalle_criterios
                        )

                        # Score potencial
                        # Usar argumentos nombrados para evitar confusión
                        score_potencial, mensaje_potencial = recomendador.generar_score_potencial(
                            proyecto=proyecto_completo,
                            score_actual=resultado.score_final
                        )

                        # Mostrar score potencial
                        if score_potencial > resultado.score_final:
                            delta = score_potencial - resultado.score_final
                            col_pot1, col_pot2 = st.columns(2)

                            with col_pot1:
                                st.metric(
                                    "Score Actual",
                                    formatear_numero(resultado.score_final, 1)
                                )

                            with col_pot2:
                                st.metric(
                                    "Score Potencial",
                                    formatear_numero(score_potencial, 1),
                                    delta=f"+{formatear_numero(delta, 1)}",
                                    delta_color="normal"
                                )

                            st.info(f"💡 {mensaje_potencial}")
                        else:
                            st.success(mensaje_potencial)

                        st.markdown("")

                        # Tabs para categorías de recomendaciones
                        if any(recomendaciones.values()):
                            tabs_labels = []
                            tabs_content = []

                            if recomendaciones['criticas']:
                                tabs_labels.append("🔴 Críticas")
                                tabs_content.append(recomendaciones['criticas'])

                            if recomendaciones['importantes']:
                                tabs_labels.append("🟡 Importantes")
                                tabs_content.append(recomendaciones['importantes'])

                            if recomendaciones['opcionales']:
                                tabs_labels.append("🟢 Opcionales")
                                tabs_content.append(recomendaciones['opcionales'])

                            if recomendaciones['fortalezas']:
                                tabs_labels.append("✅ Fortalezas")
                                tabs_content.append(recomendaciones['fortalezas'])

                            if tabs_labels:
                                tabs = st.tabs(tabs_labels)

                                for i, (tab, content) in enumerate(zip(tabs, tabs_content)):
                                    with tab:
                                        for recomendacion in content:
                                            st.markdown(recomendacion)
                                            st.markdown("")
                        else:
                            st.info("No hay recomendaciones específicas para este proyecto.")

                    except Exception as e:
                        st.error(f"❌ Error al generar recomendaciones: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())

        # Botón para exportar
        st.markdown("---")
        st.markdown("### 📥 Exportar Resultados")

        # Crear exportador con los datos
        exportador = ExportadorResultados(reporte, resultados_detallados)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Exportar a CSV
            try:
                csv_data = exportador.exportar_csv()
                st.download_button(
                    label="📄 CSV",
                    data=csv_data,
                    file_name="evaluacion_proyectos.csv",
                    mime="text/csv",
                    use_container_width=True,
                    help="Descarga un archivo CSV con el ranking"
                )
            except Exception as e:
                st.error(f"Error al generar CSV: {str(e)}")

        with col2:
            # Exportar a Excel
            try:
                excel_data = exportador.exportar_excel()
                st.download_button(
                    label="📊 Excel",
                    data=excel_data,
                    file_name="evaluacion_proyectos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    help="Descarga un archivo Excel con múltiples hojas"
                )
            except Exception as e:
                st.error(f"Error al generar Excel: {str(e)}")

        with col3:
            # Exportar a Word
            try:
                word_data = exportador.exportar_word()
                st.download_button(
                    label="📝 Word",
                    data=word_data,
                    file_name="evaluacion_proyectos.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    help="Descarga un reporte en formato Word"
                )
            except Exception as e:
                st.error(f"Error al generar Word: {str(e)}")

        with col4:
            # Exportar a PDF
            try:
                pdf_data = exportador.exportar_pdf()
                st.download_button(
                    label="📑 PDF",
                    data=pdf_data,
                    file_name="evaluacion_proyectos.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    help="Descarga un reporte en formato PDF"
                )
            except Exception as e:
                st.error(f"Error al generar PDF: {str(e)}")
