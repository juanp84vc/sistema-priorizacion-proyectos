"""
Script manual para crear tabla de proyectos en Supabase PostgreSQL.
Usa POOLER connection (la que funciona desde Streamlit Cloud).
"""
import psycopg2

# DIRECT CONNECTION (para ejecutar desde local)
# En Streamlit Cloud se usa pooler, pero desde local usamos direct
CONNECTION_STRING = "postgresql://postgres:Inteligenciaa25*@db.xgqljxgjtscyczbhybqt.supabase.co:5432/postgres"

def crear_tablas_proyectos():
    """Crea las tablas para proyectos en PostgreSQL."""
    print("🔗 Conectando a PostgreSQL (pooler)...")
    conn = psycopg2.connect(CONNECTION_STRING)

    try:
        cursor = conn.cursor()
        print("✅ Conexión establecida")

        # Tabla principal de proyectos
        print("📝 Creando tabla proyectos...")
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
        print("✅ Tabla proyectos creada")

        # Tabla de historial de cambios
        print("📝 Creando tabla historial_cambios...")
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
        print("✅ Tabla historial_cambios creada")

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
    crear_tablas_proyectos()
