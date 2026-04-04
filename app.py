"""
app.py — Entry point do Dashboard de Orçamento Federal
Uso: streamlit run app.py
"""

import streamlit as st

# --- Configuração da página ---
st.set_page_config(
    page_title="Para Onde Vai Seu Imposto?",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS customizado ---
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Navegação ---
visao_geral = st.Page("pages/1_visao_geral.py", title="Visão Geral", icon="📊")
explorar = st.Page("pages/2_explorar.py", title="Explorar", icon="🔍")
simulador = st.Page("pages/3_simulador.py", title="Simulador", icon="⚙️")

pg = st.navigation([visao_geral, explorar, simulador])

# --- Sidebar global ---
st.sidebar.title("💰 Para Onde Vai Seu Imposto?")
st.sidebar.caption("Dashboard do Orçamento Federal Brasileiro")
st.sidebar.divider()

pg.run()
