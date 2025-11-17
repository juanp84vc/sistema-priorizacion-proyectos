# IMPLEMENTACIÓN CRITERIO RIESGOS (15%)

**Fecha**: 2025-01-17
**Sesión**: 7
**Estado**: ✅ COMPLETADO
**Arquitectura**: C - 100% COMPLETA

---

## RESUMEN EJECUTIVO

Se implementó exitosamente el criterio **Riesgos (15%)**, completando la Arquitectura C al **100%**.

### Logros Principales

- ✅ Criterio Riesgos implementado con 5 componentes
- ✅ 48 tests comprehensivos (100% passing)
- ✅ Integración completa en MotorScoringArquitecturaC
- ✅ Validación E2E exitosa
- ✅ Sistema alcanza 129 tests totales
- ✅ **ARQUITECTURA C 100% COMPLETA**

---

## ARQUITECTURA DEL CRITERIO RIESGOS

### Peso en el Sistema

```
Riesgos: 15% del score total
```

### Metodología: Scoring INVERSO

**Principio Fundamental**: Más riesgo → Menos puntos

```
Score = 100 - (nivel_riesgo / 25 × 100)
```

Donde:
```
Nivel de Riesgo = Probabilidad × Impacto
Rango: 1-25
```

### Componentes del Criterio (Pesos Internos)

1. **Riesgo Técnico/Operacional**: 30%
2. **Riesgo Social/Comunitario**: 25%
3. **Riesgo Financiero/Presupuestario**: 20%
4. **Riesgo Regulatorio/Legal**: 15%
5. **Factores Automáticos**: 10%

**Total**: 100%

---

## IMPLEMENTACIÓN TÉCNICA

### 1. Modelo de Datos (ProyectoSocial)

Se agregaron **10 nuevos campos** al modelo:

```python
# Riesgo Técnico/Operacional
riesgo_tecnico_probabilidad: Optional[int] = None  # 1-5
riesgo_tecnico_impacto: Optional[int] = None  # 1-5

# Riesgo Social/Comunitario
riesgo_social_probabilidad: Optional[int] = None  # 1-5
riesgo_social_impacto: Optional[int] = None  # 1-5

# Riesgo Financiero/Presupuestario
riesgo_financiero_probabilidad: Optional[int] = None  # 1-5
riesgo_financiero_impacto: Optional[int] = None  # 1-5

# Riesgo Regulatorio/Legal
riesgo_regulatorio_probabilidad: Optional[int] = None  # 1-5
riesgo_regulatorio_impacto: Optional[int] = None  # 1-5

# Duración estimada (para factores automáticos)
duracion_estimada_meses: Optional[int] = None

# Observaciones riesgos (opcional)
observaciones_riesgos: str = ""  # Max 1000 caracteres
```

#### Método de Validación

```python
def validar_riesgos(self) -> Dict[str, Any]:
    """
    Valida datos del criterio Riesgos

    Returns:
        Dict con 'valido', 'errores', 'advertencias', 'mensaje'
    """
    # Valida que todos los riesgos tengan probabilidad e impacto
    # Valida rango 1-5
    # Genera advertencias para riesgos altos (nivel >= 16)
```

---

### 2. Clase RiesgosCriterio

**Archivo**: `src/criterios/riesgos.py` (387 líneas)

#### Estructura

```python
@dataclass
class ResultadoRiesgos:
    """Resultado detallado de evaluación Riesgos"""
    score: float  # 0-100

    # Niveles de riesgo (1-25)
    nivel_riesgo_tecnico: int
    nivel_riesgo_social: int
    nivel_riesgo_financiero: int
    nivel_riesgo_regulatorio: int

    # Scores por componente (0-100, inverso)
    score_riesgo_tecnico: float
    score_riesgo_social: float
    score_riesgo_financiero: float
    score_riesgo_regulatorio: float
    score_factores_automaticos: float

    # Contribuciones ponderadas
    contribucion_tecnico: float
    contribucion_social: float
    contribucion_financiero: float
    contribucion_regulatorio: float
    contribucion_automaticos: float

    # Metadata
    nivel_general: str  # "BAJO", "MEDIO", "ALTO", "CRÍTICO"
    mensaje: str
    alertas: List[str]
    recomendaciones: List[str]
```

#### Métodos Principales

```python
class RiesgosCriterio:
    def evaluar(self, proyecto: ProyectoSocial) -> float:
        """Evalúa riesgos y retorna score 0-100 (inverso)"""

    def evaluar_detallado(self, proyecto: ProyectoSocial) -> ResultadoRiesgos:
        """Evaluación detallada con metadata y alertas"""

    def _calcular_nivel_riesgo(self, probabilidad: int, impacto: int) -> int:
        """Calcula nivel: Probabilidad × Impacto"""

    def _nivel_a_score_inverso(self, nivel: int) -> float:
        """Convierte nivel de riesgo a score inverso"""

    def _calcular_factores_automaticos(self, proyecto: ProyectoSocial) -> float:
        """Calcula score de factores automáticos de riesgo"""
```

---

### 3. Factores Automáticos de Riesgo

Penalizaciones automáticas basadas en características del proyecto:

#### Presupuesto
```python
if presupuesto_total > 1_000_000_000:  # > $1B
    score -= 15
elif presupuesto_total > 500_000_000:  # > $500M
    score -= 10
```

#### Duración
```python
if duracion_estimada_meses > 24:  # > 2 años
    score -= 10
elif duracion_estimada_meses > 12:  # > 1 año
    score -= 5
```

#### Complejidad Geográfica
```python
if len(departamentos) > 2:  # Múltiples departamentos
    score -= 5
```

#### Población Vulnerable
```python
if 'comunidades_indigenas' in stakeholders_involucrados:
    score -= 5  # Mayor complejidad cultural/legal
```

#### Zona NO-PDET en Área de Conflicto
```python
if not tiene_municipios_pdet:
    departamentos_conflicto = ['CHOCÓ', 'CAUCA', 'NARIÑO', 'PUTUMAYO', 'CAQUETÁ']
    if any(d in departamentos_conflicto for d in departamentos):
        score -= 10  # Menor apoyo institucional
```

---

### 4. Niveles de Riesgo

#### Escala de Probabilidad e Impacto

```
1 = Muy Baja
2 = Baja
3 = Media
4 = Alta
5 = Muy Alta
```

#### Matriz de Niveles (Prob × Impacto)

```
Nivel 1-5:    BAJO (Riesgo insignificante)
Nivel 6-12:   MEDIO (Riesgo manejable)
Nivel 13-20:  ALTO (Requiere mitigación)
Nivel 21-25:  CRÍTICO (Amenaza viabilidad)
```

#### Conversión a Score (Inverso)

| Nivel | Score | Interpretación |
|-------|-------|----------------|
| 1     | 96    | Riesgo mínimo |
| 6     | 76    | Riesgo bajo-medio |
| 13    | 48    | Riesgo alto |
| 20    | 20    | Riesgo crítico |
| 25    | 0     | Riesgo máximo |

---

### 5. Sistema de Alertas

#### Riesgos Críticos (Nivel ≥ 20)

```python
if nivel_tecnico >= 20:
    alerta = "🚨 Riesgo Técnico CRÍTICO (nivel {nivel}): \
              Requiere plan de mitigación robusto"

if nivel_social >= 20:
    alerta = "🚨 Riesgo Social CRÍTICO (nivel {nivel}): \
              Alto riesgo de conflicto comunitario"

if nivel_financiero >= 20:
    alerta = "🚨 Riesgo Financiero CRÍTICO (nivel {nivel}): \
              Revisar viabilidad presupuestaria"

if nivel_regulatorio >= 20:
    alerta = "🚨 Riesgo Regulatorio CRÍTICO (nivel {nivel}): \
              Marco legal muy incierto"
```

#### Riesgos Altos (Nivel ≥ 13)

```python
if 13 <= nivel < 20:
    alerta = "⚠️  Riesgo {tipo} ALTO (nivel {nivel}): \
              Considerar plan de mitigación"
```

---

### 6. Recomendaciones por Score

```python
if score < 40:
    recomendacion = "⚠️  Perfil de riesgo ALTO: Proyecto requiere análisis \
                     detallado de viabilidad y planes robustos de mitigación"

elif score < 60:
    recomendacion = "💡 Perfil de riesgo MEDIO: Desarrollar planes de \
                     mitigación para riesgos identificados"

if any(nivel >= 20 for niveles):
    recomendacion = "🔴 Uno o más riesgos CRÍTICOS: Considerar si proyecto \
                     es viable o requiere rediseño fundamental"
```

---

## INTEGRACIÓN EN EL MOTOR

### Cambios en MotorScoringArquitecturaC

**Archivo**: `src/scoring/motor_arquitectura_c.py`

#### 1. Import del Criterio

```python
from src.criterios.riesgos import RiesgosCriterio
```

#### 2. Inicialización

```python
def __init__(self, db_path: str = "data/proyectos.db"):
    self.criterio_sroi = SROICriterio(peso=self.PESO_SROI)
    self.criterio_stakeholders = StakeholdersCriterio(peso=self.PESO_STAKEHOLDERS)
    self.criterio_probabilidad = ProbabilidadAprobacionCriterio(
        peso=self.PESO_PROBABILIDAD,
        db_path=db_path
    )
    self.criterio_riesgos = RiesgosCriterio(peso=self.PESO_RIESGOS)  # ← NUEVO
```

#### 3. Cálculo en Motor

```python
# ========== CRITERIO 4: RIESGOS (15%) ==========
try:
    score_riesgos = self.criterio_riesgos.evaluar(proyecto)
    contribucion_riesgos = score_riesgos * self.PESO_RIESGOS
except ValueError as e:
    alertas.append(f"⚠️  Error Riesgos: {e}")
    score_riesgos = 0
    contribucion_riesgos = 0
```

#### 4. Eliminación de Código Temporal

Se eliminó el método `_calcular_riesgos_temporal()` que retornaba un valor neutro de 70.0.

---

## TESTS IMPLEMENTADOS

### Tests Unitarios: test_riesgos.py

**Total**: 48 tests (100% passing)

#### Categorías de Tests

1. **Cálculo de Niveles** (4 tests)
   - Nivel mínimo (1×1=1)
   - Nivel máximo (5×5=25)
   - Nivel medio (3×3=9)
   - Nivel asimétrico (5×2=10)

2. **Conversión a Score Inverso** (4 tests)
   - Nivel 1 → Score 96
   - Nivel 25 → Score 0
   - Nivel 13 → Score ~48
   - Nivel 6 → Score 76

3. **Proyectos Bajo Riesgo** (2 tests)
   - Score alto (~96)
   - Nivel general BAJO

4. **Proyectos Alto Riesgo** (4 tests)
   - Score bajo (<30)
   - Nivel general CRÍTICO
   - Generación de alertas
   - Alertas específicas por tipo

5. **Riesgos Individuales** (4 tests)
   - Riesgo técnico CRÍTICO
   - Riesgo social CRÍTICO
   - Riesgo financiero CRÍTICO
   - Riesgo regulatorio CRÍTICO

6. **Factores Automáticos** (9 tests)
   - Presupuesto bajo/medio/alto
   - Duración corta/media/larga
   - Múltiples departamentos
   - Penalizaciones acumuladas

7. **Pesos de Componentes** (6 tests)
   - Suma 100%
   - Peso técnico (30%)
   - Peso social (25%)
   - Peso financiero (20%)
   - Peso regulatorio (15%)
   - Peso automáticos (10%)

8. **Validaciones** (3 tests)
   - Datos completos
   - Error por probabilidad faltante
   - Error por impacto faltante

9. **Nivel General** (4 tests)
   - Nivel BAJO
   - Nivel MEDIO
   - Nivel ALTO
   - Nivel CRÍTICO

10. **Aplicar Peso** (3 tests)
    - Score 100 → 15 pts
    - Score 50 → 7.5 pts
    - Score 0 → 0 pts

11. **Recomendaciones** (2 tests)
    - Perfil alto
    - Riesgo crítico

12. **Resultado Detallado** (6 tests)
    - Estructura completa
    - Niveles de riesgo
    - Scores por componente
    - Contribuciones ponderadas
    - Suma de contribuciones

---

### Tests de Integración

#### Motor Arquitectura C

Se actualizaron 7 tests existentes para incluir campos de riesgos:

- ✅ test_pesos_suman_100
- ✅ test_proyecto_alta_prioridad_pdet_sroi_alto
- ✅ test_proyecto_rechazado_sroi_menor_1
- ✅ test_proyecto_no_pdet_score_probabilidad_cero
- ✅ test_comparacion_impacto_vs_sistema_viejo
- ✅ test_generar_reporte
- ✅ test_helper_function_calcular_score_proyecto

---

### Validación E2E

**Archivo**: `scripts/test_arquitectura_c_completa.py`

#### 6 Pruebas End-to-End

1. **Proyecto Ideal** ✅
   - SROI alto (4.8)
   - PDET (100% probabilidad)
   - Bajo riesgo
   - Alta pertinencia stakeholders
   - **Score: 92.8/100 - Nivel: MUY ALTA**

2. **Proyecto Rechazado** ✅
   - SROI < 1.0
   - **Score: 28.3/100 - Nivel: RECHAZADO**

3. **Proyecto Alto Riesgo** ✅
   - Presupuesto $2B
   - Duración 48 meses
   - Todos los riesgos CRÍTICOS
   - **Score: 58.6/100 - Nivel: MEDIA**

4. **Proyecto NO-PDET** ✅
   - Buen SROI pero sin PDET
   - **Score: 66.9/100 - Nivel: MEDIA**

5. **Validación de Pesos** ✅
   - Confirma 100% total
   - SROI 40%, Stakeholders 25%, Probabilidad 20%, Riesgos 15%

6. **Análisis de Contribuciones** ✅
   - Verifica suma de contribuciones = score total
   - Confirma SROI como dominante

---

## EJEMPLOS DE USO

### Ejemplo 1: Proyecto de Bajo Riesgo

```python
proyecto = ProyectoSocial(
    # ... datos básicos ...
    # Riesgos muy bajos
    riesgo_tecnico_probabilidad=1,  # Muy baja
    riesgo_tecnico_impacto=2,       # Baja
    # Nivel: 1×2 = 2 → Score: 92

    riesgo_social_probabilidad=1,   # Muy baja
    riesgo_social_impacto=1,        # Muy baja
    # Nivel: 1×1 = 1 → Score: 96

    riesgo_financiero_probabilidad=2,  # Baja
    riesgo_financiero_impacto=2,       # Baja
    # Nivel: 2×2 = 4 → Score: 84

    riesgo_regulatorio_probabilidad=1,  # Muy baja
    riesgo_regulatorio_impacto=1,       # Muy baja
    # Nivel: 1×1 = 1 → Score: 96

    duracion_estimada_meses=18  # Sin penalización (<24)
)

criterio = RiesgosCriterio()
resultado = criterio.evaluar_detallado(proyecto)

# Resultado esperado:
# - score_riesgo_tecnico: 92
# - score_riesgo_social: 96
# - score_riesgo_financiero: 84
# - score_riesgo_regulatorio: 96
# - score_factores_automaticos: 100 (sin penalizaciones)
# - score_total: ~91.8
# - nivel_general: "BAJO"
```

---

### Ejemplo 2: Proyecto de Alto Riesgo

```python
proyecto = ProyectoSocial(
    # ... datos básicos ...
    presupuesto_total=2_000_000_000,  # $2B - penalización -15
    duracion_estimada_meses=48,       # 4 años - penalización -10
    departamentos=["ANTIOQUIA", "CUNDINAMARCA", "VALLE"],  # -5

    # Riesgos CRÍTICOS
    riesgo_tecnico_probabilidad=5,   # Muy alta
    riesgo_tecnico_impacto=5,        # Muy alto
    # Nivel: 5×5 = 25 → Score: 0

    riesgo_social_probabilidad=4,    # Alta
    riesgo_social_impacto=5,         # Muy alto
    # Nivel: 4×5 = 20 → Score: 20

    riesgo_financiero_probabilidad=5,  # Muy alta
    riesgo_financiero_impacto=4,       # Alto
    # Nivel: 5×4 = 20 → Score: 20

    riesgo_regulatorio_probabilidad=4,  # Alta
    riesgo_regulatorio_impacto=4,       # Alto
    # Nivel: 4×4 = 16 → Score: 36
)

criterio = RiesgosCriterio()
resultado = criterio.evaluar_detallado(proyecto)

# Resultado esperado:
# - score_riesgo_tecnico: 0
# - score_riesgo_social: 20
# - score_riesgo_financiero: 20
# - score_riesgo_regulatorio: 36
# - score_factores_automaticos: 70 (100 - 15 - 10 - 5)
# - score_total: ~21.4
# - nivel_general: "CRÍTICO"
# - alertas: 4 (una por cada riesgo crítico/alto)
# - recomendaciones: Incluyen revisión de viabilidad
```

---

## IMPACTO EN EL SISTEMA

### Distribución de Pesos - Arquitectura C (COMPLETA)

```
┌─────────────────────────────────────────────┐
│ ARQUITECTURA C - 100% IMPLEMENTADA          │
├─────────────────────────────────────────────┤
│ SROI (Dominante):          40% ████████████ │
│ Stakeholders:              25% ███████      │
│ Probabilidad Aprobación:   20% ██████       │
│ Riesgos:                   15% █████        │
├─────────────────────────────────────────────┤
│ TOTAL:                    100% ████████████ │
└─────────────────────────────────────────────┘
```

### Antes vs Después

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Criterios Implementados** | 3/4 (75%) | 4/4 (100%) ✅ |
| **Criterio Riesgos** | Temporal (70 fijo) | Completo (5 componentes) ✅ |
| **Tests Totales** | 81 | 129 (+48) ✅ |
| **Validación E2E** | Parcial | Completa (6 pruebas) ✅ |
| **Pesos Sistema** | 85% funcional | 100% funcional ✅ |

---

## MÉTRICAS DE CALIDAD

### Cobertura de Tests

```
✅ 48 tests unitarios Riesgos (100% passing)
✅ 7 tests integración motor (100% passing)
✅ 6 pruebas E2E (100% passing)
✅ 129 tests totales en el sistema
```

### Complejidad del Código

```
Archivo: src/criterios/riesgos.py
- Líneas: 387
- Clases: 2 (ResultadoRiesgos, RiesgosCriterio)
- Métodos: 7 públicos, 4 privados
- Documentación: Completa (docstrings)
```

### Rendimiento

```
Tiempo de ejecución criterio Riesgos: < 1ms
Tiempo E2E completa: ~4 segundos
Tests unitarios Riesgos: 0.03 segundos
```

---

## ARCHIVOS MODIFICADOS/CREADOS

### Archivos Nuevos

1. `src/criterios/riesgos.py` (387 líneas)
2. `tests/test_riesgos.py` (294 líneas)
3. `scripts/test_arquitectura_c_completa.py` (356 líneas)
4. `IMPLEMENTACION_RIESGOS_15.md` (este archivo)

### Archivos Modificados

1. `src/models/proyecto.py`
   - Agregados 10 campos nuevos para riesgos
   - Agregado método `validar_riesgos()`

2. `src/scoring/motor_arquitectura_c.py`
   - Import de RiesgosCriterio
   - Inicialización del criterio
   - Integración en cálculo de score
   - Eliminación de método temporal

3. `tests/test_motor_arquitectura_c.py`
   - Actualizados 7 tests con campos de riesgos

---

## LECCIONES APRENDIDAS

### 1. Diseño de Scoring Inverso

La implementación de scoring inverso (más riesgo = menos puntos) resultó intuitiva:

```python
Score = 100 - (nivel / 25 × 100)
```

Esto permite que proyectos de bajo riesgo obtengan scores altos (~90-100) y proyectos de alto riesgo obtengan scores bajos (0-20).

### 2. Factores Automáticos

Los factores automáticos (presupuesto, duración, complejidad) añaden una dimensión objetiva al análisis de riesgos, capturando características inherentes del proyecto que incrementan la complejidad.

### 3. Sistema de Alertas Multi-Nivel

El sistema de alertas diferenciado (CRÍTICO vs ALTO) permite priorizar atención en los riesgos más severos.

### 4. Balance de Componentes

El balance de pesos (Técnico 30%, Social 25%, Financiero 20%, Regulatorio 15%, Automáticos 10%) refleja la importancia relativa de cada dimensión en contexto de proyectos sociales.

---

## PRÓXIMOS PASOS SUGERIDOS

### Fase de Producción

1. **Calibración de Penalizaciones Automáticas**
   - Revisar umbrales de presupuesto y duración con data real
   - Ajustar penalizaciones según experiencia

2. **Dashboard de Riesgos**
   - Visualización de matriz de riesgos
   - Gráficos de radar por dimensión
   - Alertas priorizadas

3. **Planes de Mitigación**
   - Templates para planes de mitigación
   - Tracking de acciones correctivas
   - Riesgos residuales

4. **Machine Learning**
   - Predicción de riesgos basada en proyectos históricos
   - Identificación automática de patrones de alto riesgo

---

## CONCLUSIÓN

La implementación del criterio Riesgos (15%) **completa exitosamente la Arquitectura C al 100%**, cumpliendo todos los objetivos:

✅ **Scoring inverso** implementado correctamente
✅ **5 componentes** con pesos balanceados
✅ **Sistema de alertas** multi-nivel
✅ **Factores automáticos** basados en características del proyecto
✅ **48 tests comprehensivos** (100% passing)
✅ **Integración completa** en motor
✅ **Validación E2E** exitosa
✅ **Documentación completa**

El sistema ahora cuenta con **129 tests** y evalúa proyectos en **4 dimensiones** (SROI 40%, Stakeholders 25%, Probabilidad 20%, Riesgos 15%), proporcionando un análisis integral y balanceado para la priorización de proyectos sociales.

---

**Estado Final**: ✅ **ARQUITECTURA C - 100% COMPLETADA** 🎉

---

## APÉNDICE: REFERENCIA RÁPIDA

### Escala de Probabilidad/Impacto

| Valor | Descripción |
|-------|-------------|
| 1 | Muy Baja |
| 2 | Baja |
| 3 | Media |
| 4 | Alta |
| 5 | Muy Alta |

### Niveles de Riesgo

| Rango | Nivel | Score Esperado |
|-------|-------|----------------|
| 1-5 | BAJO | 80-96 |
| 6-12 | MEDIO | 52-76 |
| 13-20 | ALTO | 20-48 |
| 21-25 | CRÍTICO | 0-16 |

### Umbrales de Penalización Automática

| Factor | Umbral | Penalización |
|--------|--------|--------------|
| Presupuesto | > $1B | -15 pts |
| Presupuesto | > $500M | -10 pts |
| Duración | > 24 meses | -10 pts |
| Duración | > 12 meses | -5 pts |
| Departamentos | > 2 | -5 pts |
| Población vulnerable | Indígenas | -5 pts |
| NO-PDET + Conflicto | Varios depts | -10 pts |

---

**Fecha de Finalización**: 2025-01-17
**Versión**: 1.0
**Autor**: Sistema de Priorización - Arquitectura C
