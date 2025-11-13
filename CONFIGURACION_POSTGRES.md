# 🗄️ Configuración de PostgreSQL para Persistencia en Producción

Esta guía explica cómo configurar PostgreSQL para que los proyectos se guarden permanentemente en Streamlit Cloud.

---

## 🎯 ¿Por qué PostgreSQL?

**Problema**: Streamlit Cloud no guarda archivos (como `proyectos.db`) permanentemente. Cuando la app se reinicia, se pierden todos los datos.

**Solución**: Usar una base de datos externa (PostgreSQL) que vive fuera de Streamlit Cloud.

---

## 📋 Pasos para Configurar

### Opción 1: Supabase (Recomendado - Gratis y Fácil)

**1. Crear cuenta en Supabase**
- Ve a [https://supabase.com](https://supabase.com)
- Click en "Start your project"
- Crea una cuenta gratuita

**2. Crear nuevo proyecto**
- Click en "New Project"
- Nombre del proyecto: `sistema-priorizacion-proyectos`
- Database Password: Crea una contraseña segura y **guárdala**
- Region: South America (São Paulo) o el más cercano
- Click en "Create new project"
- Espera 1-2 minutos mientras se crea

**3. Obtener cadena de conexión**
- En el panel de Supabase, ve a "Settings" (⚙️ abajo a la izquierda)
- Click en "Database"
- Scroll hasta "Connection string"
- Copia la cadena que dice "URI" (se ve así):
  ```
  postgresql://postgres.xxxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
  ```
- **IMPORTANTE**: Reemplaza `[YOUR-PASSWORD]` con la contraseña que creaste

**4. Configurar en Streamlit Cloud**
- Ve a tu app en [share.streamlit.io](https://share.streamlit.io)
- Click en los 3 puntos (⋮) → "Settings"
- Click en la pestaña "Secrets"
- Pega esto (reemplazando con tu cadena de conexión):
  ```toml
  [postgres]
  connection_string = "postgresql://postgres.xxxxx:[TU-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
  ```
- Click en "Save"

**5. Redeploy de la app**
- En Streamlit Cloud, click en "Reboot app"
- Espera 1-2 minutos
- ¡Listo! Ahora los datos se guardan permanentemente en Supabase

---

### Opción 2: Railway (Alternativa)

**1. Crear cuenta**
- Ve a [https://railway.app](https://railway.app)
- Regístrate con GitHub

**2. Crear base de datos**
- Click en "New Project" → "Provision PostgreSQL"
- Espera a que se cree

**3. Obtener cadena de conexión**
- Click en tu base de datos PostgreSQL
- Pestaña "Connect"
- Copia "Postgres Connection URL"

**4. Configurar en Streamlit Cloud** (igual que Supabase)
```toml
[postgres]
connection_string = "postgresql://postgres:[PASSWORD]@containers-us-west-xxx.railway.app:5432/railway"
```

---

### Opción 3: ElephantSQL (Más Simple)

**1. Crear cuenta**
- Ve a [https://www.elephantsql.com](https://www.elephantsql.com)
- Click en "Get a managed database today"

**2. Crear instancia gratuita**
- Plan: "Tiny Turtle" (Gratis)
- Name: `proyectos-sociales`
- Region: South America o más cercano
- Click en "Create instance"

**3. Obtener URL**
- Click en tu instancia creada
- Copia la "URL" completa

**4. Configurar en Streamlit Cloud**
```toml
[postgres]
connection_string = "postgres://xxx:yyy@stampy.db.elephantsql.com/xxx"
```

---

## ✅ Verificar que Funciona

**1. Después de configurar los secrets y hacer reboot:**
- Abre tu app en Streamlit Cloud
- Ve a "Nuevo Proyecto"
- Crea un proyecto de prueba
- Click en "Guardar Proyecto"

**2. Reinicia la app manualmente:**
- En Streamlit Cloud: "Reboot app"
- Espera a que cargue

**3. Verifica:**
- El proyecto sigue ahí (antes se perdía)
- ✅ **¡Persistencia funcionando!**

---

## 🔍 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'psycopg2'"
**Solución**: Ya está agregado en `requirements.txt`, espera a que Streamlit Cloud lo instale después del redeploy.

### Error de conexión a PostgreSQL
**Causas comunes**:
1. Contraseña incorrecta en la cadena de conexión
2. Cadena de conexión mal copiada (falta algún carácter)
3. IP de Streamlit Cloud no permitida en firewall

**Soluciones**:
1. Verifica que reemplazaste `[YOUR-PASSWORD]` con tu contraseña real
2. Copia nuevamente la cadena completa desde Supabase/Railway
3. En Supabase: Settings → Database → Disable "Restrict access to IP addresses"

### La app usa SQLite en local pero no cambia a PostgreSQL en producción
**Normal**: El sistema detecta automáticamente:
- **Local**: Usa SQLite (`data/proyectos.db`)
- **Streamlit Cloud con secrets**: Usa PostgreSQL automáticamente

Verás en los logs al iniciar la app:
- Local: `✅ Usando SQLite (local)`
- Producción: `✅ Usando PostgreSQL (producción)`

---

## 📊 Consultar la Base de Datos

### Ver datos en Supabase:
1. Ve a tu proyecto en Supabase
2. Click en "Table Editor" (icono de tabla a la izquierda)
3. Verás las tablas:
   - `proyectos`: Todos tus proyectos guardados
   - `historial_cambios`: Historial de modificaciones

### Ejecutar consultas SQL:
1. En Supabase: "SQL Editor"
2. Ejemplo para ver todos los proyectos:
```sql
SELECT id, nombre, organizacion, presupuesto_total
FROM proyectos
ORDER BY fecha_creacion DESC;
```

---

## 🎓 Capacitación para el Equipo

**Comparte esta guía con tu equipo de gerencia:**

1. Los datos ahora se guardan permanentemente
2. Todos verán los mismos proyectos
3. No se pierden al cerrar el navegador
4. Cambios en tiempo real para todo el equipo

**Nota importante**: Si alguien del equipo corre la app localmente (en su computadora), usará su propia base de datos SQLite local. Solo la versión en Streamlit Cloud comparte datos con PostgreSQL.

---

## 🔒 Seguridad

**Recomendaciones**:
1. **Nunca** compartas la cadena de conexión públicamente
2. Los secrets en Streamlit Cloud están encriptados
3. Cambia la contraseña de PostgreSQL periódicamente
4. En Supabase, habilita "Row Level Security" para mayor protección

---

## 💰 Costos

**Todos los servicios tienen planes gratuitos:**

| Servicio | Plan Gratis | Límite |
|----------|-------------|--------|
| Supabase | ✅ Si | 500MB base de datos, 2GB transferencia |
| Railway | ✅ Si | $5 crédito mensual (suficiente para BD pequeña) |
| ElephantSQL | ✅ Si | 20MB base de datos |

**Para este proyecto**: El plan gratuito es más que suficiente. Se necesitarían miles de proyectos para llenar 20MB.

---

## 📞 Soporte

Si tienes problemas:
1. Verifica los logs en Streamlit Cloud (botón "Manage app" → "Logs")
2. Revisa que la cadena de conexión esté correcta en Secrets
3. Contacta al equipo de desarrollo

---

**Última actualización**: 2025-01-12
**Versión del sistema**: 1.4.0
