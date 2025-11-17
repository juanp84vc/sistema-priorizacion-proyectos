"""Verificar detección PDET para TODOS los municipios"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.matriz_pdet_repository import MatrizPDETRepository

repo = MatrizPDETRepository()

print("="*60)
print("VERIFICACIÓN MASIVA DETECCIÓN PDET")
print("="*60)

# Obtener todos los departamentos
departamentos = repo.get_departamentos()

total_municipios = 0
errores = []

for dpto in departamentos:
    municipios = repo.get_municipios_por_departamento(dpto)

    for mun in municipios:
        total_municipios += 1

        # Verificar detección
        es_pdet = repo.es_municipio_pdet(mun, dpto)

        if not es_pdet:
            errores.append(f"{mun} ({dpto}) - No detectado como PDET")

        # Verificar puntajes si es PDET
        if es_pdet:
            puntajes = repo.get_puntajes_sectores(mun, dpto)
            if not puntajes or len(puntajes) != 10:
                errores.append(f"{mun} ({dpto}) - Puntajes incompletos: {len(puntajes)}/10")

print(f"\nTotal municipios verificados: {total_municipios}")
print(f"Errores encontrados: {len(errores)}")

if errores:
    print("\n⚠️  ERRORES:")
    for error in errores[:20]:  # Primeros 20
        print(f"  - {error}")
    if len(errores) > 20:
        print(f"  ... y {len(errores) - 20} más")
else:
    print("\n✅ TODOS LOS MUNICIPIOS DETECTADOS CORRECTAMENTE")

print("="*60)
