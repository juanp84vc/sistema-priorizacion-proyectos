# Guía de Despliegue - Sistema de Priorización de Proyectos

Esta guía te ayudará a desplegar el sistema para que tu equipo pueda acceder y colaborar en línea.

## Opción 1: Despliegue en Streamlit Community Cloud (GRATIS y FÁCIL)

**Ventajas:**
- ✅ Completamente GRATIS
- ✅ Muy fácil de configurar (menos de 10 minutos)
- ✅ Tu equipo puede acceder desde cualquier lugar con internet
- ✅ Actualizaciones automáticas cuando modificas el código

**Pasos:**

### 1. Subir el código a GitHub

```bash
# Desde la carpeta del proyecto
cd /Users/juanpablotovar/Desktop/claude_code/sistema-priorizacion-proyectos

# Inicializar repositorio git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Crear primer commit
git commit -m "Sistema de priorización de proyectos sociales"

# Crear repositorio en GitHub (ve a https://github.com/new)
# Luego conecta tu repositorio local:
git remote add origin https://github.com/TU_USUARIO/sistema-priorizacion-proyectos.git
git branch -M main
git push -u origin main
```

### 2. Desplegar en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en "New app"
4. Selecciona:
   - **Repository:** tu-usuario/sistema-priorizacion-proyectos
   - **Branch:** main
   - **Main file path:** app.py
5. Haz clic en "Deploy"

¡Listo! En unos minutos tendrás una URL pública como `https://tu-app.streamlit.app`

### 3. Compartir con tu equipo

Simplemente comparte la URL con los miembros de tu equipo. Ellos podrán:
- ✅ Ver todos los proyectos
- ✅ Crear nuevos proyectos
- ✅ Evaluar la cartera
- ✅ Exportar resultados

**IMPORTANTE:** Con Streamlit Community Cloud, los datos se almacenan en la sesión del navegador. Para persistencia de datos, ve a la Opción 2.

---

## Opción 2: Despliegue con Base de Datos (Persistencia de Datos)

Para que los proyectos se guarden permanentemente y todos vean los mismos datos:

### Paso 1: Agregar persistencia con SQLite

Crear archivo `src/database/db_manager.py`:

```python
import sqlite3
import json
from pathlib import Path
from typing import List
from models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto

class DatabaseManager:
    def __init__(self, db_path: str = "proyectos.db"):
        self.db_path = db_path
        self._crear_tablas()

    def _crear_tablas(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS proyectos (
                    id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    organizacion TEXT NOT NULL,
                    descripcion TEXT,
                    beneficiarios_directos INTEGER,
                    beneficiarios_indirectos INTEGER,
                    duracion_meses INTEGER,
                    presupuesto_total REAL,
                    ods_vinculados TEXT,
                    area_geografica TEXT,
                    poblacion_objetivo TEXT,
                    departamentos TEXT,
                    municipios TEXT,
                    estado TEXT,
                    indicadores_impacto TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def guardar_proyecto(self, proyecto: ProyectoSocial):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO proyectos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                proyecto.id,
                proyecto.nombre,
                proyecto.organizacion,
                proyecto.descripcion,
                proyecto.beneficiarios_directos,
                proyecto.beneficiarios_indirectos,
                proyecto.duracion_meses,
                proyecto.presupuesto_total,
                json.dumps(proyecto.ods_vinculados),
                proyecto.area_geografica.value,
                proyecto.poblacion_objetivo,
                json.dumps(proyecto.departamentos),
                json.dumps(proyecto.municipios),
                proyecto.estado.value,
                json.dumps(proyecto.indicadores_impacto)
            ))

    def obtener_todos_proyectos(self) -> List[ProyectoSocial]:
        # Implementar lectura de proyectos desde la BD
        pass
```

### Paso 2: Desplegar en Heroku, AWS o Azure

Consulta la documentación específica de cada plataforma:

- **Heroku:** [Tutorial Streamlit + Heroku](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)
- **AWS EC2:** Requiere configurar servidor Ubuntu con Python
- **Azure App Service:** Similar a Heroku

---

## Opción 3: Servidor Local para tu Organización

Si prefieres que la aplicación esté solo en la red interna de tu organización:

### 1. Configurar en un servidor local

```bash
# En el servidor (Ubuntu/Linux)
# Instalar dependencias
sudo apt update
sudo apt install python3-pip

# Clonar repositorio
git clone https://github.com/tu-usuario/sistema-priorizacion-proyectos.git
cd sistema-priorizacion-proyectos

# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar aplicación (accesible en la red local)
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### 2. Tu equipo accede con:

```
http://IP_DEL_SERVIDOR:8501
```

Por ejemplo: `http://192.168.1.100:8501`

---

## Gestión de Usuarios y Permisos

Para agregar autenticación (login) y roles de usuario, puedes usar:

### Opción Simple: streamlit-authenticator

```bash
pip install streamlit-authenticator
```

Agrega al inicio de `app.py`:

```python
import streamlit_authenticator as stauth

# Configurar usuarios
names = ['Juan Pérez', 'María García']
usernames = ['jperez', 'mgarcia']
passwords = ['pass123', 'pass456']  # Usar hashed passwords en producción

authenticator = stauth.Authenticate(
    names, usernames, passwords,
    'my_app', 'my_secret_key', cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.write(f'Bienvenido {name}')
    # Tu aplicación aquí
elif authentication_status == False:
    st.error('Usuario/contraseña incorrectos')
```

---

## Backup y Recuperación de Datos

### Opción 1: Exportar/Importar Proyectos

Agregar funcionalidad para exportar todos los proyectos a JSON:

```python
import json

# Exportar
proyectos_json = json.dumps([p.__dict__ for p in st.session_state.proyectos])
st.download_button("💾 Backup Proyectos", proyectos_json, "backup.json")

# Importar
uploaded_file = st.file_uploader("📂 Restaurar Backup")
if uploaded_file:
    proyectos_data = json.loads(uploaded_file.read())
    # Cargar proyectos...
```

---

## Contacto y Soporte

Para más ayuda con el despliegue, consulta:
- [Documentación de Streamlit](https://docs.streamlit.io)
- [Foro de Streamlit](https://discuss.streamlit.io)

---

## Costos Estimados

| Opción | Costo Mensual | Usuarios | Persistencia |
|--------|---------------|----------|--------------|
| Streamlit Cloud (Free) | $0 | Ilimitados | Sesión únicamente |
| Streamlit Cloud (Teams) | $250 | Ilimitados | Con BD externa |
| Heroku Hobby | $7 | Ilimitados | ✅ Incluida |
| AWS EC2 t2.micro | $10 | Ilimitados | ✅ Incluida |
| Servidor Local | $0 | Red interna | ✅ Incluida |

---

**Recomendación:** Comienza con **Streamlit Community Cloud (gratis)** para probar con tu equipo. Si necesitas persistencia de datos, migra a Heroku o implementa la base de datos SQLite.
