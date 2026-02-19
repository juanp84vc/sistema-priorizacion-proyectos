# Sesión Febrero 2026 — Integración CONFIS

**Fecha:** Febrero 2026
**Alcance:** Integración de metodología CONFIS (Anexo 2) al sistema de priorización
**Estado:** ✅ Completado
**Tests:** 134/134 passing (100%)

---

## Contexto

El CONFIS (Consejo Superior de Política Fiscal) define la metodología oficial para priorizar proyectos en el mecanismo de Obras por Impuestos. Esta sesión integró dicha metodología al sistema existente (Arquitectura C), reemplazando el scoring simplificado de Probabilidad de Aprobación con la fórmula oficial del Anexo 2.

---

## Cambios Implementados

### Cambio A: Gate de Elegibilidad PDET/ZOMAC

**Problema:** El sistema anterior asignaba score 0 a municipios no-PDET, pero no distinguía claramente entre "rechazado por SROI" y "no elegible por territorio".

**Solución:**
- Nueva propiedad `es_elegible_oxi` en `ProyectoSocial` (modelo)
- El motor asigna score=0 y nivel="NO ELEGIBLE" a municipios fuera de PDET/ZOMAC/Amazonía
- Alerta explícita: "Proyecto NO ELEGIBLE para Obras por Impuestos"
- Nuevo nivel de prioridad "NO ELEGIBLE" en la tabla de niveles

**Archivos modificados:**
- `src/models/proyecto.py` — Propiedad `es_elegible_oxi` + campos CONFIS
- `src/scoring/motor_arquitectura_c.py` — Lógica del gate + alertas

### Cambio B: Criterio 3 Reescrito con Lógica CONFIS

**Problema:** El criterio de Probabilidad de Aprobación usaba un scoring simple: `(puntaje_sectorial / 10) × 100`. No reflejaba la metodología oficial del CONFIS.

**Solución:** Reemplazo completo con la fórmula del Anexo 2:

```
Score = GrupoPriorización × 20% + ScoreCONFIS × 80%
ScoreCONFIS = ((PuntajeTerritorial + PuntajeSectorial) / 20) × 100
```

**8 grupos de priorización implementados:**

| Grupo | Categoría | Estructuración | Puntaje Base |
|-------|-----------|----------------|-------------|
| 1 | PATR-PDET | Contribuyente paga | 100 |
| 2 | PATR-PDET | Sin estructuración | 90 |
| 3 | PDET | Contribuyente paga | 80 |
| 4 | PDET | Sin estructuración | 70 |
| 5 | ZOMAC | Contribuyente paga | 60 |
| 6 | ZOMAC | Sin estructuración | 50 |
| 7 | Amazonía | Contribuyente paga | 40 |
| 8 | Amazonía | Sin estructuración | 30 |

**Puntaje territorial:** Promedio de IPM, MDM inverso, IICA, CULTIVOS (1-10)
**Puntaje sectorial:** Prioridad del sector en el municipio según matriz PDET (1-10)

**Archivos modificados:**
- `src/criterios/probabilidad_aprobacion_pdet.py` — Reescritura completa
- `tests/test_matriz_pdet.py` — 6 tests actualizados para nueva fórmula

### Cambio C: Alcance Territorial con Puntaje CONFIS

**Problema:** El subcriterio de Alcance Territorial (dentro de Stakeholders) usaba un bonus binario PDET (+20) que no reflejaba la necesidad real del territorio.

**Solución:** Integración del puntaje territorial CONFIS:

| Factor | Antes | Después |
|--------|-------|---------|
| Puntaje territorial | No existía | CONFIS × 3 (máx. 30) |
| Municipios | 10 pts c/u (máx. 30) | 10 pts c/u (máx. 30) |
| Bonus PDET | +20 (binario) | +15 |
| Multi-departamento | +15 | +15 |
| Corredor transmisión | +10 | +10 |
| **Máximo** | **105** (ajustado a 100) | **100** |

**Archivos modificados:**
- `src/criterios/stakeholders.py` — Nueva fórmula de alcance territorial
- `tests/test_stakeholders.py` — 2 tests actualizados

---

## Tests Actualizados

| Archivo | Tests | Cambios |
|---------|-------|---------|
| `tests/test_motor_arquitectura_c.py` | 13 tests | Reescritura completa: gate elegibilidad, CONFIS scoring, alertas |
| `tests/test_matriz_pdet.py` | 17 tests | 6 tests actualizados para fórmula CONFIS |
| `tests/test_stakeholders.py` | Integrados | 2 tests actualizados para nuevo alcance territorial |
| **Total sistema** | **134/134** | **100% passing** |

---

## Entregables Actualizados

### Excel (`Priorizacion_Proyectos_ENLAZA_GEB.xlsx`)
- Fórmula de Prob. CONFIS actualizada en hoja Evaluación Detallada
- Score Total con fórmula CONFIS inline en Registro Proyectos
- Nueva hoja "Metodología CONFIS" con documentación completa, tabla de 8 grupos, fórmulas, y 3 ejemplos de cálculo
- Panel de Control con métricas CONFIS
- Instrucciones actualizadas con secciones CONFIS y gate de elegibilidad

### Dashboard HTML (`Dashboard_Priorizacion_ENLAZA_GEB.html`)
- Scoring CONFIS integrado en cálculo de proyectos
- Datos de proyectos con campos `grupoCONFIS`, `puntajeTerritorial`, `puntajeSectorial`
- Alcance territorial usa puntaje CONFIS × 3 en vez de bonus binario PDET
- Nivel "NO ELEGIBLE" en clasificación
- Etiqueta actualizada a "Prob. CONFIS (20%)"
- Footer: "Arquitectura C v2.1 | CONFIS Integrado"

### Guía Operativa (`Guia_Operativa_Evaluadores_ENLAZA_GEB.docx`)
- Versión 2.1 con metodología CONFIS completa
- Tabla de niveles incluye "NO ELEGIBLE"
- Sección 4 reescrita: Probabilidad de Aprobación CONFIS con gate, fórmula, 8 grupos, puntajes territorial y sectorial, ejemplo numérico
- Sección 3.4 actualizada: Alcance Territorial con CONFIS
- Ejemplo completo (Sección 7) usa metodología CONFIS
- FAQ con preguntas sobre elegibilidad y grupos CONFIS

### README.md
- Reescritura completa con estado actual (v2.1, 134 tests)
- Documentación de SROI logarítmico, CONFIS, gate, rúbricas
- Historial de cambios Fase 1 + Fase 2

---

## Decisiones Técnicas

1. **Excel sin inserción de columnas:** openpyxl tiene problemas severos con `insert_cols()` en hojas con celdas combinadas (MergedCell). Solución: fórmulas CONFIS inline en columnas existentes.

2. **Excel simplificado vs Python completo:** El Excel usa grupo 4 por defecto (PDET sin estructuración) porque no tiene todos los campos CONFIS. El motor Python implementa los 8 grupos completos. Documentado en hoja "Metodología CONFIS".

3. **Puntaje territorial por defecto:** Cuando no hay datos CONFIS para un municipio, se usa puntaje territorial = 5.0 (medio) como fallback.

---

**Versión:** 2.1 (Arquitectura C + CONFIS)
**Tests:** 134/134 passing
**Fecha:** Febrero 2026
