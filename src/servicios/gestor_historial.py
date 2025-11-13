"""
Gestor de historial de versiones y trazabilidad de proyectos.
"""
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
from models.proyecto import ProyectoSocial
from models.historial import (
    HistorialProyecto, VersionProyecto, RecomendacionImplementada,
    TipoRecomendacion, EstadoRecomendacion
)


class GestorHistorial:
    """
    Gestiona el historial de versiones y recomendaciones de proyectos.
    """

    def __init__(self):
        """Inicializa el gestor de historial."""
        self.historiales: Dict[str, HistorialProyecto] = {}

    def crear_historial(self, proyecto: ProyectoSocial, score_inicial: float,
                       scores_criterios: Dict[str, float],
                       recomendaciones: Dict[str, List[str]]) -> HistorialProyecto:
        """
        Crea un nuevo historial para un proyecto.

        Args:
            proyecto: Proyecto para el cual crear el historial
            score_inicial: Score inicial del proyecto
            scores_criterios: Scores por criterio
            recomendaciones: Dict con recomendaciones por categoría

        Returns:
            HistorialProyecto creado
        """
        # Crear primera versión
        version_inicial = VersionProyecto(
            numero_version=1,
            fecha=datetime.now(),
            score_total=score_inicial,
            scores_criterios=scores_criterios,
            recomendaciones_generadas=[],
            cambios_desde_version_anterior=["Versión inicial del proyecto"],
            usuario="Sistema",
            notas="Primera evaluación del proyecto"
        )

        # Convertir recomendaciones a objetos RecomendacionImplementada
        recomendaciones_obj = self._convertir_recomendaciones(recomendaciones, scores_criterios)
        version_inicial.recomendaciones_generadas = recomendaciones_obj

        # Crear historial
        historial = HistorialProyecto(
            proyecto_id=proyecto.id,
            proyecto_nombre=proyecto.nombre,
            fecha_creacion=datetime.now(),
            versiones=[version_inicial],
            recomendaciones_pendientes=recomendaciones_obj.copy()
        )

        self.historiales[proyecto.id] = historial
        return historial

    def agregar_version(self, proyecto_id: str, nuevo_score: float,
                       nuevos_scores_criterios: Dict[str, float],
                       cambios_realizados: List[str],
                       recomendaciones_implementadas: List[str],
                       notas: str = "") -> VersionProyecto:
        """
        Agrega una nueva versión al historial de un proyecto.

        Args:
            proyecto_id: ID del proyecto
            nuevo_score: Nuevo score total
            nuevos_scores_criterios: Nuevos scores por criterio
            cambios_realizados: Lista de cambios realizados
            recomendaciones_implementadas: IDs de recomendaciones implementadas
            notas: Notas adicionales

        Returns:
            Nueva versión creada
        """
        if proyecto_id not in self.historiales:
            raise ValueError(f"No existe historial para el proyecto {proyecto_id}")

        historial = self.historiales[proyecto_id]
        numero_version = historial.numero_versiones + 1

        # Marcar recomendaciones como implementadas
        for rec_id in recomendaciones_implementadas:
            for rec in historial.recomendaciones_pendientes:
                if rec.id == rec_id:
                    rec.marcar_implementada(
                        nota=f"Implementada en versión {numero_version}",
                        cambios=cambios_realizados
                    )
                    # Mover de pendientes a la versión
                    historial.recomendaciones_pendientes.remove(rec)

        # Crear nueva versión
        nueva_version = VersionProyecto(
            numero_version=numero_version,
            fecha=datetime.now(),
            score_total=nuevo_score,
            scores_criterios=nuevos_scores_criterios,
            cambios_desde_version_anterior=cambios_realizados,
            usuario="Usuario",
            notas=notas
        )

        historial.agregar_version(nueva_version)
        return nueva_version

    def obtener_historial(self, proyecto_id: str) -> Optional[HistorialProyecto]:
        """
        Obtiene el historial completo de un proyecto.

        Args:
            proyecto_id: ID del proyecto

        Returns:
            HistorialProyecto o None si no existe
        """
        return self.historiales.get(proyecto_id)

    def comparar_versiones(self, proyecto_id: str, version1: int, version2: int) -> Dict:
        """
        Compara dos versiones de un proyecto.

        Args:
            proyecto_id: ID del proyecto
            version1: Número de primera versión
            version2: Número de segunda versión

        Returns:
            Dict con la comparación
        """
        historial = self.historiales.get(proyecto_id)
        if not historial:
            raise ValueError(f"No existe historial para el proyecto {proyecto_id}")

        if version1 < 1 or version1 > historial.numero_versiones:
            raise ValueError(f"Versión {version1} no existe")
        if version2 < 1 or version2 > historial.numero_versiones:
            raise ValueError(f"Versión {version2} no existe")

        v1 = historial.versiones[version1 - 1]
        v2 = historial.versiones[version2 - 1]

        diferencia_score = v2.score_total - v1.score_total
        porcentaje_mejora = (diferencia_score / v1.score_total * 100) if v1.score_total > 0 else 0

        # Comparar scores por criterio
        diferencias_criterios = {}
        for criterio in v2.scores_criterios:
            if criterio in v1.scores_criterios:
                diff = v2.scores_criterios[criterio] - v1.scores_criterios[criterio]
                diferencias_criterios[criterio] = {
                    'version_anterior': v1.scores_criterios[criterio],
                    'version_actual': v2.scores_criterios[criterio],
                    'diferencia': diff,
                    'porcentaje': (diff / v1.scores_criterios[criterio] * 100) if v1.scores_criterios[criterio] > 0 else 0
                }

        return {
            'proyecto_id': proyecto_id,
            'version_anterior': {
                'numero': version1,
                'fecha': v1.fecha.isoformat(),
                'score': v1.score_total
            },
            'version_actual': {
                'numero': version2,
                'fecha': v2.fecha.isoformat(),
                'score': v2.score_total
            },
            'mejora': {
                'diferencia_puntos': diferencia_score,
                'porcentaje': porcentaje_mejora
            },
            'diferencias_por_criterio': diferencias_criterios,
            'cambios_realizados': v2.cambios_desde_version_anterior
        }

    def _convertir_recomendaciones(self, recomendaciones: Dict[str, List[str]],
                                   scores_criterios: Dict[str, float]) -> List[RecomendacionImplementada]:
        """
        Convierte recomendaciones en formato texto a objetos RecomendacionImplementada.

        Args:
            recomendaciones: Dict con recomendaciones por categoría
            scores_criterios: Scores actuales por criterio

        Returns:
            Lista de RecomendacionImplementada
        """
        resultado = []

        # Mapeo de categorías a tipos
        tipo_map = {
            'criticas': TipoRecomendacion.CRITICA,
            'importantes': TipoRecomendacion.IMPORTANTE,
            'opcionales': TipoRecomendacion.OPCIONAL,
            'fortalezas': TipoRecomendacion.FORTALEZA
        }

        for categoria, lista_recs in recomendaciones.items():
            if categoria not in tipo_map:
                continue

            for rec_texto in lista_recs:
                # Extraer criterio del texto (buscar nombre del criterio en el texto)
                criterio = self._extraer_criterio_de_texto(rec_texto)

                # Extraer impacto estimado del texto
                impacto = self._extraer_impacto_de_texto(rec_texto)

                # Generar ID único
                rec_id = self._generar_id_recomendacion(rec_texto)

                rec_obj = RecomendacionImplementada(
                    id=rec_id,
                    criterio=criterio,
                    tipo=tipo_map[categoria],
                    descripcion=rec_texto,
                    impacto_estimado=impacto,
                    estado=EstadoRecomendacion.PENDIENTE,
                    fecha_creacion=datetime.now()
                )

                resultado.append(rec_obj)

        return resultado

    def _extraer_criterio_de_texto(self, texto: str) -> str:
        """Extrae el nombre del criterio del texto de la recomendación."""
        criterios = [
            "COSTO-EFECTIVIDAD",
            "STAKEHOLDERS",
            "PROBABILIDAD APROBACIÓN",
            "RIESGOS"
        ]

        texto_upper = texto.upper()
        for criterio in criterios:
            if criterio in texto_upper:
                return criterio.title()

        return "General"

    def _extraer_impacto_de_texto(self, texto: str) -> str:
        """Extrae el impacto estimado del texto de la recomendación."""
        # Buscar patrones como "+XX puntos", "+XX-YY puntos", "Impacto: +XX"
        import re

        patrones = [
            r'[Ii]mpacto[:\s]+\+?(\d+(?:-\d+)?)\s*puntos?',
            r'\+(\d+(?:-\d+)?)\s*puntos?',
            r'[Mm]ejora[:\s]+\+?(\d+(?:-\d+)?)\s*puntos?'
        ]

        for patron in patrones:
            match = re.search(patron, texto)
            if match:
                return f"+{match.group(1)} puntos"

        return "Variable"

    def _generar_id_recomendacion(self, texto: str) -> str:
        """Genera un ID único para una recomendación basado en su contenido."""
        # Usar hash del texto para generar ID único
        hash_obj = hashlib.md5(texto.encode())
        return f"rec_{hash_obj.hexdigest()[:12]}"

    def generar_reporte_trazabilidad(self, proyecto_id: str) -> Dict:
        """
        Genera un reporte completo de trazabilidad para exportar.

        Args:
            proyecto_id: ID del proyecto

        Returns:
            Dict con información completa de trazabilidad
        """
        historial = self.historiales.get(proyecto_id)
        if not historial:
            return {
                'error': f'No existe historial para el proyecto {proyecto_id}'
            }

        return historial.generar_reporte_trazabilidad()

    def obtener_estadisticas_mejora(self, proyecto_id: str) -> Dict:
        """
        Calcula estadísticas de mejora del proyecto.

        Args:
            proyecto_id: ID del proyecto

        Returns:
            Dict con estadísticas
        """
        historial = self.historiales.get(proyecto_id)
        if not historial or historial.numero_versiones < 2:
            return {
                'versiones_insuficientes': True,
                'mensaje': 'Se necesitan al menos 2 versiones para calcular estadísticas'
            }

        version_inicial = historial.versiones[0]
        version_actual = historial.version_actual

        # Calcular mejora por criterio
        mejoras_criterios = {}
        for criterio in version_actual.scores_criterios:
            if criterio in version_inicial.scores_criterios:
                mejora = version_actual.scores_criterios[criterio] - version_inicial.scores_criterios[criterio]
                mejoras_criterios[criterio] = {
                    'score_inicial': version_inicial.scores_criterios[criterio],
                    'score_actual': version_actual.scores_criterios[criterio],
                    'mejora_puntos': mejora,
                    'mejora_porcentaje': (mejora / version_inicial.scores_criterios[criterio] * 100)
                                        if version_inicial.scores_criterios[criterio] > 0 else 0
                }

        # Calcular tasa de implementación de recomendaciones
        total_recomendaciones = len(historial.obtener_recomendaciones_implementadas()) + len(historial.recomendaciones_pendientes)
        tasa_implementacion = (len(historial.obtener_recomendaciones_implementadas()) / total_recomendaciones * 100) \
                             if total_recomendaciones > 0 else 0

        return {
            'proyecto_id': proyecto_id,
            'proyecto_nombre': historial.proyecto_nombre,
            'periodo': {
                'fecha_inicio': version_inicial.fecha.isoformat(),
                'fecha_actual': version_actual.fecha.isoformat(),
                'duracion_dias': (version_actual.fecha - version_inicial.fecha).days
            },
            'scores': {
                'inicial': version_inicial.score_total,
                'actual': version_actual.score_total,
                'mejora_total': historial.mejora_total,
                'porcentaje_mejora': historial.porcentaje_mejora
            },
            'mejoras_por_criterio': mejoras_criterios,
            'recomendaciones': {
                'total_generadas': total_recomendaciones,
                'implementadas': len(historial.obtener_recomendaciones_implementadas()),
                'pendientes': len(historial.recomendaciones_pendientes),
                'tasa_implementacion': tasa_implementacion
            },
            'versiones': historial.numero_versiones
        }
