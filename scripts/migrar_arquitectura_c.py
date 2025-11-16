#!/usr/bin/env python3
"""
Script de migración: Recalcular proyectos con Arquitectura C

Recalcula scores de todos los proyectos existentes usando
el nuevo motor de scoring y compara con scores anteriores.

Ejecutar con:
    python3 scripts/migrar_arquitectura_c.py
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scoring.motor_arquitectura_c import MotorScoringArquitecturaC, calcular_score_proyecto
from src.models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto


def main():
    print("=" * 80)
    print("MIGRACIÓN A ARQUITECTURA C - RECÁLCULO DE PROYECTOS")
    print("=" * 80)

    # Inicializar motor
    motor = MotorScoringArquitecturaC()

    print(f"\n📊 Motor de Scoring: Arquitectura {motor.VERSION}")
    print(f"   Pesos:")
    print(f"   - SROI: {motor.PESO_SROI * 100:.0f}%")
    print(f"   - Stakeholders: {motor.PESO_STAKEHOLDERS * 100:.0f}%")
    print(f"   - Probabilidad Aprobación: {motor.PESO_PROBABILIDAD * 100:.0f}%")
    print(f"   - Riesgos: {motor.PESO_RIESGOS * 100:.0f}%")

    # TODO: Cargar proyectos existentes desde base de datos
    # repo = ProyectoRepository()
    # proyectos = repo.listar_todos()

    # Por ahora crear proyectos de ejemplo
    proyectos = crear_proyectos_ejemplo()

    print(f"\n📁 Proyectos a recalcular: {len(proyectos)}")

    # Recalcular cada proyecto
    print("\n" + "=" * 80)
    print("RECALCULANDO PROYECTOS...")
    print("=" * 80)

    resultados = []

    for i, proyecto in enumerate(proyectos, 1):
        print(f"\n[{i}/{len(proyectos)}] {proyecto.nombre}")
        print("-" * 80)

        try:
            # Calcular score con Arquitectura C
            resultado = motor.calcular_score(proyecto, detallado=True)

            # Mostrar resultado
            print(f"Score Total: {resultado.score_total:.1f}/100")
            print(f"Nivel: {resultado.nivel_prioridad}")
            print(f"\nDesglose:")
            print(f"  SROI (40%):           {resultado.score_sroi:.1f} → {resultado.contribucion_sroi:.1f} pts")
            print(f"  Stakeholders (25%):   {resultado.score_stakeholders:.1f} → {resultado.contribucion_stakeholders:.1f} pts")
            print(f"  Prob. Aprobación (20%): {resultado.score_probabilidad:.1f} → {resultado.contribucion_probabilidad:.1f} pts")
            print(f"  Riesgos (15%):        {resultado.score_riesgos:.1f} → {resultado.contribucion_riesgos:.1f} pts")

            if resultado.alertas:
                print(f"\nAlertas:")
                for alerta in resultado.alertas:
                    print(f"  {alerta}")

            if resultado.recomendaciones:
                print(f"\nRecomendaciones:")
                for rec in resultado.recomendaciones:
                    print(f"  {rec}")

            resultados.append({
                'proyecto': proyecto,
                'resultado': resultado,
                'exito': True
            })

            # TODO: Guardar score actualizado en base de datos
            # proyecto.score_arquitectura_c = resultado.score_total
            # proyecto.nivel_prioridad = resultado.nivel_prioridad
            # repo.actualizar(proyecto)

        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            resultados.append({
                'proyecto': proyecto,
                'resultado': None,
                'exito': False,
                'error': str(e)
            })

    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DE MIGRACIÓN")
    print("=" * 80)

    exitosos = sum(1 for r in resultados if r['exito'])
    fallidos = len(resultados) - exitosos

    print(f"\nProyectos procesados: {len(resultados)}")
    print(f"  ✅ Exitosos: {exitosos}")
    print(f"  ❌ Fallidos: {fallidos}")

    if exitosos > 0:
        # Estadísticas de scores
        scores = [r['resultado'].score_total for r in resultados if r['exito']]
        print(f"\nEstadísticas de scores:")
        print(f"  Promedio: {sum(scores)/len(scores):.1f}")
        print(f"  Máximo: {max(scores):.1f}")
        print(f"  Mínimo: {min(scores):.1f}")

        # Distribución por nivel
        niveles = {}
        for r in resultados:
            if r['exito']:
                nivel = r['resultado'].nivel_prioridad
                niveles[nivel] = niveles.get(nivel, 0) + 1

        print(f"\nDistribución por nivel:")
        for nivel in ["MUY ALTA", "ALTA", "MEDIA", "BAJA", "RECHAZADO"]:
            if nivel in niveles:
                print(f"  {nivel}: {niveles[nivel]} proyectos")

    print("\n" + "=" * 80)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 80)


def crear_proyectos_ejemplo():
    """Crea proyectos de ejemplo para testing"""

    proyectos = []

    # Proyecto 1: Alta prioridad (SROI alto + PDET)
    p1 = ProyectoSocial(
        id="EJEMPLO-001",
        nombre="Alcantarillado Rural Abejorral",
        organizacion="Alcaldía de Abejorral",
        descripcion="Mejoramiento alcantarillado zona rural",
        departamentos=["ANTIOQUIA"],
        municipios=["ABEJORRAL"],
        sectores=["Alcantarillado", "Infraestructura Rural"],
        presupuesto_total=500_000_000,
        beneficiarios_directos=2000,
        beneficiarios_indirectos=8000,
        duracion_meses=24,
        ods_vinculados=["ODS 6"],
        area_geografica=AreaGeografica.RURAL,
        poblacion_objetivo="Comunidades rurales",
        indicadores_impacto={'sroi': 4.2},
        tiene_municipios_pdet=True,
        puntajes_pdet={"Alcantarillado": 10, "Infraestructura Rural": 9},
        puntaje_sectorial_max=10
    )
    proyectos.append(p1)

    # Proyecto 2: Prioridad media (SROI medio + PDET)
    p2 = ProyectoSocial(
        id="EJEMPLO-002",
        nombre="Centro Educativo Comunitario",
        organizacion="Fundación Educación",
        descripcion="Centro educativo para niños vulnerables",
        departamentos=["ANTIOQUIA"],
        municipios=["ABEJORRAL"],
        sectores=["Educación"],
        presupuesto_total=300_000_000,
        beneficiarios_directos=500,
        beneficiarios_indirectos=2000,
        duracion_meses=36,
        ods_vinculados=["ODS 4"],
        area_geografica=AreaGeografica.RURAL,
        poblacion_objetivo="Niños y jóvenes",
        indicadores_impacto={'sroi': 2.5},
        tiene_municipios_pdet=True,
        puntajes_pdet={"Educación": 6},
        puntaje_sectorial_max=6
    )
    proyectos.append(p2)

    # Proyecto 3: Rechazado (SROI < 1.0)
    p3 = ProyectoSocial(
        id="EJEMPLO-003",
        nombre="Evento Cultural Masivo",
        organizacion="Organización Cultural",
        descripcion="Festival cultural de un día",
        departamentos=["ANTIOQUIA"],
        municipios=["ABEJORRAL"],
        sectores=["Cultura"],
        presupuesto_total=100_000_000,
        beneficiarios_directos=5000,
        beneficiarios_indirectos=10000,
        duracion_meses=3,
        ods_vinculados=["ODS 11"],
        area_geografica=AreaGeografica.URBANA,
        poblacion_objetivo="Público general",
        indicadores_impacto={'sroi': 0.7},
        tiene_municipios_pdet=True,
        puntajes_pdet={"Cultura": 4},
        puntaje_sectorial_max=4
    )
    proyectos.append(p3)

    # Proyecto 4: NO-PDET (Score 0 en probabilidad)
    p4 = ProyectoSocial(
        id="EJEMPLO-004",
        nombre="Formación Empresarial Bogotá",
        organizacion="Fundación Capital",
        descripcion="Programa formación emprendedores",
        departamentos=["CUNDINAMARCA"],
        municipios=["BOGOTÁ"],
        sectores=["Educación"],
        presupuesto_total=400_000_000,
        beneficiarios_directos=1000,
        beneficiarios_indirectos=5000,
        duracion_meses=24,
        ods_vinculados=["ODS 4", "ODS 8"],
        area_geografica=AreaGeografica.URBANA,
        poblacion_objetivo="Emprendedores",
        indicadores_impacto={'sroi': 3.5},
        tiene_municipios_pdet=False,
        puntajes_pdet={},
        puntaje_sectorial_max=None
    )
    proyectos.append(p4)

    # Proyecto 5: SROI excepcional (> 7.0) con alerta
    p5 = ProyectoSocial(
        id="EJEMPLO-005",
        nombre="Microcréditos Solidarios",
        organizacion="ONG Microfinanzas",
        descripcion="Programa microcréditos para mujeres",
        departamentos=["ANTIOQUIA"],
        municipios=["ABEJORRAL"],
        sectores=["Infraestructura Rural"],
        presupuesto_total=200_000_000,
        beneficiarios_directos=500,
        beneficiarios_indirectos=2000,
        duracion_meses=36,
        ods_vinculados=["ODS 1", "ODS 5"],
        area_geografica=AreaGeografica.RURAL,
        poblacion_objetivo="Mujeres cabeza de hogar",
        indicadores_impacto={'sroi': 8.5},
        tiene_municipios_pdet=True,
        puntajes_pdet={"Infraestructura Rural": 9},
        puntaje_sectorial_max=9,
        observaciones_sroi="""
        SROI excepcional basado en:
        - Modelo probado en 15 países
        - Tasa repago: 98%
        - Estudio longitudinal 10 años
        - Certificación ISO 26000
        """
    )
    proyectos.append(p5)

    return proyectos


if __name__ == "__main__":
    main()
