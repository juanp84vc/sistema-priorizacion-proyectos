"""
Modelo de datos para matriz de priorización sectorial PDET/ZOMAC.

Obras por Impuestos - Datos oficiales de priorización sectorial
para 362 municipios en zonas PDET y ZOMAC.
"""
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime


@dataclass
class RegistroMunicipioPDET:
    """
    Registro de priorización sectorial para municipio PDET/ZOMAC
    según Obras por Impuestos.

    Contiene puntajes 1-10 para 10 sectores, donde 10 indica
    máxima prioridad de inversión en ese sector para el municipio.
    """
    departamento: str
    municipio: str

    # Puntajes sectoriales (1-10, donde 10 = máxima prioridad)
    educacion: int
    salud: int
    alcantarillado: int
    via: int  # Infraestructura vial
    energia: int
    banda_ancha: int  # Conectividad
    riesgo_ambiental: int
    infraestructura_rural: int
    cultura: int
    deporte: int

    # Metadata
    es_pdet_zomac: bool = True  # Todos estos municipios lo son
    fecha_actualizacion: datetime = None

    def __post_init__(self):
        """Validaciones y normalización"""
        if self.fecha_actualizacion is None:
            self.fecha_actualizacion = datetime.now()

        # Normalizar nombres
        self.departamento = self.departamento.upper().strip()
        self.municipio = self.municipio.upper().strip()

        # Validar rangos
        sectores = [
            self.educacion, self.salud, self.alcantarillado, self.via,
            self.energia, self.banda_ancha, self.riesgo_ambiental,
            self.infraestructura_rural, self.cultura, self.deporte
        ]

        for puntaje in sectores:
            if not (1 <= puntaje <= 10):
                raise ValueError(f"Puntaje fuera de rango 1-10: {puntaje}")

    def get_puntaje_sector(self, sector: str) -> int:
        """
        Obtiene puntaje de un sector específico.

        Args:
            sector: Nombre del sector (acepta variaciones)

        Returns:
            Puntaje 1-10, o 0 si sector no reconocido
        """
        # Normalizar nombre sector
        sector_norm = sector.upper().strip()

        # Mapa de sectores (incluye variaciones de nombres)
        mapa_sectores = {
            'EDUCACIÓN': self.educacion,
            'EDUCACION': self.educacion,
            'SALUD': self.salud,
            'ALCANTARILLADO': self.alcantarillado,
            'VÍA': self.via,
            'VIA': self.via,
            'VÍAS': self.via,
            'VIAS': self.via,
            'INFRAESTRUCTURA VIAL': self.via,
            'ENERGÍA': self.energia,
            'ENERGIA': self.energia,
            'BANDA ANCHA': self.banda_ancha,
            'CONECTIVIDAD': self.banda_ancha,
            'RIESGO AMBIENTAL': self.riesgo_ambiental,
            'INFRAESTRUCTURA RURAL': self.infraestructura_rural,
            'INFRA RURAL': self.infraestructura_rural,
            'CULTURA': self.cultura,
            'DEPORTE': self.deporte,
            'DEPORTES': self.deporte,
        }

        return mapa_sectores.get(sector_norm, 0)

    def get_sectores_ordenados(self) -> List[Tuple[str, int]]:
        """
        Retorna sectores ordenados por prioridad (mayor a menor).

        Returns:
            Lista de tuplas (nombre_sector, puntaje) ordenadas
            por puntaje descendente
        """
        sectores = [
            ('Educación', self.educacion),
            ('Salud', self.salud),
            ('Alcantarillado', self.alcantarillado),
            ('Vía', self.via),
            ('Energía', self.energia),
            ('Banda Ancha', self.banda_ancha),
            ('Riesgo Ambiental', self.riesgo_ambiental),
            ('Infraestructura Rural', self.infraestructura_rural),
            ('Cultura', self.cultura),
            ('Deporte', self.deporte),
        ]

        return sorted(sectores, key=lambda x: x[1], reverse=True)

    def get_sectores_prioritarios(self, umbral: int = 7) -> List[Tuple[str, int]]:
        """
        Retorna solo sectores con prioridad alta (≥ umbral).

        Args:
            umbral: Puntaje mínimo para considerar prioritario (default 7)

        Returns:
            Lista de tuplas (nombre_sector, puntaje) con puntaje ≥ umbral
        """
        return [(nombre, puntaje) for nombre, puntaje in self.get_sectores_ordenados()
                if puntaje >= umbral]

    def get_puntaje_promedio(self) -> float:
        """Calcula puntaje promedio de todos los sectores"""
        sectores = [
            self.educacion, self.salud, self.alcantarillado, self.via,
            self.energia, self.banda_ancha, self.riesgo_ambiental,
            self.infraestructura_rural, self.cultura, self.deporte
        ]
        return sum(sectores) / len(sectores)

    def get_puntaje_maximo(self) -> Tuple[str, int]:
        """
        Retorna el sector con mayor prioridad.

        Returns:
            Tupla (nombre_sector, puntaje) del sector con puntaje máximo
        """
        sectores_ordenados = self.get_sectores_ordenados()
        return sectores_ordenados[0]

    def to_dict(self) -> Dict:
        """Convierte registro a diccionario para serialización"""
        return {
            'departamento': self.departamento,
            'municipio': self.municipio,
            'puntajes': {
                'Educación': self.educacion,
                'Salud': self.salud,
                'Alcantarillado': self.alcantarillado,
                'Vía': self.via,
                'Energía': self.energia,
                'Banda Ancha': self.banda_ancha,
                'Riesgo Ambiental': self.riesgo_ambiental,
                'Infraestructura Rural': self.infraestructura_rural,
                'Cultura': self.cultura,
                'Deporte': self.deporte,
            },
            'es_pdet_zomac': self.es_pdet_zomac,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }

    def __str__(self) -> str:
        """Representación legible del registro"""
        sector_max, puntaje_max = self.get_puntaje_maximo()
        return (f"RegistroMunicipioPDET({self.municipio}, {self.departamento} | "
                f"Sector prioritario: {sector_max} ({puntaje_max}/10))")

    def __repr__(self) -> str:
        """Representación técnica del registro"""
        return (f"RegistroMunicipioPDET(departamento='{self.departamento}', "
                f"municipio='{self.municipio}')")
