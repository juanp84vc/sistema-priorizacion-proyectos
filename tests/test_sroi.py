"""
Tests comprehensivos para el criterio SROI.
Arquitectura C - Criterio dominante (40%)

Valida:
- Conversión SROI → Score según rangos aprobados
- Gates de validación (< 1.0, > 7.0, > 5.0)
- Aplicación de peso (40%)
- Impacto vs sistema actual (incremento 10x)
"""
import unittest
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from criterios.sroi import SROICriterio, ResultadoSROI
from models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto


class TestSROICriterio(unittest.TestCase):
    """Tests para el criterio SROI"""

    def setUp(self):
        self.criterio = SROICriterio()

    # ========== TESTS DE CONVERSIÓN ==========

    def test_sroi_menor_1_score_0(self):
        """SROI < 1.0 debe retornar score 0 (RECHAZAR)"""
        proyecto = ProyectoSocial(
            id="test-1",
            nombre="Test Proyecto",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 0.8},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        score = self.criterio.evaluar(proyecto)
        self.assertEqual(score, 0.0)

    def test_sroi_exactamente_1_score_60(self):
        """SROI = 1.0 debe retornar score 60 (BAJA)"""
        proyecto = ProyectoSocial(
            id="test-2",
            nombre="Test Proyecto",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 1.0},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        score = self.criterio.evaluar(proyecto)
        self.assertEqual(score, 60.0)

    def test_sroi_1_a_2_score_60(self):
        """SROI 1.0-1.99 debe retornar score 60 (BAJA)"""
        for sroi_val in [1.0, 1.5, 1.99]:
            with self.subTest(sroi=sroi_val):
                proyecto = ProyectoSocial(
                    id=f"test-{sroi_val}",
                    nombre="Test Proyecto",
                    organizacion="Test Org",
                    descripcion="Test",
                    indicadores_impacto={'sroi': sroi_val},
                    presupuesto_total=1000000,
                    beneficiarios_directos=100,
                    beneficiarios_indirectos=200,
                    duracion_meses=12,
                    ods_vinculados=["ODS 1"],
                    area_geografica=AreaGeografica.URBANA,
                    poblacion_objetivo="General",
                    departamentos=["Antioquia"]
                )
                score = self.criterio.evaluar(proyecto)
                self.assertEqual(score, 60.0)

    def test_sroi_2_a_3_score_80(self):
        """SROI 2.0-2.99 debe retornar score 80 (MEDIA)"""
        for sroi_val in [2.0, 2.5, 2.99]:
            with self.subTest(sroi=sroi_val):
                proyecto = ProyectoSocial(
                    id=f"test-{sroi_val}",
                    nombre="Test Proyecto",
                    organizacion="Test Org",
                    descripcion="Test",
                    indicadores_impacto={'sroi': sroi_val},
                    presupuesto_total=1000000,
                    beneficiarios_directos=100,
                    beneficiarios_indirectos=200,
                    duracion_meses=12,
                    ods_vinculados=["ODS 1"],
                    area_geografica=AreaGeografica.URBANA,
                    poblacion_objetivo="General",
                    departamentos=["Antioquia"]
                )
                score = self.criterio.evaluar(proyecto)
                self.assertEqual(score, 80.0)

    def test_sroi_mayor_igual_3_score_95(self):
        """SROI ≥ 3.0 debe retornar score 95 (ALTA)"""
        for sroi_val in [3.0, 4.5, 6.0, 10.0]:
            with self.subTest(sroi=sroi_val):
                proyecto = ProyectoSocial(
                    id=f"test-{sroi_val}",
                    nombre="Test Proyecto",
                    organizacion="Test Org",
                    descripcion="Test",
                    indicadores_impacto={'sroi': sroi_val},
                    presupuesto_total=1000000,
                    beneficiarios_directos=100,
                    beneficiarios_indirectos=200,
                    duracion_meses=12,
                    ods_vinculados=["ODS 1"],
                    area_geografica=AreaGeografica.URBANA,
                    poblacion_objetivo="General",
                    departamentos=["Antioquia"]
                )
                score = self.criterio.evaluar(proyecto)
                self.assertEqual(score, 95.0)

    # ========== TESTS DE GATES DE VALIDACIÓN ==========

    def test_rechazo_automatico_sroi_menor_1(self):
        """SROI < 1.0 debe generar rechazo automático"""
        proyecto = ProyectoSocial(
            id="test-rechazo",
            nombre="Test Rechazo",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 0.5},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertEqual(resultado.score, 0.0)
        self.assertEqual(resultado.nivel, "RECHAZAR")
        self.assertTrue(resultado.requiere_observaciones)
        self.assertTrue(any("RECHAZADO" in alerta for alerta in resultado.alertas))

    def test_alerta_sroi_mayor_7(self):
        """SROI > 7.0 debe generar alerta de verificación"""
        proyecto = ProyectoSocial(
            id="test-alerta",
            nombre="Test Alerta",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 8.5},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertEqual(resultado.score, 95.0)  # Score sigue siendo 95
        self.assertEqual(resultado.nivel, "VERIFICAR")
        self.assertTrue(resultado.requiere_observaciones)
        self.assertTrue(
            any("SROI excepcional" in alerta for alerta in resultado.alertas)
        )

    def test_requiere_observaciones_sroi_mayor_5(self):
        """SROI > 5.0 debe requerir observaciones"""
        proyecto = ProyectoSocial(
            id="test-obs",
            nombre="Test Observaciones",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 5.5},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertTrue(resultado.requiere_observaciones)
        if not proyecto.observaciones_sroi:
            self.assertTrue(
                any("documentar metodología" in alerta.lower()
                    for alerta in resultado.alertas)
            )

    def test_sroi_marginal_genera_alerta(self):
        """SROI 1.0-2.0 debe generar alerta de optimización"""
        proyecto = ProyectoSocial(
            id="test-marginal",
            nombre="Test Marginal",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 1.5},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)

        self.assertTrue(
            any("SROI marginal" in alerta for alerta in resultado.alertas)
        )

    # ========== TESTS DE APLICACIÓN DE PESO ==========

    def test_peso_40_porciento(self):
        """El criterio debe tener peso del 40%"""
        self.assertEqual(self.criterio.peso, 0.40)

    def test_aplicar_peso_score_100(self):
        """Score 100 con peso 40% debe contribuir 40 puntos"""
        contribucion = self.criterio.aplicar_peso(100)
        self.assertEqual(contribucion, 40.0)

    def test_aplicar_peso_score_95(self):
        """Score 95 (SROI ≥3.0) con peso 40% debe contribuir 38 puntos"""
        contribucion = self.criterio.aplicar_peso(95)
        self.assertEqual(contribucion, 38.0)

    def test_aplicar_peso_score_80(self):
        """Score 80 (SROI 2-3) con peso 40% debe contribuir 32 puntos"""
        contribucion = self.criterio.aplicar_peso(80)
        self.assertEqual(contribucion, 32.0)

    def test_aplicar_peso_score_60(self):
        """Score 60 (SROI 1-2) con peso 40% debe contribuir 24 puntos"""
        contribucion = self.criterio.aplicar_peso(60)
        self.assertEqual(contribucion, 24.0)

    def test_aplicar_peso_score_0(self):
        """Score 0 (SROI <1) con peso 40% debe contribuir 0 puntos"""
        contribucion = self.criterio.aplicar_peso(0)
        self.assertEqual(contribucion, 0.0)

    # ========== TESTS DE VALIDACIÓN ==========

    def test_error_sroi_no_definido(self):
        """Debe lanzar error si SROI no está definido"""
        proyecto = ProyectoSocial(
            id="test-sin-sroi",
            nombre="Test Sin SROI",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={},  # Sin SROI
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        with self.assertRaises(ValueError) as context:
            self.criterio.evaluar(proyecto)
        self.assertIn("SROI no definido", str(context.exception))

    def test_error_sroi_negativo(self):
        """Debe lanzar error si SROI es negativo"""
        proyecto = ProyectoSocial(
            id="test-negativo",
            nombre="Test SROI Negativo",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': -2.0},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        with self.assertRaises(ValueError) as context:
            self.criterio.evaluar(proyecto)
        self.assertIn("no puede ser negativo", str(context.exception))

    def test_error_sroi_no_numerico(self):
        """Debe lanzar error si SROI no es numérico"""
        proyecto = ProyectoSocial(
            id="test-string",
            nombre="Test SROI String",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': "3.5"},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        with self.assertRaises(ValueError) as context:
            self.criterio.evaluar(proyecto)
        self.assertIn("debe ser numérico", str(context.exception))

    # ========== TESTS DE IMPACTO VS SISTEMA ACTUAL ==========

    def test_impacto_vs_sistema_actual_sroi_alto(self):
        """Comparar impacto SROI 4.2 en sistema actual vs Arquitectura C"""
        proyecto = ProyectoSocial(
            id="test-impacto",
            nombre="Proyecto Transformacional",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 4.2},
            presupuesto_total=500_000_000,
            beneficiarios_directos=2000,
            beneficiarios_indirectos=5000,
            duracion_meses=24,
            ods_vinculados=["ODS 1", "ODS 2"],
            area_geografica=AreaGeografica.RURAL,
            poblacion_objetivo="Campesinos",
            departamentos=["Caquetá"]
        )

        # Arquitectura C (nuevo)
        score_nuevo = self.criterio.evaluar(proyecto)
        contribucion_nueva = self.criterio.aplicar_peso(score_nuevo)

        # Sistema actual (viejo): SROI era 3.75% = 0.0375
        # SROI 4.2 → Score ~95 en bonus → 95 × 0.15 = 14.25
        # Contribución total: 14.25 × 0.25 = 3.56 puntos
        contribucion_vieja = 3.56

        # Nueva contribución debe ser ~10x mayor
        self.assertEqual(score_nuevo, 95.0)
        self.assertEqual(contribucion_nueva, 38.0)
        self.assertGreater(contribucion_nueva / contribucion_vieja, 10)

        # Diferencia: 38 - 3.56 = 34.44 puntos más
        diferencia = contribucion_nueva - contribucion_vieja
        self.assertAlmostEqual(diferencia, 34.44, delta=0.5)

    # ========== TESTS DE NIVELES DE PRIORIDAD ==========

    def test_get_nivel_prioridad_rechazar(self):
        """Score 0 debe mapear a RECHAZAR"""
        nivel = self.criterio.get_nivel_prioridad(0)
        self.assertEqual(nivel, "RECHAZAR")

    def test_get_nivel_prioridad_baja(self):
        """Score 60 debe mapear a BAJA"""
        nivel = self.criterio.get_nivel_prioridad(60)
        self.assertEqual(nivel, "BAJA")

    def test_get_nivel_prioridad_media(self):
        """Score 80 debe mapear a MEDIA"""
        nivel = self.criterio.get_nivel_prioridad(80)
        self.assertEqual(nivel, "MEDIA")

    def test_get_nivel_prioridad_alta(self):
        """Score 95 debe mapear a ALTA"""
        nivel = self.criterio.get_nivel_prioridad(95)
        self.assertEqual(nivel, "ALTA")


class TestProyectoSROIValidacion(unittest.TestCase):
    """Tests para método validar_sroi() en ProyectoSocial"""

    def test_validacion_sroi_rechazar(self):
        """SROI < 1.0 debe marcar como no válido"""
        proyecto = ProyectoSocial(
            id="test-val-1",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 0.7},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        validacion = proyecto.validar_sroi()

        self.assertFalse(validacion['valido'])
        self.assertEqual(validacion['nivel'], 'RECHAZAR')
        self.assertTrue(validacion['requiere_observaciones'])

    def test_validacion_sroi_verificar(self):
        """SROI > 7.0 debe marcar como verificar"""
        proyecto = ProyectoSocial(
            id="test-val-2",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 9.0},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        validacion = proyecto.validar_sroi()

        self.assertTrue(validacion['valido'])
        self.assertEqual(validacion['nivel'], 'VERIFICAR')
        self.assertTrue(validacion['requiere_observaciones'])

    def test_validacion_sroi_alta(self):
        """SROI ≥ 3.0 debe marcar como alta"""
        proyecto = ProyectoSocial(
            id="test-val-3",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 4.5},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        validacion = proyecto.validar_sroi()

        self.assertTrue(validacion['valido'])
        self.assertEqual(validacion['nivel'], 'ALTA')

    def test_validacion_sroi_media(self):
        """SROI 2.0-2.99 debe marcar como media"""
        proyecto = ProyectoSocial(
            id="test-val-4",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 2.5},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        validacion = proyecto.validar_sroi()

        self.assertTrue(validacion['valido'])
        self.assertEqual(validacion['nivel'], 'MEDIA')

    def test_validacion_sroi_baja(self):
        """SROI 1.0-1.99 debe marcar como baja"""
        proyecto = ProyectoSocial(
            id="test-val-5",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            indicadores_impacto={'sroi': 1.5},
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["ODS 1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General",
            departamentos=["Antioquia"]
        )
        validacion = proyecto.validar_sroi()

        self.assertTrue(validacion['valido'])
        self.assertEqual(validacion['nivel'], 'BAJA')


if __name__ == '__main__':
    unittest.main()
