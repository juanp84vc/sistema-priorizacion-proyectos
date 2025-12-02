"""Dashboard con visualizaciones y métricas agregadas - Diseño Ejecutivo."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from datetime import datetime
from pathlib import Path
import sys

# Agregar src al path si no está
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importar exportador de cartera profesional
try:
    from servicios.exportador_cartera import ExportadorCartera
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "exportador_cartera",
        Path(__file__).parent.parent / "src" / "servicios" / "exportador_cartera.py"
    )
    exportador_cartera_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exportador_cartera_module)
    ExportadorCartera = exportador_cartera_module.ExportadorCartera

# Importar componentes UI ejecutivos
try:
    from ui.componentes import ComponentesUI
    from ui.estilos import EstilosUI
    UI_DISPONIBLE = True
except ImportError:
    UI_DISPONIBLE = False


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
    """Muestra el dashboard con visualizaciones - Diseño Ejecutivo."""

    # Header ejecutivo
    if UI_DISPONIBLE:
        ComponentesUI.header_ejecutivo(
            titulo="Dashboard Ejecutivo",
            subtitulo="Análisis integral del portafolio de proyectos de inversión social",
            mostrar_fecha=True
        )
    else:
        st.markdown('<h1 class="main-header animate-fade-in-down">Dashboard Ejecutivo</h1>',
                    unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #cbd5e1; margin-bottom: 2rem;">Análisis integral del portafolio de proyectos</p>', unsafe_allow_html=True)

    # Verificar que hay proyectos
    if len(st.session_state.proyectos) == 0:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
             border: 1px solid rgba(14, 165, 233, 0.2); border-radius: 1rem;
             padding: 3rem; text-align: center; margin: 2rem 0;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #f8fafc; margin-bottom: 1rem;">No hay proyectos registrados</h3>
            <p style="color: #94a3b8;">Agregue proyectos desde el módulo "Nuevo Proyecto" para visualizar el dashboard ejecutivo</p>
        </div>
        """, unsafe_allow_html=True)
        return

    proyectos = st.session_state.proyectos

    # Calcular métricas
    presupuesto_total = sum(p.presupuesto_total for p in proyectos)
    beneficiarios_total = sum(p.beneficiarios_totales for p in proyectos)
    costo_promedio = presupuesto_total / beneficiarios_total if beneficiarios_total > 0 else 0

    # Calcular SROI promedio
    sroi_total = 0
    proyectos_con_sroi = 0
    for p in proyectos:
        sroi_valor = p.indicadores_impacto.get('sroi', 0.0)
        try:
            sroi_num = float(sroi_valor) if sroi_valor else 0.0
            if sroi_num > 0:
                sroi_total += sroi_num
                proyectos_con_sroi += 1
        except (ValueError, TypeError):
            pass
    sroi_promedio = sroi_total / proyectos_con_sroi if proyectos_con_sroi > 0 else 0

    # KPIs ejecutivos
    if UI_DISPONIBLE:
        ComponentesUI.kpis_ejecutivos([
            {'valor': len(proyectos), 'etiqueta': 'Proyectos en Cartera'},
            {'valor': f"${formatear_numero(presupuesto_total / 1e6, 1)}M", 'etiqueta': 'Inversión Total'},
            {'valor': formatear_numero(beneficiarios_total, 0), 'etiqueta': 'Beneficiarios'},
            {'valor': f"${formatear_numero(costo_promedio, 0)}", 'etiqueta': 'Costo/Beneficiario'},
            {'valor': f"{formatear_numero(sroi_promedio, 1)}:1" if sroi_promedio > 0 else "N/A", 'etiqueta': 'SROI Promedio'}
        ])
    else:
        # Fallback a diseño anterior
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">TOTAL PROYECTOS</p>
                <h2 class="text-gradient-primary" style="margin: 0.5rem 0; font-size: 2rem;">{len(proyectos)}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">PRESUPUESTO TOTAL</p>
                <h2 class="text-gradient-primary" style="margin: 0.5rem 0; font-size: 2rem;">${formatear_numero(presupuesto_total / 1e6, 1)}M</h2>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">BENEFICIARIOS</p>
                <h2 class="text-gradient-primary" style="margin: 0.5rem 0; font-size: 2rem;">{formatear_numero(beneficiarios_total, 0)}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">COSTO/BENEFICIARIO</p>
                <h2 class="text-gradient-primary" style="margin: 0.5rem 0; font-size: 2rem;">${formatear_numero(costo_promedio)}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col5:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">SROI PROMEDIO</p>
                <h2 class="text-gradient-accent" style="margin: 0.5rem 0; font-size: 2rem;">{f"{formatear_numero(sroi_promedio, 1)}:1" if sroi_promedio > 0 else "N/A"}</h2>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualizaciones
    st.markdown('<h2 class="section-header">🌍 Distribución Geográfica</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Distribución por área geográfica
        areas = [p.area_geografica.value for p in proyectos]
        contador_areas = Counter(areas)

        df_areas = pd.DataFrame([
            {'Área': area, 'Proyectos': count}
            for area, count in contador_areas.items()
        ])

        fig_areas = px.pie(
            df_areas,
            values='Proyectos',
            names='Área',
            title='Proyectos por Área Geográfica',
            color_discrete_sequence=['#10b981', '#06b6d4', '#8b5cf6', '#f59e0b', '#ef4444']
        )
        
        fig_areas.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1', family='Inter'),
            title_font=dict(size=16, color='#f8fafc')
        )

        st.plotly_chart(fig_areas, use_container_width=True)

    with col2:
        # Distribución por departamentos
        todos_deptos = []
        for p in proyectos:
            todos_deptos.extend(p.departamentos)

        contador_deptos = Counter(todos_deptos)
        top_deptos = contador_deptos.most_common(10)

        df_deptos = pd.DataFrame([
            {'Departamento': depto, 'Proyectos': count}
            for depto, count in top_deptos
        ])

        fig_deptos = px.bar(
            df_deptos,
            x='Departamento',
            y='Proyectos',
            title='Top 10 Departamentos',
            color='Proyectos',
            color_continuous_scale=[[0, '#10b981'], [0.5, '#06b6d4'], [1, '#8b5cf6']]
        )

        fig_deptos.update_layout(
            showlegend=False, 
            xaxis_tickangle=-45,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1', family='Inter'),
            title_font=dict(size=16, color='#f8fafc'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )

        st.plotly_chart(fig_deptos, use_container_width=True)

    # Presupuestos
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h3 style="color: #f8fafc; margin-bottom: 1rem;">💰 Presupuesto por Proyecto</h3>', unsafe_allow_html=True)

        df_presupuesto = pd.DataFrame([
            {
                'Proyecto': p.nombre[:30] + '...' if len(p.nombre) > 30 else p.nombre,
                'Presupuesto': p.presupuesto_total
            }
            for p in proyectos
        ])

        df_presupuesto = df_presupuesto.sort_values('Presupuesto', ascending=True)

        fig_presupuesto = px.bar(
            df_presupuesto,
            x='Presupuesto',
            y='Proyecto',
            orientation='h',
            title='Presupuesto por Proyecto',
            color='Presupuesto',
            color_continuous_scale=[[0, '#10b981'], [0.5, '#06b6d4'], [1, '#8b5cf6']]
        )

        fig_presupuesto.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1', family='Inter'),
            title_font=dict(size=16, color='#f8fafc'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )

        st.plotly_chart(fig_presupuesto, use_container_width=True)

    with col2:
        st.markdown('<h3 style="color: #f8fafc; margin-bottom: 1rem;">👥 Beneficiarios por Proyecto</h3>', unsafe_allow_html=True)

        df_beneficiarios = pd.DataFrame([
            {
                'Proyecto': p.nombre[:30] + '...' if len(p.nombre) > 30 else p.nombre,
                'Directos': p.beneficiarios_directos,
                'Indirectos': p.beneficiarios_indirectos
            }
            for p in proyectos
        ])

        fig_beneficiarios = go.Figure()

        fig_beneficiarios.add_trace(go.Bar(
            y=df_beneficiarios['Proyecto'],
            x=df_beneficiarios['Directos'],
            name='Directos',
            orientation='h',
            marker=dict(color='#10b981')
        ))

        fig_beneficiarios.add_trace(go.Bar(
            y=df_beneficiarios['Proyecto'],
            x=df_beneficiarios['Indirectos'],
            name='Indirectos',
            orientation='h',
            marker=dict(color='#06b6d4')
        ))

        fig_beneficiarios.update_layout(
            barmode='stack',
            title='Beneficiarios Directos e Indirectos',
            xaxis_title='Beneficiarios',
            yaxis_title='Proyecto',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1', family='Inter'),
            title_font=dict(size=16, color='#f8fafc'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )

        st.plotly_chart(fig_beneficiarios, use_container_width=True)

    # Duración y eficiencia
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h3 style="color: #f8fafc; margin-bottom: 1rem;">⏱️ Duración de Proyectos</h3>', unsafe_allow_html=True)

        df_duracion = pd.DataFrame([
            {
                'Proyecto': p.nombre[:30] + '...' if len(p.nombre) > 30 else p.nombre,
                'Duración (años)': p.duracion_años
            }
            for p in proyectos
        ])

        fig_duracion = px.scatter(
            df_duracion,
            x='Duración (años)',
            y='Proyecto',
            size='Duración (años)',
            color='Duración (años)',
            color_continuous_scale=[[0, '#f59e0b'], [0.5, '#ef4444'], [1, '#8b5cf6']],
            title='Duración de Proyectos'
        )
        
        fig_duracion.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1', family='Inter'),
            title_font=dict(size=16, color='#f8fafc'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )

        st.plotly_chart(fig_duracion, use_container_width=True)

    with col2:
        st.markdown('<h3 style="color: #f8fafc; margin-bottom: 1rem;">📊 Eficiencia: Costo/Beneficiario</h3>', unsafe_allow_html=True)

        df_eficiencia = pd.DataFrame([
            {
                'Proyecto': p.nombre[:30] + '...' if len(p.nombre) > 30 else p.nombre,
                'Costo/Beneficiario': p.presupuesto_por_beneficiario
            }
            for p in proyectos
        ])

        df_eficiencia = df_eficiencia.sort_values('Costo/Beneficiario')

        fig_eficiencia = px.bar(
            df_eficiencia,
            x='Costo/Beneficiario',
            y='Proyecto',
            orientation='h',
            title='Costo por Beneficiario (menor es mejor)',
            color='Costo/Beneficiario',
            color_continuous_scale=[[0, '#10b981'], [0.5, '#f59e0b'], [1, '#ef4444']]
        )
        
        fig_eficiencia.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1', family='Inter'),
            title_font=dict(size=16, color='#f8fafc'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )

        st.plotly_chart(fig_eficiencia, use_container_width=True)

    # SROI por proyecto
    st.markdown("---")
    st.markdown('<h2 class="section-header">📈 Retorno Social de la Inversión (SROI)</h2>', unsafe_allow_html=True)

    # Filtrar proyectos con SROI
    proyectos_sroi = []
    for p in proyectos:
        sroi_valor = p.indicadores_impacto.get('sroi', 0.0)
        try:
            sroi_num = float(sroi_valor) if sroi_valor else 0.0
            if sroi_num > 0:
                proyectos_sroi.append({
                    'Proyecto': p.nombre[:30] + '...' if len(p.nombre) > 30 else p.nombre,
                    'SROI': sroi_num
                })
        except (ValueError, TypeError):
            pass

    if proyectos_sroi:
        df_sroi = pd.DataFrame(proyectos_sroi)
        df_sroi = df_sroi.sort_values('SROI', ascending=True)

        fig_sroi = px.bar(
            df_sroi,
            x='SROI',
            y='Proyecto',
            orientation='h',
            title='Retorno Social por Proyecto (mayor es mejor)',
            color='SROI',
            color_continuous_scale=[[0, '#10b981'], [0.5, '#06b6d4'], [1, '#8b5cf6']],
            text='SROI'
        )

        fig_sroi.update_traces(
            texttemplate='%{text:.1f}:1',
            textposition='outside'
        )

        fig_sroi.update_layout(
            xaxis_title='SROI (retorno por cada peso invertido)',
            yaxis_title='Proyecto',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1', family='Inter'),
            title_font=dict(size=16, color='#f8fafc'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )

        st.plotly_chart(fig_sroi, use_container_width=True)

        # Análisis del SROI
        col1, col2, col3 = st.columns(3)

        with col1:
            sroi_max = max([p['SROI'] for p in proyectos_sroi])
            proyecto_max = next(p for p in proyectos_sroi if p['SROI'] == sroi_max)
            st.metric(
                "Mayor SROI",
                f"{formatear_numero(sroi_max, 1)}:1",
                help=f"Proyecto: {proyecto_max['Proyecto']}"
            )

        with col2:
            sroi_min = min([p['SROI'] for p in proyectos_sroi])
            proyecto_min = next(p for p in proyectos_sroi if p['SROI'] == sroi_min)
            st.metric(
                "Menor SROI",
                f"{formatear_numero(sroi_min, 1)}:1",
                help=f"Proyecto: {proyecto_min['Proyecto']}"
            )

        with col3:
            sroi_acumulado = sum([p['SROI'] for p in proyectos_sroi])
            st.metric(
                "SROI Acumulado Portfolio",
                f"{formatear_numero(sroi_acumulado, 1)}:1",
                help=f"Suma total del retorno social de {len(proyectos_sroi)} proyectos"
            )
    else:
        st.info("No hay proyectos con SROI documentado.")

    # Tabla resumen
    st.markdown("---")
    st.markdown("### 📋 Tabla Resumen de Proyectos")

    df_resumen = pd.DataFrame([
        {
            'ID': p.id,
            'Nombre': p.nombre,
            'Organización': p.organizacion,
            'Presupuesto': f"${formatear_numero(p.presupuesto_total, 0)}",
            'Beneficiarios': formatear_numero(p.beneficiarios_totales, 0),
            'Duración (años)': formatear_numero(p.duracion_años, 1),
            'Área': p.area_geografica.value,
            'SROI': (lambda sroi_val: f"{formatear_numero(sroi_val, 1)}:1" if sroi_val > 0 else "N/A")(
                float(p.indicadores_impacto.get('sroi', 0.0)) if p.indicadores_impacto.get('sroi', 0.0) else 0.0
            ),
            'Estado': p.estado.value
        }
        for p in proyectos
    ])

    st.dataframe(df_resumen, use_container_width=True, hide_index=True)

    # Sección de Exportación Ejecutiva
    st.markdown("---")
    st.markdown("""
    <div class="seccion-titulo">📥 Exportar Informes Ejecutivos</div>
    <p style="color: #94a3b8; margin-bottom: 1rem;">Genere reportes profesionales para presentación al comité de aprobación</p>
    """, unsafe_allow_html=True)

    # Preparar datos para exportador profesional
    def _preparar_datos_dashboard():
        """Prepara datos del dashboard para exportación profesional."""
        resultados_detallados = []
        for p in proyectos:
            sroi_valor = float(p.indicadores_impacto.get('sroi', 1.5)) if p.indicadores_impacto.get('sroi') else 1.5

            # Calcular score simple basado en SROI
            if sroi_valor < 1.0:
                score_sroi = 0
            elif sroi_valor < 2.0:
                score_sroi = 60
            elif sroi_valor < 3.0:
                score_sroi = 80
            else:
                score_sroi = 95

            resultado = {
                'nombre': p.nombre,
                'proyecto': p.nombre,
                'score_final': score_sroi * 0.4 + 70 * 0.6,  # Score aproximado
                'detalle_criterios': [
                    {'criterio': 'SROI', 'score_base': score_sroi, 'contribucion_parcial': score_sroi * 0.4},
                    {'criterio': 'Stakeholders', 'score_base': 70, 'contribucion_parcial': 70 * 0.25},
                    {'criterio': 'Probabilidad', 'score_base': 70, 'contribucion_parcial': 70 * 0.20},
                    {'criterio': 'Riesgos', 'score_base': 70, 'contribucion_parcial': 70 * 0.15}
                ],
                'alertas': []
            }
            resultados_detallados.append(resultado)

        reporte = {
            'fecha': datetime.now().strftime("%Y-%m-%d"),
            'total_proyectos': len(proyectos),
            'presupuesto_total': presupuesto_total,
            'beneficiarios_total': beneficiarios_total
        }

        return reporte, resultados_detallados

    # Contenedor de reportes profesionales
    st.markdown("""
    <div style="background: linear-gradient(145deg, rgba(14, 165, 233, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%);
         border: 1px solid rgba(14, 165, 233, 0.2); border-radius: 1rem;
         padding: 1.5rem; margin: 1rem 0;">
        <h4 style="color: #f8fafc; margin: 0 0 1rem 0;">Reportes para Comité de Aprobación</h4>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        try:
            reporte_dash, resultados_dash = _preparar_datos_dashboard()
            exportador_prof = ExportadorCartera(reporte_dash, resultados_dash)
            word_data = exportador_prof.exportar_word()
            st.download_button(
                label="📝 Informe Word",
                data=word_data,
                file_name=f"informe_ejecutivo_{datetime.now().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                help="Documento completo con portada, metodología, ranking y recomendaciones"
            )
        except Exception as e:
            st.error(f"Error Word: {str(e)}")

    with col2:
        try:
            reporte_dash, resultados_dash = _preparar_datos_dashboard()
            exportador_prof = ExportadorCartera(reporte_dash, resultados_dash)
            excel_data = exportador_prof.exportar_excel()
            st.download_button(
                label="📊 Análisis Excel",
                data=excel_data,
                file_name=f"analisis_cartera_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="5 hojas: Resumen, Ranking, Comparativo, Detalle, Metodología"
            )
        except Exception as e:
            st.error(f"Error Excel: {str(e)}")

    with col3:
        try:
            reporte_dash, resultados_dash = _preparar_datos_dashboard()
            exportador_prof = ExportadorCartera(reporte_dash, resultados_dash)
            pptx_data = exportador_prof.exportar_powerpoint()
            st.download_button(
                label="📽️ Presentación PPT",
                data=pptx_data,
                file_name=f"presentacion_comite_{datetime.now().strftime('%Y%m%d')}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                use_container_width=True,
                help="5 slides ejecutivos para presentación al comité"
            )
        except Exception as e:
            st.error(f"Error PowerPoint: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Exportaciones básicas en expander
    with st.expander("Exportaciones Básicas", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            # CSV
            csv = df_resumen.to_csv(index=False, sep=';')
            st.download_button(
                label="📄 CSV",
                data=csv,
                file_name="dashboard_proyectos.csv",
                mime="text/csv",
                use_container_width=True,
                help="Tabla resumen en formato CSV"
            )

        with col2:
            # Markdown
            fecha = datetime.now().strftime("%Y-%m-%d")
            markdown_content = f"""# Dashboard de Proyectos
**Fecha de generación:** {fecha}

## 📊 Métricas Generales

- **Total de Proyectos:** {len(proyectos)}
- **Presupuesto Total:** ${formatear_numero(presupuesto_total)}
- **Beneficiarios Totales:** {formatear_numero(beneficiarios_total, 0)}
- **Costo Promedio por Beneficiario:** ${formatear_numero(costo_promedio)}

## 📋 Listado de Proyectos

"""
            for p in proyectos:
                markdown_content += f"""
### {p.nombre}

- **ID:** {p.id}
- **Organización:** {p.organizacion}
- **Presupuesto:** ${formatear_numero(p.presupuesto_total)}
- **Beneficiarios Directos:** {formatear_numero(p.beneficiarios_directos, 0)}
- **Beneficiarios Indirectos:** {formatear_numero(p.beneficiarios_indirectos, 0)}
- **Duración:** {formatear_numero(p.duracion_años, 1)} años
- **Área Geográfica:** {p.area_geografica.value}
- **Departamentos:** {', '.join(p.departamentos)}
{f"- **Municipios:** {', '.join(p.municipios)}" if p.municipios else ""}
- **Estado:** {p.estado.value}
- **Costo por Beneficiario:** ${formatear_numero(p.presupuesto_por_beneficiario)}

**Descripción:**
{p.descripcion}

---
"""

            st.download_button(
                label="📝 Markdown",
                data=markdown_content,
                file_name="dashboard_proyectos.md",
                mime="text/markdown",
                use_container_width=True,
                help="Dashboard completo en formato Markdown"
            )

        with col3:
            # Fichas Técnicas
            fichas_content = f"""# FICHAS TÉCNICAS DE PROYECTOS
**Fecha de generación:** {fecha}

---

"""
            for idx, p in enumerate(proyectos, 1):
                fichas_content += f"""
## FICHA TÉCNICA #{idx}

### INFORMACIÓN GENERAL
**Proyecto:** {p.nombre}
**ID:** {p.id}
**Organización Ejecutora:** {p.organizacion}
**Estado:** {p.estado.value.upper()}

### DESCRIPCIÓN
{p.descripcion}

### POBLACIÓN OBJETIVO
**Tipo:** {p.poblacion_objetivo}
**Beneficiarios Directos:** {formatear_numero(p.beneficiarios_directos, 0)}
**Beneficiarios Indirectos:** {formatear_numero(p.beneficiarios_indirectos, 0)}
**Total Beneficiarios:** {formatear_numero(p.beneficiarios_totales, 0)}

### ALCANCE GEOGRÁFICO
**Área:** {p.area_geografica.value.upper()}
**Departamentos:** {', '.join(p.departamentos)}
{f"**Municipios:** {', '.join(p.municipios)}" if p.municipios else ""}

### FINANCIAMIENTO
**Presupuesto Total:** ${formatear_numero(p.presupuesto_total)}
**Duración:** {formatear_numero(p.duracion_meses, 0)} meses ({formatear_numero(p.duracion_años, 1)} años)
**Costo por Beneficiario:** ${formatear_numero(p.presupuesto_por_beneficiario)}

### INDICADORES DE CAPACIDAD ORGANIZACIONAL
- **Años de experiencia:** {p.indicadores_impacto.get('años_experiencia', 'N/A')}
- **Equipo calificado:** {formatear_numero(p.indicadores_impacto.get('equipo_calificado', 0) * 100, 0)}%
- **Proyectos exitosos previos:** {p.indicadores_impacto.get('proyectos_exitosos', 'N/A')}
- **Fuentes de financiamiento:** {p.indicadores_impacto.get('fuentes_financiamiento', 'N/A')}
- **Ingresos propios:** {formatear_numero(p.indicadores_impacto.get('ingresos_propios_pct', 0), 0)}%

---

"""

        st.download_button(
            label="📋 Fichas Técnicas",
            data=fichas_content,
            file_name="fichas_tecnicas_proyectos.txt",
            mime="text/plain",
            use_container_width=True,
            help="Fichas técnicas completas de todos los proyectos"
        )
