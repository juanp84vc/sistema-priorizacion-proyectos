"""
Ejemplos de uso del Sistema de Priorización de Proyectos Sociales.

Este script demuestra:
1. Creación de proyectos
2. Configuración de criterios con diferentes pesos
3. Uso de diferentes estrategias de evaluación
4. Generación de reportes y comparaciones

Principios SOLID demostrados:
- DIP: Todo se inyecta por dependencias
- OCP: Fácil agregar nuevos criterios sin modificar código
- SRP: Cada componente tiene una responsabilidad única
"""

from src.models.proyecto import ProyectoSocial, AreaGeografica
from src.criterios import (
    ImpactoSocialCriterio,
    SostenibilidadFinancieraCriterio,
    AlineacionODSCriterio,
    CapacidadOrganizacionalCriterio
)
from src.estrategias import ScoringPonderado, ScoringUmbral
from src.servicios import SistemaPriorizacionProyectos
import json


def crear_proyectos_ejemplo():
    """Crea proyectos de ejemplo para demostración."""

    proyecto1 = ProyectoSocial(
        id="PROY-001",
        nombre="Educación Digital Rural",
        organizacion="Fundación TechRural",
        descripcion="Programa de alfabetización digital en zonas rurales",
        presupuesto_total=150000.0,
        duracion_meses=24,
        area_geografica=AreaGeografica.RURAL,
        beneficiarios_directos=500,
        beneficiarios_indirectos=1500,
        poblacion_objetivo="Niños y jóvenes en zonas rurales",
        departamentos=["Cundinamarca", "Boyacá"],
        ods_vinculados=["ODS 4", "ODS 9", "ODS 10"],
        indicadores_impacto={
            'años_experiencia': 8,
            'equipo_calificado': 0.8,
            'proyectos_exitosos': 4,
            'fuentes_financiamiento': 3,
            'ingresos_propios_pct': 20
        }
    )

    proyecto2 = ProyectoSocial(
        id="PROY-002",
        nombre="Agricultura Sostenible",
        organizacion="ONG Tierra Verde",
        descripcion="Capacitación en técnicas agrícolas sostenibles",
        presupuesto_total=200000.0,
        duracion_meses=36,
        area_geografica=AreaGeografica.RURAL,
        beneficiarios_directos=800,
        beneficiarios_indirectos=3200,
        poblacion_objetivo="Pequeños agricultores",
        departamentos=["Nariño", "Cauca", "Huila"],
        ods_vinculados=["ODS 2", "ODS 12", "ODS 13", "ODS 15"],
        indicadores_impacto={
            'años_experiencia': 12,
            'equipo_calificado': 0.9,
            'proyectos_exitosos': 7,
            'fuentes_financiamiento': 4,
            'ingresos_propios_pct': 35
        }
    )

    proyecto3 = ProyectoSocial(
        id="PROY-003",
        nombre="Emprendimiento Juvenil Urbano",
        organizacion="Instituto de Innovación Social",
        descripcion="Incubadora de emprendimientos sociales para jóvenes",
        presupuesto_total=180000.0,
        duracion_meses=24,
        area_geografica=AreaGeografica.URBANA,
        beneficiarios_directos=300,
        beneficiarios_indirectos=900,
        poblacion_objetivo="Jóvenes emprendedores 18-30 años",
        departamentos=["Bogotá D.C."],
        ods_vinculados=["ODS 8", "ODS 10"],
        indicadores_impacto={
            'años_experiencia': 5,
            'equipo_calificado': 0.7,
            'proyectos_exitosos': 2,
            'fuentes_financiamiento': 2,
            'ingresos_propios_pct': 15
        }
    )

    proyecto4 = ProyectoSocial(
        id="PROY-004",
        nombre="Salud Comunitaria Integral",
        organizacion="Red de Salud Popular",
        descripcion="Programa integral de salud preventiva comunitaria",
        presupuesto_total=250000.0,
        duracion_meses=36,
        area_geografica=AreaGeografica.PERIURBANA,
        beneficiarios_directos=1200,
        beneficiarios_indirectos=4800,
        poblacion_objetivo="Comunidades periurbanas vulnerables",
        departamentos=["Antioquia", "Valle del Cauca"],
        ods_vinculados=["ODS 3", "ODS 5", "ODS 10"],
        indicadores_impacto={
            'años_experiencia': 15,
            'equipo_calificado': 0.95,
            'proyectos_exitosos': 10,
            'fuentes_financiamiento': 5,
            'ingresos_propios_pct': 25
        }
    )

    return [proyecto1, proyecto2, proyecto3, proyecto4]


def ejemplo_1_scoring_ponderado():
    """
    Ejemplo 1: Evaluación con scoring ponderado.
    Énfasis en impacto social.
    """
    print("\n" + "="*70)
    print("EJEMPLO 1: Scoring Ponderado - Énfasis en Impacto Social")
    print("="*70)

    # Configurar criterios (pesos suman 1.0)
    criterios = [
        ImpactoSocialCriterio(peso=0.4),
        SostenibilidadFinancieraCriterio(peso=0.3),
        AlineacionODSCriterio(
            ods_prioritarios=["ODS 2", "ODS 3", "ODS 4"],
            peso=0.2
        ),
        CapacidadOrganizacionalCriterio(peso=0.1)
    ]

    # Crear sistema con estrategia de scoring ponderado
    sistema = SistemaPriorizacionProyectos(
        criterios=criterios,
        estrategia=ScoringPonderado()
    )

    # Evaluar cartera
    proyectos = crear_proyectos_ejemplo()
    reporte = sistema.generar_reporte(proyectos)

    # Mostrar resultados
    print(f"\nEstrategia: {reporte['estrategia']}")
    print(f"Total de proyectos evaluados: {reporte['total_proyectos']}")
    print(f"\nCriterios aplicados: {', '.join(reporte['criterios'])}")

    print("\n" + "-"*70)
    print("RANKING DE PROYECTOS")
    print("-"*70)
    for item in reporte['ranking']:
        print(f"\n{item['posicion']}. {item['proyecto_id']}")
        print(f"   Score: {item['score']:.2f}")
        print(f"   {item['recomendacion']}")

    print("\n" + "-"*70)
    print("ESTADÍSTICAS")
    print("-"*70)
    stats = reporte['estadisticas']
    print(f"Score máximo: {stats['score_maximo']:.2f}")
    print(f"Score mínimo: {stats['score_minimo']:.2f}")
    print(f"Score promedio: {stats['score_promedio']:.2f}")
    print(f"\nProyectos por prioridad:")
    print(f"  - Alta (≥80): {stats['proyectos_alta_prioridad']}")
    print(f"  - Media (60-79): {stats['proyectos_media_prioridad']}")
    print(f"  - Baja (<60): {stats['proyectos_baja_prioridad']}")


def ejemplo_2_scoring_umbral():
    """
    Ejemplo 2: Evaluación con umbrales mínimos.
    Énfasis en sostenibilidad financiera.
    """
    print("\n" + "="*70)
    print("EJEMPLO 2: Scoring con Umbrales - Énfasis en Sostenibilidad")
    print("="*70)

    # Configurar criterios con énfasis en sostenibilidad
    criterios = [
        ImpactoSocialCriterio(peso=0.3),
        SostenibilidadFinancieraCriterio(peso=0.4),
        AlineacionODSCriterio(
            ods_prioritarios=["ODS 8", "ODS 9", "ODS 12"],
            peso=0.15
        ),
        CapacidadOrganizacionalCriterio(peso=0.15)
    ]

    # Definir umbrales mínimos estrictos
    umbrales = {
        "Sostenibilidad Financiera": 50.0,  # Muy importante
        "Capacidad Organizacional": 40.0,
        "Impacto Social": 35.0,
        "Alineación ODS": 30.0
    }

    # Crear sistema con estrategia de umbrales
    sistema = SistemaPriorizacionProyectos(
        criterios=criterios,
        estrategia=ScoringUmbral(umbrales_minimos=umbrales)
    )

    # Evaluar cartera
    proyectos = crear_proyectos_ejemplo()
    resultados = sistema.priorizar_cartera(proyectos)

    print(f"\nUmbrales mínimos aplicados:")
    for criterio, umbral in umbrales.items():
        print(f"  - {criterio}: {umbral:.1f}")

    print("\n" + "-"*70)
    print("RESULTADOS DE EVALUACIÓN")
    print("-"*70)

    for idx, resultado in enumerate(resultados, 1):
        print(f"\n{idx}. Proyecto: {resultado.proyecto_nombre}")
        print(f"   ID: {resultado.proyecto_id}")
        print(f"   Score Final: {resultado.score_final:.2f}")
        print(f"   {resultado.recomendacion}")

        # Mostrar observaciones
        if resultado.observaciones:
            for obs in resultado.observaciones:
                print(f"   {obs}")


def ejemplo_3_comparacion_proyectos():
    """
    Ejemplo 3: Comparación detallada entre dos proyectos.
    """
    print("\n" + "="*70)
    print("EJEMPLO 3: Comparación Detallada de Proyectos")
    print("="*70)

    # Configurar sistema
    criterios = [
        ImpactoSocialCriterio(peso=0.35),
        SostenibilidadFinancieraCriterio(peso=0.35),
        AlineacionODSCriterio(
            ods_prioritarios=["ODS 2", "ODS 3", "ODS 4", "ODS 8"],
            peso=0.2
        ),
        CapacidadOrganizacionalCriterio(peso=0.1)
    ]

    sistema = SistemaPriorizacionProyectos(
        criterios=criterios,
        estrategia=ScoringPonderado()
    )

    # Comparar proyectos
    proyectos = crear_proyectos_ejemplo()
    comparacion = sistema.comparar_proyectos(proyectos[0], proyectos[1])

    print(f"\nComparando:")
    print(f"  Proyecto 1: {comparacion['proyecto_1']['nombre']}")
    print(f"  Proyecto 2: {comparacion['proyecto_2']['nombre']}")

    print("\n" + "-"*70)
    print("SCORES FINALES")
    print("-"*70)
    print(f"Proyecto 1: {comparacion['proyecto_1']['score_final']:.2f}")
    print(f"Proyecto 2: {comparacion['proyecto_2']['score_final']:.2f}")
    print(f"\nGanador: {comparacion['ganador']}")

    print("\n" + "-"*70)
    print("COMPARACIÓN POR CRITERIO")
    print("-"*70)

    for criterio, datos in comparacion['diferencias'].items():
        print(f"\n{criterio}:")
        print(f"  Proyecto 1: {datos['proyecto_1']:.2f}")
        print(f"  Proyecto 2: {datos['proyecto_2']:.2f}")
        print(f"  Diferencia: {datos['diferencia']:+.2f}")


def ejemplo_4_evaluacion_individual():
    """
    Ejemplo 4: Evaluación detallada de un proyecto individual.
    """
    print("\n" + "="*70)
    print("EJEMPLO 4: Evaluación Detallada Individual")
    print("="*70)

    # Configurar sistema
    criterios = [
        ImpactoSocialCriterio(peso=0.4),
        SostenibilidadFinancieraCriterio(peso=0.3),
        AlineacionODSCriterio(
            ods_prioritarios=["ODS 3", "ODS 5", "ODS 10"],
            peso=0.2
        ),
        CapacidadOrganizacionalCriterio(peso=0.1)
    ]

    sistema = SistemaPriorizacionProyectos(
        criterios=criterios,
        estrategia=ScoringPonderado()
    )

    # Evaluar proyecto individual
    proyecto = crear_proyectos_ejemplo()[3]  # Salud Comunitaria
    resultado = sistema.evaluar_proyecto(proyecto)

    print(f"\nProyecto: {proyecto.nombre}")
    print(f"Organización: {proyecto.organizacion}")
    print(f"Descripción: {proyecto.descripcion}")

    print("\n" + "-"*70)
    print("INFORMACIÓN DEL PROYECTO")
    print("-"*70)
    print(f"Presupuesto: ${proyecto.presupuesto_total:,.2f}")
    print(f"Duración: {proyecto.duracion_años} años")
    print(f"Área: {proyecto.area_geografica.value}")
    print(f"Beneficiarios directos: {proyecto.beneficiarios_directos:,}")
    print(f"Beneficiarios indirectos: {proyecto.beneficiarios_indirectos:,}")
    print(f"Costo por beneficiario: ${proyecto.presupuesto_por_beneficiario:,.2f}")
    print(f"ODS vinculados: {', '.join(proyecto.ods_vinculados)}")

    print("\n" + "-"*70)
    print("RESULTADOS DE EVALUACIÓN")
    print("-"*70)
    print(f"\nScore Final: {resultado.score_final:.2f}/100")
    print(f"Recomendación: {resultado.recomendacion}")

    print("\nDesglose por Criterio:")
    for criterio, detalle in resultado.detalle_criterios.items():
        print(f"\n  {criterio}:")
        print(f"    - Score base: {detalle['score_base']:.2f}/100")
        print(f"    - Peso: {detalle['peso']:.1%}")
        print(f"    - Score ponderado: {detalle['score_ponderado']:.2f}")

    if resultado.observaciones:
        print("\nObservaciones:")
        for obs in resultado.observaciones:
            print(f"  • {obs}")


def main():
    """Ejecuta todos los ejemplos."""
    print("\n" + "🎯"*35)
    print("SISTEMA DE PRIORIZACIÓN DE PROYECTOS SOCIALES")
    print("Demostración de Principios SOLID")
    print("🎯"*35)

    ejemplo_1_scoring_ponderado()
    ejemplo_2_scoring_umbral()
    ejemplo_3_comparacion_proyectos()
    ejemplo_4_evaluacion_individual()

    print("\n" + "="*70)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("="*70)
    print("\nEste sistema demuestra los principios SOLID:")
    print("  • SRP: Cada clase tiene una sola responsabilidad")
    print("  • OCP: Extensible sin modificar código existente")
    print("  • LSP: Criterios y estrategias son intercambiables")
    print("  • ISP: Interfaces focalizadas y mínimas")
    print("  • DIP: Sistema depende de abstracciones\n")


if __name__ == "__main__":
    main()
