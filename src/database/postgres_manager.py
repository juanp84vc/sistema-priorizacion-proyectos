"""
Gestor de Base de Datos PostgreSQL para Streamlit Cloud.
Compatible con la interfaz del DatabaseManager SQLite.
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# Agregar src al path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class PostgreSQLManager:
    """Gestor de base de datos PostgreSQL para producción."""

    def __init__(self, connection_string: str):
        """
        Inicializa el gestor de PostgreSQL.

        Args:
            connection_string: URL de conexión a PostgreSQL
        """
        if not POSTGRES_AVAILABLE:
            raise ImportError("psycopg2 no está instalado. Ejecuta: pip install psycopg2-binary")

        self.connection_string = connection_string
        self.connection = None
        self._initialize_database()

    def _get_connection(self):
        """Obtiene una conexión a PostgreSQL."""
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(self.connection_string)
        return self.connection

    def _initialize_database(self):
        """Crea las tablas necesarias si no existen."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Tabla principal de proyectos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proyectos (
                id TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                organizacion TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                beneficiarios_directos INTEGER NOT NULL,
                beneficiarios_indirectos INTEGER NOT NULL,
                duracion_meses INTEGER NOT NULL,
                presupuesto_total REAL NOT NULL,
                ods_vinculados TEXT NOT NULL,
                area_geografica TEXT NOT NULL,
                poblacion_objetivo TEXT NOT NULL,
                departamentos TEXT NOT NULL,
                municipios TEXT,
                estado TEXT NOT NULL,
                indicadores_impacto TEXT NOT NULL,
                fecha_creacion TIMESTAMP NOT NULL,
                fecha_modificacion TIMESTAMP NOT NULL
            )
        """)

        # Tabla de historial de cambios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_cambios (
                id SERIAL PRIMARY KEY,
                proyecto_id TEXT NOT NULL,
                accion TEXT NOT NULL,
                usuario TEXT,
                fecha TIMESTAMP NOT NULL,
                cambios TEXT,
                FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE CASCADE
            )
        """)

        conn.commit()

    def _proyecto_to_dict(self, proyecto: ProyectoSocial) -> Dict[str, Any]:
        """Convierte un objeto ProyectoSocial a diccionario para guardar en BD."""
        return {
            'id': proyecto.id,
            'nombre': proyecto.nombre,
            'organizacion': proyecto.organizacion,
            'descripcion': proyecto.descripcion,
            'beneficiarios_directos': proyecto.beneficiarios_directos,
            'beneficiarios_indirectos': proyecto.beneficiarios_indirectos,
            'duracion_meses': proyecto.duracion_meses,
            'presupuesto_total': proyecto.presupuesto_total,
            'ods_vinculados': json.dumps(proyecto.ods_vinculados),
            'area_geografica': proyecto.area_geografica.value,
            'poblacion_objetivo': proyecto.poblacion_objetivo,
            'departamentos': json.dumps(proyecto.departamentos),
            'municipios': json.dumps(proyecto.municipios) if proyecto.municipios else json.dumps([]),
            'estado': proyecto.estado.value,
            'indicadores_impacto': json.dumps(proyecto.indicadores_impacto),
            'fecha_creacion': datetime.now(),
            'fecha_modificacion': datetime.now()
        }

    def _dict_to_proyecto(self, data: Dict[str, Any]) -> ProyectoSocial:
        """Convierte un diccionario de BD a objeto ProyectoSocial."""
        ods_vinculados = json.loads(data['ods_vinculados'])
        departamentos = json.loads(data['departamentos'])
        municipios = json.loads(data['municipios']) if data['municipios'] else []
        indicadores_impacto = json.loads(data['indicadores_impacto'])

        return ProyectoSocial(
            id=data['id'],
            nombre=data['nombre'],
            organizacion=data['organizacion'],
            descripcion=data['descripcion'],
            beneficiarios_directos=data['beneficiarios_directos'],
            beneficiarios_indirectos=data['beneficiarios_indirectos'],
            duracion_meses=data['duracion_meses'],
            presupuesto_total=data['presupuesto_total'],
            ods_vinculados=ods_vinculados,
            area_geografica=AreaGeografica(data['area_geografica']),
            poblacion_objetivo=data['poblacion_objetivo'],
            departamentos=departamentos,
            municipios=municipios,
            estado=EstadoProyecto(data['estado']),
            indicadores_impacto=indicadores_impacto
        )

    def crear_proyecto(self, proyecto: ProyectoSocial) -> bool:
        """Crea un nuevo proyecto en la base de datos."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Verificar si ya existe
            cursor.execute("SELECT id FROM proyectos WHERE id = %s", (proyecto.id,))
            if cursor.fetchone():
                return False

            # Insertar proyecto
            data = self._proyecto_to_dict(proyecto)
            cursor.execute("""
                INSERT INTO proyectos (
                    id, nombre, organizacion, descripcion,
                    beneficiarios_directos, beneficiarios_indirectos,
                    duracion_meses, presupuesto_total, ods_vinculados,
                    area_geografica, poblacion_objetivo, departamentos,
                    municipios, estado, indicadores_impacto,
                    fecha_creacion, fecha_modificacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['id'], data['nombre'], data['organizacion'], data['descripcion'],
                data['beneficiarios_directos'], data['beneficiarios_indirectos'],
                data['duracion_meses'], data['presupuesto_total'], data['ods_vinculados'],
                data['area_geografica'], data['poblacion_objetivo'], data['departamentos'],
                data['municipios'], data['estado'], data['indicadores_impacto'],
                data['fecha_creacion'], data['fecha_modificacion']
            ))

            # Registrar en historial
            cursor.execute("""
                INSERT INTO historial_cambios (proyecto_id, accion, fecha, cambios)
                VALUES (%s, %s, %s, %s)
            """, (proyecto.id, 'CREATE', datetime.now(), json.dumps(data, default=str)))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error al crear proyecto: {e}")
            return False

    def obtener_proyecto(self, proyecto_id: str) -> Optional[ProyectoSocial]:
        """Obtiene un proyecto por su ID."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM proyectos WHERE id = %s", (proyecto_id,))
        row = cursor.fetchone()

        if row:
            return self._dict_to_proyecto(dict(row))
        return None

    def obtener_todos_proyectos(self) -> List[ProyectoSocial]:
        """Obtiene todos los proyectos de la base de datos."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM proyectos ORDER BY fecha_creacion DESC")
        rows = cursor.fetchall()

        return [self._dict_to_proyecto(dict(row)) for row in rows]

    def actualizar_proyecto(self, proyecto: ProyectoSocial) -> bool:
        """Actualiza un proyecto existente."""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Verificar si existe
            cursor.execute("SELECT * FROM proyectos WHERE id = %s", (proyecto.id,))
            if not cursor.fetchone():
                return False

            # Actualizar proyecto
            data = self._proyecto_to_dict(proyecto)
            data['fecha_modificacion'] = datetime.now()

            cursor.execute("""
                UPDATE proyectos SET
                    nombre = %s, organizacion = %s, descripcion = %s,
                    beneficiarios_directos = %s, beneficiarios_indirectos = %s,
                    duracion_meses = %s, presupuesto_total = %s, ods_vinculados = %s,
                    area_geografica = %s, poblacion_objetivo = %s, departamentos = %s,
                    municipios = %s, estado = %s, indicadores_impacto = %s,
                    fecha_modificacion = %s
                WHERE id = %s
            """, (
                data['nombre'], data['organizacion'], data['descripcion'],
                data['beneficiarios_directos'], data['beneficiarios_indirectos'],
                data['duracion_meses'], data['presupuesto_total'], data['ods_vinculados'],
                data['area_geografica'], data['poblacion_objetivo'], data['departamentos'],
                data['municipios'], data['estado'], data['indicadores_impacto'],
                data['fecha_modificacion'], proyecto.id
            ))

            # Registrar en historial
            cursor.execute("""
                INSERT INTO historial_cambios (proyecto_id, accion, fecha, cambios)
                VALUES (%s, %s, %s, %s)
            """, (proyecto.id, 'UPDATE', datetime.now(), json.dumps(data, default=str)))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error al actualizar proyecto: {e}")
            return False

    def eliminar_proyecto(self, proyecto_id: str) -> bool:
        """Elimina un proyecto de la base de datos."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # Obtener proyecto antes de eliminar
            cursor.execute("SELECT * FROM proyectos WHERE id = %s", (proyecto_id,))
            proyecto_data = cursor.fetchone()
            if not proyecto_data:
                return False

            # Registrar en historial antes de eliminar
            cursor.execute("""
                INSERT INTO historial_cambios (proyecto_id, accion, fecha, cambios)
                VALUES (%s, %s, %s, %s)
            """, (proyecto_id, 'DELETE', datetime.now(), json.dumps(dict(proyecto_data), default=str)))

            # Eliminar proyecto
            cursor.execute("DELETE FROM proyectos WHERE id = %s", (proyecto_id,))

            conn.commit()
            return True

        except Exception as e:
            conn.rollback()
            print(f"Error al eliminar proyecto: {e}")
            return False

    def buscar_proyectos(self,
                         texto: Optional[str] = None,
                         organizacion: Optional[str] = None,
                         departamento: Optional[str] = None,
                         ods: Optional[List[str]] = None,
                         area_geografica: Optional[str] = None,
                         estado: Optional[str] = None) -> List[ProyectoSocial]:
        """Busca proyectos según criterios específicos."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = "SELECT * FROM proyectos WHERE 1=1"
        params = []

        if texto:
            query += " AND (nombre ILIKE %s OR id ILIKE %s OR organizacion ILIKE %s)"
            pattern = f"%{texto}%"
            params.extend([pattern, pattern, pattern])

        if organizacion:
            query += " AND organizacion = %s"
            params.append(organizacion)

        if departamento:
            query += " AND departamentos ILIKE %s"
            params.append(f"%{departamento}%")

        if ods:
            for ods_item in ods:
                query += " AND ods_vinculados ILIKE %s"
                params.append(f"%{ods_item}%")

        if area_geografica:
            query += " AND area_geografica = %s"
            params.append(area_geografica)

        if estado:
            query += " AND estado = %s"
            params.append(estado)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [self._dict_to_proyecto(dict(row)) for row in rows]

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales de los proyectos."""
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                COUNT(*) as total_proyectos,
                SUM(beneficiarios_directos) as total_beneficiarios_directos,
                SUM(beneficiarios_indirectos) as total_beneficiarios_indirectos,
                SUM(presupuesto_total) as presupuesto_total,
                AVG(presupuesto_total) as presupuesto_promedio,
                COUNT(DISTINCT organizacion) as total_organizaciones
            FROM proyectos
        """)

        row = cursor.fetchone()

        return {
            'total_proyectos': row['total_proyectos'] or 0,
            'total_beneficiarios_directos': row['total_beneficiarios_directos'] or 0,
            'total_beneficiarios_indirectos': row['total_beneficiarios_indirectos'] or 0,
            'presupuesto_total': float(row['presupuesto_total']) if row['presupuesto_total'] else 0,
            'presupuesto_promedio': float(row['presupuesto_promedio']) if row['presupuesto_promedio'] else 0,
            'total_organizaciones': row['total_organizaciones'] or 0
        }

    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos."""
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.connection = None
