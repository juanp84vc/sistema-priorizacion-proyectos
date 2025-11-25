"""
Estrategia de scoring ponderado.
SRP: Solo implementa lógica de scoring ponderado.
"""
from typing import List
from estrategias.base import EstrategiaEvaluacion
from models.proyecto import ProyectoSocial
from models.evaluacion import ResultadoEvaluacion


class ScoringPonderado(EstrategiaEvaluacion):
    """
    Estrategia de evaluación con scoring ponderado.

    Calcula score final como suma ponderada de scores
    de criterios individuales.

    Score_final = Σ(score_criterio_i × peso_i)
    """

    def evaluar_proyecto(
        self,
        proyecto: ProyectoSocial,
        criterios: List
    ) -> ResultadoEvaluacion:
        """
        Evalúa proyecto con scoring ponderado.

        Args:
            proyecto: Proyecto a evaluar
            criterios: Lista de CriterioEvaluacion

        Returns:
            ResultadoEvaluacion con score ponderado
        """
        score_total = 0.0
        scores_por_criterio = {}
        pesos_por_criterio = {}

        # Validar que pesos sumen 1.0
        suma_pesos = sum(c.peso for c in criterios)
        if not (0.99 <= suma_pesos <= 1.01):  # Tolerancia para float
            raise ValueError(
                f"Suma de pesos debe ser 1.0, actual: {suma_pesos}"
            )

        # Evaluar cada criterio
        detalle_criterios = {}
        for criterio in criterios:
            score_criterio = criterio.evaluar(proyecto)
            score_ponderado = score_criterio * criterio.peso

            detalle_criterios[criterio.nombre] = {
                'score_base': score_criterio,
                'peso': criterio.peso,
                'score_ponderado': score_ponderado
            }
            score_total += score_ponderado

        resultado = ResultadoEvaluacion(
            proyecto_id=proyecto.id,
            proyecto_nombre=proyecto.nombre,
            score_final=round(score_total, 2),
            detalle_criterios=detalle_criterios,
            recomendacion=self._generar_recomendacion(score_total)
        )

        # Agregar observación sobre la estrategia
        resultado.agregar_observacion(f"Estrategia: {self.get_nombre()}")
        resultado.agregar_observacion(f"Suma de pesos: {suma_pesos:.2f}")

        return resultado

    def _generar_recomendacion(self, score: float) -> str:
        """Genera recomendación basada en score."""
        if score >= 80:
            return "PRIORIDAD ALTA - Proyecto altamente recomendado"
        elif score >= 60:
            return "PRIORIDAD MEDIA - Proyecto recomendado con ajustes"
        elif score >= 40:
            return "PRIORIDAD BAJA - Revisar viabilidad"
        else:
            return "NO RECOMENDADO - Requiere mejoras significativas"

    def get_nombre(self) -> str:
        return "Scoring Ponderado"

    def get_descripcion(self) -> str:
        return (
            "Estrategia de evaluación que calcula score final como "
            "suma ponderada de scores individuales de criterios."
        )
