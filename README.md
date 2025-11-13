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
    ImpactoSocialCriterio,
    SostenibilidadFinancieraCriterio,
    AlineacionODSCriterio,
    CapacidadOrganizacionalCriterio
)
from src.estrategias.scoring_ponderado import ScoringPonderado
from src.servicios.sistema_priorizacion import SistemaPriorizacionProyectos

# Configurar sistema
sistema = SistemaPriorizacionProyectos(
    criterios=[
        ImpactoSocialCriterio(peso=0.4),
        SostenibilidadFinancieraCriterio(peso=0.3),
        AlineacionODSCriterio(["ODS 1", "ODS 4", "ODS 10"], peso=0.2),
        CapacidadOrganizacionalCriterio(peso=0.1)
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
- `ImpactoSocialCriterio`: Solo evalúa impacto social
- `SostenibilidadCriterio`: Solo evalúa sostenibilidad financiera
- `AlineacionODSCriterio`: Solo evalúa alineación con ODS
- `CapacidadOrganizacionalCriterio`: Solo evalúa capacidad de ejecución

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
│   │   ├── impacto_social.py
│   │   ├── sostenibilidad.py
│   │   ├── alineacion_ods.py
│   │   └── capacidad_organizacional.py
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

### 1. Impacto Social (40%)
- Número de beneficiarios directos e indirectos
- Área geográfica (rural tiene multiplicador)
- Duración del proyecto

### 2. Sostenibilidad Financiera (30%)
- Diversificación de fuentes de financiamiento
- Porcentaje de ingresos propios
- Eficiencia presupuestaria (costo por beneficiario)

### 3. Alineación con ODS (20%)
- ODS prioritarios de la organización
- Cantidad de ODS que aborda el proyecto
- Bonus por integralidad (3+ ODS)

### 4. Capacidad Organizacional (10%)
- Años de experiencia de la organización
- Calificación del equipo
- Proyectos exitosos previos

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
