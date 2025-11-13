"""
Criterio de Contribución al Relacionamiento con Stakeholders.
Evalúa la contribución del proyecto al relacionamiento con stakeholders locales
y a la viabilidad de las operaciones y proyectos de GEB.
"""
from criterios.base import CriterioEvaluacion
from models.proyecto import ProyectoSocial


class ContribucionStakeholdersCriterio(CriterioEvaluacion):
    """
    Evalúa la contribución del proyecto al relacionamiento con stakeholders
    locales y a la viabilidad de las operaciones.

    Considera:
    - Nivel de involucramiento de comunidades locales
    - Fortalecimiento de relaciones institucionales
    - Apoyo a viabilidad operativa de proyectos de GEB
    - Cobertura geográfica estratégica
    """

    def __init__(
        self,
        peso: float = 0.25,
        bonus_area_nacional: float = 1.15,
        bonus_multiples_departamentos: float = 1.1
    ):
        """
        Args:
            peso: Peso del criterio en la evaluación total
            bonus_area_nacional: Multiplicador para proyectos de alcance nacional
            bonus_multiples_departamentos: Multiplicador para proyectos multi-departamentales
        """
        super().__init__(peso)
        self.bonus_nacional = bonus_area_nacional
        self.bonus_multi_depto = bonus_multiples_departamentos

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa la contribución a stakeholders del proyecto.

        Metodología:
        1. Score base por alcance geográfico (nacional > regional > local)
        2. Bonus por múltiples departamentos (mayor relacionamiento)
        3. Bonus por alta cobertura de beneficiarios
        4. Evaluación de sostenibilidad como proxy de viabilidad
        5. Normaliza a escala 0-100

        Returns:
            Score de 0-100 (100 = máxima contribución a stakeholders)
        """
        score = 0

        # 1. Score base según área geográfica (40 puntos)
        if proyecto.area_geografica.value == "nacional":
            score += 40  # Máximo impacto en relacionamiento
        elif proyecto.area_geografica.value == "regional":
            score += 30  # Alto impacto regional
        elif proyecto.area_geografica.value == "departamental":
            score += 25  # Buen impacto departamental
        else:  # municipal
            score += 20  # Impacto local focalizado

        # 2. Bonus por múltiples departamentos (20 puntos)
        num_departamentos = len(proyecto.departamentos)
        if num_departamentos >= 5:
            score += 20  # Múltiples stakeholders departamentales
        elif num_departamentos >= 3:
            score += 15
        elif num_departamentos >= 2:
            score += 10
        else:
            score += 5

        # 3. Evaluación por cobertura de beneficiarios (20 puntos)
        # Más beneficiarios = mayor relacionamiento con comunidades
        total_beneficiarios = proyecto.beneficiarios_totales
        if total_beneficiarios >= 10000:
            score += 20  # Amplia cobertura comunitaria
        elif total_beneficiarios >= 5000:
            score += 15
        elif total_beneficiarios >= 1000:
            score += 10
        else:
            score += 5

        # 4. Viabilidad operativa basada en sostenibilidad (20 puntos)
        # Proyectos con buena planificación financiera apoyan viabilidad
        costo_por_beneficiario = proyecto.presupuesto_por_beneficiario
        if costo_por_beneficiario <= 1000:  # Eficiente
            score += 20
        elif costo_por_beneficiario <= 3000:  # Razonable
            score += 15
        elif costo_por_beneficiario <= 5000:  # Aceptable
            score += 10
        else:  # Alto riesgo de viabilidad
            score += 5

        # Bonus por alcance nacional o multi-departamental
        if proyecto.area_geografica.value == "nacional":
            score *= self.bonus_nacional
        elif num_departamentos >= 3:
            score *= self.bonus_multi_depto

        # Bonus adicional por proyectos con poblaciones objetivo vulnerables
        # (mayor impacto en relacionamiento social)
        poblaciones_prioritarias = [
            "niños", "mujeres", "adultos mayores", "discapacidad",
            "desplazados", "víctimas", "indígenas", "afrocolombianos"
        ]
        poblacion_lower = proyecto.poblacion_objetivo.lower()
        if any(pop in poblacion_lower for pop in poblaciones_prioritarias):
            score *= 1.05  # 5% bonus por población vulnerable

        return min(max(score, 0), 100)

    def get_nombre(self) -> str:
        return "Contribución al Relacionamiento con Stakeholders"

    def get_descripcion(self) -> str:
        return (
            "Evalúa la contribución del proyecto al relacionamiento con stakeholders "
            "locales (comunidades, autoridades, instituciones) y a la viabilidad de "
            "las operaciones y proyectos de GEB. Considera alcance geográfico, "
            "cobertura de beneficiarios y sostenibilidad operativa."
        )

    def get_detalles_evaluacion(self, proyecto: ProyectoSocial) -> dict:
        """
        Retorna detalles de la evaluación para debugging y análisis.

        Returns:
            Diccionario con métricas clave
        """
        poblaciones_prioritarias = [
            "niños", "mujeres", "adultos mayores", "discapacidad",
            "desplazados", "víctimas", "indígenas", "afrocolombianos"
        ]
        poblacion_lower = proyecto.poblacion_objetivo.lower()
        tiene_poblacion_vulnerable = any(pop in poblacion_lower for pop in poblaciones_prioritarias)

        return {
            'area_geografica': proyecto.area_geografica.value,
            'num_departamentos': len(proyecto.departamentos),
            'departamentos': proyecto.departamentos,
            'beneficiarios_totales': proyecto.beneficiarios_totales,
            'costo_por_beneficiario': proyecto.presupuesto_por_beneficiario,
            'poblacion_objetivo': proyecto.poblacion_objetivo,
            'tiene_poblacion_vulnerable': tiene_poblacion_vulnerable,
            'nivel_relacionamiento': 'Alto' if len(proyecto.departamentos) >= 3 else
                                   'Medio' if len(proyecto.departamentos) >= 2 else
                                   'Básico'
        }
