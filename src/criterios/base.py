"""
Abstracción base para criterios de evaluación.
OCP: Abierto a extensión, cerrado a modificación.
DIP: Dependencia en abstracción, no implementación concreta.
"""
from abc import ABC, abstractmethod
from typing import Dict
import sys
from pathlib import Path

# Agregar src al path si no está
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models.proyecto import ProyectoSocial


class CriterioEvaluacion(ABC):
    """
    Abstracción base para todos los criterios de evaluación.
    LSP: Todas las subclases deben poder sustituir esta clase.
    """

    def __init__(self, peso: float):
        """
        Args:
            peso: Peso del criterio (0-1)
        """
        if not 0 <= peso <= 1:
            raise ValueError(f"Peso debe estar entre 0 y 1, recibido: {peso}")
        self._peso = peso

    @abstractmethod
    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa el proyecto según el criterio.

        Args:
            proyecto: Proyecto a evaluar

        Returns:
            Score normalizado entre 0-100
        """
        pass

    @abstractmethod
    def get_nombre(self) -> str:
        """Retorna el nombre del criterio"""
        pass

    @abstractmethod
    def get_descripcion(self) -> str:
        """Retorna la descripción del criterio"""
        pass

    @property
    def peso(self) -> float:
        """Retorna el peso del criterio"""
        return self._peso

    def get_peso(self) -> float:
        """Retorna el peso del criterio"""
        return self._peso

    def evaluar_ponderado(self, proyecto: ProyectoSocial) -> Dict[str, float]:
        """
        Evalúa y pondera el score.

        Returns:
            Dict con score_base y score_ponderado
        """
        score_base = self.evaluar(proyecto)
        score_ponderado = score_base * self._peso

        return {
            'score_base': round(score_base, 2),
            'score_ponderado': round(score_ponderado, 2),
            'peso': self._peso
        }

    def _normalizar_score(self, valor: float, max_valor: float) -> float:
        """
        Normaliza un valor a escala 0-100.

        Args:
            valor: Valor a normalizar
            max_valor: Valor máximo esperado

        Returns:
            Valor normalizado (0-100)
        """
        if max_valor == 0:
            return 0
        return min((valor / max_valor) * 100, 100)
