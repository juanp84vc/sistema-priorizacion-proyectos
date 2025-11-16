# Script de Validación con Proyectos Reales ENLAZA

## Descripción

Script interactivo para validar el sistema de scoring Arquitectura C con proyectos reales de ENLAZA.

Permite capturar datos de proyectos reales y ver cómo son evaluados por el nuevo motor de scoring con SROI dominante (40%).

## Características

- ✅ **Entrada interactiva**: Captura datos paso a paso con validación
- ✅ **Detección automática PDET**: Identifica municipios PDET y sectores prioritarios
- ✅ **Sugerencias inteligentes**: Muestra sectores con puntajes y estrellas visuales
- ✅ **Validación SROI**: Alertas para valores excepcionales o inválidos
- ✅ **Desglose completo**: Muestra contribución de cada criterio al score
- ✅ **Comparación múltiple**: Compara varios proyectos en tabla ordenada
- ✅ **Visualización clara**: Barras de progreso y códigos de color

## Uso

### Ejecutar el script

```bash
cd /Users/juanpablotovar/Desktop/sistema-priorizacion-proyectos
python3 scripts/validar_proyectos_enlaza.py
```

### Flujo de captura

El script te guiará a través de las siguientes secciones:

#### 1. Datos Básicos
- Nombre del proyecto
- Organización ejecutora
- Descripción breve

#### 2. Ubicación
- Departamento
- Municipio principal
- **Detección automática**: El script verifica si es municipio PDET
- Si es PDET, muestra sectores prioritarios con puntajes

#### 3. Área Geográfica
- Rural / Urbana / Mixta

#### 4. Datos Financieros
- Presupuesto total (COP)
- Duración en meses

#### 5. Beneficiarios
- Beneficiarios directos
- Beneficiarios indirectos (opcional, default: 3x directos)
- Población objetivo

#### 6. SROI (CRÍTICO - 40% del score)
- Valor SROI calculado
- **Validación automática**:
  - SROI < 1.0 → Alerta de rechazo
  - SROI > 7.0 → Solicita documentación
- Metodología utilizada
- Nivel de confianza

#### 7. ODS
- Objetivos de Desarrollo Sostenible vinculados

## Ejemplos de Entrada

### Proyecto PDET de Alta Prioridad

```
Nombre: Alcantarillado Rural Abejorral
Organización: Alcaldía de Abejorral
Departamento: ANTIOQUIA
Municipio: ABEJORRAL

✅ ABEJORRAL es un municipio PDET
   Subregión: Oriente Antioqueño

💡 Sectores prioritarios:
   1. Alcantarillado: 10/10 ⭐⭐⭐⭐⭐
   2. Infraestructura Rural: 9/10 ⭐⭐⭐⭐⭐
   ...

Sectores: Alcantarillado, Infraestructura Rural
Área: RURAL
Presupuesto: 500000000
Duración: 24
Beneficiarios directos: 2000
SROI: 4.2
Metodología: Evaluación post-proyecto
Nivel confianza: ALTO

Resultado esperado:
✅ Score Total: ~88/100
✅ Nivel: MUY ALTA
```

### Proyecto NO-PDET con SROI Alto

```
Nombre: Formación Empresarial Bogotá
Organización: Fundación Capital
Departamento: CUNDINAMARCA
Municipio: BOGOTÁ

ℹ️  BOGOTÁ NO es un municipio PDET
   Este proyecto NO será elegible para Obras por Impuestos

Sectores: Educación
Área: URBANA
Presupuesto: 400000000
Duración: 24
Beneficiarios directos: 1000
SROI: 3.5

Resultado esperado:
Score Total: ~60/100 (sin puntos de Probabilidad PDET)
Nivel: MEDIA
```

### Proyecto Rechazado (SROI < 1.0)

```
Nombre: Evento Cultural Masivo
SROI: 0.7

⚠️  ALERTA: SROI < 1.0 → El proyecto será RECHAZADO
    El proyecto destruye valor social

Resultado esperado:
🚫 Score Total: 0/100
🚫 Nivel: RECHAZADO
```

## Interpretación de Resultados

### Score Total (0-100)

| Rango | Nivel | Interpretación |
|-------|-------|----------------|
| 85-100 | MUY ALTA | Recomendar aprobación prioritaria |
| 70-84 | ALTA | Recomendar aprobación |
| 50-69 | MEDIA | Considerar mejoras antes de aprobación |
| 1-49 | BAJA | Revisar viabilidad |
| 0 | RECHAZADO | SROI < 1.0 - Destruye valor social |

### Desglose por Criterio

```
📊 DESGLOSE POR CRITERIO:

1. SROI (40%):
   Score: 95.0/100 ███████████████████████████████████████████████
   Contribución: 38.0 pts

2. Stakeholders (25%):
   Score: 85.0/100 ██████████████████████████████████████████
   Contribución: 21.3 pts

3. Prob. Aprobación (20%):
   Score: 100.0/100 ██████████████████████████████████████████████████
   Contribución: 20.0 pts

4. Riesgos (15%):
   Score: 70.0/100 ███████████████████████████████████
   Contribución: 10.5 pts

   ────────────────────────────────────────
   TOTAL: 89.8/100
```

### Alertas y Recomendaciones

El sistema genera automáticamente:

- 🚫 **Alertas de rechazo**: SROI < 1.0
- ⚠️  **Alertas de verificación**: SROI > 7.0 (requiere documentación)
- ℹ️  **Alertas informativas**: Municipio NO-PDET
- 💡 **Recomendaciones**: Proyecto PDET con alta prioridad
- ✅ **Aprobaciones**: Proyectos de alta prioridad

## Comparación Múltiple

Al capturar varios proyectos, el script genera tabla comparativa:

```
COMPARACIÓN DE PROYECTOS

#    Proyecto                       Score      Nivel           SROI
────────────────────────────────────────────────────────────────────
1    Alcantarillado Rural Abej..    89.8/100   MUY ALTA         4.2
2    Microcréditos Solidarios       87.5/100   MUY ALTA         8.5
3    Centro Educativo Comunita..    65.2/100   MEDIA            2.5
4    Formación Empresarial Bog..    60.1/100   MEDIA            3.5
5    Evento Cultural Masivo          0.0/100   RECHAZADO        0.7

Estadísticas:
  Promedio: 60.5
  Máximo: 89.8
  Mínimo: 0.0

Distribución por nivel de prioridad:
  MUY ALTA: 2 proyecto(s)
  MEDIA: 2 proyecto(s)
  RECHAZADO: 1 proyecto(s)
```

## Arquitectura C - Pesos Aplicados

El script usa el motor de scoring Arquitectura C con los siguientes pesos:

- **SROI**: 40% (dominante) - Incremento 10.6x vs sistema anterior
- **Stakeholders**: 25%
- **Probabilidad Aprobación**: 20% (con datos oficiales PDET)
- **Riesgos**: 15%

**Total**: 100%

## Validaciones Automáticas

### SROI Gates

1. **Gate de Rechazo** (SROI < 1.0):
   - Score SROI = 0
   - Nivel = RECHAZADO
   - Alerta: "Proyecto destruye valor social"

2. **Gate de Verificación** (SROI > 7.0):
   - Solicita documentación de soporte
   - Requiere metodología y nivel de confianza

3. **Gate de Documentación** (SROI > 5.0):
   - Solicita observaciones sobre cálculo

### PDET Validation

- Verifica automáticamente si municipio está en los 362 PDET/ZOMAC
- Consulta matriz oficial de priorización sectorial
- Asigna puntajes 1-10 según sector
- Proyectos NO-PDET obtienen 0 en Probabilidad

## Notas Técnicas

### Rangos de Conversión SROI

| SROI | Score | Interpretación |
|------|-------|----------------|
| < 1.0 | 0 | RECHAZADO - Destruye valor |
| 1.0-1.99 | 60 | Retorno bajo |
| 2.0-2.99 | 80 | Retorno bueno |
| ≥ 3.0 | 95 | Retorno alto |
| > 7.0 | 95 | EXCEPCIONAL - Requiere verificación |

### Base de Datos

El script usa la base de datos SQLite `data/proyectos.db` que contiene:
- Matriz oficial PDET/ZOMAC (362 municipios)
- 10 sectores priorizados por municipio
- Puntajes 1-10 por sector

## Solución de Problemas

### Error: "No module named 'src'"

```bash
# Asegúrate de ejecutar desde el directorio raíz del proyecto
cd /Users/juanpablotovar/Desktop/sistema-priorizacion-proyectos
python3 scripts/validar_proyectos_enlaza.py
```

### Error: "No se pudo cargar matriz PDET"

Verifica que existe la base de datos:
```bash
ls -la data/proyectos.db
```

Si no existe, ejecuta primero el script de migración:
```bash
python3 scripts/migrar_arquitectura_c.py
```

### Municipio no reconocido como PDET

- Verifica ortografía (usa MAYÚSCULAS)
- Ejemplo correcto: `ABEJORRAL`, no `Abejorral` o `abejorral`
- Consulta lista de 362 municipios PDET en la base de datos

## Próximos Pasos

Después de validar tus proyectos:

1. **Revisar resultados**: Analiza scores y recomendaciones
2. **Ajustar proyectos**: Mejora SROI o selección de sectores si es necesario
3. **Integrar a producción**: Usa los proyectos validados en el sistema principal
4. **Exportar datos**: (Funcionalidad futura) Guardar proyectos en base de datos

## Referencias

- Documentación completa: `docs/ARQUITECTURA_C_IMPLEMENTACION.md`
- Criterio SROI: `docs/SROI_CRITERIO_IMPLEMENTACION.md`
- Criterio Probabilidad: `docs/PROBABILIDAD_APROBACION_PDET.md`
- Tests: `tests/test_motor_arquitectura_c.py`
