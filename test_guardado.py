#!/usr/bin/env python3
"""
Script de prueba para verificar el guardado de proyectos.
"""
import sys
sys.path.insert(0, 'src')

from database.db_manager import get_db_manager
from models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto

# Crear proyecto de prueba
proyecto_test = ProyectoSocial(
    id="test-proyecto-001",
    nombre="Proyecto de Prueba Guardado",
    organizacion="ENLAZA GEB",
    descripcion="Proyecto de prueba para verificar guardado",
    presupuesto_total=100000000,
    beneficiarios_directos=100,
    beneficiarios_indirectos=400,
    duracion_estimada_meses=12,
    duracion_meses=12,
    departamentos=["CESAR"],
    municipios=["AGUSTÍN CODAZZI"],
    area_geografica=AreaGeografica.RURAL,
    poblacion_objetivo="Comunidad rural",
    ods_vinculados=[],
    indicadores_impacto={'sroi': 3.5},
    tiene_municipios_pdet=True,
    puntajes_pdet={'energia': 10},
    puntaje_sectorial_max=10,
    sectores=['energia'],
    pertinencia_operacional=4,
    mejora_relacionamiento=5,
    en_corredor_transmision=True,
    stakeholders_involucrados=['autoridades_locales', 'lideres_comunitarios'],
    riesgo_tecnico_probabilidad=2,
    riesgo_tecnico_impacto=2,
    riesgo_social_probabilidad=2,
    riesgo_social_impacto=2,
    riesgo_financiero_probabilidad=2,
    riesgo_financiero_impacto=2,
    riesgo_regulatorio_probabilidad=2,
    riesgo_regulatorio_impacto=2
)

print("🧪 Probando guardado de proyecto...")
print(f"Proyecto: {proyecto_test.nombre}")
print(f"ID: {proyecto_test.id}")
print()

# Obtener DB manager
db = get_db_manager()

# Intentar guardar
try:
    resultado = db.crear_proyecto(proyecto_test)
    
    if resultado:
        print("✅ ÉXITO: Proyecto guardado correctamente")
        print()
        
        # Verificar que se guardó
        proyecto_recuperado = db.obtener_proyecto(proyecto_test.id)
        if proyecto_recuperado:
            print("✅ VERIFICADO: Proyecto recuperado de la base de datos")
            print(f"   - Nombre: {proyecto_recuperado.nombre}")
            print(f"   - Organización: {proyecto_recuperado.organizacion}")
            print(f"   - Presupuesto: ${proyecto_recuperado.presupuesto_total:,.0f}")
        else:
            print("❌ ERROR: No se pudo recuperar el proyecto")
    else:
        print("⚠️  ADVERTENCIA: El proyecto ya existe en la base de datos")
        print("   (Esto es normal si ya ejecutaste este script antes)")
        
        # Verificar que existe
        proyecto_recuperado = db.obtener_proyecto(proyecto_test.id)
        if proyecto_recuperado:
            print("✅ CONFIRMADO: El proyecto existe en la base de datos")
        
except Exception as e:
    print(f"❌ ERROR al guardar: {e}")
    import traceback
    traceback.print_exc()

print()
print("📊 Proyectos en la base de datos:")
todos = db.obtener_todos_proyectos()
print(f"Total: {len(todos)} proyectos")
for p in todos:
    print(f"  - {p.id}: {p.nombre}")
