#!/usr/bin/env python3
"""
Script de migración de BD para Arquitectura C.
Agrega columnas faltantes a la tabla proyectos.

Ejecutar con:
    python3 scripts/migrar_bd_arquitectura_c.py
"""

import sqlite3
import os
from datetime import datetime
import shutil

DB_PATH = "data/proyectos.db"

def backup_database():
    """Crea backup antes de migrar"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"data/proyectos_backup_{timestamp}.db"

    if os.path.exists(DB_PATH):
        shutil.copy(DB_PATH, backup_path)
        print(f"✅ Backup creado: {backup_path}")
        return backup_path
    else:
        print(f"⚠️ No existe {DB_PATH}, se creará nueva base de datos")
        return None

def get_existing_columns():
    """Obtiene columnas existentes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(proyectos)")
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()
    return columns

def migrate():
    """Ejecuta migración"""

    print("="*60)
    print("MIGRACIÓN BD - ARQUITECTURA C")
    print("="*60)

    # Backup primero
    backup_database()

    # Columnas a agregar con valores por defecto
    nuevas_columnas = [
        # Campos PDET/Probabilidad
        ("sectores", "TEXT DEFAULT '[]'"),
        ("puntajes_pdet", "TEXT DEFAULT '{}'"),
        ("tiene_municipios_pdet", "INTEGER DEFAULT 0"),
        ("puntaje_sectorial_max", "INTEGER DEFAULT 0"),

        # Campos SROI adicionales
        ("observaciones_sroi", "TEXT DEFAULT ''"),
        ("nivel_confianza_sroi", "TEXT DEFAULT ''"),
        ("fecha_calculo_sroi", "TEXT DEFAULT ''"),
        ("metodologia_sroi", "TEXT DEFAULT ''"),

        # Campos Stakeholders
        ("pertinencia_operacional", "INTEGER DEFAULT 3"),
        ("mejora_relacionamiento", "INTEGER DEFAULT 3"),
        ("stakeholders_involucrados", "TEXT DEFAULT '[]'"),
        ("en_corredor_transmision", "INTEGER DEFAULT 0"),
        ("observaciones_stakeholders", "TEXT DEFAULT ''"),

        # Campos Riesgos (4 tipos × 2 dimensiones)
        ("riesgo_tecnico_probabilidad", "INTEGER DEFAULT 2"),
        ("riesgo_tecnico_impacto", "INTEGER DEFAULT 2"),
        ("riesgo_social_probabilidad", "INTEGER DEFAULT 2"),
        ("riesgo_social_impacto", "INTEGER DEFAULT 2"),
        ("riesgo_financiero_probabilidad", "INTEGER DEFAULT 2"),
        ("riesgo_financiero_impacto", "INTEGER DEFAULT 3"),
        ("riesgo_regulatorio_probabilidad", "INTEGER DEFAULT 2"),
        ("riesgo_regulatorio_impacto", "INTEGER DEFAULT 2"),

        # Campo adicional de duración
        ("duracion_estimada_meses", "INTEGER DEFAULT 12"),
    ]

    # Obtener columnas existentes
    existentes = get_existing_columns()
    print(f"\n📊 Columnas existentes: {len(existentes)}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    agregadas = 0
    ya_existen = 0
    errores = 0

    print("\n🔄 Agregando columnas:")

    for col_name, col_type in nuevas_columnas:
        if col_name not in existentes:
            try:
                sql = f"ALTER TABLE proyectos ADD COLUMN {col_name} {col_type}"
                cursor.execute(sql)
                print(f"  ✅ Agregada: {col_name}")
                agregadas += 1
            except sqlite3.OperationalError as e:
                print(f"  ❌ Error en {col_name}: {e}")
                errores += 1
        else:
            print(f"  ⏭️  Ya existe: {col_name}")
            ya_existen += 1

    conn.commit()
    conn.close()

    print(f"\n{'='*60}")
    print("RESULTADO DE MIGRACIÓN")
    print(f"{'='*60}")
    print(f"  Columnas agregadas: {agregadas}")
    print(f"  Columnas ya existentes: {ya_existen}")
    print(f"  Errores: {errores}")
    print(f"  Total columnas antes: {len(existentes)}")
    print(f"  Total columnas ahora: {len(existentes) + agregadas}")
    print(f"{'='*60}")

    # Verificación final
    if agregadas > 0 or ya_existen > 0:
        print("\n🔍 VERIFICACIÓN FINAL:")
        nuevas_existentes = get_existing_columns()
        print(f"  Columnas en tabla: {len(nuevas_existentes)}")

        # Verificar que todas las columnas nuevas existen
        faltantes = []
        for col_name, _ in nuevas_columnas:
            if col_name not in nuevas_existentes:
                faltantes.append(col_name)

        if faltantes:
            print(f"\n  ⚠️  Columnas que faltan: {faltantes}")
        else:
            print(f"  ✅ Todas las columnas de Arquitectura C están presentes")

    return agregadas

if __name__ == "__main__":
    try:
        columnas_agregadas = migrate()
        print(f"\n✅ Migración completada exitosamente")
        print(f"   {columnas_agregadas} columnas nuevas agregadas")
    except Exception as e:
        print(f"\n❌ Error durante migración: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
