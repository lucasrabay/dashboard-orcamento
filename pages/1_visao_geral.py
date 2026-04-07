"""
Página: Visão Geral do Orçamento Federal.
Consome os dados e filtros já populados em st.session_state pelo app.py.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.gemini_insights import exibir_insight, montar_contexto_geral

# ---------------------------------------------------------------------------
# Guard: dados precisam ter sido carregados pelo app.py
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def formatar_bilhoes(valor: float) -> str:
    """Formata valor em R$ em escala humana (mi / bi / tri)."""
    if pd.isna(valor):
        return "R$ 0"
    abs_valor = abs(valor)
    if abs_valor >= 1e12:
        return f"R$ {valor / 1e12:,.2f} tri".replace(",", "X").replace(".", ",").replace("X", ".")
    if abs_valor >= 1e9:
        return f"R$ {valor / 1e9:,.2f} bi".replace(",", "X").replace(".", ",").replace("X", ".")
    if abs_valor >= 1e6:
        return f"R$ {valor / 1e6:,.1f} mi".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {valor:,.0f}".replace(",", ".")


def truncar(texto: str, n: int = 25) -> str:
    return texto if len(texto) <= n else texto[: n - 1] + "…"


# ---------------------------------------------------------------------------
# 1. Título e contexto
# ---------------------------------------------------------------------------
st.title("📊 Visão Geral do Orçamento Federal")
st.caption(f"Ano de referência: **{ano}** · Métrica: **{metrica}**")


# ---------------------------------------------------------------------------
# 2. KPIs
# ---------------------------------------------------------------------------
total_metrica = df_filtrado[metrica].sum()
total_empenhado = df_filtrado["Valor Empenhado (R$)"].sum()

# Variação vs ano anterior (usa df_completo para ter o histórico,
# mas respeita o recorte de funções via df_filtrado)
funcoes_ativas = df_filtrado["Nome Função"].unique().tolist()
df_ano_anterior = df_completo[
    (df_completo["Ano"] == ano - 1) & (df_completo["Nome Função"].isin(funcoes_ativas))
]
total_ano_anterior = df_ano_anterior[metrica].sum() if not df_ano_anterior.empty else 0

if total_ano_anterior > 0:
    variacao_pct = (total_metrica - total_ano_anterior) / total_ano_anterior * 100
    delta_total = f"{variacao_pct:+.1f}% vs {ano - 1}"
else:
    delta_total = None

# Maior função
por_funcao = (
    df_filtrado.groupby("Nome Função", as_index=False)[metrica]
    .sum()
    .sort_values(metrica, ascending=False)
)
if not por_funcao.empty and total_metrica > 0:
    maior_nome = por_funcao.iloc[0]["Nome Função"]
    maior_valor = por_funcao.iloc[0][metrica]
    maior_pct = maior_valor / total_metrica * 100
else:
    maior_nome, maior_pct = "—", 0

n_funcoes = df_filtrado["Nome Função"].nunique()
n_orgaos = df_filtrado["Nome Órgão Superior"].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    label=f"Total ({metrica.replace(' (R$)', '')})",
    value=formatar_bilhoes(total_metrica),
    delta=delta_total,
)
col2.metric(
    label="Total Empenhado",
    value=formatar_bilhoes(total_empenhado),
)
col3.metric(
    label="Maior área",
    value=truncar(maior_nome, 25),
    delta=f"{maior_pct:.1f}% do total",
    delta_color="off",
)
col4.metric(
    label="Áreas / Órgãos",
    value=f"{n_funcoes} / {n_orgaos}",
)

# Insight com IA — logo após os KPIs, contextualiza os gráficos
variacao_yoy = variacao_pct if delta_total is not None else None
contexto_geral = montar_contexto_geral(
    total_pago=total_metrica,
    maior_funcao=maior_nome,
    pct_maior=maior_pct,
    n_funcoes=n_funcoes,
    variacao_yoy=variacao_yoy,
    ano=ano,
)
exibir_insight(contexto_geral, tipo="geral", titulo="💡 Destaques do orçamento")


# ---------------------------------------------------------------------------
# 3. Gráficos — Treemap + Top 10 órgãos
# ---------------------------------------------------------------------------
st.divider()
col_tree, col_bar = st.columns([3, 2])

with col_tree:
    # Treemap não aceita valores negativos → filtra
    df_tree = df_filtrado[df_filtrado[metrica] > 0].copy()
    if df_tree.empty:
        st.info("Sem dados positivos para exibir no treemap.")
    else:
        fig_tree = px.treemap(
            df_tree,
            path=["Nome Função", "Nome Subfunção"],
            values=metrica,
            color="Nome Função",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title=f"Composição do orçamento por área — {ano}",
        )
        fig_tree.update_traces(
            textinfo="label+percent parent",
            hovertemplate="<b>%{label}</b><br>"
            + metrica
            + ": R$ %{value:,.2f}<br>"
            + "<extra></extra>",
        )
        fig_tree.update_layout(
            height=500,
            margin=dict(t=50, l=10, r=10, b=10),
        )
        st.plotly_chart(fig_tree, use_container_width=True)

with col_bar:
    top_orgaos = (
        df_filtrado.groupby("Nome Órgão Superior", as_index=False)[metrica]
        .sum()
        .sort_values(metrica, ascending=False)
        .head(10)
        .sort_values(metrica, ascending=True)  # para barras horizontais: maior em cima
    )
    if top_orgaos.empty:
        st.info("Sem dados para exibir no ranking de órgãos.")
    else:
        fig_bar = px.bar(
            top_orgaos,
            x=metrica,
            y="Nome Órgão Superior",
            orientation="h",
            title=f"Top 10 órgãos — {ano}",
        )
        fig_bar.update_traces(
            marker_color="#4C78A8",
            hovertemplate="<b>%{y}</b><br>"
            + metrica
            + ": R$ %{x:,.2f}<br>"
            + "<extra></extra>",
        )
        fig_bar.update_layout(
            height=500,
            yaxis_title=None,
            xaxis_title=metrica,
            margin=dict(t=50, l=10, r=10, b=10),
        )
        st.plotly_chart(fig_bar, use_container_width=True)


# ---------------------------------------------------------------------------
# 4. Waffle chart — "Para onde vai cada R$ 1,00"
# ---------------------------------------------------------------------------
st.divider()

df_waffle = (
    df_filtrado[df_filtrado[metrica] > 0]
    .groupby("Nome Função", as_index=False)[metrica]
    .sum()
    .sort_values(metrica, ascending=False)
)

total_waffle = df_waffle[metrica].sum()
if total_waffle <= 0 or df_waffle.empty:
    st.info("Sem dados para gerar o waffle chart.")
else:
    # Calcula quantos dos 100 quadrados cada função recebe (arredondamento +
    # ajuste para totalizar exatamente 100)
    df_waffle["proporcao"] = df_waffle[metrica] / total_waffle
    df_waffle["quadrados"] = (df_waffle["proporcao"] * 100).round().astype(int)

    diff = 100 - df_waffle["quadrados"].sum()
    if diff != 0 and not df_waffle.empty:
        # Ajusta o primeiro (maior) para fechar em 100
        df_waffle.iloc[0, df_waffle.columns.get_loc("quadrados")] += diff

    # Monta um trace por função — cada trace contém todos os quadrados
    # daquela fatia (cor uniforme, legenda única)
    cores = px.colors.qualitative.Set2
    fig_waffle = go.Figure()

    idx = 0
    for i, (_, row) in enumerate(df_waffle.iterrows()):
        n_quad = int(row["quadrados"])
        if n_quad <= 0:
            continue
        funcao = row["Nome Função"]
        valor = row[metrica]
        pct = row["proporcao"] * 100
        cor = cores[i % len(cores)]

        xs = [(idx + k) % 10 for k in range(n_quad)]
        ys = [9 - ((idx + k) // 10) for k in range(n_quad)]
        idx += n_quad

        fig_waffle.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers",
                marker=dict(symbol="square", size=28, color=cor),
                name=funcao,
                legendgroup=funcao,
                showlegend=True,
                hovertemplate=(
                    f"<b>{funcao}</b><br>"
                    f"{pct:.1f}% do total<br>"
                    f"R$ {valor:,.2f}"
                    "<extra></extra>"
                ),
            )
        )

    fig_waffle.update_layout(
        title=f"Para onde vai cada R$ 1,00 de imposto — {ano}",
        height=500,
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, 9.5],
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, 9.5],
            scaleanchor="x",
            scaleratio=1,
        ),
        margin=dict(t=60, l=10, r=10, b=10),
        legend=dict(title="Função", itemsizing="constant"),
    )
    st.plotly_chart(fig_waffle, use_container_width=True)


