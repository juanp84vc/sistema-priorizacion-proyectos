"""
Tests de integración para MotorScoringArquitecturaC

Valida:
- Funcionamiento completo del motor
- Gate de elegibilidad PDET/ZOMAC (Ajuste CONFIS Feb 2026)
- Integración de criterios SROI, Stakeholders, Probabilidad CONFIS y Riesgos
- Cálculo correcto de scores
- Gates de validación
"""
import unittest
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scoring.motor_arquitectura_c import MotorScoringArquitecturaC, calcular_score_proyecto
from src.models.proyecto import ProyectoSocial, AreaGeografica


class TestMotorScoringArquitecturaC(unittest.TestCase):
    """Tests para motor de scoring Arquitectura C"""

    def setUp(self):
        self.motor = MotorScoringArquitecturaC()

    def _crear_proyecto_base(self, **kwargs):
        """Helper para crear proyecto con valores por defecto."""
        defaults = {
            'id': "TEST-000",
            'nombre': "Proyecto Test",
            'organizacion': "Test Org",
            'descripcion': "Test",
            'indicadores_impacto': {'sroi': 2.5},
            'presupuesto_total': 300_000_000,
            'beneficiarios_directos': 1000,
            'beneficiarios_indirectos': 3000,
            'duracion_meses': 24,
            'ods_vinculados': ["ODS 6"],
            'area_geografica': AreaGeografica.RURAL,
            'poblacion_objetivo': "Comunidades rurales",
            'departamentos': ["ANTIOQUIA"],
            'municipios': ["ABEJORRAL"],
            'sectores': ["Alcantarillado"],
            'tiene_municipios_pdet': True,
            'tipo_municipio': "PDET",
            'pertinencia_operacional': 3,
            'mejora_relacionamiento': 3,
            'riesgo_tecnico_probabilidad': 2,
            'riesgo_tecnico_impacto': 2,
            'riesgo_social_probabilidad': 2,
            'riesgo_social_impacto': 2,
            'riesgo_financiero_probabilidad': 2,
            'riesgo_financiero_impacto': 2,
            'riesgo_regulatorio_probabilidad': 2,
            'riesgo_regulatorio_impacto': 2,
            'duracion_estimada_meses': 24
        }
        defaults.update(kwargs)
        return ProyectoSocial(**defaults)

    def test_pesos_suman_100(self):
        """Verificar que pesos suman 100%"""
        total = (
            self.motor.PESO_SROI +
            self.motor.PESO_STAKEHOLDERS +
            self.motor.PESO_PROBABILIDAD +
            self.motor.PESO_RIESGOS
        )
        self.assertAlmostEqual(total, 1.0, places=2)

    # ========== GATE ELEGIBILIDAD PDET/ZOMAC ==========

    def test_gate_no_elegible_sin_pdet(self):
        """Proyecto NO PDET/ZOMAC debe ser NO ELEGIBLE (Gate CONFIS)"""
        proyecto = self._crear_proyecto_base(
            id="TEST-GATE-01",
            tiene_municipios_pdet=False,
            tipo_municipio=None,
            municipios=["BOGOTÁ"],
            departamentos=["CUNDINAMARCA"]
        )

        resultado = self.motor.calcular_score(proyecto)

        self.assertEqual(resultado.score_total, 0)
        self.assertEqual(resultado.nivel_prioridad, "NO ELEGIBLE")
        self.assertTrue(any("NO ELEGIBLE" in a for a in resultado.alertas))

    def test_gate_elegible_pdet(self):
        """Proyecto PDET debe pasar el gate y obtener score > 0"""
        proyecto = self._crear_proyecto_base(
            id="TEST-GATE-02",
            tiene_municipios_pdet=True,
            tipo_municipio="PDET"
        )

        resultado = self.motor.calcular_score(proyecto)

        self.assertGreater(resultado.score_total, 0)
        self.assertNotEqual(resultado.nivel_prioridad, "NO ELEGIBLE")

    def test_gate_elegible_zomac(self):
        """Proyecto ZOMAC debe pasar el gate"""
        proyecto = self._crear_proyecto_base(
            id="TEST-GATE-03",
            tiene_municipios_pdet=False,
            tipo_municipio="ZOMAC"
        )

        resultado = self.motor.calcular_score(proyecto)

        self.assertGreater(resultado.score_total, 0)
        self.assertNotEqual(resultado.nivel_prioridad, "NO ELEGIBLE")

    def test_gate_elegible_amazonia(self):
        """Proyecto Amazonía debe pasar el gate"""
        proyecto = self._crear_proyecto_base(
            id="TEST-GATE-04",
            tiene_municipios_pdet=False,
            tipo_municipio="AMAZONIA"
        )

        resultado = self.motor.calcular_score(proyecto)

        self.assertGreater(resultado.score_total, 0)

    # ========== SROI ==========

    def test_proyecto_alta_prioridad_pdet_sroi_alto(self):
        """Proyecto con SROI alto y PDET debe tener score muy alto"""
        proyecto = self._crear_proyecto_base(
            id="TEST-001",
            nombre="Proyecto Alta Prioridad",
            indicadores_impacto={'sroi': 4.5},
            puntajes_pdet={"Alcantarillado": 10},
            puntaje_sectorial_max=10,
            puntaje_territorial_confis=8.0,
            pertinencia_operacional=5,
            mejora_relacionamiento=5,
            en_corredor_transmision=True,
            stakeholders_involucrados=['autoridades_locales', 'comunidades_indigenas', 'lideres_comunitarios'],
        )

        resultado = self.motor.calcular_score(proyecto)

        # Score debe ser muy alto
        self.assertGreater(resultado.score_total, 80)
        self.assertIn(resultado.nivel_prioridad, ["ALTA", "MUY ALTA"])

        # SROI 4.5 → 98.0 (techo) → contribución = 98.0 × 0.40 = 39.2
        self.assertAlmostEqual(resultado.contribucion_sroi, 39.2, delta=1)

    def test_proyecto_rechazado_sroi_menor_1(self):
        """Proyecto con SROI < 1.0 debe ser rechazado"""
        proyecto = self._crear_proyecto_base(
            id="TEST-002",
            nombre="Proyecto Rechazado",
            indicadores_impacto={'sroi': 0.8},
            riesgo_tecnico_probabilidad=1,
            riesgo_tecnico_impacto=1,
            riesgo_social_probabilidad=1,
            riesgo_social_impacto=1,
            riesgo_financiero_probabilidad=1,
            riesgo_financiero_impacto=1,
            riesgo_regulatorio_probabilidad=1,
            riesgo_regulatorio_impacto=1,
        )

        resultado = self.motor.calcular_score(proyecto)

        self.assertEqual(resultado.score_sroi, 0.0)
        self.assertEqual(resultado.contribucion_sroi, 0.0)
        self.assertEqual(resultado.nivel_prioridad, "RECHAZADO")
        self.assertTrue(any("RECHAZADO" in alerta for alerta in resultado.alertas))

    # ========== PROBABILIDAD CONFIS ==========

    def test_probabilidad_confis_grupo_pdet(self):
        """Proyecto PDET sin estructuración → Grupo 4"""
        proyecto = self._crear_proyecto_base(
            id="TEST-CONFIS-01",
            tipo_municipio="PDET",
            es_patr_pdet=False,
            contribuyente_paga_estructuracion=False,
            puntaje_territorial_confis=7.0,
            puntaje_sectorial_max=8,
        )

        resultado = self.motor.calcular_score(proyecto)

        # Grupo 4 score = 70
        # Territorial 7 + Sectorial 8 = 15 → (15/20)*100 = 75
        # Score prob = 70*0.20 + 75*0.80 = 14 + 60 = 74
        self.assertGreater(resultado.score_probabilidad, 60)

    def test_probabilidad_confis_patr_pdet_con_estructuracion(self):
        """Proyecto PATR-PDET con estructuración → Grupo 1 (máxima prioridad)"""
        proyecto = self._crear_proyecto_base(
            id="TEST-CONFIS-02",
            tipo_municipio="PDET",
            es_patr_pdet=True,
            contribuyente_paga_estructuracion=True,
            puntaje_territorial_confis=9.0,
            puntaje_sectorial_max=9,
        )

        resultado = self.motor.calcular_score(proyecto)

        # Grupo 1 score = 100
        # Territorial 9 + Sectorial 9 = 18 → (18/20)*100 = 90
        # Score prob = 100*0.20 + 90*0.80 = 20 + 72 = 92
        self.assertGreater(resultado.score_probabilidad, 85)

    # ========== COMPARACIÓN SISTEMA VIEJO ==========

    def test_comparacion_impacto_vs_sistema_viejo(self):
        """Comparar impacto SROI vs sistema anterior (incremento 10x)"""
        proyecto = self._crear_proyecto_base(
            id="TEST-004",
            indicadores_impacto={'sroi': 4.2},
            puntajes_pdet={"Alcantarillado": 10},
            puntaje_sectorial_max=10,
            pertinencia_operacional=4,
            mejora_relacionamiento=4,
        )

        resultado = self.motor.calcular_score(proyecto)

        # Sistema nuevo: SROI 4.2 → 98.0 (techo) → contribuye 98.0 × 0.40 = 39.2
        contribucion_nueva = resultado.contribucion_sroi
        contribucion_vieja = 3.56

        factor = contribucion_nueva / contribucion_vieja
        self.assertGreater(factor, 10)

    # ========== REPORTE ==========

    def test_generar_reporte(self):
        """Test de generación de reporte"""
        proyecto = self._crear_proyecto_base(
            id="TEST-005",
            indicadores_impacto={'sroi': 3.0},
            riesgo_tecnico_probabilidad=3,
            riesgo_tecnico_impacto=3,
            riesgo_social_probabilidad=3,
            riesgo_social_impacto=3,
            riesgo_financiero_probabilidad=3,
            riesgo_financiero_impacto=3,
            riesgo_regulatorio_probabilidad=3,
            riesgo_regulatorio_impacto=3,
        )

        resultado = self.motor.calcular_score(proyecto)
        reporte = self.motor.generar_reporte(resultado)

        self.assertIn("SCORE TOTAL", reporte)
        self.assertIn("SROI", reporte)
        self.assertIn("Stakeholders", reporte)
        self.assertIn("Prob. Aprobación", reporte)
        self.assertIn("Riesgos", reporte)
        self.assertIn("40%", reporte)
        self.assertIn("20%", reporte)

    # ========== HELPER FUNCTION ==========

    def test_helper_function_calcular_score_proyecto(self):
        """Test de función helper"""
        proyecto = self._crear_proyecto_base(
            id="TEST-006",
            indicadores_impacto={'sroi': 2.5},
        )

        resultado = calcular_score_proyecto(proyecto)

        self.assertIsNotNone(resultado)
        self.assertGreater(resultado.score_total, 0)
        self.assertEqual(resultado.version_arquitectura, "C")

    # ========== ALCANCE TERRITORIAL CONFIS ==========

    def test_alcance_territorial_con_puntaje_confis(self):
        """Alcance territorial debe usar puntaje CONFIS territorial"""
        proyecto_alto = self._crear_proyecto_base(
            id="TEST-ALC-01",
            puntaje_territorial_confis=9.0,
            en_corredor_transmision=True,
        )
        proyecto_bajo = self._crear_proyecto_base(
            id="TEST-ALC-02",
            puntaje_territorial_confis=2.0,
            en_corredor_transmision=False,
        )

        resultado_alto = self.motor.calcular_score(proyecto_alto)
        resultado_bajo = self.motor.calcular_score(proyecto_bajo)

        # Proyecto con territorial alto debe tener mejor score stakeholders
        self.assertGreater(resultado_alto.score_stakeholders, resultado_bajo.score_stakeholders)


if __name__ == '__main__':
    unittest.main()
