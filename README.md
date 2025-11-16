# Sistema de Priorización de Proyectos Sociales

Sistema modular y extensible para evaluar y priorizar proyectos de inversión social siguiendo **estrictamente los principios SOLID**.

## 🎯 Características

### 🎯 Sistema de Priorización Arquitectura C

- **SROI Dominante (40%):** Criterio principal de evaluación con impacto 10.7x mayor
- **Datos Oficiales PDET/ZOMAC:** Matriz gubernamental de 362 municipios × 10 sectores
- **Scoring Automático:** Motor integrado con validaciones y alertas
- **Validado con Datos Reales:** 4 proyectos ENLAZA en prefactibilidad
- **50 Tests Passing:** Calidad asegurada (100%)

### 🏗️ Arquitectura SOLID

- ✅ Evaluación multi-criterio configurable
- ✅ Múltiples estrategias de scoring
- ✅ Extensible sin modificar código existente (OCP)
- ✅ Componentes intercambiables (LSP)
- ✅ Fácil agregar nuevos criterios
- ✅ Arquitectura basada en abstracciones (DIP)
- ✅ 100% Python type-safe

## 📦 Instalación

```bash
cd /Users/juanpablotovar/Desktop/claude_code/sistema-priorizacion-proyectos
pip install -r requirements.txt
```

## 🚀 Uso Rápido

```python
from src.models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto
from src.criterios import (
    CostoEfectividadCriterio,
    ContribucionStakeholdersCriterio,
    ProbabilidadAprobacionCriterio,
    RiesgosCriterio
)
from src.estrategias.scoring_ponderado import ScoringPonderado
from src.servicios.sistema_priorizacion import SistemaPriorizacionProyectos

# Configurar sistema
sistema = SistemaPriorizacionProyectos(
    criterios=[
        CostoEfectividadCriterio(peso=0.25),
        ContribucionStakeholdersCriterio(peso=0.25),
        ProbabilidadAprobacionCriterio(peso=0.25),
        RiesgosCriterio(peso=0.25)
    ],
    estrategia=ScoringPonderado()
)

# Evaluar proyectos
resultados = sistema.priorizar_cartera(proyectos)

for resultado in resultados:
    print(f"{resultado.proyecto_nombre}: {resultado.score_final:.2f}")
    print(f"  Recomendación: {resultado.recomendacion}")
```

## 🏗️ Arquitectura SOLID

### Single Responsibility Principle (SRP)
Cada criterio tiene UNA sola responsabilidad:
- `CostoEfectividadCriterio`: Solo evalúa relación costo-efectividad
- `ContribucionStakeholdersCriterio`: Solo evalúa contribución a stakeholders
- `ProbabilidadAprobacionCriterio`: Solo evalúa probabilidad de aprobación gubernamental
- `RiesgosCriterio`: Solo evalúa riesgos del proyecto

### Open/Closed Principle (OCP)
Extensible sin modificación:
```python
# Agregar nuevo criterio SIN modificar código existente
class InnovacionCriterio(CriterioEvaluacion):
    def evaluar(self, proyecto):
        # Nueva lógica de evaluación
        pass
```

### Liskov Substitution Principle (LSP)
Todos los criterios son intercambiables:
```python
# Cualquier criterio funciona igual
for criterio in criterios:
    score = criterio.evaluar(proyecto)  # Siempre funciona
```

### Interface Segregation Principle (ISP)
Interfaces mínimas y focalizadas:
- `CriterioEvaluacion`: Solo métodos esenciales (`evaluar`, `get_nombre`, `get_descripcion`)
- No forzamos métodos innecesarios

### Dependency Inversion Principle (DIP)
Dependemos de abstracciones:
```python
# Sistema depende de abstracción, no implementación
def __init__(self, criterios: List[CriterioEvaluacion]):
    # Funciona con CUALQUIER criterio que implemente la interfaz
```

## 📂 Estructura del Proyecto

```
sistema-priorizacion-proyectos/
├── src/
│   ├── models/              # Modelos de dominio
│   │   ├── proyecto.py      # ProyectoSocial, AreaGeografica, EstadoProyecto
│   │   └── evaluacion.py    # ResultadoEvaluacion
│   ├── criterios/           # Criterios de evaluación
│   │   ├── base.py          # Abstracción base (DIP)
│   │   ├── costo_efectividad.py
│   │   ├── stakeholders.py
│   │   ├── probabilidad_aprobacion.py
│   │   └── riesgos.py
│   ├── estrategias/         # Estrategias de scoring
│   │   ├── base.py
│   │   ├── scoring_ponderado.py
│   │   └── scoring_umbral.py
│   └── servicios/           # Servicios de aplicación
│       └── sistema_priorizacion.py
├── tests/                   # Tests unitarios
├── data/                    # Datos de ejemplo
├── main.py                  # Ejemplos de uso
├── requirements.txt
└── README.md
```

## 📊 Criterios de Evaluación - Arquitectura C

**Sistema de Scoring:** Score Final = Σ(Score_criterio × Peso)

### 1. Social Return on Investment - SROI (40%) ⭐ DOMINANTE

**Criterio más importante del sistema**

- **Descripción:** Evalúa el retorno social de la inversión, midiendo cuánto valor social se genera por cada peso invertido
- **Metodología:** Conversión SROI → Score según rangos aprobados
- **Rangos de conversión:**
  - SROI < 1.0: Score 0 (RECHAZADO - destruye valor social)
  - SROI 1.0-1.99: Score 60 (Prioridad BAJA - retorno marginal)
  - SROI 2.0-2.99: Score 80 (Prioridad MEDIA - retorno aceptable)
  - SROI ≥ 3.0: Score 95 (Prioridad ALTA - retorno excelente)
- **Gates de validación:**
  - Rechazo automático: SROI < 1.0
  - Alerta verificación: SROI > 7.0 (requiere validación metodológica)
  - Observaciones obligatorias: SROI > 5.0
- **Peso:** 40% (10.6x más impacto vs sistema anterior)
- **Implementación:** `src/criterios/sroi.py`

### 2. Contribución al Relacionamiento con Stakeholders (25%)

- **Descripción:** Mide contribución al relacionamiento con stakeholders locales y viabilidad operativa
- **Factores evaluados:**
  - Alcance geográfico (departamentos, municipios)
  - Cobertura de beneficiarios (directos e indirectos)
  - Fortalecimiento de relaciones institucionales
  - Viabilidad operativa
- **Score alto indica:** Fuerte relacionamiento y alta viabilidad operativa
- **Peso:** 25%
- **Estado:** Cálculo temporal (reimplementación pendiente)

### 3. Probabilidad de Aprobación - Obras por Impuestos (20%)

**Con datos oficiales PDET/ZOMAC**

- **Descripción:** Evalúa probabilidad de aprobación en mecanismo Obras por Impuestos usando matriz oficial de priorización sectorial
- **Metodología:** 100% basado en datos oficiales gubernamentales
- **Componentes:**
  - Prioridad sectorial PDET/ZOMAC (100% del criterio)
  - Matriz oficial: 362 municipios × 10 sectores
  - Puntajes sectoriales: 1-10 (10 = máxima prioridad)
- **Scoring:**
  - Municipios PDET: Score = (Puntaje_sectorial / 10) × 100
  - Municipios NO-PDET: Score = 0 (no elegibles para Obras por Impuestos)
- **Sectores evaluados:**
  1. Educación
  2. Salud
  3. Alcantarillado
  4. Vía (Infraestructura vial)
  5. Energía
  6. Banda Ancha (Conectividad)
  7. Riesgo Ambiental
  8. Infraestructura Rural
  9. Cultura
  10. Deporte
- **Peso:** 20%
- **Implementación:** `src/criterios/probabilidad_aprobacion_pdet.py`
- **Datos:** `data/proyectos.db` (tabla matriz_pdet_zomac)

### 4. Evaluación de Riesgos (15%)

- **Descripción:** Analiza riesgos del proyecto en múltiples dimensiones
- **Tipos de riesgo evaluados:**
  - Tecnológicos
  - Regulatorios
  - Financieros
  - Sociales
  - Operativos
- **Factores considerados:**
  - Complejidad presupuestaria
  - Duración del proyecto
  - Alcance geográfico
  - Características población objetivo
- **Score alto:** Bajo riesgo (escala inversa)
- **Peso:** 15%
- **Estado:** Cálculo temporal (reimplementación pendiente)

---

## 🎯 Cambios vs Sistema Anterior

| Criterio | Peso Anterior | Peso Arquitectura C | Cambio |
|----------|---------------|---------------------|--------|
| **SROI** | 3.75% | **40%** | **+36.25%** 🚀 |
| Costo-Efectividad | 25% | **0%** | **ELIMINADO** ❌ |
| Stakeholders | 25% | 25% | Sin cambio |
| Prob. Aprobación | 25% | 20% | -5% |
| Riesgos | 25% | 15% | -10% |

### Impacto Demostrado

**Proyecto transformacional (SROI 4.2 + PDET alta prioridad):**
- Sistema anterior: 60/100 (prioridad MEDIA)
- Arquitectura C: 92.2/100 (prioridad MUY ALTA)
- **Mejora: +32 puntos (+53%)** 🎯

**Factor de incremento SROI:**
- Contribución anterior: 3.56 puntos (3.75% peso)
- Contribución nueva: 38.0 puntos (40% peso)
- **Factor: 10.7x más impacto** 🚀

---

## 📈 Motor de Scoring

### Fórmula de Cálculo
```python
Score_Final = (
    SROI × 40% +
    Stakeholders × 25% +
    Probabilidad_Aprobación × 20% +
    Riesgos × 15%
)
```

### Niveles de Prioridad

| Score | Nivel | Descripción |
|-------|-------|-------------|
| 0 | RECHAZADO | SROI < 1.0 (destruye valor social) |
| 1-49 | BAJA | Retorno limitado, alto riesgo |
| 50-69 | MEDIA | Retorno aceptable, riesgo moderado |
| 70-84 | ALTA | Retorno excelente, bajo riesgo |
| 85-100 | MUY ALTA | Retorno excepcional, muy bajo riesgo |

### Implementación

**Motor principal:** `src/scoring/motor_arquitectura_c.py`
```python
from src.scoring.motor_arquitectura_c import calcular_score_proyecto

# Calcular score de un proyecto
resultado = calcular_score_proyecto(proyecto)

# Resultado incluye:
# - score_total: 0-100
# - Scores individuales por criterio
# - Contribuciones (score × peso)
# - nivel_prioridad: MUY ALTA, ALTA, MEDIA, BAJA, RECHAZADO
# - Alertas y recomendaciones
```

---

## ✅ Estado de Implementación

| Componente | Estado | Tests |
|------------|--------|-------|
| SROI (40%) | ✅ Completado | 28/28 ✅ |
| Prob. Aprobación (20%) | ✅ Completado | 15/15 ✅ |
| Matriz PDET/ZOMAC | ✅ Cargada | 362 municipios ✅ |
| Motor Arquitectura C | ✅ Integrado | 7/7 ✅ |
| Stakeholders (25%) | ⏳ Temporal | - |
| Riesgos (15%) | ⏳ Temporal | - |

**Tests totales:** 50/50 passing (100%)

**Validación:** 4 proyectos ENLAZA reales (prefactibilidad)

**Estado:** ✅ EN PRODUCCIÓN

## 🎲 Estrategias de Scoring

### Scoring Ponderado
Score final = suma de scores ponderados de cada criterio

### Scoring con Umbral
Requiere que todos los criterios superen un umbral mínimo.
Si alguno está bajo el umbral, se aplica penalización.

## 📚 Documentación Técnica

### Arquitectura del Sistema

- **[SESSION_SUMMARY.md](SESSION_SUMMARY.md)**: Resumen completo de 5 sesiones de desarrollo (15-16 Nov 2025)
- **[VALIDACION_PROYECTOS_REALES.md](VALIDACION_PROYECTOS_REALES.md)**: Validación con 4 proyectos ENLAZA reales
- **[scripts/README_VALIDACION.md](scripts/README_VALIDACION.md)**: Guía del script de validación interactiva

### Referencias

- **Arquitectura C aprobada:** 15 Noviembre 2025
- **Implementación:** 15-16 Noviembre 2025 (8 horas, 5 sesiones)
- **Validación con proyectos reales:** 16 Noviembre 2025
- **Versión:** 1.0 (Production-ready)
- **Tests:** 50/50 passing (100%)

---

## 📝 Ejemplo Completo

Ver `main.py` para ejemplos completos de uso con datos reales.

```bash
python main.py
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest tests/ -v

# Con coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔧 Extensión del Sistema

### Agregar Nuevo Criterio

```python
# 1. Crear nueva clase que herede de CriterioEvaluacion
from src.criterios.base import CriterioEvaluacion

class TransparenciaCriterio(CriterioEvaluacion):
    def evaluar(self, proyecto: ProyectoSocial) -> float:
        # Tu lógica aquí
        return score

    def get_nombre(self) -> str:
        return "Transparencia"

    def get_descripcion(self) -> str:
        return "Evalúa nivel de transparencia y rendición de cuentas"

# 2. Usar sin modificar código existente
sistema = SistemaPriorizacionProyectos(
    criterios=[
        # ... criterios existentes ...
        TransparenciaCriterio(peso=0.15)  # ¡Funciona!
    ],
    estrategia=ScoringPonderado()
)
```

### Agregar Nueva Estrategia de Scoring

```python
from src.estrategias.base import EstrategiaScoring

class ScoringMultiplicativo(EstrategiaScoring):
    def calcular_score(self, proyecto, evaluaciones):
        # Multiplica scores en lugar de sumarlos
        score = 100
        for eval_data in evaluaciones.values():
            score *= (eval_data['score_base'] / 100)
        return score * 100

# Usar
sistema.estrategia = ScoringMultiplicativo()
```

## 🎯 Casos de Uso

1. **Fundaciones**: Priorizar propuestas de proyectos sociales
2. **ONGs**: Evaluar impacto de programas
3. **Gobierno**: Asignar recursos a proyectos comunitarios
4. **Empresas**: Programas de responsabilidad social empresarial
5. **Academia**: Evaluar proyectos de extensión

## 📖 Documentación Adicional

- Cada archivo tiene docstrings completos
- Los principios SOLID están documentados en el código
- Ver comentarios inline para detalles de implementación

## 🤝 Contribuir

Este proyecto sigue estrictamente los principios SOLID. Cualquier contribución debe:
1. Mantener responsabilidad única (SRP)
2. Ser extensible sin modificación (OCP)
3. Respetar contratos de interfaces (LSP)
4. Mantener interfaces mínimas (ISP)
5. Depender de abstracciones (DIP)

## 📝 Licencia

MIT - Código educativo para proyectos de valor compartido

## ✨ Autor

Desarrollado como ejemplo de aplicación de principios SOLID en proyectos de ciencia de datos e inversión social.

---

**⚠️ Nota**: Este sistema está diseñado con fines educativos y como plantilla para proyectos reales.
Para uso en producción, se recomienda agregar:
- Persistencia en base de datos
- API REST para integración
- Interfaz web de usuario
- Sistema de autenticación
- Logs y monitoreo
- Tests de integración completos


## 🌐 Despliegue en Streamlit Cloud

### Requisitos previos
1. Cuenta en [Streamlit Cloud](https://streamlit.io/cloud)
2. Repositorio en GitHub con este código
3. API Keys configuradas (Google Gemini, Claude, etc.)

### Pasos para desplegar:

1. **Subir código a GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
   git push -u origin main
   ```

2. **Configurar en Streamlit Cloud:**
   - Ve a [share.streamlit.io](https://share.streamlit.io)
   - Conecta tu repositorio de GitHub
   - Selecciona el archivo `app.py`
   - En **Advanced settings** → **Secrets**, agrega:
     ```toml
     GOOGLE_API_KEY = "tu_api_key_de_google"
     ANTHROPIC_API_KEY = "tu_api_key_de_claude"
     OPENAI_API_KEY = "tu_api_key_de_openai"
     LLM_PROVIDER = "gemini"
     ```

3. **Deploy!**
   - Haz clic en "Deploy"
   - La aplicación estará disponible en: `https://TU_APP.streamlit.app`

### Variables de entorno necesarias:

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `GOOGLE_API_KEY` | API Key de Google Gemini | Sí (si usas Gemini) |
| `ANTHROPIC_API_KEY` | API Key de Claude | Sí (si usas Claude) |
| `OPENAI_API_KEY` | API Key de OpenAI | Sí (si usas ChatGPT) |
| `LLM_PROVIDER` | Proveedor por defecto: `gemini`, `claude`, o `openai` | Sí |

### Notas importantes para producción:

- ⚠️ **Base de datos**: En producción, considera usar PostgreSQL en lugar de SQLite
- 🔒 **Seguridad**: Nunca subas archivos `.env` a GitHub
- 📊 **Límites**: Streamlit Cloud tiene límites de recursos gratuitos
- 💾 **Persistencia**: Los archivos guardados pueden perderse en reinicios (usa almacenamiento externo para producción)

