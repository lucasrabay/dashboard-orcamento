"""components/plotly_theme.py — Template Plotly customizado."""

import plotly.graph_objects as go
import plotly.io as pio

# Paleta sequencial monocromática (tons de cinza-azulado)
PALETA_SEQUENCIAL = [
    "#0F172A",  # Slate 900
    "#1E293B",  # Slate 800
    "#334155",  # Slate 700
    "#475569",  # Slate 600
    "#64748B",  # Slate 500
    "#94A3B8",  # Slate 400
    "#CBD5E1",  # Slate 300
]

# Paleta categórica (para gráficos com múltiplas séries)
PALETA_CATEGORICA = [
    "#059669",  # Verde accent
    "#0F172A",  # Slate 900
    "#475569",  # Slate 600
    "#94A3B8",  # Slate 400
    "#D97706",  # Amber
    "#0891B2",  # Cyan
    "#7C3AED",  # Violet
    "#DC2626",  # Red
    "#65A30D",  # Lime
    "#DB2777",  # Pink
]

ACCENT = "#059669"


def get_theme() -> go.layout.Template:
    """Retorna o template Plotly customizado."""
    return go.layout.Template(
        layout=dict(
            font=dict(
                family='-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif',
                size=13,
                color="#0F172A",
            ),
            title=dict(
                font=dict(size=15, color="#0F172A"),
                x=0.0,
                xanchor="left",
                pad=dict(b=12),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=PALETA_CATEGORICA,
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor="#E2E8F0",
                linewidth=1,
                tickfont=dict(size=12, color="#64748B"),
                title=dict(font=dict(size=12, color="#94A3B8")),
                ticks="outside",
                tickcolor="#E2E8F0",
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#F1F5F9",
                gridwidth=1,
                showline=False,
                tickfont=dict(size=12, color="#64748B"),
                title=dict(font=dict(size=12, color="#94A3B8")),
            ),
            legend=dict(
                font=dict(size=12, color="#475569"),
                bgcolor="rgba(255,255,255,0)",
                bordercolor="#E2E8F0",
                borderwidth=0,
            ),
            margin=dict(l=10, r=10, t=40, b=10),
            hoverlabel=dict(
                bgcolor="#0F172A",
                bordercolor="#0F172A",
                font=dict(size=12, color="#FFFFFF"),
            ),
        )
    )


def register_theme():
    """Registra o template e o define como padrão."""
    pio.templates["custom"] = get_theme()
    pio.templates.default = "custom"
