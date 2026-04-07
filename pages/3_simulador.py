"""
Página: Simulador de Cenários.
Permite realocar o orçamento com sliders e ver o impacto em tempo real.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.gemini_insights import exibir_insight, montar_contexto_simulacao

# ---------------------------------------------------------------------------
# Guard
# ---------------------------------------------------------------------------
df_completo: pd.DataFrame | None = st.session_state.get("df_completo")
ano: int | None = st.session_state.get("ano_selecionado")
metrica: str | None = st.session_state.get("metrica_selecionada")

if df_completo is None or ano is None or metrica is None:
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


def truncar(texto: str, n: int = 40) -> str:
    return texto if len(texto) <= n else texto[: n - 1] + "…"


# ---------------------------------------------------------------------------
# 1. Título e contexto
# ---------------------------------------------------------------------------
st.title("⚙️ Simulador de Cenários")
st.caption(f"Redistribua o orçamento de {ano} e veja o impacto")

# ---------------------------------------------------------------------------
# 2. Preparação dos dados — top 8 funções do ano selecionado
# ---------------------------------------------------------------------------
df_ano = (
    df_completo[df_completo["Ano"] == ano]
    .groupby("Nome Função", as_index=False)[metrica]
    .sum()
    .sort_values(metrica, ascending=False)
)
top8 = df_ano.head(8).reset_index(drop=True)
total_original = top8[metrica].sum()

st.info(
    f"**Orçamento base ({ano}):** {formatar_bilhoes(total_original)} · "
    f"**{len(top8)} maiores áreas** sendo simuladas · "
    "Ajuste os sliders abaixo para simular uma realocação."
)

# ---------------------------------------------------------------------------
# 3. Sliders de realocação
# ---------------------------------------------------------------------------
st.subheader("🎛️ Ajuste a distribuição (variação %)")

col_esq, col_dir = st.columns(2)
ajustes: list[float] = []

for i, row in top8.iterrows():
    col = col_esq if i < 4 else col_dir
    with col:
        pct = st.slider(
            label=truncar(row["Nome Função"]),
            min_value=-50.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            format="%+.1f%%",
            help=f"Original: {formatar_bilhoes(row[metrica])}",
            key=f"slider_{i}",
        )
        ajustes.append(pct)

# Valores simulados
top8["Ajuste %"] = ajustes
top8["Simulado"] = top8[metrica] * (1 + top8["Ajuste %"] / 100)

total_simulado = top8["Simulado"].sum()
diferenca = total_simulado - total_original

# ---------------------------------------------------------------------------
# 4. KPIs do cenário
# ---------------------------------------------------------------------------
st.divider()
k1, k2, k3 = st.columns(3)

k1.metric(label="Orçamento original", value=formatar_bilhoes(total_original))

variacao_pct = (
    (total_simulado - total_original) / total_original * 100
    if total_original != 0
    else 0
)
k2.metric(
    label="Orçamento simulado",
    value=formatar_bilhoes(total_simulado),
    delta=f"{variacao_pct:+.1f}%",
)

k3.metric(
    label="Diferença",
    value=formatar_bilhoes(abs(diferenca)),
    delta="Aumento" if diferenca >= 0 else "Redução",
    delta_color="normal" if diferenca >= 0 else "inverse",
)

# ---------------------------------------------------------------------------
# 5. Gráfico comparativo — barras agrupadas
# ---------------------------------------------------------------------------
nomes = top8["Nome Função"].tolist()

fig = go.Figure(
    data=[
        go.Bar(
            name="Real",
            x=nomes,
            y=top8[metrica],
            marker_color="#4C78A8",
            hovertemplate="<b>%{x}</b><br>Real: R$ %{y:,.0f}<extra></extra>",
        ),
        go.Bar(
            name="Simulado",
            x=nomes,
            y=top8["Simulado"],
            marker_color="#F58518",
            hovertemplate="<b>%{x}</b><br>Simulado: R$ %{y:,.0f}<extra></extra>",
        ),
    ]
)
fig.update_layout(
    barmode="group",
    title="Orçamento real vs. cenário simulado",
    yaxis_tickformat=",",
    height=450,
    margin=dict(t=50, l=10, r=10, b=10),
)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# 6. Tabela de mudanças
# ---------------------------------------------------------------------------
with st.expander("📋 Detalhamento das mudanças"):
    df_tab = pd.DataFrame(
        {
            "Área": top8["Nome Função"],
            "Original": top8[metrica],
            "Simulado": top8["Simulado"],
            "Variação R$": top8["Simulado"] - top8[metrica],
            "Variação %": top8["Ajuste %"].astype(float),
        }
    )
    st.dataframe(
        df_tab,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Original": st.column_config.NumberColumn(format="R$ %,.0f"),
            "Simulado": st.column_config.NumberColumn(format="R$ %,.0f"),
            "Variação R$": st.column_config.NumberColumn(format="R$ %+,.0f"),
            "Variação %": st.column_config.NumberColumn(format="%+.1f%%"),
        },
    )

# ---------------------------------------------------------------------------
# 7. Insight com IA sobre o cenário simulado
# ---------------------------------------------------------------------------
st.divider()
algum_slider_movido = any(a != 0 for a in ajustes)

if algum_slider_movido:
    realocacoes = {
        row["Nome Função"]: {"original": row[metrica], "novo": row["Simulado"]}
        for _, row in top8.iterrows()
        if row["Ajuste %"] != 0
    }
    contexto_sim = montar_contexto_simulacao(realocacoes, total_original)
    exibir_insight(contexto_sim, tipo="simulacao", titulo="🤖 Análise do cenário simulado")
else:
    st.info(
        "💡 *Ajuste os sliders acima para simular uma realocação "
        "e receber uma análise personalizada.*"
    )
