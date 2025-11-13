"""
Criterio de Evaluación de Riesgos.
Evalúa los riesgos tecnológicos, regulatorios, financieros, sociales, etc.
asociados a la ejecución del proyecto.
"""
from criterios.base import CriterioEvaluacion
from models.proyecto import ProyectoSocial


class RiesgosCriterio(CriterioEvaluacion):
    """
    Evalúa los riesgos asociados a la ejecución del proyecto.

    Considera:
    - Riesgo financiero (presupuesto vs alcance)
    - Riesgo de sostenibilidad (duración y costo operativo)
    - Riesgo de alcance (complejidad geográfica)
    - Riesgo operativo (capacidad organizacional)

    Nota: A menor riesgo, mayor score (inverso)
    """

    def __init__(
        self,
        peso: float = 0.25,
        umbral_riesgo_alto: float = 60,
        umbral_riesgo_medio: float = 75
    ):
        """
        Args:
            peso: Peso del criterio en la evaluación total
            umbral_riesgo_alto: Score por debajo del cual se considera riesgo alto
            umbral_riesgo_medio: Score por debajo del cual se considera riesgo medio
        """
        super().__init__(peso)
        self.umbral_alto = umbral_riesgo_alto
        self.umbral_medio = umbral_riesgo_medio

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa los riesgos del proyecto.

        Metodología:
        1. Evalúa riesgo financiero (presupuesto vs beneficiarios)
        2. Evalúa riesgo de sostenibilidad temporal
        3. Evalúa riesgo de complejidad geográfica
        4. Evalúa riesgo operativo
        5. Combina riesgos en score total
        6. Invierte escala: bajo riesgo = alto score

        Returns:
            Score de 0-100 (100 = bajo riesgo, alta seguridad de éxito)
        """
        riesgo_total = 0

        # 1. Riesgo financiero (30 puntos)
        # Basado en costo por beneficiario y presupuesto total
        costo_por_beneficiario = proyecto.presupuesto_por_beneficiario
        presupuesto_total = proyecto.presupuesto_total

        # Riesgo por costo unitario alto
        if costo_por_beneficiario <= 1000:
            riesgo_financiero_unitario = 15  # Bajo riesgo
        elif costo_por_beneficiario <= 3000:
            riesgo_financiero_unitario = 10  # Riesgo moderado
        elif costo_por_beneficiario <= 5000:
            riesgo_financiero_unitario = 5   # Riesgo medio-alto
        else:
            riesgo_financiero_unitario = 2   # Alto riesgo

        # Riesgo por presupuesto total (proyectos muy grandes tienen más riesgo)
        if presupuesto_total <= 500_000_000:  # Hasta 500M
            riesgo_financiero_total = 15  # Bajo riesgo
        elif presupuesto_total <= 2_000_000_000:  # Hasta 2B
            riesgo_financiero_total = 12  # Riesgo moderado
        elif presupuesto_total <= 5_000_000_000:  # Hasta 5B
            riesgo_financiero_total = 8   # Riesgo medio
        else:
            riesgo_financiero_total = 5   # Alto riesgo

        riesgo_total += riesgo_financiero_unitario + riesgo_financiero_total

        # 2. Riesgo de sostenibilidad temporal (25 puntos)
        # Proyectos muy largos tienen mayor riesgo de cambios de contexto
        duracion_años = proyecto.duracion_años

        if duracion_años <= 1:
            riesgo_temporal = 25  # Bajo riesgo
        elif duracion_años <= 2:
            riesgo_temporal = 20  # Riesgo moderado
        elif duracion_años <= 3:
            riesgo_temporal = 15  # Riesgo medio
        else:
            riesgo_temporal = 10  # Alto riesgo (cambios de gobierno, etc.)

        riesgo_total += riesgo_temporal

        # 3. Riesgo de complejidad geográfica (25 puntos)
        # Más departamentos/municipios = mayor complejidad operativa
        num_departamentos = len(proyecto.departamentos)
        area = proyecto.area_geografica.value

        if area == "municipal":
            riesgo_geografico = 25  # Bajo riesgo (focalizado)
        elif area == "departamental" and num_departamentos == 1:
            riesgo_geografico = 20  # Riesgo moderado
        elif area == "regional" or num_departamentos <= 3:
            riesgo_geografico = 15  # Riesgo medio
        else:  # nacional o muchos departamentos
            riesgo_geografico = 10  # Alto riesgo (coordinación compleja)

        riesgo_total += riesgo_geografico

        # 4. Riesgo operativo y social (20 puntos)
        # Basado en ratio beneficiarios vs presupuesto (eficiencia)
        beneficiarios_totales = proyecto.beneficiarios_totales

        # Proyectos con muy pocos beneficiarios tienen mayor riesgo de justificación
        if beneficiarios_totales >= 5000:
            riesgo_operativo = 10  # Bajo riesgo
        elif beneficiarios_totales >= 1000:
            riesgo_operativo = 7   # Riesgo moderado
        elif beneficiarios_totales >= 500:
            riesgo_operativo = 5   # Riesgo medio
        else:
            riesgo_operativo = 3   # Alto riesgo

        # Riesgo por poblaciones difíciles de alcanzar
        poblaciones_complejas = [
            "desplazados", "víctimas", "rural dispersa", "difícil acceso",
            "conflicto", "vulnerable extrema"
        ]
        poblacion_lower = proyecto.poblacion_objetivo.lower()
        tiene_poblacion_compleja = any(pop in poblacion_lower for pop in poblaciones_complejas)

        if tiene_poblacion_compleja:
            riesgo_social = 5   # Mayor riesgo de ejecución
        else:
            riesgo_social = 10  # Menor riesgo

        riesgo_total += riesgo_operativo + riesgo_social

        # Penalizaciones adicionales por riesgos específicos

        # Riesgo regulatorio: proyectos muy complejos en alcance
        if num_departamentos >= 10 and presupuesto_total >= 5_000_000_000:
            riesgo_total *= 0.9  # 10% penalización por alta complejidad regulatoria

        # Riesgo tecnológico implícito en poblaciones rurales
        if "rural" in poblacion_lower or "dispersa" in poblacion_lower:
            riesgo_total *= 0.95  # 5% penalización por desafíos tecnológicos

        return min(max(riesgo_total, 0), 100)

    @staticmethod
    def score_a_nivel_riesgo(score: float) -> str:
        """
        Convierte un score numérico a nivel de riesgo.

        Args:
            score: Score de 0-100

        Returns:
            Nivel de riesgo como string ("bajo", "medio", "alto")
        """
        if score >= 75:
            return "bajo"
        elif score >= 60:
            return "medio"
        else:
            return "alto"

    def evaluar_con_nivel(self, proyecto: ProyectoSocial) -> tuple[float, str]:
        """
        Evalúa el proyecto y retorna tanto el score como el nivel de riesgo.

        Returns:
            Tupla (score, nivel) donde nivel es "bajo", "medio" o "alto"
        """
        score = self.evaluar(proyecto)
        nivel = self.score_a_nivel_riesgo(score)
        return score, nivel

    def get_nombre(self) -> str:
        return "Evaluación de Riesgos"

    def get_descripcion(self) -> str:
        return (
            "Evalúa los riesgos tecnológicos, regulatorios, financieros, sociales "
            "y operativos asociados a la ejecución del proyecto. Considera "
            "complejidad presupuestaria, duración, alcance geográfico y "
            "características de la población objetivo. Score alto = bajo riesgo."
        )

    def get_detalles_evaluacion(self, proyecto: ProyectoSocial) -> dict:
        """
        Retorna detalles de la evaluación para debugging y análisis.

        Returns:
            Diccionario con métricas clave
        """
        score, nivel_riesgo = self.evaluar_con_nivel(proyecto)

        poblaciones_complejas = [
            "desplazados", "víctimas", "rural dispersa", "difícil acceso",
            "conflicto", "vulnerable extrema"
        ]
        poblacion_lower = proyecto.poblacion_objetivo.lower()
        tiene_poblacion_compleja = any(pop in poblacion_lower for pop in poblaciones_complejas)

        # Identificar riesgos específicos
        riesgos_identificados = []

        if proyecto.presupuesto_total > 5_000_000_000:
            riesgos_identificados.append("Financiero: Presupuesto muy alto")

        if proyecto.duracion_años > 3:
            riesgos_identificados.append("Temporal: Duración extendida")

        if len(proyecto.departamentos) >= 5:
            riesgos_identificados.append("Geográfico: Múltiples departamentos")

        if proyecto.beneficiarios_totales < 500:
            riesgos_identificados.append("Operativo: Pocos beneficiarios")

        if tiene_poblacion_compleja:
            riesgos_identificados.append("Social: Población de difícil acceso")

        if proyecto.costo_por_beneficiario > 5000:
            riesgos_identificados.append("Financiero: Alto costo unitario")

        return {
            'nivel_riesgo': nivel_riesgo,
            'score_seguridad': score,
            'costo_por_beneficiario': proyecto.presupuesto_por_beneficiario,
            'presupuesto_total': proyecto.presupuesto_total,
            'duracion_años': proyecto.duracion_años,
            'num_departamentos': len(proyecto.departamentos),
            'area_geografica': proyecto.area_geografica.value,
            'beneficiarios_totales': proyecto.beneficiarios_totales,
            'poblacion_objetivo': proyecto.poblacion_objetivo,
            'tiene_poblacion_compleja': tiene_poblacion_compleja,
            'riesgos_identificados': riesgos_identificados if riesgos_identificados else ["Ninguno crítico"],
            'recomendacion': 'Aprobación segura' if score >= 75 else
                           'Requiere análisis adicional' if score >= 60 else
                           'Requiere mitigación de riesgos'
        }
