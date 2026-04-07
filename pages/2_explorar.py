"""
Página: Explorar o Orçamento.
Drill-down hierárquico via sunburst, evolução temporal e tabela detalhada.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from components.gemini_insights import exibir_insight, montar_contexto_comparativo
from components.ui import page_header, section_header

# ---------------------------------------------------------------------------
# Guard
# ---------------------------------------------------------------------------
df_filtrado: pd.DataFrame | None = st.session_state.get("df_filtrado")
df_completo: pd.DataFrame | None = st.session_state.get("df_completo")
ano: int | None = st.session_state.get("ano_selecionado")
metrica: str | None = st.session_state.get("metrica_selecionada")

if df_filtrado is None or df_completo is None or ano is None or metrica is None:
    st.warning(
        "Dados não inicializados. Volte ao início do app para carregar o dataset."
    )
    st.stop()

COLUNAS_VALOR = [
    "Valor Empenhado (R$)",
    "Valor Liquidado (R$)",
    "Valor Pago (R$)",
]

# ---------------------------------------------------------------------------
# 1. Título
# ---------------------------------------------------------------------------
page_header(
    icon_name="search",
    title="Explorar",
    subtitle="Navegue pelo orçamento em profundidade e compare áreas ao longo do tempo",
)

# ---------------------------------------------------------------------------
# 2. Sunburst — composição hierárquica
# ---------------------------------------------------------------------------
section_header(
    title="Drill-down hierárquico",
    subtitle=f"Composição do orçamento de {ano}",
)
df_sun = (
    df_filtrado[df_filtrado[metrica] > 0]
    .groupby(["Nome Função", "Nome Subfunção"], as_index=False)[metrica]
    .sum()
)

if df_sun.empty:
    st.info("Sem dados positivos para exibir no sunburst.")
else:
    fig_sun = px.sunburst(
        df_sun,
        path=["Nome Função", "Nome Subfunção"],
        values=metrica,
        color="Nome Função",
    )
    fig_sun.update_traces(
        hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<extra></extra>",
    )
    fig_sun.update_layout(height=550, margin=dict(t=50, l=10, r=10, b=10))
    st.plotly_chart(fig_sun, use_container_width=True)

# ---------------------------------------------------------------------------
# 3. Evolução temporal — line chart (usa df_completo, TODOS os anos)
# ---------------------------------------------------------------------------
section_header(
    title="Evolução temporal",
    subtitle="Compare a trajetória de gastos por área ao longo dos anos",
)

# Default: top 5 funções com maior valor pago no último ano disponível
ultimo_ano = int(df_completo["Ano"].max())
top5_funcoes = (
    df_completo[df_completo["Ano"] == ultimo_ano]
    .groupby("Nome Função", as_index=False)[metrica]
    .sum()
    .nlargest(5, metrica)["Nome Função"]
    .tolist()
)

todas_funcoes = sorted(df_completo["Nome Função"].dropna().unique().tolist())
funcoes_comparar = st.multiselect(
    "Selecione as áreas para comparar",
    options=todas_funcoes,
    default=top5_funcoes,
)

if not funcoes_comparar:
    st.warning("Selecione ao menos uma área para visualizar a evolução.")
else:
    df_evo = (
        df_completo[df_completo["Nome Função"].isin(funcoes_comparar)]
        .groupby(["Ano", "Nome Função"], as_index=False)[metrica]
        .sum()
    )
    fig_line = px.line(
        df_evo,
        x="Ano",
        y=metrica,
        color="Nome Função",
        markers=True,
    )
    fig_line.update_layout(
        height=400,
        xaxis=dict(dtick=1),
        margin=dict(t=50, l=10, r=10, b=10),
    )
    fig_line.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>"
        "Ano: %{x}<br>"
        f"{metrica}: R$ %{{y:,.0f}}"
        "<extra></extra>",
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Insight com IA — análise de tendência após o line chart
    dados_por_ano = {}
    for a in sorted(df_completo["Ano"].unique()):
        df_a = df_completo[df_completo["Ano"] == a]
        total_a = df_a[metrica].sum()
        por_funcao = df_a.groupby("Nome Função")[metrica].sum()
        maior = por_funcao.idxmax() if len(por_funcao) > 0 else "N/A"
        dados_por_ano[int(a)] = {"total": total_a, "maior_funcao": maior}

    contexto_comp = montar_contexto_comparativo(dados_por_ano)
    exibir_insight(contexto_comp, tipo="comparativo", titulo="Análise de tendência")

# ---------------------------------------------------------------------------
# 4. Tabela detalhada
# ---------------------------------------------------------------------------
section_header(title="Dados detalhados")

with st.expander("Ver tabela completa"):
    df_tab = (
        df_filtrado.groupby(["Nome Função", "Nome Subfunção"], as_index=False)[
            COLUNAS_VALOR
        ]
        .sum()
        .sort_values("Valor Pago (R$)", ascending=False)
    )
    st.dataframe(
        df_tab,
        use_container_width=True,
        column_config={
            col: st.column_config.NumberColumn(format="R$ %.0f")
            for col in COLUNAS_VALOR
        },
    )

