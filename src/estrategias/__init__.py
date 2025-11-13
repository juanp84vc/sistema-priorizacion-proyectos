"""
Módulo de estrategias de evaluación.
OCP: Fácilmente extensible con nuevas estrategias.
"""
from estrategias.base import EstrategiaEvaluacion
from estrategias.scoring_ponderado import ScoringPonderado
from estrategias.scoring_umbral import ScoringUmbral

__all__ = [
    'EstrategiaEvaluacion',
    'ScoringPonderado',
    'ScoringUmbral'
]
