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
        assert repo.es_municipio_pdet("ANTIOQUIA", "ABEJORRAL") is True
        assert repo.es_municipio_pdet("CUNDINAMARCA", "BOGOTÁ") is False
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

        # Con puntaje PDET=10 → Score = 100/100 (sin otros componentes)
        # Esperamos score = 100 (probabilidad alta)
        assert score == 100, f"Score esperado 100, obtenido: {score}"

        # Verificar metadata
        assert proyecto_pdet_alta_prioridad.tiene_municipios_pdet is True
        assert proyecto_pdet_alta_prioridad.puntaje_sectorial_max == 10
        assert "Alcantarillado" in proyecto_pdet_alta_prioridad.puntajes_pdet

        print(f"\n✅ Proyecto alta prioridad PDET:")
        print(f"   Score: {score:.1f}/100")
        print(f"   Puntaje sectorial: {proyecto_pdet_alta_prioridad.puntaje_sectorial_max}/10")
        print(f"   Probabilidad: {criterio.score_a_probabilidad(score)}")

    def test_evaluacion_pdet_baja_prioridad(self, criterio, proyecto_pdet_baja_prioridad):
        """Proyecto con sector de baja prioridad PDET debe tener score más bajo"""
        score = criterio.evaluar(proyecto_pdet_baja_prioridad)

        # Con puntaje PDET=3 → Score = 30/100 (basado solo en puntaje sectorial)
        # Esperamos score = 30 (probabilidad baja)
        assert score == 30, f"Score esperado 30, obtenido: {score}"

        assert proyecto_pdet_baja_prioridad.tiene_municipios_pdet is True
        assert proyecto_pdet_baja_prioridad.puntaje_sectorial_max == 3

        print(f"\n✅ Proyecto baja prioridad PDET:")
        print(f"   Score: {score:.1f}/100")
        print(f"   Puntaje sectorial: {proyecto_pdet_baja_prioridad.puntaje_sectorial_max}/10")
        print(f"   Probabilidad: {criterio.score_a_probabilidad(score)}")

    def test_evaluacion_no_pdet(self, criterio, proyecto_no_pdet):
        """Proyecto en municipio NO-PDET debe tener score 0 (no aplica a Obras por Impuestos)"""
        score = criterio.evaluar(proyecto_no_pdet)

        # Sin municipios PDET → Score = 0 (no puede usar mecanismo Obras por Impuestos)
        assert score == 0, f"Score esperado 0, obtenido: {score}"
        assert proyecto_no_pdet.tiene_municipios_pdet is False
        assert proyecto_no_pdet.puntaje_sectorial_max is None

        print(f"\n✅ Proyecto NO-PDET:")
        print(f"   Score: {score:.1f}/100")
        print(f"   Es PDET: {proyecto_no_pdet.tiene_municipios_pdet}")
        print(f"   Probabilidad: {criterio.score_a_probabilidad(score)}")
        print(f"   Nota: No aplica a mecanismo Obras por Impuestos (exclusivo PDET/ZOMAC)")

    def test_detalles_evaluacion(self, criterio, proyecto_pdet_alta_prioridad):
        """Verifica método get_detalles_evaluacion()"""
        detalles = criterio.get_detalles_evaluacion(proyecto_pdet_alta_prioridad)

        assert "probabilidad_nivel" in detalles
        assert "score_total" in detalles
        assert "componentes" in detalles
        assert "prioridad_sectorial_pdet" in detalles["componentes"]
        assert "metadata" in detalles  # Metadata descriptiva (no afecta score)

        # Verificar que solo hay un componente (100% sectorial)
        assert len(detalles["componentes"]) == 1
        assert detalles["componentes"]["prioridad_sectorial_pdet"]["peso"] == 1.00

        print(f"\n✅ Detalles de evaluación:")
        print(f"   Nivel: {detalles['probabilidad_nivel']}")
        print(f"   Score total: {detalles['score_total']:.1f}")
        print(f"   Componente único:")
        comp_data = detalles["componentes"]["prioridad_sectorial_pdet"]
        print(f"     - Prioridad sectorial PDET: {comp_data['score']:.1f} (peso {comp_data['peso']}) = {comp_data['ponderado']:.1f}")
        print(f"   Metadata descriptiva (no afecta score):")
        print(f"     - ODS: {detalles['metadata']['ods_vinculados']}")
        print(f"     - Población: {detalles['metadata']['poblacion_objetivo']}")

    def test_comparacion_alta_vs_baja_prioridad(
        self,
        criterio,
        proyecto_pdet_alta_prioridad,
        proyecto_pdet_baja_prioridad
    ):
        """Proyecto con alta prioridad PDET debe tener score mayor que baja prioridad"""
        score_alta = criterio.evaluar(proyecto_pdet_alta_prioridad)
        score_baja = criterio.evaluar(proyecto_pdet_baja_prioridad)

        # Alta prioridad (10/10) = 100, Baja prioridad (3/10) = 30
        assert score_alta == 100, f"Score alta esperado 100, obtenido: {score_alta}"
        assert score_baja == 30, f"Score baja esperado 30, obtenido: {score_baja}"
        assert score_alta > score_baja

        diferencia = score_alta - score_baja
        print(f"\n✅ Comparación alta vs baja prioridad:")
        print(f"   Alta (10/10): {score_alta:.1f} ({criterio.score_a_probabilidad(score_alta)})")
        print(f"   Baja (3/10): {score_baja:.1f} ({criterio.score_a_probabilidad(score_baja)})")
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

        criterio.evaluar(proyecto)

        # Debería usar puntaje MÁXIMO = 10 (Alcantarillado)
        assert proyecto.puntaje_sectorial_max == 10
        assert "Alcantarillado" in proyecto.puntajes_pdet
        assert proyecto.puntajes_pdet["Alcantarillado"] == 10

        print(f"\n✅ Proyecto multi-sectorial:")
        print(f"   Puntaje máximo: {proyecto.puntaje_sectorial_max}/10")
        print(f"   Puntajes por sector: {proyecto.puntajes_pdet}")

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
