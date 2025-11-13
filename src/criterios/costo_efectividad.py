"""
Criterio de Relación Costo-Efectividad.
Evalúa la relación cuantitativa entre los beneficios obtenidos y su costo unitario.
"""
from criterios.base import CriterioEvaluacion
from models.proyecto import ProyectoSocial


class CostoEfectividadCriterio(CriterioEvaluacion):
    """
    Evalúa la relación costo-efectividad del proyecto.

    Considera:
    - Costo por beneficiario
    - Eficiencia en uso de recursos
    - Relación beneficio/inversión
    """

    def __init__(
        self,
        peso: float = 0.25,
        costo_optimo_por_beneficiario: float = 500.0,
        costo_maximo_aceptable: float = 5000.0
    ):
        """
        Args:
            peso: Peso del criterio en la evaluación total
            costo_optimo_por_beneficiario: Costo ideal por beneficiario (menor es mejor)
            costo_maximo_aceptable: Costo máximo aceptable por beneficiario
        """
        super().__init__(peso)
        self.costo_optimo = costo_optimo_por_beneficiario
        self.costo_maximo = costo_maximo_aceptable

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa la costo-efectividad del proyecto.

        Metodología:
        1. Calcula costo por beneficiario
        2. Evalúa eficiencia temporal (costo anualizado)
        3. Aplica escala inversa (menor costo = mayor puntaje)
        4. Normaliza a escala 0-100

        Returns:
            Score de 0-100 (100 = máxima costo-efectividad)
        """
        if proyecto.beneficiarios_totales == 0:
            return 0

        # Costo por beneficiario
        costo_por_beneficiario = proyecto.presupuesto_por_beneficiario

        # Si el costo está por encima del máximo aceptable, score muy bajo
        if costo_por_beneficiario >= self.costo_maximo:
            return 10  # Puntaje mínimo para proyectos muy costosos

        # Calcular score inverso (menor costo = mayor score)
        # Fórmula: score = 100 * (1 - (costo - optimo) / (maximo - optimo))
        if costo_por_beneficiario <= self.costo_optimo:
            score = 100  # Costo óptimo o mejor
        else:
            # Escala lineal decreciente del costo óptimo al máximo
            rango = self.costo_maximo - self.costo_optimo
            exceso = costo_por_beneficiario - self.costo_optimo
            score = 100 * (1 - (exceso / rango))

        # Bonus por eficiencia temporal: proyectos más cortos son más eficientes
        if proyecto.duracion_años <= 1:
            score *= 1.1  # 10% bonus para proyectos de 1 año o menos
        elif proyecto.duracion_años > 3:
            score *= 0.95  # 5% penalización para proyectos muy largos

        # Bonus por bajo costo operativo relativo
        # (Si el presupuesto total es bajo pero llega a muchos beneficiarios)
        beneficiarios_por_millon = proyecto.beneficiarios_totales / (proyecto.presupuesto_total / 1_000_000)
        if beneficiarios_por_millon > 1000:  # Más de 1000 beneficiarios por millón de pesos
            score *= 1.05  # 5% bonus por alta eficiencia

        return min(max(score, 0), 100)

    def get_nombre(self) -> str:
        return "Relación Costo-Efectividad"

    def get_descripcion(self) -> str:
        return (
            "Evalúa la relación cuantitativa entre los beneficios obtenidos "
            "y su costo unitario. Prioriza proyectos con mayor impacto por "
            "peso invertido, considerando eficiencia temporal y operativa."
        )

    def get_detalles_evaluacion(self, proyecto: ProyectoSocial) -> dict:
        """
        Retorna detalles de la evaluación para debugging y análisis.

        Returns:
            Diccionario con métricas clave
        """
        return {
            'costo_por_beneficiario': proyecto.presupuesto_por_beneficiario,
            'costo_optimo_referencia': self.costo_optimo,
            'costo_maximo_referencia': self.costo_maximo,
            'beneficiarios_totales': proyecto.beneficiarios_totales,
            'presupuesto_total': proyecto.presupuesto_total,
            'duracion_años': proyecto.duracion_años,
            'eficiencia': 'Alta' if proyecto.presupuesto_por_beneficiario <= self.costo_optimo else
                         'Media' if proyecto.presupuesto_por_beneficiario <= self.costo_optimo * 2 else
                         'Baja'
        }
