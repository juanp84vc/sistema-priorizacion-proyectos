"""
Repositorio para acceso a matriz de priorización sectorial PDET/ZOMAC.

Proporciona interfaz para consultar datos oficiales de Obras por Impuestos
sobre priorización sectorial en 362 municipios PDET/ZOMAC.
"""
import sqlite3
from typing import Optional, List, Tuple
from pathlib import Path
import sys

# Agregar src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.matriz_pdet_zomac import RegistroMunicipioPDET


class MatrizPDETRepository:
    """
    Repositorio para acceder a matriz de priorización PDET/ZOMAC.

    Almacena y consulta datos de 362 municipios con puntajes
    de priorización sectorial (1-10) para 10 sectores.
    """

    def __init__(self, db_path: str = "data/proyectos.db"):
        """
        Inicializa repositorio.

        Args:
            db_path: Ruta a base de datos SQLite
        """
        self.db_path = db_path
        self._inicializar_tabla()

    def _inicializar_tabla(self):
        """Crea tabla matriz_pdet_zomac si no existe"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS matriz_pdet_zomac (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    departamento TEXT NOT NULL,
                    municipio TEXT NOT NULL,
                    educacion INTEGER NOT NULL,
                    salud INTEGER NOT NULL,
                    alcantarillado INTEGER NOT NULL,
                    via INTEGER NOT NULL,
                    energia INTEGER NOT NULL,
                    banda_ancha INTEGER NOT NULL,
                    riesgo_ambiental INTEGER NOT NULL,
                    infraestructura_rural INTEGER NOT NULL,
                    cultura INTEGER NOT NULL,
                    deporte INTEGER NOT NULL,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(departamento, municipio)
                )
            """)

            # Crear índices para búsquedas rápidas
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_departamento
                ON matriz_pdet_zomac(departamento)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_municipio
                ON matriz_pdet_zomac(municipio)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_depto_mun
                ON matriz_pdet_zomac(departamento, municipio)
            """)

            conn.commit()

    def get_municipio(self, departamento: str, municipio: str) -> Optional[RegistroMunicipioPDET]:
        """
        Obtiene registro de un municipio específico.

        Args:
            departamento: Nombre del departamento
            municipio: Nombre del municipio

        Returns:
            RegistroMunicipioPDET si existe, None si no está en PDET/ZOMAC
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM matriz_pdet_zomac
                WHERE UPPER(departamento) = UPPER(?)
                AND UPPER(municipio) = UPPER(?)
            """, (departamento, municipio))

            row = cursor.fetchone()
            if not row:
                return None

            return RegistroMunicipioPDET(
                departamento=row['departamento'],
                municipio=row['municipio'],
                educacion=row['educacion'],
                salud=row['salud'],
                alcantarillado=row['alcantarillado'],
                via=row['via'],
                energia=row['energia'],
                banda_ancha=row['banda_ancha'],
                riesgo_ambiental=row['riesgo_ambiental'],
                infraestructura_rural=row['infraestructura_rural'],
                cultura=row['cultura'],
                deporte=row['deporte']
            )

    def get_municipios_por_puntaje_sector(
        self,
        sector: str,
        puntaje_minimo: int = 7
    ) -> List[RegistroMunicipioPDET]:
        """
        Obtiene municipios con puntaje alto en un sector específico.

        Args:
            sector: Nombre del sector (ej. 'educacion', 'salud')
            puntaje_minimo: Puntaje mínimo requerido

        Returns:
            Lista de registros ordenados por puntaje descendente
        """
        # Normalizar nombre columna
        sector_col = sector.lower().replace(' ', '_').replace('í', 'i').replace('ó', 'o')

        # Validar que sea columna válida
        sectores_validos = [
            'educacion', 'salud', 'alcantarillado', 'via', 'energia',
            'banda_ancha', 'riesgo_ambiental', 'infraestructura_rural',
            'cultura', 'deporte'
        ]

        if sector_col not in sectores_validos:
            raise ValueError(f"Sector inválido: {sector}. Válidos: {sectores_validos}")

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = f"""
                SELECT * FROM matriz_pdet_zomac
                WHERE {sector_col} >= ?
                ORDER BY {sector_col} DESC
            """
            cursor = conn.execute(query, (puntaje_minimo,))

            return [
                RegistroMunicipioPDET(
                    departamento=row['departamento'],
                    municipio=row['municipio'],
                    educacion=row['educacion'],
                    salud=row['salud'],
                    alcantarillado=row['alcantarillado'],
                    via=row['via'],
                    energia=row['energia'],
                    banda_ancha=row['banda_ancha'],
                    riesgo_ambiental=row['riesgo_ambiental'],
                    infraestructura_rural=row['infraestructura_rural'],
                    cultura=row['cultura'],
                    deporte=row['deporte']
                )
                for row in cursor.fetchall()
            ]

    def es_municipio_pdet(self, departamento: str, municipio: str) -> bool:
        """
        Verifica si municipio está en lista PDET/ZOMAC.

        Args:
            departamento: Nombre del departamento
            municipio: Nombre del municipio

        Returns:
            True si está en PDET/ZOMAC, False si no
        """
        return self.get_municipio(departamento, municipio) is not None

    def get_departamentos(self) -> List[str]:
        """
        Lista todos los departamentos PDET/ZOMAC.

        Returns:
            Lista de nombres de departamentos ordenados alfabéticamente
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT DISTINCT departamento
                FROM matriz_pdet_zomac
                ORDER BY departamento
            """)
            return [row[0] for row in cursor.fetchall()]

    def get_municipios_por_departamento(self, departamento: str) -> List[str]:
        """
        Lista municipios PDET/ZOMAC de un departamento.

        Args:
            departamento: Nombre del departamento

        Returns:
            Lista de nombres de municipios ordenados alfabéticamente
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT municipio
                FROM matriz_pdet_zomac
                WHERE UPPER(departamento) = UPPER(?)
                ORDER BY municipio
            """, (departamento,))
            return [row[0] for row in cursor.fetchall()]

    def get_total_municipios(self) -> int:
        """
        Cuenta total de municipios PDET/ZOMAC.

        Returns:
            Número total de municipios en la matriz
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM matriz_pdet_zomac")
            return cursor.fetchone()[0]

    def get_estadisticas_sector(self, sector: str) -> dict:
        """
        Obtiene estadísticas de un sector.

        Args:
            sector: Nombre del sector

        Returns:
            Diccionario con estadísticas (promedio, max, min, etc.)
        """
        # Normalizar nombre columna
        sector_col = sector.lower().replace(' ', '_').replace('í', 'i').replace('ó', 'o')

        with sqlite3.connect(self.db_path) as conn:
            query = f"""
                SELECT
                    AVG({sector_col}) as promedio,
                    MAX({sector_col}) as maximo,
                    MIN({sector_col}) as minimo,
                    COUNT(CASE WHEN {sector_col} >= 7 THEN 1 END) as alta_prioridad,
                    COUNT(CASE WHEN {sector_col} BETWEEN 4 AND 6 THEN 1 END) as media_prioridad,
                    COUNT(CASE WHEN {sector_col} <= 3 THEN 1 END) as baja_prioridad
                FROM matriz_pdet_zomac
            """
            cursor = conn.execute(query)
            row = cursor.fetchone()

            return {
                'sector': sector,
                'promedio': round(row[0], 2),
                'maximo': row[1],
                'minimo': row[2],
                'municipios_alta_prioridad': row[3],
                'municipios_media_prioridad': row[4],
                'municipios_baja_prioridad': row[5]
            }

    def buscar_municipios(self, texto: str, limite: int = 10) -> List[Tuple[str, str]]:
        """
        Busca municipios por nombre parcial.

        Args:
            texto: Texto a buscar en nombre de municipio
            limite: Número máximo de resultados

        Returns:
            Lista de tuplas (departamento, municipio)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT departamento, municipio
                FROM matriz_pdet_zomac
                WHERE UPPER(municipio) LIKE UPPER(?)
                ORDER BY municipio
                LIMIT ?
            """, (f"%{texto}%", limite))

            return [(row[0], row[1]) for row in cursor.fetchall()]

    def vaciar_tabla(self):
        """
        Elimina todos los registros de la tabla.
        Útil para recarga de datos.

        ⚠️ PRECAUCIÓN: Operación destructiva.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM matriz_pdet_zomac")
            conn.commit()

    def __str__(self) -> str:
        """Representación legible del repositorio"""
        total = self.get_total_municipios()
        deptos = len(self.get_departamentos())
        return f"MatrizPDETRepository({total} municipios, {deptos} departamentos)"

    def __repr__(self) -> str:
        """Representación técnica del repositorio"""
        return f"MatrizPDETRepository(db_path='{self.db_path}')"
