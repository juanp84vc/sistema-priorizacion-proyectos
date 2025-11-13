"""
Criterio de Capacidad Organizacional.
SRP: Solo evalúa la capacidad de la organización para ejecutar el proyecto.
"""
from criterios.base import CriterioEvaluacion
from models.proyecto import ProyectoSocial


class CapacidadOrganizacionalCriterio(CriterioEvaluacion):
    """
    Evalúa la capacidad organizacional para ejecutar el proyecto.

    Considera:
    - Experiencia de la organización
    - Calidad del equipo
    - Proyectos exitosos previos
    - Capacidad de gestión
    """

    def __init__(self, peso: float = 0.1):
        super().__init__(peso)

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa capacidad organizacional.

        Componentes:
        - Experiencia (40%)
        - Equipo calificado (30%)
        - Trayectoria (30%)
        """
        score = 0

        # 1. Experiencia de la organización (40 puntos)
        años_experiencia = proyecto.indicadores_impacto.get('años_experiencia', 0)
        score_experiencia = min((años_experiencia / 10) * 40, 40)  # Máx 10 años
        score += score_experiencia

        # 2. Equipo calificado (30 puntos)
        # Asumiendo un score 0-1 que representa % de equipo con calificaciones
        equipo_score = proyecto.indicadores_impacto.get('equipo_calificado', 0)
        score_equipo = equipo_score * 30
        score += score_equipo

        # 3. Proyectos exitosos previos (30 puntos)
        proyectos_exitosos = proyecto.indicadores_impacto.get('proyectos_exitosos', 0)
        score_trayectoria = min((proyectos_exitosos / 5) * 30, 30)  # Máx 5 proyectos
        score += score_trayectoria

        return score

    def get_nombre(self) -> str:
        return "Capacidad Organizacional"

    def get_descripcion(self) -> str:
        return (
            "Evalúa la experiencia, equipo y trayectoria de la organización "
            "para ejecutar exitosamente el proyecto."
        )
