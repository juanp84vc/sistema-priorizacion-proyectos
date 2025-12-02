"""
Modulo de explicaciones detalladas para reportes.
Genera textos explicativos para el comite evaluador.

Este modulo proporciona explicaciones paso a paso de como se calcula
cada criterio de la Arquitectura C, incluyendo formulas y escalas.
"""

from typing import Dict, Any, List, Optional


class ExplicadorCriterios:
    """Genera explicaciones detalladas de cada criterio de Arquitectura C"""

    # =========================================================================
    # CONSTANTES DE ARQUITECTURA C
    # =========================================================================

    PESO_SROI = 0.40
    PESO_STAKEHOLDERS = 0.25
    PESO_PROBABILIDAD = 0.20
    PESO_RIESGOS = 0.15

    # =========================================================================
    # SROI (40%)
    # =========================================================================

    @staticmethod
    def explicar_sroi(sroi_valor: float, score: float, contribucion: float) -> Dict[str, Any]:
        """
        Genera explicacion detallada del SROI.

        Args:
            sroi_valor: Valor SROI del proyecto (ej: 2.5)
            score: Score obtenido (0-100)
            contribucion: Contribucion al score final (0-40)

        Returns:
            Diccionario con explicacion completa
        """
        # Determinar rango y calcular formula
        if sroi_valor < 1.0:
            rango = "Destruye valor"
            nivel = "RECHAZADO"
            color = "rojo"
            formula = f"SROI {sroi_valor:.2f} < 1.0 -> Score = 0 (Automatico)"
            interpretacion = (
                f"El proyecto DESTRUYE valor social. Por cada $1 invertido, "
                f"solo se generan ${sroi_valor:.2f} de valor social. "
                f"Esto significa una perdida neta de ${1-sroi_valor:.2f} por cada peso invertido."
            )
            recomendacion = "RECHAZAR - El proyecto no es viable desde perspectiva de retorno social."

        elif sroi_valor < 2.0:
            rango = "Bajo (1.0 - 2.0)"
            nivel = "PRIORIDAD BAJA"
            color = "amarillo"
            # Formula: Score = 60 (base para SROI 1.0-2.0)
            formula = f"SROI en rango 1.0-2.0 -> Score = 60 (fijo)"
            interpretacion = (
                f"El proyecto genera valor social MARGINAL. Por cada $1 invertido, "
                f"se generan ${sroi_valor:.2f} de valor social. "
                f"Beneficio neto: ${sroi_valor-1:.2f} por peso invertido."
            )
            recomendacion = "EVALUAR - Considerar optimizaciones para mejorar el retorno."

        elif sroi_valor < 3.0:
            rango = "Bueno (2.0 - 3.0)"
            nivel = "PRIORIDAD MEDIA"
            color = "verde_claro"
            formula = f"SROI en rango 2.0-3.0 -> Score = 80 (fijo)"
            interpretacion = (
                f"El proyecto genera BUEN valor social. Por cada $1 invertido, "
                f"se generan ${sroi_valor:.2f} de valor social. "
                f"Beneficio neto: ${sroi_valor-1:.2f} por peso invertido."
            )
            recomendacion = "APROBAR - Retorno social solido que justifica la inversion."

        else:  # sroi >= 3.0
            rango = "Excelente (>= 3.0)"
            nivel = "PRIORIDAD ALTA"
            color = "verde"
            formula = f"SROI >= 3.0 -> Score = 95 (fijo)"
            interpretacion = (
                f"El proyecto genera EXCELENTE valor social. Por cada $1 invertido, "
                f"se generan ${sroi_valor:.2f} de valor social. "
                f"Beneficio neto: ${sroi_valor-1:.2f} por peso invertido."
            )
            recomendacion = "PRIORIZAR - Maximo retorno social, aprobar con prioridad."

            if sroi_valor > 7.0:
                interpretacion += (
                    f"\n\nALERTA: SROI excepcionalmente alto (>{sroi_valor:.1f}). "
                    f"Se recomienda verificar metodologia de calculo."
                )

        return {
            "titulo": "SROI - Retorno Social de Inversion",
            "peso": "40%",
            "peso_decimal": 0.40,
            "definicion": (
                "El SROI (Social Return on Investment) mide cuanto valor social "
                "genera cada peso invertido en el proyecto. Un SROI de 2.5 significa "
                "que por cada $1 invertido, se generan $2.50 de valor social."
            ),
            "valor_input": sroi_valor,
            "score": score,
            "contribucion": contribucion,
            "max_contribucion": 40.0,
            "rango": rango,
            "nivel": nivel,
            "color": color,
            "formula_aplicada": formula,
            "calculo_contribucion": f"Contribucion = {score:.1f} x 0.40 = {contribucion:.1f} puntos",
            "interpretacion": interpretacion,
            "recomendacion": recomendacion,
            "escala_referencia": [
                {"rango": "< 1.0", "score": "0", "nivel": "RECHAZADO", "descripcion": "Destruye valor social"},
                {"rango": "1.0 - 2.0", "score": "60", "nivel": "BAJA", "descripcion": "Valor marginal"},
                {"rango": "2.0 - 3.0", "score": "80", "nivel": "MEDIA", "descripcion": "Buen retorno"},
                {"rango": ">= 3.0", "score": "95", "nivel": "ALTA", "descripcion": "Excelente retorno"},
            ]
        }

    # =========================================================================
    # STAKEHOLDERS (25%)
    # =========================================================================

    @staticmethod
    def explicar_stakeholders(
        pertinencia: int,
        relacionamiento: int,
        score_pertinencia: float,
        score_relacionamiento: float,
        score_alcance: float,
        score_tipo: float,
        score_total: float,
        contribucion: float,
        en_corredor: bool = False,
        stakeholders_lista: List[str] = None,
        num_municipios: int = 1
    ) -> Dict[str, Any]:
        """
        Genera explicacion detallada de Stakeholders.

        Args:
            pertinencia: Valor de pertinencia operacional (1-5)
            relacionamiento: Valor de mejora relacionamiento (1-5)
            score_pertinencia: Score del componente pertinencia (0-100)
            score_relacionamiento: Score del componente relacionamiento (0-100)
            score_alcance: Score del componente alcance territorial (0-100)
            score_tipo: Score del componente tipo stakeholders (0-100)
            score_total: Score total del criterio (0-100)
            contribucion: Contribucion al score final (0-25)
            en_corredor: Si esta en corredor de transmision
            stakeholders_lista: Lista de stakeholders involucrados
            num_municipios: Numero de municipios del proyecto

        Returns:
            Diccionario con explicacion completa
        """
        # Mapeos de escalas
        escala_pertinencia = {
            5: ("Muy Alta", "Critico para las operaciones de ENLAZA", 100),
            4: ("Alta", "Importante para las operaciones", 85),
            3: ("Media", "Util para las operaciones", 65),
            2: ("Baja", "Marginal para las operaciones", 40),
            1: ("Nula", "Sin pertinencia operacional", 20)
        }

        escala_relacionamiento = {
            5: ("Sustancial", "Transforma la relacion con comunidades", 100),
            4: ("Genera Confianza", "Mejora significativa del relacionamiento", 85),
            3: ("Moderada", "Contribucion positiva al relacionamiento", 65),
            2: ("Limitada", "Mejora menor del relacionamiento", 40),
            1: ("No Aporta", "Sin efecto en el relacionamiento", 20)
        }

        # Obtener descripciones
        nivel_pert, desc_pert, _ = escala_pertinencia.get(pertinencia, ("N/A", "", 50))
        nivel_rel, desc_rel, _ = escala_relacionamiento.get(relacionamiento, ("N/A", "", 50))

        # Calcular contribuciones parciales
        contrib_pertinencia = score_pertinencia * 0.40
        contrib_relacionamiento = score_relacionamiento * 0.35
        contrib_alcance = score_alcance * 0.15
        contrib_tipo = score_tipo * 0.10

        # Construir componentes
        componentes = [
            {
                "nombre": "Pertinencia Operacional",
                "peso": "40%",
                "valor_input": f"{pertinencia}/5",
                "score": score_pertinencia,
                "contribucion_parcial": contrib_pertinencia,
                "nivel": nivel_pert,
                "descripcion": desc_pert,
                "formula": f"Pertinencia {pertinencia}/5 -> Score {score_pertinencia:.0f} -> Contrib: {score_pertinencia:.0f} x 0.40 = {contrib_pertinencia:.1f}"
            },
            {
                "nombre": "Mejora del Relacionamiento",
                "peso": "35%",
                "valor_input": f"{relacionamiento}/5",
                "score": score_relacionamiento,
                "contribucion_parcial": contrib_relacionamiento,
                "nivel": nivel_rel,
                "descripcion": desc_rel,
                "formula": f"Relacionamiento {relacionamiento}/5 -> Score {score_relacionamiento:.0f} -> Contrib: {score_relacionamiento:.0f} x 0.35 = {contrib_relacionamiento:.1f}"
            },
            {
                "nombre": "Alcance Territorial",
                "peso": "15%",
                "score": score_alcance,
                "contribucion_parcial": contrib_alcance,
                "en_corredor": en_corredor,
                "num_municipios": num_municipios,
                "descripcion": f"{'En corredor de transmision (+bonus)' if en_corredor else 'Fuera de corredor'}, {num_municipios} municipio(s)",
                "formula": f"Alcance {score_alcance:.0f} -> Contrib: {score_alcance:.0f} x 0.15 = {contrib_alcance:.1f}"
            },
            {
                "nombre": "Tipo de Stakeholders",
                "peso": "10%",
                "score": score_tipo,
                "contribucion_parcial": contrib_tipo,
                "stakeholders": stakeholders_lista or [],
                "descripcion": f"{len(stakeholders_lista or [])} tipo(s) de stakeholders involucrados",
                "formula": f"Tipo {score_tipo:.0f} -> Contrib: {score_tipo:.0f} x 0.10 = {contrib_tipo:.1f}"
            }
        ]

        # Interpretacion general
        if score_total >= 80:
            interpretacion = (
                f"El proyecto tiene ALTA relevancia estrategica para ENLAZA. "
                f"Con pertinencia {nivel_pert} y capacidad {nivel_rel} de mejorar "
                f"el relacionamiento comunitario, se recomienda priorizar."
            )
        elif score_total >= 60:
            interpretacion = (
                f"El proyecto tiene relevancia MEDIA para ENLAZA. "
                f"Contribuye al relacionamiento pero hay oportunidades de mejora."
            )
        else:
            interpretacion = (
                f"El proyecto tiene relevancia BAJA para ENLAZA. "
                f"Considerar si se alinea con objetivos estrategicos."
            )

        return {
            "titulo": "Stakeholders - Relacionamiento y Pertinencia Operacional",
            "peso": "25%",
            "peso_decimal": 0.25,
            "definicion": (
                "Evalua como el proyecto contribuye al relacionamiento con stakeholders "
                "y facilita las operaciones de ENLAZA. Considera pertinencia operacional, "
                "mejora del relacionamiento, alcance territorial y tipos de stakeholders."
            ),
            "score": score_total,
            "contribucion": contribucion,
            "max_contribucion": 25.0,
            "componentes": componentes,
            "formula_general": (
                "Score = (Pertinencia x 40%) + (Relacionamiento x 35%) + "
                "(Alcance x 15%) + (Tipo Stakeholders x 10%)"
            ),
            "calculo_detallado": (
                f"Score = ({score_pertinencia:.0f} x 0.40) + ({score_relacionamiento:.0f} x 0.35) + "
                f"({score_alcance:.0f} x 0.15) + ({score_tipo:.0f} x 0.10) = {score_total:.1f}"
            ),
            "calculo_contribucion": f"Contribucion = {score_total:.1f} x 0.25 = {contribucion:.1f} puntos",
            "interpretacion": interpretacion,
            "escala_pertinencia": [
                {"valor": 5, "nivel": "Muy Alta", "score": 100, "descripcion": "Critico para operaciones"},
                {"valor": 4, "nivel": "Alta", "score": 85, "descripcion": "Importante para operaciones"},
                {"valor": 3, "nivel": "Media", "score": 65, "descripcion": "Util para operaciones"},
                {"valor": 2, "nivel": "Baja", "score": 40, "descripcion": "Marginal para operaciones"},
                {"valor": 1, "nivel": "Nula", "score": 20, "descripcion": "Sin pertinencia"}
            ],
            "escala_relacionamiento": [
                {"valor": 5, "nivel": "Sustancial", "score": 100, "descripcion": "Transforma relacion"},
                {"valor": 4, "nivel": "Genera Confianza", "score": 85, "descripcion": "Mejora significativa"},
                {"valor": 3, "nivel": "Moderada", "score": 65, "descripcion": "Mejora positiva"},
                {"valor": 2, "nivel": "Limitada", "score": 40, "descripcion": "Mejora menor"},
                {"valor": 1, "nivel": "No Aporta", "score": 20, "descripcion": "Sin efecto"}
            ]
        }

    # =========================================================================
    # PROBABILIDAD DE APROBACION PDET (20%)
    # =========================================================================

    @staticmethod
    def explicar_probabilidad(
        municipio: str,
        departamento: str,
        es_pdet: bool,
        sector: str,
        puntaje_sectorial: float,
        score: float,
        contribucion: float
    ) -> Dict[str, Any]:
        """
        Genera explicacion detallada de Probabilidad de Aprobacion.

        Args:
            municipio: Nombre del municipio
            departamento: Nombre del departamento
            es_pdet: Si el municipio es PDET
            sector: Sector del proyecto
            puntaje_sectorial: Puntaje sectorial PDET (0-10)
            score: Score obtenido (0-100)
            contribucion: Contribucion al score final (0-20)

        Returns:
            Diccionario con explicacion completa
        """
        if es_pdet:
            estado_pdet = f"SI - {municipio} es uno de los 362 municipios PDET priorizados"
            explicacion_pdet = (
                "Los municipios PDET (Programas de Desarrollo con Enfoque Territorial) "
                "tienen prioridad en proyectos de Obras por Impuestos. Esto aumenta "
                "significativamente la probabilidad de aprobacion y acceso a recursos."
            )
            formula = f"Score = (Puntaje Sectorial / 10) x 100 = ({puntaje_sectorial}/10) x 100 = {score:.0f}"

            if puntaje_sectorial >= 8:
                nivel_sector = "MAXIMA"
                desc_sector = "Sector con maxima prioridad en territorios PDET"
            elif puntaje_sectorial >= 6:
                nivel_sector = "ALTA"
                desc_sector = "Sector prioritario segun lineamientos PDET"
            elif puntaje_sectorial >= 4:
                nivel_sector = "MEDIA"
                desc_sector = "Sector con prioridad moderada"
            else:
                nivel_sector = "BAJA"
                desc_sector = "Sector con baja prioridad en PDET"

        else:
            estado_pdet = f"NO - {municipio} no esta en la lista de 362 municipios PDET"
            explicacion_pdet = (
                "Al no ser municipio PDET, el proyecto NO es elegible para el mecanismo "
                "de Obras por Impuestos. Esto reduce significativamente la probabilidad "
                "de aprobacion y acceso a recursos tributarios."
            )
            formula = "Municipio NO-PDET -> Score = 0 (no elegible para OxI)"
            nivel_sector = "N/A"
            desc_sector = "No aplica - Municipio fuera de cobertura PDET"
            puntaje_sectorial = 0

        # Sectores de referencia
        sectores_pdet = {
            "Educacion": {"puntaje": 10, "descripcion": "Maxima prioridad"},
            "Salud": {"puntaje": 9, "descripcion": "Muy alta prioridad"},
            "Agua y Saneamiento": {"puntaje": 9, "descripcion": "Muy alta prioridad"},
            "Alcantarillado": {"puntaje": 9, "descripcion": "Muy alta prioridad"},
            "Energia": {"puntaje": 8, "descripcion": "Alta prioridad"},
            "Vivienda": {"puntaje": 7, "descripcion": "Prioridad media-alta"},
            "Infraestructura vial": {"puntaje": 7, "descripcion": "Prioridad media-alta"},
            "Infraestructura Rural": {"puntaje": 8, "descripcion": "Alta prioridad"},
            "Cultura y Deporte": {"puntaje": 6, "descripcion": "Prioridad media"},
            "Productivo": {"puntaje": 5, "descripcion": "Prioridad moderada"}
        }

        return {
            "titulo": "Probabilidad de Aprobacion PDET",
            "peso": "20%",
            "peso_decimal": 0.20,
            "definicion": (
                "Evalua la probabilidad de que el proyecto sea aprobado en el mecanismo "
                "de Obras por Impuestos (OxI). Se basa en si el municipio es PDET y "
                "el puntaje del sector de inversion segun la matriz oficial."
            ),
            "municipio": municipio,
            "departamento": departamento,
            "es_pdet": es_pdet,
            "estado_pdet": estado_pdet,
            "explicacion_pdet": explicacion_pdet,
            "sector": sector,
            "puntaje_sectorial": puntaje_sectorial,
            "nivel_sector": nivel_sector,
            "desc_sector": desc_sector,
            "score": score,
            "contribucion": contribucion,
            "max_contribucion": 20.0,
            "formula_aplicada": formula,
            "calculo_contribucion": f"Contribucion = {score:.1f} x 0.20 = {contribucion:.1f} puntos",
            "interpretacion": (
                f"Proyecto en {'municipio PDET' if es_pdet else 'municipio NO-PDET'}, "
                f"sector {sector} con puntaje {puntaje_sectorial}/10. "
                f"{'Alta probabilidad de aprobacion.' if es_pdet and puntaje_sectorial >= 6 else 'Probabilidad de aprobacion limitada.'}"
            ),
            "sectores_referencia": sectores_pdet,
            "nota_importante": (
                "Los 362 municipios PDET fueron priorizados por el Gobierno Nacional "
                "para la construccion de paz. Proyectos en estos municipios tienen "
                "acceso preferencial al mecanismo de Obras por Impuestos."
            ) if es_pdet else (
                "RECOMENDACION: Considerar reubicar el proyecto a un municipio PDET "
                "para aumentar probabilidad de aprobacion y acceso a beneficios tributarios."
            )
        }

    # =========================================================================
    # RIESGOS (15%)
    # =========================================================================

    @staticmethod
    def explicar_riesgos(
        riesgo_tecnico: tuple,
        riesgo_social: tuple,
        riesgo_financiero: tuple,
        riesgo_regulatorio: tuple,
        score_tecnico: float,
        score_social: float,
        score_financiero: float,
        score_regulatorio: float,
        score_total: float,
        contribucion: float
    ) -> Dict[str, Any]:
        """
        Genera explicacion detallada de Riesgos.

        Args:
            riesgo_tecnico: Tupla (probabilidad, impacto)
            riesgo_social: Tupla (probabilidad, impacto)
            riesgo_financiero: Tupla (probabilidad, impacto)
            riesgo_regulatorio: Tupla (probabilidad, impacto)
            score_tecnico: Score del riesgo tecnico (0-100)
            score_social: Score del riesgo social (0-100)
            score_financiero: Score del riesgo financiero (0-100)
            score_regulatorio: Score del riesgo regulatorio (0-100)
            score_total: Score total del criterio (0-100)
            contribucion: Contribucion al score final (0-15)

        Returns:
            Diccionario con explicacion completa
        """
        def interpretar_severidad(severidad: int) -> tuple:
            if severidad <= 5:
                return ("MUY BAJO", "verde", "Riesgo minimo, seguimiento estandar")
            elif severidad <= 10:
                return ("BAJO", "verde_claro", "Riesgo controlable, monitoreo regular")
            elif severidad <= 15:
                return ("MEDIO", "amarillo", "Riesgo moderado, plan de mitigacion requerido")
            elif severidad <= 20:
                return ("ALTO", "naranja", "Riesgo significativo, mitigacion prioritaria")
            else:
                return ("CRITICO", "rojo", "Riesgo critico, evaluar viabilidad")

        def calcular_score_riesgo(severidad: int) -> float:
            # Score inverso: mas riesgo = menos puntos
            return max(0, 100 - (severidad * 4))

        # Calcular severidades
        sev_tecnico = riesgo_tecnico[0] * riesgo_tecnico[1]
        sev_social = riesgo_social[0] * riesgo_social[1]
        sev_financiero = riesgo_financiero[0] * riesgo_financiero[1]
        sev_regulatorio = riesgo_regulatorio[0] * riesgo_regulatorio[1]

        # Construir detalle de cada riesgo
        riesgos = [
            {
                "tipo": "Tecnico",
                "descripcion": "Complejidad de ejecucion, requerimientos especializados, dependencias tecnologicas",
                "probabilidad": riesgo_tecnico[0],
                "impacto": riesgo_tecnico[1],
                "severidad": sev_tecnico,
                "score": score_tecnico,
                "nivel": interpretar_severidad(sev_tecnico)[0],
                "color": interpretar_severidad(sev_tecnico)[1],
                "mitigacion": interpretar_severidad(sev_tecnico)[2],
                "formula": f"Severidad = {riesgo_tecnico[0]} x {riesgo_tecnico[1]} = {sev_tecnico}; Score = 100 - ({sev_tecnico} x 4) = {score_tecnico:.0f}"
            },
            {
                "tipo": "Social",
                "descripcion": "Aceptacion comunitaria, conflictos potenciales, resistencia al proyecto",
                "probabilidad": riesgo_social[0],
                "impacto": riesgo_social[1],
                "severidad": sev_social,
                "score": score_social,
                "nivel": interpretar_severidad(sev_social)[0],
                "color": interpretar_severidad(sev_social)[1],
                "mitigacion": interpretar_severidad(sev_social)[2],
                "formula": f"Severidad = {riesgo_social[0]} x {riesgo_social[1]} = {sev_social}; Score = 100 - ({sev_social} x 4) = {score_social:.0f}"
            },
            {
                "tipo": "Financiero",
                "descripcion": "Estabilidad de financiamiento, sobrecostos potenciales, capacidad de ejecucion",
                "probabilidad": riesgo_financiero[0],
                "impacto": riesgo_financiero[1],
                "severidad": sev_financiero,
                "score": score_financiero,
                "nivel": interpretar_severidad(sev_financiero)[0],
                "color": interpretar_severidad(sev_financiero)[1],
                "mitigacion": interpretar_severidad(sev_financiero)[2],
                "formula": f"Severidad = {riesgo_financiero[0]} x {riesgo_financiero[1]} = {sev_financiero}; Score = 100 - ({sev_financiero} x 4) = {score_financiero:.0f}"
            },
            {
                "tipo": "Regulatorio",
                "descripcion": "Permisos requeridos, cambios normativos, complejidad legal",
                "probabilidad": riesgo_regulatorio[0],
                "impacto": riesgo_regulatorio[1],
                "severidad": sev_regulatorio,
                "score": score_regulatorio,
                "nivel": interpretar_severidad(sev_regulatorio)[0],
                "color": interpretar_severidad(sev_regulatorio)[1],
                "mitigacion": interpretar_severidad(sev_regulatorio)[2],
                "formula": f"Severidad = {riesgo_regulatorio[0]} x {riesgo_regulatorio[1]} = {sev_regulatorio}; Score = 100 - ({sev_regulatorio} x 4) = {score_regulatorio:.0f}"
            }
        ]

        # Identificar riesgos criticos
        riesgos_altos = [r for r in riesgos if r['severidad'] > 12]
        alertas = [
            f"ALERTA: Riesgo {r['tipo']} con severidad {r['severidad']}/25 - {r['mitigacion']}"
            for r in riesgos_altos
        ]

        # Interpretacion general
        if score_total >= 80:
            perfil = "BAJO"
            interpretacion = (
                "El proyecto presenta un perfil de riesgo FAVORABLE. "
                "Los riesgos identificados son controlables con seguimiento estandar."
            )
        elif score_total >= 60:
            perfil = "MEDIO"
            interpretacion = (
                "El proyecto presenta un perfil de riesgo MODERADO. "
                "Se requiere plan de mitigacion para los riesgos identificados."
            )
        elif score_total >= 40:
            perfil = "ALTO"
            interpretacion = (
                "El proyecto presenta un perfil de riesgo ALTO. "
                "Se requiere plan de mitigacion robusto y seguimiento intensivo."
            )
        else:
            perfil = "CRITICO"
            interpretacion = (
                "El proyecto presenta un perfil de riesgo CRITICO. "
                "Evaluar viabilidad antes de aprobar."
            )

        return {
            "titulo": "Analisis de Riesgos",
            "peso": "15%",
            "peso_decimal": 0.15,
            "definicion": (
                "Evalua los riesgos del proyecto en 4 dimensiones. "
                "IMPORTANTE: Un score ALTO significa BAJO riesgo (proyecto mas seguro). "
                "El score se calcula de forma inversa: mas riesgo = menos puntos."
            ),
            "riesgos": riesgos,
            "score": score_total,
            "contribucion": contribucion,
            "max_contribucion": 15.0,
            "perfil_riesgo": perfil,
            "formula_general": (
                "Severidad = Probabilidad x Impacto (escala 1-25)\n"
                "Score por riesgo = 100 - (Severidad x 4)\n"
                "Score Total = Promedio de los 4 scores"
            ),
            "calculo_detallado": (
                f"Score Total = ({score_tecnico:.0f} + {score_social:.0f} + "
                f"{score_financiero:.0f} + {score_regulatorio:.0f}) / 4 = {score_total:.1f}"
            ),
            "calculo_contribucion": f"Contribucion = {score_total:.1f} x 0.15 = {contribucion:.1f} puntos",
            "interpretacion": interpretacion,
            "alertas": alertas,
            "escala_severidad": [
                {"rango": "1-5", "nivel": "MUY BAJO", "descripcion": "Riesgo minimo"},
                {"rango": "6-10", "nivel": "BAJO", "descripcion": "Riesgo controlable"},
                {"rango": "11-15", "nivel": "MEDIO", "descripcion": "Requiere mitigacion"},
                {"rango": "16-20", "nivel": "ALTO", "descripcion": "Mitigacion prioritaria"},
                {"rango": "21-25", "nivel": "CRITICO", "descripcion": "Evaluar viabilidad"}
            ],
            "escala_probabilidad": [
                {"valor": 1, "descripcion": "Muy improbable (< 10%)"},
                {"valor": 2, "descripcion": "Poco probable (10-30%)"},
                {"valor": 3, "descripcion": "Posible (30-50%)"},
                {"valor": 4, "descripcion": "Probable (50-70%)"},
                {"valor": 5, "descripcion": "Muy probable (> 70%)"}
            ],
            "escala_impacto": [
                {"valor": 1, "descripcion": "Insignificante"},
                {"valor": 2, "descripcion": "Menor"},
                {"valor": 3, "descripcion": "Moderado"},
                {"valor": 4, "descripcion": "Mayor"},
                {"valor": 5, "descripcion": "Catastrofico"}
            ]
        }

    # =========================================================================
    # RESUMEN EJECUTIVO
    # =========================================================================

    @staticmethod
    def generar_resumen_metodologia() -> Dict[str, Any]:
        """
        Genera un resumen de la metodologia Arquitectura C.

        Returns:
            Diccionario con descripcion de la metodologia
        """
        return {
            "nombre": "Arquitectura C - Sistema de Priorizacion de Proyectos",
            "version": "1.0",
            "descripcion": (
                "Sistema de evaluacion multi-criterio para priorizar proyectos sociales "
                "basado en cuatro dimensiones clave: retorno social, stakeholders, "
                "probabilidad de aprobacion y gestion de riesgos."
            ),
            "formula_general": (
                "Score Total = (SROI x 40%) + (Stakeholders x 25%) + "
                "(Probabilidad x 20%) + (Riesgos x 15%)"
            ),
            "criterios": [
                {
                    "nombre": "SROI (Retorno Social)",
                    "peso": "40%",
                    "descripcion": "Mide cuanto valor social genera cada peso invertido"
                },
                {
                    "nombre": "Stakeholders",
                    "peso": "25%",
                    "descripcion": "Evalua relacionamiento y pertinencia operacional"
                },
                {
                    "nombre": "Probabilidad de Aprobacion",
                    "peso": "20%",
                    "descripcion": "Evalua elegibilidad PDET y sector de inversion"
                },
                {
                    "nombre": "Riesgos",
                    "peso": "15%",
                    "descripcion": "Analiza riesgos tecnicos, sociales, financieros y regulatorios"
                }
            ],
            "niveles_prioridad": [
                {"rango": "85-100", "nivel": "MUY ALTA", "recomendacion": "Aprobacion inmediata"},
                {"rango": "70-84", "nivel": "ALTA", "recomendacion": "Aprobacion recomendada"},
                {"rango": "50-69", "nivel": "MEDIA", "recomendacion": "Evaluacion detallada"},
                {"rango": "30-49", "nivel": "BAJA", "recomendacion": "Requiere mejoras"},
                {"rango": "0-29", "nivel": "RECHAZADO", "recomendacion": "No aprobar"}
            ],
            "nota": (
                "Este sistema fue disenado para ENLAZA GEB con el objetivo de "
                "priorizar proyectos de valor compartido que maximicen el impacto "
                "social mientras facilitan las operaciones de transmision de energia."
            )
        }
