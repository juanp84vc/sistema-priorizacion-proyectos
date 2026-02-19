"""
Tests unitarios para matriz PDET/ZOMAC y criterio de probabilidad.

Valida:
1. Repositorio matriz PDET (carga y consultas)
2. Integración con criterio de probabilidad de aprobación
3. Scoring con datos oficiales PDET/ZOMAC
"""
import pytest
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.matriz_pdet_repository import MatrizPDETRepository
from criterios.probabilidad_aprobacion_pdet import ProbabilidadAprobacionCriterio
from models.proyecto import ProyectoSocial, AreaGeografica


class TestMatrizPDET:
    """Tests del repositorio matriz PDET/ZOMAC"""

    @pytest.fixture
    def repo(self):
        """Repositorio con datos cargados"""
        db_path = str(Path(__file__).parent.parent / "data" / "proyectos.db")
        return MatrizPDETRepository(db_path)

    def test_total_municipios(self, repo):
        """Verifica total de municipios cargados"""
        total = repo.get_total_municipios()
        # Esperamos 362 municipios únicos (pueden haber registros duplicados)
        assert total >= 362, f"Esperado >= 362 municipios, encontrado: {total}"
        print(f"\n✅ Total municipios en BD: {total}")

    def test_municipio_existe(self, repo):
        """Verifica que Abejorral (Antioquia) existe en matriz"""
        registro = repo.get_municipio("ANTIOQUIA", "ABEJORRAL")
        assert registro is not None, "Abejorral debería existir en matriz PDET"
        assert registro.municipio == "ABEJORRAL"
        assert registro.departamento == "ANTIOQUIA"
        print(f"\n✅ Abejorral encontrado: {registro}")

    def test_puntajes_abejorral(self, repo):
        """Verifica puntajes sectoriales de Abejorral"""
        registro = repo.get_municipio("ANTIOQUIA", "ABEJORRAL")
        assert registro is not None

        # Verificar puntajes conocidos
        assert registro.alcantarillado == 10, "Alcantarillado debería ser 10"
        assert registro.infraestructura_rural == 9, "Infra Rural debería ser 9"
        assert registro.banda_ancha == 8, "Banda Ancha debería ser 8"

        print(f"\n✅ Puntajes Abejorral verificados:")
        print(f"   Alcantarillado: {registro.alcantarillado}/10")
        print(f"   Infra Rural: {registro.infraestructura_rural}/10")
        print(f"   Banda Ancha: {registro.banda_ancha}/10")

    def test_get_puntaje_sector(self, repo):
        """Verifica método get_puntaje_sector()"""
        registro = repo.get_municipio("ANTIOQUIA", "ABEJORRAL")
        assert registro is not None

        # Probar diferentes nombres de sector
        assert registro.get_puntaje_sector("Alcantarillado") == 10
        assert registro.get_puntaje_sector("Infraestructura Rural") == 9
        assert registro.get_puntaje_sector("Banda Ancha") == 8
        assert registro.get_puntaje_sector("Salud") == 3

        # Sector inexistente
        assert registro.get_puntaje_sector("Inexistente") == 0

        print(f"\n✅ get_puntaje_sector() funciona correctamente")

    def test_municipio_no_pdet(self, repo):
        """Verifica que municipios no-PDET retornan None"""
        # Bogotá no debería estar en matriz PDET/ZOMAC
        registro = repo.get_municipio("CUNDINAMARCA", "BOGOTÁ")
        assert registro is None, "Bogotá no debería estar en matriz PDET"
        print(f"\n✅ Municipios no-PDET retornan None correctamente")

    def test_es_municipio_pdet(self, repo):
        """Verifica método es_municipio_pdet()"""
        assert repo.es_municipio_pdet("ABEJORRAL", "ANTIOQUIA") is True
        assert repo.es_municipio_pdet("BOGOTÁ", "CUNDINAMARCA") is False
        print(f"\n✅ es_municipio_pdet() funciona correctamente")

    def test_get_sectores_ordenados(self, repo):
        """Verifica ordenamiento de sectores por puntaje"""
        registro = repo.get_municipio("ANTIOQUIA", "ABEJORRAL")
        assert registro is not None

        sectores_ordenados = registro.get_sectores_ordenados()

        # Primeros 3 deberían ser los de mayor puntaje
        assert sectores_ordenados[0][0] == "Alcantarillado"
        assert sectores_ordenados[0][1] == 10

        print(f"\n✅ Sectores ordenados de Abejorral:")
        for sector, puntaje in sectores_ordenados[:5]:
            print(f"   {sector}: {puntaje}/10")

    def test_get_departamentos(self, repo):
        """Verifica lista de departamentos PDET"""
        departamentos = repo.get_departamentos()
        assert len(departamentos) > 0
        assert "ANTIOQUIA" in departamentos
        print(f"\n✅ {len(departamentos)} departamentos PDET encontrados")


class TestProbabilidadConPDET:
    """Tests del criterio de probabilidad con integración PDET"""

    @pytest.fixture
    def criterio(self):
        """Criterio de probabilidad configurado"""
        db_path = str(Path(__file__).parent.parent / "data" / "proyectos.db")
        return ProbabilidadAprobacionCriterio(peso=0.20, db_path=db_path)

    @pytest.fixture
    def proyecto_pdet_alta_prioridad(self):
        """Proyecto en municipio PDET con sector de alta prioridad"""
        return ProyectoSocial(
            id="P001",
            nombre="Proyecto Alcantarillado Abejorral",
            organizacion="ONG Test",
            descripcion="Mejoramiento de alcantarillado",
            beneficiarios_directos=500,
            beneficiarios_indirectos=2000,
            duracion_meses=12,
            presupuesto_total=100000000,
            ods_vinculados=["3", "6", "11"],  # 3 ODS prioritarios
            area_geografica=AreaGeografica.RURAL,
            poblacion_objetivo="Niños y adultos mayores",
            departamentos=["ANTIOQUIA"],
            municipios=["ABEJORRAL"],
            sectores=["Alcantarillado"]  # Sector con puntaje 10 en Abejorral
        )

    @pytest.fixture
    def proyecto_pdet_baja_prioridad(self):
        """Proyecto en municipio PDET con sector de baja prioridad"""
        return ProyectoSocial(
            id="P002",
            nombre="Proyecto Salud Abejorral",
            organizacion="ONG Test",
            descripcion="Centro de salud",
            beneficiarios_directos=300,
            beneficiarios_indirectos=1200,
            duracion_meses=18,
            presupuesto_total=150000000,
            ods_vinculados=["3"],  # 1 ODS prioritario
            area_geografica=AreaGeografica.RURAL,
            poblacion_objetivo="Población general",
            departamentos=["ANTIOQUIA"],
            municipios=["ABEJORRAL"],
            sectores=["Salud"]  # Sector con puntaje 3 en Abejorral
        )

    @pytest.fixture
    def proyecto_no_pdet(self):
        """Proyecto en municipio NO-PDET"""
        return ProyectoSocial(
            id="P003",
            nombre="Proyecto Educación Bogotá",
            organizacion="ONG Test",
            descripcion="Escuela en Bogotá",
            beneficiarios_directos=800,
            beneficiarios_indirectos=3200,
            duracion_meses=24,
            presupuesto_total=200000000,
            ods_vinculados=["4", "10"],  # 2 ODS prioritarios
            area_geografica=AreaGeografica.URBANA,
            poblacion_objetivo="Niños y adolescentes",
            departamentos=["CUNDINAMARCA"],
            municipios=["BOGOTÁ"],
            sectores=["Educación"]
        )

    def test_evaluacion_pdet_alta_prioridad(self, criterio, proyecto_pdet_alta_prioridad):
        """Proyecto con sector de alta prioridad PDET debe tener score alto"""
        score = criterio.evaluar(proyecto_pdet_alta_prioridad)

        # CONFIS (Feb 2026): Grupo 4 (PDET sin estruc.) = 70
        # Territorial 5.0 (default) + Sectorial 10 = 15 → (15/20)*100 = 75
        # Score = 70*0.20 + 75*0.80 = 14 + 60 = 74
        assert score > 70, f"Score esperado >70, obtenido: {score}"
        assert score < 80, f"Score esperado <80, obtenido: {score}"

        # Verificar metadata
        assert proyecto_pdet_alta_prioridad.tiene_municipios_pdet is True
        assert proyecto_pdet_alta_prioridad.puntaje_sectorial_max == 10

        print(f"\n✅ Proyecto alta prioridad PDET (CONFIS):")
        print(f"   Score: {score:.1f}/100")
        print(f"   Grupo CONFIS: {proyecto_pdet_alta_prioridad.grupo_priorizacion_confis}")
        print(f"   Probabilidad: {criterio.score_a_probabilidad(score)}")

    def test_evaluacion_pdet_baja_prioridad(self, criterio, proyecto_pdet_baja_prioridad):
        """Proyecto con sector de baja prioridad PDET debe tener score más bajo"""
        score = criterio.evaluar(proyecto_pdet_baja_prioridad)

        # CONFIS (Feb 2026): Grupo 4 = 70
        # Territorial 5.0 (default) + Sectorial 3 = 8 → (8/20)*100 = 40
        # Score = 70*0.20 + 40*0.80 = 14 + 32 = 46
        assert score > 40, f"Score esperado >40, obtenido: {score}"
        assert score < 55, f"Score esperado <55, obtenido: {score}"

        assert proyecto_pdet_baja_prioridad.tiene_municipios_pdet is True
        assert proyecto_pdet_baja_prioridad.puntaje_sectorial_max == 3

        print(f"\n✅ Proyecto baja prioridad PDET (CONFIS):")
        print(f"   Score: {score:.1f}/100")
        print(f"   Grupo CONFIS: {proyecto_pdet_baja_prioridad.grupo_priorizacion_confis}")
        print(f"   Probabilidad: {criterio.score_a_probabilidad(score)}")

    def test_evaluacion_no_pdet(self, criterio, proyecto_no_pdet):
        """Proyecto en municipio NO-PDET obtiene score CONFIS con defaults neutros.
        Nota: el gate de elegibilidad ahora está en el motor, no en el criterio."""
        score = criterio.evaluar(proyecto_no_pdet)

        # CONFIS (Feb 2026): Sin datos en DB → defaults neutros
        # Grupo 4 (PDET default) = 70, Territorial 5.0, Sectorial 5.0
        # Score = 70*0.20 + ((5+5)/20)*100*0.80 = 14 + 40 = 54
        # Nota: El gate de elegibilidad ahora se maneja en el motor,
        # no en el criterio individual
        assert score > 45, f"Score esperado >45, obtenido: {score}"
        assert score < 60, f"Score esperado <60, obtenido: {score}"

        print(f"\n✅ Proyecto NO-PDET (score CONFIS con defaults):")
        print(f"   Score: {score:.1f}/100")
        print(f"   Nota: Gate de elegibilidad se maneja en motor_arquitectura_c")

    def test_detalles_evaluacion(self, criterio, proyecto_pdet_alta_prioridad):
        """Verifica método get_detalles_evaluacion() con estructura CONFIS"""
        detalles = criterio.get_detalles_evaluacion(proyecto_pdet_alta_prioridad)

        assert "probabilidad_nivel" in detalles
        assert "score_total" in detalles
        assert "componentes" in detalles
        # CONFIS (Feb 2026): 2 componentes: grupo_priorizacion + score_confis
        assert "grupo_priorizacion" in detalles["componentes"]
        assert "score_confis" in detalles["componentes"]

        # Verificar estructura CONFIS
        assert len(detalles["componentes"]) == 2
        assert detalles["componentes"]["grupo_priorizacion"]["peso"] == 0.20
        assert detalles["componentes"]["score_confis"]["peso"] == 0.80

        print(f"\n✅ Detalles de evaluación CONFIS:")
        print(f"   Nivel: {detalles['probabilidad_nivel']}")
        print(f"   Score total: {detalles['score_total']:.1f}")
        grupo = detalles["componentes"]["grupo_priorizacion"]
        confis = detalles["componentes"]["score_confis"]
        print(f"   Grupo: {grupo['grupo']} ({grupo['nombre']})")
        print(f"   Territorial: {confis['territorial']}, Sectorial: {confis['sectorial']}")

    def test_comparacion_alta_vs_baja_prioridad(
        self,
        criterio,
        proyecto_pdet_alta_prioridad,
        proyecto_pdet_baja_prioridad
    ):
        """Proyecto con alta prioridad PDET debe tener score mayor que baja prioridad"""
        score_alta = criterio.evaluar(proyecto_pdet_alta_prioridad)
        score_baja = criterio.evaluar(proyecto_pdet_baja_prioridad)

        # CONFIS: Alta > Baja (sectorial 10 vs 3, mismo grupo)
        assert score_alta > score_baja, (
            f"Score alta ({score_alta}) debe ser > baja ({score_baja})"
        )

        diferencia = score_alta - score_baja
        assert diferencia > 15, f"Diferencia esperada >15, obtenida: {diferencia}"

        print(f"\n✅ Comparación alta vs baja prioridad (CONFIS):")
        print(f"   Alta: {score_alta:.1f} ({criterio.score_a_probabilidad(score_alta)})")
        print(f"   Baja: {score_baja:.1f} ({criterio.score_a_probabilidad(score_baja)})")
        print(f"   Diferencia: {diferencia:.1f} puntos")

    def test_multiples_sectores(self, criterio):
        """Proyecto con múltiples sectores debe usar el puntaje MÁXIMO"""
        proyecto = ProyectoSocial(
            id="P004",
            nombre="Proyecto Multi-Sectorial",
            organizacion="ONG Test",
            descripcion="Proyecto combinado",
            beneficiarios_directos=1000,
            beneficiarios_indirectos=4000,
            duracion_meses=36,
            presupuesto_total=300000000,
            ods_vinculados=["3", "4", "6"],
            area_geografica=AreaGeografica.RURAL,
            poblacion_objetivo="Niños y mujeres",
            departamentos=["ANTIOQUIA"],
            municipios=["ABEJORRAL"],
            sectores=["Salud", "Alcantarillado", "Educación"]  # Puntajes: 3, 10, 7
        )

        score = criterio.evaluar(proyecto)

        # CONFIS: Debería usar puntaje MÁXIMO = 10 (Alcantarillado)
        assert proyecto.puntaje_sectorial_max == 10
        # Verificar que score refleja el puntaje alto
        assert score > 70, f"Score esperado >70 con sectorial=10, obtenido: {score}"

        print(f"\n✅ Proyecto multi-sectorial (CONFIS):")
        print(f"   Puntaje máximo sectorial: {proyecto.puntaje_sectorial_max}/10")
        print(f"   Score CONFIS: {score:.1f}")

    def test_score_a_probabilidad(self, criterio):
        """Verifica conversión de score a nivel de probabilidad"""
        assert criterio.score_a_probabilidad(90) == "alta"
        assert criterio.score_a_probabilidad(75) == "alta"
        assert criterio.score_a_probabilidad(60) == "media"
        assert criterio.score_a_probabilidad(45) == "media"
        assert criterio.score_a_probabilidad(30) == "baja"
        assert criterio.score_a_probabilidad(10) == "baja"

        print(f"\n✅ Conversión score → probabilidad:")
        print(f"   90 → {criterio.score_a_probabilidad(90)}")
        print(f"   60 → {criterio.score_a_probabilidad(60)}")
        print(f"   30 → {criterio.score_a_probabilidad(30)}")


if __name__ == "__main__":
    # Ejecutar tests con pytest
    pytest.main([__file__, "-v", "--tb=short"])
