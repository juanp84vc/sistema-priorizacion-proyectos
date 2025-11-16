#!/usr/bin/env python3
"""
Script de Validación Interactiva - Proyectos ENLAZA Reales

Permite al usuario ingresar datos de proyectos ENLAZA reales y
validar cómo los evalúa el sistema de scoring Arquitectura C.

Ejecutar con:
    python3 scripts/validar_proyectos_enlaza.py

Características:
- Entrada interactiva de datos de proyectos
- Detección automática de municipios PDET
- Sugerencias de sectores con prioridades
- Cálculo de scores con desglose completo
- Comparación entre múltiples proyectos
- Exportación opcional a base de datos
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scoring.motor_arquitectura_c import MotorScoringArquitecturaC, ResultadoScoring
from src.models.proyecto import ProyectoSocial, AreaGeografica
from src.database.matriz_pdet_repository import MatrizPDETRepository


def limpiar_pantalla():
    """Limpia la pantalla de la consola"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def mostrar_banner():
    """Muestra banner del sistema"""
    print("=" * 80)
    print(" " * 20 + "VALIDACIÓN PROYECTOS ENLAZA")
    print(" " * 15 + "Sistema de Scoring Arquitectura C")
    print("=" * 80)
    print()


def input_requerido(prompt: str, tipo=str, validar=None):
    """
    Solicita input requerido con validación

    Args:
        prompt: Mensaje a mostrar
        tipo: Tipo de dato esperado (str, int, float)
        validar: Función de validación opcional

    Returns:
        Valor ingresado y validado
    """
    while True:
        try:
            valor_str = input(f"{prompt}: ").strip()

            if not valor_str:
                print("❌ Este campo es requerido. Inténtalo de nuevo.")
                continue

            # Convertir a tipo deseado
            if tipo == int:
                valor = int(valor_str)
            elif tipo == float:
                valor = float(valor_str.replace(',', '.'))
            else:
                valor = valor_str

            # Validación adicional
            if validar and not validar(valor):
                print("❌ Valor inválido. Inténtalo de nuevo.")
                continue

            return valor

        except ValueError:
            print(f"❌ Por favor ingresa un valor de tipo {tipo.__name__}")


def input_opcional(prompt: str, tipo=str, default=None):
    """Solicita input opcional con valor por defecto"""
    valor_str = input(f"{prompt} [{default if default else 'Opcional'}]: ").strip()

    if not valor_str:
        return default

    try:
        if tipo == int:
            return int(valor_str)
        elif tipo == float:
            return float(valor_str.replace(',', '.'))
        else:
            return valor_str
    except ValueError:
        return default


def seleccionar_opcion(prompt: str, opciones: List[str]) -> str:
    """Muestra menú de opciones y retorna selección"""
    print(f"\n{prompt}")
    for i, opcion in enumerate(opciones, 1):
        print(f"  {i}. {opcion}")

    while True:
        try:
            seleccion = int(input("\nSelecciona opción: ").strip())
            if 1 <= seleccion <= len(opciones):
                return opciones[seleccion - 1]
            else:
                print(f"❌ Ingresa un número entre 1 y {len(opciones)}")
        except ValueError:
            print("❌ Ingresa un número válido")


def capturar_proyecto() -> Optional[ProyectoSocial]:
    """
    Captura datos de un proyecto interactivamente

    Returns:
        ProyectoSocial o None si el usuario cancela
    """
    print("\n" + "=" * 80)
    print("CAPTURA DE DATOS DEL PROYECTO")
    print("=" * 80)
    print()

    # Datos básicos
    print("📋 DATOS BÁSICOS")
    print("-" * 80)

    nombre = input_requerido("Nombre del proyecto")
    organizacion = input_requerido("Organización ejecutora")
    descripcion = input_opcional("Descripción breve", default="")

    # Ubicación
    print("\n📍 UBICACIÓN")
    print("-" * 80)

    departamento = input_requerido("Departamento").upper()
    municipio = input_requerido("Municipio principal").upper()

    # Verificar si es PDET
    matriz_repo = MatrizPDETRepository()
    municipio_pdet = matriz_repo.get_municipio(departamento, municipio)

    es_pdet = municipio_pdet is not None

    if es_pdet:
        print(f"\n✅ {municipio} es un municipio PDET")
        print(f"   Subregión: {municipio_pdet.subregion_pdet if municipio_pdet else 'N/A'}")
        print("\n💡 Sectores prioritarios disponibles:")

        # Obtener sectores disponibles del municipio
        sectores_disponibles = municipio_pdet.get_sectores_priorizados() if municipio_pdet else {}

        if sectores_disponibles:
            sectores_ordenados = sorted(
                sectores_disponibles.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for i, (sector, puntaje) in enumerate(sectores_ordenados, 1):
                estrellas = "⭐" * min(puntaje, 5)
                print(f"   {i}. {sector}: {puntaje}/10 {estrellas}")

        print("\nIngresa sectores del proyecto (separados por coma):")
        print("Ejemplo: Alcantarillado, Infraestructura Rural")
        sectores_str = input_requerido("Sectores")
        sectores = [s.strip() for s in sectores_str.split(',')]

        # Obtener puntajes PDET
        puntajes_pdet = {}
        puntaje_max = 0

        for sector in sectores:
            puntaje = municipio_pdet.get_puntaje_sector(sector) if municipio_pdet else 0
            if puntaje > 0:
                puntajes_pdet[sector] = puntaje
                puntaje_max = max(puntaje_max, puntaje)

        if puntajes_pdet:
            print("\n✅ Puntajes PDET asignados:")
            for sector, puntaje in puntajes_pdet.items():
                print(f"   {sector}: {puntaje}/10")

    else:
        print(f"\nℹ️  {municipio} NO es un municipio PDET")
        print("   Este proyecto NO será elegible para Obras por Impuestos")

        sectores_str = input_opcional("Sectores (separados por coma)", default="General")
        sectores = [s.strip() for s in sectores_str.split(',')] if sectores_str else ["General"]
        puntajes_pdet = {}
        puntaje_max = None

    # Área geográfica
    print("\n🗺️  ÁREA GEOGRÁFICA")
    area_str = seleccionar_opcion(
        "Selecciona área geográfica:",
        ["RURAL", "URBANA", "MIXTA"]
    )
    area_geografica = AreaGeografica[area_str]

    # Financieros
    print("\n💰 DATOS FINANCIEROS")
    print("-" * 80)

    presupuesto = input_requerido(
        "Presupuesto total (COP)",
        tipo=int,
        validar=lambda x: x > 0
    )

    duracion = input_requerido(
        "Duración en meses",
        tipo=int,
        validar=lambda x: 1 <= x <= 120
    )

    # Beneficiarios
    print("\n👥 BENEFICIARIOS")
    print("-" * 80)

    beneficiarios_directos = input_requerido(
        "Beneficiarios directos",
        tipo=int,
        validar=lambda x: x > 0
    )

    beneficiarios_indirectos = input_opcional(
        "Beneficiarios indirectos",
        tipo=int,
        default=beneficiarios_directos * 3
    )

    poblacion_objetivo = input_opcional(
        "Población objetivo",
        default="Comunidades vulnerables"
    )

    # SROI - CRÍTICO
    print("\n📊 SROI (SOCIAL RETURN ON INVESTMENT) - CRITERIO DOMINANTE 40%")
    print("-" * 80)
    print("El SROI mide cuánto valor social se genera por cada peso invertido.")
    print("\nReferencias:")
    print("  SROI < 1.0  → Proyecto RECHAZADO (destruye valor)")
    print("  SROI 1.0-2.0 → Retorno bajo (60 pts)")
    print("  SROI 2.0-3.0 → Retorno bueno (80 pts)")
    print("  SROI ≥ 3.0   → Retorno alto (95 pts)")
    print("  SROI > 7.0   → EXCEPCIONAL - Requiere verificación")
    print()

    sroi = input_requerido(
        "Valor SROI calculado",
        tipo=float,
        validar=lambda x: x >= 0
    )

    if sroi < 1.0:
        print("\n⚠️  ALERTA: SROI < 1.0 → El proyecto será RECHAZADO")
        print("    El proyecto destruye valor social (invierte más de lo que genera)")
        confirmar = input("¿Continuar de todos modos? (s/n): ").strip().lower()
        if confirmar != 's':
            print("❌ Captura cancelada")
            return None

    elif sroi > 7.0:
        print("\n⚠️  SROI EXCEPCIONAL > 7.0 detectado")
        print("    El sistema solicitará documentación de soporte")
        observaciones_sroi = input_requerido(
            "Documentación/justificación del SROI excepcional"
        )
    else:
        observaciones_sroi = input_opcional(
            "Observaciones sobre cálculo SROI",
            default=""
        )

    # Metodología SROI
    metodologia_opciones = [
        "Evaluación post-proyecto",
        "Proyección basada en proyectos similares",
        "Estudio académico",
        "Certificación externa",
        "Otra"
    ]

    metodologia_sroi = seleccionar_opcion(
        "\nMetodología utilizada para calcular SROI:",
        metodologia_opciones
    )

    # Nivel de confianza
    nivel_confianza = seleccionar_opcion(
        "\nNivel de confianza en el cálculo SROI:",
        ["BAJO", "MEDIO", "ALTO", "MUY_ALTO"]
    )

    # ODS
    print("\n🎯 OBJETIVOS DE DESARROLLO SOSTENIBLE")
    print("-" * 80)
    ods_str = input_opcional(
        "ODS vinculados (separados por coma, ej: ODS 1, ODS 6)",
        default="ODS 1"
    )
    ods_vinculados = [ods.strip() for ods in ods_str.split(',')] if ods_str else ["ODS 1"]

    # Crear proyecto
    try:
        proyecto = ProyectoSocial(
            id=f"ENLAZA-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            nombre=nombre,
            organizacion=organizacion,
            descripcion=descripcion,
            departamentos=[departamento],
            municipios=[municipio],
            sectores=sectores,
            presupuesto_total=presupuesto,
            beneficiarios_directos=beneficiarios_directos,
            beneficiarios_indirectos=beneficiarios_indirectos,
            duracion_meses=duracion,
            ods_vinculados=ods_vinculados,
            area_geografica=area_geografica,
            poblacion_objetivo=poblacion_objetivo,
            indicadores_impacto={'sroi': sroi},
            tiene_municipios_pdet=es_pdet,
            puntajes_pdet=puntajes_pdet if puntajes_pdet else {},
            puntaje_sectorial_max=puntaje_max,
            observaciones_sroi=observaciones_sroi,
            metodologia_sroi=metodologia_sroi,
            nivel_confianza_sroi=nivel_confianza,
            fecha_calculo_sroi=datetime.now()
        )

        return proyecto

    except Exception as e:
        print(f"\n❌ Error al crear proyecto: {e}")
        return None


def mostrar_resultado(proyecto: ProyectoSocial, resultado: ResultadoScoring, numero: int):
    """Muestra resultado de scoring de forma visual"""

    print("\n" + "=" * 80)
    print(f"RESULTADO #{numero}: {proyecto.nombre}")
    print("=" * 80)
    print()

    # Header con info básica
    print(f"📋 Organización: {proyecto.organizacion}")
    print(f"📍 Ubicación: {proyecto.municipios[0]}, {proyecto.departamentos[0]}")
    print(f"💰 Presupuesto: ${proyecto.presupuesto_total:,} COP")
    print(f"👥 Beneficiarios: {proyecto.beneficiarios_totales:,}")

    if proyecto.tiene_municipios_pdet:
        print(f"✅ Municipio PDET - Elegible para Obras por Impuestos")
    else:
        print(f"ℹ️  NO-PDET - No elegible para Obras por Impuestos")

    print()

    # Score total destacado
    print("┌" + "─" * 78 + "┐")
    print(f"│  SCORE TOTAL: {resultado.score_total:.1f}/100 " + " " * (78 - 25 - len(f"{resultado.score_total:.1f}")) + "│")
    print(f"│  NIVEL: {resultado.nivel_prioridad}" + " " * (78 - 10 - len(resultado.nivel_prioridad)) + "│")
    print("└" + "─" * 78 + "┘")
    print()

    # Desglose por criterio
    print("📊 DESGLOSE POR CRITERIO:")
    print("-" * 80)

    # SROI
    barra_sroi = "█" * int(resultado.score_sroi / 2)
    print(f"1. SROI (40%):")
    print(f"   Score: {resultado.score_sroi:.1f}/100 {barra_sroi}")
    print(f"   Contribución: {resultado.contribucion_sroi:.1f} pts")

    # Stakeholders
    barra_stake = "█" * int(resultado.score_stakeholders / 2)
    print(f"\n2. Stakeholders (25%):")
    print(f"   Score: {resultado.score_stakeholders:.1f}/100 {barra_stake}")
    print(f"   Contribución: {resultado.contribucion_stakeholders:.1f} pts")

    # Probabilidad
    barra_prob = "█" * int(resultado.score_probabilidad / 2)
    print(f"\n3. Probabilidad Aprobación (20%):")
    print(f"   Score: {resultado.score_probabilidad:.1f}/100 {barra_prob}")
    print(f"   Contribución: {resultado.contribucion_probabilidad:.1f} pts")

    # Riesgos
    barra_riesgos = "█" * int(resultado.score_riesgos / 2)
    print(f"\n4. Riesgos (15%):")
    print(f"   Score: {resultado.score_riesgos:.1f}/100 {barra_riesgos}")
    print(f"   Contribución: {resultado.contribucion_riesgos:.1f} pts")

    print()
    print(f"   {'─' * 40}")
    print(f"   TOTAL: {resultado.score_total:.1f}/100")

    # Alertas
    if resultado.alertas:
        print()
        print("⚠️  ALERTAS:")
        print("-" * 80)
        for alerta in resultado.alertas:
            print(f"  {alerta}")

    # Recomendaciones
    if resultado.recomendaciones:
        print()
        print("💡 RECOMENDACIONES:")
        print("-" * 80)
        for rec in resultado.recomendaciones:
            print(f"  {rec}")

    print()


def mostrar_comparacion(proyectos_resultados: List[tuple]):
    """Muestra tabla comparativa de múltiples proyectos"""

    if len(proyectos_resultados) < 2:
        return

    print("\n" + "=" * 80)
    print("COMPARACIÓN DE PROYECTOS")
    print("=" * 80)
    print()

    # Header
    print(f"{'#':<4} {'Proyecto':<30} {'Score':<10} {'Nivel':<15} {'SROI':<8}")
    print("-" * 80)

    # Ordenar por score descendente
    proyectos_ordenados = sorted(
        proyectos_resultados,
        key=lambda x: x[1].score_total,
        reverse=True
    )

    for i, (proyecto, resultado) in enumerate(proyectos_ordenados, 1):
        nombre_corto = proyecto.nombre[:28] + ".." if len(proyecto.nombre) > 30 else proyecto.nombre
        sroi = proyecto.indicadores_impacto.get('sroi', 0)

        print(f"{i:<4} {nombre_corto:<30} {resultado.score_total:>6.1f}/100  {resultado.nivel_prioridad:<15} {sroi:>5.1f}")

    print()

    # Estadísticas
    scores = [r.score_total for _, r in proyectos_resultados]
    print(f"Estadísticas:")
    print(f"  Promedio: {sum(scores)/len(scores):.1f}")
    print(f"  Máximo: {max(scores):.1f}")
    print(f"  Mínimo: {min(scores):.1f}")
    print()


def main():
    """Función principal"""

    limpiar_pantalla()
    mostrar_banner()

    print("Este script te permite validar proyectos ENLAZA reales con el")
    print("nuevo sistema de scoring Arquitectura C.")
    print()
    print("📌 Características:")
    print("  - SROI como criterio dominante (40%)")
    print("  - Datos oficiales PDET/ZOMAC integrados")
    print("  - Probabilidad de aprobación con matriz sectorial")
    print("  - Validación automática de calidad")
    print()

    input("Presiona ENTER para comenzar...")

    # Inicializar motor
    motor = MotorScoringArquitecturaC()

    proyectos_resultados = []

    while True:
        limpiar_pantalla()
        mostrar_banner()

        print(f"Proyectos capturados: {len(proyectos_resultados)}")
        print()

        # Capturar proyecto
        proyecto = capturar_proyecto()

        if proyecto is None:
            if len(proyectos_resultados) == 0:
                print("\n❌ No se capturó ningún proyecto. Saliendo...")
                break
            else:
                print("\n✅ Captura cancelada")
        else:
            # Calcular score
            print("\n⚙️  Calculando score...")
            try:
                resultado = motor.calcular_score(proyecto, detallado=True)
                proyectos_resultados.append((proyecto, resultado))

                # Mostrar resultado
                mostrar_resultado(proyecto, resultado, len(proyectos_resultados))

            except Exception as e:
                print(f"\n❌ Error al calcular score: {e}")
                import traceback
                traceback.print_exc()

        # Preguntar si desea continuar
        print()
        print("Opciones:")
        print("  1. Capturar otro proyecto")
        print("  2. Ver comparación de proyectos")
        print("  3. Salir")

        opcion = input("\nSelecciona opción: ").strip()

        if opcion == "2":
            if len(proyectos_resultados) > 0:
                limpiar_pantalla()
                mostrar_banner()
                mostrar_comparacion(proyectos_resultados)
                input("\nPresiona ENTER para continuar...")
            else:
                print("❌ No hay proyectos para comparar")
                input("\nPresiona ENTER para continuar...")

        elif opcion == "3" or opcion.lower() == "n":
            break

    # Resumen final
    if len(proyectos_resultados) > 0:
        limpiar_pantalla()
        mostrar_banner()

        print("=" * 80)
        print("RESUMEN FINAL DE VALIDACIÓN")
        print("=" * 80)
        print()

        print(f"Total de proyectos evaluados: {len(proyectos_resultados)}")
        print()

        mostrar_comparacion(proyectos_resultados)

        # Distribución por nivel
        niveles = {}
        for _, resultado in proyectos_resultados:
            nivel = resultado.nivel_prioridad
            niveles[nivel] = niveles.get(nivel, 0) + 1

        print("Distribución por nivel de prioridad:")
        for nivel in ["MUY ALTA", "ALTA", "MEDIA", "BAJA", "RECHAZADO"]:
            if nivel in niveles:
                print(f"  {nivel}: {niveles[nivel]} proyecto(s)")

        print()
        print("=" * 80)
        print("✅ VALIDACIÓN COMPLETADA")
        print("=" * 80)
        print()
        print("Los proyectos han sido evaluados con Arquitectura C:")
        print("  - SROI: 40% (dominante)")
        print("  - Stakeholders: 25%")
        print("  - Probabilidad Aprobación: 20% (con datos PDET)")
        print("  - Riesgos: 15%")
        print()
        print("📊 Los resultados reflejan el impacto real del SROI en la priorización.")
        print()


if __name__ == "__main__":
    main()
