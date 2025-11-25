"""Página de inicio de la aplicación."""
import streamlit as st
from pathlib import Path


def show():
    """Muestra la página de inicio."""
    
    # Hero Section con imagen
    hero_path = Path(__file__).parent.parent / "static" / "images" / "hero_valor_compartido.png"
    
    if hero_path.exists():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.image(str(hero_path), use_container_width=True)
    
    st.markdown('<h1 class="main-header animate-fade-in-down">🎯 Sistema de Priorización de Proyectos Sociales</h1>',
                unsafe_allow_html=True)
    
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #cbd5e1; margin-bottom: 2rem;" class="animate-fade-in-up">Transformando ideas en impacto social medible</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Métricas principales con diseño moderno
    col1, col2, col3 = st.columns(3)
    
    num_proyectos = len(st.session_state.proyectos)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">📊</div>
            <h2 class="text-gradient-primary" style="margin: 0; font-size: 2.5rem;">{}</h2>
            <p style="color: #94a3b8; margin-top: 0.5rem; font-size: 0.9rem;">Proyectos Registrados</p>
        </div>
        """.format(num_proyectos), unsafe_allow_html=True)
    
    with col2:
        if num_proyectos > 0:
            presupuesto_total = sum(p.presupuesto_total for p in st.session_state.proyectos)
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 2rem 1rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">💰</div>
                <h2 class="text-gradient-primary" style="margin: 0; font-size: 2.5rem;">${:,.0f}M</h2>
                <p style="color: #94a3b8; margin-top: 0.5rem; font-size: 0.9rem;">Presupuesto Total</p>
            </div>
            """.format(presupuesto_total / 1e6), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 2rem 1rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">💰</div>
                <h2 class="text-gradient-primary" style="margin: 0; font-size: 2.5rem;">$0</h2>
                <p style="color: #94a3b8; margin-top: 0.5rem; font-size: 0.9rem;">Presupuesto Total</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if num_proyectos > 0:
            beneficiarios_total = sum(p.beneficiarios_totales for p in st.session_state.proyectos)
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 2rem 1rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">👥</div>
                <h2 class="text-gradient-primary" style="margin: 0; font-size: 2.5rem;">{:,}</h2>
                <p style="color: #94a3b8; margin-top: 0.5rem; font-size: 0.9rem;">Beneficiarios Totales</p>
            </div>
            """.format(beneficiarios_total), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="glass-card" style="text-align: center; padding: 2rem 1rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">👥</div>
                <h2 class="text-gradient-primary" style="margin: 0; font-size: 2.5rem;">0</h2>
                <p style="color: #94a3b8; margin-top: 0.5rem; font-size: 0.9rem;">Beneficiarios Totales</p>
            </div>
            """, unsafe_allow_html=True)

    # Call to action si no hay proyectos
    if num_proyectos == 0:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="info-box" style="text-align: center; padding: 2rem;">
                <h3 style="color: #f8fafc; margin-bottom: 1rem;">🚀 ¡Comienza ahora!</h3>
                <p style="color: #cbd5e1;">Registra tu primer proyecto y descubre cómo priorizamos el impacto social</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Características principales con tarjetas modernas
    st.markdown('<h2 class="section-header">⚡ Características Principales</h2>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🎯</div>
            <h3 class="text-gradient-primary" style="margin-bottom: 1rem;">Priorización Inteligente</h3>
            <ul style="color: #cbd5e1; line-height: 1.8;">
                <li>Impacto social (SROI 40%)</li>
                <li>Sostenibilidad financiera</li>
                <li>Alineación con ODS</li>
                <li>Capacidad organizacional</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">📊</div>
            <h3 class="text-gradient-primary" style="margin-bottom: 1rem;">Múltiples Estrategias</h3>
            <ul style="color: #cbd5e1; line-height: 1.8;">
                <li>Scoring ponderado</li>
                <li>Umbrales mínimos</li>
                <li>Comparación directa</li>
                <li>Análisis de cartera</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🛠️</div>
            <h3 class="text-gradient-primary" style="margin-bottom: 1rem;">Totalmente Configurable</h3>
            <ul style="color: #cbd5e1; line-height: 1.8;">
                <li>Criterios propios</li>
                <li>Pesos ajustables</li>
                <li>ODS prioritarios</li>
                <li>Umbrales personalizados</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Guía rápida con diseño moderno
    st.markdown('<h2 class="section-header">🚀 Cómo Empezar</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #f8fafc; margin-bottom: 1rem;">1️⃣ Registrar Proyecto</h3>
            <p style="color: #cbd5e1; line-height: 1.6;">
                Ve a <strong>➕ Nuevo Proyecto</strong> y completa el formulario con información básica, 
                datos financieros, indicadores de impacto y ODS vinculados.
            </p>
        </div>
        <br>
        <div class="glass-card">
            <h3 style="color: #f8fafc; margin-bottom: 1rem;">2️⃣ Evaluar Cartera</h3>
            <p style="color: #cbd5e1; line-height: 1.6;">
                En <strong>📊 Evaluar Cartera</strong> selecciona proyectos, elige estrategia de evaluación, 
                visualiza ranking y exporta resultados.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #f8fafc; margin-bottom: 1rem;">3️⃣ Análisis Visual</h3>
            <p style="color: #cbd5e1; line-height: 1.6;">
                El <strong>📈 Dashboard</strong> muestra distribución por ODS, métricas agregadas, 
                comparaciones visuales y tendencias de la cartera.
            </p>
        </div>
        <br>
        <div class="glass-card">
            <h3 style="color: #f8fafc; margin-bottom: 1rem;">4️⃣ Personalización</h3>
            <p style="color: #cbd5e1; line-height: 1.6;">
                En <strong>⚙️ Configuración</strong> ajusta pesos de criterios, define ODS prioritarios, 
                configura umbrales y guarda configuraciones.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Arquitectura SOLID
    st.markdown("---")

    with st.expander("🏗️ Arquitectura del Sistema (Principios SOLID)"):
        st.markdown("""
        <div style="color: #cbd5e1; line-height: 1.8;">
            <p>Este sistema está construido siguiendo los <strong>Principios SOLID</strong> de diseño de software:</p>
            
            <ul>
                <li><strong>S</strong> - Single Responsibility: Cada criterio tiene una sola responsabilidad</li>
                <li><strong>O</strong> - Open/Closed: Extensible sin modificar código existente</li>
                <li><strong>L</strong> - Liskov Substitution: Criterios intercambiables</li>
                <li><strong>I</strong> - Interface Segregation: Interfaces mínimas y focalizadas</li>
                <li><strong>D</strong> - Dependency Inversion: Sistema depende de abstracciones</li>
            </ul>
            
            <p style="margin-top: 1rem;"><strong>Esto garantiza:</strong></p>
            <ul>
                <li>✅ Fácil mantenimiento</li>
                <li>✅ Extensibilidad sin romper funcionalidad</li>
                <li>✅ Código limpio y testeable</li>
                <li>✅ Adaptabilidad a nuevos requerimientos</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

