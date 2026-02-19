"""
Criterio de evaluación: Social Return on Investment (SROI)
Arquitectura C - Peso: 40% (DOMINANTE)

Este criterio evalúa el retorno social de la inversión, que es la métrica
MÁS IMPORTANTE para priorizar proyectos de valor compartido.

Metodología (Ajuste Feb 2026):
- Función logarítmica continua: Score = 60 + 35 × ln(SROI) / ln(3)
- Elimina discontinuidades de rangos discretos
- Gate de rechazo preservado: SROI < 1.0 → Score 0
- Puntos de anclaje: SROI=1→60, SROI=2→82, SROI=3→95
- Techo: 98 pts (evita distorsión por SROI extremos)
- SROI > 7.0 → Alerta de verificación

Historial:
- Arquitectura C aprobada (15 Nov 2025) - rangos discretos
- Ajuste metodológico (Feb 2026) - función logarítmica continua
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import math
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

    Conversión SROI → Score (función logarítmica continua):
    - < 1.0: 0 (RECHAZAR - destruye valor social)
    - >= 1.0: Score = 60 + 35 × ln(SROI) / ln(3)
    - Techo: 98 pts

    Puntos de referencia:
    - SROI 1.0 → 60 pts
    - SROI 1.5 → 73 pts
    - SROI 2.0 → 82 pts
    - SROI 3.0 → 95 pts
    - SROI 5.0 → 98 pts (techo)

    Gates de validación:
    - SROI < 1.0: Rechazo automático
    - SROI > 7.0: Alerta verificación metodológica
    - SROI > 5.0: Requiere observaciones obligatorias
    """

    # Constantes de la función logarítmica
    SCORE_BASE = 60.0       # Score en SROI = 1.0
    SCORE_RANGO = 35.0      # Rango adicional (60 + 35 = 95 en SROI = 3.0)
    LOG_REFERENCIA = math.log(3.0)  # ln(3) ≈ 1.0986
    SCORE_TECHO = 98.0      # Techo máximo

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
        Convierte valor SROI a score 0-100 usando función logarítmica continua.

        Ajuste metodológico (Feb 2026):
        - < 1.0: 0 (RECHAZAR - gate preservado)
        - >= 1.0: Score = 60 + 35 × ln(SROI) / ln(3)
        - Techo: 98 pts

        Puntos de anclaje:
        - SROI 1.0 → 60 (ln(1)=0, score=60+0=60)
        - SROI 2.0 → 82.1
        - SROI 3.0 → 95.0 (ln(3)/ln(3)=1, score=60+35=95)
        - SROI 5.0+ → 98 (techo)

        Args:
            sroi: Valor SROI del proyecto

        Returns:
            Score 0-100
        """
        if sroi < 1.0:
            return 0.0

        # Función logarítmica continua
        score = self.SCORE_BASE + self.SCORE_RANGO * math.log(sroi) / self.LOG_REFERENCIA

        # Aplicar techo y piso
        return min(max(score, 0.0), self.SCORE_TECHO)

    def get_nivel_prioridad(self, score: float) -> str:
        """
        Determina nivel de prioridad basado en score SROI.

        Con función continua, los niveles usan rangos en vez de valores exactos:
        - 0: RECHAZAR (SROI < 1.0)
        - 1-69: BAJA (SROI ~1.0-1.7)
        - 70-84: MEDIA (SROI ~1.7-2.5)
        - 85+: ALTA (SROI ~2.5+)

        Args:
            score: Score 0-100

        Returns:
            Nivel de prioridad como string
        """
        if score == 0:
            return "RECHAZAR"
        elif score < 70:
            return "BAJA"
        elif score < 85:
            return "MEDIA"
        else:
            return "ALTA"

    def aplicar_peso(self, score: float) -> float:
        """
        Aplica el peso del criterio (40%) al score.

        Args:
            score: Score base 0-100

        Returns:
            Contribución al score final (0-40)
        """
        return score * self.peso

    def get_nombre(self) -> str:
        """Retorna el nombre del criterio"""
        return self.nombre

    def get_descripcion(self) -> str:
        """Retorna la descripción del criterio"""
        return self.descripcion
