"""
Modelos de dominio para proyectos sociales.
SRP: Cada modelo tiene una responsabilidad clara.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class AreaGeografica(Enum):
    """Áreas geográficas de intervención"""
    URBANA = "urbana"
    RURAL = "rural"
    PERIURBANA = "periurbana"
    NACIONAL = "nacional"


class EstadoProyecto(Enum):
    """Estados del ciclo de vida del proyecto"""
    PROPUESTA = "propuesta"
    EVALUACION = "evaluacion"
    APROBADO = "aprobado"
    EN_EJECUCION = "en_ejecucion"
    FINALIZADO = "finalizado"
    RECHAZADO = "rechazado"


@dataclass
class ProyectoSocial:
    """
    Modelo de proyecto social.
    ISP: Interface mínima con solo los campos necesarios.
    """
    id: str
    nombre: str
    organizacion: str
    descripcion: str
    beneficiarios_directos: int
    beneficiarios_indirectos: int
    duracion_meses: int
    presupuesto_total: float
    ods_vinculados: List[str]
    area_geografica: AreaGeografica
    poblacion_objetivo: str
    departamentos: List[str]
    municipios: List[str] = field(default_factory=list)
    estado: EstadoProyecto = EstadoProyecto.PROPUESTA

    # NUEVO: Sectores del proyecto (para matriz PDET/ZOMAC)
    sectores: List[str] = field(default_factory=list)
    # Ejemplo: ["Educación", "Salud", "Infraestructura Rural"]

    # Indicadores específicos
    indicadores_impacto: Dict[str, float] = field(default_factory=dict)

    # NUEVO: Puntajes PDET calculados automáticamente
    puntajes_pdet: Dict[str, int] = field(default_factory=dict)
    # Ejemplo: {"Educación": 6, "Salud": 3, "Infraestructura Rural": 9}

    # NUEVO: Indicador si tiene municipios PDET
    tiene_municipios_pdet: bool = False

    # NUEVO: Puntaje máximo sectorial (calculado)
    puntaje_sectorial_max: Optional[int] = None

    # Metadata
    fecha_presentacion: str = ""
    contacto_organizacion: str = ""

    def __post_init__(self):
        """Validaciones básicas"""
        if self.beneficiarios_directos < 0:
            raise ValueError("Beneficiarios directos debe ser positivo")
        if self.duracion_meses <= 0:
            raise ValueError("Duración debe ser mayor a 0")
        if self.presupuesto_total <= 0:
            raise ValueError("Presupuesto debe ser mayor a 0")

    @property
    def beneficiarios_totales(self) -> int:
        """Total de beneficiarios (directos + indirectos)"""
        return self.beneficiarios_directos + self.beneficiarios_indirectos

    @property
    def presupuesto_por_beneficiario(self) -> float:
        """Costo promedio por beneficiario"""
        return self.presupuesto_total / self.beneficiarios_totales if self.beneficiarios_totales > 0 else 0

    @property
    def duracion_años(self) -> float:
        """Duración en años"""
        return self.duracion_meses / 12
