# 🤖 Asistente IA - Guía de Configuración

El sistema ahora incluye un Asistente IA powered by Google Gemini que proporciona análisis inteligente de proyectos sociales.

## 🚀 Configuración Rápida

### 1. Obtener API Key de Google Gemini

1. Ve a: **https://aistudio.google.com/app/apikey**
2. Inicia sesión con tu cuenta de Google
3. Click en **"Create API key"**
4. Copia tu API key (empieza con `AIzaSy...`)

### 2. Configurar la Aplicación

1. Abre el archivo `.env` en la raíz del proyecto
2. Reemplaza `YOUR_ACTUAL_API_KEY_HERE` con tu API key real:

```env
GOOGLE_API_KEY=AIzaSyC...tu_api_key_aqui
```

3. Guarda el archivo

### 3. Reiniciar la Aplicación

```bash
streamlit run app.py
```

## 💡 Funcionalidades del Asistente

### 1. 💬 Consultar Proyecto
- Haz preguntas sobre proyectos específicos
- Obtén explicaciones sobre scores
- Identifica fortalezas y debilidades
- Genera resúmenes ejecutivos

**Ejemplos de preguntas:**
- "¿Por qué este proyecto tiene bajo score en stakeholders?"
- "¿Qué debo mejorar primero en este proyecto?"
- "¿Cuáles son las fortalezas principales?"

### 2. 📊 Análisis de Cartera
- Analiza tendencias en toda la cartera
- Identifica proyectos con mayor potencial
- Detecta riesgos comunes
- Obtén recomendaciones estratégicas

**Tipos de análisis disponibles:**
- Tendencias y Patrones
- Ranking de Proyectos
- Análisis de Riesgos
- Oportunidades de Mejora

### 3. 🔄 Comparar Proyectos
- Compara dos proyectos lado a lado
- Análisis detallado de diferencias
- Recomendación sobre cuál priorizar
- Identificación de fortalezas relativas

### 4. 💭 Chat Libre
- Conversa libremente sobre tus proyectos
- Mantiene contexto de conversaciones previas
- Responde preguntas generales
- Proporciona consultoría experta

## 📊 Límites de Uso (Cuota Gratuita)

Google Gemini ofrece una cuota gratuita generosa:

- **Gemini 1.5 Flash** (usado por defecto):
  - 15 requests/minuto
  - 1,000,000 tokens/día
  - ✅ **GRATIS**

Esto es más que suficiente para uso normal del sistema.

## 🔒 Seguridad

- ✅ El archivo `.env` está en `.gitignore` (no se sube a GitHub)
- ✅ La API key nunca se expone en el código
- ✅ Usa variables de entorno seguras
- ✅ Sin costo hasta que excedas la cuota gratuita

## ❓ Solución de Problemas

### Error: "API key no configurada"
**Solución:** Verifica que el archivo `.env` existe y contiene tu API key real.

### Error: "Invalid API key"
**Solución:** Verifica que copiaste la API key completa desde Google AI Studio.

### Error: "Quota exceeded"
**Solución:** Has excedido la cuota gratuita. Espera 24 horas o actualiza a plan de pago.

### El asistente responde lento
**Normal:** La primera consulta puede tardar unos segundos. Las siguientes son más rápidas.

## 📚 Más Información

- **Documentación Gemini:** https://ai.google.dev/docs
- **Crear API Keys:** https://aistudio.google.com/app/apikey
- **Pricing:** https://ai.google.dev/pricing

## 🎯 Consejos de Uso

1. **Sé específico en tus preguntas:** Mejor "¿Por qué el costo-efectividad es bajo?" que "¿Qué pasa?"

2. **Usa el contexto:** El asistente tiene acceso a todos los datos del proyecto evaluado

3. **Genera resúmenes ejecutivos:** Útil para presentaciones a stakeholders

4. **Compara antes de decidir:** Usa la función de comparación para elegir entre proyectos similares

5. **Explora tendencias:** El análisis de cartera identifica patrones que no son obvios

---

**¡Disfruta del Asistente IA! 🚀**
