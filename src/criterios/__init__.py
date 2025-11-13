"""Criterios de evaluación de proyectos"""
from criterios.base import CriterioEvaluacion
from criterios.impacto_social import ImpactoSocialCriterio
from criterios.sostenibilidad import SostenibilidadFinancieraCriterio
from criterios.alineacion_ods import AlineacionODSCriterio
from criterios.capacidad_organizacional import CapacidadOrganizacionalCriterio

__all__ = [
    'CriterioEvaluacion',
    'ImpactoSocialCriterio',
    'SostenibilidadFinancieraCriterio',
    'AlineacionODSCriterio',
    'CapacidadOrganizacionalCriterio'
]
