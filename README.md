# Sistema de Priorización de Proyectos Sociales

Sistema modular y extensible para evaluar y priorizar proyectos de inversión social siguiendo **estrictamente los principios SOLID**.

## 🎯 Características

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

## 📊 Criterios de Evaluación

### 1. Relación Costo-Efectividad (25%)
- Evalúa la relación cuantitativa entre beneficios obtenidos y su costo unitario
- Considera costo por beneficiario, eficiencia temporal y operativa
- Metodología: Escala inversa (menor costo = mayor score)
- Score alto indica excelente eficiencia en el uso de recursos

### 2. Contribución al Relacionamiento con Stakeholders (25%)
- Mide contribución al relacionamiento con stakeholders locales y viabilidad operativa
- Considera alcance geográfico, múltiples departamentos y cobertura de beneficiarios
- Evalúa fortalecimiento de relaciones institucionales
- Score alto indica fuerte relacionamiento y viabilidad operativa

### 3. Probabilidad de Aprobación Gubernamental (25%)
- Evalúa probabilidad de aprobación por Gobierno Nacional, distrital o local
- Niveles: **alta, media, baja**
- Considera alineación con ODS prioritarios y viabilidad presupuestaria
- Evalúa población objetivo prioritaria y alcance geográfico estratégico

### 4. Evaluación de Riesgos (25%)
- Analiza riesgos tecnológicos, regulatorios, financieros, sociales y operativos
- Considera complejidad presupuestaria, duración y alcance geográfico
- Evalúa características de población objetivo
- Score alto = bajo riesgo (escala inversa)

## 🎲 Estrategias de Scoring

### Scoring Ponderado
Score final = suma de scores ponderados de cada criterio

### Scoring con Umbral
Requiere que todos los criterios superen un umbral mínimo.
Si alguno está bajo el umbral, se aplica penalización.

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

