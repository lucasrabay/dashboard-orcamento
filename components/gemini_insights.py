"""
Módulo de geração de insights com Gemini.
Centraliza prompts, chamadas à API e exibição nos componentes do dashboard.
"""

import os

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("GEMINI_API_KEY")
if _API_KEY:
    genai.configure(api_key=_API_KEY)

_MODELS = ["gemini-3.1-flash-lite-preview"]

# ---------------------------------------------------------------------------
# Prompts por tipo de insight
# ---------------------------------------------------------------------------
_PROMPTS: dict[str, str] = {
    "geral": (
        "Você é um analista de orçamento público brasileiro.\n"
        "Com base nos dados abaixo, gere um parágrafo curto (3-4 frases) com:\n"
        "- O principal destaque do orçamento\n"
        "- Uma comparação relevante\n"
        "- Uma sugestão de ação ou ponto de atenção para o gestor público\n\n"
        "Dados:\n{contexto}\n\n"
        "Responda em português brasileiro, de forma direta e objetiva. "
        "Use valores em bilhões/milhões quando apropriado. "
        "Não use bullet points, escreva em prosa corrida."
    ),
    "comparativo": (
        "Você é um analista de dados públicos brasileiro.\n"
        "Compare os dados abaixo entre os anos apresentados. Destaque:\n"
        "- A tendência principal (crescimento, queda ou estabilidade)\n"
        "- A área com maior variação absoluta\n"
        "- Um possível contexto ou explicação para as mudanças observadas\n\n"
        "Dados:\n{contexto}\n\n"
        "Responda em 2-3 frases em português, de forma analítica e objetiva."
    ),
    "simulacao": (
        "Você é um consultor de políticas públicas brasileiro.\n"
        "O usuário simulou uma realocação do orçamento federal. Analise:\n"
        "- Os potenciais impactos positivos e negativos da redistribuição proposta\n"
        "- Se a magnitude das mudanças é realista e implementável\n"
        "- Uma recomendação concreta ao gestor\n\n"
        "Dados do cenário:\n{contexto}\n\n"
        "Responda em 3-4 frases em português, de forma pragmática e equilibrada."
    ),
}


# ---------------------------------------------------------------------------
# Geração de insight (cacheada por 5 min)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=300, show_spinner=False)
def gerar_insight(contexto: str, tipo: str) -> str:
    """Chama o Gemini e retorna o texto gerado."""
    if not _API_KEY:
        return (
            "Configure a variável GEMINI_API_KEY no arquivo .env "
            "para ativar os textos dinâmicos com IA."
        )
    prompt = _PROMPTS[tipo].format(contexto=contexto)
    config = genai.types.GenerationConfig(max_output_tokens=300, temperature=0.7)

    # Tenta cada modelo na lista; se um estourar cota, tenta o próximo
    last_error = None
    for model_name in _MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt, generation_config=config)
            return response.text.strip()
        except Exception as e:
            last_error = e

    err_msg = str(last_error)
    if "429" in err_msg or "ResourceExhausted" in err_msg:
        return (
            "⚠️ Cota da API Gemini esgotada. "
            "Aguarde o reset diário ou ative o billing em https://ai.google.dev"
        )
    return f"⚠️ Não foi possível gerar a análise. Erro: {err_msg}"


# ---------------------------------------------------------------------------
# Funções auxiliares para montar contexto
# ---------------------------------------------------------------------------
def montar_contexto_geral(
    total_pago: float,
    maior_funcao: str,
    pct_maior: float,
    n_funcoes: int,
    variacao_yoy: float | None,
    ano: int,
) -> str:
    variacao_str = f"{variacao_yoy:+.1f}%" if variacao_yoy is not None else "N/A"
    return (
        f"Ano: {ano}\n"
        f"Total pago pelo governo federal: R$ {total_pago:,.0f}\n"
        f"Maior área de gasto: {maior_funcao} ({pct_maior:.1f}% do total)\n"
        f"Número de áreas orçamentárias: {n_funcoes}\n"
        f"Variação em relação ao ano anterior: {variacao_str}"
    )


def montar_contexto_comparativo(dados_por_ano: dict) -> str:
    linhas = []
    for ano in sorted(dados_por_ano):
        d = dados_por_ano[ano]
        linhas.append(
            f"Ano {ano}: Total = R$ {d['total']:,.0f} | "
            f"Maior área = {d['maior_funcao']}"
        )
    return "\n".join(linhas)


def montar_contexto_simulacao(
    realocacoes: dict, total_original: float
) -> str:
    linhas = [f"Orçamento original total: R$ {total_original:,.0f}\n"]
    for funcao, vals in realocacoes.items():
        original = vals["original"]
        novo = vals["novo"]
        diff = novo - original
        pct = (diff / original * 100) if original else 0
        linhas.append(
            f"- {funcao}: R$ {original:,.0f} → R$ {novo:,.0f} "
            f"(variação: {pct:+.1f}%)"
        )
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Exibição padronizada
# ---------------------------------------------------------------------------
def exibir_insight(contexto: str, tipo: str, titulo: str) -> None:
    """Gera e exibe o insight dentro de um st.info."""
    with st.spinner("Gerando análise com IA..."):
        texto = gerar_insight(contexto, tipo)
    st.info(f"**{titulo}**\n\n{texto}")
