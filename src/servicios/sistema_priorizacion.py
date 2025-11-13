"""
Sistema principal de priorización de proyectos.
SRP: Orquesta evaluación, no implementa lógica de criterios.
DIP: Depende de abstracciones (CriterioEvaluacion, EstrategiaEvaluacion).
"""
from typing import List
from models.proyecto import ProyectoSocial
from models.evaluacion import ResultadoEvaluacion
from criterios.base import CriterioEvaluacion
from estrategias.base import EstrategiaEvaluacion


class SistemaPriorizacionProyectos:
    """
    Sistema principal para priorización de proyectos sociales.

    Responsabilidades:
    - Coordinar evaluación de proyectos
    - Aplicar estrategia de scoring
    - Generar ranking de proyectos

    DIP: Recibe abstracciones por inyección de dependencias.
    OCP: Extensible agregando nuevos criterios/estrategias.
    """

    def __init__(
        self,
        criterios: List[CriterioEvaluacion],
        estrategia: EstrategiaEvaluacion
    ):
        """
        Inicializa sistema con criterios y estrategia.

        Args:
            criterios: Lista de criterios a aplicar
            estrategia: Estrategia de evaluación a usar
        """
        if not criterios:
            raise ValueError("Debe proporcionar al menos un criterio")

        self.criterios = criterios
        self.estrategia = estrategia

    def evaluar_proyecto(
        self,
        proyecto: ProyectoSocial
    ) -> ResultadoEvaluacion:
        """
        Evalúa un proyecto individual.

        Args:
            proyecto: Proyecto a evaluar

        Returns:
            ResultadoEvaluacion con scores y recomendación
        """
        return self.estrategia.evaluar_proyecto(proyecto, self.criterios)

    def priorizar_cartera(
        self,
        proyectos: List[ProyectoSocial]
    ) -> List[ResultadoEvaluacion]:
        """
        Evalúa y prioriza una cartera de proyectos.

        Args:
            proyectos: Lista de proyectos a evaluar

        Returns:
            Lista de ResultadoEvaluacion ordenada por score
            (mayor a menor)
        """
        if not proyectos:
            return []

        resultados = [
            self.evaluar_proyecto(proyecto)
            for proyecto in proyectos
        ]

        # Ordenar por score final (descendente)
        resultados.sort(key=lambda r: r.score_final, reverse=True)

        return resultados

    def generar_reporte(
        self,
        proyectos: List[ProyectoSocial]
    ) -> dict:
        """
        Genera reporte completo de evaluación de cartera.

        Args:
            proyectos: Lista de proyectos a evaluar

        Returns:
            Dict con resumen estadístico y ranking
        """
        resultados = self.priorizar_cartera(proyectos)

        if not resultados:
            return {
                'total_proyectos': 0,
                'ranking': [],
                'estadisticas': {}
            }

        scores = [r.score_final for r in resultados]

        # Calcular desviación estándar
        promedio = sum(scores) / len(scores)
        varianza = sum((s - promedio) ** 2 for s in scores) / len(scores)
        desviacion_estandar = varianza ** 0.5

        return {
            'total_proyectos': len(proyectos),
            'estrategia': self.estrategia.get_nombre(),
            'criterios': [c.get_nombre() for c in self.criterios],
            'ranking': [
                {
                    'posicion': idx + 1,
                    'proyecto_id': r.proyecto_id,
                    'proyecto_nombre': r.proyecto_nombre,
                    'score': r.score_final,
                    'recomendacion': r.recomendacion
                }
                for idx, r in enumerate(resultados)
            ],
            'estadisticas': {
                'score_maximo': max(scores),
                'score_minimo': min(scores),
                'score_promedio': promedio,
                'desviacion_estandar': desviacion_estandar,
                'proyectos_alta_prioridad': sum(
                    1 for s in scores if s >= 80
                ),
                'proyectos_media_prioridad': sum(
                    1 for s in scores if 60 <= s < 80
                ),
                'proyectos_baja_prioridad': sum(
                    1 for s in scores if s < 60
                )
            }
        }

    def comparar_proyectos(
        self,
        proyecto1: ProyectoSocial,
        proyecto2: ProyectoSocial
    ) -> dict:
        """
        Compara dos proyectos en detalle.

        Args:
            proyecto1: Primer proyecto
            proyecto2: Segundo proyecto

        Returns:
            Dict con comparación detallada
        """
        resultado1 = self.evaluar_proyecto(proyecto1)
        resultado2 = self.evaluar_proyecto(proyecto2)

        return {
            'proyecto_1': {
                'id': proyecto1.id,
                'nombre': proyecto1.nombre,
                'score_final': resultado1.score_final,
                'detalle_criterios': resultado1.detalle_criterios
            },
            'proyecto_2': {
                'id': proyecto2.id,
                'nombre': proyecto2.nombre,
                'score_final': resultado2.score_final,
                'detalle_criterios': resultado2.detalle_criterios
            },
            'diferencias': {
                criterio: {
                    'proyecto_1': resultado1.detalle_criterios[criterio]['score_base'],
                    'proyecto_2': resultado2.detalle_criterios[criterio]['score_base'],
                    'diferencia': (
                        resultado1.detalle_criterios[criterio]['score_base'] -
                        resultado2.detalle_criterios[criterio]['score_base']
                    )
                }
                for criterio in resultado1.detalle_criterios.keys()
            },
            'ganador': (
                proyecto1.id
                if resultado1.score_final > resultado2.score_final
                else proyecto2.id
            )
        }
