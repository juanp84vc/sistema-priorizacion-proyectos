import unittest
from src.criterios.stakeholders import StakeholdersCriterio, ResultadoStakeholders
from src.models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto


class TestStakeholdersCriterio(unittest.TestCase):
    """Tests para el criterio Stakeholders"""

    def setUp(self):
        self.criterio = StakeholdersCriterio()

    # ========== TESTS DE PERTINENCIA OPERACIONAL ==========

    def test_pertinencia_muy_alta_score_100(self):
        """Pertinencia MUY ALTA (5) debe dar score 100"""
        proyecto = ProyectoSocial(
            id="test-1",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=5,
            mejora_relacionamiento=3,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_pertinencia, 100.0)

    def test_pertinencia_alta_score_85(self):
        """Pertinencia ALTA (4) debe dar score 85"""
        proyecto = ProyectoSocial(
            id="test-2",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=4,
            mejora_relacionamiento=3,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_pertinencia, 85.0)

    def test_pertinencia_media_score_65(self):
        """Pertinencia MEDIA (3) debe dar score 65"""
        proyecto = ProyectoSocial(
            id="test-3",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_pertinencia, 65.0)

    def test_pertinencia_baja_score_40(self):
        """Pertinencia BAJA (2) debe dar score 40"""
        proyecto = ProyectoSocial(
            id="test-4",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=2,
            mejora_relacionamiento=3,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_pertinencia, 40.0)

    def test_pertinencia_nula_score_20(self):
        """Pertinencia NULA (1) debe dar score 20"""
        proyecto = ProyectoSocial(
            id="test-5",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=1,
            mejora_relacionamiento=3,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_pertinencia, 20.0)

    # ========== TESTS DE MEJORA RELACIONAMIENTO ==========

    def test_relacionamiento_sustancial_score_100(self):
        """Mejora SUSTANCIAL (5) debe dar score 100"""
        proyecto = ProyectoSocial(
            id="test-6",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=5,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_relacionamiento, 100.0)

    def test_relacionamiento_genera_confianza_score_85(self):
        """Genera CONFIANZA (4) debe dar score 85"""
        proyecto = ProyectoSocial(
            id="test-7",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=4,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_relacionamiento, 85.0)

    def test_relacionamiento_moderado_score_65(self):
        """Contribución MODERADA (3) debe dar score 65"""
        proyecto = ProyectoSocial(
            id="test-8",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_relacionamiento, 65.0)

    def test_relacionamiento_limitado_score_40(self):
        """Impacto LIMITADO (2) debe dar score 40"""
        proyecto = ProyectoSocial(
            id="test-9",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=2,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_relacionamiento, 40.0)

    def test_relacionamiento_no_aporta_score_20(self):
        """NO APORTA (1) debe dar score 20"""
        proyecto = ProyectoSocial(
            id="test-10",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=1,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_relacionamiento, 20.0)

    # ========== TESTS DE ALCANCE TERRITORIAL ==========

    def test_alcance_basico_1_municipio(self):
        """1 municipio NO-PDET debe dar score bajo"""
        proyecto = ProyectoSocial(
            id="test-11",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            municipios=["BOGOTÁ"],
            departamentos=["CUNDINAMARCA"],
            tiene_municipios_pdet=False,
            en_corredor_transmision=False,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test"
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        # 1 municipio = 10 pts → ~9.5/100
        self.assertLess(resultado.score_alcance, 15)
        self.assertGreater(resultado.score_alcance, 8)

    def test_alcance_pdet_aumenta_score(self):
        """Municipio PDET debe aumentar score significativamente"""
        proyecto = ProyectoSocial(
            id="test-12",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            municipios=["ABEJORRAL"],
            departamentos=["ANTIOQUIA"],
            tiene_municipios_pdet=True,
            en_corredor_transmision=False,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test"
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        # 1 municipio (10) + PDET (20) = 30 pts → ~28.6/100
        self.assertGreater(resultado.score_alcance, 25)
        self.assertLess(resultado.score_alcance, 32)

    def test_alcance_multiples_municipios(self):
        """Múltiples municipios deben aumentar score base"""
        proyecto = ProyectoSocial(
            id="test-13",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            municipios=["BOGOTÁ", "SOACHA", "CHÍA"],
            departamentos=["CUNDINAMARCA"],
            tiene_municipios_pdet=False,
            en_corredor_transmision=False,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test"
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        # 3 municipios = 30 pts → ~28.6/100
        self.assertGreater(resultado.score_alcance, 25)

    def test_alcance_multiples_departamentos_bonus(self):
        """Múltiples departamentos deben dar bonus"""
        proyecto_1_depto = ProyectoSocial(
            id="test-14",
            nombre="Test 1",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            municipios=["BOGOTÁ"],
            departamentos=["CUNDINAMARCA"],
            tiene_municipios_pdet=False,
            en_corredor_transmision=False,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test"
        )

        proyecto_2_deptos = ProyectoSocial(
            id="test-15",
            nombre="Test 2",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            municipios=["BOGOTÁ"],
            departamentos=["CUNDINAMARCA", "BOYACÁ"],
            tiene_municipios_pdet=False,
            en_corredor_transmision=False,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test"
        )

        resultado_1 = self.criterio.evaluar_detallado(proyecto_1_depto)
        resultado_2 = self.criterio.evaluar_detallado(proyecto_2_deptos)

        self.assertGreater(resultado_2.score_alcance, resultado_1.score_alcance)

    def test_alcance_corredor_transmision_bonus(self):
        """Corredor de transmisión debe dar bonus"""
        proyecto_sin = ProyectoSocial(
            id="test-16",
            nombre="Test Sin",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            municipios=["ABEJORRAL"],
            departamentos=["ANTIOQUIA"],
            tiene_municipios_pdet=True,
            en_corredor_transmision=False,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test"
        )

        proyecto_con = ProyectoSocial(
            id="test-17",
            nombre="Test Con",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            municipios=["ABEJORRAL"],
            departamentos=["ANTIOQUIA"],
            tiene_municipios_pdet=True,
            en_corredor_transmision=True,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test"
        )

        resultado_sin = self.criterio.evaluar_detallado(proyecto_sin)
        resultado_con = self.criterio.evaluar_detallado(proyecto_con)

        self.assertGreater(resultado_con.score_alcance, resultado_sin.score_alcance)

    # ========== TESTS DE STAKEHOLDERS TIPO ==========

    def test_stakeholders_ninguno_score_neutro(self):
        """Sin stakeholders especificados debe dar score neutro (50)"""
        proyecto = ProyectoSocial(
            id="test-18",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            stakeholders_involucrados=[],
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_stakeholders_tipo, 50.0)

    def test_stakeholders_autoridades_indigenas_alto(self):
        """Autoridades + indígenas debe dar score alto"""
        proyecto = ProyectoSocial(
            id="test-19",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            stakeholders_involucrados=[
                'autoridades_locales',
                'comunidades_indigenas'
            ],
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        # 25 + 25 = 50 de 110 → ~45.5/100
        self.assertGreater(resultado.score_stakeholders_tipo, 40)
        self.assertLess(resultado.score_stakeholders_tipo, 50)

    def test_stakeholders_todos_score_100(self):
        """Todos los stakeholders deben dar score 100"""
        proyecto = ProyectoSocial(
            id="test-20",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=3,
            stakeholders_involucrados=[
                'autoridades_locales',
                'lideres_comunitarios',
                'comunidades_indigenas',
                'organizaciones_sociales',
                'sector_privado',
                'academia',
                'medios_comunicacion'
            ],
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.score_stakeholders_tipo, 100.0)

    # ========== TESTS DE PONDERACIÓN ==========

    def test_pesos_componentes_suman_100(self):
        """Pesos de componentes deben sumar 100%"""
        total = (
            self.criterio.PESO_PERTINENCIA +
            self.criterio.PESO_RELACIONAMIENTO +
            self.criterio.PESO_ALCANCE +
            self.criterio.PESO_STAKEHOLDERS_TIPO
        )
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_proyecto_estrategico_alto_score(self):
        """Proyecto estratégico (pertinencia 5 + relacionamiento 5) debe tener score muy alto"""
        proyecto = ProyectoSocial(
            id="test-21",
            nombre="Proyecto Estratégico",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=5,
            mejora_relacionamiento=5,
            municipios=["ABEJORRAL", "SONSÓN", "ARGELIA"],
            departamentos=["ANTIOQUIA"],
            tiene_municipios_pdet=True,
            en_corredor_transmision=True,
            stakeholders_involucrados=[
                'autoridades_locales',
                'lideres_comunitarios',
                'comunidades_indigenas'
            ],
            presupuesto_total=500000000,
            beneficiarios_directos=2000,
            beneficiarios_indirectos=8000,
            duracion_meses=24,
            ods_vinculados=["1", "3", "10"],
            area_geografica=AreaGeografica.RURAL,
            poblacion_objetivo="Comunidades rurales"
        )

        score = self.criterio.evaluar(proyecto)
        self.assertGreater(score, 85)

    def test_proyecto_marginal_bajo_score(self):
        """Proyecto marginal (pertinencia 1 + relacionamiento 1) debe tener score bajo"""
        proyecto = ProyectoSocial(
            id="test-22",
            nombre="Proyecto Marginal",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=1,
            mejora_relacionamiento=1,
            municipios=["BOGOTÁ"],
            departamentos=["CUNDINAMARCA"],
            tiene_municipios_pdet=False,
            en_corredor_transmision=False,
            stakeholders_involucrados=[],
            presupuesto_total=100000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=200,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="General"
        )

        score = self.criterio.evaluar(proyecto)
        self.assertLess(score, 40)

    # ========== TESTS DE APLICACIÓN DE PESO ==========

    def test_peso_25_porciento(self):
        """El criterio debe tener peso del 25%"""
        self.assertEqual(self.criterio.peso, 0.25)

    def test_aplicar_peso_score_100(self):
        """Score 100 con peso 25% debe contribuir 25 puntos"""
        contribucion = self.criterio.aplicar_peso(100)
        self.assertEqual(contribucion, 25.0)

    def test_aplicar_peso_score_80(self):
        """Score 80 con peso 25% debe contribuir 20 puntos"""
        contribucion = self.criterio.aplicar_peso(80)
        self.assertEqual(contribucion, 20.0)

    # ========== TESTS DE VALIDACIÓN ==========

    def test_error_sin_pertinencia(self):
        """Debe lanzar error si pertinencia no definida"""
        proyecto = ProyectoSocial(
            id="test-23",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=None,
            mejora_relacionamiento=3,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        with self.assertRaises(ValueError):
            self.criterio.evaluar(proyecto)

    def test_error_sin_relacionamiento(self):
        """Debe lanzar error si relacionamiento no definido"""
        proyecto = ProyectoSocial(
            id="test-24",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=3,
            mejora_relacionamiento=None,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        with self.assertRaises(ValueError):
            self.criterio.evaluar(proyecto)

    # ========== TESTS DE ALERTAS ==========

    def test_alerta_pertinencia_muy_alta(self):
        """Pertinencia MUY ALTA debe generar alerta"""
        proyecto = ProyectoSocial(
            id="test-25",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=5,
            mejora_relacionamiento=3,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertTrue(
            any("MUY ALTA" in alerta for alerta in resultado.alertas)
        )

    def test_recomendacion_proyecto_estrategico(self):
        """Proyecto estratégico debe recibir recomendación de priorización"""
        proyecto = ProyectoSocial(
            id="test-26",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=5,
            mejora_relacionamiento=5,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertTrue(
            any("estratégico" in rec.lower() for rec in resultado.recomendaciones)
        )

    def test_nivel_muy_alto(self):
        """Score >= 85 debe dar nivel MUY ALTO"""
        proyecto = ProyectoSocial(
            id="test-27",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=5,
            mejora_relacionamiento=5,
            municipios=["ABEJORRAL", "SONSÓN"],
            departamentos=["ANTIOQUIA"],
            tiene_municipios_pdet=True,
            en_corredor_transmision=True,
            stakeholders_involucrados=['autoridades_locales', 'comunidades_indigenas'],
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test"
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.nivel, "MUY ALTO")

    def test_nivel_bajo(self):
        """Score < 50 debe dar nivel BAJO"""
        proyecto = ProyectoSocial(
            id="test-28",
            nombre="Test",
            organizacion="Test Org",
            descripcion="Test",
            pertinencia_operacional=1,
            mejora_relacionamiento=1,
            presupuesto_total=1000000,
            beneficiarios_directos=100,
            beneficiarios_indirectos=100,
            duracion_meses=12,
            ods_vinculados=["1"],
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Test",
            departamentos=["ANTIOQUIA"]
        )
        resultado = self.criterio.evaluar_detallado(proyecto)
        self.assertEqual(resultado.nivel, "BAJO")


if __name__ == '__main__':
    unittest.main()
