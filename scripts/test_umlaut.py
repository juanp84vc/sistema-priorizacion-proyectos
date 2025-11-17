"""Test umlaut normalization"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.matriz_pdet_repository import MatrizPDETRepository

repo = MatrizPDETRepository()

print("="*60)
print("TEST: MAGÜÍ (Ü)")
print("="*60)

# Test normalización
tests = ["MAGÜÍ", "MAGUI"]
for test in tests:
    norm = repo.normalizar_texto(test)
    print(f"  '{test}' → '{norm}'")

# Test detección
print("\nTest detección PDET:")
tests_pdet = [
    ("MAGÜÍ", "NARIÑO"),
    ("MAGUI", "NARIÑO")
]

for mun, dept in tests_pdet:
    es_pdet = repo.es_municipio_pdet(mun, dept)
    print(f"  {mun} ({dept}) → PDET: {es_pdet}")

print("="*60)
