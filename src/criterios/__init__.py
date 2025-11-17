"""
Módulo de criterios de evaluación para Arquitectura C
"""

from .sroi import SROICriterio, ResultadoSROI
from .probabilidad_aprobacion_pdet import ProbabilidadAprobacionCriterio
from .stakeholders import StakeholdersCriterio, ResultadoStakeholders
from .riesgos import RiesgosCriterio, ResultadoRiesgos

__all__ = [
    'SROICriterio',
    'ResultadoSROI',
    'ProbabilidadAprobacionCriterio',
    'StakeholdersCriterio',
    'ResultadoStakeholders',
    'RiesgosCriterio',
    'ResultadoRiesgos',
]
