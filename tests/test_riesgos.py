"""
Tests para el criterio Riesgos (15%)
Arquitectura C - Sistema de evaluación de riesgos
"""
import unittest
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.criterios.riesgos import RiesgosCriterio, ResultadoRiesgos
from src.models.proyecto import ProyectoSocial, AreaGeografica


class TestRiesgosCriterio(unittest.TestCase):
    """Tests para el criterio Riesgos"""

    def setUp(self):
        """Setup común para tests"""
        self.criterio = RiesgosCriterio()

    def _crear_proyecto_base(self) -> ProyectoSocial:
        """Helper: Crear proyecto base con riesgos mínimos"""
        return ProyectoSocial(
            id="TEST-001",
            nombre="Proyecto Test",
            organizacion="ONG Test",
            descripcion="Proyecto de prueba",
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            presupuesto_total=100_000_000,
            ods_vinculados=["4"],
            area_geografica=AreaGeografica.RURAL,
            poblacion_objetivo="Comunidad rural",
            departamentos=["CUNDINAMARCA"],
            municipios=["Bogotá"],
            # Riesgos mínimos (probabilidad=1, impacto=1)
            riesgo_tecnico_probabilidad=1,
            riesgo_tecnico_impacto=1,
            riesgo_social_probabilidad=1,
            riesgo_social_impacto=1,
            riesgo_financiero_probabilidad=1,
            riesgo_financiero_impacto=1,
            riesgo_regulatorio_probabilidad=1,
            riesgo_regulatorio_impacto=1,
            duracion_estimada_meses=12
        )

    # ========== TESTS: CÁLCULO DE NIVELES DE RIESGO ==========

    def test_calcular_nivel_riesgo_minimo(self):
        """Test: Nivel mínimo de riesgo (1×1=1)"""
        nivel = self.criterio._calcular_nivel_riesgo(1, 1)
        self.assertEqual(nivel, 1)

    def test_calcular_nivel_riesgo_maximo(self):
        """Test: Nivel máximo de riesgo (5×5=25)"""
        nivel = self.criterio._calcular_nivel_riesgo(5, 5)
        self.assertEqual(nivel, 25)

    def test_calcular_nivel_riesgo_medio(self):
        """Test: Nivel medio de riesgo (3×3=9)"""
        nivel = self.criterio._calcular_nivel_riesgo(3, 3)
        self.assertEqual(nivel, 9)

    def test_calcular_nivel_riesgo_asimetrico(self):
        """Test: Nivel asimétrico (5×2=10)"""
        nivel = self.criterio._calcular_nivel_riesgo(5, 2)
        self.assertEqual(nivel, 10)

    # ========== TESTS: CONVERSIÓN A SCORE INVERSO ==========

    def test_nivel_a_score_inverso_minimo(self):
        """Test: Nivel 1 → Score 96"""
        score = self.criterio._nivel_a_score_inverso(1)
        self.assertAlmostEqual(score, 96.0, places=1)

    def test_nivel_a_score_inverso_maximo(self):
        """Test: Nivel 25 → Score 0"""
        score = self.criterio._nivel_a_score_inverso(25)
        self.assertAlmostEqual(score, 0.0, places=1)

    def test_nivel_a_score_inverso_medio(self):
        """Test: Nivel 13 → Score ~48"""
        score = self.criterio._nivel_a_score_inverso(13)
        self.assertAlmostEqual(score, 48.0, places=0)

    def test_nivel_a_score_inverso_cuarto(self):
        """Test: Nivel 6 → Score 76"""
        score = self.criterio._nivel_a_score_inverso(6)
        self.assertAlmostEqual(score, 76.0, places=1)

    # ========== TESTS: PROYECTOS CON BAJO RIESGO ==========

    def test_proyecto_bajo_riesgo_score_alto(self):
        """Test: Proyecto bajo riesgo → Score alto (~96)"""
        proyecto = self._crear_proyecto_base()
        # Todos los riesgos en 1×1 = 1 (mínimo)
        score = self.criterio.evaluar(proyecto)

        # Score esperado: ~96 (todos los riesgos en nivel 1)
        self.assertGreater(score, 90)
        self.assertLessEqual(score, 100)

    def test_proyecto_bajo_riesgo_nivel_bajo(self):
        """Test: Proyecto bajo riesgo → Nivel general BAJO"""
        proyecto = self._crear_proyecto_base()
        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertEqual(resultado.nivel_general, "BAJO")
        self.assertGreater(resultado.score, 90)

    # ========== TESTS: PROYECTOS CON ALTO RIESGO ==========

    def test_proyecto_alto_riesgo_score_bajo(self):
        """Test: Proyecto alto riesgo → Score bajo"""
        proyecto = self._crear_proyecto_base()
        # Todos los riesgos críticos
        proyecto.riesgo_tecnico_probabilidad = 5
        proyecto.riesgo_tecnico_impacto = 5  # Nivel 25
        proyecto.riesgo_social_probabilidad = 5
        proyecto.riesgo_social_impacto = 5  # Nivel 25
        proyecto.riesgo_financiero_probabilidad = 5
        proyecto.riesgo_financiero_impacto = 5  # Nivel 25
        proyecto.riesgo_regulatorio_probabilidad = 5
        proyecto.riesgo_regulatorio_impacto = 5  # Nivel 25

        score = self.criterio.evaluar(proyecto)

        # Score debe ser muy bajo (<20) con todos los riesgos críticos
        self.assertLess(score, 20)

    def test_proyecto_critico_nivel_critico(self):
        """Test: Proyecto con riesgo crítico → Nivel CRÍTICO"""
        proyecto = self._crear_proyecto_base()
        proyecto.riesgo_tecnico_probabilidad = 5
        proyecto.riesgo_tecnico_impacto = 5  # Nivel 25 (crítico)

        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertEqual(resultado.nivel_general, "CRÍTICO")
        self.assertEqual(resultado.nivel_riesgo_tecnico, 25)

    def test_proyecto_alto_riesgo_alertas(self):
        """Test: Proyecto alto riesgo → Genera alertas"""
        proyecto = self._crear_proyecto_base()
        proyecto.riesgo_tecnico_probabilidad = 5
        proyecto.riesgo_tecnico_impacto = 4  # Nivel 20 (crítico)

        resultado = self.criterio.evaluar_detallado(proyecto)

        # Debe tener alertas
        self.assertTrue(len(resultado.alertas) > 0)
        # Alerta debe mencionar riesgo técnico
        alertas_str = ' '.join(resultado.alertas)
        self.assertIn('Técnico', alertas_str)

    # ========== TESTS: RIESGOS INDIVIDUALES ==========

    def test_riesgo_tecnico_alto(self):
        """Test: Riesgo técnico alto genera alerta específica"""
        proyecto = self._crear_proyecto_base()
        proyecto.riesgo_tecnico_probabilidad = 4
        proyecto.riesgo_tecnico_impacto = 5  # Nivel 20 (crítico)

        resultado = self.criterio.evaluar_detallado(proyecto)

        # Verificar nivel técnico
        self.assertEqual(resultado.nivel_riesgo_tecnico, 20)
        # Verificar alerta
        alertas_str = ' '.join(resultado.alertas)
        self.assertIn('Técnico CRÍTICO', alertas_str)

    def test_riesgo_social_alto(self):
        """Test: Riesgo social alto genera alerta específica"""
        proyecto = self._crear_proyecto_base()
        proyecto.riesgo_social_probabilidad = 5
        proyecto.riesgo_social_impacto = 4  # Nivel 20 (crítico)

        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertEqual(resultado.nivel_riesgo_social, 20)
        alertas_str = ' '.join(resultado.alertas)
        self.assertIn('Social CRÍTICO', alertas_str)

    def test_riesgo_financiero_alto(self):
        """Test: Riesgo financiero alto genera alerta"""
        proyecto = self._crear_proyecto_base()
        proyecto.riesgo_financiero_probabilidad = 5
        proyecto.riesgo_financiero_impacto = 5  # Nivel 25 (crítico)

        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertEqual(resultado.nivel_riesgo_financiero, 25)
        alertas_str = ' '.join(resultado.alertas)
        self.assertIn('Financiero CRÍTICO', alertas_str)

    def test_riesgo_regulatorio_alto(self):
        """Test: Riesgo regulatorio alto genera alerta"""
        proyecto = self._crear_proyecto_base()
        proyecto.riesgo_regulatorio_probabilidad = 4
        proyecto.riesgo_regulatorio_impacto = 5  # Nivel 20 (crítico)

        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertEqual(resultado.nivel_riesgo_regulatorio, 20)
        alertas_str = ' '.join(resultado.alertas)
        self.assertIn('Regulatorio CRÍTICO', alertas_str)

    # ========== TESTS: FACTORES AUTOMÁTICOS ==========

    def test_factor_automatico_presupuesto_bajo(self):
        """Test: Presupuesto bajo → Score neutral 100.0"""
        proyecto = self._crear_proyecto_base()
        proyecto.presupuesto_total = 100_000_000  # 100M (bajo)

        score = self.criterio._calcular_factores_automaticos(proyecto)

        # Score = 100.0 (neutral, sin penalización)
        self.assertEqual(score, 100.0)

    def test_factor_automatico_presupuesto_medio(self):
        """Test: Presupuesto medio → Score neutral 100.0"""
        proyecto = self._crear_proyecto_base()
        proyecto.presupuesto_total = 600_000_000  # 600M (medio)

        score = self.criterio._calcular_factores_automaticos(proyecto)

        # Score = 100.0 (neutral, genera alerta informativa)
        self.assertEqual(score, 100.0)

    def test_factor_automatico_presupuesto_alto(self):
        """Test: Presupuesto alto → Score neutral 100.0"""
        proyecto = self._crear_proyecto_base()
        proyecto.presupuesto_total = 1_500_000_000  # 1.5B (alto)

        score = self.criterio._calcular_factores_automaticos(proyecto)

        # Score = 100.0 (neutral, genera alerta informativa)
        self.assertEqual(score, 100.0)

    def test_factor_automatico_duracion_corta(self):
        """Test: Duración corta → Score neutral 100.0"""
        proyecto = self._crear_proyecto_base()
        proyecto.duracion_estimada_meses = 6  # 6 meses

        score = self.criterio._calcular_factores_automaticos(proyecto)

        self.assertEqual(score, 100.0)

    def test_factor_automatico_duracion_media(self):
        """Test: Duración media → Score neutral 100.0"""
        proyecto = self._crear_proyecto_base()
        proyecto.duracion_estimada_meses = 18  # 18 meses

        score = self.criterio._calcular_factores_automaticos(proyecto)

        # Score = 100.0 (neutral, genera alerta informativa)
        self.assertEqual(score, 100.0)

    def test_factor_automatico_duracion_larga(self):
        """Test: Duración larga → Score neutral 100.0"""
        proyecto = self._crear_proyecto_base()
        proyecto.duracion_estimada_meses = 36  # 36 meses

        score = self.criterio._calcular_factores_automaticos(proyecto)

        # Score = 100.0 (neutral, genera alerta informativa)
        self.assertEqual(score, 100.0)

    def test_factor_automatico_multiples_departamentos(self):
        """Test: Múltiples departamentos → Score neutral 100.0"""
        proyecto = self._crear_proyecto_base()
        proyecto.departamentos = ["CUNDINAMARCA", "BOYACÁ", "TOLIMA"]  # 3 depts

        score = self.criterio._calcular_factores_automaticos(proyecto)

        # Score = 100.0 (neutral, genera alerta informativa)
        self.assertEqual(score, 100.0)

    def test_factor_automatico_acumulado(self):
        """Test: Múltiples factores → Score neutral 100.0"""
        proyecto = self._crear_proyecto_base()
        proyecto.presupuesto_total = 1_500_000_000
        proyecto.duracion_estimada_meses = 36
        proyecto.departamentos = ["CUNDINAMARCA", "BOYACÁ", "TOLIMA"]

        score = self.criterio._calcular_factores_automaticos(proyecto)

        # Score = 100.0 (neutral, genera alertas informativas)
        self.assertEqual(score, 100.0)

    # ========== TESTS: PESOS DE COMPONENTES ==========

    def test_pesos_componentes_suma_100(self):
        """Test: Pesos de componentes suman 100%"""
        suma = (
            self.criterio.PESO_TECNICO +
            self.criterio.PESO_SOCIAL +
            self.criterio.PESO_FINANCIERO +
            self.criterio.PESO_REGULATORIO +
            self.criterio.PESO_AUTOMATICOS
        )
        self.assertAlmostEqual(suma, 1.0, places=2)

    def test_peso_tecnico_correcto(self):
        """Test: Peso técnico = 30%"""
        self.assertEqual(self.criterio.PESO_TECNICO, 0.30)

    def test_peso_social_correcto(self):
        """Test: Peso social = 25%"""
        self.assertEqual(self.criterio.PESO_SOCIAL, 0.25)

    def test_peso_financiero_correcto(self):
        """Test: Peso financiero = 20%"""
        self.assertEqual(self.criterio.PESO_FINANCIERO, 0.20)

    def test_peso_regulatorio_correcto(self):
        """Test: Peso regulatorio = 15%"""
        self.assertEqual(self.criterio.PESO_REGULATORIO, 0.15)

    def test_peso_automaticos_correcto(self):
        """Test: Peso automáticos = 10%"""
        self.assertEqual(self.criterio.PESO_AUTOMATICOS, 0.10)

    # ========== TESTS: VALIDACIONES ==========

    def test_validacion_riesgos_datos_completos(self):
        """Test: Proyecto con datos completos → Validación OK"""
        proyecto = self._crear_proyecto_base()

        validacion = proyecto.validar_riesgos()

        self.assertTrue(validacion['valido'])
        self.assertEqual(len(validacion['errores']), 0)

    def test_validacion_error_riesgo_faltante(self):
        """Test: Riesgo sin probabilidad → Error de validación"""
        proyecto = self._crear_proyecto_base()
        proyecto.riesgo_tecnico_probabilidad = None

        with self.assertRaises(ValueError):
            self.criterio.evaluar(proyecto)

    def test_validacion_error_impacto_faltante(self):
        """Test: Riesgo sin impacto → Error de validación"""
        proyecto = self._crear_proyecto_base()
        proyecto.riesgo_social_impacto = None

        with self.assertRaises(ValueError):
            self.criterio.evaluar(proyecto)

    # ========== TESTS: NIVEL GENERAL DE RIESGO ==========

    def test_determinar_nivel_general_bajo(self):
        """Test: Todos los niveles bajos → Nivel general BAJO"""
        niveles = [1, 2, 3, 4]
        nivel = self.criterio._determinar_nivel_general(niveles)
        self.assertEqual(nivel, "BAJO")

    def test_determinar_nivel_general_medio(self):
        """Test: Nivel máximo 10 → Nivel general MEDIO"""
        niveles = [1, 3, 10, 5]
        nivel = self.criterio._determinar_nivel_general(niveles)
        self.assertEqual(nivel, "MEDIO")

    def test_determinar_nivel_general_alto(self):
        """Test: Nivel máximo 15 → Nivel general ALTO"""
        niveles = [5, 8, 15, 10]
        nivel = self.criterio._determinar_nivel_general(niveles)
        self.assertEqual(nivel, "ALTO")

    def test_determinar_nivel_general_critico(self):
        """Test: Nivel máximo 25 → Nivel general CRÍTICO"""
        niveles = [5, 10, 25, 12]
        nivel = self.criterio._determinar_nivel_general(niveles)
        self.assertEqual(nivel, "CRÍTICO")

    # ========== TESTS: APLICAR PESO ==========

    def test_aplicar_peso_score_100(self):
        """Test: Score 100 × 15% = 15"""
        contribucion = self.criterio.aplicar_peso(100)
        self.assertAlmostEqual(contribucion, 15.0, places=1)

    def test_aplicar_peso_score_50(self):
        """Test: Score 50 × 15% = 7.5"""
        contribucion = self.criterio.aplicar_peso(50)
        self.assertAlmostEqual(contribucion, 7.5, places=1)

    def test_aplicar_peso_score_0(self):
        """Test: Score 0 × 15% = 0"""
        contribucion = self.criterio.aplicar_peso(0)
        self.assertAlmostEqual(contribucion, 0.0, places=1)

    # ========== TESTS: RECOMENDACIONES ==========

    def test_recomendaciones_perfil_alto(self):
        """Test: Perfil de riesgo alto → Recomendaciones específicas"""
        proyecto = self._crear_proyecto_base()
        proyecto.riesgo_tecnico_probabilidad = 5
        proyecto.riesgo_tecnico_impacto = 5  # Nivel 25 (crítico)

        resultado = self.criterio.evaluar_detallado(proyecto)

        # Debe tener recomendaciones
        self.assertTrue(len(resultado.recomendaciones) > 0)

    def test_recomendaciones_riesgo_critico(self):
        """Test: Riesgo crítico → Recomienda revisar viabilidad"""
        proyecto = self._crear_proyecto_base()
        proyecto.riesgo_tecnico_probabilidad = 5
        proyecto.riesgo_tecnico_impacto = 5  # Nivel 25
        proyecto.riesgo_social_probabilidad = 5
        proyecto.riesgo_social_impacto = 4  # Nivel 20

        resultado = self.criterio.evaluar_detallado(proyecto)

        recs_str = ' '.join(resultado.recomendaciones)
        self.assertIn('CRÍTICO', recs_str)

    # ========== TESTS: RESULTADO DETALLADO ==========

    def test_resultado_detallado_estructura(self):
        """Test: Resultado detallado tiene estructura completa"""
        proyecto = self._crear_proyecto_base()
        resultado = self.criterio.evaluar_detallado(proyecto)

        # Verificar campos obligatorios
        self.assertIsNotNone(resultado.score)
        self.assertIsNotNone(resultado.nivel_general)
        self.assertIsNotNone(resultado.mensaje)
        self.assertIsInstance(resultado.alertas, list)
        self.assertIsInstance(resultado.recomendaciones, list)

    def test_resultado_detallado_niveles(self):
        """Test: Resultado detallado contiene todos los niveles"""
        proyecto = self._crear_proyecto_base()
        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertIsNotNone(resultado.nivel_riesgo_tecnico)
        self.assertIsNotNone(resultado.nivel_riesgo_social)
        self.assertIsNotNone(resultado.nivel_riesgo_financiero)
        self.assertIsNotNone(resultado.nivel_riesgo_regulatorio)

    def test_resultado_detallado_scores(self):
        """Test: Resultado detallado contiene todos los scores"""
        proyecto = self._crear_proyecto_base()
        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertIsNotNone(resultado.score_riesgo_tecnico)
        self.assertIsNotNone(resultado.score_riesgo_social)
        self.assertIsNotNone(resultado.score_riesgo_financiero)
        self.assertIsNotNone(resultado.score_riesgo_regulatorio)
        self.assertIsNotNone(resultado.score_factores_automaticos)

    def test_resultado_detallado_contribuciones(self):
        """Test: Resultado detallado contiene contribuciones ponderadas"""
        proyecto = self._crear_proyecto_base()
        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertIsNotNone(resultado.contribucion_tecnico)
        self.assertIsNotNone(resultado.contribucion_social)
        self.assertIsNotNone(resultado.contribucion_financiero)
        self.assertIsNotNone(resultado.contribucion_regulatorio)
        self.assertIsNotNone(resultado.contribucion_automaticos)

    def test_resultado_detallado_suma_contribuciones(self):
        """Test: Suma de contribuciones = score total"""
        proyecto = self._crear_proyecto_base()
        resultado = self.criterio.evaluar_detallado(proyecto)

        suma = (
            resultado.contribucion_tecnico +
            resultado.contribucion_social +
            resultado.contribucion_financiero +
            resultado.contribucion_regulatorio +
            resultado.contribucion_automaticos
        )

        self.assertAlmostEqual(suma, resultado.score, places=1)


if __name__ == '__main__':
    unittest.main()
