# Solución: Problema de Conexión PostgreSQL con Supabase

## Problema Identificado

Las tablas no se creaban en Supabase debido a un **formato incorrecto en la cadena de conexión**.

### ❌ Formato Incorrecto (Pooler)
```
postgresql://postgres.xgqljxgjtscyczbhybqt:Inteligenciaa25*@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
```

**Error:** `FATAL: Tenant or user not found`

### ✅ Formato Correcto (Conexión Directa)
```
postgresql://postgres:Inteligenciaa25*@db.xgqljxgjtscyczbhybqt.supabase.co:5432/postgres
```

## Diferencias Clave

| Aspecto | Pooler (Incorrecto) | Directo (Correcto) |
|---------|---------------------|-------------------|
| **Usuario** | `postgres.xgqljxgjtscyczbhybqt` | `postgres` |
| **Host** | `aws-0-sa-east-1.pooler.supabase.com` | `db.xgqljxgjtscyczbhybqt.supabase.co` |
| **Puerto** | `6543` | `5432` |

## Acciones Tomadas

### 1. Creación Manual de Tablas
- ✅ Ejecutado script `create_tables_manual.py`
- ✅ Tabla `consultas_ia` creada exitosamente
- ✅ Índices creados: `idx_proyecto_id`, `idx_timestamp`, `idx_tipo_analisis`

### 2. Actualización de Documentación
- ✅ `.streamlit/secrets.toml.example` actualizado con formato correcto
- ✅ Agregados comentarios explicativos

## Próximos Pasos

### Para Activar PostgreSQL en Streamlit Cloud:

1. **Actualizar Secrets en Streamlit Cloud** con el formato correcto:
   ```toml
   GOOGLE_API_KEY = "AIzaSyDKgsOPGSG5OInViXth_8SGuQntqWstPHI"
   LLM_PROVIDER = "gemini"

   [postgres]
   connection_string = "postgresql://postgres:Inteligenciaa25*@db.xgqljxgjtscyczbhybqt.supabase.co:5432/postgres"
   connection_string_historial = "postgresql://postgres:Inteligenciaa25*@db.xgqljxgjtscyczbhybqt.supabase.co:5432/postgres"
   ```

2. **Reboot de la aplicación** en Streamlit Cloud

3. **Verificar logs** - Deberías ver:
   ```
   ✅ HistorialIA usando PostgreSQL (producción)
   ```

## Estado Actual

### ✅ Funcionando
- Proyectos con PostgreSQL persistente
- Tablas de Historial IA creadas en Supabase
- Código listo para PostgreSQL

### ⏳ Pendiente
- Actualizar secrets en Streamlit Cloud con formato correcto
- Verificar que psycopg2-binary se instale correctamente
- Confirmar logs de PostgreSQL en producción

## Notas Técnicas

### ¿Por qué falló el formato pooler?

El formato pooler de Supabase incluye el project reference en el nombre de usuario:
- `postgres.PROJECT_REF`

Pero esto solo funciona con algunas configuraciones específicas. La conexión directa es más confiable:
- Usuario: `postgres` (sin project reference)
- Host: `db.PROJECT_REF.supabase.co`

### Ventajas de la Conexión Directa

1. **Compatible** con todas las herramientas PostgreSQL estándar
2. **Sin límites** de conexión del pooler
3. **Mejor debugging** - errores más claros
4. **Más estable** para aplicaciones de largo recorrido

### Cuándo Usar Pooler

El pooler (puerto 6543) es útil para:
- Aplicaciones serverless con muchas conexiones concurrentes
- Funciones edge que necesitan connection pooling automático
- Workloads con picos de tráfico muy altos

Para Streamlit Cloud con conexiones persistentes, la conexión directa es más apropiada.

## Verificación de Tablas

Puedes verificar que las tablas existen ejecutando:

```python
python3 create_tables_manual.py
```

Salida esperada:
```
🔗 Conectando a PostgreSQL...
✅ Conexión establecida
📝 Creando tabla consultas_ia...
✅ Tabla consultas_ia creada
📝 Creando índices...
✅ Índices creados

🎉 ¡Tablas creadas exitosamente en Supabase!

📊 Verificando tablas existentes...
Tablas encontradas: 1
  - consultas_ia

🔌 Conexión cerrada
```

## Recursos

- [Supabase Database Connections](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)
