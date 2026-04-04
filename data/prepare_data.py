"""
prepare_data.py — ETL do Portal da Transparência
Roda uma única vez: lê os CSVs brutos e gera despesas_limpo.csv
Uso: python data/prepare_data.py
"""

import pandas as pd
import glob
import os

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
OUTPUT = os.path.join(os.path.dirname(__file__), "despesas_limpo.csv")

# Colunas que vamos manter (nomes originais com encoding latin-1)
COLUNAS_USAR = [
    "Ano e mês do lançamento",
    "Código Órgão Superior",
    "Nome Órgão Superior",
    "Código Função",
    "Nome Função",
    "Código Subfunção",
    "Nome Subfunção",
    "Nome Programa Orçamentário",
    "Valor Empenhado (R$)",
    "Valor Liquidado (R$)",
    "Valor Pago (R$)",
]

COLUNAS_VALOR = [
    "Valor Empenhado (R$)",
    "Valor Liquidado (R$)",
    "Valor Pago (R$)",
]


def parse_brl(valor: str) -> float:
    """Converte '515873,30' -> 515873.30"""
    if isinstance(valor, (int, float)):
        return float(valor)
    return float(str(valor).replace(".", "").replace(",", "."))


def load_csv(filepath: str) -> pd.DataFrame:
    """Carrega um CSV do Portal da Transparência"""
    print(f"  Lendo {os.path.basename(filepath)}...")
    df = pd.read_csv(
        filepath,
        sep=";",
        encoding="latin-1",
        dtype=str,
    )
    # Corrige typo presente em arquivos mais antigos ("Subfução" → "Subfunção")
    df.rename(columns={"Código Subfução": "Código Subfunção"}, inplace=True)
    df = df[COLUNAS_USAR]
    # Converter valores monetários
    for col in COLUNAS_VALOR:
        df[col] = df[col].apply(parse_brl)

    # Extrair ano do campo "2025/12" -> 2025
    df["Ano"] = df["Ano e mês do lançamento"].str[:4].astype(int)

    return df


def main():
    arquivos = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))
    if not arquivos:
        print(f"ERRO: Nenhum CSV encontrado em {RAW_DIR}")
        return

    print(f"Encontrados {len(arquivos)} arquivos:\n")

    # 1. Carregar todos
    dfs = [load_csv(f) for f in arquivos]
    df_all = pd.concat(dfs, ignore_index=True)
    print(f"\n  Total de linhas brutas: {len(df_all):,}")

    # 2. Agregar por Ano + Órgão Superior + Função + Subfunção
    df_agg = (
        df_all.groupby(
            [
                "Ano",
                "Código Órgão Superior",
                "Nome Órgão Superior",
                "Código Função",
                "Nome Função",
                "Código Subfunção",
                "Nome Subfunção",
            ],
            as_index=False,
        )[COLUNAS_VALOR]
        .sum()
    )

    # 3. Limpar nomes (remover espaços extras, truncamentos)
    for col in ["Nome Órgão Superior", "Nome Função", "Nome Subfunção"]:
        df_agg[col] = df_agg[col].str.strip()

    # 4. Ordenar
    df_agg = df_agg.sort_values(["Ano", "Valor Pago (R$)"], ascending=[True, False])

    # 5. Salvar
    df_agg.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"\n  Linhas agregadas: {len(df_agg):,}")
    print(f"  Arquivo salvo: {OUTPUT}")
    print(f"  Tamanho: {os.path.getsize(OUTPUT) / 1024 / 1024:.1f} MB")

    # 6. Resumo rápido
    print("\n--- Resumo ---")
    print(f"  Anos: {sorted(df_agg['Ano'].unique())}")
    print(f"  Funções únicas: {df_agg['Nome Função'].nunique()}")
    print(f"  Órgãos únicos: {df_agg['Nome Órgão Superior'].nunique()}")
    print(f"  Total pago (todos os anos): R$ {df_agg['Valor Pago (R$)'].sum():,.2f}")


if __name__ == "__main__":
    main()
