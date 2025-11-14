"""
Servicio de almacenamiento y gestión del historial de consultas IA.
Soporta SQLite (local) y PostgreSQL (producción).
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# Intentar importar streamlit para acceso a secrets
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

# Intentar importar psycopg2 para PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class HistorialIA:
    """Gestiona el almacenamiento persistente de consultas y respuestas del asistente IA."""

    def __init__(self, db_path: Optional[str] = None, connection_string: Optional[str] = None):
        """
        Inicializa el servicio de historial.
        Detecta automáticamente si usar PostgreSQL (producción) o SQLite (local).

        Args:
            db_path: Ruta a la base de datos SQLite (solo para local)
            connection_string: Cadena de conexión PostgreSQL (opcional)
        """
        # Determinar si usar PostgreSQL o SQLite
        self.use_postgres = False
        self.connection_string = connection_string

        # Intentar usar PostgreSQL si está disponible en Streamlit secrets
        if connection_string is None and STREAMLIT_AVAILABLE:
            try:
                if 'postgres' in st.secrets and 'connection_string_historial' in st.secrets['postgres']:
                    self.connection_string = st.secrets['postgres']['connection_string_historial']
                    self.use_postgres = True
            except:
                pass

        if self.connection_string:
            self.use_postgres = True

        if self.use_postgres and not POSTGRES_AVAILABLE:
            print("⚠️ PostgreSQL configurado pero psycopg2 no disponible, usando SQLite")
            self.use_postgres = False

        # Configurar base de datos según tipo
        if self.use_postgres:
            self.conn_pool = None
            print("✅ HistorialIA usando PostgreSQL (producción)")
            self._inicializar_db_postgres()
        else:
            # SQLite para local
            if db_path is None:
                data_dir = Path(__file__).parent.parent.parent / 'data'
                data_dir.mkdir(exist_ok=True)
                db_path = data_dir / 'historial_ia.db'
            self.db_path = str(db_path)
            print("✅ HistorialIA usando SQLite (local)")
            self._inicializar_db_sqlite()

    def _get_postgres_connection(self):
        """Obtiene una conexión PostgreSQL."""
        return psycopg2.connect(self.connection_string)

    def _inicializar_db_postgres(self):
        """Crea las tablas necesarias en PostgreSQL si no existen."""
        conn = self._get_postgres_connection()
        try:
            cursor = conn.cursor()

            # Tabla principal de consultas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS consultas_ia (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    proyecto_id TEXT,
                    proyecto_nombre TEXT,
                    tipo_analisis TEXT NOT NULL,
                    pregunta TEXT NOT NULL,
                    respuesta TEXT NOT NULL,
                    llm_provider TEXT,
                    llm_model TEXT,
                    usuario TEXT,
                    metadata TEXT
                )
            ''')

            # Índices para búsquedas rápidas
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_proyecto_id
                ON consultas_ia(proyecto_id)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON consultas_ia(timestamp DESC)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_tipo_analisis
                ON consultas_ia(tipo_analisis)
            ''')

            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def _inicializar_db_sqlite(self):
        """Crea las tablas necesarias en SQLite si no existen."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla principal de consultas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consultas_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                proyecto_id TEXT,
                proyecto_nombre TEXT,
                tipo_analisis TEXT NOT NULL,
                pregunta TEXT NOT NULL,
                respuesta TEXT NOT NULL,
                llm_provider TEXT,
                llm_model TEXT,
                usuario TEXT,
                metadata TEXT
            )
        ''')

        # Índices para búsquedas rápidas
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_proyecto_id
            ON consultas_ia(proyecto_id)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON consultas_ia(timestamp DESC)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tipo_analisis
            ON consultas_ia(tipo_analisis)
        ''')

        conn.commit()
        conn.close()

    def guardar_consulta(self,
                        pregunta: str,
                        respuesta: str,
                        tipo_analisis: str,
                        proyecto_id: Optional[str] = None,
                        proyecto_nombre: Optional[str] = None,
                        llm_provider: Optional[str] = None,
                        llm_model: Optional[str] = None,
                        usuario: Optional[str] = None,
                        metadata: Optional[str] = None) -> int:
        """
        Guarda una consulta y su respuesta en la base de datos.

        Args:
            pregunta: Pregunta del usuario
            respuesta: Respuesta del asistente IA
            tipo_analisis: Tipo de análisis (consulta_proyecto, consulta_cartera, etc.)
            proyecto_id: ID del proyecto (opcional)
            proyecto_nombre: Nombre del proyecto (opcional)
            llm_provider: Proveedor LLM usado (claude, openai, gemini)
            llm_model: Modelo específico usado
            usuario: Usuario que hizo la consulta (opcional)
            metadata: Información adicional en JSON (opcional)

        Returns:
            ID de la consulta guardada
        """
        if self.use_postgres:
            conn = self._get_postgres_connection()
            try:
                cursor = conn.cursor()
                timestamp = datetime.now()

                cursor.execute('''
                    INSERT INTO consultas_ia
                    (timestamp, proyecto_id, proyecto_nombre, tipo_analisis, pregunta,
                     respuesta, llm_provider, llm_model, usuario, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (timestamp, proyecto_id, proyecto_nombre, tipo_analisis, pregunta,
                      respuesta, llm_provider, llm_model, usuario, metadata))

                consulta_id = cursor.fetchone()[0]
                conn.commit()
                return consulta_id
            finally:
                cursor.close()
                conn.close()
        else:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            timestamp = datetime.now().isoformat()

            cursor.execute('''
                INSERT INTO consultas_ia
                (timestamp, proyecto_id, proyecto_nombre, tipo_analisis, pregunta,
                 respuesta, llm_provider, llm_model, usuario, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, proyecto_id, proyecto_nombre, tipo_analisis, pregunta,
                  respuesta, llm_provider, llm_model, usuario, metadata))

            consulta_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return consulta_id

    def obtener_consulta(self, consulta_id: int) -> Optional[Dict]:
        """
        Obtiene una consulta específica por su ID.

        Args:
            consulta_id: ID de la consulta

        Returns:
            Diccionario con los datos de la consulta o None si no existe
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM consultas_ia WHERE id = ?
        ''', (consulta_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def obtener_consultas_proyecto(self, proyecto_id: str,
                                   limite: int = 50) -> List[Dict]:
        """
        Obtiene todas las consultas de un proyecto específico.

        Args:
            proyecto_id: ID del proyecto
            limite: Número máximo de consultas a retornar

        Returns:
            Lista de consultas ordenadas por fecha (más reciente primero)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM consultas_ia
            WHERE proyecto_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (proyecto_id, limite))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def obtener_consultas_recientes(self, limite: int = 50,
                                    tipo_analisis: Optional[str] = None) -> List[Dict]:
        """
        Obtiene las consultas más recientes.

        Args:
            limite: Número máximo de consultas a retornar
            tipo_analisis: Filtrar por tipo de análisis (opcional)

        Returns:
            Lista de consultas ordenadas por fecha (más reciente primero)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if tipo_analisis:
            cursor.execute('''
                SELECT * FROM consultas_ia
                WHERE tipo_analisis = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (tipo_analisis, limite))
        else:
            cursor.execute('''
                SELECT * FROM consultas_ia
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limite,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def buscar_consultas(self, termino_busqueda: str, limite: int = 50) -> List[Dict]:
        """
        Busca consultas por término en pregunta o respuesta.

        Args:
            termino_busqueda: Término a buscar
            limite: Número máximo de resultados

        Returns:
            Lista de consultas que coinciden con la búsqueda
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM consultas_ia
            WHERE pregunta LIKE ? OR respuesta LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{termino_busqueda}%', f'%{termino_busqueda}%', limite))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas generales del historial.

        Returns:
            Diccionario con estadísticas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total de consultas
        cursor.execute('SELECT COUNT(*) FROM consultas_ia')
        total_consultas = cursor.fetchone()[0]

        # Consultas por tipo
        cursor.execute('''
            SELECT tipo_analisis, COUNT(*) as cantidad
            FROM consultas_ia
            GROUP BY tipo_analisis
            ORDER BY cantidad DESC
        ''')
        por_tipo = {row[0]: row[1] for row in cursor.fetchall()}

        # Proyectos más consultados
        cursor.execute('''
            SELECT proyecto_nombre, COUNT(*) as cantidad
            FROM consultas_ia
            WHERE proyecto_nombre IS NOT NULL
            GROUP BY proyecto_nombre
            ORDER BY cantidad DESC
            LIMIT 10
        ''')
        proyectos_top = [{'proyecto': row[0], 'consultas': row[1]}
                         for row in cursor.fetchall()]

        # Consultas por proveedor LLM
        cursor.execute('''
            SELECT llm_provider, COUNT(*) as cantidad
            FROM consultas_ia
            WHERE llm_provider IS NOT NULL
            GROUP BY llm_provider
        ''')
        por_llm = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            'total_consultas': total_consultas,
            'por_tipo': por_tipo,
            'proyectos_top': proyectos_top,
            'por_llm': por_llm
        }

    def eliminar_consulta(self, consulta_id: int) -> bool:
        """
        Elimina una consulta específica.

        Args:
            consulta_id: ID de la consulta a eliminar

        Returns:
            True si se eliminó correctamente, False si no existía
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM consultas_ia WHERE id = ?', (consulta_id,))
        eliminados = cursor.rowcount

        conn.commit()
        conn.close()

        return eliminados > 0

    def limpiar_historial_antiguo(self, dias: int = 90) -> int:
        """
        Elimina consultas más antiguas que el número de días especificado.

        Args:
            dias: Número de días a mantener

        Returns:
            Número de consultas eliminadas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        fecha_limite = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_limite = fecha_limite.replace(day=fecha_limite.day - dias)

        cursor.execute('''
            DELETE FROM consultas_ia
            WHERE timestamp < ?
        ''', (fecha_limite.isoformat(),))

        eliminados = cursor.rowcount
        conn.commit()
        conn.close()

        return eliminados
