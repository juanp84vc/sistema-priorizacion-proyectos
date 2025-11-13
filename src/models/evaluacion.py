"""
Modelo de resultado de evaluación.
SRP: Solo almacena resultados de evaluación.
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ResultadoEvaluacion:
    """
    Resultado de evaluación de un proyecto.
    SRP: Solo almacena resultados de evaluación.
    """
    proyecto_id: str
    proyecto_nombre: str
    score_final: float
    detalle_criterios: Dict[str, Dict[str, float]]
    recomendacion: str
    observaciones: List[str] = field(default_factory=list)

    def agregar_observacion(self, observacion: str):
        """Agrega una observación al resultado"""
        self.observaciones.append(observacion)

    def to_dict(self) -> Dict:
        """Convierte a diccionario para exportación"""
        return {
            'proyecto_id': self.proyecto_id,
            'proyecto_nombre': self.proyecto_nombre,
            'score_final': round(self.score_final, 2),
            'detalle_criterios': self.detalle_criterios,
            'recomendacion': self.recomendacion,
            'observaciones': self.observaciones
        }
