#!/usr/bin/env python3
"""
Demostración: Comparación de scores por sector PDET/ZOMAC

Compara 3 proyectos idénticos en Abejorral con diferentes sectores
para validar que prioridad sectorial impacta correctamente el scoring.
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto
from criterios.probabilidad_aprobacion_pdet import ProbabilidadAprobacionCriterio


def crear_proyecto_base(sector: str) -> ProyectoSocial:
    """Crea proyecto base con sector específico"""
    return ProyectoSocial(
        id=f"TEST-{sector.upper()[:3]}",
        nombre=f"Proyecto {sector} Abejorral",
        organizacion="Alcaldía de Abejorral",
        descripcion=f"Proyecto de {sector} en zona rural",
        departamentos=["ANTIOQUIA"],
        municipios=["ABEJORRAL"],
        area_geografica=AreaGeografica.RURAL,
        sectores=[sector],
        beneficiarios_directos=2000,
        beneficiarios_indirectos=8000,
        poblacion_objetivo="Población rural",
        presupuesto_total=500_000_000,
        duracion_meses=18,
        ods_vinculados=["3", "6"],  # 2 ODS prioritarios
        indicadores_impacto={'sroi': 4.0},
        estado=EstadoProyecto.EVALUACION
    )


def main():
    print("=" * 100)
    print("📊 DEMOSTRACIÓN: IMPACTO DE PRIORIDAD SECTORIAL PDET/ZOMAC EN SCORING")
    print("=" * 100)
    print("\n🎯 Escenario: 3 proyectos idénticos en Abejorral, Antioquia")
    print("   Única diferencia: Sector del proyecto")
    print("   Objetivo: Validar que prioridad sectorial oficial impacta scoring")
    print("   Metodología: Score = (Puntaje_Sectorial / 10) × 100 (100% basado en PDET)\n")

    db_path = str(Path(__file__).parent.parent / "data" / "proyectos.db")
    criterio = ProbabilidadAprobacionCriterio(db_path=db_path)

    # Proyectos con diferentes prioridades sectoriales
    proyectos = [
        ("Alcantarillado", 10, "🟢"),      # Máxima prioridad
        ("Educación", 6, "🟡"),            # Prioridad media
        ("Salud", 3, "🔴"),                # Baja prioridad
    ]

    resultados = []

    for sector, puntaje_esperado, emoji in proyectos:
        proyecto = crear_proyecto_base(sector)
        score = criterio.evaluar(proyecto)
        nivel = criterio.score_a_probabilidad(score)

        resultados.append({
            'sector': sector,
            'puntaje_pdet': proyecto.puntaje_sectorial_max,
            'puntaje_esperado': puntaje_esperado,
            'score': score,
            'nivel': nivel,
            'emoji': emoji
        })

    # Mostrar resultados
    print("\n" + "=" * 100)
    print("📋 RESULTADOS DE EVALUACIÓN")
    print("=" * 100)
    print(f"\n{'Sector':<20} {'Prioridad PDET':<20} {'Score Total':<15} {'Probabilidad':<15} {'Status'}")
    print("-" * 100)

    for r in resultados:
        print(f"{r['sector']:<20} "
              f"{r['puntaje_pdet']}/10 (esperado: {r['puntaje_esperado']})   "
              f"{r['score']:>6.1f}/100      "
              f"{r['nivel'].upper():<15} "
              f"{r['emoji']}")

    # Análisis diferencial
    print("\n" + "=" * 100)
    print("📈 ANÁLISIS DIFERENCIAL")
    print("=" * 100)

    diff_alta_baja = resultados[0]['score'] - resultados[2]['score']
    diff_alta_media = resultados[0]['score'] - resultados[1]['score']

    print(f"\n🔸 Diferencia Alta vs Baja prioridad:")
    print(f"   {resultados[0]['sector']} (10/10) vs {resultados[2]['sector']} (3/10)")
    print(f"   Diferencia: {diff_alta_baja:.1f} puntos")
    print(f"   Impacto: {resultados[0]['nivel'].upper()} vs {resultados[2]['nivel'].upper()}")

    print(f"\n🔸 Diferencia Alta vs Media prioridad:")
    print(f"   {resultados[0]['sector']} (10/10) vs {resultados[1]['sector']} (6/10)")
    print(f"   Diferencia: {diff_alta_media:.1f} puntos")
    print(f"   Impacto: {resultados[0]['nivel'].upper()} vs {resultados[1]['nivel'].upper()}")

    # Validación matemática
    print("\n" + "=" * 100)
    print("🧮 VALIDACIÓN MATEMÁTICA")
    print("=" * 100)

    print("\nFórmula (100% basado en prioridad sectorial PDET):")
    print("  Score = (Puntaje_Sector / 10) × 100")

    for r in resultados:
        score_teorico = (r['puntaje_pdet'] / 10) * 100
        print(f"\n  {r['sector']}:")
        print(f"    Score = ({r['puntaje_pdet']}/10) × 100 = {score_teorico:.1f} puntos")
        if score_teorico == r['score']:
            print(f"    ✅ Coincide con score calculado: {r['score']:.1f}")

    # Conclusiones
    print("\n" + "=" * 100)
    print("✅ CONCLUSIONES")
    print("=" * 100)

    validaciones = [
        (
            "Puntajes PDET correctos",
            all(r['puntaje_pdet'] == r['puntaje_esperado'] for r in resultados)
        ),
        (
            "Diferencia significativa alta vs baja",
            diff_alta_baja == 70  # 100 - 30 = 70 puntos
        ),
        (
            "Alta prioridad (10/10) → Score 100",
            resultados[0]['score'] == 100
        ),
        (
            "Baja prioridad (3/10) → Score 30",
            resultados[2]['score'] == 30
        ),
        (
            "Media prioridad (6/10) → Score 60",
            resultados[1]['score'] == 60
        ),
        (
            "Ordenamiento correcto",
            resultados[0]['score'] > resultados[1]['score'] > resultados[2]['score']
        ),
    ]

    print()
    todas_ok = True
    for descripcion, resultado in validaciones:
        simbolo = "✅" if resultado else "❌"
        print(f"  {simbolo} {descripcion}")
        if not resultado:
            todas_ok = False

    if todas_ok:
        print("\n" + "=" * 100)
        print("🎉 DEMOSTRACIÓN EXITOSA")
        print("=" * 100)
        print("\n💡 Interpretación:")
        print("   - La matriz PDET/ZOMAC oficial está integrada correctamente")
        print("   - Los puntajes sectoriales impactan 100% el scoring (fórmula lineal 1-10 → 10-100)")
        print("   - Proyectos en sectores de alta prioridad obtienen scores 70 puntos superiores")
        print("   - El sistema refleja fielmente datos oficiales Obras por Impuestos")
        print("   - Municipios NO-PDET reciben score 0 (mecanismo exclusivo PDET/ZOMAC)")
        print("\n✅ Sistema listo para producción\n")
    else:
        print("\n❌ Algunas validaciones fallaron - revisar\n")

    return todas_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
