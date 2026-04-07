"""components/ui.py — Helpers de UI customizados."""

import streamlit as st


# --- Ícones SVG (Lucide-style) ---
# Cada ícone é uma string SVG já configurada com stroke="currentColor"
ICONS = {
    "bar_chart": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
    "search": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "sliders": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>',
    "trending_up": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "info": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    "sparkles": '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M5.6 18.4l12.8-12.8"/></svg>',
    "dollar": '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
}


def icon(name: str, color: str = "#0F172A", size: int = 20) -> str:
    """Retorna o SVG de um ícone Lucide com cor e tamanho customizados."""
    svg = ICONS.get(name, "")
    if not svg:
        return ""
    svg = svg.replace('width="20"', f'width="{size}"').replace(
        'width="16"', f'width="{size}"'
    )
    svg = svg.replace('height="20"', f'height="{size}"').replace(
        'height="16"', f'height="{size}"'
    )
    return f'<span style="color: {color}; display: inline-flex; vertical-align: middle;">{svg}</span>'


def page_header(icon_name: str, title: str, subtitle: str = ""):
    """Renderiza um header de página padronizado com ícone SVG, título e subtítulo."""
    icon_html = icon(icon_name, color="#059669", size=28)
    html = f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px;">
        {icon_html}
        <h1 style="margin: 0; font-size: 28px; font-weight: 700; color: #0F172A; letter-spacing: -0.02em;">{title}</h1>
    </div>
    """
    if subtitle:
        html += f'<p style="color: #64748B; font-size: 15px; margin: 0 0 24px 0;">{subtitle}</p>'
    else:
        html += '<div style="margin-bottom: 24px;"></div>'
    st.markdown(html, unsafe_allow_html=True)


def metric_card(
    label: str,
    value: str,
    delta: str = "",
    delta_positive: bool = True,
    help_text: str = "",
):
    """Renderiza um card de KPI customizado mais profissional que st.metric."""
    delta_color = "#059669" if delta_positive else "#DC2626"
    delta_html = ""
    if delta:
        delta_html = f'<div style="font-size: 13px; color: {delta_color}; font-weight: 500; margin-top: 4px;">{delta}</div>'

    help_html = ""
    if help_text:
        help_html = f'<div style="font-size: 12px; color: #94A3B8; margin-top: 8px;">{help_text}</div>'

    html = (
        '<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:8px;padding:20px;height:100%;">'
        f'<div style="font-size:11px;color:#94A3B8;text-transform:uppercase;letter-spacing:0.05em;font-weight:600;margin-bottom:8px;">{label}</div>'
        f'<div style="font-size:26px;color:#0F172A;font-weight:700;line-height:1.2;">{value}</div>'
        f"{delta_html}"
        f"{help_html}"
        "</div>"
    )
    st.html(html)


def insight_box(title: str, content: str):
    """Renderiza uma caixa de insight (texto dinâmico do Gemini) com visual refinado."""
    sparkles = icon("sparkles", color="#059669", size=16)
    html = f"""
    <div style="
        background: #F0FDF4;
        border-left: 3px solid #059669;
        border-radius: 6px;
        padding: 16px 20px;
        margin: 16px 0;
    ">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            {sparkles}
            <span style="font-size: 12px; font-weight: 600; color: #047857; text-transform: uppercase; letter-spacing: 0.05em;">{title}</span>
        </div>
        <div style="color: #1E293B; font-size: 14px; line-height: 1.6;">{content}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = ""):
    """Header de seção dentro de uma página (menor que page_header)."""
    html = f'<h3 style="font-size: 18px; font-weight: 600; color: #0F172A; margin: 24px 0 4px 0;">{title}</h3>'
    if subtitle:
        html += f'<p style="font-size: 13px; color: #64748B; margin: 0 0 16px 0;">{subtitle}</p>'
    else:
        html += '<div style="margin-bottom: 16px;"></div>'
    st.markdown(html, unsafe_allow_html=True)


def footer():
    """Footer global com créditos e fonte de dados."""
    html = """
    <div style="
        margin-top: 64px;
        padding-top: 24px;
        border-top: 1px solid #E2E8F0;
        color: #94A3B8;
        font-size: 12px;
        text-align: center;
    ">
        Dados: <a href="https://portaldatransparencia.gov.br" target="_blank" style="color: #64748B; text-decoration: none;">Portal da Transparência do Governo Federal</a>
        &middot; UFPB &middot; Visualização de Dados 2025
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
