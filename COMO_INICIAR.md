# 🚀 Cómo Iniciar la Aplicación

## ✅ La aplicación ya está arreglada y funcionando!

---

## Método 1: Usando el Script (MÁS FÁCIL)

### Paso 1: Abre Terminal
- Presiona `Cmd + Espacio`
- Escribe "Terminal"
- Presiona Enter

### Paso 2: Copia y pega estos comandos
```bash
cd /Users/juanpablotovar/Desktop/claude_code/sistema-priorizacion-proyectos
./iniciar_app.sh
```

### Paso 3: ¡Listo!
- La app se abrirá automáticamente en tu navegador
- Si no se abre, ve a: http://localhost:8501

---

## Método 2: Comando Directo

```bash
cd /Users/juanpablotovar/Desktop/claude_code/sistema-priorizacion-proyectos && streamlit run app.py
```

---

## 🛑 Para Detener la Aplicación

Presiona **Ctrl + C** en la Terminal

---

## ✅ Verificación

Si ves algo como esto, está funcionando:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.237:8501
```

---

## 🐛 Si Algo Sale Mal

### Error: "command not found: streamlit"
```bash
pip3 install streamlit plotly pandas openpyxl reportlab
```

### Error: "No such file or directory"
Asegúrate de estar en la carpeta correcta:
```bash
cd /Users/juanpablotovar/Desktop/claude_code/sistema-priorizacion-proyectos
pwd  # Debe mostrar la ruta completa
ls app.py  # Debe mostrar "app.py"
```

### Puerto ocupado
Si dice que el puerto 8501 está ocupado:
```bash
streamlit run app.py --server.port 8502
```

---

## 📱 URLs de Acceso

Una vez iniciada, puedes acceder en:
- **Navegador local**: http://localhost:8501
- **Desde otro dispositivo en tu red**: http://192.168.1.237:8501

---

## 🎉 ¡Eso es Todo!

La aplicación estará lista para usar en 3-5 segundos después de ejecutar el comando.
