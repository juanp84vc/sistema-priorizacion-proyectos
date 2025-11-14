# 🚀 Guía de Despliegue - Streamlit Cloud

## ✅ Checklist previo

- [ ] Tienes una cuenta en GitHub
- [ ] Tienes una cuenta en Streamlit Cloud (gratis en [streamlit.io/cloud](https://streamlit.io/cloud))
- [ ] Tienes tus API Keys de los LLMs que vas a usar

## 📋 Paso 1: Preparar el código

1. **Inicializar Git (si no está inicializado):**
   ```bash
   cd /Users/juanpablotovar/Library/Mobile\ Documents/.Trash/claude_code/sistema-priorizacion-proyectos
   git init
   ```

2. **Verificar que `.gitignore` existe:**
   ```bash
   cat .gitignore
   ```
   Debe incluir `.env` y `.streamlit/secrets.toml` para NO subir tus API keys

3. **Hacer commit:**
   ```bash
   git add .
   git commit -m "Sistema de Priorización con Historial IA y exportación"
   ```

## 📤 Paso 2: Subir a GitHub

1. **Crear repositorio en GitHub:**
   - Ve a [github.com/new](https://github.com/new)
   - Nombre sugerido: `sistema-priorizacion-proyectos`
   - Hazlo **privado** si contiene datos sensibles
   - NO inicialices con README (ya tienes uno)

2. **Conectar y subir:**
   ```bash
   git remote add origin https://github.com/TU_USUARIO/sistema-priorizacion-proyectos.git
   git branch -M main
   git push -u origin main
   ```

## ☁️ Paso 3: Desplegar en Streamlit Cloud

1. **Ir a Streamlit Cloud:**
   - Abre [share.streamlit.io](https://share.streamlit.io)
   - Haz clic en **"New app"**

2. **Configurar la aplicación:**
   - **Repository:** Selecciona tu repositorio
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** Elige un nombre único (ej: `priorizacion-proyectos-tu-nombre`)

3. **Configurar Secrets (MUY IMPORTANTE):**
   - Haz clic en **"Advanced settings..."**
   - En la pestaña **"Secrets"**, pega esto (reemplaza con tus API keys reales):

   ```toml
   # Google Gemini API Key
   GOOGLE_API_KEY = "AIzaSy..."

   # Anthropic Claude API Key (opcional)
   ANTHROPIC_API_KEY = "sk-ant-api03-..."

   # OpenAI API Key (opcional)
   OPENAI_API_KEY = "sk-..."

   # Modelo LLM preferido
   LLM_PROVIDER = "gemini"
   ```

4. **Deploy!**
   - Haz clic en **"Deploy!"**
   - Espera 2-3 minutos mientras se instalan las dependencias
   - Tu app estará en: `https://TU-APP-NOMBRE.streamlit.app`

## 🔧 Paso 4: Verificar funcionamiento

Una vez desplegada, verifica:

- [  ] ✅ La aplicación carga sin errores
- [ ] ✅ Puedes crear proyectos
- [ ] ✅ El Asistente IA funciona (verifica que la API key esté bien)
- [ ] ✅ El Historial IA guarda consultas
- [ ] ✅ Puedes exportar a PDF, Word y Markdown

## 🐛 Solución de problemas

### Error: "No module named 'google.generativeai'"
**Solución:** Verifica que `requirements.txt` esté en la raíz del proyecto

### Error: "API key not valid"
**Solución:**
1. Ve a la configuración de tu app en Streamlit Cloud
2. **Settings** → **Secrets**
3. Verifica que las API keys sean correctas
4. Haz clic en **"Save"**
5. La app se reiniciará automáticamente

### Error: "Database is locked"
**Solución:**
- SQLite tiene limitaciones en entornos compartidos
- Para producción, considera migrar a PostgreSQL
- Ver documentación en `database/MIGRATION.md`

### La app está lenta
**Solución:**
- Streamlit Cloud gratuito tiene recursos limitados
- Verifica que estés usando streaming para respuestas largas
- Considera upgrade a Streamlit Cloud Pro

## 🔄 Actualizar la aplicación

Cuando hagas cambios:

```bash
git add .
git commit -m "Descripción de los cambios"
git push
```

Streamlit Cloud detectará el push y redesplegará automáticamente.

## 📊 Límites de Streamlit Cloud (Free tier)

- **CPU:** Limitado
- **RAM:** ~1GB
- **Storage:** Efímero (se pierde en reinicios)
- **Apps activas:** 1 app privada, apps públicas ilimitadas
- **Horas de uso:** Ilimitadas

⚠️ **Importante:** Para almacenamiento persistente en producción, usa:
- PostgreSQL (recomendado)
- AWS S3 para exports
- Redis para caché

## 🔐 Seguridad

✅ **HACER:**
- Usar secrets de Streamlit Cloud para API keys
- Hacer repositorio privado si contiene datos sensibles
- Rotar API keys periódicamente
- Limitar acceso con autenticación si es necesario

❌ **NO HACER:**
- Subir archivo `.env` a GitHub
- Hardcodear API keys en el código
- Hacer público un repo con datos sensibles
- Compartir tu URL de Streamlit sin control de acceso

## 🆘 Soporte

- Documentación Streamlit: [docs.streamlit.io](https://docs.streamlit.io)
- Foro de Streamlit: [discuss.streamlit.io](https://discuss.streamlit.io)
- GitHub Issues: Crea un issue en tu repositorio

---

¡Listo! Tu aplicación debería estar funcionando en la nube 🎉
