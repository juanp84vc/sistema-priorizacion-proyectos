"""
Página de Historial de Análisis IA.
"""
import streamlit as st
from datetime import datetime
from servicios.historial_ia import HistorialIA
from servicios.exportador_ia import ExportadorIA
import base64


def show():
    """Muestra la página del Historial de Análisis IA."""
    st.markdown("### 📚 Historial de Análisis IA")

    # Inicializar servicios
    try:
        historial = HistorialIA()
        exportador = ExportadorIA()
    except Exception as e:
        st.error(f"❌ Error al inicializar servicios: {str(e)}")
        return

    # Estadísticas generales
    with st.expander("📊 Estadísticas Generales", expanded=False):
        try:
            stats = historial.obtener_estadisticas()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Consultas", stats['total_consultas'])
            with col2:
                if stats['por_llm']:
                    llm_principal = max(stats['por_llm'].items(), key=lambda x: x[1])
                    st.metric("LLM Más Usado", f"{llm_principal[0]} ({llm_principal[1]})")
                else:
                    st.metric("LLM Más Usado", "N/A")
            with col3:
                st.metric("Tipos de Análisis", len(stats['por_tipo']))

            # Distribución por tipo
            if stats['por_tipo']:
                st.markdown("**Consultas por Tipo:**")
                for tipo, cantidad in sorted(stats['por_tipo'].items(), key=lambda x: x[1], reverse=True):
                    st.write(f"- {tipo.replace('_', ' ').title()}: {cantidad}")

            # Top proyectos
            if stats['proyectos_top']:
                st.markdown("**Proyectos Más Consultados:**")
                for i, proyecto in enumerate(stats['proyectos_top'][:5], 1):
                    st.write(f"{i}. {proyecto['proyecto']} ({proyecto['consultas']} consultas)")

        except Exception as e:
            st.error(f"Error al cargar estadísticas: {str(e)}")

    st.markdown("---")

    # Filtros
    st.markdown("#### 🔍 Buscar y Filtrar")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        termino_busqueda = st.text_input(
            "Buscar en consultas",
            placeholder="Escribe para buscar en preguntas y respuestas...",
            help="Busca por texto en preguntas y respuestas"
        )

    with col2:
        tipo_filtro = st.selectbox(
            "Tipo de Análisis",
            ["Todos", "consulta_proyecto", "consulta_cartera", "resumen_ejecutivo",
             "tendencias_cartera", "comparacion_proyectos", "chat"]
        )

    with col3:
        limite = st.number_input("Resultados", min_value=10, max_value=100, value=20, step=10)

    # Obtener consultas
    try:
        if termino_busqueda:
            consultas = historial.buscar_consultas(termino_busqueda, limite=limite)
        elif tipo_filtro != "Todos":
            consultas = historial.obtener_consultas_recientes(limite=limite, tipo_analisis=tipo_filtro)
        else:
            consultas = historial.obtener_consultas_recientes(limite=limite)

        st.markdown(f"**{len(consultas)} consultas encontradas**")

        if consultas:
            st.markdown("---")

            # Mostrar consultas
            for consulta in consultas:
                with st.expander(
                    f"🔹 {consulta['tipo_analisis'].replace('_', ' ').title()} - "
                    f"{datetime.fromisoformat(consulta['timestamp']).strftime('%d/%m/%Y %H:%M')}",
                    expanded=False
                ):
                    # Metadatos
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if consulta.get('proyecto_nombre'):
                            st.markdown(f"**Proyecto:** {consulta['proyecto_nombre']}")
                    with col2:
                        if consulta.get('llm_provider'):
                            llm_text = consulta['llm_provider']
                            if consulta.get('llm_model'):
                                llm_text += f" ({consulta['llm_model']})"
                            st.markdown(f"**LLM:** {llm_text}")
                    with col3:
                        st.markdown(f"**ID:** {consulta['id']}")

                    st.markdown("---")

                    # Pregunta
                    st.markdown("**❓ Pregunta:**")
                    st.info(consulta['pregunta'])

                    # Respuesta
                    st.markdown("**💡 Análisis:**")
                    st.markdown(consulta['respuesta'])

                    # Botones de exportación
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

                    with col1:
                        # Exportar a PDF
                        try:
                            pdf_bytes = exportador.exportar_a_pdf(consulta)
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"analisis_{consulta['id']}_{timestamp}.pdf"

                            st.download_button(
                                label="📄 PDF",
                                data=pdf_bytes,
                                file_name=filename,
                                mime="application/pdf",
                                key=f"pdf_{consulta['id']}"
                            )
                        except Exception as e:
                            st.error(f"Error PDF: {str(e)}")

                    with col2:
                        # Exportar a Word
                        try:
                            docx_bytes = exportador.exportar_a_docx(consulta)
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"analisis_{consulta['id']}_{timestamp}.docx"

                            st.download_button(
                                label="📝 Word",
                                data=docx_bytes,
                                file_name=filename,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"docx_{consulta['id']}"
                            )
                        except Exception as e:
                            st.error(f"Error Word: {str(e)}")

                    with col3:
                        # Exportar a Markdown
                        try:
                            md_content = exportador.exportar_a_markdown(consulta)
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"analisis_{consulta['id']}_{timestamp}.md"

                            st.download_button(
                                label="📋 MD",
                                data=md_content,
                                file_name=filename,
                                mime="text/markdown",
                                key=f"md_{consulta['id']}"
                            )
                        except Exception as e:
                            st.error(f"Error MD: {str(e)}")
        else:
            st.info("No se encontraron consultas con los filtros aplicados.")

    except Exception as e:
        st.error(f"❌ Error al cargar consultas: {str(e)}")
        st.code(str(e))
