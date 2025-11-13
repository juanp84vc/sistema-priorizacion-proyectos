"""
Criterio de Sostenibilidad Financiera.
SRP: Solo evalúa sostenibilidad financiera.
"""
from criterios.base import CriterioEvaluacion
from models.proyecto import ProyectoSocial


class SostenibilidadFinancieraCriterio(CriterioEvaluacion):
    """
    Evalúa la sostenibilidad financiera del proyecto.

    Considera:
    - Diversificación de fuentes de financiamiento
    - Modelo de ingresos propios
    - Eficiencia en uso de recursos
    """

    def __init__(self, peso: float = 0.3):
        super().__init__(peso)

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa sostenibilidad financiera.

        Componentes:
        - Diversificación de fuentes (40%)
        - Ingresos propios (40%)
        - Eficiencia presupuestaria (20%)
        """
        score = 0

        # 1. Diversificación de fuentes (40 puntos)
        fuentes = proyecto.indicadores_impacto.get('fuentes_financiamiento', 1)
        score_fuentes = min((fuentes / 4) * 40, 40)  # Máx 4 fuentes = 40 pts
        score += score_fuentes

        # 2. Ingresos propios (40 puntos)
        ingresos_propios_pct = proyecto.indicadores_impacto.get('ingresos_propios_pct', 0)
        score_ingresos = (ingresos_propios_pct / 100) * 40
        score += score_ingresos

        # 3. Eficiencia presupuestaria (20 puntos)
        costo_beneficiario = proyecto.presupuesto_por_beneficiario
        # Asumiendo que menos de $500/beneficiario es eficiente
        if costo_beneficiario < 500:
            score_eficiencia = 20
        elif costo_beneficiario < 1000:
            score_eficiencia = 15
        elif costo_beneficiario < 2000:
            score_eficiencia = 10
        else:
            score_eficiencia = 5
        score += score_eficiencia

        return score

    def get_nombre(self) -> str:
        return "Sostenibilidad Financiera"

    def get_descripcion(self) -> str:
        return (
            "Evalúa la viabilidad financiera a largo plazo, "
            "diversificación de fuentes y modelo de ingresos."
        )
