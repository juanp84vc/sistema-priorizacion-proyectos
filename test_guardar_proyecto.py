"""
Script de prueba para verificar que podemos guardar proyectos en Supabase.
"""
import sys
from pathlib import Path
import uuid

# Agregar src al path
src_path = str(Path(__file__).parent / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models.proyecto import ProyectoSocial, AreaGeografica, EstadoProyecto
from database.postgres_manager import PostgreSQLManager

# DIRECT CONNECTION (para ejecutar desde local)
CONNECTION_STRING = "postgresql://postgres:Inteligenciaa25*@db.xgqljxgjtscyczbhybqt.supabase.co:5432/postgres"

def test_crear_proyecto():
    """Prueba crear un proyecto en Supabase."""
    print("🔗 Conectando a PostgreSQL...")

    # Inicializar el gestor
    db = PostgreSQLManager(CONNECTION_STRING)
    print("✅ Gestor PostgreSQL inicializado")

    # Crear un proyecto de prueba
    print("\n📝 Creando proyecto de prueba...")
    proyecto_id = f"TEST-{uuid.uuid4().hex[:8].upper()}"
    proyecto = ProyectoSocial(
        id=proyecto_id,
        nombre="Proyecto de Prueba - Persistencia Supabase",
        organizacion="Organización de Prueba",
        descripcion="Este es un proyecto de prueba para verificar la persistencia en Supabase PostgreSQL",
        beneficiarios_directos=100,
        beneficiarios_indirectos=500,
        duracion_meses=12,
        presupuesto_total=50000000.0,
        ods_vinculados=["ODS 1: Fin de la pobreza", "ODS 4: Educación de calidad"],
        area_geografica=AreaGeografica.URBANA,
        poblacion_objetivo="Niños y adolescentes en situación de vulnerabilidad",
        departamentos=["Cundinamarca"],
        municipios=["Bogotá D.C."],
        estado=EstadoProyecto.EVALUACION,
        indicadores_impacto=["Número de beneficiarios directos", "Tasa de permanencia escolar"]
    )

    print(f"  ID: {proyecto.id}")
    print(f"  Nombre: {proyecto.nombre}")

    # Guardar en base de datos
    print("\n💾 Guardando proyecto en Supabase...")
    resultado = db.crear_proyecto(proyecto)

    if resultado:
        print("✅ ¡Proyecto guardado exitosamente!")

        # Verificar que se guardó
        print("\n🔍 Verificando que el proyecto se guardó...")
        proyecto_recuperado = db.obtener_proyecto(proyecto.id)

        if proyecto_recuperado:
            print("✅ Proyecto recuperado correctamente")
            print(f"  ID: {proyecto_recuperado.id}")
            print(f"  Nombre: {proyecto_recuperado.nombre}")
            print(f"  Organización: {proyecto_recuperado.organizacion}")
            print(f"  Beneficiarios directos: {proyecto_recuperado.beneficiarios_directos}")

            # Listar todos los proyectos
            print("\n📊 Listando todos los proyectos en Supabase...")
            todos = db.obtener_todos_proyectos()
            print(f"Total de proyectos: {len(todos)}")
            for p in todos:
                print(f"  - {p.nombre} (ID: {p.id})")

            return True
        else:
            print("❌ Error: No se pudo recuperar el proyecto")
            return False
    else:
        print("❌ Error al guardar el proyecto")
        return False

if __name__ == "__main__":
    try:
        exito = test_crear_proyecto()
        print("\n" + "="*60)
        if exito:
            print("🎉 ÉXITO: El proyecto se guardó y recuperó correctamente")
            print("✅ La persistencia en Supabase está funcionando")
        else:
            print("❌ FALLO: Hubo un problema con la persistencia")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
