"""
Servicio de Asistente IA con Google Gemini.
Proporciona análisis inteligente de proyectos y responde preguntas contextuales.
"""
import os
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from models.proyecto import ProyectoSocial
from models.evaluacion import ResultadoEvaluacion

# Asegurar que las variables de entorno estén cargadas
# Buscar el archivo .env en la raíz del proyecto (para desarrollo local)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Intentar importar streamlit para acceso a secrets (Streamlit Cloud)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class AsistenteIA:
    """
    Asistente inteligente para análisis de proyectos sociales.
    Usa Google Gemini para proporcionar insights y responder preguntas.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el asistente IA.

        Args:
            api_key: API key de Google Gemini (si no se proporciona, lee de .env o st.secrets)
        """
        # Recargar .env para asegurar que está actualizado (desarrollo local)
        load_dotenv(dotenv_path=env_path, override=True)

        # Obtener API key de múltiples fuentes (en orden de prioridad):
        # 1. Parámetro directo
        # 2. Streamlit secrets (Streamlit Cloud)
        # 3. Variable de entorno (local con .env)
        self.api_key = None

        if api_key:
            self.api_key = api_key
        elif STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
            try:
                if 'GOOGLE_API_KEY' in st.secrets:
                    self.api_key = st.secrets['GOOGLE_API_KEY']
            except:
                pass  # Si no hay secrets.toml, usar variable de entorno

        if not self.api_key:
            self.api_key = os.getenv('GOOGLE_API_KEY')

        # Debug: imprimir información
        fuente = "Variable de entorno"
        if api_key:
            fuente = "Parámetro directo"
        elif self.api_key and self.api_key != os.getenv('GOOGLE_API_KEY'):
            fuente = "Streamlit Secrets"

        print(f"DEBUG - API Key cargada: {self.api_key[:20] if self.api_key else 'None'}...")
        print(f"DEBUG - Fuente: {fuente}")
        print(f"DEBUG - Ruta .env: {env_path}")
        print(f"DEBUG - .env existe: {env_path.exists()}")

        # Validación simplificada
        if not self.api_key:
            raise ValueError(
                "API key de Google Gemini no encontrada. "
                "Configura GOOGLE_API_KEY en:\n"
                "- Desarrollo local: archivo .env en la raíz del proyecto\n"
                "- Streamlit Cloud: Settings > Secrets"
            )

        # Configurar Gemini
        genai.configure(api_key=self.api_key)

        # Usar Gemini 2.5 Flash (modelo estable, rápido y gratis)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # Historial de conversación
        self.historial_chat: List[Dict[str, str]] = []

    def _construir_contexto_proyecto(self, proyecto: ProyectoSocial,
                                     resultado: Optional[ResultadoEvaluacion] = None) -> str:
        """
        Construye el contexto completo de un proyecto para el LLM.

        Args:
            proyecto: Proyecto a analizar
            resultado: Resultado de evaluación (opcional)

        Returns:
            String con el contexto del proyecto
        """
        # Construir ubicación legible
        ubicacion = f"{', '.join(proyecto.departamentos)}"
        if proyecto.municipios:
            ubicacion += f" (Municipios: {', '.join(proyecto.municipios)})"

        contexto = f"""
## Información del Proyecto: {proyecto.nombre}

**Datos Generales:**
- ID: {proyecto.id}
- Organización: {proyecto.organizacion}
- Descripción: {proyecto.descripcion}
- Ubicación: {ubicacion}
- Área Geográfica: {proyecto.area_geografica.value}
- Población Objetivo: {proyecto.poblacion_objetivo}
- Duración: {proyecto.duracion_meses} meses ({proyecto.duracion_años:.1f} años)
- ODS Vinculados: {', '.join(proyecto.ods_vinculados)}
- Estado: {proyecto.estado.value}

**Financiamiento y Beneficiarios:**
- Presupuesto Total: ${proyecto.presupuesto_total:,.0f}
- Beneficiarios Directos: {proyecto.beneficiarios_directos:,}
- Beneficiarios Indirectos: {proyecto.beneficiarios_indirectos:,}
- Beneficiarios Totales: {proyecto.beneficiarios_totales:,}
- Costo por Beneficiario: ${proyecto.presupuesto_por_beneficiario:,.2f}
"""

        # Agregar indicadores de impacto si existen
        if proyecto.indicadores_impacto:
            contexto += "\n**Indicadores de Impacto:**\n"
            for indicador, valor in proyecto.indicadores_impacto.items():
                contexto += f"- {indicador}: {valor}\n"

        # Agregar resultado de evaluación si existe
        if resultado:
            contexto += f"""
**Evaluación del Sistema:**
- Score Final: {resultado.score_final:.1f}/100
- Recomendación: {resultado.recomendacion}

**Scores por Criterio:**
"""
            for criterio, detalle in resultado.detalle_criterios.items():
                contexto += f"- {criterio}: {detalle['score_base']:.1f} (peso: {detalle['peso']*100:.0f}%)\n"

        return contexto

    def _construir_contexto_cartera(self, proyectos: List[ProyectoSocial],
                                   resultados: Optional[List[ResultadoEvaluacion]] = None) -> str:
        """
        Construye el contexto de una cartera de proyectos.

        Args:
            proyectos: Lista de proyectos
            resultados: Lista de resultados de evaluación (opcional)

        Returns:
            String con el contexto de la cartera
        """
        contexto = f"""
## Cartera de Proyectos

**Resumen General:**
- Total de proyectos: {len(proyectos)}
- Presupuesto total: ${sum(p.presupuesto_total for p in proyectos):,.0f}
- Beneficiarios totales: {sum(p.beneficiarios_directos for p in proyectos):,}

**Proyectos en la Cartera:**
"""

        for i, proyecto in enumerate(proyectos, 1):
            score_info = ""
            if resultados and i-1 < len(resultados):
                score_info = f" | Score: {resultados[i-1].score_final:.1f}"

            # Construir ubicación legible
            ubicacion = ', '.join(proyecto.departamentos)
            if proyecto.municipios:
                ubicacion += f" ({len(proyecto.municipios)} municipios)"

            contexto += f"""
{i}. **{proyecto.nombre}**
   - Organización: {proyecto.organizacion}
   - Ubicación: {ubicacion}
   - Presupuesto: ${proyecto.presupuesto_total:,.0f}
   - Beneficiarios: {proyecto.beneficiarios_totales:,}
   - Duración: {proyecto.duracion_meses} meses{score_info}
"""

        return contexto

    def consultar_proyecto(self, pregunta: str, proyecto: ProyectoSocial,
                          resultado: Optional[ResultadoEvaluacion] = None) -> str:
        """
        Responde preguntas sobre un proyecto específico.

        Args:
            pregunta: Pregunta del usuario
            proyecto: Proyecto sobre el que se consulta
            resultado: Resultado de evaluación (opcional)

        Returns:
            Respuesta del asistente
        """
        contexto = self._construir_contexto_proyecto(proyecto, resultado)

        prompt = f"""Eres un experto en evaluación de proyectos sociales. Un usuario te está consultando sobre un proyecto.

{contexto}

**Sistema de Evaluación:**
El sistema evalúa proyectos con 4 criterios:
1. **Costo-Efectividad** (25%): Mide el SROI, costo por beneficiario, y ubicación prioritaria (ZOMAC/PDET)
2. **Relacionamiento con Stakeholders** (25%): Evalúa cantidad, compromiso y diversidad de stakeholders
3. **Probabilidad de Aprobación** (25%): Considera probabilidad y cumplimiento regulatorio
4. **Evaluación de Riesgos** (25%): Analiza riesgos identificados, planes de mitigación y gravedad

**Pregunta del usuario:**
{pregunta}

**Instrucciones:**
- Responde de manera clara, concisa y profesional
- Usa los datos del proyecto para fundamentar tu respuesta
- Si la pregunta es sobre mejoras, sé específico y práctico
- Si preguntan por qué tiene bajo score en un criterio, explica con datos
- Usa formato markdown para mejor legibilidad
- No inventes datos, usa solo la información proporcionada
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error al consultar el asistente: {str(e)}"

    def consultar_cartera(self, pregunta: str, proyectos: List[ProyectoSocial],
                         resultados: Optional[List[ResultadoEvaluacion]] = None) -> str:
        """
        Responde preguntas sobre una cartera de proyectos.

        Args:
            pregunta: Pregunta del usuario
            proyectos: Lista de proyectos
            resultados: Lista de resultados de evaluación (opcional)

        Returns:
            Respuesta del asistente
        """
        contexto = self._construir_contexto_cartera(proyectos, resultados)

        prompt = f"""Eres un experto en evaluación de proyectos sociales. Un usuario te está consultando sobre una cartera de proyectos.

{contexto}

**Sistema de Evaluación:**
El sistema evalúa proyectos con 4 criterios (cada uno 25%):
1. **Costo-Efectividad**: SROI, costo por beneficiario, ubicación prioritaria
2. **Relacionamiento con Stakeholders**: Cantidad, compromiso, diversidad
3. **Probabilidad de Aprobación**: Probabilidad, cumplimiento regulatorio
4. **Evaluación de Riesgos**: Riesgos, planes de mitigación, gravedad

**Pregunta del usuario:**
{pregunta}

**Instrucciones:**
- Proporciona análisis comparativo entre proyectos cuando sea relevante
- Identifica patrones, tendencias y oportunidades
- Si preguntan por los mejores, usa los scores si están disponibles
- Sé específico con nombres de proyectos y datos
- Usa formato markdown y listas para claridad
- No inventes datos, usa solo la información proporcionada
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error al consultar el asistente: {str(e)}"

    def generar_resumen_ejecutivo(self, proyecto: ProyectoSocial,
                                  resultado: ResultadoEvaluacion) -> str:
        """
        Genera un resumen ejecutivo del proyecto.

        Args:
            proyecto: Proyecto a resumir
            resultado: Resultado de evaluación

        Returns:
            Resumen ejecutivo en formato markdown
        """
        contexto = self._construir_contexto_proyecto(proyecto, resultado)

        prompt = f"""Genera un resumen ejecutivo profesional para este proyecto social.

{contexto}

**Formato del resumen:**
1. **Síntesis del Proyecto** (2-3 líneas)
2. **Fortalezas Clave** (3 puntos)
3. **Áreas de Oportunidad** (2-3 puntos)
4. **Recomendación General** (1 párrafo)

Usa formato markdown, sé conciso y profesional. Base todo en los datos proporcionados.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error al generar resumen: {str(e)}"

    def analizar_tendencias_cartera(self, proyectos: List[ProyectoSocial],
                                   resultados: List[ResultadoEvaluacion]) -> str:
        """
        Analiza tendencias en la cartera de proyectos.

        Args:
            proyectos: Lista de proyectos
            resultados: Lista de resultados de evaluación

        Returns:
            Análisis de tendencias
        """
        contexto = self._construir_contexto_cartera(proyectos, resultados)

        prompt = f"""Analiza las tendencias y patrones en esta cartera de proyectos sociales.

{contexto}

**Proporciona:**
1. **Patrones Comunes**: Identifica características compartidas
2. **Distribución de Scores**: Analiza la distribución de calificaciones
3. **Áreas de Fortaleza**: Qué hace bien la cartera en general
4. **Áreas de Mejora**: Dónde hay oportunidades de optimización
5. **Recomendaciones Estratégicas**: 3-4 recomendaciones para la cartera completa

Usa formato markdown con listas y sé específico con datos.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error al analizar tendencias: {str(e)}"

    def comparar_proyectos(self, proyecto1: ProyectoSocial, proyecto2: ProyectoSocial,
                          resultado1: Optional[ResultadoEvaluacion] = None,
                          resultado2: Optional[ResultadoEvaluacion] = None) -> str:
        """
        Compara dos proyectos en detalle.

        Args:
            proyecto1: Primer proyecto
            proyecto2: Segundo proyecto
            resultado1: Resultado del primer proyecto (opcional)
            resultado2: Resultado del segundo proyecto (opcional)

        Returns:
            Comparación detallada
        """
        contexto1 = self._construir_contexto_proyecto(proyecto1, resultado1)
        contexto2 = self._construir_contexto_proyecto(proyecto2, resultado2)

        prompt = f"""Compara estos dos proyectos sociales en detalle:

# PROYECTO 1:
{contexto1}

# PROYECTO 2:
{contexto2}

**Proporciona:**
1. **Comparación de Scores** (si disponibles)
2. **Diferencias Clave**: ¿En qué se diferencian?
3. **Fortalezas Relativas**: ¿Qué hace mejor cada uno?
4. **Recomendación**: ¿Cuál es preferible y por qué?

Usa formato markdown con tablas si es apropiado. Sé específico con datos.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error al comparar proyectos: {str(e)}"

    def chat(self, mensaje: str, contexto: Optional[str] = None) -> str:
        """
        Chat conversacional con el asistente.

        Args:
            mensaje: Mensaje del usuario
            contexto: Contexto adicional (opcional)

        Returns:
            Respuesta del asistente
        """
        # Agregar mensaje al historial
        self.historial_chat.append({
            'role': 'user',
            'content': mensaje,
            'timestamp': datetime.now().isoformat()
        })

        # Construir prompt con contexto e historial
        prompt = f"""Eres un experto asistente en evaluación de proyectos sociales.

{"CONTEXTO:\n" + contexto if contexto else ""}

**Historial de conversación reciente:**
"""
        # Incluir últimos 5 mensajes del historial
        for msg in self.historial_chat[-5:]:
            prompt += f"\n{msg['role']}: {msg['content']}"

        prompt += f"""

**Nuevo mensaje del usuario:**
{mensaje}

Responde de manera profesional, clara y útil. Usa formato markdown.
"""

        try:
            response = self.model.generate_content(prompt)
            respuesta = response.text

            # Agregar respuesta al historial
            self.historial_chat.append({
                'role': 'assistant',
                'content': respuesta,
                'timestamp': datetime.now().isoformat()
            })

            return respuesta
        except Exception as e:
            return f"❌ Error en el chat: {str(e)}"

    def limpiar_historial(self):
        """Limpia el historial de conversación."""
        self.historial_chat = []
