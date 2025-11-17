"""
Modelos de dominio para proyectos sociales.
SRP: Cada modelo tiene una responsabilidad clara.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class AreaGeografica(Enum):
    """Áreas geográficas de intervención"""
    URBANA = "urbana"
    RURAL = "rural"
    PERIURBANA = "periurbana"
    NACIONAL = "nacional"


class EstadoProyecto(Enum):
    """Estados del ciclo de vida del proyecto"""
    PROPUESTA = "propuesta"
    EVALUACION = "evaluacion"
    APROBADO = "aprobado"
    EN_EJECUCION = "en_ejecucion"
    FINALIZADO = "finalizado"
    RECHAZADO = "rechazado"


@dataclass
class ProyectoSocial:
    """
    Modelo de proyecto social.
    ISP: Interface mínima con solo los campos necesarios.
    """
    id: str
    nombre: str
    organizacion: str
    descripcion: str
    beneficiarios_directos: int
    beneficiarios_indirectos: int
    duracion_meses: int
    presupuesto_total: float
    ods_vinculados: List[str]
    area_geografica: AreaGeografica
    poblacion_objetivo: str
    departamentos: List[str]
    municipios: List[str] = field(default_factory=list)
    estado: EstadoProyecto = EstadoProyecto.PROPUESTA

    # NUEVO: Sectores del proyecto (para matriz PDET/ZOMAC)
    sectores: List[str] = field(default_factory=list)
    # Ejemplo: ["Educación", "Salud", "Infraestructura Rural"]

    # Indicadores específicos
    indicadores_impacto: Dict[str, float] = field(default_factory=dict)

    # NUEVO: Puntajes PDET calculados automáticamente
    puntajes_pdet: Dict[str, int] = field(default_factory=dict)
    # Ejemplo: {"Educación": 6, "Salud": 3, "Infraestructura Rural": 9}

    # NUEVO: Indicador si tiene municipios PDET
    tiene_municipios_pdet: bool = False

    # NUEVO: Puntaje máximo sectorial (calculado)
    puntaje_sectorial_max: Optional[int] = None

    # NUEVO: Observaciones SROI (metodología, supuestos, fuentes) - Arquitectura C
    observaciones_sroi: str = ""
    # Max 1000 caracteres
    # Formato: Markdown simple permitido
    # Propósito: Documentar cálculo SROI, supuestos, limitaciones

    # NUEVO: Metadata SROI - Arquitectura C
    nivel_confianza_sroi: Optional[str] = None  # "Alta", "Media", "Baja"
    fecha_calculo_sroi: Optional[str] = None
    metodologia_sroi: Optional[str] = None  # "Estándar", "Simplificada", "Preliminar"

    # ========== NUEVOS: Criterio Stakeholders - Arquitectura C ==========

    # Pertinencia Operacional/Reputacional (1-5)
    pertinencia_operacional: Optional[int] = None
    # 5=Muy Alta, 4=Alta, 3=Media, 2=Baja, 1=Nula

    # Mejora del Relacionamiento (1-5)
    mejora_relacionamiento: Optional[int] = None
    # 5=Sustancial, 4=Confianza, 3=Moderada, 2=Limitada, 1=No aporta

    # Stakeholders involucrados (lista de strings)
    stakeholders_involucrados: List[str] = field(default_factory=list)
    # Opciones: 'autoridades_locales', 'lideres_comunitarios',
    #           'comunidades_indigenas', 'organizaciones_sociales',
    #           'sector_privado', 'academia', 'medios_comunicacion'

    # Corredor de transmisión (boolean)
    en_corredor_transmision: bool = False

    # Observaciones stakeholders (opcional)
    observaciones_stakeholders: str = ""
    # Max 1000 caracteres, para explicar contexto específico

    # ========== NUEVOS: Criterio Riesgos - Arquitectura C ==========

    # Riesgo Técnico/Operacional
    riesgo_tecnico_probabilidad: Optional[int] = None  # 1-5
    riesgo_tecnico_impacto: Optional[int] = None  # 1-5

    # Riesgo Social/Comunitario
    riesgo_social_probabilidad: Optional[int] = None  # 1-5
    riesgo_social_impacto: Optional[int] = None  # 1-5

    # Riesgo Financiero/Presupuestario
    riesgo_financiero_probabilidad: Optional[int] = None  # 1-5
    riesgo_financiero_impacto: Optional[int] = None  # 1-5

    # Riesgo Regulatorio/Legal
    riesgo_regulatorio_probabilidad: Optional[int] = None  # 1-5
    riesgo_regulatorio_impacto: Optional[int] = None  # 1-5

    # Duración estimada (meses)
    duracion_estimada_meses: Optional[int] = None

    # Observaciones riesgos (opcional)
    observaciones_riesgos: str = ""
    # Max 1000 caracteres

    # Metadata
    fecha_presentacion: str = ""
    contacto_organizacion: str = ""

    def __post_init__(self):
        """Validaciones básicas"""
        if self.beneficiarios_directos < 0:
            raise ValueError("Beneficiarios directos debe ser positivo")
        if self.duracion_meses <= 0:
            raise ValueError("Duración debe ser mayor a 0")
        if self.presupuesto_total <= 0:
            raise ValueError("Presupuesto debe ser mayor a 0")

    @property
    def beneficiarios_totales(self) -> int:
        """Total de beneficiarios (directos + indirectos)"""
        return self.beneficiarios_directos + self.beneficiarios_indirectos

    @property
    def presupuesto_por_beneficiario(self) -> float:
        """Costo promedio por beneficiario"""
        return self.presupuesto_total / self.beneficiarios_totales if self.beneficiarios_totales > 0 else 0

    @property
    def duracion_años(self) -> float:
        """Duración en años"""
        return self.duracion_meses / 12

    def validar_sroi(self) -> Dict[str, Any]:
        """
        Valida el valor SROI del proyecto según Arquitectura C.

        Rangos aprobados (15 Nov 2025):
        - < 1.0: RECHAZAR (destruye valor social)
        - 1.0-1.99: BAJA (retorno marginal)
        - 2.0-2.99: MEDIA (retorno aceptable)
        - ≥ 3.0: ALTA (retorno excelente)
        - > 7.0: VERIFICAR (requiere validación metodológica)

        Returns:
            Dict con:
            - 'valido': bool
            - 'mensaje': str
            - 'nivel': str (RECHAZAR, BAJA, MEDIA, ALTA, VERIFICAR)
            - 'requiere_observaciones': bool
        """
        sroi = self.indicadores_impacto.get('sroi', 0)

        if sroi < 1.0:
            return {
                'valido': False,
                'mensaje': 'RECHAZADO - SROI < 1.0 destruye valor social',
                'nivel': 'RECHAZAR',
                'requiere_observaciones': True
            }
        elif sroi > 7.0:
            return {
                'valido': True,
                'mensaje': 'ALERTA - SROI > 7.0 requiere verificación metodológica',
                'nivel': 'VERIFICAR',
                'requiere_observaciones': True
            }
        elif sroi > 5.0:
            return {
                'valido': True,
                'mensaje': 'SROI alto - Documentar metodología',
                'nivel': 'ALTA',
                'requiere_observaciones': True
            }
        elif sroi >= 3.0:
            return {
                'valido': True,
                'mensaje': 'SROI excelente',
                'nivel': 'ALTA',
                'requiere_observaciones': False
            }
        elif sroi >= 2.0:
            return {
                'valido': True,
                'mensaje': 'SROI aceptable',
                'nivel': 'MEDIA',
                'requiere_observaciones': False
            }
        else:  # 1.0 <= sroi < 2.0
            return {
                'valido': True,
                'mensaje': 'SROI marginal',
                'nivel': 'BAJA',
                'requiere_observaciones': False
            }

    def validar_riesgos(self) -> Dict[str, Any]:
        """
        Valida datos del criterio Riesgos

        Returns:
            Dict con 'valido', 'errores', 'advertencias', 'mensaje'
        """
        errores = []
        advertencias = []

        # Validar cada tipo de riesgo
        riesgos = [
            ('técnico', self.riesgo_tecnico_probabilidad, self.riesgo_tecnico_impacto),
            ('social', self.riesgo_social_probabilidad, self.riesgo_social_impacto),
            ('financiero', self.riesgo_financiero_probabilidad, self.riesgo_financiero_impacto),
            ('regulatorio', self.riesgo_regulatorio_probabilidad, self.riesgo_regulatorio_impacto)
        ]

        for nombre, prob, imp in riesgos:
            if prob is None or imp is None:
                errores.append(f"Riesgo {nombre}: probabilidad e impacto requeridos")
            else:
                if prob not in [1, 2, 3, 4, 5]:
                    errores.append(f"Riesgo {nombre}: probabilidad inválida ({prob})")
                if imp not in [1, 2, 3, 4, 5]:
                    errores.append(f"Riesgo {nombre}: impacto inválido ({imp})")

                # Advertencias para riesgos altos
                if prob and imp:
                    nivel = prob * imp
                    if nivel >= 16:
                        advertencias.append(
                            f"⚠️  Riesgo {nombre} ALTO (nivel {nivel}): "
                            f"Considerar plan de mitigación"
                        )

        return {
            'valido': len(errores) == 0,
            'errores': errores,
            'advertencias': advertencias,
            'mensaje': errores[0] if errores else "Validación exitosa"
        }

    def validar_stakeholders(self) -> Dict[str, Any]:
        """
        Valida datos del criterio Stakeholders

        Returns:
            Dict con 'valido', 'mensaje', 'errores', 'advertencias'
        """
        errores = []
        advertencias = []

        # Validar pertinencia operacional
        if self.pertinencia_operacional is None:
            errores.append("Pertinencia operacional no definida")
        elif self.pertinencia_operacional not in [1, 2, 3, 4, 5]:
            errores.append(f"Pertinencia operacional inválida: {self.pertinencia_operacional}")

        # Validar mejora relacionamiento
        if self.mejora_relacionamiento is None:
            errores.append("Mejora relacionamiento no definida")
        elif self.mejora_relacionamiento not in [1, 2, 3, 4, 5]:
            errores.append(f"Mejora relacionamiento inválida: {self.mejora_relacionamiento}")

        # Advertencias
        if self.pertinencia_operacional == 5 and not self.observaciones_stakeholders:
            advertencias.append(
                "Pertinencia MUY ALTA: Recomendar documentar contexto operacional"
            )

        if self.mejora_relacionamiento == 5 and not self.observaciones_stakeholders:
            advertencias.append(
                "Mejora SUSTANCIAL: Recomendar documentar estrategia de relacionamiento"
            )

        if not self.stakeholders_involucrados:
            advertencias.append(
                "Sin stakeholders especificados: Considerar agregar para evaluación completa"
            )

        return {
            'valido': len(errores) == 0,
            'errores': errores,
            'advertencias': advertencias,
            'mensaje': errores[0] if errores else "Validación exitosa"
        }
