"""
Página para ver historial de versiones y trazabilidad de proyectos.
"""
import streamlit as st
from datetime import datetime
from typing import Optional
from servicios.gestor_historial import GestorHistorial
from models.historial import EstadoRecomendacion


def show():
    """Muestra página de historial de proyectos."""
    st.markdown("### 📚 Historial de Versiones y Trazabilidad")
    st.markdown("---")

    # Obtener gestor de historial desde session_state
    if 'gestor_historial' not in st.session_state:
        st.session_state.gestor_historial = GestorHistorial()

    gestor = st.session_state.gestor_historial

    # Obtener proyectos con historial
    proyectos_con_historial = [
        (proyecto, gestor.obtener_historial(proyecto.id))
        for proyecto in st.session_state.proyectos
        if gestor.obtener_historial(proyecto.id) is not None
    ]

    if not proyectos_con_historial:
        st.info("📭 No hay proyectos con historial de versiones aún. Los proyectos generan historial automáticamente al ser evaluados.")
        return

    # Selector de proyecto
    opciones_proyectos = [p.nombre for p, _ in proyectos_con_historial]
    proyecto_seleccionado = st.selectbox(
        "Selecciona un proyecto:",
        opciones_proyectos
    )

    # Obtener proyecto e historial
    proyecto, historial = next(
        (p, h) for p, h in proyectos_con_historial
        if p.nombre == proyecto_seleccionado
    )

    # Tabs principales
    tab_resumen, tab_versiones, tab_recomendaciones, tab_comparar, tab_exportar = st.tabs([
        "📊 Resumen", "📖 Versiones", "✅ Recomendaciones", "🔄 Comparar", "📥 Exportar"
    ])

    # ==================== TAB: RESUMEN ====================
    with tab_resumen:
        st.markdown(f"#### {historial.proyecto_nombre}")

        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Versiones", historial.numero_versiones)

        with col2:
            st.metric(
                "Score Actual",
                f"{historial.version_actual.score_total:.1f}",
                delta=f"{historial.mejora_total:+.1f}" if historial.numero_versiones > 1 else None
            )

        with col3:
            if historial.numero_versiones > 1:
                st.metric("Mejora Total", f"{historial.porcentaje_mejora:.1f}%")
            else:
                st.metric("Mejora Total", "N/A")

        with col4:
            total_recs = len(historial.obtener_recomendaciones_implementadas()) + len(historial.recomendaciones_pendientes)
            implementadas = len(historial.obtener_recomendaciones_implementadas())
            if total_recs > 0:
                tasa = (implementadas / total_recs * 100)
                st.metric("Implementación", f"{tasa:.0f}%")
            else:
                st.metric("Implementación", "N/A")

        st.markdown("---")

        # Timeline de versiones
        st.markdown("##### 📅 Línea de Tiempo")
        timeline = historial.generar_timeline()

        for evento in timeline:
            fecha = datetime.fromisoformat(evento['fecha']).strftime("%d/%m/%Y %H:%M")

            if evento['tipo'] == 'version':
                st.markdown(
                    f"**{fecha}** - 🔖 Versión {evento['numero_version']} "
                    f"(Score: {evento['score']:.1f})"
                )
                if evento.get('cambios'):
                    for cambio in evento['cambios'][:3]:  # Mostrar solo primeros 3
                        st.markdown(f"  - {cambio}")
                    if len(evento['cambios']) > 3:
                        st.markdown(f"  - *...y {len(evento['cambios']) - 3} más*")

            elif evento['tipo'] == 'recomendacion_implementada':
                st.markdown(
                    f"**{fecha}** - ✅ Recomendación implementada: "
                    f"*{evento['descripcion'][:60]}...*"
                )

        # Estadísticas de mejora (si hay más de una versión)
        if historial.numero_versiones > 1:
            st.markdown("---")
            st.markdown("##### 📈 Estadísticas de Mejora")

            stats = gestor.obtener_estadisticas_mejora(proyecto.id)

            if not stats.get('versiones_insuficientes'):
                # Mejoras por criterio
                st.markdown("**Mejora por Criterio:**")

                for criterio, datos in stats['mejoras_por_criterio'].items():
                    col_a, col_b, col_c = st.columns([2, 1, 1])

                    with col_a:
                        st.markdown(f"**{criterio}**")

                    with col_b:
                        st.markdown(f"{datos['score_inicial']:.1f} → {datos['score_actual']:.1f}")

                    with col_c:
                        mejora = datos['mejora_puntos']
                        color = "🟢" if mejora > 0 else "🔴" if mejora < 0 else "⚪"
                        st.markdown(f"{color} {mejora:+.1f} pts ({datos['mejora_porcentaje']:+.1f}%)")

    # ==================== TAB: VERSIONES ====================
    with tab_versiones:
        st.markdown("#### Historial de Versiones")

        # Mostrar versiones en orden inverso (más reciente primero)
        for version in reversed(historial.versiones):
            with st.expander(
                f"📌 Versión {version.numero_version} - {version.fecha.strftime('%d/%m/%Y %H:%M')} "
                f"(Score: {version.score_total:.1f})",
                expanded=(version == historial.version_actual)
            ):
                # Información de la versión
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Score Total:** {version.score_total:.1f}")
                    st.markdown(f"**Usuario:** {version.usuario}")

                with col2:
                    st.markdown(f"**Fecha:** {version.fecha.strftime('%d/%m/%Y %H:%M')}")
                    if version.notas:
                        st.markdown(f"**Notas:** {version.notas}")

                # Scores por criterio
                st.markdown("**Scores por Criterio:**")
                for criterio, score in version.scores_criterios.items():
                    st.markdown(f"- {criterio}: {score:.1f}")

                # Cambios realizados
                if version.cambios_desde_version_anterior:
                    st.markdown("**Cambios realizados:**")
                    for cambio in version.cambios_desde_version_anterior:
                        st.markdown(f"- {cambio}")

                # Recomendaciones generadas
                if version.recomendaciones_generadas:
                    st.markdown(f"**Recomendaciones generadas:** {len(version.recomendaciones_generadas)}")

    # ==================== TAB: RECOMENDACIONES ====================
    with tab_recomendaciones:
        st.markdown("#### Gestión de Recomendaciones")

        # Subtabs para pendientes e implementadas
        sub_tab_pendientes, sub_tab_implementadas = st.tabs([
            f"⏳ Pendientes ({len(historial.recomendaciones_pendientes)})",
            f"✅ Implementadas ({len(historial.obtener_recomendaciones_implementadas())})"
        ])

        with sub_tab_pendientes:
            if not historial.recomendaciones_pendientes:
                st.success("🎉 ¡Todas las recomendaciones han sido implementadas!")
            else:
                st.markdown("##### Recomendaciones Pendientes")

                for rec in historial.recomendaciones_pendientes:
                    with st.expander(f"{rec.tipo.value.upper()} - {rec.criterio}"):
                        st.markdown(f"**Descripción:**  \n{rec.descripcion}")
                        st.markdown(f"**Impacto estimado:** {rec.impacto_estimado}")
                        st.markdown(f"**Fecha creación:** {rec.fecha_creacion.strftime('%d/%m/%Y')}")
                        st.markdown(f"**Estado:** {rec.estado.value}")

                        # Botón para marcar como implementada
                        with st.form(key=f"form_{rec.id}"):
                            st.markdown("**Marcar como implementada:**")
                            nota = st.text_area("Nota de implementación:", key=f"nota_{rec.id}")
                            cambios = st.text_area(
                                "Cambios realizados (uno por línea):",
                                key=f"cambios_{rec.id}"
                            )

                            if st.form_submit_button("✅ Marcar como implementada"):
                                cambios_list = [c.strip() for c in cambios.split('\n') if c.strip()]
                                rec.marcar_implementada(nota=nota, cambios=cambios_list)
                                historial.recomendaciones_pendientes.remove(rec)
                                st.success("✅ Recomendación marcada como implementada")
                                st.rerun()

        with sub_tab_implementadas:
            recs_implementadas = historial.obtener_recomendaciones_implementadas()

            if not recs_implementadas:
                st.info("No hay recomendaciones implementadas aún.")
            else:
                st.markdown("##### Recomendaciones Implementadas")

                for rec in recs_implementadas:
                    with st.expander(
                        f"✅ {rec.tipo.value.upper()} - {rec.criterio} "
                        f"({rec.fecha_implementacion.strftime('%d/%m/%Y') if rec.fecha_implementacion else 'N/A'})"
                    ):
                        st.markdown(f"**Descripción:**  \n{rec.descripcion}")
                        st.markdown(f"**Impacto estimado:** {rec.impacto_estimado}")
                        st.markdown(f"**Fecha creación:** {rec.fecha_creacion.strftime('%d/%m/%Y')}")

                        if rec.fecha_implementacion:
                            st.markdown(f"**Fecha implementación:** {rec.fecha_implementacion.strftime('%d/%m/%Y %H:%M')}")

                        if rec.nota_implementacion:
                            st.markdown(f"**Nota:** {rec.nota_implementacion}")

                        if rec.cambios_realizados:
                            st.markdown("**Cambios realizados:**")
                            for cambio in rec.cambios_realizados:
                                st.markdown(f"- {cambio}")

    # ==================== TAB: COMPARAR ====================
    with tab_comparar:
        st.markdown("#### Comparar Versiones")

        if historial.numero_versiones < 2:
            st.info("Se necesitan al menos 2 versiones para comparar.")
        else:
            col1, col2 = st.columns(2)

            with col1:
                v1 = st.selectbox(
                    "Versión 1:",
                    range(1, historial.numero_versiones + 1),
                    key="version1"
                )

            with col2:
                v2 = st.selectbox(
                    "Versión 2:",
                    range(1, historial.numero_versiones + 1),
                    index=historial.numero_versiones - 1,
                    key="version2"
                )

            if st.button("🔄 Comparar"):
                if v1 == v2:
                    st.warning("⚠️ Selecciona dos versiones diferentes para comparar.")
                else:
                    comparacion = gestor.comparar_versiones(proyecto.id, v1, v2)

                    # Resumen de comparación
                    st.markdown("##### Resumen de Comparación")

                    col_a, col_b, col_c = st.columns(3)

                    with col_a:
                        st.metric(
                            f"Versión {v1}",
                            f"{comparacion['version_anterior']['score']:.1f}"
                        )

                    with col_b:
                        st.metric(
                            "Mejora",
                            f"{comparacion['mejora']['diferencia_puntos']:+.1f}",
                            delta=f"{comparacion['mejora']['porcentaje']:+.1f}%"
                        )

                    with col_c:
                        st.metric(
                            f"Versión {v2}",
                            f"{comparacion['version_actual']['score']:.1f}"
                        )

                    # Diferencias por criterio
                    st.markdown("---")
                    st.markdown("##### Diferencias por Criterio")

                    for criterio, dif in comparacion['diferencias_por_criterio'].items():
                        col_x, col_y, col_z = st.columns([2, 1, 1])

                        with col_x:
                            st.markdown(f"**{criterio}**")

                        with col_y:
                            st.markdown(
                                f"{dif['version_anterior']:.1f} → {dif['version_actual']:.1f}"
                            )

                        with col_z:
                            color = "🟢" if dif['diferencia'] > 0 else "🔴" if dif['diferencia'] < 0 else "⚪"
                            st.markdown(
                                f"{color} {dif['diferencia']:+.1f} ({dif['porcentaje']:+.1f}%)"
                            )

                    # Cambios realizados
                    if comparacion['cambios_realizados']:
                        st.markdown("---")
                        st.markdown("##### Cambios Realizados")
                        for cambio in comparacion['cambios_realizados']:
                            st.markdown(f"- {cambio}")

    # ==================== TAB: EXPORTAR ====================
    with tab_exportar:
        st.markdown("#### Exportar Reporte de Trazabilidad")

        st.markdown("""
        Genera un reporte completo que incluye:
        - Historial completo de versiones
        - Todas las recomendaciones generadas
        - Recomendaciones implementadas con fechas
        - Estadísticas de mejora
        - Timeline de eventos
        """)

        if st.button("📥 Generar Reporte de Trazabilidad"):
            reporte = gestor.generar_reporte_trazabilidad(proyecto.id)

            if 'error' in reporte:
                st.error(f"❌ {reporte['error']}")
            else:
                # Mostrar reporte en formato JSON estructurado
                st.json(reporte)

                st.success("✅ Reporte generado. Este reporte será incluido automáticamente en las exportaciones PDF y Word.")
                st.info("💡 Los exportadores PDF y Word incluirán automáticamente esta información de trazabilidad.")
