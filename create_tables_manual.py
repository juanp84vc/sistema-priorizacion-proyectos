"""
Script manual para crear tablas en Supabase PostgreSQL.
Ejecutar localmente para inicializar la base de datos.
"""
import psycopg2
from psycopg2.extras import RealDictCursor

# Cadena de conexión de Supabase
# Usar conexión directa sin pooler
CONNECTION_STRING = "postgresql://postgres:Inteligenciaa25*@db.xgqljxgjtscyczbhybqt.supabase.co:5432/postgres"

def crear_tablas_historial():
    """Crea las tablas para el Historial IA en PostgreSQL."""
    print("🔗 Conectando a PostgreSQL...")
    conn = psycopg2.connect(CONNECTION_STRING)

    try:
        cursor = conn.cursor()
        print("✅ Conexión establecida")

        # Tabla principal de consultas
        print("📝 Creando tabla consultas_ia...")
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
        print("✅ Tabla consultas_ia creada")

        # Índices para búsquedas rápidas
        print("📝 Creando índices...")
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
        print("✅ Índices creados")

        conn.commit()
        print("\n🎉 ¡Tablas creadas exitosamente en Supabase!")

        # Verificar tablas
        print("\n📊 Verificando tablas existentes...")
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)

        tables = cursor.fetchall()
        print(f"Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    crear_tablas_historial()
