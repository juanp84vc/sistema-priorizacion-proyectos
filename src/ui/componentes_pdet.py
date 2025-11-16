"""
Componentes de UI para integración PDET/ZOMAC
Selector de sectores con puntajes en tiempo real

Proporciona componentes visuales interactivos para:
- Selección de sectores con visualización de prioridades PDET
- Indicadores de municipios PDET/ZOMAC
- Estimación de probabilidad de aprobación en tiempo real
"""

import streamlit as st
from typing import List, Dict, Optional, Tuple
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.matriz_pdet_repository import MatrizPDETRepository


class SelectorSectoresPDET:
    """
    Componente para seleccionar sectores con visualización de puntajes PDET.

    Renderiza una interfaz interactiva que muestra:
    - Sectores ordenados por prioridad PDET
    - Puntajes visuales con estrellas (⭐)
    - Etiquetas de recomendación (💡 MÁXIMA PRIORIDAD)
    - Estimación de probabilidad de aprobación en tiempo real
    """

    # Lista oficial de sectores (10 sectores Obras por Impuestos)
    SECTORES_DISPONIBLES = [
        "Educación",
        "Salud",
        "Alcantarillado",
        "Vía",
        "Energía",
        "Banda Ancha",
        "Riesgo Ambiental",
        "Infraestructura Rural",
        "Cultura",
        "Deporte"
    ]

    def __init__(self, db_path: str = "data/proyectos.db"):
        """
        Inicializa el selector de sectores.

        Args:
            db_path: Ruta a la base de datos con matriz PDET
        """
        try:
            self.repo = MatrizPDETRepository(db_path)
        except Exception as e:
            st.error(f"Error al cargar matriz PDET: {e}")
            self.repo = None

    def render(
        self,
        departamento: str,
        municipio: str,
        key: str = "selector_sectores"
    ) -> Tuple[List[str], Dict[str, int], bool]:
        """
        Renderiza selector de sectores con puntajes PDET.

        Args:
            departamento: Departamento del proyecto
            municipio: Municipio del proyecto
            key: Key único para el componente Streamlit

        Returns:
            Tuple de (sectores_seleccionados, puntajes_pdet, es_pdet)
        """

        if not self.repo:
            return self._render_error()

        # Verificar si es municipio PDET
        es_pdet = self.repo.es_municipio_pdet(departamento, municipio)

        if not es_pdet:
            return self._render_no_pdet(municipio)

        # Obtener registro PDET del municipio
        registro = self.repo.get_municipio(departamento, municipio)

        if not registro:
            return self._render_no_pdet(municipio)

        # Renderizar selector para municipio PDET
        return self._render_pdet(registro, key)

    def _render_error(self) -> Tuple[List[str], Dict[str, int], bool]:
        """Renderiza mensaje de error"""
        st.error("⚠️  No se pudo cargar la matriz PDET. Contacte al administrador.")

        sectores = st.multiselect(
            "Sectores del proyecto:",
            options=self.SECTORES_DISPONIBLES
        )

        return sectores, {}, False

    def _render_no_pdet(
        self,
        municipio: str
    ) -> Tuple[List[str], Dict[str, int], bool]:
        """Renderiza mensaje para municipio NO-PDET"""

        st.markdown("---")
        st.markdown("### 🎯 Sectores del Proyecto")

        st.info(
            f"ℹ️  **{municipio}** no es municipio PDET/ZOMAC\n\n"
            "Este municipio **no es elegible** para el mecanismo "
            "**Obras por Impuestos**.\n\n"
            "Puede continuar con el proyecto usando otras fuentes "
            "de financiamiento."
        )

        st.warning(
            "**Score Probabilidad Aprobación (Obras por Impuestos):** 0/100"
        )

        # Permitir selección de sectores pero sin puntajes
        st.markdown("#### Sectores del proyecto (opcional):")
        sectores = st.multiselect(
            "Seleccione sector(es):",
            options=self.SECTORES_DISPONIBLES,
            help="Para contexto y clasificación del proyecto"
        )

        return sectores, {}, False

    def _render_pdet(
        self,
        registro,
        key: str
    ) -> Tuple[List[str], Dict[str, int], bool]:
        """Renderiza selector para municipio PDET con puntajes"""

        st.markdown("---")
        st.markdown("### 🎯 Sectores del Proyecto")

        # Indicador PDET
        st.success(
            f"✅ **{registro.municipio} ({registro.departamento})** "
            f"es municipio PDET/ZOMAC\n\n"
            f"Elegible para mecanismo **Obras por Impuestos**"
        )

        # Obtener sectores ordenados por prioridad
        sectores_ordenados = registro.get_sectores_ordenados()

        # Crear opciones con puntajes visibles
        opciones_con_puntaje = []
        puntajes_map = {}

        for sector, puntaje in sectores_ordenados:
            estrellas = "⭐" * puntaje

            # Etiqueta de recomendación
            if puntaje >= 9:
                tag = " 💡 MÁXIMA PRIORIDAD"
                opciones_con_puntaje.append(
                    f"{sector} - {puntaje}/10 {estrellas}{tag}"
                )
            elif puntaje >= 7:
                tag = " 💡 ALTA PRIORIDAD"
                opciones_con_puntaje.append(
                    f"{sector} - {puntaje}/10 {estrellas}{tag}"
                )
            elif puntaje >= 5:
                opciones_con_puntaje.append(
                    f"{sector} - {puntaje}/10 {estrellas}"
                )
            else:
                opciones_con_puntaje.append(
                    f"{sector} - {puntaje}/10 {estrellas}"
                )

            puntajes_map[sector] = puntaje

        # Selector multiselect
        st.markdown("#### Seleccione sector(es) principal(es):")

        selecciones_con_formato = st.multiselect(
            "Sectores:",
            options=opciones_con_puntaje,
            key=key,
            help="Seleccione los sectores principales del proyecto. "
                 "Sectores con mayor puntaje tienen mayor probabilidad "
                 "de aprobación en Obras por Impuestos.\n\n"
                 "💡 = Sectores recomendados (alta prioridad)\n"
                 "⭐ = Nivel de prioridad (1-10)"
        )

        # Extraer nombres de sectores sin formateo
        sectores_seleccionados = []
        puntajes_seleccionados = {}

        for sel in selecciones_con_formato:
            # Extraer nombre del sector (antes del " - ")
            nombre_sector = sel.split(" - ")[0]
            sectores_seleccionados.append(nombre_sector)
            puntajes_seleccionados[nombre_sector] = puntajes_map[nombre_sector]

        # Mostrar estimación si hay sectores seleccionados
        if sectores_seleccionados:
            self._render_estimacion(
                sectores_seleccionados,
                puntajes_seleccionados
            )

        return sectores_seleccionados, puntajes_seleccionados, True

    def _render_estimacion(
        self,
        sectores: List[str],
        puntajes: Dict[str, int]
    ):
        """Renderiza panel de estimación de probabilidad"""

        st.markdown("---")
        st.markdown("### 📊 Estimación Probabilidad Aprobación")

        # Calcular puntaje máximo
        puntaje_max = max(puntajes.values()) if puntajes else 0
        score = (puntaje_max / 10) * 100

        # Determinar nivel
        if score >= 80:
            nivel = "ALTA"
            emoji = "🟢"
            color = "success"
        elif score >= 60:
            nivel = "MEDIA"
            emoji = "🟡"
            color = "warning"
        else:
            nivel = "BAJA"
            emoji = "🔴"
            color = "error"

        # Mostrar score
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Score Estimado",
                f"{score:.0f}/100",
                delta=None,
                help="Score basado en el sector de mayor prioridad seleccionado"
            )

        with col2:
            st.metric(
                "Probabilidad",
                f"{nivel} {emoji}",
                delta=None,
                help="Nivel de probabilidad de aprobación en Obras por Impuestos"
            )

        # Detalles
        st.markdown("**Sectores seleccionados:**")

        # Ordenar por puntaje descendente para mostrar
        sectores_ordenados = sorted(
            puntajes.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for sector, puntaje in sectores_ordenados:
            estrellas = "⭐" * puntaje
            st.markdown(f"• **{sector}:** {puntaje}/10 {estrellas}")

        st.markdown(f"**Puntaje máximo:** {puntaje_max}/10")

        # Recomendación
        if puntaje_max >= 9:
            st.success(
                "💡 **Excelente:** Ha seleccionado sectores de máxima "
                "prioridad en Obras por Impuestos. "
                "Su proyecto tiene **alta probabilidad de aprobación**."
            )
        elif puntaje_max >= 7:
            st.info(
                "💡 **Bien:** Ha seleccionado sectores de alta prioridad. "
                "Su proyecto tiene **buena probabilidad de aprobación**."
            )
        elif puntaje_max >= 5:
            st.warning(
                "⚠️  **Advertencia:** Los sectores seleccionados tienen "
                "prioridad media. Considere incluir sectores de mayor "
                "prioridad si es posible."
            )
        else:
            st.error(
                "⚠️  **Atención:** Los sectores seleccionados tienen "
                "**baja prioridad** en este municipio. "
                "Recomendamos revisar sectores con mayor puntaje."
            )


def render_indicador_pdet(departamento: str, municipio: str, db_path: str = "data/proyectos.db"):
    """
    Renderiza indicador simple de si municipio es PDET/ZOMAC.

    Args:
        departamento: Departamento del municipio
        municipio: Nombre del municipio
        db_path: Ruta a la base de datos con matriz PDET
    """
    try:
        repo = MatrizPDETRepository(db_path)
        es_pdet = repo.es_municipio_pdet(departamento, municipio)

        if es_pdet:
            st.success(
                f"✅ **{municipio}** es municipio PDET/ZOMAC "
                f"(elegible para Obras por Impuestos)"
            )
        else:
            st.info(
                f"ℹ️  **{municipio}** no es municipio PDET/ZOMAC "
                f"(no elegible para Obras por Impuestos)"
            )
    except Exception as e:
        st.warning(f"⚠️  No se pudo verificar estado PDET: {e}")
