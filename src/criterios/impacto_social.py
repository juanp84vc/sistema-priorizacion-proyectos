"""
Criterio de Impacto Social.
SRP: Solo evalúa impacto social, nada más.
"""
from criterios.base import CriterioEvaluacion
from models.proyecto import ProyectoSocial, AreaGeografica


class ImpactoSocialCriterio(CriterioEvaluacion):
    """
    Evalúa el impacto social del proyecto.

    Considera:
    - Número de beneficiarios
    - Tipo de área geográfica
    - Alcance (directo vs indirecto)
    """

    def __init__(
        self,
        peso: float = 0.4,
        beneficiarios_objetivo: int = 1000,
        multiplicador_rural: float = 1.2
    ):
        """
        Args:
            peso: Peso del criterio
            beneficiarios_objetivo: Número objetivo de beneficiarios
            multiplicador_rural: Factor multiplicador para áreas rurales
        """
        super().__init__(peso)
        self.beneficiarios_objetivo = beneficiarios_objetivo
        self.multiplicador_rural = multiplicador_rural

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa impacto social del proyecto.

        Metodología:
        1. Calcula beneficiarios anualizados
        2. Aplica multiplicador geográfico
        3. Normaliza a escala 0-100
        """
        # Beneficiarios anualizados
        beneficiarios_anuales = (
            proyecto.beneficiarios_totales / proyecto.duracion_años
        )

        # Aplicar multiplicador geográfico
        if proyecto.area_geografica == AreaGeografica.RURAL:
            beneficiarios_anuales *= self.multiplicador_rural

        # Normalizar
        score = self._normalizar_score(
            beneficiarios_anuales,
            self.beneficiarios_objetivo
        )

        # Bonus por alcance indirecto significativo
        ratio_indirectos = (
            proyecto.beneficiarios_indirectos / proyecto.beneficiarios_totales
            if proyecto.beneficiarios_totales > 0 else 0
        )

        if ratio_indirectos > 0.5:  # Más del 50% indirectos
            score *= 1.1  # 10% bonus

        return min(score, 100)

    def get_nombre(self) -> str:
        return "Impacto Social"

    def get_descripcion(self) -> str:
        return (
            "Evalúa el alcance y profundidad del impacto social, "
            "considerando beneficiarios directos e indirectos, "
            "área geográfica y duración del proyecto."
        )
