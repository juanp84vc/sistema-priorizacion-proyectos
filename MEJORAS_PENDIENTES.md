# 📋 Mejoras Pendientes y Futuras

Este documento describe las mejoras planificadas para el Sistema de Priorización de Proyectos Sociales.

---

## ✅ Mejoras Implementadas Recientemente

### 1. **Sistema de Recomendaciones Personalizadas** ✅ IMPLEMENTADO
Al guardar un proyecto, el sistema analiza automáticamente los datos y genera recomendaciones categorizadas:

- **Críticas**: Aspectos que deben corregirse urgentemente
- **Importantes**: Mejoras que aumentarían significativamente el puntaje
- **Opcionales**: Optimizaciones adicionales
- **Fortalezas**: Aspectos destacados del proyecto

El sistema también estima el score potencial del proyecto y sugiere mejoras específicas para:
- Optimizar el número de beneficiarios
- Incluir ODS adicionales prioritarios
- Reforzar las fuentes de financiamiento
- Mejorar la capacidad organizacional
- Optimizar el presupuesto y duración

**Valor añadido**: Los asesores de gerencia pueden usar estas sugerencias como guía para perfeccionar las propuestas antes de su presentación final.

### 2. **Selector Dinámico de Municipios** ✅
- Se actualiza automáticamente según los departamentos seleccionados
- Movido fuera del formulario para permitir actualizaciones en tiempo real

### 3. **Formato de Números Correcto** ✅
- Aplicado en toda la interfaz: 1.234.567,89 (punto para miles, coma para decimales)

### 4. **Prevención de Duplicados** ✅
- Validación de IDs únicos de proyectos

### 5. **Botón Limpiar Formulario** ✅
- Permite restablecer todos los campos rápidamente

### 6. **Exportaciones Completas** ✅
- CSV, Excel, Word y PDF funcionando correctamente
- Todos con formato de números correcto

---

## 🚀 Mejoras Prioritarias (Próximos Pasos)

### 1. **Persistencia de Datos con Base de Datos** 🔴 ALTA PRIORIDAD

**Problema actual**: Los proyectos solo se guardan en la sesión del navegador y se pierden al cerrar o recargar.

**Solución**: Implementar SQLite o PostgreSQL

**Beneficios**:
- ✅ Proyectos guardados permanentemente
- ✅ Todo el equipo ve los mismos datos
- ✅ Historial de cambios
- ✅ Backups automáticos

**Código base**: Ver archivo `DESPLIEGUE.md` sección "Opción 2"

**Archivos a crear**:
```
src/database/
  ├── db_manager.py       # Gestor de base de datos
  ├── migrations.py       # Migraciones de esquema
  └── backup.py          # Sistema de respaldo
```

**Tareas**:
- [ ] Crear esquema de base de datos
- [ ] Implementar CRUD (Create, Read, Update, Delete)
- [ ] Migrar proyectos de session_state a BD
- [ ] Agregar sistema de backups automáticos
- [ ] Implementar sincronización en tiempo real

---

### 2. **Sistema de Autenticación y Roles** 🔴 ALTA PRIORIDAD

**Necesidad**: Controlar quién puede crear, editar o eliminar proyectos

**Roles propuestos**:
- **Administrador**: Control total del sistema
- **Evaluador**: Puede evaluar y priorizar proyectos
- **Creador**: Puede crear y editar sus propios proyectos
- **Visor**: Solo puede ver proyectos y resultados

**Implementación sugerida**:
```bash
pip install streamlit-authenticator
```

**Funcionalidades**:
- [ ] Login seguro con hashed passwords
- [ ] Registro de nuevos usuarios
- [ ] Asignación de roles
- [ ] Permisos diferenciados por rol
- [ ] Registro de actividad (quién creó/modificó cada proyecto)
- [ ] Recuperación de contraseña

---

### 3. **Edición de Proyectos Existentes** 🟡 MEDIA PRIORIDAD

**Funcionalidad**: Permitir modificar proyectos ya guardados

**Interfaz propuesta**:
- Botón "✏️ Editar" en cada proyecto registrado
- Cargar datos del proyecto en el formulario
- Actualizar proyecto con validaciones
- Historial de versiones (opcional)

**Tareas**:
- [ ] Agregar botón de edición en lista de proyectos
- [ ] Cargar datos en el formulario
- [ ] Validar cambios (evitar conflictos de ID)
- [ ] Actualizar proyecto en BD
- [ ] Registrar cambios en historial
- [ ] Notificar a usuarios involucrados

---

### 4. **Búsqueda y Filtros Avanzados** 🟡 MEDIA PRIORIDAD

**Funcionalidad**: Facilitar la búsqueda de proyectos específicos

**Filtros propuestos**:
- 🔍 Búsqueda por nombre o ID
- 🏢 Filtrar por organización
- 📍 Filtrar por departamento/municipio
- 🎯 Filtrar por ODS vinculados
- 💰 Rango de presupuesto
- 📊 Estado del proyecto (propuesta, aprobado, etc.)
- 🌍 Área geográfica

**Interfaz**:
```python
# En página de Dashboard o nueva página "Buscar Proyectos"
col1, col2, col3 = st.columns(3)
with col1:
    busqueda = st.text_input("🔍 Buscar por nombre o ID")
with col2:
    departamento_filtro = st.selectbox("📍 Departamento", ["Todos"] + lista_departamentos)
with col3:
    ods_filtro = st.multiselect("🎯 ODS", opciones_ods)
```

**Tareas**:
- [ ] Crear página de búsqueda avanzada
- [ ] Implementar filtros múltiples
- [ ] Agregar ordenamiento (por presupuesto, beneficiarios, etc.)
- [ ] Exportar resultados de búsqueda
- [ ] Guardar búsquedas frecuentes

---

### 5. **Comparador de Proyectos** 🟡 MEDIA PRIORIDAD

**Funcionalidad**: Comparar 2-4 proyectos lado a lado

**Visualización**:
- Tabla comparativa con métricas clave
- Gráficos radar superpuestos
- Diferencias destacadas
- Recomendación automática (cuál priorizar)

**Interfaz**:
```python
proyectos_comparar = st.multiselect("Selecciona proyectos a comparar (2-4)",
                                     opciones_proyectos, max_selections=4)
if len(proyectos_comparar) >= 2:
    # Mostrar comparación
    df_comparacion = generar_tabla_comparativa(proyectos_comparar)
    st.dataframe(df_comparacion)
```

**Tareas**:
- [ ] Crear función de comparación
- [ ] Diseñar tabla comparativa
- [ ] Generar gráficos comparativos
- [ ] Exportar comparación a PDF/Excel

---

### 6. **Notificaciones y Alertas** 🟢 BAJA PRIORIDAD

**Funcionalidad**: Informar a usuarios sobre eventos importantes

**Tipos de notificaciones**:
- 📬 Nuevo proyecto agregado al sistema
- ✅ Proyecto aprobado/rechazado
- ⏰ Recordatorios de evaluación pendiente
- 📊 Resultados de evaluación disponibles
- 💬 Comentarios en proyectos

**Implementación**:
- [ ] Sistema de notificaciones en app (badge)
- [ ] Notificaciones por email (opcional)
- [ ] Panel de notificaciones en sidebar
- [ ] Preferencias de notificación por usuario

---

### 7. **Dashboard Interactivo Mejorado** 🟢 BAJA PRIORIDAD

**Mejoras propuestas**:
- 📅 Filtros por rango de fechas
- 📊 Más gráficos interactivos (Sankey, Treemap)
- 🗺️ Mapa de Colombia con proyectos por departamento
- 📈 Tendencias temporales
- 🎨 Temas personalizables (claro/oscuro)

**Gráficos nuevos**:
- Mapa de calor por departamento
- Flujo de Sankey: ODS → Proyectos → Beneficiarios
- Treemap de presupuestos por organización
- Línea temporal de proyectos

**Tareas**:
- [ ] Agregar Plotly Mapbox para visualización geográfica
- [ ] Implementar filtros de fecha
- [ ] Crear gráficos adicionales
- [ ] Agregar selector de tema (claro/oscuro)

---

### 8. **Exportación de Recomendaciones** 🟢 BAJA PRIORIDAD

**Funcionalidad**: Exportar las recomendaciones personalizadas a documentos

**Formatos**:
- 📄 PDF: Reporte de optimización del proyecto
- 📝 Word: Documento editable con sugerencias
- 📧 Email: Enviar recomendaciones al responsable del proyecto

**Tareas**:
- [ ] Crear plantilla de reporte de recomendaciones
- [ ] Agregar botón de exportación
- [ ] Implementar envío por email (opcional)

---

### 9. **Módulo de Comentarios y Colaboración** 🟢 BAJA PRIORIDAD

**Funcionalidad**: Permitir que el equipo comente y discuta proyectos

**Características**:
- 💬 Comentarios por proyecto
- 📌 Menciones (@usuario)
- 🔔 Notificaciones de respuestas
- ✅ Marcar comentarios como resueltos

**Implementación**:
```python
# En cada proyecto
st.markdown("### 💬 Comentarios")
nuevo_comentario = st.text_area("Agregar comentario")
if st.button("Publicar"):
    guardar_comentario(proyecto_id, usuario, nuevo_comentario)
```

**Tareas**:
- [ ] Crear tabla de comentarios en BD
- [ ] Interfaz de comentarios
- [ ] Sistema de menciones
- [ ] Notificaciones de nuevos comentarios

---

### 10. **Importación Masiva de Proyectos** 🟢 BAJA PRIORIDAD

**Funcionalidad**: Cargar múltiples proyectos desde Excel/CSV

**Proceso**:
1. Descargar plantilla Excel
2. Llenar datos de proyectos
3. Subir archivo
4. Validar datos
5. Importar proyectos

**Tareas**:
- [ ] Crear plantilla Excel
- [ ] Validador de datos
- [ ] Interfaz de carga
- [ ] Reporte de errores/advertencias

---

## 📝 Notas de Implementación

### Priorización Sugerida

**Fase 1** (Crítico para producción):
1. Persistencia de datos (Base de datos)
2. Autenticación y roles
3. Sistema de recomendaciones ✅ COMPLETADO

**Fase 2** (Mejoras de experiencia):
4. Edición de proyectos
5. Búsqueda y filtros avanzados
6. Comparador de proyectos

**Fase 3** (Funcionalidades avanzadas):
7. Notificaciones
8. Dashboard mejorado
9. Módulo de comentarios

**Fase 4** (Optimizaciones):
10. Importación masiva
11. Exportación de recomendaciones

---

## 🛠️ Recursos Necesarios

### Dependencias adicionales:
```bash
# Base de datos
pip install sqlalchemy alembic psycopg2-binary

# Autenticación
pip install streamlit-authenticator bcrypt

# Notificaciones por email (opcional)
pip install sendgrid

# Mapas interactivos
pip install folium streamlit-folium
```

### Infraestructura:
- Servidor de base de datos (PostgreSQL recomendado)
- Servidor de aplicación (Streamlit Cloud, Heroku, AWS, Azure)
- Servicio de email (SendGrid, AWS SES) - opcional
- Sistema de backups automatizados

---

## 📞 Contacto y Soporte

Para solicitar la implementación de alguna mejora específica o reportar issues:
- Crear issue en el repositorio de GitHub
- Contactar al equipo de desarrollo
- Revisar documentación en `DESPLIEGUE.md`

---

**Última actualización**: 2025-01-12
**Versión del sistema**: 1.1.0
