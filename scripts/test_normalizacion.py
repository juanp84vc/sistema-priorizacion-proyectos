"""Test de función de normalización"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.matriz_pdet_repository import MatrizPDETRepository

repo = MatrizPDETRepository()

print("="*60)
print("TEST NORMALIZACIÓN")
print("="*60)

# Test de normalización
tests = [
    "AGUSTÍN CODAZZI",
    "Agustín Codazzi",
    "AGUSTIN CODAZZI",
    "Agustin Codazzi",
    "agustín codazzi",
    "agustin codazzi"
]

print("\nNormalización de texto:")
for test in tests:
    normalizado = repo.normalizar_texto(test)
    print(f"  '{test}' → '{normalizado}'")

# Test directo en BD
print("\nQuery directo a BD (con normalización SQL):")
import sqlite3
conn = sqlite3.connect('data/proyectos.db')
cursor = conn.cursor()

# Ver qué hay realmente en la BD
query_raw = """
SELECT municipio, departamento
FROM matriz_pdet_zomac
WHERE municipio LIKE '%AGUST%'
"""
cursor.execute(query_raw)
print("  Registros en BD:")
for row in cursor.fetchall():
    print(f"    municipio='{row[0]}', departamento='{row[1]}'")

# Probar normalización SQL
municipio_norm = repo.normalizar_texto("Agustín Codazzi")
departamento_norm = repo.normalizar_texto("CESAR")

print(f"\n  Buscando con:")
print(f"    municipio_norm = '{municipio_norm}'")
print(f"    departamento_norm = '{departamento_norm}'")

query_test = """
SELECT
    municipio,
    departamento,
    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
              UPPER(municipio),
              'Á', 'A'), 'É', 'E'), 'Í', 'I'), 'Ó', 'O'), 'Ú', 'U'),
            'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u'
    ) as municipio_normalizado,
    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
              UPPER(departamento),
              'Á', 'A'), 'É', 'E'), 'Í', 'I'), 'Ó', 'O'), 'Ú', 'U'),
            'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u'
    ) as departamento_normalizado
FROM matriz_pdet_zomac
WHERE REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
              UPPER(municipio),
              'Á', 'A'), 'É', 'E'), 'Í', 'I'), 'Ó', 'O'), 'Ú', 'U'),
            'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u'
) = ?
AND REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
            REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
              UPPER(departamento),
              'Á', 'A'), 'É', 'E'), 'Í', 'I'), 'Ó', 'O'), 'Ú', 'U'),
            'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u'
) = ?
"""

cursor.execute(query_test, (municipio_norm, departamento_norm))
resultados = cursor.fetchall()

print(f"\n  Resultados encontrados: {len(resultados)}")
for row in resultados:
    print(f"    municipio='{row[0]}', departamento='{row[1]}'")
    print(f"    municipio_norm='{row[2]}', departamento_norm='{row[3]}'")

conn.close()

print("\n" + "="*60)
