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
        # Umbrales para Costo-Efectividad
        self.costo_optimo_beneficiario = 500.0
        self.costo_maximo_beneficiario = 5000.0
        self.costo_ideal_beneficiario = 1000.0

        # Umbrales para duración
        self.duracion_optima_años = (1, 3)

        # Umbrales para beneficiarios
        self.beneficiarios_minimo = 500
        self.beneficiarios_bueno = 1000
        self.beneficiarios_excelente = 5000

        # Umbrales para SROI
        self.sroi_bueno = 2.0
        self.sroi_muy_bueno = 3.0
        self.sroi_excelente = 5.0

        # Umbrales para presupuesto total
        self.presupuesto_bajo = 500_000_000
        self.presupuesto_medio = 2_000_000_000
        self.presupuesto_alto = 5_000_000_000

    def analizar_proyecto(self, proyecto: ProyectoSocial, scores_criterios: Dict = None) -> Dict[str, List[str]]:
        """
        Analiza un proyecto y genera recomendaciones categorizadas basadas en los 4 criterios.

        Args:
            proyecto: Proyecto a analizar
            scores_criterios: Dict con scores de cada criterio (opcional)

        Returns:
            Dict con recomendaciones por categoría (criticas, importantes, opcionales, fortalezas)
        """
        recomendaciones = {
            'criticas': [],      # Deben corregirse urgentemente (score < 40)
            'importantes': [],   # Mejorarían significativamente el score (score 40-70)
            'opcionales': [],    # Optimizaciones adicionales (score 70-85)
            'fortalezas': []     # Aspectos positivos del proyecto (score > 85)
        }

        # Analizar cada criterio del sistema
        self._analizar_costo_efectividad(proyecto, recomendaciones, scores_criterios)
        self._analizar_stakeholders(proyecto, recomendaciones, scores_criterios)
        self._analizar_probabilidad_aprobacion(proyecto, recomendaciones, scores_criterios)
        self._analizar_riesgos(proyecto, recomendaciones, scores_criterios)

        return recomendaciones

    # ============================================================================
    # CRITERIO 1: COSTO-EFECTIVIDAD
    # ============================================================================

    def _analizar_costo_efectividad(self, proyecto: ProyectoSocial, recomendaciones: Dict, scores: Dict = None):
        """
        Analiza el criterio de Costo-Efectividad y genera recomendaciones.

        Factores evaluados:
        - Costo por beneficiario
        - Duración del proyecto
        - Eficiencia (beneficiarios por millón)
        - Pertinencia operacional
        - SROI
        """
        costo_por_beneficiario = proyecto.presupuesto_por_beneficiario
        beneficiarios_por_millon = proyecto.beneficiarios_totales / (proyecto.presupuesto_total / 1_000_000)

        # Obtener score si está disponible
        score_criterio = None
        if scores and 'Relación Costo-Efectividad' in scores:
            score_criterio = scores['Relación Costo-Efectividad'].get('score_base', None)

        # Header del criterio
        if score_criterio:
            if score_criterio < 40:
                recomendaciones['criticas'].append(f"🔴 **COSTO-EFECTIVIDAD (Score: {score_criterio:.1f}/100)** - Requiere mejoras urgentes")
            elif score_criterio < 70:
                recomendaciones['importantes'].append(f"🟡 **COSTO-EFECTIVIDAD (Score: {score_criterio:.1f}/100)** - Requiere optimización")
            elif score_criterio < 85:
                recomendaciones['opcionales'].append(f"🟢 **COSTO-EFECTIVIDAD (Score: {score_criterio:.1f}/100)** - Buen desempeño, puede mejorar")
            else:
                recomendaciones['fortalezas'].append(f"✅ **COSTO-EFECTIVIDAD (Score: {score_criterio:.1f}/100)** - Excelente")

        # 1. Análisis de Costo por Beneficiario
        if costo_por_beneficiario >= self.costo_maximo_beneficiario:
            mejora_necesaria = costo_por_beneficiario - self.costo_ideal_beneficiario
            porcentaje_reduccion = (mejora_necesaria / costo_por_beneficiario) * 100

            recomendaciones['criticas'].append(
                f"   💰 **Costo crítico**: ${costo_por_beneficiario:,.0f}/beneficiario (muy alto)\n"
                f"   • **Meta**: Reducir a máximo ${self.costo_maximo_beneficiario:,.0f}/beneficiario\n"
                f"   • **Ideal**: ${self.costo_ideal_beneficiario:,.0f}/beneficiario\n"
                f"   • **Estrategias**:\n"
                f"      - Aumentar beneficiarios (+50% = costo unitario -33%)\n"
                f"      - Reducir presupuesto total (-{porcentaje_reduccion:.0f}%)\n"
                f"      - Combinar ambas estrategias\n"
                f"   • **Impacto**: +40-50 puntos en score"
            )
        elif costo_por_beneficiario > self.costo_ideal_beneficiario:
            recomendaciones['importantes'].append(
                f"   💰 **Optimizar costo**: ${costo_por_beneficiario:,.0f}/beneficiario\n"
                f"   • **Meta**: Reducir a ${self.costo_ideal_beneficiario:,.0f}/beneficiario\n"
                f"   • **Estrategias**:\n"
                f"      - Ampliar cobertura de beneficiarios\n"
                f"      - Optimizar costos operativos\n"
                f"      - Buscar co-financiamiento\n"
                f"   • **Impacto**: +15-25 puntos en score"
            )
        elif costo_por_beneficiario <= self.costo_optimo_beneficiario:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Excelente eficiencia**: ${costo_por_beneficiario:,.0f}/beneficiario (óptimo)"
            )

        # 2. Análisis de SROI
        sroi = proyecto.indicadores_impacto.get('sroi', 0.0)
        try:
            sroi_valor = float(sroi) if sroi else 0.0

            if sroi_valor == 0:
                recomendaciones['importantes'].append(
                    f"   📊 **Sin SROI documentado**\n"
                    f"   • **Acción**: Calcular el retorno social de la inversión\n"
                    f"   • **Meta**: SROI ≥ 2.0:1 (bueno), idealmente ≥ 3.0:1\n"
                    f"   • **Beneficio**: Hasta +15% en el score\n"
                    f"   • **Impacto**: +5-10 puntos en score"
                )
            elif sroi_valor < self.sroi_bueno:
                recomendaciones['importantes'].append(
                    f"   📊 **SROI bajo**: {sroi_valor:.1f}:1\n"
                    f"   • **Meta**: Aumentar a ≥ 2.0:1 para obtener bonus\n"
                    f"   • **Estrategias**:\n"
                    f"      - Ampliar beneficiarios indirectos\n"
                    f"      - Documentar impactos a largo plazo\n"
                    f"      - Cuantificar beneficios ambientales/sociales\n"
                    f"   • **Impacto**: +3-8 puntos en score"
                )
            elif sroi_valor < self.sroi_excelente:
                nivel = "muy bueno" if sroi_valor >= self.sroi_muy_bueno else "bueno"
                recomendaciones['opcionales'].append(
                    f"   📊 **SROI {nivel}**: {sroi_valor:.1f}:1\n"
                    f"   • **Optimización**: Aumentar a ≥ 5.0:1 para máximo bonus (+15%)\n"
                    f"   • **Impacto potencial**: +2-5 puntos adicionales"
                )
            else:
                recomendaciones['fortalezas'].append(
                    f"   ✅ **SROI excelente**: {sroi_valor:.1f}:1 (≥5.0:1 = +15% bonus)"
                )
        except (ValueError, TypeError):
            pass

        # 3. Análisis de Pertinencia Operacional
        pertinencia = proyecto.indicadores_impacto.get('pertinencia_operacional', 'Media')
        if pertinencia == 'Baja':
            recomendaciones['importantes'].append(
                f"   🎯 **Pertinencia operacional baja**\n"
                f"   • **Acción**: Aumentar alineación con objetivos estratégicos\n"
                f"   • **Penalización actual**: -15%\n"
                f"   • **Meta**: Cambiar a 'Media' o 'Alta'\n"
                f"   • **Impacto**: +10-20 puntos en score"
            )
        elif pertinencia == 'Media':
            recomendaciones['opcionales'].append(
                f"   🎯 **Pertinencia operacional media**\n"
                f"   • **Optimización**: Aumentar a 'Alta' para bonus +15%\n"
                f"   • **Impacto potencial**: +5-10 puntos"
            )
        else:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Alta pertinencia operacional** (+15% bonus)"
            )

        # 4. Análisis de Duración
        if proyecto.duracion_años <= 1:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Duración eficiente**: {proyecto.duracion_años:.1f} años (+10% bonus)"
            )
        elif proyecto.duracion_años > 3:
            recomendaciones['opcionales'].append(
                f"   ⏱️ **Duración extensa**: {proyecto.duracion_años:.1f} años (-5% penalización)\n"
                f"   • **Sugerencia**: Dividir en fases de máximo 3 años\n"
                f"   • **Beneficio**: Eliminar penalización"
            )

        # 5. Análisis de Eficiencia
        if beneficiarios_por_millon > 1000:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Alta eficiencia**: {beneficiarios_por_millon:.0f} beneficiarios/millón (+5% bonus)"
            )

    # ============================================================================
    # CRITERIO 2: RELACIONAMIENTO CON STAKEHOLDERS
    # ============================================================================

    def _analizar_stakeholders(self, proyecto: ProyectoSocial, recomendaciones: Dict, scores: Dict = None):
        """
        Analiza el criterio de Relacionamiento con Stakeholders.

        Factores evaluados:
        - Área geográfica
        - Número de departamentos
        - Cobertura de beneficiarios
        - Costo por beneficiario (viabilidad)
        - Contribución al relacionamiento
        """
        num_departamentos = len(proyecto.departamentos)
        total_beneficiarios = proyecto.beneficiarios_totales

        # Obtener score si está disponible
        score_criterio = None
        if scores and 'Contribución al Relacionamiento con Stakeholders' in scores:
            score_criterio = scores['Contribución al Relacionamiento con Stakeholders'].get('score_base', None)

        # Header del criterio
        if score_criterio:
            if score_criterio < 40:
                recomendaciones['criticas'].append(f"🔴 **STAKEHOLDERS (Score: {score_criterio:.1f}/100)** - Requiere mejoras urgentes")
            elif score_criterio < 70:
                recomendaciones['importantes'].append(f"🟡 **STAKEHOLDERS (Score: {score_criterio:.1f}/100)** - Requiere optimización")
            elif score_criterio < 85:
                recomendaciones['opcionales'].append(f"🟢 **STAKEHOLDERS (Score: {score_criterio:.1f}/100)** - Buen desempeño")
            else:
                recomendaciones['fortalezas'].append(f"✅ **STAKEHOLDERS (Score: {score_criterio:.1f}/100)** - Excelente")

        # 1. Análisis de Cobertura Geográfica
        area = proyecto.area_geografica.value
        if area == "municipal" and num_departamentos == 1:
            recomendaciones['importantes'].append(
                f"   🗺️ **Alcance limitado**: Municipal (1 departamento)\n"
                f"   • **Meta**: Expandir a Departamental (múltiples municipios) o Regional\n"
                f"   • **Estrategias**:\n"
                f"      - Ampliar a 2-3 departamentos vecinos (+10% bonus)\n"
                f"      - Expandir a nivel regional (+25-30 puntos base)\n"
                f"      - Buscar alianzas inter-departamentales\n"
                f"   • **Impacto**: +8-15 puntos en score"
            )
        elif area == "departamental" and num_departamentos < 3:
            recomendaciones['opcionales'].append(
                f"   🗺️ **Ampliar cobertura**: {num_departamentos} departamento(s)\n"
                f"   • **Meta**: 3+ departamentos para bonus multi-departamental (+10%)\n"
                f"   • **Impacto potencial**: +5-10 puntos"
            )
        elif area == "nacional" or num_departamentos >= 5:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Amplia cobertura**: {num_departamentos} departamentos (bonus +10-15%)"
            )

        # 2. Análisis de Beneficiarios
        if total_beneficiarios < self.beneficiarios_minimo:
            recomendaciones['criticas'].append(
                f"   👥 **Pocos beneficiarios**: {total_beneficiarios} personas\n"
                f"   • **Meta mínima**: {self.beneficiarios_minimo} beneficiarios\n"
                f"   • **Ideal**: {self.beneficiarios_bueno}+ para buen score\n"
                f"   • **Estrategias**:\n"
                f"      - Ampliar población objetivo\n"
                f"      - Incluir beneficiarios indirectos (familias, comunidades)\n"
                f"      - Expandir geográficamente\n"
                f"   • **Impacto**: +10-15 puntos en score"
            )
        elif total_beneficiarios < self.beneficiarios_bueno:
            recomendaciones['importantes'].append(
                f"   👥 **Ampliar beneficiarios**: {total_beneficiarios} personas\n"
                f"   • **Meta**: {self.beneficiarios_bueno}+ para mejor score\n"
                f"   • **Ideal**: {self.beneficiarios_excelente}+ para excelencia\n"
                f"   • **Impacto**: +5-10 puntos en score"
            )
        elif total_beneficiarios >= self.beneficiarios_excelente:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Amplia cobertura**: {total_beneficiarios:,} beneficiarios"
            )

        # 3. Análisis de Contribución al Relacionamiento
        contribucion = proyecto.indicadores_impacto.get('contribucion_stakeholders', 'Moderada')
        if contribucion == 'Baja':
            recomendaciones['importantes'].append(
                f"   🤝 **Contribución baja al relacionamiento**\n"
                f"   • **Penalización actual**: -20%\n"
                f"   • **Meta**: Aumentar a 'Moderada' o 'Alta'\n"
                f"   • **Estrategias**:\n"
                f"      - Fortalecer vínculos con comunidades locales\n"
                f"      - Incluir autoridades locales en planificación\n"
                f"      - Documentar impacto en relaciones institucionales\n"
                f"   • **Impacto**: +10-20 puntos en score"
            )
        elif contribucion == 'Moderada':
            recomendaciones['opcionales'].append(
                f"   🤝 **Contribución moderada**\n"
                f"   • **Optimización**: Aumentar a 'Alta' para bonus +20%\n"
                f"   • **Impacto potencial**: +5-12 puntos"
            )
        else:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Alta contribución al relacionamiento** (+20% bonus)"
            )

        # 4. Población Vulnerable
        poblaciones_prioritarias = ["niños", "mujeres", "adultos mayores", "discapacidad",
                                    "desplazados", "víctimas", "indígenas", "afrocolombianos"]
        poblacion_lower = proyecto.poblacion_objetivo.lower()
        tiene_poblacion_vulnerable = any(pop in poblacion_lower for pop in poblaciones_prioritarias)

        if tiene_poblacion_vulnerable:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Población vulnerable**: Mayor impacto social (+5% bonus)"
            )

    # ============================================================================
    # CRITERIO 3: PROBABILIDAD DE APROBACIÓN
    # ============================================================================

    def _analizar_probabilidad_aprobacion(self, proyecto: ProyectoSocial, recomendaciones: Dict, scores: Dict = None):
        """
        Analiza el criterio de Probabilidad de Aprobación Gubernamental.

        Factores evaluados:
        - Viabilidad presupuestaria (costo por beneficiario)
        - Población objetivo prioritaria
        - Alcance geográfico
        - Alineación con sectores ZOMAC/PDET
        - Número de beneficiarios
        """
        costo_por_beneficiario = proyecto.presupuesto_por_beneficiario

        # Obtener score si está disponible
        score_criterio = None
        if scores and 'Probabilidad de Aprobación Gubernamental' in scores:
            score_criterio = scores['Probabilidad de Aprobación Gubernamental'].get('score_base', None)

        # Header del criterio
        if score_criterio:
            if score_criterio < 40:
                recomendaciones['criticas'].append(f"🔴 **PROBABILIDAD APROBACIÓN (Score: {score_criterio:.1f}/100)** - Baja probabilidad")
            elif score_criterio < 70:
                recomendaciones['importantes'].append(f"🟡 **PROBABILIDAD APROBACIÓN (Score: {score_criterio:.1f}/100)** - Probabilidad media")
            elif score_criterio < 85:
                recomendaciones['opcionales'].append(f"🟢 **PROBABILIDAD APROBACIÓN (Score: {score_criterio:.1f}/100)** - Buena probabilidad")
            else:
                recomendaciones['fortalezas'].append(f"✅ **PROBABILIDAD APROBACIÓN (Score: {score_criterio:.1f}/100)** - Alta probabilidad")

        # 1. Análisis de Viabilidad Presupuestaria
        if costo_por_beneficiario > 5000:
            recomendaciones['importantes'].append(
                f"   💰 **Viabilidad presupuestaria desafiante**: ${costo_por_beneficiario:,.0f}/beneficiario\n"
                f"   • **Meta**: Reducir a máximo $5,000/beneficiario\n"
                f"   • **Ideal**: $1,000/beneficiario para máxima viabilidad\n"
                f"   • **Estrategias**: Ver recomendaciones de Costo-Efectividad\n"
                f"   • **Impacto**: +10-20 puntos en score"
            )
        elif costo_por_beneficiario <= 1000:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Alta viabilidad presupuestaria**: ${costo_por_beneficiario:,.0f}/beneficiario"
            )

        # 2. Análisis de Población Objetivo
        poblaciones_prioritarias = ["niños", "niñas", "infancia", "adolescentes", "mujeres",
                                    "adultos mayores", "discapacidad", "desplazados",
                                    "víctimas", "indígenas", "afrocolombianos", "vulnerable"]
        poblacion_lower = proyecto.poblacion_objetivo.lower()
        tiene_poblacion_prioritaria = any(pop in poblacion_lower for pop in poblaciones_prioritarias)

        if not tiene_poblacion_prioritaria:
            recomendaciones['importantes'].append(
                f"   👥 **Sin población prioritaria identificada**\n"
                f"   • **Acción**: Enfocar o incluir poblaciones vulnerables\n"
                f"   • **Poblaciones prioritarias**: Niños, mujeres, adultos mayores,\n"
                f"     desplazados, víctimas, indígenas, afrocolombianos\n"
                f"   • **Impacto**: +15-25 puntos en score"
            )
        else:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Población prioritaria**: Alta prioridad gubernamental (+25 puntos)"
            )

        # 3. Análisis de Alcance Geográfico
        area = proyecto.area_geografica.value
        if area == "municipal":
            recomendaciones['opcionales'].append(
                f"   🗺️ **Alcance municipal**\n"
                f"   • **Optimización**: Expandir a departamental (+4 pts) o regional (+7 pts)\n"
                f"   • **Impacto potencial**: +4-12 puntos"
            )
        elif area == "nacional":
            recomendaciones['fortalezas'].append(
                f"   ✅ **Alcance nacional**: Máximo interés gubernamental (+20 puntos)"
            )

        # 4. Análisis de Sectores ZOMAC/PDET
        sectores = proyecto.indicadores_impacto.get('sectores_zomac', 'Top 4 sectores ZOMAC/PDET')
        if sectores == 'No ZOMAC/PDET o no se alinea':
            recomendaciones['criticas'].append(
                f"   🎯 **Sin alineación ZOMAC/PDET**\n"
                f"   • **Penalización actual**: -15%\n"
                f"   • **Meta**: Alinear con sectores prioritarios ZOMAC/PDET\n"
                f"   • **Estrategias**:\n"
                f"      - Ajustar enfoque a sectores prioritarios\n"
                f"      - Documentar alineación con PDET territorial\n"
                f"      - Incluir componente de construcción de paz\n"
                f"   • **Impacto**: +15-35 puntos en score"
            )
        elif sectores == 'Requiere esfuerzos de alineación':
            recomendaciones['importantes'].append(
                f"   🎯 **Requiere alineación ZOMAC/PDET**\n"
                f"   • **Penalización actual**: -5%\n"
                f"   • **Meta**: Mejorar alineación a Top 4, Top 3 o Top 2\n"
                f"   • **Impacto**: +10-30 puntos en score"
            )
        elif sectores not in ['Top 2 sectores prioritarios ZOMAC/PDET']:
            nivel = "Top 3" if sectores == 'Top 3 sectores ZOMAC/PDET' else "Top 4"
            recomendaciones['opcionales'].append(
                f"   🎯 **Alineación ZOMAC/PDET {nivel}**\n"
                f"   • **Optimización**: Mejorar a Top 2 para máximo bonus (+30%)\n"
                f"   • **Impacto potencial**: +3-8 puntos"
            )
        else:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Top 2 sectores prioritarios ZOMAC/PDET** (+30% bonus máximo)"
            )

        # 5. Análisis de Número de Beneficiarios
        if proyecto.beneficiarios_totales >= 5000:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Alto impacto**: {proyecto.beneficiarios_totales:,} beneficiarios (+10% bonus)"
            )
        elif proyecto.beneficiarios_totales < 1000:
            recomendaciones['opcionales'].append(
                f"   👥 **Ampliar beneficiarios**: {proyecto.beneficiarios_totales} personas\n"
                f"   • **Meta**: 5,000+ para bonus de alto impacto (+10%)\n"
                f"   • **Impacto potencial**: +5-10 puntos"
            )

        # 6. Análisis de Duración
        if proyecto.duracion_años >= 3:
            recomendaciones['opcionales'].append(
                f"   ⏱️ **Duración extensa**: {proyecto.duracion_años:.1f} años\n"
                f"   • **Penalización**: -5% por mayor compromiso requerido\n"
                f"   • **Sugerencia**: Considerar fases más cortas"
            )

    # ============================================================================
    # CRITERIO 4: EVALUACIÓN DE RIESGOS
    # ============================================================================

    def _analizar_riesgos(self, proyecto: ProyectoSocial, recomendaciones: Dict, scores: Dict = None):
        """
        Analiza el criterio de Evaluación de Riesgos.

        Factores evaluados:
        - Riesgo financiero (presupuesto y costo unitario)
        - Riesgo temporal (duración)
        - Riesgo geográfico (complejidad)
        - Riesgo operativo y social
        - Nivel de riesgos (cualitativo)

        Nota: Score alto = Bajo riesgo (escala inversa)
        """
        costo_por_beneficiario = proyecto.presupuesto_por_beneficiario
        presupuesto_total = proyecto.presupuesto_total
        num_departamentos = len(proyecto.departamentos)

        # Obtener score si está disponible
        score_criterio = None
        if scores and 'Evaluación de Riesgos' in scores:
            score_criterio = scores['Evaluación de Riesgos'].get('score_base', None)

        # Header del criterio (invertido: score bajo = riesgo alto)
        if score_criterio:
            if score_criterio < 60:
                recomendaciones['criticas'].append(f"🔴 **RIESGOS (Score: {score_criterio:.1f}/100)** - Riesgo ALTO")
            elif score_criterio < 75:
                recomendaciones['importantes'].append(f"🟡 **RIESGOS (Score: {score_criterio:.1f}/100)** - Riesgo MEDIO")
            elif score_criterio < 85:
                recomendaciones['opcionales'].append(f"🟢 **RIESGOS (Score: {score_criterio:.1f}/100)** - Riesgo BAJO")
            else:
                recomendaciones['fortalezas'].append(f"✅ **RIESGOS (Score: {score_criterio:.1f}/100)** - Riesgo MUY BAJO")

        # 1. Análisis de Riesgo Financiero Unitario
        if costo_por_beneficiario > 5000:
            recomendaciones['criticas'].append(
                f"   💰 **Riesgo financiero alto**: ${costo_por_beneficiario:,.0f}/beneficiario\n"
                f"   • **Problema**: Costo unitario muy alto (baja puntuación de riesgo)\n"
                f"   • **Meta**: Reducir a <$5,000/beneficiario\n"
                f"   • **Impacto**: +8-13 puntos en score de seguridad"
            )
        elif costo_por_beneficiario <= 1000:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Bajo riesgo financiero unitario**: ${costo_por_beneficiario:,.0f}/beneficiario"
            )

        # 2. Análisis de Riesgo por Presupuesto Total
        if presupuesto_total > self.presupuesto_alto:
            recomendaciones['importantes'].append(
                f"   💰 **Presupuesto muy alto**: ${presupuesto_total:,.0f}\n"
                f"   • **Riesgo**: Proyectos grandes tienen mayor riesgo de ejecución\n"
                f"   • **Recomendación**: Dividir en fases o componentes\n"
                f"   • **Impacto**: +3-7 puntos al reducir presupuesto"
            )
        elif presupuesto_total <= self.presupuesto_bajo:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Presupuesto controlado**: ${presupuesto_total:,.0f} (bajo riesgo)"
            )

        # 3. Análisis de Riesgo Temporal
        if proyecto.duracion_años > 3:
            recomendaciones['importantes'].append(
                f"   ⏱️ **Duración extensa**: {proyecto.duracion_años:.1f} años\n"
                f"   • **Riesgo**: Cambios de gobierno, contexto, prioridades\n"
                f"   • **Recomendación**: Máximo 3 años o dividir en fases\n"
                f"   • **Impacto**: +5-10 puntos al reducir duración"
            )
        elif proyecto.duracion_años <= 1:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Duración corta**: {proyecto.duracion_años:.1f} años (bajo riesgo temporal)"
            )

        # 4. Análisis de Riesgo Geográfico
        area = proyecto.area_geografica.value
        if area == "nacional" or num_departamentos >= 10:
            recomendaciones['importantes'].append(
                f"   🗺️ **Alta complejidad geográfica**: {num_departamentos} departamentos\n"
                f"   • **Riesgo**: Coordinación compleja, logística difícil\n"
                f"   • **Recomendación**: Fortalecer equipo regional\n"
                f"   • **Impacto moderado en score**"
            )
        elif area == "municipal":
            recomendaciones['fortalezas'].append(
                f"   ✅ **Alcance focalizado**: Municipal (bajo riesgo operativo)"
            )

        # 5. Análisis de Riesgo Operativo
        if proyecto.beneficiarios_totales < 500:
            recomendaciones['importantes'].append(
                f"   👥 **Pocos beneficiarios**: {proyecto.beneficiarios_totales}\n"
                f"   • **Riesgo**: Dificultad para justificar inversión\n"
                f"   • **Meta**: Mínimo 500, idealmente 1,000+\n"
                f"   • **Impacto**: +2-7 puntos al aumentar beneficiarios"
            )
        elif proyecto.beneficiarios_totales >= 5000:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Muchos beneficiarios**: {proyecto.beneficiarios_totales:,} (bajo riesgo de justificación)"
            )

        # 6. Análisis de Población de Difícil Acceso
        poblaciones_complejas = ["desplazados", "víctimas", "rural dispersa", "difícil acceso",
                                 "conflicto", "vulnerable extrema"]
        poblacion_lower = proyecto.poblacion_objetivo.lower()
        tiene_poblacion_compleja = any(pop in poblacion_lower for pop in poblaciones_complejas)

        if tiene_poblacion_compleja:
            recomendaciones['opcionales'].append(
                f"   👥 **Población de difícil acceso**\n"
                f"   • **Riesgo moderado**: Mayor desafío de ejecución\n"
                f"   • **Recomendación**: Planificar logística robusta\n"
                f"   • **Penalización actual**: -5% en score"
            )

        # 7. Análisis de Nivel de Riesgos (Cualitativo)
        nivel_riesgos = proyecto.indicadores_impacto.get('nivel_riesgos', 'Medios y manejables')
        if nivel_riesgos == 'Altos y complejos':
            recomendaciones['criticas'].append(
                f"   ⚠️ **Riesgos altos y complejos**\n"
                f"   • **Penalización actual**: -30%\n"
                f"   • **Meta**: Reducir a 'Altos pero mitigables' o 'Medios y manejables'\n"
                f"   • **Estrategias**:\n"
                f"      - Desarrollar plan de mitigación robusto\n"
                f"      - Reducir complejidad del proyecto\n"
                f"      - Fortalecer capacidades organizacionales\n"
                f"   • **Impacto**: +15-25 puntos en score"
            )
        elif nivel_riesgos == 'Altos pero mitigables':
            recomendaciones['importantes'].append(
                f"   ⚠️ **Riesgos altos pero mitigables**\n"
                f"   • **Penalización actual**: -15%\n"
                f"   • **Meta**: Reducir a 'Medios y manejables' o 'Bajos y manejables'\n"
                f"   • **Impacto**: +10-20 puntos en score"
            )
        elif nivel_riesgos == 'Medios y manejables':
            recomendaciones['opcionales'].append(
                f"   🎯 **Riesgos medios y manejables**\n"
                f"   • **Optimización**: Reducir a 'Bajos y manejables' para bonus +25%\n"
                f"   • **Impacto potencial**: +8-15 puntos"
            )
        else:
            recomendaciones['fortalezas'].append(
                f"   ✅ **Riesgos bajos y manejables** (+25% bonus en score)"
            )

        # 8. Penalización por Alta Complejidad Regulatoria
        if num_departamentos >= 10 and presupuesto_total >= self.presupuesto_alto:
            recomendaciones['importantes'].append(
                f"   📋 **Alta complejidad regulatoria**\n"
                f"   • **Causa**: {num_departamentos} deptos + presupuesto ${presupuesto_total:,.0f}\n"
                f"   • **Penalización**: -10% en score\n"
                f"   • **Recomendación**: Simplificar alcance o dividir proyecto"
            )

    def generar_score_potencial(self, proyecto: ProyectoSocial, score_actual: float) -> Tuple[float, str]:
        """
        Estima el score potencial si se implementan las recomendaciones.

        Args:
            proyecto: Proyecto a analizar
            score_actual: Score actual del proyecto

        Returns:
            Tuple[score_potencial, mensaje_explicativo]
        """
        mejora_potencial = 0

        # Estimar mejora por cada área crítica
        costo = proyecto.presupuesto_por_beneficiario
        if costo > self.costo_maximo_beneficiario:
            mejora_potencial += 15  # Gran impacto

        sroi = proyecto.indicadores_impacto.get('sroi', 0.0)
        if float(sroi if sroi else 0.0) < self.sroi_bueno:
            mejora_potencial += 8

        if proyecto.beneficiarios_totales < self.beneficiarios_minimo:
            mejora_potencial += 12

        sectores = proyecto.indicadores_impacto.get('sectores_zomac', '')
        if 'No ZOMAC' in sectores or 'Requiere esfuerzo' in sectores:
            mejora_potencial += 10

        nivel_riesgos = proyecto.indicadores_impacto.get('nivel_riesgos', 'Medios')
        if 'Altos' in nivel_riesgos:
            mejora_potencial += 15

        score_potencial = min(score_actual + mejora_potencial, 100)

        if mejora_potencial > 0:
            mensaje = (
                f"Implementando las recomendaciones críticas e importantes, "
                f"el proyecto podría alcanzar ~{score_potencial:.0f} puntos "
                f"(mejora de +{mejora_potencial:.0f} puntos desde {score_actual:.0f})"
            )
        else:
            mensaje = f"El proyecto está bien estructurado con un score de {score_actual:.0f} puntos"

        return score_potencial, mensaje
