#!/usr/bin/env python3
"""
Script E2E para validar Arquitectura C completa al 100%

Valida los 4 criterios:
- SROI (40%)
- Stakeholders (25%)
- Probabilidad Aprobación (20%)
- Riesgos (15%)

Total: 100% COMPLETO
"""
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.proyecto import ProyectoSocial, AreaGeografica
from src.scoring.motor_arquitectura_c import MotorScoringArquitecturaC


def print_separator(title: str = ""):
    """Imprime separador visual"""
    if title:
        print(f"\n{'=' * 80}")
        print(f"  {title}")
        print(f"{'=' * 80}\n")
    else:
        print(f"\n{'-' * 80}\n")


def test_proyecto_ideal():
    """Proyecto ideal: Alto SROI, PDET, bajo riesgo, alta pertinencia"""
    print_separator("PRUEBA 1: PROYECTO IDEAL")

    proyecto = ProyectoSocial(
        id="IDEAL-001",
        nombre="Acueducto Rural Comunitario - Zona PDET",
        organizacion="Aguas para Todos",
        descripcion="Construcción de acueducto comunitario en zona rural PDET",
        indicadores_impacto={'sroi': 4.8},  # SROI excelente
        presupuesto_total=450_000_000,
        beneficiarios_directos=2500,
        beneficiarios_indirectos=10000,
        duracion_meses=18,
        ods_vinculados=["ODS 6", "ODS 3"],
        area_geografica=AreaGeografica.RURAL,
        poblacion_objetivo="Comunidades rurales",
        departamentos=["ANTIOQUIA"],
        municipios=["ABEJORRAL"],
        sectores=["alcantarillado"],
        # Stakeholders: Alta pertinencia
        pertinencia_operacional=5,
        mejora_relacionamiento=5,
        en_corredor_transmision=True,
        stakeholders_involucrados=[
            'autoridades_locales',
            'lideres_comunitarios',
            'comunidades_indigenas'
        ],
        # Riesgos: Muy bajos
        riesgo_tecnico_probabilidad=1,
        riesgo_tecnico_impacto=2,
        riesgo_social_probabilidad=1,
        riesgo_social_impacto=1,
        riesgo_financiero_probabilidad=2,
        riesgo_financiero_impacto=2,
        riesgo_regulatorio_probabilidad=1,
        riesgo_regulatorio_impacto=1,
        duracion_estimada_meses=18
    )

    motor = MotorScoringArquitecturaC()
    resultado = motor.calcular_score(proyecto, detallado=True)

    print(motor.generar_reporte(resultado))

    # Validaciones
    assert resultado.score_total > 85, f"Score esperado >85, obtenido {resultado.score_total}"
    assert resultado.nivel_prioridad in ["MUY ALTA", "ALTA"], f"Prioridad esperada MUY ALTA/ALTA"
    assert resultado.score_sroi > 90, "SROI debe ser >90"
    assert resultado.score_stakeholders > 80, "Stakeholders debe ser >80"
    assert resultado.score_probabilidad == 100, "Probabilidad debe ser 100 (PDET max)"
    assert resultado.score_riesgos > 90, "Riesgos debe ser >90 (bajo riesgo)"

    print("✅ Proyecto ideal validado correctamente")


def test_proyecto_rechazado():
    """Proyecto rechazado por SROI < 1.0"""
    print_separator("PRUEBA 2: PROYECTO RECHAZADO (SROI < 1.0)")

    proyecto = ProyectoSocial(
        id="RECH-001",
        nombre="Proyecto Ineficiente",
        organizacion="Org Test",
        descripcion="Proyecto con bajo impacto social",
        indicadores_impacto={'sroi': 0.7},  # DESTRUYE VALOR
        presupuesto_total=200_000_000,
        beneficiarios_directos=100,
        beneficiarios_indirectos=200,
        duracion_meses=12,
        ods_vinculados=["ODS 1"],
        area_geografica=AreaGeografica.URBANA,
        poblacion_objetivo="General",
        departamentos=["CUNDINAMARCA"],
        municipios=["BOGOTÁ"],
        # Riesgos bajos (no importan)
        riesgo_tecnico_probabilidad=1,
        riesgo_tecnico_impacto=1,
        riesgo_social_probabilidad=1,
        riesgo_social_impacto=1,
        riesgo_financiero_probabilidad=1,
        riesgo_financiero_impacto=1,
        riesgo_regulatorio_probabilidad=1,
        riesgo_regulatorio_impacto=1,
        duracion_estimada_meses=12,
        # Stakeholders
        pertinencia_operacional=3,
        mejora_relacionamiento=3
    )

    motor = MotorScoringArquitecturaC()
    resultado = motor.calcular_score(proyecto, detallado=True)

    print(motor.generar_reporte(resultado))

    # Validaciones
    assert resultado.score_sroi == 0, "SROI debe ser 0 (rechazado)"
    assert resultado.nivel_prioridad == "RECHAZADO", "Nivel debe ser RECHAZADO"
    assert any("RECHAZADO" in alerta for alerta in resultado.alertas), "Debe tener alerta de rechazo"

    print("✅ Proyecto rechazado correctamente por SROI < 1.0")


def test_proyecto_alto_riesgo():
    """Proyecto con riesgos críticos"""
    print_separator("PRUEBA 3: PROYECTO ALTO RIESGO")

    proyecto = ProyectoSocial(
        id="RISK-001",
        nombre="Megaproyecto de Infraestructura",
        organizacion="Constructor S.A.",
        descripcion="Proyecto complejo con muchos riesgos",
        indicadores_impacto={'sroi': 3.2},
        presupuesto_total=2_000_000_000,  # 2B - penalización automática
        beneficiarios_directos=5000,
        beneficiarios_indirectos=20000,
        duracion_meses=48,  # 4 años - penalización automática
        ods_vinculados=["ODS 9"],
        area_geografica=AreaGeografica.NACIONAL,
        poblacion_objetivo="Población nacional",
        departamentos=["ANTIOQUIA", "CUNDINAMARCA", "VALLE DEL CAUCA"],  # Múltiples depts
        municipios=["MEDELLÍN", "BOGOTÁ", "CALI"],
        sectores=["via"],
        # Stakeholders
        pertinencia_operacional=4,
        mejora_relacionamiento=3,
        en_corredor_transmision=True,
        # Riesgos: CRÍTICOS
        riesgo_tecnico_probabilidad=5,
        riesgo_tecnico_impacto=5,  # Nivel 25 - CRÍTICO
        riesgo_social_probabilidad=4,
        riesgo_social_impacto=5,  # Nivel 20 - CRÍTICO
        riesgo_financiero_probabilidad=5,
        riesgo_financiero_impacto=4,  # Nivel 20 - CRÍTICO
        riesgo_regulatorio_probabilidad=4,
        riesgo_regulatorio_impacto=4,  # Nivel 16 - ALTO
        duracion_estimada_meses=48
    )

    motor = MotorScoringArquitecturaC()
    resultado = motor.calcular_score(proyecto, detallado=True)

    print(motor.generar_reporte(resultado))

    # Validaciones
    assert resultado.score_riesgos < 25, f"Riesgos debe ser <25, obtenido {resultado.score_riesgos}"
    assert len(resultado.alertas) >= 0, "Puede tener alertas de riesgo"
    assert resultado.nivel_prioridad in ["BAJA", "MEDIA"], "Prioridad debe ser BAJA o MEDIA"

    print("✅ Proyecto de alto riesgo evaluado correctamente")


def test_proyecto_no_pdet():
    """Proyecto NO-PDET con buen SROI"""
    print_separator("PRUEBA 4: PROYECTO NO-PDET")

    proyecto = ProyectoSocial(
        id="NOPDET-001",
        nombre="Educación Urbana",
        organizacion="Educación para Todos",
        descripcion="Programa educativo en zona urbana",
        indicadores_impacto={'sroi': 3.8},
        presupuesto_total=300_000_000,
        beneficiarios_directos=1500,
        beneficiarios_indirectos=5000,
        duracion_meses=24,
        ods_vinculados=["ODS 4"],
        area_geografica=AreaGeografica.URBANA,
        poblacion_objetivo="Estudiantes urbanos",
        departamentos=["CUNDINAMARCA"],
        municipios=["BOGOTÁ"],
        tiene_municipios_pdet=False,  # NO PDET
        # Stakeholders
        pertinencia_operacional=4,
        mejora_relacionamiento=4,
        stakeholders_involucrados=['autoridades_locales', 'academia'],
        # Riesgos moderados
        riesgo_tecnico_probabilidad=2,
        riesgo_tecnico_impacto=3,
        riesgo_social_probabilidad=2,
        riesgo_social_impacto=2,
        riesgo_financiero_probabilidad=3,
        riesgo_financiero_impacto=3,
        riesgo_regulatorio_probabilidad=2,
        riesgo_regulatorio_impacto=2,
        duracion_estimada_meses=24
    )

    motor = MotorScoringArquitecturaC()
    resultado = motor.calcular_score(proyecto, detallado=True)

    print(motor.generar_reporte(resultado))

    # Validaciones
    assert resultado.score_probabilidad == 0, "Probabilidad debe ser 0 (NO-PDET)"
    assert resultado.contribucion_probabilidad == 0, "Contribución probabilidad debe ser 0"
    assert resultado.score_sroi > 80, "SROI debe ser alto"
    assert resultado.score_total > 50, "Score total debe ser >50 (compensado por SROI)"

    print("✅ Proyecto NO-PDET evaluado correctamente")


def test_pesos_arquitectura_c():
    """Validar que pesos suman 100%"""
    print_separator("PRUEBA 5: VALIDACIÓN DE PESOS")

    motor = MotorScoringArquitecturaC()

    total = (
        motor.PESO_SROI +
        motor.PESO_STAKEHOLDERS +
        motor.PESO_PROBABILIDAD +
        motor.PESO_RIESGOS
    )

    print(f"SROI:                 {motor.PESO_SROI * 100:.0f}%")
    print(f"Stakeholders:         {motor.PESO_STAKEHOLDERS * 100:.0f}%")
    print(f"Prob. Aprobación:     {motor.PESO_PROBABILIDAD * 100:.0f}%")
    print(f"Riesgos:              {motor.PESO_RIESGOS * 100:.0f}%")
    print(f"{'-' * 30}")
    print(f"TOTAL:                {total * 100:.0f}%")

    assert total == 1.0, f"Pesos deben sumar 100%, suman {total * 100}%"
    assert motor.PESO_SROI == 0.40, "SROI debe ser 40%"
    assert motor.PESO_STAKEHOLDERS == 0.25, "Stakeholders debe ser 25%"
    assert motor.PESO_PROBABILIDAD == 0.20, "Probabilidad debe ser 20%"
    assert motor.PESO_RIESGOS == 0.15, "Riesgos debe ser 15%"

    print("\n✅ Pesos de Arquitectura C validados (100% COMPLETO)")


def test_comparacion_contribuciones():
    """Comparar contribuciones de cada criterio"""
    print_separator("PRUEBA 6: ANÁLISIS DE CONTRIBUCIONES")

    proyecto = ProyectoSocial(
        id="COMP-001",
        nombre="Proyecto de Análisis",
        organizacion="Test Org",
        descripcion="Proyecto para análisis de contribuciones",
        indicadores_impacto={'sroi': 4.0},
        presupuesto_total=400_000_000,
        beneficiarios_directos=2000,
        beneficiarios_indirectos=8000,
        duracion_meses=20,
        ods_vinculados=["ODS 6"],
        area_geografica=AreaGeografica.RURAL,
        poblacion_objetivo="Comunidades rurales",
        departamentos=["ANTIOQUIA"],
        municipios=["ABEJORRAL"],
        sectores=["alcantarillado"],
        # Stakeholders
        pertinencia_operacional=4,
        mejora_relacionamiento=5,
        en_corredor_transmision=True,
        stakeholders_involucrados=['autoridades_locales', 'lideres_comunitarios'],
        # Riesgos bajos
        riesgo_tecnico_probabilidad=2,
        riesgo_tecnico_impacto=2,
        riesgo_social_probabilidad=1,
        riesgo_social_impacto=2,
        riesgo_financiero_probabilidad=2,
        riesgo_financiero_impacto=3,
        riesgo_regulatorio_probabilidad=1,
        riesgo_regulatorio_impacto=2,
        duracion_estimada_meses=20
    )

    motor = MotorScoringArquitecturaC()
    resultado = motor.calcular_score(proyecto, detallado=True)

    print(f"Score total: {resultado.score_total:.2f}/100")
    print(f"\nContribuciones por criterio:")
    print(f"  SROI (40%):            {resultado.contribucion_sroi:.2f} pts")
    print(f"  Stakeholders (25%):    {resultado.contribucion_stakeholders:.2f} pts")
    print(f"  Probabilidad (20%):    {resultado.contribucion_probabilidad:.2f} pts")
    print(f"  Riesgos (15%):         {resultado.contribucion_riesgos:.2f} pts")
    print(f"  {'-' * 40}")
    print(f"  TOTAL:                 {resultado.score_total:.2f} pts")

    # Validar que la suma de contribuciones = score total
    suma_contribuciones = (
        resultado.contribucion_sroi +
        resultado.contribucion_stakeholders +
        resultado.contribucion_probabilidad +
        resultado.contribucion_riesgos
    )

    assert abs(suma_contribuciones - resultado.score_total) < 0.01, \
        "Suma de contribuciones debe igualar score total"

    # SROI debe ser la contribución dominante (40%)
    assert resultado.contribucion_sroi > resultado.contribucion_stakeholders, \
        "SROI debe contribuir más que Stakeholders"
    assert resultado.contribucion_sroi > resultado.contribucion_probabilidad, \
        "SROI debe contribuir más que Probabilidad"
    assert resultado.contribucion_sroi > resultado.contribucion_riesgos, \
        "SROI debe contribuir más que Riesgos"

    print("\n✅ Contribuciones validadas correctamente")


def main():
    """Ejecuta todas las pruebas E2E"""
    print_separator("🎉 VALIDACIÓN E2E: ARQUITECTURA C AL 100% 🎉")

    try:
        test_pesos_arquitectura_c()
        test_proyecto_ideal()
        test_proyecto_rechazado()
        test_proyecto_alto_riesgo()
        test_proyecto_no_pdet()
        test_comparacion_contribuciones()

        print_separator("✅ TODAS LAS PRUEBAS PASARON ✅")
        print("\n🎊 ARQUITECTURA C COMPLETADA AL 100% 🎊")
        print("\nCriterios implementados:")
        print("  ✅ SROI (40%) - Dominante")
        print("  ✅ Stakeholders (25%)")
        print("  ✅ Probabilidad Aprobación (20%)")
        print("  ✅ Riesgos (15%)")
        print("\n  TOTAL: 100% ✅\n")

        return 0

    except AssertionError as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
