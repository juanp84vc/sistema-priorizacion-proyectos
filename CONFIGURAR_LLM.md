# 🚀 Guía de Configuración de LLMs

Esta aplicación ahora soporta **3 proveedores de LLM** para el Asistente IA. Puedes elegir el que mejor se adapte a tus necesidades.

## 📊 Comparación de Proveedores

| Proveedor | Velocidad | Calidad | Costo | Recomendado |
|-----------|-----------|---------|-------|-------------|
| **Claude 3.5 Haiku** | ⚡⚡⚡ Muy rápido (0.5-2s) | ⭐⭐⭐⭐⭐ Excelente | ~$0.50 por 1000 análisis | ✅ **SÍ** |
| **GPT-4o-mini** | ⚡⚡ Rápido (1-2s) | ⭐⭐⭐⭐ Muy buena | ~$0.30 por 1000 análisis | ✅ Alternativa |
| **Gemini 2.5 Flash** | ⚡ Normal (2-4s) | ⭐⭐⭐ Buena | 💰 GRATIS | 🆓 Sin presupuesto |

## 🔑 Cómo Obtener API Keys

### 1. Claude (Anthropic) - RECOMENDADO ⭐

**Por qué Claude:**
- 🏃 **2-3x más rápido** que Gemini
- 🎯 **Mejor calidad** de análisis
- 💰 **$5 gratis** al registrarte
- 🔥 Claude 3.5 Haiku es el **más rápido** del mercado

**Pasos:**
1. Ve a: https://console.anthropic.com/
2. Crea una cuenta o inicia sesión
3. Ve a "Settings" > "API Keys"
4. Crea una nueva API key
5. Copia la key y pégala en `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-...
   LLM_PROVIDER=claude
   ```

**Costos estimados:**
- 100 análisis: ~$0.50
- 1000 análisis: ~$5.00
- Los primeros $5 son gratis

---

### 2. OpenAI (ChatGPT) - Alternativa Rápida

**Por qué OpenAI:**
- ⚡ Rápido (1-2s)
- 📊 Muy buena calidad
- 💰 Más económico que Claude

**Pasos:**
1. Ve a: https://platform.openai.com/signup
2. Crea una cuenta
3. Agrega créditos (mínimo $5)
4. Ve a: https://platform.openai.com/api-keys
5. Crea una nueva API key
6. Copia la key y pégala en `.env`:
   ```
   OPENAI_API_KEY=sk-proj-...
   LLM_PROVIDER=openai
   ```

**Costos estimados:**
- 100 análisis: ~$0.30
- 1000 análisis: ~$3.00

---

### 3. Gemini (Google) - Opción Gratuita

**Por qué Gemini:**
- 🆓 **GRATIS** (1500 requests/día)
- ✅ Ya configurado en tu `.env`
- ⚠️ Más lento (2-4s)

**Pasos:**
1. Ya tienes API key configurada
2. Solo asegúrate que `.env` tenga:
   ```
   GOOGLE_API_KEY=AIzaSyDKgsOPGSG5OInViXth_8SGuQntqWstPHI
   LLM_PROVIDER=gemini
   ```

**Límites:**
- 1500 requests por día
- 2 millones de tokens gratis al mes

---

## ⚙️ Configuración en `.env`

Edita el archivo `.env` en la raíz del proyecto:

```bash
# Elige UNO de estos proveedores:

# Opción 1: Claude (MÁS RÁPIDO - recomendado)
ANTHROPIC_API_KEY=sk-ant-api03-tu-api-key-aqui
LLM_PROVIDER=claude

# Opción 2: OpenAI (rápido y económico)
OPENAI_API_KEY=sk-proj-tu-api-key-aqui
LLM_PROVIDER=openai

# Opción 3: Gemini (gratis, más lento)
GOOGLE_API_KEY=AIzaSyDKgsOPGSG5OInViXth_8SGuQntqWstPHI
LLM_PROVIDER=gemini
```

## 🔄 Cambiar de Proveedor

Puedes cambiar de proveedor en cualquier momento:

1. Edita `.env` y cambia `LLM_PROVIDER=claude` (o `openai` o `gemini`)
2. En la app, haz clic en "🔄 Reiniciar" en la página del Asistente IA
3. Listo! El asistente usará el nuevo proveedor

## 🌐 Configuración en Streamlit Cloud

Si despliegas en Streamlit Cloud:

1. Ve a tu app en https://share.streamlit.io/
2. Settings > Secrets
3. Agrega:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-api03-..."
   OPENAI_API_KEY = "sk-proj-..."
   GOOGLE_API_KEY = "AIzaSy..."
   LLM_PROVIDER = "claude"
   ```

## 💡 Recomendación Final

**Para mejor experiencia:**
1. ✅ **Usa Claude** si tienes presupuesto (~$5-10 mensuales)
2. ✅ Usa OpenAI como alternativa
3. 🆓 Usa Gemini solo si necesitas opción gratuita

**La diferencia de velocidad es significativa:**
- Claude: Respuesta visible en **0.5-1 segundo**
- Gemini: Respuesta visible en **2-3 segundos**

¡Con Claude notarás la diferencia inmediatamente! 🚀
