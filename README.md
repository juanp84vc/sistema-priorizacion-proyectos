# Sistema de Priorización de Proyectos Sociales — ENLAZA GEB

Sistema modular y extensible para evaluar y priorizar proyectos de inversión social para el mecanismo de Obras por Impuestos, siguiendo los principios SOLID y la metodología CONFIS (Consejo Superior de Política Fiscal).

## Características principales

- **Arquitectura C con CONFIS integrado**: Scoring multi-criterio calibrado con datos oficiales del gobierno colombiano
- **SROI Logarítmico (40%)**: Función continua log₁₀ que elimina discontinuidades y premia proporcionalmente
- **Datos oficiales PDET/ZOMAC**: Matriz gubernamental de 362 municipios × 10 sectores en SQLite
- **Metodología CONFIS completa**: 8 grupos de priorización, puntajes territoriales y sectoriales
- **Gate de elegibilidad**: Solo municipios PDET/ZOMAC/Amazonía elegibles para Obras por Impuestos
- **Rúbricas objetivas**: Criterios verificables que reducen variabilidad inter-evaluador de ~45 a ~10 puntos
- **134 tests passing**: Cobertura completa de todos los criterios y el motor de scoring
- **Validado con datos reales**: 4 proyectos ENLAZA en prefactibilidad

## Instalación

```bash
pip install -r requirements.txt
```

## Uso rápido

```python
from src.scoring.motor_arquitectura_c import MotorArquitecturaC
from src.models.proyecto import ProyectoSocial, AreaGeografica

# Crear proyecto
proyecto = ProyectoSocial(
    id="P001",
    nombre="Alcantarillado Rural Abejorral",
    organizacion="ENLAZA GEB",
    descripcion="Mejoramiento de alcantarillado en zona PDET",
    beneficiarios_directos=500,
    beneficiarios_indirectos=2000,
    duracion_meses=12,
    presupuesto_total=100_000_000,
    sroi=3.5,
    ods_vinculados=["6", "11"],
    area_geografica=AreaGeografica.RURAL,
    poblacion_objetivo="Comunidades rurales",
    departamentos=["ANTIOQUIA"],
    municipios=["ABEJORRAL"],
    sectores=["Alcantarillado"]
)

# Evaluar
motor = MotorArquitecturaC(db_path="data/proyectos.db")
resultado = motor.evaluar_proyecto(proyecto)

print(f"Score: {resultado['score_total']:.1f}/100")
print(f"Nivel: {resultado['nivel_prioridad']}")
print(f"Alertas: {resultado['alertas']}")
```

## Arquitectura del Scoring

**Fórmula principal — Arquitectura C v2.1:**

```
Score_Final = SROI(40%) + Stakeholders(25%) + Prob.CONFIS(20%) + Riesgos(15%)
```

### Niveles de prioridad

| Score | Nivel | Descripción |
|-------|-------|-------------|
| 0 | RECHAZADO | SROI < 1.0 (destruye valor social) |
| 0 | NO ELEGIBLE | Municipio fuera de PDET/ZOMAC/Amazonía |
| 1–49 | BAJA | Retorno limitado o alto riesgo |
| 50–69 | MEDIA | Retorno aceptable, riesgo moderado |
| 70–84 | ALTA | Retorno excelente, bajo riesgo |
| 85–100 | MUY ALTA | Retorno excepcional, muy bajo riesgo |

---

## Criterios de evaluación

### 1. SROI — Social Return on Investment (40%)

Criterio dominante del sistema. Usa una función logarítmica continua que elimina los saltos discretos del modelo anterior.

**Fórmula:**
```
Score = min(100, max(0, 28.43 × log₁₀(SROI) + 60))
```

Esto produce una curva suave donde SROI=1.0→60, SROI=3.0→73.6, SROI=10.0→88.4, SROI=30.0→102→cap 100.

**Gates de validación:**
- Rechazo automático si SROI < 1.0 (score=0, nivel=RECHAZADO)
- Alerta de verificación si SROI > 7.0 (requiere validación metodológica)
- Observaciones obligatorias si SROI > 5.0

**Implementación:** `src/criterios/sroi.py`

### 2. Stakeholders — Relacionamiento y Pertinencia Operacional (25%)

Evalúa la contribución del proyecto al relacionamiento con comunidades y la pertinencia para las operaciones de ENLAZA.

**Componentes:**
- Pertinencia operacional (40%): Escala 1-5 con rúbricas verificables
- Mejora del relacionamiento (35%): Escala 1-5 con criterios documentados
- Alcance territorial (15%): Puntaje territorial CONFIS ×3 (max 30) + municipios ×10 (max 30) + bonus PDET (+15) + multi-departamento (+15) + corredor transmisión (+10) = max 100
- Stakeholders involucrados (10%): Tipos de actores (autoridades, líderes, comunidades indígenas, etc.)

**Implementación:** `src/criterios/stakeholders.py`

### 3. Probabilidad de Aprobación CONFIS (20%)

Evalúa la probabilidad de aprobación del proyecto en el mecanismo de Obras por Impuestos usando la metodología oficial del CONFIS (Anexo 2).

**Gate de elegibilidad:** Solo proyectos en municipios PDET, ZOMAC o Amazonía son elegibles. Los demás obtienen score=0 y nivel "NO ELEGIBLE".

**Fórmula CONFIS:**
```
Score = GrupoPriorización × 20% + ScoreCONFIS × 80%
ScoreCONFIS = ((PuntajeTerritorial + PuntajeSectorial) / 20) × 100
```

**8 grupos de priorización (Anexo 2 CONFIS):**

| Grupo | Descripción | Puntaje base |
|-------|-------------|-------------|
| 1 | PATR-PDET con estructuración OxI | 100 |
| 2 | PATR-PDET sin estructuración | 90 |
| 3 | PDET con estructuración OxI | 80 |
| 4 | PDET sin estructuración | 70 |
| 5 | ZOMAC con estructuración OxI | 60 |
| 6 | ZOMAC sin estructuración | 50 |
| 7 | Amazonía con estructuración OxI | 40 |
| 8 | Amazonía sin estructuración | 30 |

**Puntaje territorial:** Promedio de IPM, MDM inverso, IICA y CULTIVOS (1-10).
**Puntaje sectorial:** Prioridad del sector en el municipio según matriz PDET (1-10).

**Implementación:** `src/criterios/probabilidad_aprobacion_pdet.py`

### 4. Evaluación de Riesgos (15%)

Evalúa riesgos en múltiples dimensiones con sistema de alertas integrado al motor.

**Dimensiones:** Tecnológicos, regulatorios, financieros, sociales, operativos. La escala es inversa (score alto = bajo riesgo).

**Alertas del motor:**
- ⚠️ Presupuesto > $500M → riesgo financiero elevado
- ⚠️ Duración > 36 meses → riesgo operativo elevado
- ⚠️ Sin stakeholders específicos → revisar pertinencia

**Implementación:** `src/criterios/riesgos.py`

---

## Estructura del proyecto

```
sistema-priorizacion-proyectos/
├── src/
│   ├── models/
│   │   ├── proyecto.py                      # ProyectoSocial con campos CONFIS
│   │   └── evaluacion.py                    # ResultadoEvaluacion
│   ├── criterios/
│   │   ├── base.py                          # Abstracción base (DIP)
│   │   ├── sroi.py                          # SROI logarítmico (40%)
│   │   ├── stakeholders.py                  # Stakeholders con rúbricas (25%)
│   │   ├── probabilidad_aprobacion_pdet.py  # Prob. CONFIS (20%)
│   │   └── riesgos.py                       # Riesgos con alertas (15%)
│   ├── scoring/
│   │   └── motor_arquitectura_c.py          # Motor principal + gate elegibilidad
│   ├── database/
│   │   └── matriz_pdet_repository.py        # Repositorio SQLite PDET/ZOMAC
│   ├── estrategias/
│   │   ├── base.py
│   │   ├── scoring_ponderado.py
│   │   └── scoring_umbral.py
│   └── servicios/
│       └── sistema_priorizacion.py
├── tests/
│   ├── test_sroi.py                         # 28 tests SROI
│   ├── test_motor_arquitectura_c.py         # 13 tests motor + gate
│   ├── test_matriz_pdet.py                  # 17 tests PDET + CONFIS
│   ├── test_stakeholders.py                 # Tests stakeholders + territorial
│   └── ...                                  # Tests adicionales
├── data/
│   └── proyectos.db                         # SQLite: matriz_pdet_zomac (362 municipios)
├── Priorizacion_Proyectos_ENLAZA_GEB.xlsx   # Excel operativo con fórmulas CONFIS
├── Dashboard_Priorizacion_ENLAZA_GEB.html   # Dashboard interactivo
├── Guia_Operativa_Evaluadores_ENLAZA_GEB.docx  # Guía para evaluadores
├── main.py
├── requirements.txt
├── README.md
└── README_APP.md                            # Documentación app Streamlit
```

## Estado de implementación

| Componente | Estado | Tests |
|------------|--------|-------|
| SROI logarítmico (40%) | ✅ Completado | 28/28 |
| Stakeholders con rúbricas (25%) | ✅ Completado | Tests integrados |
| Prob. CONFIS (20%) | ✅ Completado | 17/17 |
| Riesgos con alertas (15%) | ✅ Completado | Tests integrados |
| Motor Arquitectura C + Gate | ✅ Completado | 13/13 |
| Matriz PDET/ZOMAC | ✅ Cargada | 362 municipios |
| Excel operativo | ✅ Actualizado | Fórmulas CONFIS |
| Dashboard HTML | ✅ Actualizado | CONFIS integrado |
| Guía Operativa | ✅ Actualizada | CONFIS documentado |

**Tests totales:** 134/134 passing (100%)

---

## Entregables

1. **Excel operativo** (`Priorizacion_Proyectos_ENLAZA_GEB.xlsx`): Hojas de registro, evaluación detallada, catálogos, panel de control, instrucciones, y hoja "Metodología CONFIS" con documentación completa de los 8 grupos, fórmulas, y ejemplos de cálculo.

2. **Dashboard interactivo** (`Dashboard_Priorizacion_ENLAZA_GEB.html`): Visualización de proyectos con gráficos radar, barras comparativas, tabla de resultados, y scoring CONFIS integrado. Se abre directamente en el navegador.

3. **Guía operativa** (`Guia_Operativa_Evaluadores_ENLAZA_GEB.docx`): Documento para evaluadores con instrucciones paso a paso, escalas de evaluación con rúbricas verificables, y la nueva metodología CONFIS.

4. **Motor Python** (`src/`): Implementación completa en Python con arquitectura SOLID, 134 tests, y base de datos SQLite con datos oficiales PDET/ZOMAC.

---

## Historial de cambios

### Fase 2 — Integración CONFIS (Feb 2026)

**Cambio A: Gate de elegibilidad PDET/ZOMAC**
- Propiedad `es_elegible_oxi` en ProyectoSocial
- Motor asigna score=0, nivel="NO ELEGIBLE" a municipios fuera de PDET/ZOMAC/Amazonía
- Alerta explícita: "Proyecto NO ELEGIBLE para Obras por Impuestos"

**Cambio B: Criterio 3 reescrito con lógica CONFIS**
- Reemplaza scoring simple (puntaje sectorial / 10 × 100) con fórmula oficial del Anexo 2
- 8 grupos de priorización con puntajes base 30-100
- Score = GrupoPriorización×20% + ScoreCONFIS×80%
- Puntaje territorial (IPM+MDM+IICA+CULTIVOS) y sectorial (1-10)

**Cambio C: Alcance Territorial con puntaje CONFIS**
- Reemplaza bonus binario PDET (+20) con puntaje territorial CONFIS ×3 (max 30)
- Nueva distribución: territorial(30) + municipios(30) + PDET(15) + multi-depto(15) + corredor(10) = 100

### Fase 1 — Arquitectura C (Nov 2025)

- Implementación inicial con 4 criterios y pesos calibrados
- SROI logarítmico continuo (reemplaza rangos discretos)
- Rúbricas objetivas para Pertinencia y Relacionamiento
- Conversión de Riesgos de input directo a sistema de alertas
- Integración de matriz PDET/ZOMAC en SQLite
- Validación con 4 proyectos ENLAZA reales

---

## Testing

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Con coverage
pytest tests/ --cov=src --cov-report=html

# Solo tests CONFIS
pytest tests/test_matriz_pdet.py -v

# Solo motor de scoring
pytest tests/test_motor_arquitectura_c.py -v
```

## Arquitectura SOLID

El sistema sigue estrictamente los principios SOLID, permitiendo agregar nuevos criterios sin modificar código existente:

```python
from src.criterios.base import CriterioEvaluacion

class NuevoCriterio(CriterioEvaluacion):
    def evaluar(self, proyecto):
        return score  # 0-100

    def get_nombre(self):
        return "Nuevo Criterio"

    def get_descripcion(self):
        return "Descripción del criterio"
```

Cada criterio tiene una sola responsabilidad (SRP), todos son intercambiables a través de la interfaz base (LSP), y el sistema depende de abstracciones, no de implementaciones concretas (DIP).

## Despliegue Streamlit

Ver `README_APP.md` para instrucciones de despliegue de la aplicación web en Streamlit Cloud.

---

**Versión:** 2.1 (Arquitectura C + CONFIS)
**Tests:** 134/134 passing
**Última actualización:** Febrero 2026
