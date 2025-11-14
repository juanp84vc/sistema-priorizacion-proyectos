"""
Servicio de Asistente IA con múltiples LLMs (Claude, OpenAI, Gemini).
Proporciona análisis inteligente de proyectos y responde preguntas contextuales.
"""
import os
import hashlib
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from models.proyecto import ProyectoSocial
from models.evaluacion import ResultadoEvaluacion
from servicios.llm_provider import LLMProvider
from servicios.historial_ia import HistorialIA

# Configuración de entorno
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)


class AsistenteIA:
    """
    Asistente inteligente para análisis de proyectos sociales.
    Soporta múltiples LLMs: Claude (recomendado), OpenAI (ChatGPT), y Gemini.
    """

    def __init__(self, provider: Optional[str] = None, guardar_historial: bool = True):
        """
        Inicializa el asistente IA con proveedor de LLM configurable.

        Args:
            provider: Proveedor de LLM ('claude', 'openai', 'gemini')
                     Si es None, usa LLM_PROVIDER del .env (default: claude)
            guardar_historial: Si debe guardar automáticamente las consultas en la base de datos
        """
        # Recargar .env para asegurar que está actualizado
        load_dotenv(dotenv_path=env_path, override=True)

        # Inicializar proveedor de LLM
        try:
            self.llm = LLMProvider(provider=provider)
            llm_info = self.llm.get_info()
            print(f"✅ Asistente IA inicializado con {llm_info['provider']} ({llm_info['model']})")
        except Exception as e:
            raise ValueError(f"Error al inicializar LLM: {str(e)}")

        # Historial de conversación
        self.historial_chat: List[Dict[str, str]] = []

        # Caché de respuestas (clave: hash de pregunta+contexto, valor: {respuesta, timestamp})
        self._cache: Dict[str, Dict] = {}
        self._cache_ttl = timedelta(minutes=30)  # TTL de 30 minutos

        # Servicio de historial persistente
        self.guardar_historial = guardar_historial
        if self.guardar_historial:
            try:
                self.historial_db = HistorialIA()
            except Exception as e:
                print(f"⚠️ No se pudo inicializar historial persistente: {str(e)}")
                self.guardar_historial = False

    def _generar_cache_key(self, *args) -> str:
        """Genera una clave de caché única basada en los argumentos."""
        content = '|'.join(str(arg) for arg in args)
        return hashlib.md5(content.encode()).hexdigest()

    def _get_from_cache(self, key: str) -> Optional[str]:
        """Obtiene una respuesta del caché si existe y no ha expirado."""
        if key in self._cache:
            cached = self._cache[key]
            if datetime.now() - cached['timestamp'] < self._cache_ttl:
                return cached['respuesta']
            else:
                # Eliminar entrada expirada
                del self._cache[key]
        return None

    def _save_to_cache(self, key: str, respuesta: str):
        """Guarda una respuesta en el caché."""
        self._cache[key] = {
            'respuesta': respuesta,
            'timestamp': datetime.now()
        }

    def limpiar_cache(self):
        """Limpia el caché de respuestas."""
        self._cache = {}

    def _guardar_en_historial(self, pregunta: str, respuesta: str, tipo_analisis: str,
                              proyecto_id: Optional[str] = None,
                              proyecto_nombre: Optional[str] = None) -> Optional[int]:
        """
        Guarda una consulta en el historial persistente si está habilitado.

        Args:
            pregunta: Pregunta del usuario
            respuesta: Respuesta del asistente
            tipo_analisis: Tipo de análisis realizado
            proyecto_id: ID del proyecto (opcional)
            proyecto_nombre: Nombre del proyecto (opcional)

        Returns:
            ID de la consulta guardada o None si no se guardó
        """
        if not self.guardar_historial:
            return None

        try:
            llm_info = self.llm.get_info()
            consulta_id = self.historial_db.guardar_consulta(
                pregunta=pregunta,
                respuesta=respuesta,
                tipo_analisis=tipo_analisis,
                proyecto_id=proyecto_id,
                proyecto_nombre=proyecto_nombre,
                llm_provider=llm_info['provider'],
                llm_model=llm_info['model']
            )
            return consulta_id
        except Exception as e:
            print(f"⚠️ Error al guardar en historial: {str(e)}")
            return None

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
                                   resultados: Optional[List[ResultadoEvaluacion]] = None,
                                   compacto: bool = False) -> str:
        """
        Construye el contexto de una cartera de proyectos.

        Args:
            proyectos: Lista de proyectos
            resultados: Lista de resultados de evaluación (opcional)
            compacto: Si True, genera versión reducida para ahorrar tokens

        Returns:
            String con el contexto de la cartera
        """
        if compacto:
            # Versión compacta: solo datos esenciales
            contexto = f"""Cartera: {len(proyectos)} proyectos | Presupuesto: ${sum(p.presupuesto_total for p in proyectos):,.0f} | Beneficiarios: {sum(p.beneficiarios_directos for p in proyectos):,}\n\n"""

            for i, proyecto in enumerate(proyectos, 1):
                score_info = ""
                if resultados and i-1 < len(resultados):
                    score_info = f" | Score: {resultados[i-1].score_final:.1f}"

                ubicacion = ', '.join(proyecto.departamentos[:2])  # Solo primeros 2 departamentos
                contexto += f"{i}. {proyecto.nombre} | {proyecto.organizacion} | {ubicacion} | ${proyecto.presupuesto_total:,.0f} | {proyecto.beneficiarios_totales:,} benef. | {proyecto.duracion_meses}m{score_info}\n"

            return contexto

        # Versión completa (original)
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
        Responde preguntas sobre un proyecto específico (con caché).

        Args:
            pregunta: Pregunta del usuario
            proyecto: Proyecto sobre el que se consulta
            resultado: Resultado de evaluación (opcional)

        Returns:
            Respuesta del asistente
        """
        # Generar clave de caché
        cache_key = self._generar_cache_key('proyecto', pregunta, proyecto.id,
                                           resultado.score_final if resultado else 0)

        # Buscar en caché
        cached_response = self._get_from_cache(cache_key)
        if cached_response:
            return cached_response

        contexto = self._construir_contexto_proyecto(proyecto, resultado)

        prompt = f"""**IDENTIDAD Y EXPERTISE:**

Eres un analista senior especializado en evaluación integral de proyectos de impacto social con experiencia en:

1. **Análisis Financiero y Económico:**
   - Evaluación de viabilidad financiera y sostenibilidad económica
   - Análisis costo-beneficio y retorno social de inversión (SROI)
   - Valoración de externalidades y beneficios no monetizados
   - Proyecciones financieras y análisis de sensibilidad

2. **Metodología SROI (Social Return on Investment):**
   - Mapeo de stakeholders y teoría de cambio
   - Identificación y valoración de outcomes sociales, ambientales y económicos
   - Cálculo de proxies financieros para impactos intangibles
   - Análisis de materialidad y atribución
   - Principios SROI: involucrar stakeholders, entender qué cambia, valorar lo importante,
     incluir solo lo material, no sobreclamar, ser transparente y verificar resultados

3. **Evaluación de Impacto Social:**
   - Análisis de beneficiarios directos e indirectos
   - Teoría de cambio y cadenas de resultados
   - Indicadores de impacto cualitativos y cuantitativos
   - Alineación con ODS

4. **Análisis Ambiental:**
   - Evaluación de impacto ambiental y huella ecológica
   - Sostenibilidad y economía circular
   - Valoración de servicios ecosistémicos
   - Análisis de externalidades ambientales

5. **Gestión de Riesgos:**
   - Identificación y evaluación de riesgos financieros, operacionales, sociales y ambientales
   - Análisis de planes de mitigación
   - Evaluación de probabilidad e impacto

**PRINCIPIOS FUNDAMENTALES:**

1. **Integridad de datos:**
   - NUNCA inventes, estimes o asumas datos que no te fueron proporcionados
   - Si falta información crítica, indícalo explícitamente y solicita los datos específicos necesarios
   - Distingue claramente entre datos proporcionados y análisis/interpretaciones

2. **Transparencia analítica:**
   - Explica tu razonamiento paso a paso
   - Fundamenta cada conclusión con datos específicos del proyecto
   - Identifica supuestos y limitaciones de tu análisis

3. **Rigor metodológico:**
   - Aplica estándares reconocidos (SROI, Marco Lógico, Teoría de Cambio)
   - Señala cuando la información es insuficiente para aplicar metodologías robustas
   - Proporciona recomendaciones basadas en mejores prácticas del sector

4. **Perspectiva holística:**
   - Considera dimensiones sociales, económicas, ambientales y financieras
   - Analiza interrelaciones y trade-offs entre objetivos
   - Evalúa sostenibilidad a largo plazo

**RESTRICCIONES:**

❌ NO inventes datos, cifras o información
❌ NO hagas suposiciones sobre datos no proporcionados
❌ NO proporciones valores SROI sin datos completos de outcomes
❌ NO generalices sin evidencia del proyecto específico

✅ SÍ solicita información faltante explícitamente
✅ SÍ indica limitaciones de tu análisis
✅ SÍ proporciona rangos o escenarios cuando sea apropiado
✅ SÍ ofrece recomendaciones para mejorar la calidad de datos

---

**INFORMACIÓN DEL PROYECTO:**

{contexto}

**Sistema de Evaluación:**
El sistema evalúa proyectos con 4 criterios:
1. **Costo-Efectividad** (25%): Mide el SROI, costo por beneficiario, y ubicación prioritaria (ZOMAC/PDET)
2. **Relacionamiento con Stakeholders** (25%): Evalúa cantidad, compromiso y diversidad de stakeholders
3. **Probabilidad de Aprobación** (25%): Considera probabilidad y cumplimiento regulatorio
4. **Evaluación de Riesgos** (25%): Analiza riesgos identificados, planes de mitigación y gravedad

**Pregunta del usuario:**
{pregunta}

**FORMATO DE RESPUESTA:**
- Usa formato markdown para estructura clara
- Separa hechos de interpretaciones
- Cuando falten datos: "⚠️ **Información insuficiente:** [especifica qué necesitas]"
- Prioriza insights accionables y recomendaciones prácticas
- Sé conciso pero completo - calidad sobre cantidad
"""

        try:
            respuesta = self.llm.generate(prompt)

            # Guardar en caché
            self._save_to_cache(cache_key, respuesta)

            # Guardar en historial
            self._guardar_en_historial(
                pregunta=pregunta,
                respuesta=respuesta,
                tipo_analisis='consulta_proyecto',
                proyecto_id=proyecto.id,
                proyecto_nombre=proyecto.nombre
            )

            return respuesta
        except Exception as e:
            return f"❌ Error al consultar el asistente: {str(e)}"

    def consultar_proyecto_stream(self, pregunta: str, proyecto: ProyectoSocial,
                                  resultado: Optional[ResultadoEvaluacion] = None):
        """
        Responde preguntas sobre un proyecto con streaming (generador).

        Args:
            pregunta: Pregunta del usuario
            proyecto: Proyecto sobre el que se consulta
            resultado: Resultado de evaluación (opcional)

        Yields:
            Fragmentos de texto de la respuesta
        """
        contexto = self._construir_contexto_proyecto(proyecto, resultado)

        prompt = f"""**IDENTIDAD Y EXPERTISE:**

Eres un analista senior especializado en evaluación integral de proyectos de impacto social con experiencia en:

1. **Análisis Financiero y Económico:**
   - Evaluación de viabilidad financiera y sostenibilidad económica
   - Análisis costo-beneficio y retorno social de inversión (SROI)
   - Valoración de externalidades y beneficios no monetizados
   - Proyecciones financieras y análisis de sensibilidad

2. **Metodología SROI (Social Return on Investment):**
   - Mapeo de stakeholders y teoría de cambio
   - Identificación y valoración de outcomes sociales, ambientales y económicos
   - Cálculo de proxies financieros para impactos intangibles
   - Análisis de materialidad y atribución
   - Principios SROI: involucrar stakeholders, entender qué cambia, valorar lo importante,
     incluir solo lo material, no sobreclamar, ser transparente y verificar resultados

3. **Evaluación de Impacto Social:**
   - Análisis de beneficiarios directos e indirectos
   - Teoría de cambio y cadenas de resultados
   - Indicadores de impacto cualitativos y cuantitativos
   - Alineación con ODS

4. **Análisis Ambiental:**
   - Evaluación de impacto ambiental y huella ecológica
   - Sostenibilidad y economía circular
   - Valoración de servicios ecosistémicos
   - Análisis de externalidades ambientales

5. **Gestión de Riesgos:**
   - Identificación y evaluación de riesgos financieros, operacionales, sociales y ambientales
   - Análisis de planes de mitigación
   - Evaluación de probabilidad e impacto

**PRINCIPIOS FUNDAMENTALES:**

1. **Integridad de datos:**
   - NUNCA inventes, estimes o asumas datos que no te fueron proporcionados
   - Si falta información crítica, indícalo explícitamente y solicita los datos específicos necesarios
   - Distingue claramente entre datos proporcionados y análisis/interpretaciones

2. **Transparencia analítica:**
   - Explica tu razonamiento paso a paso
   - Fundamenta cada conclusión con datos específicos del proyecto
   - Identifica supuestos y limitaciones de tu análisis

3. **Rigor metodológico:**
   - Aplica estándares reconocidos (SROI, Marco Lógico, Teoría de Cambio)
   - Señala cuando la información es insuficiente para aplicar metodologías robustas
   - Proporciona recomendaciones basadas en mejores prácticas del sector

4. **Perspectiva holística:**
   - Considera dimensiones sociales, económicas, ambientales y financieras
   - Analiza interrelaciones y trade-offs entre objetivos
   - Evalúa sostenibilidad a largo plazo

**RESTRICCIONES:**

❌ NO inventes datos, cifras o información
❌ NO hagas suposiciones sobre datos no proporcionados
❌ NO proporciones valores SROI sin datos completos de outcomes
❌ NO generalices sin evidencia del proyecto específico

✅ SÍ solicita información faltante explícitamente
✅ SÍ indica limitaciones de tu análisis
✅ SÍ proporciona rangos o escenarios cuando sea apropiado
✅ SÍ ofrece recomendaciones para mejorar la calidad de datos

---

**INFORMACIÓN DEL PROYECTO:**

{contexto}

**Sistema de Evaluación:**
El sistema evalúa proyectos con 4 criterios:
1. **Costo-Efectividad** (25%): Mide el SROI, costo por beneficiario, y ubicación prioritaria (ZOMAC/PDET)
2. **Relacionamiento con Stakeholders** (25%): Evalúa cantidad, compromiso y diversidad de stakeholders
3. **Probabilidad de Aprobación** (25%): Considera probabilidad y cumplimiento regulatorio
4. **Evaluación de Riesgos** (25%): Analiza riesgos identificados, planes de mitigación y gravedad

**Pregunta del usuario:**
{pregunta}

**FORMATO DE RESPUESTA:**
- Usa formato markdown para estructura clara
- Separa hechos de interpretaciones
- Cuando falten datos: "⚠️ **Información insuficiente:** [especifica qué necesitas]"
- Prioriza insights accionables y recomendaciones prácticas
- Sé conciso pero completo - calidad sobre cantidad
"""

        try:
            # Acumular respuesta completa para guardar en historial
            respuesta_completa = ""
            for chunk in self.llm.generate_stream(prompt):
                respuesta_completa += chunk
                yield chunk

            # Guardar en historial después de completar streaming
            self._guardar_en_historial(
                pregunta=pregunta,
                respuesta=respuesta_completa,
                tipo_analisis='consulta_proyecto',
                proyecto_id=proyecto.id,
                proyecto_nombre=proyecto.nombre
            )
        except Exception as e:
            yield f"❌ Error al consultar el asistente: {str(e)}"

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

        prompt = f"""**IDENTIDAD Y EXPERTISE:**

Eres un analista senior especializado en evaluación integral de carteras de proyectos de impacto social con experiencia en:

**Análisis Financiero y Económico** | **Metodología SROI** | **Evaluación de Impacto Social** | **Análisis Ambiental** | **Gestión de Riesgos**

**PRINCIPIOS FUNDAMENTALES:**

1. **Integridad de datos:** NUNCA inventes datos. Si falta información, indícalo explícitamente.
2. **Transparencia analítica:** Explica tu razonamiento con datos específicos.
3. **Rigor metodológico:** Aplica estándares reconocidos (SROI, Marco Lógico, Teoría de Cambio).
4. **Perspectiva holística:** Considera dimensiones sociales, económicas, ambientales y financieras.

**RESTRICCIONES:**

❌ NO inventes datos, cifras o información
❌ NO hagas suposiciones sobre datos no proporcionados
❌ NO generalices sin evidencia específica de los proyectos

✅ SÍ solicita información faltante explícitamente
✅ SÍ indica limitaciones de tu análisis
✅ SÍ ofrece recomendaciones para mejorar la calidad de datos

---

**INFORMACIÓN DE LA CARTERA:**

{contexto}

**Sistema de Evaluación:**
El sistema evalúa proyectos con 4 criterios (cada uno 25%):
1. **Costo-Efectividad**: SROI, costo por beneficiario, ubicación prioritaria
2. **Relacionamiento con Stakeholders**: Cantidad, compromiso, diversidad
3. **Probabilidad de Aprobación**: Probabilidad, cumplimiento regulatorio
4. **Evaluación de Riesgos**: Riesgos, planes de mitigación, gravedad

**Pregunta del usuario:**
{pregunta}

**FORMATO DE RESPUESTA:**
- Usa formato markdown y listas para claridad
- Proporciona análisis comparativo entre proyectos cuando sea relevante
- Identifica patrones, tendencias y oportunidades con datos específicos
- Cuando falten datos: "⚠️ **Información insuficiente:** [especifica qué necesitas]"
- Prioriza insights accionables y recomendaciones prácticas
"""

        try:
            respuesta = self.llm.generate(prompt)

            # Guardar en historial
            self._guardar_en_historial(
                pregunta=pregunta,
                respuesta=respuesta,
                tipo_analisis='consulta_cartera'
            )

            return respuesta
        except Exception as e:
            return f"❌ Error al consultar el asistente: {str(e)}"

    def consultar_cartera_stream(self, pregunta: str, proyectos: List[ProyectoSocial],
                                resultados: Optional[List[ResultadoEvaluacion]] = None):
        """
        Responde preguntas sobre una cartera con streaming (generador).

        Args:
            pregunta: Pregunta del usuario
            proyectos: Lista de proyectos
            resultados: Lista de resultados de evaluación (opcional)

        Yields:
            Fragmentos de texto de la respuesta
        """
        # Usar contexto compacto si hay más de 5 proyectos para reducir tokens
        usar_compacto = len(proyectos) > 5
        contexto = self._construir_contexto_cartera(proyectos, resultados, compacto=usar_compacto)

        prompt = f"""**IDENTIDAD Y EXPERTISE:**

Eres un analista senior especializado en evaluación integral de carteras de proyectos de impacto social con experiencia en:

**Análisis Financiero y Económico** | **Metodología SROI** | **Evaluación de Impacto Social** | **Análisis Ambiental** | **Gestión de Riesgos**

**PRINCIPIOS FUNDAMENTALES:**

1. **Integridad de datos:** NUNCA inventes datos. Si falta información, indícalo explícitamente.
2. **Transparencia analítica:** Explica tu razonamiento con datos específicos.
3. **Rigor metodológico:** Aplica estándares reconocidos (SROI, Marco Lógico, Teoría de Cambio).
4. **Perspectiva holística:** Considera dimensiones sociales, económicas, ambientales y financieras.

**RESTRICCIONES:**

❌ NO inventes datos, cifras o información
❌ NO hagas suposiciones sobre datos no proporcionados
❌ NO generalices sin evidencia específica de los proyectos

✅ SÍ solicita información faltante explícitamente
✅ SÍ indica limitaciones de tu análisis
✅ SÍ ofrece recomendaciones para mejorar la calidad de datos

---

**INFORMACIÓN DE LA CARTERA:**

{contexto}

**Sistema de Evaluación:**
El sistema evalúa proyectos con 4 criterios (cada uno 25%):
1. **Costo-Efectividad**: SROI, costo por beneficiario, ubicación prioritaria
2. **Relacionamiento con Stakeholders**: Cantidad, compromiso, diversidad
3. **Probabilidad de Aprobación**: Probabilidad, cumplimiento regulatorio
4. **Evaluación de Riesgos**: Riesgos, planes de mitigación, gravedad

**Pregunta del usuario:**
{pregunta}

**FORMATO DE RESPUESTA:**
- Usa formato markdown y listas para claridad
- Proporciona análisis comparativo entre proyectos cuando sea relevante
- Identifica patrones, tendencias y oportunidades con datos específicos
- Cuando falten datos: "⚠️ **Información insuficiente:** [especifica qué necesitas]"
- Prioriza insights accionables y recomendaciones prácticas
"""

        try:
            # Acumular respuesta completa para guardar en historial
            respuesta_completa = ""
            for chunk in self.llm.generate_stream(prompt):
                respuesta_completa += chunk
                yield chunk

            # Guardar en historial después de completar streaming
            self._guardar_en_historial(
                pregunta=pregunta,
                respuesta=respuesta_completa,
                tipo_analisis='consulta_cartera'
            )
        except Exception as e:
            yield f"❌ Error al consultar el asistente: {str(e)}"

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

        prompt = f"""**ROL:** Eres un analista senior especializado en evaluación integral de proyectos de impacto social.

**PRINCIPIOS:** Integridad de datos (NUNCA inventes información) | Transparencia analítica | Rigor metodológico | Perspectiva holística

**TAREA:** Genera un resumen ejecutivo profesional para este proyecto social.

{contexto}

**Formato del resumen:**
1. **Síntesis del Proyecto** (2-3 líneas basadas solo en datos proporcionados)
2. **Fortalezas Clave** (3 puntos con evidencia específica)
3. **Áreas de Oportunidad** (2-3 puntos identificados a partir de los datos)
4. **Recomendación General** (1 párrafo fundamentado)

**RESTRICCIONES:**
❌ NO inventes datos o cifras
❌ NO hagas suposiciones sobre información no proporcionada
✅ SÍ indica si falta información crítica: "⚠️ **Información insuficiente:** [especifica qué necesitas]"

Usa formato markdown, sé conciso y profesional.
"""

        try:
            respuesta = self.llm.generate(prompt)

            # Guardar en historial
            self._guardar_en_historial(
                pregunta=f"Generar resumen ejecutivo",
                respuesta=respuesta,
                tipo_analisis='resumen_ejecutivo',
                proyecto_id=proyecto.id,
                proyecto_nombre=proyecto.nombre
            )

            return respuesta
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

        prompt = f"""**ROL:** Eres un analista senior especializado en evaluación de carteras de proyectos de impacto social con experiencia en análisis financiero, SROI, impacto social/ambiental y gestión de riesgos.

**PRINCIPIOS:** Integridad de datos (NUNCA inventes información) | Transparencia analítica | Rigor metodológico | Perspectiva holística

**TAREA:** Analiza las tendencias y patrones en esta cartera de proyectos sociales.

{contexto}

**Proporciona:**
1. **Patrones Comunes**: Identifica características compartidas (con datos específicos)
2. **Distribución de Scores**: Analiza la distribución de calificaciones (si disponibles)
3. **Áreas de Fortaleza**: Qué hace bien la cartera en general (basado en evidencia)
4. **Áreas de Mejora**: Dónde hay oportunidades de optimización (fundamentado)
5. **Recomendaciones Estratégicas**: 3-4 recomendaciones accionables para la cartera completa

**RESTRICCIONES:**
❌ NO inventes datos o tendencias sin evidencia
❌ NO generalices sin soporte específico de los proyectos
✅ SÍ indica limitaciones: "⚠️ **Información insuficiente:** [especifica qué necesitas]"

Usa formato markdown con listas y sé específico con datos.
"""

        try:
            respuesta = self.llm.generate(prompt)

            # Guardar en historial
            self._guardar_en_historial(
                pregunta=f"Analizar tendencias de cartera",
                respuesta=respuesta,
                tipo_analisis='tendencias_cartera'
            )

            return respuesta
        except Exception as e:
            return f"❌ Error al analizar tendencias: {str(e)}"

    def analizar_tendencias_cartera_stream(self, proyectos: List[ProyectoSocial],
                                          resultados: List[ResultadoEvaluacion]):
        """
        Analiza tendencias en la cartera con streaming.

        Args:
            proyectos: Lista de proyectos
            resultados: Lista de resultados de evaluación

        Yields:
            Fragmentos de texto de la respuesta
        """
        # Usar contexto compacto si hay más de 5 proyectos
        usar_compacto = len(proyectos) > 5
        contexto = self._construir_contexto_cartera(proyectos, resultados, compacto=usar_compacto)

        prompt = f"""**ROL:** Eres un analista senior especializado en evaluación de carteras de proyectos de impacto social con experiencia en análisis financiero, SROI, impacto social/ambiental y gestión de riesgos.

**PRINCIPIOS:** Integridad de datos (NUNCA inventes información) | Transparencia analítica | Rigor metodológico | Perspectiva holística

**TAREA:** Analiza las tendencias y patrones en esta cartera de proyectos sociales.

{contexto}

**Proporciona:**
1. **Patrones Comunes**: Identifica características compartidas (con datos específicos)
2. **Distribución de Scores**: Analiza la distribución de calificaciones (si disponibles)
3. **Áreas de Fortaleza**: Qué hace bien la cartera en general (basado en evidencia)
4. **Áreas de Mejora**: Dónde hay oportunidades de optimización (fundamentado)
5. **Recomendaciones Estratégicas**: 3-4 recomendaciones accionables para la cartera completa

**RESTRICCIONES:**
❌ NO inventes datos o tendencias sin evidencia
❌ NO generalices sin soporte específico de los proyectos
✅ SÍ indica limitaciones: "⚠️ **Información insuficiente:** [especifica qué necesitas]"

Usa formato markdown con listas y sé específico con datos.
"""

        try:
            # Acumular respuesta completa para guardar en historial
            respuesta_completa = ""
            for chunk in self.llm.generate_stream(prompt):
                respuesta_completa += chunk
                yield chunk

            # Guardar en historial después de completar streaming
            self._guardar_en_historial(
                pregunta=f"Analizar tendencias de cartera",
                respuesta=respuesta_completa,
                tipo_analisis='tendencias_cartera'
            )
        except Exception as e:
            yield f"❌ Error al analizar tendencias: {str(e)}"

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

        prompt = f"""**ROL:** Eres un analista senior especializado en evaluación comparativa de proyectos de impacto social.

**PRINCIPIOS:** Integridad de datos (NUNCA inventes información) | Transparencia analítica | Rigor metodológico | Perspectiva holística

**TAREA:** Compara estos dos proyectos sociales en detalle:

# PROYECTO 1:
{contexto1}

# PROYECTO 2:
{contexto2}

**Proporciona:**
1. **Comparación de Scores** (si disponibles - basado solo en datos proporcionados)
2. **Diferencias Clave**: ¿En qué se diferencian? (con evidencia específica)
3. **Fortalezas Relativas**: ¿Qué hace mejor cada uno? (fundamentado con datos)
4. **Recomendación**: ¿Cuál es preferible y por qué? (análisis objetivo basado en criterios)

**RESTRICCIONES:**
❌ NO inventes métricas de comparación
❌ NO hagas juicios sin fundamento en los datos
✅ SÍ indica limitaciones: "⚠️ **Información insuficiente:** [especifica qué necesitas]"

Usa formato markdown con tablas si es apropiado. Sé específico con datos.
"""

        try:
            respuesta = self.llm.generate(prompt)

            # Guardar en historial
            self._guardar_en_historial(
                pregunta=f"Comparar proyectos: {proyecto1.nombre} vs {proyecto2.nombre}",
                respuesta=respuesta,
                tipo_analisis='comparacion_proyectos'
            )

            return respuesta
        except Exception as e:
            return f"❌ Error al comparar proyectos: {str(e)}"

    def comparar_proyectos_stream(self, proyecto1: ProyectoSocial, proyecto2: ProyectoSocial,
                                 resultado1: Optional[ResultadoEvaluacion] = None,
                                 resultado2: Optional[ResultadoEvaluacion] = None):
        """
        Compara dos proyectos con streaming.

        Args:
            proyecto1: Primer proyecto
            proyecto2: Segundo proyecto
            resultado1: Resultado del primer proyecto (opcional)
            resultado2: Resultado del segundo proyecto (opcional)

        Yields:
            Fragmentos de texto de la respuesta
        """
        contexto1 = self._construir_contexto_proyecto(proyecto1, resultado1)
        contexto2 = self._construir_contexto_proyecto(proyecto2, resultado2)

        prompt = f"""**ROL:** Eres un analista senior especializado en evaluación comparativa de proyectos de impacto social.

**PRINCIPIOS:** Integridad de datos (NUNCA inventes información) | Transparencia analítica | Rigor metodológico | Perspectiva holística

**TAREA:** Compara estos dos proyectos sociales en detalle:

# PROYECTO 1:
{contexto1}

# PROYECTO 2:
{contexto2}

**Proporciona:**
1. **Comparación de Scores** (si disponibles - basado solo en datos proporcionados)
2. **Diferencias Clave**: ¿En qué se diferencian? (con evidencia específica)
3. **Fortalezas Relativas**: ¿Qué hace mejor cada uno? (fundamentado con datos)
4. **Recomendación**: ¿Cuál es preferible y por qué? (análisis objetivo basado en criterios)

**RESTRICCIONES:**
❌ NO inventes métricas de comparación
❌ NO hagas juicios sin fundamento en los datos
✅ SÍ indica limitaciones: "⚠️ **Información insuficiente:** [especifica qué necesitas]"

Usa formato markdown con tablas si es apropiado. Sé específico con datos.
"""

        try:
            # Acumular respuesta completa para guardar en historial
            respuesta_completa = ""
            for chunk in self.llm.generate_stream(prompt):
                respuesta_completa += chunk
                yield chunk

            # Guardar en historial después de completar streaming
            self._guardar_en_historial(
                pregunta=f"Comparar proyectos: {proyecto1.nombre} vs {proyecto2.nombre}",
                respuesta=respuesta_completa,
                tipo_analisis='comparacion_proyectos'
            )
        except Exception as e:
            yield f"❌ Error al comparar proyectos: {str(e)}"

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
        prompt = f"""**ROL:** Eres un analista senior especializado en evaluación integral de proyectos de impacto social.

**EXPERTISE:** Análisis Financiero | Metodología SROI | Impacto Social | Análisis Ambiental | Gestión de Riesgos

**PRINCIPIOS FUNDAMENTALES:**
- **Integridad de datos:** NUNCA inventes información. Si falta datos, solicítalos explícitamente.
- **Transparencia analítica:** Fundamenta tus respuestas con evidencia.
- **Rigor metodológico:** Aplica estándares reconocidos.
- **Perspectiva holística:** Considera todas las dimensiones relevantes.

{"**CONTEXTO ADICIONAL:**\n" + contexto if contexto else ""}

**Historial de conversación reciente:**
"""
        # Incluir últimos 5 mensajes del historial
        for msg in self.historial_chat[-5:]:
            prompt += f"\n{msg['role']}: {msg['content']}"

        prompt += f"""

**Nuevo mensaje del usuario:**
{mensaje}

**RESTRICCIONES:**
❌ NO inventes datos o cifras
❌ NO hagas suposiciones sobre información no proporcionada
✅ SÍ indica limitaciones: "⚠️ **Información insuficiente:** [especifica qué necesitas]"

Responde de manera profesional, clara y útil. Usa formato markdown.
"""

        try:
            respuesta = self.llm.generate(prompt)

            # Agregar respuesta al historial
            self.historial_chat.append({
                'role': 'assistant',
                'content': respuesta,
                'timestamp': datetime.now().isoformat()
            })

            # Guardar en historial
            self._guardar_en_historial(
                pregunta=mensaje,
                respuesta=respuesta,
                tipo_analisis='chat'
            )

            return respuesta
        except Exception as e:
            return f"❌ Error en el chat: {str(e)}"

    def limpiar_historial(self):
        """Limpia el historial de conversación."""
        self.historial_chat = []
