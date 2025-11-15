#!/usr/bin/env python3
"""
Script de validación: Integración PDET/ZOMAC
Prueba end-to-end con proyecto ejemplo
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto
from criterios.probabilidad_aprobacion_pdet import ProbabilidadAprobacionCriterio
from database.matriz_pdet_repository import MatrizPDETRepository


def main():
    print("=" * 80)
    print("🧪 VALIDACIÓN END-TO-END: INTEGRACIÓN PDET/ZOMAC")
    print("=" * 80)

    # 1. Verificar matriz PDET
    print("\n📊 PASO 1: Verificar matriz PDET cargada")
    print("-" * 80)

    db_path = str(Path(__file__).parent.parent / "data" / "proyectos.db")
    repo = MatrizPDETRepository(db_path)
    total = repo.get_total_municipios()
    print(f"✓ Municipios en matriz: {total}")

    registro = repo.get_municipio("ANTIOQUIA", "ABEJORRAL")
    if registro:
        print(f"✓ Registro ABEJORRAL encontrado")
        print(f"\n  Prioridades sectoriales:")
        for sector, puntaje in registro.get_sectores_ordenados()[:5]:
            estrellas = '⭐' * puntaje
            print(f"    {sector:30s}: {puntaje:2d}/10  {estrellas}")
    else:
        print("❌ ERROR: No se encontró Abejorral")
        return False

    # 2. Crear proyecto de prueba
    print("\n\n🏗️  PASO 2: Crear proyecto de prueba")
    print("-" * 80)

    proyecto = ProyectoSocial(
        id="TEST-PDET-001",
        nombre="Mejoramiento Alcantarillado Rural Abejorral",
        organizacion="Alcaldía de Abejorral",
        descripcion="Proyecto para mejorar sistemas de alcantarillado en zona rural",

        # Ubicación
        departamentos=["ANTIOQUIA"],
        municipios=["ABEJORRAL"],
        area_geografica=AreaGeografica.RURAL,

        # Sectores (NUEVO)
        sectores=["Alcantarillado", "Infraestructura Rural"],

        # Beneficiarios
        beneficiarios_directos=2000,
        beneficiarios_indirectos=8000,
        poblacion_objetivo="Población rural de Abejorral",

        # Financiero
        presupuesto_total=500_000_000,  # $500M COP
        duracion_meses=18,

        # ODS
        ods_vinculados=["6", "11"],  # Agua limpia y saneamiento, Ciudades sostenibles

        # Impacto
        indicadores_impacto={
            'sroi': 4.2,
        },

        # Estado
        estado=EstadoProyecto.EVALUACION
    )

    print(f"✓ Proyecto creado: {proyecto.nombre}")
    print(f"  Departamento: {proyecto.departamentos[0]}")
    print(f"  Municipio: {proyecto.municipios[0]}")
    print(f"  Sectores: {', '.join(proyecto.sectores)}")
    print(f"  SROI: {proyecto.indicadores_impacto.get('sroi', 'N/A')}")
    print(f"  Presupuesto: ${proyecto.presupuesto_total:,} COP")
    print(f"  Beneficiarios: {proyecto.beneficiarios_totales:,}")

    # 3. Evaluar con criterio PDET
    print("\n\n📈 PASO 3: Evaluar con criterio Probabilidad Aprobación (PDET)")
    print("-" * 80)

    criterio = ProbabilidadAprobacionCriterio(db_path=db_path)
    score = criterio.evaluar(proyecto)

    print(f"\n🎯 SCORE TOTAL: {score:.1f}/100")

    # 4. Verificar metadata automática
    print("\n\n🔍 PASO 4: Verificar metadata calculada automáticamente")
    print("-" * 80)

    print(f"\n  tiene_municipios_pdet: {proyecto.tiene_municipios_pdet}")
    print(f"  puntaje_sectorial_max: {proyecto.puntaje_sectorial_max}")
    print(f"\n  puntajes_pdet:")
    for sector, puntaje in proyecto.puntajes_pdet.items():
        print(f"    {sector:30s}: {puntaje}/10")

    # 5. Desglose detallado
    print("\n\n📊 PASO 5: Desglose detallado del scoring")
    print("-" * 80)

    # Calcular componente único
    score_sectorial = criterio._evaluar_prioridad_sectorial_pdet(proyecto)

    print(f"\n  Componente ÚNICO - Prioridad Sectorial PDET (100%):")
    print(f"    Score: {score_sectorial:.1f}/100")
    print(f"    Contribución: {score_sectorial * 1.00:.1f} puntos (100% del criterio)")
    print(f"    Sectores evaluados: {', '.join(proyecto.sectores)}")
    print(f"    Puntaje máximo encontrado: {proyecto.puntaje_sectorial_max}/10")
    print(f"    Fórmula: ({proyecto.puntaje_sectorial_max}/10) × 100 = {score_sectorial:.1f}")

    print(f"\n  Metadata descriptiva (NO afecta scoring):")
    print(f"    ODS vinculados: {', '.join(proyecto.ods_vinculados)}")
    print(f"    Población objetivo: {proyecto.poblacion_objetivo}")

    print(f"\n  SCORE TOTAL: {score:.1f}/100")

    # 6. Interpretación
    print("\n\n✅ PASO 6: Interpretación del resultado")
    print("-" * 80)

    nivel = criterio.score_a_probabilidad(score)

    if score >= 75:
        emoji = "🟢"
    elif score >= 45:
        emoji = "🟡"
    else:
        emoji = "🔴"

    print(f"\n  {emoji} Probabilidad de Aprobación: {nivel.upper()}")
    print(f"  Score: {score:.1f}/100")

    if proyecto.puntaje_sectorial_max >= 9:
        sector_max = max(proyecto.puntajes_pdet, key=proyecto.puntajes_pdet.get)
        print(f"\n  💡 Recomendación:")
        print(f"     Este proyecto tiene MÁXIMA PRIORIDAD sectorial ({proyecto.puntaje_sectorial_max}/10)")
        print(f"     en el mecanismo Obras por Impuestos.")
        print(f"     Enfatizar sector '{sector_max}'")
        print(f"     en la propuesta para maximizar probabilidad de aprobación.")

    # 7. Validación final
    print("\n\n🎉 PASO 7: Validación final")
    print("-" * 80)

    validaciones = [
        ("Matriz PDET cargada", total == 372),
        ("Municipio ABEJORRAL encontrado", registro is not None),
        ("Proyecto creado correctamente", proyecto is not None),
        ("Score calculado", score > 0),
        ("Metadata automática", proyecto.tiene_municipios_pdet is True),
        ("Puntajes PDET poblados", len(proyecto.puntajes_pdet) > 0),
        ("Score en rango válido", 0 <= score <= 100),
        ("Puntaje sectorial máximo correcto", proyecto.puntaje_sectorial_max == 10),
        ("Alcantarillado tiene puntaje 10", proyecto.puntajes_pdet.get("Alcantarillado") == 10),
        ("Infraestructura Rural tiene puntaje 9", proyecto.puntajes_pdet.get("Infraestructura Rural") == 9),
    ]

    print()
    todas_ok = True
    for descripcion, resultado in validaciones:
        simbolo = "✅" if resultado else "❌"
        print(f"  {simbolo} {descripcion}")
        if not resultado:
            todas_ok = False

    print("\n" + "=" * 80)
    if todas_ok:
        print("✅ VALIDACIÓN EXITOSA - INTEGRACIÓN PDET/ZOMAC FUNCIONA CORRECTAMENTE")
    else:
        print("❌ VALIDACIÓN FALLÓ - REVISAR ERRORES")
    print("=" * 80)

    return todas_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
