"""Test para municipios con Ñ"""

import sys
from pathlib import Path
import sqlite3

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.matriz_pdet_repository import MatrizPDETRepository

repo = MatrizPDETRepository()

print("="*60)
print("TEST: MUNICIPIOS CON Ñ")
print("="*60)

# Ver qué hay en BD
conn = sqlite3.connect('data/proyectos.db')
cursor = conn.cursor()

query = """
SELECT municipio, departamento
FROM matriz_pdet_zomac
WHERE municipio LIKE '%PEÑON%' OR municipio LIKE '%PEÑÓN%'
   OR municipio LIKE '%NARIÑO%' OR municipio LIKE '%NARINO%'
ORDER BY municipio
"""

cursor.execute(query)
print("\nRegistros con PEÑON o NARIÑO en BD:")
for row in cursor.fetchall():
    print(f"  municipio='{row[0]}', departamento='{row[1]}'")

conn.close()

# Test normalización
print("\nTest de normalización:")
tests = ["EL PEÑÓN", "EL PENON", "NARIÑO", "NARINO", "PUERTO NARIÑO", "PUERTO NARINO"]
for test in tests:
    norm = repo.normalizar_texto(test)
    print(f"  '{test}' → '{norm}'")

# Test detección
print("\nTest detección PDET:")
tests_pdet = [
    ("EL PEÑÓN", "CUNDINAMARCA"),
    ("EL PENON", "CUNDINAMARCA"),
    ("NARIÑO", "ANTIOQUIA"),
    ("NARINO", "ANTIOQUIA"),
    ("PUERTO NARIÑO", "AMAZONAS"),
    ("PUERTO NARINO", "AMAZONAS")
]

for mun, dept in tests_pdet:
    es_pdet = repo.es_municipio_pdet(mun, dept)
    print(f"  {mun} ({dept}) → PDET: {es_pdet}")

print("="*60)
