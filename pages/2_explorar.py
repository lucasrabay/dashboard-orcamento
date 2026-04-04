"""Stub — Explorar."""

import streamlit as st

st.title("🔍 Explorar")

df = st.session_state.get("df_filtrado")
if df is None:
    st.warning("Dados não carregados. Volte para a página inicial.")
    st.stop()

st.write(f"Linhas no df filtrado: **{len(df):,}**")
st.dataframe(df.head())
