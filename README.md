# Para Onde Vai Seu Imposto?

> Dashboard interativo para análise do orçamento federal brasileiro, com insights gerados por IA.

Uma ferramenta de visualização e exploração de dados que permite ao cidadão entender, em poucos cliques, como o governo federal aloca seus recursos — e simular cenários alternativos de redistribuição orçamentária.

---

## Sobre o projeto

Este dashboard transforma os microdados brutos do **Portal da Transparência** do Governo Federal em uma narrativa visual acessível. O usuário pode:

- **Visualizar** a composição do orçamento federal de forma hierárquica e intuitiva
- **Explorar** a evolução dos gastos por área ao longo dos anos
- **Simular** realocações orçamentárias e analisar seus impactos potenciais
- **Receber análises automáticas** geradas por IA contextualizadas aos filtros aplicados

O projeto cobre o período de **2020 a 2025**, totalizando mais de **R$ 1,48 trilhão** em despesas executadas, distribuídas entre **29 áreas funcionais** e **36 órgãos superiores** do Poder Executivo Federal.

---

## Funcionalidades

### Visão Geral
Painel macro com KPIs do exercício, distribuição hierárquica via treemap, ranking dos principais órgãos executores e um waffle chart que decompõe visualmente cada R$ 1,00 de imposto pago.

### Explorar
Drill-down hierárquico via sunburst (Função → Subfunção) e análise de evolução temporal multivariada — o usuário escolhe quais áreas comparar e visualiza a trajetória ao longo de 6 anos.

### Simulador de Cenários
Ferramenta interativa de redistribuição orçamentária. O usuário ajusta sliders de variação percentual sobre as 8 maiores áreas e visualiza, em tempo real, o impacto financeiro absoluto e relativo da nova alocação. Inclui análise de viabilidade gerada por IA.

### Análises com IA
Cada página integra o **Google Gemini** para gerar interpretações dinâmicas dos dados filtrados. Os textos contextualizam números, destacam tendências e sugerem pontos de atenção — sem templates fixos, adaptando-se a cada combinação de filtros.

---

## Stack técnica

| Camada | Tecnologia |
|---|---|
| Aplicação | Streamlit (multipage) |
| Visualização | Plotly Express + Plotly Graph Objects |
| Manipulação de dados | Pandas |
| LLM | Google Gemini (gemini-2.0-flash) |
| Configuração | python-dotenv |
| Design system | CSS customizado + Material icons + ícones Lucide |

---

## Estrutura do projeto

```
dashboard-orcamento/
├── app.py                        # Entry point + navegação multipage
├── .streamlit/
│   └── config.toml               # Theme global
├── pages/
│   ├── 1_visao_geral.py          # KPIs, treemap, ranking, waffle chart
│   ├── 2_explorar.py             # Sunburst + evolução temporal
│   └── 3_simulador.py            # Cenários "e se?"
├── components/
│   ├── data_loader.py            # Carregamento e cache dos dados
│   ├── gemini_insights.py        # Integração com Google Gemini
│   ├── ui.py                     # Helpers de UI (cards, headers, ícones)
│   └── plotly_theme.py           # Template Plotly customizado
├── data/
│   ├── raw/                      # CSVs brutos do Portal da Transparência
│   ├── prepare_data.py           # Script de ETL
│   └── despesas_limpo.csv        # Dataset processado
├── assets/
│   └── style.css                 # CSS customizado do design system
├── requirements.txt
├── .env                          # GEMINI_API_KEY
└── README.md
```

---

## Como executar

### 1. Pré-requisitos

- Python 3.11 ou superior
- Chave de API do Google Gemini ([obter aqui](https://aistudio.google.com/app/apikey))

### 2. Clonar e instalar dependências

```bash
git clone <url-do-repo>
cd dashboard-orcamento
pip install -r requirements.txt
```

### 3. Baixar os dados brutos

Acesse o [Portal da Transparência — Execução da Despesa](https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao) e baixe os arquivos de **dezembro** dos anos de 2020 a 2025. Coloque os CSVs em `data/raw/`.

A pasta deve ficar assim:

```
data/raw/
├── 202012_Despesas.csv
├── 202112_Despesas.csv
├── 202212_Despesas.csv
├── 202312_Despesas.csv
├── 202412_Despesas.csv
└── 202512_Despesas.csv
```

### 4. Processar os dados

```bash
python data/prepare_data.py
```

Este script lê todos os CSVs brutos (~440 MB no total), aplica limpeza, padronização e agregação, e gera um único `despesas_limpo.csv` de aproximadamente 1 MB com 6.885 linhas otimizadas para visualização.

### 5. Configurar a chave da API

Crie um arquivo `.env` na raiz do projeto:

```bash
echo "GEMINI_API_KEY=sua_chave_aqui" > .env
```

### 6. Rodar o dashboard

```bash
streamlit run app.py
```

O dashboard abrirá automaticamente em `http://localhost:8501`.

---


## Decisões de design

**Paleta monocromática com accent verde** — Inspirada em produtos como Linear e Stripe, a paleta sóbria (cinza-azulado) com accent verde (#059669) reforça a seriedade dos dados públicos e remete ao tema financeiro sem ser caricato.

**Insights antes dos gráficos** — Na página de Visão Geral, o texto da IA aparece logo após os KPIs, contextualizando o que o usuário está prestes a ver. Isso segue o princípio de "lead with the insight" do storytelling com dados.

**Cache agressivo** — Todas as chamadas ao Gemini usam `@st.cache_data(ttl=300)`. Filtros que produzem o mesmo contexto retornam respostas instantâneas, sem custo adicional de API.

**Cores que codificam significado** — Verde para valores positivos e neutros, vermelho apenas para reduções no simulador. Nos gráficos, o accent verde é reservado para destaque de elementos comparativos, evitando o "arco-íris" de gráficos amadores.

---

## Fontes de dados

- [Portal da Transparência do Governo Federal](https://portaldatransparencia.gov.br/) — Controladoria-Geral da União (CGU)
- Período coberto: 2020 a 2025 (execução orçamentária consolidada)

---

## Créditos

**Autor**: Lucas Rabay Butcher 

---

## Licença

Projeto desenvolvido para fins acadêmicos. Os dados utilizados são públicos e disponibilizados pelo Portal da Transparência do Governo Federal sob os termos da Lei de Acesso à Informação (Lei nº 12.527/2011).