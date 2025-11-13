"""
Criterio de Alineación con ODS.
SRP: Solo evalúa alineación con Objetivos de Desarrollo Sostenible.
"""
from typing import List
from criterios.base import CriterioEvaluacion
from models.proyecto import ProyectoSocial


class AlineacionODSCriterio(CriterioEvaluacion):
    """
    Evalúa alineación con Objetivos de Desarrollo Sostenible.

    OCP: Fácil agregar nuevos ODS prioritarios sin modificar código.
    """

    # ODS completos para referencia
    TODOS_LOS_ODS = [
        "ODS 1", "ODS 2", "ODS 3", "ODS 4", "ODS 5", "ODS 6",
        "ODS 7", "ODS 8", "ODS 9", "ODS 10", "ODS 11", "ODS 12",
        "ODS 13", "ODS 14", "ODS 15", "ODS 16", "ODS 17"
    ]

    def __init__(
        self,
        ods_prioritarios: List[str],
        peso: float = 0.2
    ):
        """
        Args:
            ods_prioritarios: Lista de ODS prioritarios para la organización
            peso: Peso del criterio
        """
        super().__init__(peso)
        self.ods_prioritarios = set(ods_prioritarios)

        if not self.ods_prioritarios:
            raise ValueError("Debe especificar al menos un ODS prioritario")

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa alineación con ODS.

        Metodología:
        - ODS prioritarios alineados: peso mayor
        - ODS no prioritarios: peso menor
        - Múltiples ODS: bonus por integralidad
        """
        ods_proyecto = set(proyecto.ods_vinculados)

        # ODS prioritarios que el proyecto aborda
        ods_prioritarios_alineados = ods_proyecto & self.ods_prioritarios
        num_prioritarios = len(ods_prioritarios_alineados)

        # ODS no prioritarios que el proyecto aborda
        ods_otros = ods_proyecto - self.ods_prioritarios
        num_otros = len(ods_otros)

        # Score base por alineación con prioritarios (70% del score)
        score_prioritarios = (num_prioritarios / len(self.ods_prioritarios)) * 70

        # Score adicional por otros ODS (hasta 20%)
        score_otros = min(num_otros * 5, 20)

        # Bonus por integralidad (10%)
        # Si aborda 3+ ODS, es un proyecto integral
        bonus_integralidad = 10 if len(ods_proyecto) >= 3 else 0

        score = score_prioritarios + score_otros + bonus_integralidad

        return min(score, 100)

    def get_nombre(self) -> str:
        return "Alineación ODS"

    def get_descripcion(self) -> str:
        return (
            f"Evalúa la alineación del proyecto con los ODS prioritarios: "
            f"{', '.join(sorted(self.ods_prioritarios))}"
        )
