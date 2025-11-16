"""
Tests de integración para MotorScoringArquitecturaC

Valida:
- Funcionamiento completo del motor
- Integración de criterios SROI y Probabilidad PDET
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

    def test_pesos_suman_100(self):
        """Verificar que pesos suman 100%"""
        total = (
            self.motor.PESO_SROI +
            self.motor.PESO_STAKEHOLDERS +
            self.motor.PESO_PROBABILIDAD +
            self.motor.PESO_RIESGOS
        )
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_proyecto_alta_prioridad_pdet_sroi_alto(self):
        """Proyecto con SROI alto y PDET debe tener score muy alto"""
        proyecto = ProyectoSocial(
            id="TEST-001",
            nombre="Proyecto Alta Prioridad",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 4.5},
            presupuesto_total=500_000_000,
            beneficiarios_directos=2000,
            beneficiarios_indirectos=8000,
            duracion_meses=24,
            ods_vinculados=["ODS 6"],
            area_geografica=AreaGeografica.RURAL,
            poblacion_objetivo="Comunidades rurales",
            departamentos=["ANTIOQUIA"],
            municipios=["ABEJORRAL"],
            sectores=["Alcantarillado"],
            tiene_municipios_pdet=True,
            puntajes_pdet={"Alcantarillado": 10},
            puntaje_sectorial_max=10
        )

        resultado = self.motor.calcular_score(proyecto)

        # Score debe ser muy alto
        self.assertGreater(resultado.score_total, 85)
        self.assertIn(resultado.nivel_prioridad, ["ALTA", "MUY ALTA"])

        # SROI debe contribuir ~38 puntos (95 × 0.40)
        self.assertAlmostEqual(resultado.contribucion_sroi, 38.0, delta=1)

        # Prob. Aprobación debe contribuir ~20 puntos (100 × 0.20)
        self.assertAlmostEqual(resultado.contribucion_probabilidad, 20.0, delta=1)

    def test_proyecto_rechazado_sroi_menor_1(self):
        """Proyecto con SROI < 1.0 debe ser rechazado"""
        proyecto = ProyectoSocial(
            id="TEST-002",
            nombre="Proyecto Rechazado",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 0.8},
            presupuesto_total=100_000_000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["ANTIOQUIA"],
            municipios=["ABEJORRAL"]
        )

        resultado = self.motor.calcular_score(proyecto)

        self.assertEqual(resultado.score_sroi, 0.0)
        self.assertEqual(resultado.contribucion_sroi, 0.0)
        self.assertEqual(resultado.nivel_prioridad, "RECHAZADO")
        self.assertTrue(any("RECHAZADO" in alerta for alerta in resultado.alertas))

    def test_proyecto_no_pdet_score_probabilidad_cero(self):
        """Proyecto NO-PDET debe tener score 0 en probabilidad"""
        proyecto = ProyectoSocial(
            id="TEST-003",
            nombre="Proyecto No PDET",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 3.5},
            presupuesto_total=300_000_000,
            beneficiarios_directos=1000,
            beneficiarios_indirectos=3000,
            duracion_meses=24,
            ods_vinculados=["ODS 4"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["CUNDINAMARCA"],
            municipios=["BOGOTÁ"],
            tiene_municipios_pdet=False
        )

        resultado = self.motor.calcular_score(proyecto)

        # Probabilidad debe ser 0
        self.assertEqual(resultado.score_probabilidad, 0.0)
        self.assertEqual(resultado.contribucion_probabilidad, 0.0)

        # Pero SROI debe aportar
        self.assertGreater(resultado.contribucion_sroi, 0)

    def test_comparacion_impacto_vs_sistema_viejo(self):
        """Comparar impacto SROI vs sistema anterior (incremento 10x)"""
        proyecto = ProyectoSocial(
            id="TEST-004",
            nombre="Proyecto Comparación",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 4.2},
            presupuesto_total=500_000_000,
            beneficiarios_directos=2000,
            beneficiarios_indirectos=8000,
            duracion_meses=24,
            ods_vinculados=["ODS 6"],
            area_geografica=AreaGeografica.RURAL,
            poblacion_objetivo="Comunidades",
            departamentos=["ANTIOQUIA"],
            municipios=["ABEJORRAL"],
            sectores=["Alcantarillado"],
            tiene_municipios_pdet=True,
            puntajes_pdet={"Alcantarillado": 10},
            puntaje_sectorial_max=10
        )

        resultado = self.motor.calcular_score(proyecto)

        # Sistema nuevo: SROI contribuye ~38 puntos
        contribucion_nueva = resultado.contribucion_sroi

        # Sistema viejo: SROI contribuía ~3.56 puntos
        contribucion_vieja = 3.56

        # Diferencia debe ser ~10x
        factor = contribucion_nueva / contribucion_vieja
        self.assertGreater(factor, 10)

    def test_generar_reporte(self):
        """Test de generación de reporte"""
        proyecto = ProyectoSocial(
            id="TEST-005",
            nombre="Proyecto Test Reporte",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 3.0},
            presupuesto_total=200_000_000,
            beneficiarios_directos=500,
            beneficiarios_indirectos=2000,
            duracion_meses=24,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.RURAL,
            poblacion_objetivo="General",
            departamentos=["ANTIOQUIA"],
            municipios=["ABEJORRAL"]
        )

        resultado = self.motor.calcular_score(proyecto)
        reporte = self.motor.generar_reporte(resultado)

        # Verificar que reporte contiene info clave
        self.assertIn("SCORE TOTAL", reporte)
        self.assertIn("SROI", reporte)
        self.assertIn("Stakeholders", reporte)
        self.assertIn("Prob. Aprobación", reporte)
        self.assertIn("Riesgos", reporte)
        self.assertIn("40%", reporte)  # Peso SROI
        self.assertIn("20%", reporte)  # Peso Probabilidad

    def test_helper_function_calcular_score_proyecto(self):
        """Test de función helper"""
        proyecto = ProyectoSocial(
            id="TEST-006",
            nombre="Test Helper",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 2.5},
            presupuesto_total=150_000_000,
            beneficiarios_directos=300,
            beneficiarios_indirectos=1000,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.RURAL,
            poblacion_objetivo="General",
            departamentos=["ANTIOQUIA"],
            municipios=["ABEJORRAL"]
        )

        resultado = calcular_score_proyecto(proyecto)

        self.assertIsNotNone(resultado)
        self.assertGreater(resultado.score_total, 0)
        self.assertEqual(resultado.version_arquitectura, "C")


if __name__ == '__main__':
    unittest.main()
