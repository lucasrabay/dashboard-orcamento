"""
Para Onde Vai Seu Imposto? — dashboard Streamlit multipage.
Entry point: configura página, carrega dados, monta sidebar global e roteia.
Uso: streamlit run app.py
"""

import os

import pandas as pd
import streamlit as st

from components.plotly_theme import register_theme
from components.ui import footer

register_theme()

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Para Onde Vai Seu Imposto?",
    page_icon="💰",
    layout="wide",
)

# Carregar CSS customizado
CSS_PATH = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "despesas_limpo.csv")

METRICAS = [
    "Valor Pago (R$)",
    "Valor Empenhado (R$)",
    "Valor Liquidado (R$)",
]


# ---------------------------------------------------------------------------
# Carregamento dos dados (cache para não reler o CSV a cada interação)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Carregando dados do orçamento...")
def carregar_dados(caminho: str) -> pd.DataFrame:
    df = pd.read_csv(caminho)
    df["Ano"] = df["Ano"].astype(int)
    return df


try:
    df_completo = carregar_dados(DATA_PATH)
except FileNotFoundError:
    st.error(
        "Arquivo `data/despesas_limpo.csv` não encontrado.\n\n"
        "Rode primeiro o ETL para gerar o dataset limpo:\n\n"
        "```bash\npython data/prepare_data.py\n```"
    )
    st.stop()


# ---------------------------------------------------------------------------
# Sidebar global — filtros compartilhados por todas as páginas
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 24px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 24px;">
        <div style="font-size: 16px; font-weight: 700; color: #0F172A; letter-spacing: -0.01em;">
            Orçamento Federal
        </div>
        <div style="font-size: 12px; color: #64748B; margin-top: 2px;">
            Para onde vai seu imposto
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size: 11px; font-weight: 600; color: #94A3B8; '
        'text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">'
        "FILTROS</div>",
        unsafe_allow_html=True,
    )

    anos_disponiveis = sorted(df_completo["Ano"].unique().tolist())
    ano_selecionado = st.selectbox(
        "Ano",
        options=anos_disponiveis,
        index=len(anos_disponiveis) - 1,  # default = último ano
    )

    metrica_selecionada = st.radio(
        "Métrica",
        options=METRICAS,
        index=0,
    )

    funcoes_disponiveis = sorted(df_completo["Nome Função"].dropna().unique().tolist())
    funcoes_selecionadas = st.multiselect(
        "Funções",
        options=funcoes_disponiveis,
        default=funcoes_disponiveis,  # default = todas
    )


# ---------------------------------------------------------------------------
# Aplicar filtros e expor no session_state para as páginas consumirem
# ---------------------------------------------------------------------------
df_filtrado = df_completo[
    (df_completo["Ano"] == ano_selecionado)
    & (df_completo["Nome Função"].isin(funcoes_selecionadas))
]

st.session_state["df_completo"] = df_completo
st.session_state["df_filtrado"] = df_filtrado
st.session_state["ano_selecionado"] = ano_selecionado
st.session_state["metrica_selecionada"] = metrica_selecionada
st.session_state["funcoes_selecionadas"] = funcoes_selecionadas


# ---------------------------------------------------------------------------
# Navegação multipage
# ---------------------------------------------------------------------------
paginas = [
    st.Page("pages/1_visao_geral.py", title="Visão Geral", icon=":material/dashboard:", default=True),
    st.Page("pages/2_explorar.py", title="Explorar", icon=":material/search:"),
    st.Page("pages/3_simulador.py", title="Simulador", icon=":material/tune:"),
]

nav = st.navigation(paginas)
nav.run()

footer()
