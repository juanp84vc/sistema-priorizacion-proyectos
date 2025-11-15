"""
Criterio de Probabilidad de Aprobación con integración PDET/ZOMAC.

Evalúa la probabilidad de aprobación en Obras por Impuestos basándose
ÚNICAMENTE en la priorización sectorial oficial PDET/ZOMAC.

Obras por Impuestos es un mecanismo EXCLUSIVO para los 362 municipios
PDET/ZOMAC. Municipios fuera de esta lista no pueden acceder al mecanismo.

Versión actualizada con matriz oficial de 362 municipios.
"""
from enum import Enum
from typing import List, Optional
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from criterios.base import CriterioEvaluacion
from models.proyecto import ProyectoSocial
from database.matriz_pdet_repository import MatrizPDETRepository


class NivelProbabilidad(Enum):
    """Niveles de probabilidad de aprobación."""
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"


class ProbabilidadAprobacionCriterio(CriterioEvaluacion):
    """
    Evalúa probabilidad de aprobación en mecanismo Obras por Impuestos
    basándose en la matriz oficial de priorización sectorial PDET/ZOMAC.

    Criterio: 20% del score total (Arquitectura C)

    Metodología:
    - Usa matriz oficial de 362 municipios PDET/ZOMAC
    - 10 sectores priorizados con puntajes 1-10
    - Score = (puntaje_max_sectorial / 10) × 100
    - Proyectos NO-PDET obtienen 0 (no aplican a este mecanismo)

    Nota: ODS vinculados y población objetivo se guardan como metadata
    descriptiva en el proyecto pero NO influyen en el scoring de este criterio
    específico de Obras por Impuestos.
    """

    def __init__(
        self,
        peso: float = 0.20,
        probabilidad_manual: NivelProbabilidad = None,
        db_path: str = "data/proyectos.db"
    ):
        """
        Inicializa criterio.

        Args:
            peso: Peso del criterio en evaluación total (recomendado: 0.20)
            probabilidad_manual: Probabilidad asignada manualmente (opcional)
            db_path: Ruta a base de datos con matriz PDET
        """
        super().__init__(peso)
        self.probabilidad_manual = probabilidad_manual

        # Conectar a repositorio matriz PDET
        try:
            self.matriz_repo = MatrizPDETRepository(db_path)
        except Exception as e:
            print(f"⚠️  Advertencia: No se pudo cargar matriz PDET: {e}")
            print(f"   El criterio funcionará sin datos PDET (score neutro)")
            self.matriz_repo = None

    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa probabilidad de aprobación basándose ÚNICAMENTE en
        prioridad sectorial oficial de Obras por Impuestos PDET/ZOMAC.

        El mecanismo Obras por Impuestos es EXCLUSIVO para municipios PDET/ZOMAC.
        La aprobación se basa en los puntajes sectoriales oficiales (1-10).

        ODS y población objetivo se guardan como metadata pero NO influyen
        en el scoring de este criterio específico.

        Returns:
            Score de 0-100 basado en prioridad sectorial oficial:
            - Puntaje 10/10 → 100/100 (máxima prioridad)
            - Puntaje 5/10 → 50/100 (media prioridad)
            - Puntaje 1/10 → 10/100 (baja prioridad)
            - NO-PDET → 0/100 (no aplica al mecanismo)
        """
        # Si hay probabilidad manual, usarla directamente
        if self.probabilidad_manual:
            return self._probabilidad_a_score(self.probabilidad_manual)

        # ÚNICO COMPONENTE: Prioridad sectorial PDET/ZOMAC (100%)
        score = self._evaluar_prioridad_sectorial_pdet(proyecto)

        return min(max(score, 0), 100)

    def _evaluar_prioridad_sectorial_pdet(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa prioridad sectorial usando matriz oficial PDET/ZOMAC.

        Lógica:
        1. Identifica municipios PDET del proyecto
        2. Para cada municipio, obtiene puntajes de sectores del proyecto
        3. Usa el puntaje MÁXIMO (favorece mejor oportunidad)
        4. Convierte puntaje 1-10 a score 0-100

        Returns:
            Score 0-100 basado en priorización sectorial oficial
            0 si el proyecto no está en municipios PDET/ZOMAC
        """
        if self.matriz_repo is None:
            # Sin matriz PDET → No se puede evaluar, retornar 0
            return 0.0

        if not proyecto.municipios or not proyecto.sectores:
            # Sin datos suficientes → No se puede evaluar
            return 0.0

        puntajes_encontrados = []

        # Evaluar cada combinación municipio-sector
        for municipio_nombre in proyecto.municipios:
            # Buscar departamento del municipio
            departamento = self._get_departamento_municipio(
                municipio_nombre,
                proyecto.departamentos
            )

            if not departamento:
                continue

            # Obtener registro PDET del municipio
            registro = self.matriz_repo.get_municipio(departamento, municipio_nombre)

            if not registro:
                # Municipio no es PDET/ZOMAC → No suma puntaje
                continue

            # Obtener puntajes de cada sector del proyecto
            for sector in proyecto.sectores:
                puntaje = registro.get_puntaje_sector(sector)
                if puntaje > 0:
                    puntajes_encontrados.append({
                        'municipio': municipio_nombre,
                        'departamento': departamento,
                        'sector': sector,
                        'puntaje': puntaje
                    })

        if not puntajes_encontrados:
            # Ningún municipio es PDET/ZOMAC
            # → Score 0 (no puede usar mecanismo Obras por Impuestos)
            proyecto.tiene_municipios_pdet = False
            return 0.0

        # Usar puntaje MÁXIMO (favorece mejor oportunidad)
        mejor_match = max(puntajes_encontrados, key=lambda x: x['puntaje'])
        puntaje_max = mejor_match['puntaje']

        # Convertir puntaje 1-10 a score 0-100
        # Puntaje 10 → 100 pts (máxima prioridad)
        # Puntaje 5 → 50 pts (media)
        # Puntaje 1 → 10 pts (baja prioridad)
        score = (puntaje_max / 10) * 100

        # Guardar metadata en proyecto
        proyecto.tiene_municipios_pdet = True
        proyecto.puntaje_sectorial_max = puntaje_max

        # Guardar todos los puntajes por sector
        puntajes_por_sector = {}
        for match in puntajes_encontrados:
            sector = match['sector']
            if sector not in puntajes_por_sector or match['puntaje'] > puntajes_por_sector[sector]:
                puntajes_por_sector[sector] = match['puntaje']

        proyecto.puntajes_pdet = puntajes_por_sector

        return score

    def _get_departamento_municipio(
        self,
        municipio: str,
        departamentos: List[str]
    ) -> Optional[str]:
        """
        Identifica departamento de un municipio.

        Args:
            municipio: Nombre del municipio
            departamentos: Lista de departamentos del proyecto

        Returns:
            Nombre del departamento o None
        """
        # Estrategia simple: usar primer departamento
        # TODO: Mejorar con validación cruzada en FASE 3
        if not departamentos:
            return None

        # Si hay múltiples departamentos, intentar encontrar el correcto
        if len(departamentos) == 1:
            return departamentos[0]

        # Buscar en cada departamento
        for depto in departamentos:
            if self.matriz_repo and self.matriz_repo.es_municipio_pdet(depto, municipio):
                return depto

        # Si no encontró, usar primero
        return departamentos[0]

    def _evaluar_ods(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa ODS vinculados.

        ODS prioritarios en Colombia: 1, 2, 3, 4, 5, 8, 10, 16

        Returns:
            Score 0-100 basado en alineación con ODS
        """
        ods_prioritarios = ["1", "2", "3", "4", "5", "8", "10", "16"]
        num_ods_prioritarios = len([
            ods for ods in proyecto.ods_vinculados
            if ods in ods_prioritarios
        ])

        if num_ods_prioritarios >= 3:
            return 100  # Altamente alineado
        elif num_ods_prioritarios >= 2:
            return 75  # Bien alineado
        elif num_ods_prioritarios >= 1:
            return 50  # Parcialmente alineado
        else:
            return 25  # Baja alineación

    def _evaluar_poblacion_prioritaria(self, proyecto: ProyectoSocial) -> float:
        """
        Evalúa población objetivo prioritaria.

        Poblaciones prioritarias gobierno:
        - Niños/niñas/adolescentes
        - Mujeres
        - Adultos mayores
        - Personas con discapacidad
        - Víctimas del conflicto
        - Comunidades étnicas (indígenas, afrocolombianos)
        - Población vulnerable

        Returns:
            Score 0-100 basado en población objetivo
        """
        poblaciones_prioritarias = [
            "niños", "niñas", "infancia", "adolescentes", "mujeres",
            "adultos mayores", "discapacidad", "desplazados",
            "víctimas", "indígenas", "afrocolombianos", "vulnerable"
        ]

        poblacion_lower = proyecto.poblacion_objetivo.lower()
        tiene_prioritaria = any(pop in poblacion_lower for pop in poblaciones_prioritarias)

        return 100 if tiene_prioritaria else 40

    def _probabilidad_a_score(self, probabilidad: NivelProbabilidad) -> float:
        """
        Convierte nivel de probabilidad manual a score numérico.

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
        Convierte score numérico a nivel de probabilidad.

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

    def evaluar_con_nivel(self, proyecto: ProyectoSocial) -> tuple:
        """
        Evalúa el proyecto y retorna score + nivel de probabilidad.

        Returns:
            Tupla (score, nivel) donde nivel es "alta", "media" o "baja"
        """
        score = self.evaluar(proyecto)
        nivel = self.score_a_probabilidad(score)
        return score, nivel

    def get_nombre(self) -> str:
        return "Probabilidad de Aprobación (PDET/ZOMAC)"

    def get_descripcion(self) -> str:
        return (
            "Evalúa la probabilidad de aprobación en Obras por Impuestos usando "
            "datos oficiales de priorización sectorial PDET/ZOMAC para 362 municipios. "
            "Score basado 100% en puntajes sectoriales oficiales (1-10). "
            "Municipios NO-PDET obtienen score 0 (mecanismo exclusivo PDET/ZOMAC)."
        )

    def get_detalles_evaluacion(self, proyecto: ProyectoSocial) -> dict:
        """
        Retorna detalles de la evaluación para debugging y análisis.

        Returns:
            Diccionario con métricas clave
        """
        score, nivel = self.evaluar_con_nivel(proyecto)

        # Calcular componente único
        score_pdet = self._evaluar_prioridad_sectorial_pdet(proyecto)

        detalles = {
            'probabilidad_nivel': nivel,
            'score_total': score,
            'componentes': {
                'prioridad_sectorial_pdet': {
                    'score': score_pdet,
                    'peso': 1.00,  # 100% del criterio
                    'ponderado': score_pdet * 1.00
                }
            },
            'municipios_pdet': proyecto.tiene_municipios_pdet,
            'puntaje_sectorial_max': proyecto.puntaje_sectorial_max,
            'puntajes_por_sector': proyecto.puntajes_pdet,
            'sectores_proyecto': proyecto.sectores,
            'municipios_proyecto': proyecto.municipios,
            # Metadata descriptiva (NO afecta scoring)
            'metadata': {
                'ods_vinculados': proyecto.ods_vinculados,
                'poblacion_objetivo': proyecto.poblacion_objetivo
            }
        }

        return detalles
