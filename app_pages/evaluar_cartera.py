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
    ImpactoSocialCriterio,
    SostenibilidadFinancieraCriterio,
    AlineacionODSCriterio,
    CapacidadOrganizacionalCriterio
)
from estrategias import ScoringPonderado, ScoringUmbral
from servicios import SistemaPriorizacionProyectos, ExportadorResultados


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
        peso_impacto = st.slider(
            "Impacto Social",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['impacto_social'],
            step=0.05
        )

    with col2:
        peso_sostenibilidad = st.slider(
            "Sostenibilidad",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['sostenibilidad'],
            step=0.05
        )

    with col3:
        peso_ods = st.slider(
            "Alineación ODS",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['alineacion_ods'],
            step=0.05
        )

    with col4:
        peso_capacidad = st.slider(
            "Capacidad Org.",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.configuracion['criterios']['capacidad_org'],
            step=0.05
        )

    # Validar suma de pesos
    suma_pesos = peso_impacto + peso_sostenibilidad + peso_ods + peso_capacidad

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
                umbral_impacto = st.number_input(
                    "Impacto Social",
                    min_value=0.0,
                    max_value=100.0,
                    value=35.0,
                    step=5.0
                )

            with col2:
                umbral_sostenibilidad = st.number_input(
                    "Sostenibilidad",
                    min_value=0.0,
                    max_value=100.0,
                    value=40.0,
                    step=5.0
                )

            with col3:
                umbral_ods = st.number_input(
                    "Alineación ODS",
                    min_value=0.0,
                    max_value=100.0,
                    value=30.0,
                    step=5.0
                )

            with col4:
                umbral_capacidad = st.number_input(
                    "Capacidad Org.",
                    min_value=0.0,
                    max_value=100.0,
                    value=35.0,
                    step=5.0
                )

            umbrales = {
                "Impacto Social": umbral_impacto,
                "Sostenibilidad Financiera": umbral_sostenibilidad,
                "Alineación ODS": umbral_ods,
                "Capacidad Organizacional": umbral_capacidad
            }

    # Botón evaluar
    st.markdown("---")

    if st.button("🚀 Evaluar Proyectos", type="primary", use_container_width=True):
        if not proyectos_seleccionados:
            st.warning("Selecciona al menos un proyecto")
            return

        # Crear criterios
        criterios = [
            ImpactoSocialCriterio(peso=peso_impacto),
            SostenibilidadFinancieraCriterio(peso=peso_sostenibilidad),
            AlineacionODSCriterio(
                ods_prioritarios=st.session_state.configuracion['ods_prioritarios'],
                peso=peso_ods
            ),
            CapacidadOrganizacionalCriterio(peso=peso_capacidad)
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
            with st.expander(f"**{resultado.proyecto_nombre}** - Score: {formatear_numero(resultado.score_final)}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Recomendación:** {resultado.recomendacion}")

                    # Desglose por criterio
                    st.markdown("**Desglose por Criterio:**")

                    for criterio, detalle in resultado.detalle_criterios.items():
                        col_a, col_b, col_c = st.columns(3)

                        with col_a:
                            st.metric(
                                criterio,
                                formatear_numero(detalle['score_base'], 1)
                            )

                        with col_b:
                            st.caption(f"Peso: {formatear_numero(detalle['peso'] * 100, 1)}%")

                        with col_c:
                            st.caption(f"Ponderado: {formatear_numero(detalle['score_ponderado'])}")

                with col2:
                    # Gráfico radar del proyecto
                    criterios_nombres = list(resultado.detalle_criterios.keys())
                    scores = [resultado.detalle_criterios[c]['score_base'] for c in criterios_nombres]

                    fig_radar = go.Figure()

                    fig_radar.add_trace(go.Scatterpolar(
                        r=scores,
                        theta=criterios_nombres,
                        fill='toself',
                        name=resultado.proyecto_nombre
                    ))

                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        showlegend=False,
                        height=300
                    )

                    st.plotly_chart(fig_radar, use_container_width=True)

                # Observaciones
                if resultado.observaciones:
                    st.markdown("**Observaciones:**")
                    for obs in resultado.observaciones:
                        st.caption(f"• {obs}")

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
