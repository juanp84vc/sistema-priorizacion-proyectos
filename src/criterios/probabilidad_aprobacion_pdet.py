"""
Criterio de Probabilidad de Aprobación CONFIS.

Ajuste metodológico (Feb 2026):
Evalúa la probabilidad de aprobación en Obras por Impuestos basándose
en la metodología oficial CONFIS (Anexo 2 - "Metodología para la
distribución del CUPO CONFIS").

Dos ejes de evaluación:
1. Enfoque Territorial (40%): IPM + MDM_inv + IICA + CULTIVOS → promedio 1-10
2. Enfoque Sectorial (40%): Brechas sectoriales por municipio → puntaje 1-10
3. Grupo de Priorización (20%): Grupos 1-8 según tipo PATR/PDET/ZOMAC/Amazonia

Score CONFIS = Territorial + Sectorial (rango 2-20)
Score Criterio = GrupoPrioridad(20%) + ScoreCONFIS_Norm(80%)

Obras por Impuestos es un mecanismo EXCLUSIVO para los 362 municipios
PDET/ZOMAC. Municipios fuera de esta lista no pueden acceder al mecanismo.

Historial:
- Versión original: solo puntaje sectorial
- Ajuste Feb 2026: integración completa metodología CONFIS
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
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


# Grupos de priorización CONFIS (Anexo 2)
# Puntajes asignados para scoring interno ENLAZA
# Grupos impares = contribuyente paga estructuración (mayor prioridad)
GRUPOS_CONFIS = {
    1: {"nombre": "PATR-PDET + Estructuración contribuyente", "score": 100},
    2: {"nombre": "PATR-PDET sin estructuración contribuyente", "score": 90},
    3: {"nombre": "PDET + Estructuración contribuyente", "score": 80},
    4: {"nombre": "PDET sin estructuración contribuyente", "score": 70},
    5: {"nombre": "ZOMAC alta pobreza/conflicto + Estructuración", "score": 55},
    6: {"nombre": "ZOMAC alta pobreza/conflicto sin estructuración", "score": 45},
    7: {"nombre": "Amazonía + Estructuración contribuyente", "score": 35},
    8: {"nombre": "Amazonía sin estructuración contribuyente", "score": 25},
}


@dataclass
class ResultadoProbabilidadCONFIS:
    """Resultado detallado de evaluación de Probabilidad CONFIS"""
    score: float  # 0-100

    # Componentes
    score_grupo: float  # Score del grupo de priorización (0-100)
    score_confis_normalizado: float  # Score CONFIS normalizado (0-100)
    score_sectorial: float  # Puntaje sectorial (0-10)
    score_territorial: float  # Puntaje territorial (0-10)
    puntaje_confis_total: float  # Territorial + Sectorial (2-20)

    # Contribuciones
    contribucion_grupo: float
    contribucion_confis: float

    # Grupo CONFIS
    grupo: int  # 1-8
    grupo_nombre: str

    # Metadata
    nivel: str  # "ALTA", "MEDIA", "BAJA"
    mensaje: str
    alertas: List[str]
    recomendaciones: List[str]


class ProbabilidadAprobacionCriterio(CriterioEvaluacion):
    """
    Evalúa probabilidad de aprobación en mecanismo Obras por Impuestos
    basándose en la metodología CONFIS (Anexo 2).

    Criterio: 20% del score total (Arquitectura C)

    Metodología CONFIS integrada (Feb 2026):
    Score = GrupoPrioridad(20%) + ScoreCONFIS_Normalizado(80%)

    Donde:
    - GrupoPrioridad: Score 25-100 según grupo 1-8
    - ScoreCONFIS = (Territorial + Sectorial) / 20 × 100
      - Territorial: promedio(IPM, MDM_inv, IICA, CULTIVOS), rango 1-10
      - Sectorial: puntaje brecha del sector en municipio, rango 1-10

    Grupos de priorización:
    1-2: Proyectos PATR-PDET (con/sin estructuración contribuyente)
    3-4: Municipios PDET (con/sin estructuración)
    5-6: ZOMAC alta pobreza/conflicto (con/sin estructuración)
    7-8: Amazonía (con/sin estructuración)
    """

    # Pesos internos del criterio
    PESO_GRUPO = 0.20
    PESO_CONFIS = 0.80

    def __init__(
        self,
        peso: float = 0.20,
        probabilidad_manual: NivelProbabilidad = None,
        db_path: str = "data/proyectos.db"
    ):
        """
        Inicializa criterio.

        Args:
            peso: Peso del criterio en evaluación total (0.20 = 20%)
            probabilidad_manual: Probabilidad asignada manualmente (opcional)
            db_path: Ruta a base de datos con matriz PDET
        """
        super().__init__(peso)
        self.nombre = "Probabilidad de Aprobación CONFIS"
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
        Evalúa probabilidad de aprobación usando metodología CONFIS.

        Returns:
            Score 0-100 basado en grupo + score CONFIS
        """
        # Si hay probabilidad manual, usarla directamente
        if self.probabilidad_manual:
            return self._probabilidad_a_score(self.probabilidad_manual)

        # Obtener componentes
        grupo = self._determinar_grupo(proyecto)
        score_grupo = GRUPOS_CONFIS.get(grupo, {"score": 25})["score"]

        score_territorial = self._obtener_score_territorial(proyecto)
        score_sectorial = self._obtener_score_sectorial(proyecto)

        # Score CONFIS combinado (rango 2-20 → normalizado 0-100)
        puntaje_confis = score_territorial + score_sectorial
        score_confis_norm = (puntaje_confis / 20.0) * 100

        # Score total ponderado
        score = (
            score_grupo * self.PESO_GRUPO +
            score_confis_norm * self.PESO_CONFIS
        )

        # Guardar metadata en proyecto
        proyecto.grupo_priorizacion_confis = grupo
        proyecto.puntaje_confis_total = puntaje_confis

        return min(max(score, 0), 100)

    def evaluar_detallado(self, proyecto: ProyectoSocial) -> ResultadoProbabilidadCONFIS:
        """
        Evaluación detallada con metadata completa.

        Returns:
            ResultadoProbabilidadCONFIS con desglose completo
        """
        alertas = []
        recomendaciones = []

        # Determinar grupo
        grupo = self._determinar_grupo(proyecto)
        grupo_info = GRUPOS_CONFIS.get(grupo, {"nombre": "Desconocido", "score": 25})
        score_grupo = grupo_info["score"]

        # Scores componentes
        score_territorial = self._obtener_score_territorial(proyecto)
        score_sectorial = self._obtener_score_sectorial(proyecto)

        # Score CONFIS combinado
        puntaje_confis = score_territorial + score_sectorial
        score_confis_norm = (puntaje_confis / 20.0) * 100

        # Contribuciones
        contrib_grupo = score_grupo * self.PESO_GRUPO
        contrib_confis = score_confis_norm * self.PESO_CONFIS

        # Score total
        score = contrib_grupo + contrib_confis

        # Guardar metadata
        proyecto.grupo_priorizacion_confis = grupo
        proyecto.puntaje_confis_total = puntaje_confis

        # Alertas por grupo
        if grupo <= 2:
            alertas.append(
                f"⭐ Grupo {grupo} PATR-PDET: Máxima prioridad en distribución CONFIS"
            )
        elif grupo <= 4:
            alertas.append(
                f"✅ Grupo {grupo} PDET: Alta prioridad en distribución CONFIS"
            )
        elif grupo <= 6:
            alertas.append(
                f"ℹ️  Grupo {grupo} ZOMAC: Prioridad media en distribución CONFIS"
            )
        else:
            alertas.append(
                f"⚠️  Grupo {grupo} Amazonía: Prioridad baja en distribución CONFIS"
            )

        # Alertas por score
        if score_sectorial >= 8:
            alertas.append(
                f"⭐ Brecha sectorial alta ({score_sectorial}/10): "
                f"Sector con necesidad urgente en el municipio"
            )

        if score_territorial >= 8:
            alertas.append(
                f"⭐ Puntaje territorial alto ({score_territorial:.1f}/10): "
                f"Municipio con alta vulnerabilidad"
            )

        # Recomendaciones
        if not proyecto.contribuyente_paga_estructuracion:
            recomendaciones.append(
                "💡 Si el contribuyente paga estructuración, sube al grupo "
                f"impar ({grupo-1 if grupo % 2 == 0 else grupo}) con mayor prioridad"
            )

        if score < 50:
            recomendaciones.append(
                "⚠️  Probabilidad baja: Considerar sectores con mayor brecha "
                "o municipios con mayor puntaje territorial"
            )

        if score_territorial == 5.0 and proyecto.puntaje_territorial_confis is None:
            recomendaciones.append(
                "📋 Puntaje territorial no especificado (usando default 5.0). "
                "Especificar puntaje_territorial_confis para mayor precisión"
            )

        # Determinar nivel
        nivel = self._determinar_nivel(score)

        # Mensaje
        if score >= 80:
            mensaje = "Alta probabilidad de aprobación CONFIS"
        elif score >= 60:
            mensaje = "Probabilidad media de aprobación CONFIS"
        elif score >= 40:
            mensaje = "Probabilidad baja-media de aprobación CONFIS"
        else:
            mensaje = "Probabilidad baja de aprobación CONFIS"

        return ResultadoProbabilidadCONFIS(
            score=min(max(score, 0), 100),
            score_grupo=score_grupo,
            score_confis_normalizado=score_confis_norm,
            score_sectorial=score_sectorial,
            score_territorial=score_territorial,
            puntaje_confis_total=puntaje_confis,
            contribucion_grupo=contrib_grupo,
            contribucion_confis=contrib_confis,
            grupo=grupo,
            grupo_nombre=grupo_info["nombre"],
            nivel=nivel,
            mensaje=mensaje,
            alertas=alertas,
            recomendaciones=recomendaciones
        )

    def _determinar_grupo(self, proyecto: ProyectoSocial) -> int:
        """
        Determina el grupo de priorización CONFIS (1-8).

        Lógica (Anexo 2 CONFIS):
        - Grupos 1-2: Proyectos PATR-PDET
        - Grupos 3-4: Municipios PDET
        - Grupos 5-6: ZOMAC alta pobreza/conflicto
        - Grupos 7-8: Amazonía
        - Impares: contribuyente paga estructuración
        - Pares: sin estructuración contribuyente
        """
        # Si ya está asignado manualmente, usarlo
        if proyecto.grupo_priorizacion_confis:
            return proyecto.grupo_priorizacion_confis

        # Determinar tipo de municipio
        tipo = proyecto.tipo_municipio

        # Inferir tipo si no está definido
        if tipo is None:
            if proyecto.tiene_municipios_pdet:
                tipo = "PDET"
            else:
                tipo = "PDET"  # Default conservador para elegibles

        # Asignar grupo base
        if proyecto.es_patr_pdet:
            grupo_base = 1  # PATR-PDET
        elif tipo == "PDET":
            grupo_base = 3  # PDET
        elif tipo == "ZOMAC":
            grupo_base = 5  # ZOMAC
        elif tipo == "AMAZONIA":
            grupo_base = 7  # Amazonía
        else:
            grupo_base = 5  # Default conservador

        # Ajustar por estructuración (impares = con, pares = sin)
        if not proyecto.contribuyente_paga_estructuracion:
            grupo_base += 1

        return min(grupo_base, 8)

    def _obtener_score_territorial(self, proyecto: ProyectoSocial) -> float:
        """
        Obtiene puntaje territorial CONFIS (1-10).

        El puntaje territorial es el promedio de:
        - IPM (Índice de Pobreza Multidimensional)
        - MDM invertido (Desempeño Municipal)
        - IICA (Incidencia Conflicto Armado)
        - CULTIVOS (Cultivos Ilícitos)

        Cada componente normalizado 1-10.

        Returns:
            Puntaje territorial 1-10 (5.0 si no disponible)
        """
        # Si está definido en el proyecto, usarlo
        if proyecto.puntaje_territorial_confis is not None:
            return max(min(proyecto.puntaje_territorial_confis, 10.0), 1.0)

        # Default neutro: 5.0 (punto medio de la escala)
        return 5.0

    def _obtener_score_sectorial(self, proyecto: ProyectoSocial) -> float:
        """
        Obtiene puntaje sectorial CONFIS (1-10).

        Usa la matriz PDET existente para obtener el puntaje de brecha
        del sector del proyecto en el municipio.

        Returns:
            Puntaje sectorial 1-10 (5.0 si no disponible)
        """
        # Si ya tiene puntaje sectorial max calculado, usarlo
        if proyecto.puntaje_sectorial_max is not None:
            return float(max(min(proyecto.puntaje_sectorial_max, 10), 1))

        # Intentar obtener de la base de datos
        if self.matriz_repo is None:
            return 5.0  # Neutro sin DB

        if not proyecto.municipios or not proyecto.sectores:
            return 5.0

        puntajes_encontrados = []

        for municipio_nombre in proyecto.municipios:
            departamento = self._get_departamento_municipio(
                municipio_nombre, proyecto.departamentos
            )
            if not departamento:
                continue

            registro = self.matriz_repo.get_municipio(departamento, municipio_nombre)
            if not registro:
                continue

            for sector in proyecto.sectores:
                puntaje = registro.get_puntaje_sector(sector)
                if puntaje > 0:
                    puntajes_encontrados.append(puntaje)

        if not puntajes_encontrados:
            return 5.0

        # Usar puntaje máximo (favorece mejor oportunidad)
        puntaje_max = max(puntajes_encontrados)

        # Guardar metadata
        proyecto.tiene_municipios_pdet = True
        proyecto.puntaje_sectorial_max = puntaje_max

        return float(puntaje_max)

    def _get_departamento_municipio(
        self,
        municipio: str,
        departamentos: List[str]
    ) -> Optional[str]:
        """Identifica departamento de un municipio."""
        if not departamentos:
            return None

        if len(departamentos) == 1:
            return departamentos[0]

        for depto in departamentos:
            if self.matriz_repo and self.matriz_repo.es_municipio_pdet(depto, municipio):
                return depto

        return departamentos[0]

    def _determinar_nivel(self, score: float) -> str:
        """Determina nivel de probabilidad basado en score."""
        if score >= 75:
            return "ALTA"
        elif score >= 45:
            return "MEDIA"
        else:
            return "BAJA"

    def _probabilidad_a_score(self, probabilidad: NivelProbabilidad) -> float:
        """Convierte nivel manual a score."""
        if probabilidad == NivelProbabilidad.ALTA:
            return 100
        elif probabilidad == NivelProbabilidad.MEDIA:
            return 60
        else:
            return 30

    @staticmethod
    def score_a_probabilidad(score: float) -> str:
        """Convierte score a nivel de probabilidad."""
        if score >= 75:
            return "alta"
        elif score >= 45:
            return "media"
        else:
            return "baja"

    def evaluar_con_nivel(self, proyecto: ProyectoSocial) -> tuple:
        """Evalúa y retorna (score, nivel)."""
        score = self.evaluar(proyecto)
        nivel = self.score_a_probabilidad(score)
        return score, nivel

    def get_nombre(self) -> str:
        return "Probabilidad de Aprobación CONFIS"

    def get_descripcion(self) -> str:
        return (
            "Evalúa la probabilidad de aprobación en Obras por Impuestos usando "
            "la metodología CONFIS (Anexo 2). Integra enfoque territorial "
            "(IPM, MDM, IICA, CULTIVOS), enfoque sectorial (brechas por municipio) "
            "y grupo de priorización (1-8). "
            "Score = GrupoPrioridad(20%) + ScoreCONFIS(80%)."
        )

    def get_detalles_evaluacion(self, proyecto: ProyectoSocial) -> dict:
        """Retorna detalles de la evaluación para debugging."""
        resultado = self.evaluar_detallado(proyecto)

        return {
            'probabilidad_nivel': resultado.nivel,
            'score_total': resultado.score,
            'componentes': {
                'grupo_priorizacion': {
                    'grupo': resultado.grupo,
                    'nombre': resultado.grupo_nombre,
                    'score': resultado.score_grupo,
                    'peso': self.PESO_GRUPO,
                    'ponderado': resultado.contribucion_grupo
                },
                'score_confis': {
                    'territorial': resultado.score_territorial,
                    'sectorial': resultado.score_sectorial,
                    'confis_total': resultado.puntaje_confis_total,
                    'normalizado': resultado.score_confis_normalizado,
                    'peso': self.PESO_CONFIS,
                    'ponderado': resultado.contribucion_confis
                }
            },
            'municipios_pdet': proyecto.tiene_municipios_pdet,
            'tipo_municipio': proyecto.tipo_municipio,
            'es_patr_pdet': proyecto.es_patr_pdet,
            'alertas': resultado.alertas,
            'recomendaciones': resultado.recomendaciones
        }
