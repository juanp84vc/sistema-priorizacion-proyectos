"""
Estilos CSS adicionales para UI ejecutiva.
SRP: Solo gestiona estilos y temas.
"""
import streamlit as st


class EstilosUI:
    """Gestiona estilos CSS para la interfaz ejecutiva."""

    # Colores corporativos GEB
    COLORES = {
        'primario': '#0ea5e9',        # Azul corporativo
        'primario_oscuro': '#0284c7',
        'secundario': '#10b981',      # Verde sostenibilidad
        'secundario_oscuro': '#059669',
        'acento': '#8b5cf6',          # Púrpura innovación
        'exito': '#22c55e',
        'advertencia': '#f59e0b',
        'error': '#ef4444',
        'fondo_oscuro': '#0f172a',
        'fondo_medio': '#1e293b',
        'fondo_claro': '#334155',
        'texto_primario': '#f8fafc',
        'texto_secundario': '#cbd5e1',
        'texto_muted': '#94a3b8',
        'borde': 'rgba(255, 255, 255, 0.1)',
    }

    @staticmethod
    def aplicar_estilos_ejecutivos():
        """Aplica estilos CSS ejecutivos adicionales."""
        st.markdown("""
        <style>
        /* Header Ejecutivo con gradiente */
        .header-ejecutivo {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
            border-bottom: 2px solid rgba(14, 165, 233, 0.3);
            padding: 1.5rem 2rem;
            margin: -1rem -1rem 2rem -1rem;
            border-radius: 0 0 1rem 1rem;
        }

        .header-titulo {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #0ea5e9 0%, #10b981 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            letter-spacing: -0.02em;
        }

        .header-subtitulo {
            color: #94a3b8;
            font-size: 1rem;
            margin-top: 0.5rem;
        }

        .header-fecha {
            color: #64748b;
            font-size: 0.85rem;
            text-align: right;
        }

        /* Tarjeta KPI Ejecutiva */
        .kpi-card {
            background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid rgba(14, 165, 233, 0.2);
            border-radius: 1rem;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #0ea5e9, #10b981);
        }

        .kpi-card:hover {
            transform: translateY(-4px);
            border-color: rgba(14, 165, 233, 0.4);
            box-shadow: 0 10px 30px rgba(14, 165, 233, 0.15);
        }

        .kpi-valor {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #0ea5e9 0%, #10b981 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0.5rem 0;
        }

        .kpi-etiqueta {
            color: #94a3b8;
            font-size: 0.85rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .kpi-delta {
            font-size: 0.9rem;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            display: inline-block;
            margin-top: 0.5rem;
        }

        .kpi-delta.positivo {
            background: rgba(34, 197, 94, 0.15);
            color: #22c55e;
        }

        .kpi-delta.negativo {
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
        }

        /* Tabla Ranking Ejecutiva */
        .ranking-container {
            background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            padding: 1.5rem;
            margin: 1rem 0;
        }

        .ranking-titulo {
            font-size: 1.25rem;
            font-weight: 600;
            color: #f8fafc;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .ranking-item {
            display: flex;
            align-items: center;
            padding: 1rem;
            margin: 0.5rem 0;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 0.75rem;
            border-left: 4px solid transparent;
            transition: all 0.3s ease;
        }

        .ranking-item:hover {
            background: rgba(255, 255, 255, 0.06);
            transform: translateX(4px);
        }

        .ranking-item.top-1 { border-left-color: #fbbf24; }
        .ranking-item.top-2 { border-left-color: #94a3b8; }
        .ranking-item.top-3 { border-left-color: #cd7c32; }

        .ranking-posicion {
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            margin-right: 1rem;
        }

        .ranking-posicion.pos-1 {
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
            color: #0f172a;
        }

        .ranking-posicion.pos-2 {
            background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%);
            color: #0f172a;
        }

        .ranking-posicion.pos-3 {
            background: linear-gradient(135deg, #cd7c32 0%, #a16207 100%);
            color: #0f172a;
        }

        .ranking-posicion.pos-other {
            background: rgba(255, 255, 255, 0.1);
            color: #94a3b8;
        }

        .ranking-nombre {
            flex: 1;
            color: #f8fafc;
            font-weight: 500;
        }

        .ranking-score {
            font-weight: 700;
            font-size: 1.1rem;
            padding: 0.25rem 0.75rem;
            border-radius: 0.5rem;
        }

        .ranking-score.alto { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
        .ranking-score.medio { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
        .ranking-score.bajo { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

        /* Sección con título */
        .seccion-ejecutiva {
            margin: 2rem 0;
            padding: 1.5rem;
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.5) 0%, rgba(15, 23, 42, 0.5) 100%);
            border-radius: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .seccion-titulo {
            font-size: 1.5rem;
            font-weight: 600;
            color: #f8fafc;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid rgba(14, 165, 233, 0.3);
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        /* Botones ejecutivos */
        .btn-ejecutivo {
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-ejecutivo:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(14, 165, 233, 0.3);
        }

        .btn-ejecutivo.secundario {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        .btn-ejecutivo.excel {
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
        }

        .btn-ejecutivo.ppt {
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }

        /* Badge de estado */
        .badge-estado {
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge-estado.prioritario {
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(16, 185, 129, 0.2) 100%);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }

        .badge-estado.recomendado {
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%);
            color: #0ea5e9;
            border: 1px solid rgba(14, 165, 233, 0.3);
        }

        .badge-estado.revisar {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(234, 179, 8, 0.2) 100%);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .badge-estado.diferir {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        /* Sidebar ejecutivo mejorado */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0 !important;
        }

        /* Logo container en sidebar */
        .sidebar-logo-container {
            text-align: center;
            padding: 1.5rem 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 1rem;
        }

        .sidebar-logo {
            width: 80px;
            height: auto;
            margin-bottom: 0.5rem;
        }

        .sidebar-titulo {
            font-size: 1.1rem;
            font-weight: 700;
            background: linear-gradient(135deg, #0ea5e9 0%, #10b981 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }

        .sidebar-subtitulo {
            color: #64748b;
            font-size: 0.75rem;
            margin-top: 0.25rem;
        }

        /* Navegación mejorada */
        .nav-item {
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0.5rem;
            border-radius: 0.5rem;
            color: #94a3b8;
            text-decoration: none;
            transition: all 0.2s ease;
            cursor: pointer;
            border-left: 3px solid transparent;
        }

        .nav-item:hover {
            background: rgba(14, 165, 233, 0.1);
            color: #f8fafc;
            border-left-color: #0ea5e9;
        }

        .nav-item.active {
            background: linear-gradient(90deg, rgba(14, 165, 233, 0.15) 0%, transparent 100%);
            color: #0ea5e9;
            border-left-color: #0ea5e9;
        }

        .nav-icon {
            width: 1.5rem;
            margin-right: 0.75rem;
            text-align: center;
        }

        /* Footer ejecutivo */
        .footer-ejecutivo {
            text-align: center;
            padding: 2rem 0;
            margin-top: 3rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .footer-titulo {
            font-size: 1rem;
            font-weight: 600;
            background: linear-gradient(135deg, #0ea5e9 0%, #10b981 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        .footer-subtitulo {
            color: #64748b;
            font-size: 0.8rem;
        }

        /* Animaciones sutiles */
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .animate-slide-up {
            animation: slideUp 0.4s ease-out forwards;
        }

        /* Mejoras para tablas de datos */
        .stDataFrame {
            border-radius: 0.75rem !important;
            overflow: hidden !important;
        }

        .stDataFrame > div {
            background: #1e293b !important;
        }

        /* Expander ejecutivo */
        .streamlit-expanderHeader {
            background: rgba(30, 41, 59, 0.5) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 0.5rem !important;
        }

        .streamlit-expanderHeader:hover {
            background: rgba(30, 41, 59, 0.8) !important;
            border-color: rgba(14, 165, 233, 0.3) !important;
        }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def css_kpi_card(valor: str, etiqueta: str, delta: str = None, delta_tipo: str = "positivo") -> str:
        """Genera HTML para una tarjeta KPI."""
        delta_html = ""
        if delta:
            delta_html = f'<div class="kpi-delta {delta_tipo}">{delta}</div>'

        return f"""
        <div class="kpi-card">
            <div class="kpi-etiqueta">{etiqueta}</div>
            <div class="kpi-valor">{valor}</div>
            {delta_html}
        </div>
        """

    @staticmethod
    def css_ranking_item(posicion: int, nombre: str, score: float, max_chars: int = 40) -> str:
        """Genera HTML para un item de ranking."""
        pos_class = f"pos-{posicion}" if posicion <= 3 else "pos-other"
        top_class = f"top-{posicion}" if posicion <= 3 else ""

        # Determinar clase de score
        if score >= 70:
            score_class = "alto"
        elif score >= 50:
            score_class = "medio"
        else:
            score_class = "bajo"

        nombre_truncado = nombre[:max_chars] + "..." if len(nombre) > max_chars else nombre

        return f"""
        <div class="ranking-item {top_class}">
            <div class="ranking-posicion {pos_class}">{posicion}</div>
            <div class="ranking-nombre">{nombre_truncado}</div>
            <div class="ranking-score {score_class}">{score:.1f}</div>
        </div>
        """

    @staticmethod
    def css_badge_estado(recomendacion: str) -> str:
        """Genera badge según recomendación."""
        recomendacion_lower = recomendacion.lower()

        if "priorit" in recomendacion_lower:
            clase = "prioritario"
            texto = "PRIORITARIO"
        elif "recomend" in recomendacion_lower:
            clase = "recomendado"
            texto = "RECOMENDADO"
        elif "revis" in recomendacion_lower:
            clase = "revisar"
            texto = "REVISAR"
        else:
            clase = "diferir"
            texto = "DIFERIR"

        return f'<span class="badge-estado {clase}">{texto}</span>'
