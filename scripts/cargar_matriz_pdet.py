"""
Script de carga de matriz PDET/ZOMAC desde archivo Excel.

Carga datos oficiales de priorización sectorial Obras por Impuestos
para 362 municipios PDET/ZOMAC en Colombia.

Uso:
    python3 scripts/cargar_matriz_pdet.py
"""
import pandas as pd
import sqlite3
from pathlib import Path
import sys

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.matriz_pdet_repository import MatrizPDETRepository


def cargar_matriz_desde_excel(
    excel_path: str = "/mnt/user-data/uploads/datos_sectoriales.xlsx",
    db_path: str = None
):
    """
    Carga matriz PDET/ZOMAC desde Excel a SQLite.

    Args:
        excel_path: Ruta al archivo Excel con datos sectoriales
        db_path: Ruta a base de datos SQLite (None = default)
    """

    print("=" * 80)
    print("🔄 CARGANDO MATRIZ PDET/ZOMAC - OBRAS POR IMPUESTOS")
    print("=" * 80)

    # Determinar ruta base de datos
    if db_path is None:
        project_root = Path(__file__).parent.parent
        db_path = str(project_root / "data" / "proyectos.db")

    # Verificar que directorio data existe
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📂 Configuración:")
    print(f"   Excel: {excel_path}")
    print(f"   Base de datos: {db_path}")

    # 1. Leer Excel
    print(f"\n📖 Leyendo archivo Excel...")
    try:
        df = pd.read_excel(excel_path, header=0)
        print(f"   ✅ Archivo leído correctamente")
    except FileNotFoundError:
        print(f"   ❌ ERROR: Archivo no encontrado: {excel_path}")
        print(f"\n💡 Asegúrate de que el archivo existe en la ruta especificada.")
        return False
    except Exception as e:
        print(f"   ❌ ERROR al leer Excel: {e}")
        return False

    # 2. Limpiar y normalizar columnas
    print(f"\n🧹 Limpiando datos...")

    # Renombrar columnas a nombres estándar
    df.columns = [
        'Departamento', 'Municipio', 'Educación', 'Salud',
        'Alcantarillado', 'Vía', 'Energía', 'Banda_Ancha',
        'Riesgo_Amb', 'Infra_Rural', 'Cultura', 'Deporte'
    ]

    # Eliminar fila de headers duplicados si existe
    df = df[df['Departamento'] != 'Departamento']

    # Convertir puntajes a enteros
    columnas_puntajes = [
        'Educación', 'Salud', 'Alcantarillado', 'Vía', 'Energía',
        'Banda_Ancha', 'Riesgo_Amb', 'Infra_Rural', 'Cultura', 'Deporte'
    ]

    for col in columnas_puntajes:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Limpiar nombres
    df['Departamento'] = df['Departamento'].str.upper().str.strip()
    df['Municipio'] = df['Municipio'].str.upper().str.strip()

    # Eliminar filas sin datos
    df = df.dropna(subset=['Departamento', 'Municipio'])

    print(f"   ✅ Datos limpios")
    print(f"   📊 Registros: {len(df)}")
    print(f"   🏛️  Departamentos únicos: {df['Departamento'].nunique()}")
    print(f"   🏘️  Municipios únicos: {df['Municipio'].nunique()}")

    # 3. Verificar datos
    print(f"\n🔍 Verificando calidad de datos...")

    # Verificar rangos de puntajes
    errores_rango = 0
    for col in columnas_puntajes:
        fuera_rango = df[(df[col] < 1) | (df[col] > 10)]
        if len(fuera_rango) > 0:
            errores_rango += len(fuera_rango)
            print(f"   ⚠️  {len(fuera_rango)} valores fuera de rango 1-10 en {col}")

    if errores_rango == 0:
        print(f"   ✅ Todos los puntajes en rango 1-10")
    else:
        print(f"   ⚠️  Total errores de rango: {errores_rango}")

    # 4. Conectar a base de datos
    print(f"\n💾 Conectando a base de datos...")
    try:
        repo = MatrizPDETRepository(db_path)
        print(f"   ✅ Conexión establecida")
    except Exception as e:
        print(f"   ❌ ERROR al conectar: {e}")
        return False

    # 5. Limpiar tabla existente
    print(f"\n🗑️  Limpiando datos anteriores...")
    try:
        repo.vaciar_tabla()
        print(f"   ✅ Tabla limpiada")
    except Exception as e:
        print(f"   ⚠️  Error al limpiar: {e}")

    # 6. Insertar datos
    print(f"\n📥 Insertando datos...")
    insertados = 0
    errores = 0
    duplicados = 0

    conn = sqlite3.connect(db_path)

    for idx, row in df.iterrows():
        try:
            conn.execute("""
                INSERT INTO matriz_pdet_zomac (
                    departamento, municipio, educacion, salud, alcantarillado,
                    via, energia, banda_ancha, riesgo_ambiental,
                    infraestructura_rural, cultura, deporte
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['Departamento'],
                row['Municipio'],
                int(row['Educación']),
                int(row['Salud']),
                int(row['Alcantarillado']),
                int(row['Vía']),
                int(row['Energía']),
                int(row['Banda_Ancha']),
                int(row['Riesgo_Amb']),
                int(row['Infra_Rural']),
                int(row['Cultura']),
                int(row['Deporte'])
            ))
            insertados += 1

            # Mostrar progreso cada 50 registros
            if insertados % 50 == 0:
                print(f"   📌 Progreso: {insertados} registros...")

        except sqlite3.IntegrityError:
            # Municipio duplicado
            duplicados += 1
        except Exception as e:
            errores += 1
            print(f"   ⚠️  Error en {row['Municipio']}: {e}")

    conn.commit()
    conn.close()

    print(f"\n✅ CARGA COMPLETADA")
    print(f"   ✔️  Insertados: {insertados}")
    if duplicados > 0:
        print(f"   ⚠️  Duplicados ignorados: {duplicados}")
    if errores > 0:
        print(f"   ❌ Errores: {errores}")

    # 7. Verificación final
    print(f"\n🔍 Verificación final...")
    total_db = repo.get_total_municipios()
    deptos_db = len(repo.get_departamentos())

    print(f"   📊 Registros en BD: {total_db}")
    print(f"   🏛️  Departamentos: {deptos_db}")

    if total_db == insertados:
        print(f"   ✅ ÉXITO: Todos los registros verificados")
    else:
        print(f"   ⚠️  ADVERTENCIA: Discrepancia detectada")
        print(f"      Insertados: {insertados}, En BD: {total_db}")

    # 8. Mostrar ejemplo
    print(f"\n📝 Ejemplo de datos cargados:")
    print(f"   Buscando ABEJORRAL, Antioquia...")

    registro = repo.get_municipio("ANTIOQUIA", "ABEJORRAL")
    if registro:
        print(f"   ✅ Encontrado: {registro}")
        sectores = registro.get_sectores_ordenados()
        print(f"\n   🎯 Top 3 sectores prioritarios:")
        for i, (sector, puntaje) in enumerate(sectores[:3], 1):
            print(f"      {i}. {sector}: {puntaje}/10")
    else:
        print(f"   ⚠️  No encontrado (verificar datos)")

    print("\n" + "=" * 80)
    print("✅ PROCESO FINALIZADO")
    print("=" * 80)

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Carga matriz PDET/ZOMAC desde Excel'
    )
    parser.add_argument(
        '--excel',
        default='/mnt/user-data/uploads/datos_sectoriales.xlsx',
        help='Ruta al archivo Excel'
    )
    parser.add_argument(
        '--db',
        default=None,
        help='Ruta a base de datos SQLite (default: data/proyectos.db)'
    )

    args = parser.parse_args()

    exito = cargar_matriz_desde_excel(
        excel_path=args.excel,
        db_path=args.db
    )

    sys.exit(0 if exito else 1)
