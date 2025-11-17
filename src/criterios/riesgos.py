"""
Criterio de evaluación: Riesgos
Arquitectura C - Peso: 15%

Este criterio evalúa riesgos del proyecto en múltiples dimensiones:
1. Riesgo Técnico/Operacional (30%)
2. Riesgo Social/Comunitario (25%)
3. Riesgo Financiero/Presupuestario (20%)
4. Riesgo Regulatorio/Legal (15%)
5. Factores Automáticos de Riesgo (10%)

Metodología: Score INVERSO
- Más riesgo → Score más bajo
- Menos riesgo → Score más alto

Scoring permite identificar proyectos con perfil de riesgo favorable.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from src.models.proyecto import ProyectoSocial


@dataclass
class ResultadoRiesgos:
    """Resultado detallado de evaluación Riesgos"""
    score: float  # 0-100

    # Niveles de riesgo (1-25)
    nivel_riesgo_tecnico: int
    nivel_riesgo_social: int
    nivel_riesgo_financiero: int
    nivel_riesgo_regulatorio: int

    # Scores por componente (0-100, inverso)
    score_riesgo_tecnico: float
    score_riesgo_social: float
    score_riesgo_financiero: float
    score_riesgo_regulatorio: float
    score_factores_automaticos: float

    # Contribuciones
    contribucion_tecnico: float
    contribucion_social: float
    contribucion_financiero: float
    contribucion_regulatorio: float
    contribucion_automaticos: float

    # Metadata
    nivel_general: str  # "BAJO", "MEDIO", "ALTO", "CRÍTICO"
    mensaje: str
    alertas: List[str]
    recomendaciones: List[str]


class RiesgosCriterio:
    """
    Evalúa riesgos del proyecto en múltiples dimensiones.

    Criterio: 15% del score total (Arquitectura C)

    Score INVERSO: Más riesgo = Menos puntos

    Componentes:
    - Riesgo Técnico/Operacional (30%)
    - Riesgo Social/Comunitario (25%)
    - Riesgo Financiero/Presupuestario (20%)
    - Riesgo Regulatorio/Legal (15%)
    - Factores Automáticos (10%)
    """

    # Pesos de componentes
    PESO_TECNICO = 0.30
    PESO_SOCIAL = 0.25
    PESO_FINANCIERO = 0.20
    PESO_REGULATORIO = 0.15
    PESO_AUTOMATICOS = 0.10

    def __init__(self, peso: float = 0.15):
        self.peso = peso
        self.nombre = "Evaluación de Riesgos"
        self.descripcion = "Evalúa riesgos técnicos, sociales, financieros y regulatorios"

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa riesgos del proyecto y retorna score 0-100 (inverso).

        Args:
            proyecto: Proyecto a evaluar

        Returns:
            Score 0-100 (más riesgo = menos puntos)

        Raises:
            ValueError: Si faltan datos requeridos
        """
        # Validar datos
        validacion = proyecto.validar_riesgos()
        if not validacion['valido']:
            raise ValueError(f"Datos riesgos inválidos: {validacion['mensaje']}")

        # Calcular componentes
        score_tecnico = self._calcular_riesgo_individual(
            proyecto.riesgo_tecnico_probabilidad,
            proyecto.riesgo_tecnico_impacto
        )

        score_social = self._calcular_riesgo_individual(
            proyecto.riesgo_social_probabilidad,
            proyecto.riesgo_social_impacto
        )

        score_financiero = self._calcular_riesgo_individual(
            proyecto.riesgo_financiero_probabilidad,
            proyecto.riesgo_financiero_impacto
        )

        score_regulatorio = self._calcular_riesgo_individual(
            proyecto.riesgo_regulatorio_probabilidad,
            proyecto.riesgo_regulatorio_impacto
        )

        score_automaticos = self._calcular_factores_automaticos(proyecto)

        # Score total ponderado
        score = (
            score_tecnico * self.PESO_TECNICO +
            score_social * self.PESO_SOCIAL +
            score_financiero * self.PESO_FINANCIERO +
            score_regulatorio * self.PESO_REGULATORIO +
            score_automaticos * self.PESO_AUTOMATICOS
        )

        return score

    def evaluar_detallado(self, proyecto: ProyectoSocial) -> ResultadoRiesgos:
        """
        Evaluación detallada con metadata y alertas.

        Args:
            proyecto: Proyecto a evaluar

        Returns:
            ResultadoRiesgos con detalles completos
        """
        # Validar
        validacion = proyecto.validar_riesgos()
        alertas = validacion.get('advertencias', [])
        recomendaciones = []

        # Calcular niveles de riesgo
        nivel_tecnico = self._calcular_nivel_riesgo(
            proyecto.riesgo_tecnico_probabilidad,
            proyecto.riesgo_tecnico_impacto
        )

        nivel_social = self._calcular_nivel_riesgo(
            proyecto.riesgo_social_probabilidad,
            proyecto.riesgo_social_impacto
        )

        nivel_financiero = self._calcular_nivel_riesgo(
            proyecto.riesgo_financiero_probabilidad,
            proyecto.riesgo_financiero_impacto
        )

        nivel_regulatorio = self._calcular_nivel_riesgo(
            proyecto.riesgo_regulatorio_probabilidad,
            proyecto.riesgo_regulatorio_impacto
        )

        # Calcular scores (inversos)
        score_tecnico = self._nivel_a_score_inverso(nivel_tecnico)
        score_social = self._nivel_a_score_inverso(nivel_social)
        score_financiero = self._nivel_a_score_inverso(nivel_financiero)
        score_regulatorio = self._nivel_a_score_inverso(nivel_regulatorio)
        score_automaticos = self._calcular_factores_automaticos(proyecto)

        # Contribuciones
        contrib_tecnico = score_tecnico * self.PESO_TECNICO
        contrib_social = score_social * self.PESO_SOCIAL
        contrib_financiero = score_financiero * self.PESO_FINANCIERO
        contrib_regulatorio = score_regulatorio * self.PESO_REGULATORIO
        contrib_automaticos = score_automaticos * self.PESO_AUTOMATICOS

        # Score total
        score = (
            contrib_tecnico +
            contrib_social +
            contrib_financiero +
            contrib_regulatorio +
            contrib_automaticos
        )

        # Generar alertas por riesgos críticos
        if nivel_tecnico >= 20:
            alertas.append(
                f"🚨 Riesgo Técnico CRÍTICO (nivel {nivel_tecnico}): "
                f"Requiere plan de mitigación robusto"
            )
        elif nivel_tecnico >= 13:
            alertas.append(
                f"⚠️  Riesgo Técnico ALTO (nivel {nivel_tecnico}): "
                f"Evaluar alternativas técnicas"
            )

        if nivel_social >= 20:
            alertas.append(
                f"🚨 Riesgo Social CRÍTICO (nivel {nivel_social}): "
                f"Alto riesgo de conflicto comunitario"
            )
        elif nivel_social >= 13:
            alertas.append(
                f"⚠️  Riesgo Social ALTO (nivel {nivel_social}): "
                f"Fortalecer estrategia de relacionamiento"
            )

        if nivel_financiero >= 20:
            alertas.append(
                f"🚨 Riesgo Financiero CRÍTICO (nivel {nivel_financiero}): "
                f"Revisar viabilidad presupuestaria"
            )

        if nivel_regulatorio >= 20:
            alertas.append(
                f"🚨 Riesgo Regulatorio CRÍTICO (nivel {nivel_regulatorio}): "
                f"Marco legal muy incierto"
            )

        # Recomendaciones
        if score < 40:
            recomendaciones.append(
                "⚠️  Perfil de riesgo ALTO: Proyecto requiere análisis detallado "
                "de viabilidad y planes robustos de mitigación"
            )
        elif score < 60:
            recomendaciones.append(
                "💡 Perfil de riesgo MEDIO: Desarrollar planes de mitigación "
                "para riesgos identificados"
            )

        if any(n >= 20 for n in [nivel_tecnico, nivel_social, nivel_financiero, nivel_regulatorio]):
            recomendaciones.append(
                "🔴 Uno o más riesgos CRÍTICOS: Considerar si proyecto es viable "
                "o requiere rediseño fundamental"
            )

        # Determinar nivel general
        nivel_general = self._determinar_nivel_general(
            [nivel_tecnico, nivel_social, nivel_financiero, nivel_regulatorio]
        )

        # Mensaje
        if score >= 80:
            mensaje = "Perfil de riesgo BAJO - Proyecto con alta viabilidad"
        elif score >= 60:
            mensaje = "Perfil de riesgo MEDIO - Riesgos manejables"
        elif score >= 40:
            mensaje = "Perfil de riesgo ALTO - Requiere mitigación significativa"
        else:
            mensaje = "Perfil de riesgo CRÍTICO - Viabilidad cuestionable"

        return ResultadoRiesgos(
            score=score,
            nivel_riesgo_tecnico=nivel_tecnico,
            nivel_riesgo_social=nivel_social,
            nivel_riesgo_financiero=nivel_financiero,
            nivel_riesgo_regulatorio=nivel_regulatorio,
            score_riesgo_tecnico=score_tecnico,
            score_riesgo_social=score_social,
            score_riesgo_financiero=score_financiero,
            score_riesgo_regulatorio=score_regulatorio,
            score_factores_automaticos=score_automaticos,
            contribucion_tecnico=contrib_tecnico,
            contribucion_social=contrib_social,
            contribucion_financiero=contrib_financiero,
            contribucion_regulatorio=contrib_regulatorio,
            contribucion_automaticos=contrib_automaticos,
            nivel_general=nivel_general,
            mensaje=mensaje,
            alertas=alertas,
            recomendaciones=recomendaciones
        )

    def _calcular_nivel_riesgo(self, probabilidad: int, impacto: int) -> int:
        """
        Calcula nivel de riesgo: Probabilidad × Impacto

        Returns:
            Nivel de riesgo 1-25
        """
        return probabilidad * impacto

    def _nivel_a_score_inverso(self, nivel: int) -> float:
        """
        Convierte nivel de riesgo a score inverso.

        Score = 100 - (nivel / 25 × 100)

        Args:
            nivel: Nivel de riesgo (1-25)

        Returns:
            Score 0-100 (inverso: más riesgo = menos puntos)
        """
        score = 100 - (nivel / 25 * 100)
        return max(min(score, 100), 0)

    def _calcular_riesgo_individual(self, probabilidad: Optional[int], impacto: Optional[int]) -> float:
        """Calcula score de un riesgo individual"""
        if probabilidad is None or impacto is None:
            return 70.0  # Neutro si no especificado

        nivel = self._calcular_nivel_riesgo(probabilidad, impacto)
        return self._nivel_a_score_inverso(nivel)

    def _calcular_factores_automaticos(self, proyecto: ProyectoSocial) -> float:
        """
        Calcula score de factores automáticos de riesgo.

        Penalizaciones automáticas basadas en características del proyecto.
        """
        score = 100.0

        # Penalización por presupuesto alto
        if proyecto.presupuesto_total:
            if proyecto.presupuesto_total > 1_000_000_000:
                score -= 15
            elif proyecto.presupuesto_total > 500_000_000:
                score -= 10

        # Penalización por duración larga
        if proyecto.duracion_estimada_meses:
            if proyecto.duracion_estimada_meses > 24:
                score -= 10
            elif proyecto.duracion_estimada_meses > 12:
                score -= 5

        # Penalización por múltiples departamentos
        if proyecto.departamentos and len(proyecto.departamentos) > 2:
            score -= 5

        # Penalización por población vulnerable
        if (hasattr(proyecto, 'stakeholders_involucrados') and
            proyecto.stakeholders_involucrados and
            'comunidades_indigenas' in proyecto.stakeholders_involucrados):
            score -= 5  # Mayor complejidad cultural/legal

        # Penalización por municipio NO-PDET (potencialmente menos apoyo)
        if hasattr(proyecto, 'tiene_municipios_pdet') and not proyecto.tiene_municipios_pdet:
            # Solo si está en zona que podría tener conflictos
            if proyecto.departamentos:
                departamentos_conflicto = ['CHOCÓ', 'CAUCA', 'NARIÑO', 'PUTUMAYO', 'CAQUETÁ']
                if any(d in departamentos_conflicto for d in proyecto.departamentos):
                    score -= 10

        return max(score, 0)

    def _determinar_nivel_general(self, niveles: List[int]) -> str:
        """
        Determina nivel general de riesgo basado en todos los niveles.

        Usa el nivel más alto (más conservador)
        """
        max_nivel = max(niveles) if niveles else 0

        if max_nivel >= 20:
            return "CRÍTICO"
        elif max_nivel >= 13:
            return "ALTO"
        elif max_nivel >= 6:
            return "MEDIO"
        else:
            return "BAJO"

    def aplicar_peso(self, score: float) -> float:
        """
        Aplica el peso del criterio (15%) al score.

        Args:
            score: Score base 0-100

        Returns:
            Contribución al score final (0-15)
        """
        return score * self.peso
