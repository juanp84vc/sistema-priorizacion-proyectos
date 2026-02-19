"""
Criterio de evaluación: Stakeholders (Relacionamiento y Pertinencia Operacional)
Arquitectura C - Peso: 25%

Este criterio evalúa:
1. Pertinencia operacional/reputacional para ENLAZA (40%)
2. Mejora del relacionamiento con stakeholders (35%)
3. Alcance territorial del proyecto (15%)
4. Tipo de stakeholders involucrados (10%)

Contexto ENLAZA:
- Proyectos como herramientas para licencia social
- Facilitar operaciones de líneas de transmisión
- Mejorar relacionamiento en territorios estratégicos

Ajuste metodológico (Feb 2026):
- Rúbricas objetivas con criterios verificables para Pertinencia y Relacionamiento
- Documentación de las descripciones detalladas de cada nivel de la escala
- Reduce variabilidad inter-evaluador de ~45 a ~10 puntos
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.models.proyecto import ProyectoSocial


# Mapeos de escalas a scores con rúbricas objetivas (Ajuste Feb 2026)
#
# PERTINENCIA OPERACIONAL - Criterios verificables:
# 5: Proyecto impacta directamente la operación de una línea de transmisión activa.
#    Sin licencia social, la operación se detiene.
# 4: Proyecto en territorio con comunidades que afectan la planificación de futuras
#    líneas. Influencia significativa en reputación corporativa.
# 3: Proyecto en área de influencia indirecta. Contribuye a imagen corporativa
#    pero no es crítico para operaciones.
# 2: Proyecto fuera de corredores operacionales. Beneficio marginal para
#    relacionamiento institucional.
# 1: Sin conexión con operaciones, corredores ni territorios estratégicos de ENLAZA.
ESCALA_PERTINENCIA = {
    5: 100,  # Muy Alta - Impacto directo en operación de línea activa
    4: 85,   # Alta - Territorio con comunidades que afectan futuras líneas
    3: 65,   # Media - Área de influencia indirecta
    2: 40,   # Baja - Fuera de corredores operacionales
    1: 20    # Nula - Sin conexión con operaciones ENLAZA
}

# MEJORA DEL RELACIONAMIENTO - Criterios verificables:
# 5: Existen conflictos activos documentados que el proyecto resolvería. Comunidad
#    ha manifestado oposición formal. Proyecto incluye mecanismos de participación.
# 4: No hay conflicto activo pero existe desconfianza documentada. Proyecto fortalece
#    acuerdos existentes o crea nuevos canales de diálogo.
# 3: Relación neutral sin historial negativo. Proyecto genera visibilidad positiva
#    y contacto institucional.
# 2: Comunidad ya tiene relación funcional con ENLAZA. Proyecto aporta beneficio
#    marginal al relacionamiento.
# 1: No hay comunidades relevantes o el proyecto no genera interacción con stakeholders.
ESCALA_RELACIONAMIENTO = {
    5: 100,  # Sustancial - Resuelve conflictos activos documentados
    4: 85,   # Genera Confianza - Fortalece acuerdos, crea diálogo
    3: 65,   # Moderada - Genera visibilidad positiva, relación neutral
    2: 40,   # Limitada - Relación ya funcional, beneficio marginal
    1: 20    # No Aporta - Sin interacción con stakeholders
}

# Puntajes para stakeholders
PUNTAJES_STAKEHOLDERS = {
    'autoridades_locales': 25,
    'lideres_comunitarios': 20,
    'comunidades_indigenas': 25,
    'organizaciones_sociales': 15,
    'sector_privado': 10,
    'academia': 10,
    'medios_comunicacion': 5
}

PUNTAJE_MAXIMO_STAKEHOLDERS = 110  # Suma de todos


@dataclass
class ResultadoStakeholders:
    """Resultado detallado de evaluación Stakeholders"""
    score: float  # 0-100

    # Scores por componente
    score_pertinencia: float
    score_relacionamiento: float
    score_alcance: float
    score_stakeholders_tipo: float

    # Contribuciones al score final
    contribucion_pertinencia: float
    contribucion_relacionamiento: float
    contribucion_alcance: float
    contribucion_stakeholders: float

    # Metadata
    nivel: str  # "MUY ALTO", "ALTO", "MEDIO", "BAJO"
    mensaje: str
    alertas: List[str]
    recomendaciones: List[str]


class StakeholdersCriterio:
    """
    Evalúa contribución al relacionamiento con stakeholders
    y pertinencia operacional para ENLAZA.

    Criterio: 25% del score total (Arquitectura C)

    Componentes:
    - Pertinencia Operacional (40%)
    - Mejora Relacionamiento (35%)
    - Alcance Territorial (15%)
    - Stakeholders Involucrados (10%)
    """

    # Pesos de componentes
    PESO_PERTINENCIA = 0.40
    PESO_RELACIONAMIENTO = 0.35
    PESO_ALCANCE = 0.15
    PESO_STAKEHOLDERS_TIPO = 0.10

    def __init__(self, peso: float = 0.25):
        self.peso = peso
        self.nombre = "Stakeholders (Relacionamiento y Pertinencia Operacional)"
        self.descripcion = "Evalúa relacionamiento con stakeholders y pertinencia operacional"

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa stakeholders del proyecto y retorna score 0-100.

        Args:
            proyecto: Proyecto a evaluar

        Returns:
            Score 0-100

        Raises:
            ValueError: Si faltan datos requeridos
        """
        # Validar datos
        validacion = proyecto.validar_stakeholders()
        if not validacion['valido']:
            raise ValueError(f"Datos stakeholders inválidos: {validacion['mensaje']}")

        # Calcular componentes
        score_pertinencia = self._calcular_pertinencia(proyecto)
        score_relacionamiento = self._calcular_relacionamiento(proyecto)
        score_alcance = self._calcular_alcance_territorial(proyecto)
        score_stakeholders = self._calcular_stakeholders_tipo(proyecto)

        # Score total ponderado
        score = (
            score_pertinencia * self.PESO_PERTINENCIA +
            score_relacionamiento * self.PESO_RELACIONAMIENTO +
            score_alcance * self.PESO_ALCANCE +
            score_stakeholders * self.PESO_STAKEHOLDERS_TIPO
        )

        return score

    def evaluar_detallado(self, proyecto: ProyectoSocial) -> ResultadoStakeholders:
        """
        Evaluación detallada con metadata y alertas.

        Args:
            proyecto: Proyecto a evaluar

        Returns:
            ResultadoStakeholders con detalles completos
        """
        # Validar
        validacion = proyecto.validar_stakeholders()
        alertas = validacion.get('advertencias', [])
        recomendaciones = []

        # Calcular componentes
        score_pertinencia = self._calcular_pertinencia(proyecto)
        score_relacionamiento = self._calcular_relacionamiento(proyecto)
        score_alcance = self._calcular_alcance_territorial(proyecto)
        score_stakeholders = self._calcular_stakeholders_tipo(proyecto)

        # Contribuciones
        contrib_pertinencia = score_pertinencia * self.PESO_PERTINENCIA
        contrib_relacionamiento = score_relacionamiento * self.PESO_RELACIONAMIENTO
        contrib_alcance = score_alcance * self.PESO_ALCANCE
        contrib_stakeholders = score_stakeholders * self.PESO_STAKEHOLDERS_TIPO

        # Score total
        score = (
            contrib_pertinencia +
            contrib_relacionamiento +
            contrib_alcance +
            contrib_stakeholders
        )

        # Generar alertas y recomendaciones
        if proyecto.pertinencia_operacional == 5:
            alertas.append(
                "⭐ Pertinencia MUY ALTA: Proyecto crítico para operaciones ENLAZA"
            )

        if proyecto.mejora_relacionamiento == 5:
            alertas.append(
                "⭐ Mejora SUSTANCIAL: Proyecto transforma relacionamiento"
            )

        if proyecto.pertinencia_operacional >= 4 and proyecto.mejora_relacionamiento >= 4:
            recomendaciones.append(
                "💡 Proyecto altamente estratégico: Priorizar en portafolio"
            )

        if score < 50:
            recomendaciones.append(
                "⚠️  Score bajo en Stakeholders: Revisar pertinencia estratégica"
            )

        if not proyecto.stakeholders_involucrados:
            recomendaciones.append(
                "📋 Especificar stakeholders para evaluación más precisa"
            )

        # Determinar nivel
        nivel = self._determinar_nivel(score)

        # Mensaje
        if score >= 80:
            mensaje = "Excelente contribución a relacionamiento y operaciones"
        elif score >= 60:
            mensaje = "Buena contribución a relacionamiento"
        elif score >= 40:
            mensaje = "Contribución moderada a relacionamiento"
        else:
            mensaje = "Contribución limitada a relacionamiento"

        return ResultadoStakeholders(
            score=score,
            score_pertinencia=score_pertinencia,
            score_relacionamiento=score_relacionamiento,
            score_alcance=score_alcance,
            score_stakeholders_tipo=score_stakeholders,
            contribucion_pertinencia=contrib_pertinencia,
            contribucion_relacionamiento=contrib_relacionamiento,
            contribucion_alcance=contrib_alcance,
            contribucion_stakeholders=contrib_stakeholders,
            nivel=nivel,
            mensaje=mensaje,
            alertas=alertas,
            recomendaciones=recomendaciones
        )

    def _calcular_pertinencia(self, proyecto: ProyectoSocial) -> float:
        """
        Calcula score de pertinencia operacional/reputacional (40%)

        Escala 1-5 → Score según mapeo ESCALA_PERTINENCIA
        """
        pertinencia = proyecto.pertinencia_operacional

        if pertinencia is None:
            return 50.0  # Neutro si no especificado

        return float(ESCALA_PERTINENCIA.get(pertinencia, 50))

    def _calcular_relacionamiento(self, proyecto: ProyectoSocial) -> float:
        """
        Calcula score de mejora del relacionamiento (35%)

        Escala 1-5 → Score según mapeo ESCALA_RELACIONAMIENTO
        """
        relacionamiento = proyecto.mejora_relacionamiento

        if relacionamiento is None:
            return 50.0  # Neutro si no especificado

        return float(ESCALA_RELACIONAMIENTO.get(relacionamiento, 50))

    def _calcular_alcance_territorial(self, proyecto: ProyectoSocial) -> float:
        """
        Calcula score de alcance territorial (15%)

        Ajuste CONFIS (Feb 2026):
        Reemplaza bonus binario PDET con puntaje territorial CONFIS
        (IPM + MDM_inv + IICA + CULTIVOS, promedio 1-10).

        Basado en:
        - Puntaje territorial CONFIS (max 30 pts): score_territorial × 3
        - Número de municipios (max 30 pts): min(num × 10, 30)
        - Bonus si múltiples departamentos: +15 pts
        - Bonus si corredor transmisión: +10 pts
        - Bonus si PDET: +15 pts
        """
        score = 0

        # Componente territorial CONFIS (max 30 pts)
        # Reemplaza el antiguo bonus binario PDET (+20)
        puntaje_territorial = 5.0  # Default neutro
        if proyecto.puntaje_territorial_confis is not None:
            puntaje_territorial = max(min(proyecto.puntaje_territorial_confis, 10.0), 1.0)
        score += puntaje_territorial * 3  # Max 30 pts

        # Base: número de municipios (10 pts c/u, max 30)
        num_municipios = len(proyecto.municipios) if proyecto.municipios else 1
        score_base = min(num_municipios * 10, 30)
        score += score_base

        # Bonus PDET: +15 pts
        if proyecto.tiene_municipios_pdet:
            score += 15

        # Bonus múltiples departamentos: +15 pts
        num_departamentos = len(proyecto.departamentos) if proyecto.departamentos else 1
        if num_departamentos > 1:
            score += 15

        # Bonus corredor transmisión: +10 pts
        if proyecto.en_corredor_transmision:
            score += 10

        # Normalizar a 0-100
        # Máximo posible: 30 + 30 + 15 + 15 + 10 = 100
        score_normalizado = min(score, 100)

        return score_normalizado

    def _calcular_stakeholders_tipo(self, proyecto: ProyectoSocial) -> float:
        """
        Calcula score de stakeholders involucrados (10%)

        Basado en tipos de stakeholders seleccionados
        """
        if not proyecto.stakeholders_involucrados:
            return 50.0  # Neutro si no especificados

        # Sumar puntajes de stakeholders seleccionados
        puntaje_total = 0
        for stakeholder in proyecto.stakeholders_involucrados:
            puntaje_total += PUNTAJES_STAKEHOLDERS.get(stakeholder, 0)

        # Normalizar a 0-100
        score = (puntaje_total / PUNTAJE_MAXIMO_STAKEHOLDERS) * 100

        return min(score, 100)

    def _determinar_nivel(self, score: float) -> str:
        """Determina nivel de prioridad basado en score"""
        if score >= 85:
            return "MUY ALTO"
        elif score >= 70:
            return "ALTO"
        elif score >= 50:
            return "MEDIO"
        else:
            return "BAJO"

    def aplicar_peso(self, score: float) -> float:
        """
        Aplica el peso del criterio (25%) al score.

        Args:
            score: Score base 0-100

        Returns:
            Contribución al score final (0-25)
        """
        return score * self.peso

    def get_nombre(self) -> str:
        """Retorna el nombre del criterio"""
        return self.nombre

    def get_descripcion(self) -> str:
        """Retorna la descripción del criterio"""
        return self.descripcion
