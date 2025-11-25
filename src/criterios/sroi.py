"""
Criterio de evaluación: Social Return on Investment (SROI)
Arquitectura C - Peso: 40% (DOMINANTE)

Este criterio evalúa el retorno social de la inversión, que es la métrica
MÁS IMPORTANTE para priorizar proyectos de valor compartido.

Metodología:
- Usa rangos aprobados 15 Nov 2025
- SROI < 1.0 → Rechazo automático
- SROI ≥ 3.0 → Prioridad alta
- SROI > 7.0 → Alerta de verificación

Referencias:
- AUDITORIA_SROI_ACTUAL.md
- PROPUESTA_SROI_DOMINANTE.md
- Arquitectura C aprobada (15 Nov 2025)
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.proyecto import ProyectoSocial


@dataclass
class ResultadoSROI:
    """Resultado detallado de evaluación SROI"""
    score: float  # 0-100
    sroi_valor: float  # Valor SROI original
    nivel: str  # "RECHAZAR", "BAJA", "MEDIA", "ALTA", "VERIFICAR"
    mensaje: str
    requiere_observaciones: bool
    alertas: List[str]


class SROICriterio:
    """
    Evalúa retorno social de la inversión (SROI).

    Criterio: 40% del score total (Arquitectura C)

    Conversión SROI → Score:
    - < 1.0: 0 (RECHAZAR - destruye valor)
    - 1.0-1.99: 60 (Prioridad Baja)
    - 2.0-2.99: 80 (Prioridad Media)
    - ≥ 3.0: 95 (Prioridad Alta)

    Gates de validación:
    - SROI < 1.0: Rechazo automático
    - SROI > 7.0: Alerta verificación metodológica
    - SROI > 5.0: Requiere observaciones obligatorias
    """

    def __init__(self, peso: float = 0.40):
        """
        Inicializa el criterio SROI.

        Args:
            peso: Peso del criterio (default: 0.40 = 40%)
        """
        self.peso = peso
        self.nombre = "Social Return on Investment (SROI)"
        self.descripcion = "Retorno social de la inversión"

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa el SROI del proyecto y retorna score 0-100.

        Args:
            proyecto: Proyecto a evaluar

        Returns:
            Score 0-100 basado en rangos aprobados

        Raises:
            ValueError: Si SROI es inválido
        """
        # Obtener SROI (usar valor por defecto si no está definido)
        sroi = proyecto.indicadores_impacto.get('sroi')

        if sroi is None:
            # Valor por defecto conservador: 1.5 (prioridad baja, score 60)
            # Esto permite evaluar proyectos antiguos sin SROI definido
            sroi = 1.5

        if not isinstance(sroi, (int, float)):
            raise ValueError(f"SROI debe ser numérico, recibido: {type(sroi).__name__}")

        if sroi < 0:
            raise ValueError(f"SROI no puede ser negativo: {sroi}")

        # Convertir SROI a score
        score = self._convertir_sroi_a_score(sroi)

        return score

    def evaluar_detallado(self, proyecto: ProyectoSocial) -> ResultadoSROI:
        """
        Evaluación detallada con metadata y alertas.

        Args:
            proyecto: Proyecto a evaluar

        Returns:
            ResultadoSROI con score, nivel, mensajes y alertas
        """
        sroi = proyecto.indicadores_impacto.get('sroi', 0)

        # Obtener validación del proyecto
        validacion = proyecto.validar_sroi()

        # Calcular score
        score = self._convertir_sroi_a_score(sroi)

        # Generar alertas
        alertas = []

        if sroi < 1.0:
            alertas.append("⛔ PROYECTO RECHAZADO - Destruye valor social")

        if sroi > 7.0:
            alertas.append(
                "⚠️  SROI excepcional (>7.0) - Verificar metodología de cálculo"
            )
            alertas.append(
                "   Posibles causas: Error metodológico, proxies inflados, "
                "horizonte temporal muy largo"
            )

        if sroi > 5.0 and not proyecto.observaciones_sroi:
            alertas.append(
                "📝 SROI alto - Se requiere documentar metodología en observaciones_sroi"
            )

        if 1.0 <= sroi < 2.0:
            alertas.append(
                "💡 SROI marginal - Considerar optimizar diseño del proyecto"
            )

        return ResultadoSROI(
            score=score,
            sroi_valor=sroi,
            nivel=validacion['nivel'],
            mensaje=validacion['mensaje'],
            requiere_observaciones=validacion['requiere_observaciones'],
            alertas=alertas
        )

    def _convertir_sroi_a_score(self, sroi: float) -> float:
        """
        Convierte valor SROI a score 0-100 usando rangos aprobados.

        Rangos aprobados (15 Nov 2025):
        - < 1.0: 0 (RECHAZAR)
        - 1.0-1.99: 60 (Baja)
        - 2.0-2.99: 80 (Media)
        - ≥ 3.0: 95 (Alta)

        Args:
            sroi: Valor SROI del proyecto

        Returns:
            Score 0-100
        """
        if sroi < 1.0:
            return 0.0
        elif sroi < 2.0:
            return 60.0
        elif sroi < 3.0:
            return 80.0
        else:  # sroi >= 3.0
            return 95.0

    def get_nivel_prioridad(self, score: float) -> str:
        """
        Determina nivel de prioridad basado en score.

        Args:
            score: Score 0-100

        Returns:
            Nivel de prioridad como string
        """
        if score == 0:
            return "RECHAZAR"
        elif score == 60:
            return "BAJA"
        elif score == 80:
            return "MEDIA"
        elif score == 95:
            return "ALTA"
        else:
            return "DESCONOCIDO"

    def aplicar_peso(self, score: float) -> float:
        """
        Aplica el peso del criterio (40%) al score.

        Args:
            score: Score base 0-100

        Returns:
            Contribución al score final (0-40)
        """
        return score * self.peso
