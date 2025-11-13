"""
Página del Asistente IA para análisis inteligente de proyectos.
"""
import streamlit as st
from servicios.asistente_ia import AsistenteIA


def show():
    """Muestra la página del Asistente IA."""
    st.markdown("### 🤖 Asistente IA - Análisis Inteligente de Proyectos")

    # Botón para reinicializar el asistente (útil si se actualizó el .env)
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Reiniciar", help="Recarga la configuración del asistente"):
            if 'asistente_ia' in st.session_state:
                del st.session_state.asistente_ia
            if 'chat_history' in st.session_state:
                del st.session_state.chat_history
            st.rerun()

    st.markdown("---")

    # Inicializar asistente en session_state
    if 'asistente_ia' not in st.session_state:
        try:
            st.session_state.asistente_ia = AsistenteIA()
            st.session_state.chat_history = []
        except ValueError as e:
            st.error(f"⚠️ {str(e)}")
            st.info("""
            **Cómo configurar:**
            1. Obtén tu API key en: https://aistudio.google.com/app/apikey
            2. Edita el archivo `.env` en la raíz del proyecto
            3. Reemplaza `YOUR_ACTUAL_API_KEY_HERE` con tu API key real
            4. Haz clic en el botón "🔄 Reiniciar" arriba
            """)
            return
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")
            st.code(str(e))
            return

    asistente = st.session_state.asistente_ia

    # Verificar que hay proyectos
    if not st.session_state.proyectos:
        st.info("📭 No hay proyectos registrados. Crea algunos proyectos primero para usar el asistente.")
        return

    # Tabs principales
    tab_consulta, tab_analisis, tab_comparacion, tab_chat = st.tabs([
        "💬 Consultar Proyecto", "📊 Análisis de Cartera", "🔄 Comparar Proyectos", "💭 Chat Libre"
    ])

    # ==================== TAB: CONSULTAR PROYECTO ====================
    with tab_consulta:
        st.markdown("#### Consulta sobre un Proyecto Específico")
        st.markdown("Haz preguntas sobre un proyecto y obtén respuestas inteligentes basadas en sus datos.")

        # Selector de proyecto
        proyectos_dict = {p.nombre: p for p in st.session_state.proyectos}
        proyecto_nombre = st.selectbox(
            "Selecciona un proyecto:",
            list(proyectos_dict.keys()),
            key="proyecto_consulta"
        )

        proyecto = proyectos_dict[proyecto_nombre]

        # Mostrar info básica del proyecto
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Presupuesto", f"${proyecto.presupuesto_total:,.0f}")
        with col2:
            st.metric("Beneficiarios", f"{proyecto.beneficiarios_directos:,}")
        with col3:
            st.metric("Duración", f"{proyecto.duracion_meses} meses")

        st.markdown("---")

        # Preguntas sugeridas
        st.markdown("**Preguntas sugeridas:**")
        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("¿Por qué tiene este score?", key="pregunta1"):
                st.session_state.pregunta_proyecto = "¿Por qué este proyecto tiene este score? Explica en detalle."

            if st.button("¿Qué debo mejorar primero?", key="pregunta2"):
                st.session_state.pregunta_proyecto = "¿Cuál es el aspecto más importante que debo mejorar en este proyecto y por qué?"

        with col_b:
            if st.button("¿Cuáles son sus fortalezas?", key="pregunta3"):
                st.session_state.pregunta_proyecto = "¿Cuáles son las principales fortalezas de este proyecto?"

            if st.button("Genera un resumen ejecutivo", key="pregunta4"):
                st.session_state.pregunta_proyecto = "__RESUMEN_EJECUTIVO__"

        # Campo de pregunta personalizada
        pregunta = st.text_area(
            "O escribe tu propia pregunta:",
            value=st.session_state.get('pregunta_proyecto', ''),
            height=100,
            key="pregunta_input"
        )

        if st.button("🔍 Consultar", type="primary", key="btn_consultar"):
            if not pregunta:
                st.warning("⚠️ Por favor escribe una pregunta.")
            else:
                with st.spinner("🤖 Analizando proyecto..."):
                    # Obtener resultado de evaluación si existe
                    resultado = None
                    if hasattr(st.session_state, 'resultados_evaluacion'):
                        resultado = next(
                            (r for r in st.session_state.resultados_evaluacion if r.proyecto_id == proyecto.id),
                            None
                        )

                    # Caso especial: resumen ejecutivo
                    if pregunta == "__RESUMEN_EJECUTIVO__":
                        if resultado:
                            respuesta = asistente.generar_resumen_ejecutivo(proyecto, resultado)
                        else:
                            st.warning("⚠️ Primero evalúa este proyecto en 'Evaluar Cartera' para generar un resumen ejecutivo completo.")
                            respuesta = None
                    else:
                        respuesta = asistente.consultar_proyecto(pregunta, proyecto, resultado)

                    if respuesta:
                        st.markdown("#### 💡 Respuesta del Asistente:")
                        st.markdown(respuesta)

                # Limpiar pregunta
                if 'pregunta_proyecto' in st.session_state:
                    del st.session_state.pregunta_proyecto

    # ==================== TAB: ANÁLISIS DE CARTERA ====================
    with tab_analisis:
        st.markdown("#### Análisis Inteligente de Cartera")
        st.markdown("Obtén insights sobre toda tu cartera de proyectos.")

        # Selector de tipo de análisis
        tipo_analisis = st.selectbox(
            "Tipo de análisis:",
            [
                "Tendencias y Patrones",
                "Ranking de Proyectos",
                "Análisis de Riesgos",
                "Oportunidades de Mejora",
                "Consulta Personalizada"
            ],
            key="tipo_analisis"
        )

        # Pregunta según tipo
        preguntas_predefinidas = {
            "Tendencias y Patrones": "Analiza las tendencias y patrones comunes en esta cartera de proyectos. ¿Qué características comparten?",
            "Ranking de Proyectos": "¿Cuáles son los 5 mejores proyectos de la cartera y por qué destacan?",
            "Análisis de Riesgos": "Identifica los proyectos con mayor riesgo en la cartera y explica qué riesgos enfrentan.",
            "Oportunidades de Mejora": "¿Dónde están las mayores oportunidades de mejora en esta cartera? Proporciona 5 recomendaciones estratégicas."
        }

        if tipo_analisis == "Consulta Personalizada":
            pregunta_cartera = st.text_area(
                "Escribe tu pregunta sobre la cartera:",
                height=100,
                key="pregunta_cartera_custom"
            )
        else:
            pregunta_cartera = preguntas_predefinidas[tipo_analisis]
            st.info(f"**Pregunta:** {pregunta_cartera}")

        # Opción de análisis con tendencias (requiere evaluación)
        analizar_con_scores = st.checkbox(
            "Incluir análisis de tendencias de scores (requiere haber evaluado los proyectos)",
            key="analizar_tendencias"
        )

        if st.button("📊 Analizar Cartera", type="primary", key="btn_analizar_cartera"):
            if not pregunta_cartera:
                st.warning("⚠️ Por favor escribe una pregunta.")
            else:
                with st.spinner("🤖 Analizando cartera..."):
                    # Obtener resultados si están disponibles
                    resultados = st.session_state.get('resultados_evaluacion', None) if analizar_con_scores else None

                    if analizar_con_scores and tipo_analisis == "Tendencias y Patrones" and resultados:
                        # Usar método especial para tendencias
                        respuesta = asistente.analizar_tendencias_cartera(
                            st.session_state.proyectos,
                            resultados
                        )
                    else:
                        # Consulta general de cartera
                        respuesta = asistente.consultar_cartera(
                            pregunta_cartera,
                            st.session_state.proyectos,
                            resultados
                        )

                    st.markdown("#### 💡 Análisis del Asistente:")
                    st.markdown(respuesta)

    # ==================== TAB: COMPARAR PROYECTOS ====================
    with tab_comparacion:
        st.markdown("#### Comparación Inteligente de Proyectos")
        st.markdown("Compara dos proyectos lado a lado con análisis IA.")

        col_comp1, col_comp2 = st.columns(2)

        proyectos_dict = {p.nombre: p for p in st.session_state.proyectos}

        with col_comp1:
            proyecto1_nombre = st.selectbox(
                "Proyecto 1:",
                list(proyectos_dict.keys()),
                key="proyecto_comp1"
            )

        with col_comp2:
            proyecto2_nombre = st.selectbox(
                "Proyecto 2:",
                list(proyectos_dict.keys()),
                key="proyecto_comp2"
            )

        if proyecto1_nombre == proyecto2_nombre:
            st.warning("⚠️ Por favor selecciona dos proyectos diferentes.")
        else:
            proyecto1 = proyectos_dict[proyecto1_nombre]
            proyecto2 = proyectos_dict[proyecto2_nombre]

            # Mostrar comparación básica
            st.markdown("---")
            st.markdown("##### Comparación Rápida")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**{proyecto1.nombre}**")
                st.metric("Presupuesto", f"${proyecto1.presupuesto_total:,.0f}")
                st.metric("Beneficiarios", f"{proyecto1.beneficiarios_directos:,}")
                st.metric("Duración", f"{proyecto1.duracion_meses} meses")

            with col2:
                st.markdown(f"**{proyecto2.nombre}**")
                st.metric("Presupuesto", f"${proyecto2.presupuesto_total:,.0f}")
                st.metric("Beneficiarios", f"{proyecto2.beneficiarios_directos:,}")
                st.metric("Duración", f"{proyecto2.duracion_meses} meses")

            st.markdown("---")

            if st.button("🔄 Comparar con IA", type="primary", key="btn_comparar"):
                with st.spinner("🤖 Comparando proyectos..."):
                    # Obtener resultados si existen
                    resultado1 = None
                    resultado2 = None

                    if hasattr(st.session_state, 'resultados_evaluacion'):
                        resultado1 = next(
                            (r for r in st.session_state.resultados_evaluacion if r.proyecto_id == proyecto1.id),
                            None
                        )
                        resultado2 = next(
                            (r for r in st.session_state.resultados_evaluacion if r.proyecto_id == proyecto2.id),
                            None
                        )

                    respuesta = asistente.comparar_proyectos(
                        proyecto1, proyecto2,
                        resultado1, resultado2
                    )

                    st.markdown("#### 💡 Comparación del Asistente:")
                    st.markdown(respuesta)

    # ==================== TAB: CHAT LIBRE ====================
    with tab_chat:
        st.markdown("#### Chat Conversacional")
        st.markdown("Conversa libremente con el asistente sobre tus proyectos.")

        # Mostrar historial de chat
        if st.session_state.chat_history:
            st.markdown("##### 💬 Historial de Conversación")

            for mensaje in st.session_state.chat_history:
                if mensaje['role'] == 'user':
                    st.markdown(f"**🧑 Tú:** {mensaje['content']}")
                else:
                    st.markdown(f"**🤖 Asistente:** {mensaje['content']}")
                st.markdown("---")

        # Campo de chat
        mensaje_chat = st.text_area(
            "Escribe tu mensaje:",
            height=100,
            key="mensaje_chat"
        )

        col_send, col_clear = st.columns([3, 1])

        with col_send:
            if st.button("💬 Enviar", type="primary", key="btn_chat"):
                if mensaje_chat:
                    with st.spinner("🤖 Pensando..."):
                        # Construir contexto básico
                        contexto = f"""Tienes acceso a información sobre {len(st.session_state.proyectos)} proyectos sociales.
El usuario puede preguntarte sobre proyectos específicos, pedir análisis, o hacer consultas generales."""

                        respuesta = asistente.chat(mensaje_chat, contexto)

                        # Agregar al historial local
                        st.session_state.chat_history.append({
                            'role': 'user',
                            'content': mensaje_chat
                        })
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': respuesta
                        })

                        st.rerun()

        with col_clear:
            if st.button("🗑️ Limpiar", key="btn_clear_chat"):
                st.session_state.chat_history = []
                asistente.limpiar_historial()
                st.rerun()
