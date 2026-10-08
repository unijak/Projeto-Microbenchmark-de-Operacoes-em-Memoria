import pandas as pd
import matplotlib.pyplot as plt

dfLinux = pd.read_csv("/Users/juliakellerschafer/Downloads/resultados_benchmarkLinux.csv")
dfWindows = pd.read_csv("/Users/juliakellerschafer/Downloads/resultados_benchmark.csv")

print(dfLinux.columns)
print(dfWindows.columns)

# Windows x Linux
comparacao = pd.DataFrame({
    "Windows (ns)": [
        dfWindows["alocacao_ns"].mean(),
        dfWindows["escrita_ns"].mean(),
        dfWindows["leitura_ns"].mean(),
        dfWindows["limpeza_ns"].mean(),
        dfWindows["total_ns"].mean()
    ],
    
    "Linux (ns)": [
        dfLinux["alocacao_ns"].mean(),
        dfLinux["escrita_ns"].mean(),
        dfLinux["leitura_ns"].mean(),
        dfLinux["limpeza_ns"].mean(),
        dfLinux["total_ns"].mean()
    ]
}, index=[
    "Alocação",
    "Escrita",
    "Leitura",
    "Limpeza",
    "Total"
])
print(comparacao)

comparacao.plot(kind="bar", figsize=(10, 6))

plt.title("Comparação de Desempenho: Windows x Linux")
plt.xlabel("Etapa")
plt.ylabel("Tempo (ns)")
plt.xticks(rotation=0)
plt.legend(title="Sistema Operacional")
plt.tight_layout()
plt.show()