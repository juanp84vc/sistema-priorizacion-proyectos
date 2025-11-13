"""
Abstracción base para estrategias de evaluación.
DIP: Sistema depende de abstracción, no de implementaciones concretas.
"""
from abc import ABC, abstractmethod
from typing import List
from models.proyecto import ProyectoSocial
from models.evaluacion import ResultadoEvaluacion


class EstrategiaEvaluacion(ABC):
    """
    Abstracción para estrategias de evaluación.

    Strategy Pattern: Permite cambiar algoritmo de evaluación
    sin modificar código cliente.
    """

    @abstractmethod
    def evaluar_proyecto(
        self,
        proyecto: ProyectoSocial,
        criterios: List
    ) -> ResultadoEvaluacion:
        """
        Evalúa un proyecto usando los criterios proporcionados.

        Args:
            proyecto: Proyecto a evaluar
            criterios: Lista de criterios a aplicar

        Returns:
            ResultadoEvaluacion con scores y detalles
        """
        pass

    @abstractmethod
    def get_nombre(self) -> str:
        """Retorna nombre de la estrategia."""
        pass

    @abstractmethod
    def get_descripcion(self) -> str:
        """Retorna descripción de la estrategia."""
        pass
