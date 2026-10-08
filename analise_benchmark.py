#!/usr/bin/env python3
"""
Analise dos resultados do microbenchmark de memoria/arquivo (Windows x Linux).

Le:
  dados/resultados_windows.csv
  dados/resultados_linux.csv

Gera:
  tabelas/*.csv   -> tabelas de estatisticas
  graficos/*.png  -> graficos

Uso (a partir da pasta do projeto):
  python analise_benchmark.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # gera arquivos sem precisar de interface grafica
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

BASE = Path(__file__).resolve().parent
DADOS = BASE / "dados"
TABELAS = BASE / "tabelas"
GRAFICOS = BASE / "graficos"
TABELAS.mkdir(exist_ok=True)
GRAFICOS.mkdir(exist_ok=True)

OPERACOES = ["alocacao", "escrita", "leitura", "limpeza", "total"]
ROTULOS = {
    "alocacao": "Alocação",
    "escrita": "Escrita",
    "leitura": "Leitura",
    "limpeza": "Limpeza",
    "total": "Total",
}
CORES = {"Windows": "#1f77b4", "Linux": "#e07b00"}
NS_PARA_MS = 1e6


# ------------------------------------------------------------------ carga
def carregar() -> pd.DataFrame:
    win = pd.read_csv(DADOS / "resultados_windows.csv")
    lin = pd.read_csv(DADOS / "resultados_linux.csv")
    win["so"] = "Windows"
    lin["so"] = "Linux"
    df = pd.concat([win, lin], ignore_index=True)
    for op in OPERACOES:
        df[f"{op}_ms"] = df[f"{op}_ns"] / NS_PARA_MS
    return df


def validar(df: pd.DataFrame) -> None:
    """Checagens basicas de integridade dos dados."""
    assert df.isna().sum().sum() == 0, "ha valores ausentes"
    por_grupo = df.groupby(["so", "tamanho_mb"]).size()
    assert (por_grupo == 100).all(), "esperado 100 repeticoes por tamanho e SO"
    soma = df[[f"{o}_ns" for o in OPERACOES[:-1]]].sum(axis=1)
    assert (soma == df["total_ns"]).all(), "total_ns difere da soma das etapas"


# ----------------------------------------------------------------- tabelas
def tabela_geral(df: pd.DataFrame) -> pd.DataFrame:
    """Media geral por operacao (equivalente ao benchmark.py original), em ms."""
    linhas = {}
    for op in OPERACOES:
        w = df[(df.so == "Windows")][f"{op}_ms"].mean()
        l = df[(df.so == "Linux")][f"{op}_ms"].mean()
        linhas[ROTULOS[op]] = {
            "Windows (ms)": w,
            "Linux (ms)": l,
            "Razão Windows/Linux": w / l,
        }
    return pd.DataFrame(linhas).T


def tabela_por_tamanho(df: pd.DataFrame, op: str) -> pd.DataFrame:
    g = df.groupby(["tamanho_mb", "so"])[f"{op}_ms"].agg(
        media="mean", mediana="median", desvio="std", minimo="min", maximo="max"
    )
    g["cv_%"] = g["desvio"] / g["media"] * 100
    return g.round(3).reset_index()


def tabela_comparativa_total(df: pd.DataFrame) -> pd.DataFrame:
    """Windows x Linux por tamanho para o tempo total, com teste estatistico."""
    linhas = []
    for tam, sub in df.groupby("tamanho_mb"):
        w = sub[sub.so == "Windows"]["total_ms"]
        l = sub[sub.so == "Linux"]["total_ms"]
        u, p = stats.mannwhitneyu(w, l, alternative="two-sided")
        linhas.append(
            {
                "tamanho_mb": tam,
                "windows_media_ms": w.mean(),
                "windows_mediana_ms": w.median(),
                "linux_media_ms": l.mean(),
                "linux_mediana_ms": l.median(),
                "razao_medias_win/lin": w.mean() / l.mean(),
                "razao_medianas_win/lin": w.median() / l.median(),
                "p_valor_mann_whitney": p,
            }
        )
    tabela = pd.DataFrame(linhas)
    colunas_num = [c for c in tabela.columns if c not in ("tamanho_mb", "p_valor_mann_whitney")]
    tabela[colunas_num] = tabela[colunas_num].round(4)
    # p-valores muito pequenos: notacao cientifica para nao virar "0.0"
    tabela["p_valor_mann_whitney"] = tabela["p_valor_mann_whitney"].map(lambda p: f"{p:.3e}")
    return tabela


def tabela_razao_por_operacao(df: pd.DataFrame) -> pd.DataFrame:
    """Razao Windows/Linux das medianas, por operacao e tamanho."""
    med = df.groupby(["tamanho_mb", "so"])[[f"{o}_ms" for o in OPERACOES]].median()
    razao = med.xs("Windows", level="so") / med.xs("Linux", level="so")
    razao.columns = [ROTULOS[o] for o in OPERACOES]
    return razao.round(2).reset_index()


def tabela_primeira_repeticao(df: pd.DataFrame) -> pd.DataFrame:
    """Compara a repeticao 1 (execucao 'a frio') com a mediana das demais."""
    linhas = []
    for (so, tam), sub in df.groupby(["so", "tamanho_mb"]):
        primeira = sub[sub.repeticao == 1]["total_ms"].iloc[0]
        resto = sub[sub.repeticao > 1]["total_ms"].median()
        linhas.append(
            {
                "so": so,
                "tamanho_mb": tam,
                "rep1_ms": primeira,
                "mediana_rep2a100_ms": resto,
                "rep1/mediana": primeira / resto,
            }
        )
    return pd.DataFrame(linhas).round(3)


def tabela_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Contagem de outliers (criterio de Tukey, 1,5 x IQR) no tempo total."""
    linhas = []
    for (so, tam), sub in df.groupby(["so", "tamanho_mb"]):
        q1, q3 = sub["total_ms"].quantile([0.25, 0.75])
        lim = q3 + 1.5 * (q3 - q1)
        linhas.append(
            {"so": so, "tamanho_mb": tam, "outliers_acima_de_Q3+1.5IQR": int((sub["total_ms"] > lim).sum())}
        )
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- graficos
def estilo():
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "axes.grid": True,
            "grid.alpha": 0.3,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 10,
        }
    )


def grafico_total_por_tamanho(df):
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for so in ["Windows", "Linux"]:
        g = df[df.so == so].groupby("tamanho_mb")["total_ms"]
        ax.plot(g.median().index, g.median().values, marker="o", color=CORES[so], label=f"{so} (mediana)")
        q1, q3 = g.quantile(0.25), g.quantile(0.75)
        ax.fill_between(q1.index, q1.values, q3.values, color=CORES[so], alpha=0.15)
    ax.set_xlabel("Tamanho do buffer (MB)")
    ax.set_ylabel("Tempo total (ms)")
    ax.set_title("Tempo total por tamanho: mediana e intervalo interquartil")
    ax.legend()
    fig.tight_layout()
    fig.savefig(GRAFICOS / "01_total_por_tamanho.png")
    plt.close(fig)


def grafico_operacoes_por_tamanho(df):
    ops = ["alocacao", "escrita", "leitura", "limpeza"]
    fig, eixos = plt.subplots(2, 2, figsize=(11, 7.5))
    for ax, op in zip(eixos.ravel(), ops):
        for so in ["Windows", "Linux"]:
            g = df[df.so == so].groupby("tamanho_mb")[f"{op}_ms"].median()
            ax.plot(g.index, g.values, marker="o", color=CORES[so], label=so)
        ax.set_title(ROTULOS[op])
        ax.set_xlabel("Tamanho do buffer (MB)")
        ax.set_ylabel("Mediana (ms)")
        ax.legend()
    fig.suptitle("Tempo por operação (mediana de 100 repetições)")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "02_operacoes_por_tamanho.png")
    plt.close(fig)


def grafico_boxplot_total(df):
    tamanhos = sorted(df.tamanho_mb.unique())
    fig, ax = plt.subplots(figsize=(12, 4.8))
    largura = 0.35
    for i, so in enumerate(["Windows", "Linux"]):
        dados = [df[(df.so == so) & (df.tamanho_mb == t)]["total_ms"].values for t in tamanhos]
        pos = np.arange(len(tamanhos)) + (i - 0.5) * largura
        bp = ax.boxplot(
            dados, positions=pos, widths=largura * 0.9, patch_artist=True,
            flierprops={"markersize": 2.5, "alpha": 0.5},
            medianprops={"color": "black"},
        )
        for caixa in bp["boxes"]:
            caixa.set_facecolor(CORES[so])
            caixa.set_alpha(0.6)
        ax.plot([], [], color=CORES[so], linewidth=6, alpha=0.6, label=so)
    ax.set_xticks(np.arange(len(tamanhos)))
    ax.set_xticklabels(tamanhos)
    ax.set_xlabel("Tamanho do buffer (MB)")
    ax.set_ylabel("Tempo total (ms)")
    ax.set_title("Distribuição do tempo total por tamanho")
    ax.legend()
    fig.tight_layout()
    fig.savefig(GRAFICOS / "03_boxplot_total.png")
    plt.close(fig)


def grafico_composicao(df):
    ops = ["alocacao", "escrita", "leitura", "limpeza"]
    cores_op = ["#4c78a8", "#f58518", "#54a24b", "#b279a2"]
    tamanhos = sorted(df.tamanho_mb.unique())
    fig, eixos = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, so in zip(eixos, ["Windows", "Linux"]):
        med = df[df.so == so].groupby("tamanho_mb")[[f"{o}_ms" for o in ops]].median()
        base = np.zeros(len(tamanhos))
        for op, cor in zip(ops, cores_op):
            vals = med[f"{op}_ms"].values
            ax.bar(np.arange(len(tamanhos)), vals, bottom=base, color=cor, label=ROTULOS[op])
            base += vals
        ax.set_xticks(np.arange(len(tamanhos)))
        ax.set_xticklabels(tamanhos)
        ax.set_xlabel("Tamanho do buffer (MB)")
        ax.set_title(so)
    eixos[0].set_ylabel("Soma das medianas (ms)")
    eixos[0].legend()
    fig.suptitle("Composição do tempo total por operação")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "04_composicao_tempo.png")
    plt.close(fig)


def grafico_razao(razao):
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    for op in ["Alocação", "Escrita", "Leitura", "Limpeza", "Total"]:
        ax.plot(razao["tamanho_mb"], razao[op], marker="o", label=op, linewidth=2.5 if op == "Total" else 1.3)
    ax.axhline(1, color="gray", linestyle="--", linewidth=1)
    ax.set_xlabel("Tamanho do buffer (MB)")
    ax.set_ylabel("Razão Windows / Linux (medianas)")
    ax.set_title("Quantas vezes o Windows é mais lento que o Linux")
    ax.legend(ncol=2)
    fig.tight_layout()
    fig.savefig(GRAFICOS / "05_razao_windows_linux.png")
    plt.close(fig)


def grafico_serie_repeticoes(df):
    """Tempo total ao longo das repeticoes para 100 MB e 1000 MB (efeito de aquecimento / ruido)."""
    fig, eixos = plt.subplots(1, 2, figsize=(12, 4.2))
    for ax, tam in zip(eixos, [100, 1000]):
        for so in ["Windows", "Linux"]:
            sub = df[(df.so == so) & (df.tamanho_mb == tam)]
            ax.plot(sub.repeticao, sub.total_ms, color=CORES[so], label=so, linewidth=1)
        ax.set_title(f"{tam} MB")
        ax.set_xlabel("Repetição")
        ax.set_ylabel("Tempo total (ms)")
        ax.legend()
    fig.suptitle("Tempo total ao longo das repetições")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "06_serie_repeticoes.png")
    plt.close(fig)


# -------------------------------------------------------------------- main
def main():
    df = carregar()
    validar(df)
    estilo()

    geral = tabela_geral(df)
    geral.round(3).to_csv(TABELAS / "01_media_geral_por_operacao.csv", encoding="utf-8-sig")

    for op in OPERACOES:
        tabela_por_tamanho(df, op).to_csv(
            TABELAS / f"02_estatisticas_{op}.csv", index=False, encoding="utf-8-sig"
        )

    comp = tabela_comparativa_total(df)
    comp.to_csv(TABELAS / "03_comparativo_total_por_tamanho.csv", index=False, encoding="utf-8-sig")

    razao = tabela_razao_por_operacao(df)
    razao.to_csv(TABELAS / "04_razao_windows_linux_por_operacao.csv", index=False, encoding="utf-8-sig")

    tabela_primeira_repeticao(df).to_csv(
        TABELAS / "05_primeira_repeticao_vs_demais.csv", index=False, encoding="utf-8-sig"
    )
    tabela_outliers(df).to_csv(TABELAS / "06_outliers_total.csv", index=False, encoding="utf-8-sig")

    grafico_total_por_tamanho(df)
    grafico_operacoes_por_tamanho(df)
    grafico_boxplot_total(df)
    grafico_composicao(df)
    grafico_razao(razao)
    grafico_serie_repeticoes(df)

    pd.set_option("display.width", 140)
    print("=== Média geral por operação (ms) ===")
    print(geral.round(2))
    print("\n=== Comparativo do tempo total por tamanho ===")
    print(comp.to_string(index=False))
    print("\n=== Razão Windows/Linux (medianas) ===")
    print(razao.to_string(index=False))
    print(f"\nTabelas em: {TABELAS}\nGráficos em: {GRAFICOS}")


if __name__ == "__main__":
    main()
