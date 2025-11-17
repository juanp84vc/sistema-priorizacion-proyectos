"""Script para debug de detección PDET - Agustín Codazzi"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.matriz_pdet_repository import MatrizPDETRepository

repo = MatrizPDETRepository()

print("="*60)
print("DEBUG: AGUSTÍN CODAZZI")
print("="*60)

# Buscar todas las variaciones posibles
variaciones = [
    "AGUSTÍN CODAZZI",
    "Agustín Codazzi",
    "AGUSTIN CODAZZI",
    "Agustin Codazzi",
    "agustín codazzi",
    "agustin codazzi"
]

print("\n1. Buscando variaciones en BD:")
for var in variaciones:
    es_pdet = repo.es_municipio_pdet(var, "CESAR")
    print(f"   '{var}' + 'CESAR' → PDET: {es_pdet}")

# Buscar en lista completa de municipios
print("\n2. Municipios de CESAR que contienen 'AGUST':")
municipios_cesar = repo.get_municipios_por_departamento("CESAR")
for mun in municipios_cesar:
    if "AGUST" in mun.upper():
        print(f"   - {mun}")
        # Verificar si es PDET
        es_pdet = repo.es_municipio_pdet(mun, "CESAR")
        print(f"     PDET: {es_pdet}")

        # Obtener puntajes
        if es_pdet:
            puntajes = repo.get_puntajes_sectores(mun, "CESAR")
            print(f"     Sectores: {len(puntajes)}")
            for sector, puntaje in puntajes.items():
                print(f"       - {sector}: {puntaje}/10")

# Listar TODOS los municipios PDET de CESAR
print("\n3. Todos los municipios PDET de CESAR:")
query = """
SELECT DISTINCT municipio
FROM matriz_pdet_zomac
WHERE departamento = 'CESAR'
ORDER BY municipio
"""
import sqlite3
conn = sqlite3.connect('data/proyectos.db')
cursor = conn.cursor()
cursor.execute(query)
municipios_pdet_cesar = cursor.fetchall()
conn.close()

for (mun,) in municipios_pdet_cesar:
    print(f"   - {mun}")

print("\n" + "="*60)
