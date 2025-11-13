# 📋 Mejoras Pendientes y Futuras

Este documento describe las mejoras planificadas para el Sistema de Priorización de Proyectos Sociales.

---

## ✅ Mejoras Implementadas Recientemente

### 1. **Persistencia de Datos con Base de Datos SQLite** ✅ IMPLEMENTADO (v1.3.0)
Los proyectos ahora se guardan permanentemente en una base de datos SQLite:

- **Base de datos persistente**: Los proyectos ya no se pierden al cerrar el navegador
- **Gestión completa CRUD**: Crear, leer, actualizar y eliminar proyectos desde BD
- **Historial de cambios**: Sistema de auditoría que registra todas las modificaciones
- **Búsqueda avanzada**: Funciones de búsqueda optimizadas a nivel de BD
- **Estadísticas**: Consultas agregadas para métricas del sistema
- **Backups**: Funcionalidad para crear y restaurar copias de seguridad
- **Singleton pattern**: Gestor de BD compartido en toda la aplicación

**Archivos creados**:
- `src/database/db_manager.py`: Gestor completo de base de datos
- `src/database/__init__.py`: Módulo de BD
- `data/proyectos.db`: Base de datos SQLite (no se sube a Git)
- `.gitignore`: Configurado para excluir archivos de datos locales

**Integración**:
- Todas las páginas ahora usan la BD en lugar de session_state
- Los datos persisten entre sesiones y recargas de página
- Múltiples usuarios pueden compartir la misma base de datos

**Valor añadido**: El sistema ahora es apto para producción, permitiendo trabajo colaborativo y garantizando que los datos no se pierdan.

### 2. **Sistema de Recomendaciones Personalizadas** ✅ IMPLEMENTADO
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

### 3. **Búsqueda y Edición de Proyectos** ✅ IMPLEMENTADO (v1.2.0)
Sistema completo de búsqueda, filtrado y edición:

- **Filtros avanzados**: Por texto, organización, departamento, ODS, área, estado, presupuesto
- **Ordenamiento flexible**: Por nombre, presupuesto o beneficiarios
- **Edición completa**: Formulario para modificar todos los campos de un proyecto
- **Validaciones**: Prevención de errores al editar
- **Persistencia**: Cambios guardados en base de datos

### 4. **Selector Dinámico de Municipios** ✅
- Se actualiza automáticamente según los departamentos seleccionados
- Movido fuera del formulario para permitir actualizaciones en tiempo real

### 5. **Formato de Números Correcto** ✅
- Aplicado en toda la interfaz: 1.234.567,89 (punto para miles, coma para decimales)

### 6. **Prevención de Duplicados** ✅
- Validación de IDs únicos de proyectos

### 7. **Botón Limpiar Formulario** ✅
- Permite restablecer todos los campos rápidamente

### 8. **Exportaciones Completas** ✅
- CSV, Excel, Word y PDF funcionando correctamente
- Todos con formato de números correcto

---

## 🚀 Mejoras Prioritarias (Próximos Pasos)

### 1. **Sistema de Autenticación y Roles** 🔴 ALTA PRIORIDAD

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

### 2. **Comparador de Proyectos** 🟡 MEDIA PRIORIDAD

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

### 3. **Notificaciones y Alertas** 🟢 BAJA PRIORIDAD

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

### 4. **Dashboard Interactivo Mejorado** 🟢 BAJA PRIORIDAD

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

### 5. **Exportación de Recomendaciones** 🟢 BAJA PRIORIDAD

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

### 6. **Módulo de Comentarios y Colaboración** 🟢 BAJA PRIORIDAD

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

### 7. **Importación Masiva de Proyectos** 🟢 BAJA PRIORIDAD

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

**Fase 1** (Crítico para producción): ✅ COMPLETADO
1. ✅ Persistencia de datos (Base de datos) - v1.3.0
2. ✅ Edición de proyectos - v1.2.0
3. ✅ Búsqueda y filtros avanzados - v1.2.0
4. ✅ Sistema de recomendaciones - v1.1.0

**Fase 2** (Mejoras de seguridad y experiencia):
1. Autenticación y roles
2. Comparador de proyectos
3. Dashboard mejorado

**Fase 3** (Funcionalidades avanzadas):
4. Notificaciones
5. Módulo de comentarios
6. Exportación de recomendaciones

**Fase 4** (Optimizaciones):
7. Importación masiva
8. Backups automáticos programados

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
**Versión del sistema**: 1.3.0

**Historial de versiones**:
- v1.3.0 (2025-01-12): Persistencia con SQLite
- v1.2.0 (2025-01-12): Búsqueda y edición de proyectos
- v1.1.0 (2025-01-12): Sistema de recomendaciones
- v1.0.0 (2025-01-11): Versión inicial
