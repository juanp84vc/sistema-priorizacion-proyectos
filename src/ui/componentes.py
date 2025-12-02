"""
Componentes UI reutilizables para Sistema de Priorización ENLAZA GEB.
SRP: Solo gestiona renderizado de componentes visuales.
"""
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional
from .estilos import EstilosUI


class ComponentesUI:
    """Componentes UI reutilizables con diseño ejecutivo."""

    @staticmethod
    def header_ejecutivo(
        titulo: str,
        subtitulo: str = "",
        mostrar_fecha: bool = True
    ):
        """
        Renderiza un header ejecutivo profesional.

        Args:
            titulo: Título principal
            subtitulo: Subtítulo descriptivo
            mostrar_fecha: Si mostrar la fecha actual
        """
        fecha_html = ""
        if mostrar_fecha:
            fecha = datetime.now().strftime("%d de %B, %Y")
            fecha_html = f'<div class="header-fecha">{fecha}</div>'

        st.markdown(f"""
        <div class="header-ejecutivo">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h1 class="header-titulo">{titulo}</h1>
                    <p class="header-subtitulo">{subtitulo}</p>
                </div>
                {fecha_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def kpis_ejecutivos(kpis: List[Dict[str, Any]]):
        """
        Renderiza una fila de KPIs ejecutivos.

        Args:
            kpis: Lista de diccionarios con keys: valor, etiqueta, delta (opcional), delta_tipo (opcional)
        """
        cols = st.columns(len(kpis))
        for col, kpi in zip(cols, kpis):
            with col:
                st.markdown(
                    EstilosUI.css_kpi_card(
                        valor=str(kpi.get('valor', '-')),
                        etiqueta=kpi.get('etiqueta', ''),
                        delta=kpi.get('delta'),
                        delta_tipo=kpi.get('delta_tipo', 'positivo')
                    ),
                    unsafe_allow_html=True
                )

    @staticmethod
    def ranking_proyectos(
        proyectos: List[Dict[str, Any]],
        titulo: str = "Ranking de Proyectos",
        icono: str = "",
        max_mostrar: int = 10
    ):
        """
        Renderiza un ranking visual de proyectos.

        Args:
            proyectos: Lista de proyectos con keys: nombre, score
            titulo: Título del ranking
            icono: Emoji o icono para el título
            max_mostrar: Máximo de proyectos a mostrar
        """
        items_html = ""
        for i, proyecto in enumerate(proyectos[:max_mostrar], 1):
            nombre = proyecto.get('nombre', proyecto.get('proyecto_nombre', 'Sin nombre'))
            score = proyecto.get('score', proyecto.get('score_final', 0))
            items_html += EstilosUI.css_ranking_item(i, nombre, score)

        st.markdown(f"""
        <div class="ranking-container">
            <div class="ranking-titulo">{icono} {titulo}</div>
            {items_html}
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def seccion_titulo(titulo: str, icono: str = ""):
        """Renderiza un título de sección estilizado."""
        st.markdown(f"""
        <div class="seccion-titulo">{icono} {titulo}</div>
        """, unsafe_allow_html=True)

    @staticmethod
    def badge_recomendacion(recomendacion: str):
        """Renderiza un badge de estado según la recomendación."""
        st.markdown(EstilosUI.css_badge_estado(recomendacion), unsafe_allow_html=True)

    @staticmethod
    def tarjeta_proyecto_ejecutiva(
        nombre: str,
        score: float,
        recomendacion: str,
        detalles: Dict[str, float] = None,
        posicion: int = None
    ):
        """
        Renderiza una tarjeta de proyecto con diseño ejecutivo.

        Args:
            nombre: Nombre del proyecto
            score: Score final
            recomendacion: Recomendación del motor
            detalles: Diccionario de criterios y scores
            posicion: Posición en el ranking (opcional)
        """
        # Determinar color según score
        if score >= 70:
            color_score = "#22c55e"
            bg_score = "rgba(34, 197, 94, 0.15)"
        elif score >= 50:
            color_score = "#f59e0b"
            bg_score = "rgba(245, 158, 11, 0.15)"
        else:
            color_score = "#ef4444"
            bg_score = "rgba(239, 68, 68, 0.15)"

        posicion_html = ""
        if posicion:
            pos_colors = {1: ("#fbbf24", "#0f172a"), 2: ("#94a3b8", "#0f172a"), 3: ("#cd7c32", "#0f172a")}
            bg, fg = pos_colors.get(posicion, ("rgba(255,255,255,0.1)", "#94a3b8"))
            posicion_html = f"""
            <div style="position: absolute; top: -10px; right: 10px;
                 width: 30px; height: 30px; border-radius: 50%;
                 background: linear-gradient(135deg, {bg} 0%, {bg} 100%);
                 display: flex; align-items: center; justify-content: center;
                 font-weight: 700; color: {fg}; font-size: 0.9rem;">
                {posicion}
            </div>
            """

        detalles_html = ""
        if detalles:
            detalles_html = '<div style="display: flex; gap: 1rem; margin-top: 1rem; flex-wrap: wrap;">'
            for criterio, valor in detalles.items():
                detalles_html += f"""
                <div style="text-align: center; padding: 0.5rem 1rem;
                     background: rgba(255,255,255,0.03); border-radius: 0.5rem;">
                    <div style="color: #64748b; font-size: 0.7rem; text-transform: uppercase;">{criterio}</div>
                    <div style="color: #f8fafc; font-weight: 600;">{valor:.1f}</div>
                </div>
                """
            detalles_html += '</div>'

        badge = EstilosUI.css_badge_estado(recomendacion)

        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
             border: 1px solid rgba(255,255,255,0.1); border-radius: 1rem;
             padding: 1.5rem; margin: 1rem 0; position: relative;">
            {posicion_html}
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                    <h3 style="color: #f8fafc; margin: 0 0 0.5rem 0; font-size: 1.2rem;">{nombre}</h3>
                    {badge}
                </div>
                <div style="text-align: center; padding: 0.75rem 1.25rem;
                     background: {bg_score}; border-radius: 0.75rem;">
                    <div style="font-size: 0.7rem; color: {color_score}; text-transform: uppercase;">Score</div>
                    <div style="font-size: 1.5rem; font-weight: 800; color: {color_score};">{score:.1f}</div>
                </div>
            </div>
            {detalles_html}
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def resumen_metodologia():
        """Renderiza un resumen visual de la metodología de evaluación."""
        st.markdown("""
        <div style="background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
             border: 1px solid rgba(255,255,255,0.1); border-radius: 1rem;
             padding: 1.5rem; margin: 1rem 0;">
            <h3 style="color: #f8fafc; margin: 0 0 1rem 0;">Metodología de Evaluación - Arquitectura C</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div style="text-align: center; padding: 1rem; background: rgba(14, 165, 233, 0.1);
                     border-radius: 0.75rem; border: 1px solid rgba(14, 165, 233, 0.2);">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #0ea5e9;">40%</div>
                    <div style="color: #f8fafc; font-weight: 500;">SROI</div>
                    <div style="color: #64748b; font-size: 0.8rem;">Retorno Social</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: rgba(16, 185, 129, 0.1);
                     border-radius: 0.75rem; border: 1px solid rgba(16, 185, 129, 0.2);">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #10b981;">25%</div>
                    <div style="color: #f8fafc; font-weight: 500;">Stakeholders</div>
                    <div style="color: #64748b; font-size: 0.8rem;">Alineación</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: rgba(139, 92, 246, 0.1);
                     border-radius: 0.75rem; border: 1px solid rgba(139, 92, 246, 0.2);">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #8b5cf6;">20%</div>
                    <div style="color: #f8fafc; font-weight: 500;">Probabilidad</div>
                    <div style="color: #64748b; font-size: 0.8rem;">Aprobación</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: rgba(245, 158, 11, 0.1);
                     border-radius: 0.75rem; border: 1px solid rgba(245, 158, 11, 0.2);">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #f59e0b;">15%</div>
                    <div style="color: #f8fafc; font-weight: 500;">Riesgos</div>
                    <div style="color: #64748b; font-size: 0.8rem;">Mitigación</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def separador():
        """Renderiza un separador visual elegante."""
        st.markdown("""
        <div style="height: 1px; background: linear-gradient(90deg,
             transparent, rgba(14, 165, 233, 0.3), transparent);
             margin: 2rem 0;"></div>
        """, unsafe_allow_html=True)

    @staticmethod
    def footer_ejecutivo():
        """Renderiza el footer ejecutivo."""
        st.markdown("""
        <div class="footer-ejecutivo">
            <div class="footer-titulo">Sistema de Priorización ENLAZA GEB</div>
            <div class="footer-subtitulo">Valor Compartido | Arquitectura C</div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def alerta_info(mensaje: str, icono: str = ""):
        """Renderiza una alerta informativa elegante."""
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
             border: 1px solid rgba(14, 165, 233, 0.3); border-radius: 0.75rem;
             padding: 1rem 1.25rem; display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 1.25rem;">{icono}</span>
            <span style="color: #f8fafc;">{mensaje}</span>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def alerta_exito(mensaje: str, icono: str = ""):
        """Renderiza una alerta de éxito."""
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
             border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 0.75rem;
             padding: 1rem 1.25rem; display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 1.25rem;">{icono}</span>
            <span style="color: #f8fafc;">{mensaje}</span>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def alerta_advertencia(mensaje: str, icono: str = ""):
        """Renderiza una alerta de advertencia."""
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(234, 179, 8, 0.1) 100%);
             border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 0.75rem;
             padding: 1rem 1.25rem; display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 1.25rem;">{icono}</span>
            <span style="color: #f8fafc;">{mensaje}</span>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def grafico_barras_horizontal(datos: Dict[str, float], titulo: str = "", max_valor: float = 100):
        """
        Renderiza un gráfico de barras horizontal simple.

        Args:
            datos: Diccionario con etiquetas y valores
            titulo: Título del gráfico
            max_valor: Valor máximo para escala
        """
        colores = ["#0ea5e9", "#10b981", "#8b5cf6", "#f59e0b", "#ef4444", "#ec4899"]

        barras_html = ""
        for i, (etiqueta, valor) in enumerate(datos.items()):
            porcentaje = (valor / max_valor) * 100
            color = colores[i % len(colores)]
            barras_html += f"""
            <div style="margin: 0.75rem 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                    <span style="color: #f8fafc; font-size: 0.85rem;">{etiqueta}</span>
                    <span style="color: {color}; font-weight: 600;">{valor:.1f}</span>
                </div>
                <div style="background: rgba(255,255,255,0.1); border-radius: 0.25rem; height: 8px; overflow: hidden;">
                    <div style="background: {color}; height: 100%; width: {porcentaje}%;
                         border-radius: 0.25rem; transition: width 0.5s ease;"></div>
                </div>
            </div>
            """

        titulo_html = f'<h4 style="color: #f8fafc; margin: 0 0 1rem 0;">{titulo}</h4>' if titulo else ""

        st.markdown(f"""
        <div style="background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
             border: 1px solid rgba(255,255,255,0.1); border-radius: 0.75rem;
             padding: 1.25rem; margin: 0.5rem 0;">
            {titulo_html}
            {barras_html}
        </div>
        """, unsafe_allow_html=True)
