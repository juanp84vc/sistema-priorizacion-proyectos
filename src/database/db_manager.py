"""
Gestor de Base de Datos para el Sistema de Priorización de Proyectos.
Maneja la persistencia de proyectos usando SQLite.
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys

# Agregar src al path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto


class DatabaseManager:
    """Gestor de la base de datos SQLite para proyectos sociales."""

    def __init__(self, db_path: str = "data/proyectos.db"):
        """
        Inicializa el gestor de base de datos.

        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        # Crear directorio data si no existe
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.connection = None
        self._initialize_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión a la base de datos."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Para acceder por nombre de columna
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
                fecha_creacion TEXT NOT NULL,
                fecha_modificacion TEXT NOT NULL
            )
        """)

        # Tabla de historial de cambios (opcional, para auditoría)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_cambios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proyecto_id TEXT NOT NULL,
                accion TEXT NOT NULL,
                usuario TEXT,
                fecha TEXT NOT NULL,
                cambios TEXT,
                FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
            )
        """)

        conn.commit()

    def _proyecto_to_dict(self, proyecto: ProyectoSocial) -> Dict[str, Any]:
        """
        Convierte un objeto ProyectoSocial a diccionario para guardar en BD.

        Args:
            proyecto: Objeto ProyectoSocial

        Returns:
            Diccionario con los datos del proyecto
        """
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
            'fecha_creacion': datetime.now().isoformat(),
            'fecha_modificacion': datetime.now().isoformat()
        }

    def _dict_to_proyecto(self, data: Dict[str, Any]) -> ProyectoSocial:
        """
        Convierte un diccionario de BD a objeto ProyectoSocial.

        Args:
            data: Diccionario con datos del proyecto

        Returns:
            Objeto ProyectoSocial
        """
        # Deserializar campos JSON
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
        """
        Crea un nuevo proyecto en la base de datos.

        Args:
            proyecto: Objeto ProyectoSocial a guardar

        Returns:
            True si se guardó correctamente, False si ya existe
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Verificar si ya existe
            cursor.execute("SELECT id FROM proyectos WHERE id = ?", (proyecto.id,))
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                VALUES (?, ?, ?, ?)
            """, (proyecto.id, 'CREATE', datetime.now().isoformat(), json.dumps(data)))

            conn.commit()
            return True

        except sqlite3.IntegrityError:
            return False

    def obtener_proyecto(self, proyecto_id: str) -> Optional[ProyectoSocial]:
        """
        Obtiene un proyecto por su ID.

        Args:
            proyecto_id: ID del proyecto

        Returns:
            Objeto ProyectoSocial o None si no existe
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM proyectos WHERE id = ?", (proyecto_id,))
        row = cursor.fetchone()

        if row:
            return self._dict_to_proyecto(dict(row))
        return None

    def obtener_todos_proyectos(self) -> List[ProyectoSocial]:
        """
        Obtiene todos los proyectos de la base de datos.

        Returns:
            Lista de objetos ProyectoSocial
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM proyectos ORDER BY fecha_creacion DESC")
        rows = cursor.fetchall()

        return [self._dict_to_proyecto(dict(row)) for row in rows]

    def actualizar_proyecto(self, proyecto: ProyectoSocial) -> bool:
        """
        Actualiza un proyecto existente.

        Args:
            proyecto: Objeto ProyectoSocial con los datos actualizados

        Returns:
            True si se actualizó correctamente, False si no existe
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Verificar si existe
        cursor.execute("SELECT * FROM proyectos WHERE id = ?", (proyecto.id,))
        if not cursor.fetchone():
            return False

        # Actualizar proyecto
        data = self._proyecto_to_dict(proyecto)
        data['fecha_modificacion'] = datetime.now().isoformat()

        cursor.execute("""
            UPDATE proyectos SET
                nombre = ?, organizacion = ?, descripcion = ?,
                beneficiarios_directos = ?, beneficiarios_indirectos = ?,
                duracion_meses = ?, presupuesto_total = ?, ods_vinculados = ?,
                area_geografica = ?, poblacion_objetivo = ?, departamentos = ?,
                municipios = ?, estado = ?, indicadores_impacto = ?,
                fecha_modificacion = ?
            WHERE id = ?
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
            VALUES (?, ?, ?, ?)
        """, (proyecto.id, 'UPDATE', datetime.now().isoformat(), json.dumps(data)))

        conn.commit()
        return True

    def eliminar_proyecto(self, proyecto_id: str) -> bool:
        """
        Elimina un proyecto de la base de datos.

        Args:
            proyecto_id: ID del proyecto a eliminar

        Returns:
            True si se eliminó correctamente, False si no existe
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Verificar si existe
        cursor.execute("SELECT * FROM proyectos WHERE id = ?", (proyecto_id,))
        proyecto_data = cursor.fetchone()
        if not proyecto_data:
            return False

        # Registrar en historial antes de eliminar
        cursor.execute("""
            INSERT INTO historial_cambios (proyecto_id, accion, fecha, cambios)
            VALUES (?, ?, ?, ?)
        """, (proyecto_id, 'DELETE', datetime.now().isoformat(), json.dumps(dict(proyecto_data))))

        # Eliminar proyecto
        cursor.execute("DELETE FROM proyectos WHERE id = ?", (proyecto_id,))

        conn.commit()
        return True

    def buscar_proyectos(self,
                         texto: Optional[str] = None,
                         organizacion: Optional[str] = None,
                         departamento: Optional[str] = None,
                         ods: Optional[List[str]] = None,
                         area_geografica: Optional[str] = None,
                         estado: Optional[str] = None) -> List[ProyectoSocial]:
        """
        Busca proyectos según criterios específicos.

        Args:
            texto: Texto a buscar en nombre, ID u organización
            organizacion: Nombre de la organización
            departamento: Departamento específico
            ods: Lista de ODS
            area_geografica: Área geográfica
            estado: Estado del proyecto

        Returns:
            Lista de proyectos que coinciden con los criterios
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM proyectos WHERE 1=1"
        params = []

        if texto:
            query += " AND (nombre LIKE ? OR id LIKE ? OR organizacion LIKE ?)"
            pattern = f"%{texto}%"
            params.extend([pattern, pattern, pattern])

        if organizacion:
            query += " AND organizacion = ?"
            params.append(organizacion)

        if departamento:
            query += " AND departamentos LIKE ?"
            params.append(f"%{departamento}%")

        if ods:
            for ods_item in ods:
                query += " AND ods_vinculados LIKE ?"
                params.append(f"%{ods_item}%")

        if area_geografica:
            query += " AND area_geografica = ?"
            params.append(area_geografica)

        if estado:
            query += " AND estado = ?"
            params.append(estado)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [self._dict_to_proyecto(dict(row)) for row in rows]

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de los proyectos.

        Returns:
            Diccionario con estadísticas
        """
        conn = self._get_connection()
        cursor = conn.cursor()

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
            'presupuesto_total': row['presupuesto_total'] or 0,
            'presupuesto_promedio': row['presupuesto_promedio'] or 0,
            'total_organizaciones': row['total_organizaciones'] or 0
        }

    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def crear_backup(self, backup_path: str) -> bool:
        """
        Crea una copia de seguridad de la base de datos.

        Args:
            backup_path: Ruta donde guardar el backup

        Returns:
            True si se creó el backup correctamente
        """
        try:
            import shutil
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Error al crear backup: {e}")
            return False

    def restaurar_backup(self, backup_path: str) -> bool:
        """
        Restaura la base de datos desde un backup.

        Args:
            backup_path: Ruta del backup a restaurar

        Returns:
            True si se restauró correctamente
        """
        try:
            import shutil
            if Path(backup_path).exists():
                self.cerrar_conexion()
                shutil.copy2(backup_path, self.db_path)
                self._get_connection()  # Reconectar
                return True
            return False
        except Exception as e:
            print(f"Error al restaurar backup: {e}")
            return False


# Singleton global para la aplicación
_db_manager_instance = None

def get_db_manager(db_path: str = "data/proyectos.db"):
    """
    Obtiene la instancia global del gestor de base de datos (Singleton).
    Detecta automáticamente si usar PostgreSQL (producción) o SQLite (local).

    Args:
        db_path: Ruta al archivo de base de datos SQLite (solo para local)

    Returns:
        Instancia de DatabaseManager o PostgreSQLManager
    """
    global _db_manager_instance
    if _db_manager_instance is None:
        # Intentar usar PostgreSQL si está disponible (Streamlit Cloud)
        try:
            import streamlit as st
            if 'postgres' in st.secrets and 'connection_string' in st.secrets['postgres']:
                from database.postgres_manager import PostgreSQLManager
                _db_manager_instance = PostgreSQLManager(st.secrets['postgres']['connection_string'])
                print("✅ Usando PostgreSQL (producción)")
                return _db_manager_instance
        except:
            pass

        # Usar SQLite por defecto (local)
        _db_manager_instance = DatabaseManager(db_path)
        print("✅ Usando SQLite (local)")

    return _db_manager_instance
