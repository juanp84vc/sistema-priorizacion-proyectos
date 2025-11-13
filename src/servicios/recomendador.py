"""
Sistema de recomendaciones para optimizar proyectos sociales.
Analiza proyectos y sugiere mejoras para maximizar su puntaje.
"""
from typing import List, Dict, Tuple
from models.proyecto import ProyectoSocial


class RecomendadorProyectos:
    """Genera recomendaciones personalizadas para mejorar proyectos."""

    def __init__(self):
        """Inicializa el recomendador con umbrales y mejores prácticas."""
        self.ods_prioritarios = [
            "ODS 1", "ODS 2", "ODS 3", "ODS 4", "ODS 5",
            "ODS 10", "ODS 16"  # ODS de alto impacto social
        ]

        self.ratio_beneficiarios_optimo = 3.0  # Indirectos/Directos ideal
        self.ratio_beneficiarios_minimo = 2.0

        self.costo_beneficiario_maximo = 1000  # USD por beneficiario
        self.costo_beneficiario_optimo = 500

        self.duracion_optima_meses = (12, 36)  # Entre 1 y 3 años

        self.equipo_calificado_minimo = 0.6  # 60%
        self.equipo_calificado_optimo = 0.8  # 80%

        self.fuentes_financiamiento_minimo = 3
        self.fuentes_financiamiento_optimo = 5

    def analizar_proyecto(self, proyecto: ProyectoSocial) -> Dict[str, List[str]]:
        """
        Analiza un proyecto y genera recomendaciones categorizadas.

        Args:
            proyecto: Proyecto a analizar

        Returns:
            Dict con recomendaciones por categoría (criticas, importantes, opcionales)
        """
        recomendaciones = {
            'criticas': [],      # Deben corregirse
            'importantes': [],   # Mejorarían significativamente el score
            'opcionales': [],    # Optimizaciones adicionales
            'fortalezas': []     # Aspectos positivos del proyecto
        }

        # Analizar cada aspecto del proyecto
        self._analizar_beneficiarios(proyecto, recomendaciones)
        self._analizar_presupuesto(proyecto, recomendaciones)
        self._analizar_ods(proyecto, recomendaciones)
        self._analizar_duracion(proyecto, recomendaciones)
        self._analizar_capacidad_organizacional(proyecto, recomendaciones)
        self._analizar_area_geografica(proyecto, recomendaciones)

        return recomendaciones

    def _analizar_beneficiarios(self, proyecto: ProyectoSocial, recomendaciones: Dict):
        """Analiza la estructura de beneficiarios del proyecto."""
        ratio = (proyecto.beneficiarios_indirectos / proyecto.beneficiarios_directos
                if proyecto.beneficiarios_directos > 0 else 0)

        if proyecto.beneficiarios_totales < 100:
            recomendaciones['criticas'].append(
                f"⚠️ El proyecto alcanza solo {proyecto.beneficiarios_totales} beneficiarios. "
                "Considera expandir el alcance para aumentar el impacto (mínimo recomendado: 100 beneficiarios)."
            )
        elif proyecto.beneficiarios_totales >= 1000:
            recomendaciones['fortalezas'].append(
                f"✅ Excelente alcance: {proyecto.beneficiarios_totales} beneficiarios totales."
            )

        if ratio < self.ratio_beneficiarios_minimo:
            recomendaciones['importantes'].append(
                f"📊 El ratio de beneficiarios indirectos/directos es {ratio:.1f}. "
                f"Considera ampliar los beneficiarios indirectos (familias, comunidades) "
                f"para alcanzar un ratio óptimo de {self.ratio_beneficiarios_optimo:.1f}."
            )
        elif ratio >= self.ratio_beneficiarios_optimo:
            recomendaciones['fortalezas'].append(
                f"✅ Excelente multiplicador de impacto: cada beneficiario directo impacta a {ratio:.1f} indirectos."
            )

    def _analizar_presupuesto(self, proyecto: ProyectoSocial, recomendaciones: Dict):
        """Analiza la eficiencia del presupuesto."""
        costo_por_beneficiario = proyecto.presupuesto_por_beneficiario

        if costo_por_beneficiario > self.costo_beneficiario_maximo:
            recomendaciones['importantes'].append(
                f"💰 El costo por beneficiario es ${costo_por_beneficiario:,.2f}, "
                f"que es elevado. Considera optimizar costos o aumentar beneficiarios "
                f"para alcanzar máximo ${self.costo_beneficiario_maximo:,.2f} por persona."
            )
        elif costo_por_beneficiario <= self.costo_beneficiario_optimo:
            recomendaciones['fortalezas'].append(
                f"✅ Excelente eficiencia: ${costo_por_beneficiario:,.2f} por beneficiario."
            )

        if proyecto.presupuesto_total < 50000:
            recomendaciones['opcionales'].append(
                "💡 Considera buscar co-financiamiento para aumentar el impacto del proyecto."
            )

    def _analizar_ods(self, proyecto: ProyectoSocial, recomendaciones: Dict):
        """Analiza la alineación con ODS."""
        ods_del_proyecto = set(proyecto.ods_vinculados)
        ods_prioritarios_presentes = ods_del_proyecto.intersection(self.ods_prioritarios)

        if len(proyecto.ods_vinculados) < 2:
            recomendaciones['importantes'].append(
                "🎯 El proyecto está vinculado a pocos ODS. Analiza si el proyecto "
                "puede contribuir a ODS adicionales (recomendado: 2-4 ODS)."
            )
        elif len(proyecto.ods_vinculados) > 5:
            recomendaciones['opcionales'].append(
                "🎯 El proyecto está vinculado a muchos ODS. Considera enfocarte en "
                "los 3-4 ODS más relevantes para mayor claridad."
            )
        else:
            recomendaciones['fortalezas'].append(
                f"✅ Buena alineación con {len(proyecto.ods_vinculados)} ODS."
            )

        if not ods_prioritarios_presentes:
            ods_sugeridos = ", ".join(list(set(self.ods_prioritarios) - ods_del_proyecto)[:3])
            recomendaciones['importantes'].append(
                f"🎯 Considera vincular el proyecto con ODS prioritarios como: {ods_sugeridos}. "
                "Estos ODS tienen mayor peso en la evaluación."
            )
        else:
            recomendaciones['fortalezas'].append(
                f"✅ El proyecto está alineado con {len(ods_prioritarios_presentes)} ODS prioritarios."
            )

    def _analizar_duracion(self, proyecto: ProyectoSocial, recomendaciones: Dict):
        """Analiza la duración del proyecto."""
        min_meses, max_meses = self.duracion_optima_meses

        if proyecto.duracion_meses < min_meses:
            recomendaciones['importantes'].append(
                f"⏱️ La duración de {proyecto.duracion_meses} meses es muy corta. "
                f"Proyectos de {min_meses}-{max_meses} meses tienen mejor sostenibilidad."
            )
        elif proyecto.duracion_meses > max_meses:
            recomendaciones['opcionales'].append(
                f"⏱️ La duración de {proyecto.duracion_meses} meses es extensa. "
                "Considera dividirlo en fases con entregables claros."
            )
        else:
            recomendaciones['fortalezas'].append(
                f"✅ Duración óptima: {proyecto.duracion_años:.1f} años."
            )

    def _analizar_capacidad_organizacional(self, proyecto: ProyectoSocial, recomendaciones: Dict):
        """Analiza los indicadores de capacidad de la organización."""
        indicadores = proyecto.indicadores_impacto

        # Años de experiencia
        años_exp = indicadores.get('años_experiencia', 0)
        if años_exp < 2:
            recomendaciones['importantes'].append(
                "🏢 La organización tiene poca experiencia. Considera asociarte con "
                "organizaciones experimentadas o destacar capacitaciones recibidas."
            )
        elif años_exp >= 5:
            recomendaciones['fortalezas'].append(
                f"✅ Organización con {años_exp} años de experiencia comprobada."
            )

        # Equipo calificado
        equipo_calificado = indicadores.get('equipo_calificado', 0)
        if equipo_calificado < self.equipo_calificado_minimo:
            recomendaciones['criticas'].append(
                f"⚠️ Solo el {equipo_calificado*100:.0f}% del equipo está calificado. "
                "Invierte en capacitación o contrata personal especializado "
                f"(mínimo recomendado: {self.equipo_calificado_minimo*100:.0f}%)."
            )
        elif equipo_calificado >= self.equipo_calificado_optimo:
            recomendaciones['fortalezas'].append(
                f"✅ Equipo altamente calificado: {equipo_calificado*100:.0f}%."
            )

        # Proyectos exitosos
        proyectos_exitosos = indicadores.get('proyectos_exitosos', 0)
        if proyectos_exitosos == 0:
            recomendaciones['importantes'].append(
                "📊 La organización no reporta proyectos exitosos previos. "
                "Documenta logros anteriores o considera un proyecto piloto."
            )
        elif proyectos_exitosos >= 5:
            recomendaciones['fortalezas'].append(
                f"✅ Trayectoria sólida: {proyectos_exitosos} proyectos exitosos."
            )

        # Fuentes de financiamiento
        fuentes = indicadores.get('fuentes_financiamiento', 0)
        if fuentes < self.fuentes_financiamiento_minimo:
            recomendaciones['importantes'].append(
                f"💰 Solo {fuentes} fuentes de financiamiento. Diversifica para mayor "
                f"sostenibilidad (recomendado: {self.fuentes_financiamiento_minimo}+ fuentes)."
            )
        elif fuentes >= self.fuentes_financiamiento_optimo:
            recomendaciones['fortalezas'].append(
                f"✅ Excelente diversificación: {fuentes} fuentes de financiamiento."
            )

        # Ingresos propios
        ingresos_propios = indicadores.get('ingresos_propios_pct', 0)
        if ingresos_propios < 10:
            recomendaciones['opcionales'].append(
                "💡 Desarrolla estrategias para generar ingresos propios (10-30% ideal) "
                "y mejorar la sostenibilidad financiera."
            )
        elif ingresos_propios >= 20:
            recomendaciones['fortalezas'].append(
                f"✅ Buena autosostenibilidad: {ingresos_propios:.0f}% de ingresos propios."
            )

    def _analizar_area_geografica(self, proyecto: ProyectoSocial, recomendaciones: Dict):
        """Analiza el alcance geográfico."""
        if proyecto.area_geografica.value == "rural":
            recomendaciones['fortalezas'].append(
                "✅ Foco en área rural: mayor impacto en población vulnerable."
            )

        if len(proyecto.departamentos) == 0:
            recomendaciones['criticas'].append(
                "⚠️ No se especificaron departamentos. Define la ubicación geográfica."
            )
        elif len(proyecto.departamentos) >= 3:
            recomendaciones['fortalezas'].append(
                f"✅ Amplia cobertura: {len(proyecto.departamentos)} departamentos."
            )

        if proyecto.municipios and len(proyecto.municipios) >= 5:
            recomendaciones['fortalezas'].append(
                f"✅ Alcance detallado: {len(proyecto.municipios)} municipios específicos."
            )

    def generar_score_potencial(self, proyecto: ProyectoSocial) -> Tuple[float, str]:
        """
        Estima el score potencial si se implementan las recomendaciones críticas.

        Returns:
            Tuple[score_actual_estimado, mejora_potencial]
        """
        # Estimación simple basada en indicadores clave
        score = 50.0  # Base

        # Beneficiarios (20 puntos)
        if proyecto.beneficiarios_totales >= 1000:
            score += 20
        elif proyecto.beneficiarios_totales >= 500:
            score += 15
        elif proyecto.beneficiarios_totales >= 100:
            score += 10
        else:
            score += 5

        # ODS (15 puntos)
        ods_prioritarios = set(proyecto.ods_vinculados).intersection(self.ods_prioritarios)
        score += len(ods_prioritarios) * 3
        score += len(proyecto.ods_vinculados) * 2

        # Eficiencia presupuestaria (15 puntos)
        costo = proyecto.presupuesto_por_beneficiario
        if costo <= self.costo_beneficiario_optimo:
            score += 15
        elif costo <= self.costo_beneficiario_maximo:
            score += 10
        else:
            score += 5

        # Capacidad organizacional (20 puntos)
        indicadores = proyecto.indicadores_impacto
        equipo = indicadores.get('equipo_calificado', 0)
        if equipo >= self.equipo_calificado_optimo:
            score += 10
        elif equipo >= self.equipo_calificado_minimo:
            score += 5

        fuentes = indicadores.get('fuentes_financiamiento', 0)
        score += min(fuentes * 2, 10)

        score = min(score, 100)  # Máximo 100

        # Estimar mejora potencial
        mejora = 0
        if proyecto.beneficiarios_totales < 100:
            mejora += 10
        if len(proyecto.ods_vinculados) < 2:
            mejora += 8
        if equipo < self.equipo_calificado_minimo:
            mejora += 12
        if costo > self.costo_beneficiario_maximo:
            mejora += 8

        score_potencial = min(score + mejora, 100)

        if mejora > 0:
            mensaje = f"Implementando las recomendaciones críticas, el proyecto podría alcanzar ~{score_potencial:.0f} puntos (mejora de +{mejora:.0f} puntos)"
        else:
            mensaje = f"El proyecto está bien estructurado con un score estimado de ~{score:.0f} puntos"

        return score, mensaje
