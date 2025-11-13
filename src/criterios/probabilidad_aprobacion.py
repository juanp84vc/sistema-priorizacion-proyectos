"""
Criterio de Probabilidad de Aprobación.
Evalúa la probabilidad de que el proyecto sea aprobado por parte del
Gobierno Nacional, distrital o local.
"""
from enum import Enum
from criterios.base import CriterioEvaluacion
from models.proyecto import ProyectoSocial


class NivelProbabilidad(Enum):
    """Niveles de probabilidad de aprobación."""
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class ProbabilidadAprobacionCriterio(CriterioEvaluacion):
    """
    Evalúa la probabilidad de aprobación del proyecto por parte de entidades
    gubernamentales (Nacional, distrital o local).

    Considera:
    - Alineación con prioridades gubernamentales (ODS)
    - Viabilidad presupuestaria
    - Impacto en población objetivo prioritaria
    - Alcance geográfico estratégico
    """

    def __init__(
        self,
        peso: float = 0.25,
        probabilidad_manual: NivelProbabilidad = None
    ):
        """
        Args:
            peso: Peso del criterio en la evaluación total
            probabilidad_manual: Probabilidad asignada manualmente (opcional)
                               Si se proporciona, se usa este valor directamente
        """
        super().__init__(peso)
        self.probabilidad_manual = probabilidad_manual

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa la probabilidad de aprobación del proyecto.

        Metodología:
        1. Si hay probabilidad manual asignada, la usa directamente
        2. Si no, calcula probabilidad basada en:
           - Alineación con ODS prioritarios del gobierno
           - Viabilidad presupuestaria (costo razonable)
           - Población objetivo vulnerable (prioridad social)
           - Alcance geográfico (mayor alcance = mayor interés)
        3. Convierte probabilidad a score 0-100

        Returns:
            Score de 0-100 (100 = alta probabilidad de aprobación)
        """
        # Si hay probabilidad manual, usarla directamente
        if self.probabilidad_manual:
            return self._probabilidad_a_score(self.probabilidad_manual)

        # Calcular probabilidad automática basada en características del proyecto
        score = 0

        # 1. Alineación con ODS prioritarios del gobierno (30 puntos)
        # ODS prioritarios en Colombia: 1, 2, 3, 4, 5, 8, 10, 16
        ods_prioritarios = ["1", "2", "3", "4", "5", "8", "10", "16"]
        num_ods_prioritarios = len([ods for ods in proyecto.ods_vinculados if ods in ods_prioritarios])

        if num_ods_prioritarios >= 3:
            score += 30  # Altamente alineado
        elif num_ods_prioritarios >= 2:
            score += 20  # Bien alineado
        elif num_ods_prioritarios >= 1:
            score += 10  # Parcialmente alineado
        else:
            score += 5   # Baja alineación

        # 2. Viabilidad presupuestaria (25 puntos)
        costo_por_beneficiario = proyecto.presupuesto_por_beneficiario

        if costo_por_beneficiario <= 1000:
            score += 25  # Muy viable
        elif costo_por_beneficiario <= 3000:
            score += 20  # Viable
        elif costo_por_beneficiario <= 5000:
            score += 15  # Moderadamente viable
        else:
            score += 5   # Desafiante viabilidad

        # 3. Población objetivo prioritaria (25 puntos)
        poblaciones_prioritarias = [
            "niños", "niñas", "infancia", "adolescentes", "mujeres",
            "adultos mayores", "discapacidad", "desplazados",
            "víctimas", "indígenas", "afrocolombianos", "vulnerable"
        ]
        poblacion_lower = proyecto.poblacion_objetivo.lower()
        tiene_poblacion_prioritaria = any(pop in poblacion_lower for pop in poblaciones_prioritarias)

        if tiene_poblacion_prioritaria:
            score += 25  # Alta prioridad gubernamental
        else:
            score += 10  # Prioridad estándar

        # 4. Alcance geográfico (20 puntos)
        if proyecto.area_geografica.value == "nacional":
            score += 20  # Interés nacional
        elif proyecto.area_geografica.value == "regional":
            score += 15  # Interés regional
        elif proyecto.area_geografica.value == "departamental":
            score += 12  # Interés departamental
        else:  # municipal
            score += 8   # Interés local

        # Bonus por proyectos de larga duración (mayor compromiso)
        if proyecto.duracion_años >= 3:
            score *= 0.95  # 5% penalización por mayor compromiso requerido

        # Bonus por proyectos que lleguen a muchos beneficiarios
        if proyecto.beneficiarios_totales >= 5000:
            score *= 1.1  # 10% bonus por alto impacto

        # INTEGRACIÓN DE CAMPOS CUALITATIVOS
        # Ajuste por Alineación con Sectores Prioritarios ZOMAC/PDET
        sectores = proyecto.indicadores_impacto.get('sectores_zomac', 'Top 4 sectores ZOMAC/PDET')
        if sectores == 'Top 2 sectores prioritarios ZOMAC/PDET':
            score *= 1.30  # 30% bonus por máxima prioridad (Top 2)
        elif sectores == 'Top 3 sectores ZOMAC/PDET':
            score *= 1.25  # 25% bonus por alta prioridad (Top 3)
        elif sectores == 'Top 4 sectores ZOMAC/PDET':
            score *= 1.20  # 20% bonus por prioridad (Top 4)
        elif sectores == 'Requiere esfuerzos de alineación':
            score *= 0.95  # 5% penalización por necesitar alineación
        elif sectores == 'No ZOMAC/PDET o no se alinea':
            score *= 0.85  # 15% penalización por no alineación

        return min(max(score, 0), 100)

    def _probabilidad_a_score(self, probabilidad: NivelProbabilidad) -> float:
        """
        Convierte un nivel de probabilidad a score numérico.

        Args:
            probabilidad: Nivel de probabilidad (alta, media, baja)

        Returns:
            Score de 0-100
        """
        if probabilidad == NivelProbabilidad.ALTA:
            return 100
        elif probabilidad == NivelProbabilidad.MEDIA:
            return 60
        else:  # BAJA
            return 30

    @staticmethod
    def score_a_probabilidad(score: float) -> str:
        """
        Convierte un score numérico a nivel de probabilidad.

        Args:
            score: Score de 0-100

        Returns:
            Nivel de probabilidad como string ("alta", "media", "baja")
        """
        if score >= 75:
            return "alta"
        elif score >= 45:
            return "media"
        else:
            return "baja"

    def evaluar_con_nivel(self, proyecto: ProyectoSocial) -> tuple[float, str]:
        """
        Evalúa el proyecto y retorna tanto el score como el nivel de probabilidad.

        Returns:
            Tupla (score, nivel) donde nivel es "alta", "media" o "baja"
        """
        score = self.evaluar(proyecto)
        nivel = self.score_a_probabilidad(score)
        return score, nivel

    def get_nombre(self) -> str:
        return "Probabilidad de Aprobación Gubernamental"

    def get_descripcion(self) -> str:
        return (
            "Evalúa la probabilidad de que el proyecto sea aprobado por parte del "
            "Gobierno Nacional, distrital o local. Considera alineación con "
            "prioridades gubernamentales (ODS), viabilidad presupuestaria, "
            "población objetivo prioritaria y alcance geográfico. "
            "Niveles: alta, media, baja."
        )

    def get_detalles_evaluacion(self, proyecto: ProyectoSocial) -> dict:
        """
        Retorna detalles de la evaluación para debugging y análisis.

        Returns:
            Diccionario con métricas clave
        """
        score, nivel = self.evaluar_con_nivel(proyecto)

        ods_prioritarios = ["1", "2", "3", "4", "5", "8", "10", "16"]
        num_ods_prioritarios = len([ods for ods in proyecto.ods_vinculados if ods in ods_prioritarios])

        poblaciones_prioritarias = [
            "niños", "niñas", "infancia", "adolescentes", "mujeres",
            "adultos mayores", "discapacidad", "desplazados",
            "víctimas", "indígenas", "afrocolombianos", "vulnerable"
        ]
        poblacion_lower = proyecto.poblacion_objetivo.lower()
        tiene_poblacion_prioritaria = any(pop in poblacion_lower for pop in poblaciones_prioritarias)

        return {
            'probabilidad_nivel': nivel,
            'score_numerico': score,
            'ods_vinculados': proyecto.ods_vinculados,
            'num_ods_prioritarios': num_ods_prioritarios,
            'costo_por_beneficiario': proyecto.presupuesto_por_beneficiario,
            'poblacion_objetivo': proyecto.poblacion_objetivo,
            'tiene_poblacion_prioritaria': tiene_poblacion_prioritaria,
            'area_geografica': proyecto.area_geografica.value,
            'beneficiarios_totales': proyecto.beneficiarios_totales,
            'duracion_años': proyecto.duracion_años
        }
