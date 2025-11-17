# 🧪 INSTRUCCIONES: Test Motor Arquitectura C

## Descripción

Se ha implementado una **página de prueba interactiva** para validar que el Motor de Scoring Arquitectura C está funcionando correctamente en la aplicación Streamlit.

---

## Cómo Acceder

### 1. Ejecutar la aplicación Streamlit

```bash
cd /Users/juanpablotovar/Desktop/sistema-priorizacion-proyectos
streamlit run app.py
```

### 2. Navegar a Test Motor

En el menú lateral, seleccionar: **🧪 Test Motor**

---

## Funcionalidades Disponibles

### Tab 1: 🟢 Proyecto Ideal

**Características:**
- SROI: 4.8 (excelente retorno social)
- Municipio PDET: ✅ Abejorral, Antioquia
- Sector: Alcantarillado (prioridad máxima)
- Stakeholders: Pertinencia MUY ALTA (5/5), Relacionamiento SUSTANCIAL (5/5)
- Riesgos: Muy bajos (nivel 1-2)
- Presupuesto: $450M (sin penalización)
- Duración: 18 meses (sin penalización)

**Score Esperado:** > 85 puntos (Nivel: MUY ALTA o ALTA)

**Desglose esperado:**
- SROI (40%): ~38-40 puntos
- Stakeholders (25%): ~20-22 puntos
- Probabilidad (20%): 20 puntos (PDET máximo)
- Riesgos (15%): ~13-15 puntos (riesgo muy bajo)

**Propósito:** Validar que proyectos óptimos obtienen scores altos.

---

### Tab 2: 🟡 Proyecto Promedio

**Características:**
- SROI: 3.2 (bueno)
- Municipio NO-PDET: ❌ Bogotá
- Stakeholders: Pertinencia MEDIA (3/5), Relacionamiento ALTA (4/5)
- Riesgos: Moderados (nivel 2-3)
- Presupuesto: $300M
- Duración: 24 meses

**Score Esperado:** 60-70 puntos (Nivel: MEDIA o ALTA)

**Desglose esperado:**
- SROI (40%): ~30-32 puntos
- Stakeholders (25%): ~16-18 puntos
- Probabilidad (20%): 0 puntos (NO-PDET)
- Riesgos (15%): ~11-13 puntos

**Propósito:** Validar que proyectos NO-PDET pueden obtener buenos scores compensando con SROI y Stakeholders.

---

### Tab 3: 🔴 Proyecto Alto Riesgo

**Características:**
- SROI: 2.8 (aceptable)
- Municipio PDET: ✅
- Stakeholders: Buenos
- Riesgos: **CRÍTICOS** en todos los tipos (nivel 16-25)
- Presupuesto: $2,000M (penalización -15 pts)
- Duración: 48 meses (penalización -10 pts)
- Múltiples departamentos (penalización -5 pts)

**Score Esperado:** < 60 puntos (Nivel: BAJA o MEDIA)

**Desglose esperado:**
- SROI (40%): ~25-28 puntos
- Stakeholders (25%): ~18-20 puntos
- Probabilidad (20%): 16 puntos (PDET sector vía)
- Riesgos (15%): **< 4 puntos** (riesgos críticos + penalizaciones)

**Propósito:** Validar que riesgos altos penalizan significativamente el score.

---

### Tab 4: 🎛️ Prueba Personalizada

**Controles disponibles:**

**Datos Básicos:**
- Nombre del proyecto
- Presupuesto total ($ COP)
- Beneficiarios directos

**SROI (40%):**
- Slider: 0.5 - 10.0
- Valor sugerido: 3.5

**Stakeholders (25%):**
- Pertinencia Operacional: 1-5
- Mejora Relacionamiento: 1-5

**Probabilidad (20%):**
- Checkbox: ¿Municipio PDET?

**Riesgos (15%):**
- **Riesgo Técnico:** Probabilidad (1-5) × Impacto (1-5)
- **Riesgo Social:** Probabilidad (1-5) × Impacto (1-5)
- **Riesgo Financiero:** Probabilidad (1-5) × Impacto (1-5)
- **Riesgo Regulatorio:** Probabilidad (1-5) × Impacto (1-5)

**Propósito:** Experimentar con diferentes combinaciones de parámetros.

---

## Interpretación de Resultados

### Score Total

El score se muestra en un banner visual con colores:
- **Verde (>80):** Proyecto de alta prioridad
- **Amarillo (60-80):** Proyecto de prioridad media
- **Rojo (<60):** Proyecto de baja prioridad

### Nivel de Prioridad

- **MUY ALTA:** Score ≥ 85
- **ALTA:** Score 70-84
- **MEDIA:** Score 50-69
- **BAJA:** Score < 50
- **RECHAZADO:** SROI < 1.0 (destruye valor social)

### Desglose por Criterio

Cada criterio muestra:
- **Score base** (0-100): Evaluación sin ponderar
- **Contribución ponderada**: Score × peso del criterio
- **Barra de progreso visual**

**Ejemplo:**
```
SROI (40%)
95/100 → 38.0 pts
[████████████████████] 95%
```

### Validación de Suma

La aplicación valida que:
```
Suma de Contribuciones = Score Total
```

Si hay diferencia > 0.01, se muestra error (indica bug en el código).

---

## Casos de Uso

### Caso 1: Validar SROI Dominante (40%)

**Objetivo:** Confirmar que SROI tiene el mayor impacto en el score.

**Pasos:**
1. Ir a Tab "Personalizado"
2. Configurar:
   - SROI: 8.0 (muy alto)
   - Stakeholders: 1/5 (muy bajo)
   - PDET: No
   - Riesgos: Todos 3×3 (moderado)
3. Calcular score
4. **Resultado esperado:** Score alto (>70) gracias a SROI dominante

### Caso 2: Proyecto PDET vs NO-PDET

**Objetivo:** Medir impacto de Probabilidad Aprobación (20%).

**Pasos:**
1. Crear dos proyectos idénticos en "Personalizado"
2. Proyecto A: PDET ✅
3. Proyecto B: PDET ❌
4. **Resultado esperado:** Diferencia de ~20 puntos a favor de PDET

### Caso 3: Impacto de Riesgos Críticos

**Objetivo:** Validar scoring inverso de riesgos.

**Pasos:**
1. Configurar proyecto con:
   - SROI: 5.0
   - Stakeholders: 5/5
   - PDET: Sí
   - Riesgos: Todos 5×5 (CRÍTICOS)
2. **Resultado esperado:**
   - Score Riesgos: < 10/100
   - Contribución Riesgos: < 2 puntos
   - Score total afectado significativamente

---

## Alertas y Recomendaciones

### Alertas Comunes

**🚫 PROYECTO RECHAZADO:**
```
SROI < 1.0 destruye valor social
```
→ Proyecto automáticamente rechazado, score SROI = 0

**⚠️ Error en cálculo:**
```
Error Stakeholders: Campo 'pertinencia_operacional' requerido
```
→ Falta información crítica

**ℹ️ Información PDET:**
```
Proyecto NO elegible para Obras por Impuestos (municipio no PDET)
```
→ Municipio no está en lista PDET/ZOMAC

### Recomendaciones Comunes

**✅ Alta prioridad:**
```
Proyecto de alta prioridad - Recomendar aprobación
```
→ Score ≥ 80

**💡 PDET prioritario:**
```
Proyecto en municipio PDET con alta prioridad sectorial
```
→ PDET + sector con puntaje alto

**⚠️ Baja prioridad:**
```
Proyecto de baja prioridad - Revisar viabilidad
```
→ Score < 50

---

## Detalles Técnicos (Expandible)

Al hacer clic en "🔍 Detalles Técnicos", se muestra JSON con:

```json
{
  "score_total": 87.3,
  "nivel_prioridad": "MUY ALTA",
  "scores_individuales": {
    "sroi": 95.0,
    "stakeholders": 88.5,
    "probabilidad": 100.0,
    "riesgos": 92.0
  },
  "contribuciones": {
    "sroi_40pct": 38.0,
    "stakeholders_25pct": 22.1,
    "probabilidad_20pct": 20.0,
    "riesgos_15pct": 13.8
  },
  "metadata": {
    "version_arquitectura": "C",
    "fecha_calculo": "2025-01-17T20:30:00"
  }
}
```

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'models'"

**Solución:**
```bash
# Asegurar que estás en el directorio correcto
cd /Users/juanpablotovar/Desktop/sistema-priorizacion-proyectos

# Reinstalar dependencias si es necesario
pip3 install -r requirements.txt
```

### Error: "ImportError: cannot import name 'MotorScoringArquitecturaC'"

**Causa:** Motor no está en el path.

**Solución:**
Verificar que existe:
```bash
ls src/scoring/motor_arquitectura_c.py
```

### La página no aparece en el menú

**Solución:**
1. Verificar que app.py tiene el import:
   ```python
   from app_pages import test_motor
   ```
2. Verificar routing:
   ```python
   elif menu_option == "🧪 Test Motor":
       test_motor.show()
   ```
3. Reiniciar Streamlit (Ctrl+C y `streamlit run app.py`)

---

## Próximos Pasos

Una vez validado que el motor funciona correctamente:

1. **Actualizar formulario "Nuevo Proyecto":**
   - Agregar campos de Stakeholders (pertinencia, relacionamiento)
   - Agregar campos de Riesgos (4 tipos × prob/impacto)
   - Integrar cálculo automático de score

2. **Actualizar "Evaluar Cartera":**
   - Ya está usando criterios correctos (fix aplicado)
   - Validar que muestra desglose de Arquitectura C

3. **Dashboard:**
   - Visualizaciones de distribución de scores
   - Análisis comparativo PDET vs NO-PDET
   - Correlación SROI vs Score Total

---

## Validación Completa

Para confirmar que Arquitectura C está 100% operativa:

**Checklist:**
- [ ] Tab "Proyecto Ideal" → Score > 85 ✅
- [ ] Tab "Proyecto Promedio" → Score 60-70 ✅
- [ ] Tab "Alto Riesgo" → Score < 60 ✅
- [ ] Proyecto Custom con SROI 10.0 → Contribución ~40 pts ✅
- [ ] Proyecto PDET vs NO-PDET → Diferencia ~20 pts ✅
- [ ] Suma de contribuciones = Score total ✅
- [ ] Alertas se muestran correctamente ✅
- [ ] Recomendaciones apropiadas ✅

---

## Soporte

Si encuentras algún error o comportamiento inesperado:

1. **Captura de pantalla** del resultado
2. **Copiar JSON** de "Detalles Técnicos"
3. **Descripción** del problema

Esto ayudará a diagnosticar y corregir cualquier issue.

---

**Arquitectura C: 100% Completada** ✅

**Test Motor: Listo para uso** 🚀

**Última actualización:** 17 Enero 2025
