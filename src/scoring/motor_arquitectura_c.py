"""
Motor de Scoring - Arquitectura C
Sistema de priorización con SROI dominante (40%)

Arquitectura C aprobada (15 Nov 2025):
- SROI: 40% (dominante)
- Stakeholders: 25%
- Probabilidad Aprobación: 20%
- Riesgos: 15%

Cambios vs sistema anterior:
- SROI: 3.75% → 40% (10.6x incremento)
- Costo-Efectividad: ELIMINADO
- Datos oficiales PDET/ZOMAC integrados
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.models.proyecto import ProyectoSocial
from src.criterios.sroi import SROICriterio, ResultadoSROI
from src.criterios.probabilidad_aprobacion_pdet import ProbabilidadAprobacionCriterio
from src.criterios.stakeholders import StakeholdersCriterio
from src.criterios.riesgos import RiesgosCriterio


@dataclass
class ResultadoScoring:
    """Resultado detallado del scoring de un proyecto"""

    # Score final
    score_total: float  # 0-100

    # Scores por criterio
    score_sroi: float  # 0-100
    score_stakeholders: float  # 0-100
    score_probabilidad: float  # 0-100
    score_riesgos: float  # 0-100

    # Contribuciones al score final (aplicando pesos)
    contribucion_sroi: float  # score × 0.40
    contribucion_stakeholders: float  # score × 0.25
    contribucion_probabilidad: float  # score × 0.20
    contribucion_riesgos: float  # score × 0.15

    # Nivel de prioridad
    nivel_prioridad: str  # "MUY ALTA", "ALTA", "MEDIA", "BAJA", "RECHAZADO", "NO ELEGIBLE"

    # Metadata
    fecha_calculo: datetime = field(default_factory=datetime.now)
    version_arquitectura: str = "C"

    # Alertas y recomendaciones
    alertas: List[str] = field(default_factory=list)
    recomendaciones: List[str] = field(default_factory=list)

    # Metadata detallada (opcional)
    resultado_sroi_detallado: Optional[ResultadoSROI] = None


class MotorScoringArquitecturaC:
    """
    Motor de scoring para Arquitectura C

    Calcula score final de proyectos usando:
    - SROI (40%) - Criterio dominante
    - Stakeholders (25%)
    - Probabilidad Aprobación (20%) - Con datos PDET/ZOMAC
    - Riesgos (15%)

    Sistema elimina Costo-Efectividad (era 25%, ahora 0%)
    """

    VERSION = "C"

    # Pesos aprobados Arquitectura C
    PESO_SROI = 0.40
    PESO_STAKEHOLDERS = 0.25
    PESO_PROBABILIDAD = 0.20
    PESO_RIESGOS = 0.15

    def __init__(self, db_path: str = "data/proyectos.db"):
        """
        Inicializa el motor de scoring.

        Args:
            db_path: Ruta a la base de datos con matriz PDET
        """
        # Criterios implementados
        self.criterio_sroi = SROICriterio(peso=self.PESO_SROI)
        self.criterio_probabilidad = ProbabilidadAprobacionCriterio(
            peso=self.PESO_PROBABILIDAD,
            db_path=db_path
        )
        self.criterio_stakeholders = StakeholdersCriterio(peso=self.PESO_STAKEHOLDERS)
        self.criterio_riesgos = RiesgosCriterio(peso=self.PESO_RIESGOS)

    def calcular_score(
        self,
        proyecto: ProyectoSocial,
        detallado: bool = True
    ) -> ResultadoScoring:
        """
        Calcula score final del proyecto usando Arquitectura C

        Args:
            proyecto: Proyecto a evaluar
            detallado: Si True, incluye metadata detallada

        Returns:
            ResultadoScoring con score total, contribuciones y alertas

        Raises:
            ValueError: Si proyecto no tiene datos mínimos requeridos
        """

        alertas = []
        recomendaciones = []

        # ========== GATE DE ELEGIBILIDAD PDET/ZOMAC (Ajuste CONFIS Feb 2026) ==========
        if not proyecto.es_elegible_oxi:
            alertas.append(
                "🚫 PROYECTO NO ELEGIBLE - Obras por Impuestos solo aplica "
                "para municipios PDET y/o ZOMAC"
            )
            return ResultadoScoring(
                score_total=0,
                score_sroi=0,
                score_stakeholders=0,
                score_probabilidad=0,
                score_riesgos=0,
                contribucion_sroi=0,
                contribucion_stakeholders=0,
                contribucion_probabilidad=0,
                contribucion_riesgos=0,
                nivel_prioridad="NO ELEGIBLE",
                fecha_calculo=datetime.now(),
                version_arquitectura=self.VERSION,
                alertas=alertas,
                recomendaciones=[
                    "📋 Verificar que el municipio esté en la lista PDET/ZOMAC",
                    "📋 Consultar Anexo 2 CONFIS para municipios elegibles"
                ]
            )

        # ========== CRITERIO 1: SROI (40%) ==========
        try:
            if detallado:
                resultado_sroi = self.criterio_sroi.evaluar_detallado(proyecto)
                score_sroi = resultado_sroi.score
                alertas.extend(resultado_sroi.alertas)
            else:
                score_sroi = self.criterio_sroi.evaluar(proyecto)
                resultado_sroi = None

            contribucion_sroi = score_sroi * self.PESO_SROI

        except ValueError as e:
            alertas.append(f"⚠️  Error SROI: {e}")
            score_sroi = 0
            contribucion_sroi = 0
            resultado_sroi = None

        # ========== CRITERIO 2: STAKEHOLDERS (25%) ==========
        try:
            score_stakeholders = self.criterio_stakeholders.evaluar(proyecto)
            contribucion_stakeholders = score_stakeholders * self.PESO_STAKEHOLDERS
        except ValueError as e:
            alertas.append(f"⚠️  Error Stakeholders: {e}")
            score_stakeholders = 0
            contribucion_stakeholders = 0

        # ========== CRITERIO 3: PROBABILIDAD APROBACIÓN (20%) ==========
        try:
            score_probabilidad = self.criterio_probabilidad.evaluar(proyecto)
            contribucion_probabilidad = score_probabilidad * self.PESO_PROBABILIDAD

            # Alertas específicas CONFIS
            if score_probabilidad >= 80:
                recomendaciones.append(
                    "💡 Alta prioridad CONFIS - Proyecto con excelente probabilidad de aprobación"
                )
            elif score_probabilidad >= 60:
                recomendaciones.append(
                    "ℹ️  Prioridad media CONFIS - Probabilidad aceptable de aprobación"
                )
        except Exception as e:
            alertas.append(f"⚠️  Error Probabilidad: {e}")
            score_probabilidad = 0
            contribucion_probabilidad = 0

        # ========== CRITERIO 4: RIESGOS (15%) ==========
        try:
            score_riesgos = self.criterio_riesgos.evaluar(proyecto)
            contribucion_riesgos = score_riesgos * self.PESO_RIESGOS
        except ValueError as e:
            alertas.append(f"⚠️  Error Riesgos: {e}")
            score_riesgos = 0
            contribucion_riesgos = 0

        # ========== SCORE TOTAL ==========
        score_total = (
            contribucion_sroi +
            contribucion_stakeholders +
            contribucion_probabilidad +
            contribucion_riesgos
        )

        # Asegurar rango 0-100
        score_total = min(max(score_total, 0), 100)

        # ========== NIVEL DE PRIORIDAD ==========
        nivel_prioridad = self._determinar_nivel_prioridad(
            score_total,
            score_sroi
        )

        # ========== RECOMENDACIONES ADICIONALES ==========
        if score_sroi == 0:
            alertas.insert(0, "🚫 PROYECTO RECHAZADO - SROI < 1.0 destruye valor social")

        if score_total >= 80:
            recomendaciones.append("✅ Proyecto de alta prioridad - Recomendar aprobación")
        elif score_total < 50:
            recomendaciones.append("⚠️  Proyecto de baja prioridad - Revisar viabilidad")

        # ========== CONSTRUIR RESULTADO ==========
        return ResultadoScoring(
            score_total=score_total,
            score_sroi=score_sroi,
            score_stakeholders=score_stakeholders,
            score_probabilidad=score_probabilidad,
            score_riesgos=score_riesgos,
            contribucion_sroi=contribucion_sroi,
            contribucion_stakeholders=contribucion_stakeholders,
            contribucion_probabilidad=contribucion_probabilidad,
            contribucion_riesgos=contribucion_riesgos,
            nivel_prioridad=nivel_prioridad,
            fecha_calculo=datetime.now(),
            version_arquitectura=self.VERSION,
            alertas=alertas,
            recomendaciones=recomendaciones,
            resultado_sroi_detallado=resultado_sroi
        )

    def _determinar_nivel_prioridad(
        self,
        score_total: float,
        score_sroi: float
    ) -> str:
        """
        Determina nivel de prioridad del proyecto

        Considera tanto score total como SROI (puede rechazar)
        """
        if score_sroi == 0:
            return "RECHAZADO"
        elif score_total >= 85:
            return "MUY ALTA"
        elif score_total >= 70:
            return "ALTA"
        elif score_total >= 50:
            return "MEDIA"
        else:
            return "BAJA"

    def generar_reporte(self, resultado: ResultadoScoring) -> str:
        """
        Genera reporte en texto del resultado

        Args:
            resultado: ResultadoScoring a reportar

        Returns:
            String con reporte formateado
        """
        lineas = []
        lineas.append("=" * 70)
        lineas.append("RESULTADO DE SCORING - ARQUITECTURA C")
        lineas.append("=" * 70)
        lineas.append("")

        # Score total
        lineas.append(f"SCORE TOTAL: {resultado.score_total:.1f}/100")
        lineas.append(f"NIVEL: {resultado.nivel_prioridad}")
        lineas.append("")

        # Desglose por criterio
        lineas.append("Desglose por criterio:")
        lineas.append("-" * 70)

        lineas.append(
            f"1. SROI (40%):                 "
            f"{resultado.score_sroi:.1f}/100 → "
            f"{resultado.contribucion_sroi:.1f} pts"
        )

        lineas.append(
            f"2. Stakeholders (25%):         "
            f"{resultado.score_stakeholders:.1f}/100 → "
            f"{resultado.contribucion_stakeholders:.1f} pts"
        )

        lineas.append(
            f"3. Prob. Aprobación (20%):     "
            f"{resultado.score_probabilidad:.1f}/100 → "
            f"{resultado.contribucion_probabilidad:.1f} pts"
        )

        lineas.append(
            f"4. Riesgos (15%):              "
            f"{resultado.score_riesgos:.1f}/100 → "
            f"{resultado.contribucion_riesgos:.1f} pts"
        )

        lineas.append("")
        lineas.append(
            f"TOTAL: {resultado.score_total:.1f}/100"
        )

        # Alertas
        if resultado.alertas:
            lineas.append("")
            lineas.append("Alertas:")
            lineas.append("-" * 70)
            for alerta in resultado.alertas:
                lineas.append(f"  {alerta}")

        # Recomendaciones
        if resultado.recomendaciones:
            lineas.append("")
            lineas.append("Recomendaciones:")
            lineas.append("-" * 70)
            for rec in resultado.recomendaciones:
                lineas.append(f"  {rec}")

        lineas.append("")
        lineas.append("=" * 70)

        return "\n".join(lineas)


# Función helper para uso rápido
def calcular_score_proyecto(proyecto: ProyectoSocial, db_path: str = "data/proyectos.db") -> ResultadoScoring:
    """
    Helper function para calcular score de un proyecto

    Args:
        proyecto: Proyecto a evaluar
        db_path: Ruta a base de datos con matriz PDET

    Returns:
        ResultadoScoring completo
    """
    motor = MotorScoringArquitecturaC(db_path=db_path)
    return motor.calcular_score(proyecto, detallado=True)
