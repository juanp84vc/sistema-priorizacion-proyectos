"""
Modelos para el historial de versiones y trazabilidad de proyectos.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class TipoRecomendacion(Enum):
    """Tipos de recomendación según prioridad."""
    CRITICA = "crítica"
    IMPORTANTE = "importante"
    OPCIONAL = "opcional"
    FORTALEZA = "fortaleza"


class EstadoRecomendacion(Enum):
    """Estado de implementación de una recomendación."""
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    IMPLEMENTADA = "implementada"
    RECHAZADA = "rechazada"
    NO_APLICABLE = "no_aplicable"


@dataclass
class RecomendacionImplementada:
    """
    Registro de una recomendación y su estado de implementación.

    Attributes:
        id: Identificador único de la recomendación
        criterio: Criterio al que pertenece (ej: "Costo-Efectividad")
        tipo: Tipo de recomendación (crítica, importante, etc.)
        descripcion: Descripción de la recomendación
        impacto_estimado: Puntos estimados de mejora
        estado: Estado actual de implementación
        fecha_creacion: Cuando se generó la recomendación
        fecha_implementacion: Cuando se implementó (si aplica)
        nota_implementacion: Notas sobre cómo se implementó
        cambios_realizados: Lista de cambios específicos realizados
    """
    id: str
    criterio: str
    tipo: TipoRecomendacion
    descripcion: str
    impacto_estimado: str
    estado: EstadoRecomendacion = EstadoRecomendacion.PENDIENTE
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_implementacion: Optional[datetime] = None
    nota_implementacion: Optional[str] = None
    cambios_realizados: List[str] = field(default_factory=list)

    def marcar_implementada(self, nota: str, cambios: List[str]):
        """Marca la recomendación como implementada."""
        self.estado = EstadoRecomendacion.IMPLEMENTADA
        self.fecha_implementacion = datetime.now()
        self.nota_implementacion = nota
        self.cambios_realizados = cambios

    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización."""
        return {
            'id': self.id,
            'criterio': self.criterio,
            'tipo': self.tipo.value,
            'descripcion': self.descripcion,
            'impacto_estimado': self.impacto_estimado,
            'estado': self.estado.value,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'fecha_implementacion': self.fecha_implementacion.isoformat() if self.fecha_implementacion else None,
            'nota_implementacion': self.nota_implementacion,
            'cambios_realizados': self.cambios_realizados
        }


@dataclass
class VersionProyecto:
    """
    Representa una versión específica de un proyecto con su evaluación.

    Attributes:
        numero_version: Número de versión (ej: 1, 2, 3)
        fecha: Fecha de esta versión
        score_total: Score total obtenido
        scores_criterios: Scores por cada criterio
        recomendaciones_generadas: Recomendaciones generadas en esta versión
        cambios_desde_version_anterior: Descripción de cambios
        usuario: Usuario que realizó los cambios
        notas: Notas adicionales sobre esta versión
    """
    numero_version: int
    fecha: datetime
    score_total: float
    scores_criterios: Dict[str, float]
    recomendaciones_generadas: List[RecomendacionImplementada] = field(default_factory=list)
    cambios_desde_version_anterior: List[str] = field(default_factory=list)
    usuario: str = "Sistema"
    notas: str = ""

    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización."""
        return {
            'numero_version': self.numero_version,
            'fecha': self.fecha.isoformat(),
            'score_total': self.score_total,
            'scores_criterios': self.scores_criterios,
            'recomendaciones_generadas': [r.to_dict() for r in self.recomendaciones_generadas],
            'cambios_desde_version_anterior': self.cambios_desde_version_anterior,
            'usuario': self.usuario,
            'notas': self.notas
        }


@dataclass
class HistorialProyecto:
    """
    Historial completo de un proyecto con todas sus versiones.

    Attributes:
        proyecto_id: ID del proyecto
        proyecto_nombre: Nombre del proyecto
        fecha_creacion: Fecha de creación del proyecto
        versiones: Lista de versiones del proyecto
        recomendaciones_pendientes: Recomendaciones aún no implementadas
    """
    proyecto_id: str
    proyecto_nombre: str
    fecha_creacion: datetime
    versiones: List[VersionProyecto] = field(default_factory=list)
    recomendaciones_pendientes: List[RecomendacionImplementada] = field(default_factory=list)

    @property
    def version_actual(self) -> Optional[VersionProyecto]:
        """Retorna la versión más reciente."""
        return self.versiones[-1] if self.versiones else None

    @property
    def numero_versiones(self) -> int:
        """Retorna el número total de versiones."""
        return len(self.versiones)

    @property
    def mejora_total(self) -> float:
        """Calcula la mejora total desde la primera versión."""
        if len(self.versiones) < 2:
            return 0.0
        return self.versiones[-1].score_total - self.versiones[0].score_total

    @property
    def porcentaje_mejora(self) -> float:
        """Calcula el porcentaje de mejora desde la primera versión."""
        if len(self.versiones) < 2 or self.versiones[0].score_total == 0:
            return 0.0
        mejora = self.mejora_total
        return (mejora / self.versiones[0].score_total) * 100

    def agregar_version(self, version: VersionProyecto):
        """Agrega una nueva versión al historial."""
        self.versiones.append(version)

    def obtener_recomendaciones_implementadas(self) -> List[RecomendacionImplementada]:
        """Retorna todas las recomendaciones que han sido implementadas."""
        implementadas = []
        for version in self.versiones:
            implementadas.extend([
                r for r in version.recomendaciones_generadas
                if r.estado == EstadoRecomendacion.IMPLEMENTADA
            ])
        return implementadas

    def obtener_timeline(self) -> List[Dict]:
        """
        Genera un timeline de eventos del proyecto.

        Returns:
            Lista de eventos ordenados cronológicamente
        """
        eventos = []

        # Evento de creación
        eventos.append({
            'fecha': self.fecha_creacion,
            'tipo': 'creacion',
            'descripcion': 'Proyecto creado',
            'score': self.versiones[0].score_total if self.versiones else None
        })

        # Eventos de versiones
        for i, version in enumerate(self.versiones):
            if i > 0:  # Skip primera versión (ya está en creación)
                score_anterior = self.versiones[i-1].score_total
                mejora = version.score_total - score_anterior

                eventos.append({
                    'fecha': version.fecha,
                    'tipo': 'actualizacion',
                    'version': version.numero_version,
                    'descripcion': f'Actualización v{version.numero_version}',
                    'score': version.score_total,
                    'mejora': mejora,
                    'cambios': version.cambios_desde_version_anterior
                })

        # Eventos de recomendaciones implementadas
        for rec in self.obtener_recomendaciones_implementadas():
            if rec.fecha_implementacion:
                eventos.append({
                    'fecha': rec.fecha_implementacion,
                    'tipo': 'recomendacion',
                    'criterio': rec.criterio,
                    'descripcion': f'Recomendación implementada: {rec.descripcion[:50]}...',
                    'impacto': rec.impacto_estimado
                })

        # Ordenar por fecha
        eventos.sort(key=lambda x: x['fecha'])

        return eventos

    def generar_reporte_trazabilidad(self) -> Dict:
        """
        Genera un reporte completo de trazabilidad.

        Returns:
            Diccionario con toda la información de trazabilidad
        """
        recomendaciones_impl = self.obtener_recomendaciones_implementadas()

        return {
            'proyecto': {
                'id': self.proyecto_id,
                'nombre': self.proyecto_nombre,
                'fecha_creacion': self.fecha_creacion.isoformat()
            },
            'resumen': {
                'numero_versiones': self.numero_versiones,
                'version_actual': self.version_actual.numero_version if self.version_actual else 0,
                'score_inicial': self.versiones[0].score_total if self.versiones else 0,
                'score_actual': self.version_actual.score_total if self.version_actual else 0,
                'mejora_total': self.mejora_total,
                'porcentaje_mejora': self.porcentaje_mejora,
                'recomendaciones_implementadas': len(recomendaciones_impl),
                'recomendaciones_pendientes': len(self.recomendaciones_pendientes)
            },
            'versiones': [v.to_dict() for v in self.versiones],
            'timeline': self.obtener_timeline(),
            'recomendaciones_implementadas': [r.to_dict() for r in recomendaciones_impl],
            'recomendaciones_pendientes': [r.to_dict() for r in self.recomendaciones_pendientes]
        }

    def to_dict(self) -> Dict:
        """Convierte a diccionario para serialización."""
        return {
            'proyecto_id': self.proyecto_id,
            'proyecto_nombre': self.proyecto_nombre,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'versiones': [v.to_dict() for v in self.versiones],
            'recomendaciones_pendientes': [r.to_dict() for r in self.recomendaciones_pendientes]
        }
