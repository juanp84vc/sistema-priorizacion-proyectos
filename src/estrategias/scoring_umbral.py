"""
Estrategia de scoring con umbrales mínimos.
SRP: Solo implementa lógica de scoring con umbrales.
"""
from typing import List, Dict
from estrategias.base import EstrategiaEvaluacion
from models.proyecto import ProyectoSocial
from models.evaluacion import ResultadoEvaluacion


class ScoringUmbral(EstrategiaEvaluacion):
    """
    Estrategia con umbrales mínimos por criterio.

    Además del scoring ponderado, valida que cada criterio
    supere un umbral mínimo. Proyectos que no cumplen
    umbrales son rechazados automáticamente.
    """

    def __init__(self, umbrales_minimos: Dict[str, float] = None):
        """
        Args:
            umbrales_minimos: Dict con umbral mínimo por nombre de criterio.
                             Si None, usa umbral default de 40 para todos.
        """
        self.umbrales_minimos = umbrales_minimos or {}
        self.umbral_default = 40.0

    def evaluar_proyecto(
        self,
        proyecto: ProyectoSocial,
        criterios: List
    ) -> ResultadoEvaluacion:
        """
        Evalúa proyecto con umbrales mínimos.

        Args:
            proyecto: Proyecto a evaluar
            criterios: Lista de CriterioEvaluacion

        Returns:
            ResultadoEvaluacion indicando si pasa umbrales
        """
        score_total = 0.0
        scores_por_criterio = {}
        pesos_por_criterio = {}
        criterios_rechazados = []

        # Validar pesos
        suma_pesos = sum(c.peso for c in criterios)
        if not (0.99 <= suma_pesos <= 1.01):
            raise ValueError(
                f"Suma de pesos debe ser 1.0, actual: {suma_pesos}"
            )

        # Evaluar cada criterio y verificar umbrales
        detalle_criterios = {}
        for criterio in criterios:
            nombre_criterio = criterio.get_nombre()
            score_criterio = criterio.evaluar(proyecto)

            # Obtener umbral para este criterio
            umbral = self.umbrales_minimos.get(
                nombre_criterio,
                self.umbral_default
            )

            score_ponderado = score_criterio * criterio.peso

            detalle_criterios[nombre_criterio] = {
                'score_base': score_criterio,
                'peso': criterio.peso,
                'score_ponderado': score_ponderado,
                'umbral': umbral
            }

            # Verificar umbral
            if score_criterio < umbral:
                criterios_rechazados.append({
                    'criterio': nombre_criterio,
                    'score': score_criterio,
                    'umbral_requerido': umbral
                })

            score_total += score_ponderado

        # Generar recomendación
        if criterios_rechazados:
            recomendacion = self._generar_recomendacion_rechazo(
                criterios_rechazados
            )
        else:
            recomendacion = self._generar_recomendacion_aprobado(score_total)

        resultado = ResultadoEvaluacion(
            proyecto_id=proyecto.id,
            proyecto_nombre=proyecto.nombre,
            score_final=round(score_total, 2),
            detalle_criterios=detalle_criterios,
            recomendacion=recomendacion
        )

        # Agregar observaciones
        resultado.agregar_observacion(f"Estrategia: {self.get_nombre()}")
        resultado.agregar_observacion(f"Pasa umbrales: {'Sí' if len(criterios_rechazados) == 0 else 'No'}")

        if criterios_rechazados:
            for rechazo in criterios_rechazados:
                resultado.agregar_observacion(
                    f"❌ {rechazo['criterio']}: {rechazo['score']:.1f} < {rechazo['umbral_requerido']}"
                )

        return resultado

    def _generar_recomendacion_rechazo(
        self,
        criterios_rechazados: List[Dict]
    ) -> str:
        """Genera recomendación para proyectos rechazados."""
        criterios_str = ", ".join([
            f"{c['criterio']} ({c['score']:.1f} < {c['umbral_requerido']})"
            for c in criterios_rechazados
        ])
        return (
            f"RECHAZADO - No cumple umbrales mínimos en: {criterios_str}"
        )

    def _generar_recomendacion_aprobado(self, score: float) -> str:
        """Genera recomendación para proyectos aprobados."""
        if score >= 80:
            return "APROBADO - PRIORIDAD ALTA"
        elif score >= 60:
            return "APROBADO - PRIORIDAD MEDIA"
        else:
            return "APROBADO - PRIORIDAD BAJA"

    def get_nombre(self) -> str:
        return "Scoring con Umbrales"

    def get_descripcion(self) -> str:
        return (
            "Estrategia que combina scoring ponderado con umbrales "
            "mínimos por criterio. Rechaza proyectos que no superen "
            "todos los umbrales."
        )
