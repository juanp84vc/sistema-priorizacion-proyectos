"""Dashboard con visualizaciones y métricas agregadas."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from datetime import datetime


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
    """Muestra el dashboard con visualizaciones."""
    st.markdown('<h1 class="main-header animate-fade-in-down">📈 Dashboard de Proyectos</h1>',
                unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #cbd5e1; margin-bottom: 2rem;">Visualiza el impacto de tu portafolio de proyectos</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Verificar que hay proyectos
    if len(st.session_state.proyectos) == 0:
        st.markdown("""
        <div class="info-box" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #f8fafc; margin-bottom: 1rem;">No hay proyectos registrados</h3>
            <p style="color: #cbd5e1;">Ve a 'Nuevo Proyecto' para agregar proyectos y visualizar métricas</p>
        </div>
        """, unsafe_allow_html=True)
        return

    proyectos = st.session_state.proyectos

    # Métricas principales con diseño moderno
    st.markdown('<h2 class="section-header">📊 Métricas Generales</h2>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">TOTAL PROYECTOS</p>
            <h2 class="text-gradient-primary" style="margin: 0.5rem 0; font-size: 2rem;">{}</h2>
        </div>
        """.format(len(proyectos)), unsafe_allow_html=True)

    presupuesto_total = sum(p.presupuesto_total for p in proyectos)
    with col2:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">PRESUPUESTO TOTAL</p>
            <h2 class="text-gradient-primary" style="margin: 0.5rem 0; font-size: 2rem;">${}M</h2>
        </div>
        """.format(formatear_numero(presupuesto_total / 1e6, 1)), unsafe_allow_html=True)

    beneficiarios_total = sum(p.beneficiarios_totales for p in proyectos)
    with col3:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">BENEFICIARIOS TOTALES</p>
            <h2 class="text-gradient-primary" style="margin: 0.5rem 0; font-size: 2rem;">{}</h2>
        </div>
        """.format(formatear_numero(beneficiarios_total, 0)), unsafe_allow_html=True)

    costo_promedio = presupuesto_total / beneficiarios_total if beneficiarios_total > 0 else 0
    with col4:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">COSTO/BENEFICIARIO</p>
            <h2 class="text-gradient-primary" style="margin: 0.5rem 0; font-size: 2rem;">${}</h2>
        </div>
        """.format(formatear_numero(costo_promedio)), unsafe_allow_html=True)

    # Calcular SROI promedio del portafolio
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
    with col5:
        st.markdown("""
        <div class="metric-card" style="text-align: center;">
            <p style="font-size: 0.75rem; color: #94a3b8; margin: 0;">SROI PROMEDIO</p>
            <h2 class="text-gradient-accent" style="margin: 0.5rem 0; font-size: 2rem;">{}</h2>
        </div>
        """.format(f"{formatear_numero(sroi_promedio, 1)}:1" if sroi_promedio > 0 else "N/A"), unsafe_allow_html=True)

    st.markdown("---")

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

    # Exportar
    st.markdown("---")
    st.markdown("### 📥 Exportar Dashboard")

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
