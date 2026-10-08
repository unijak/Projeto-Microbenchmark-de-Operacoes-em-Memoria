#!/usr/bin/env python3
"""
Benchmark de operacoes de memoria/arquivo usando bytearray.

Operacoes medidas (tempo em nanossegundos, via time.perf_counter_ns):
  - ALOCACAO: criar um bytearray de N bytes
  - ESCRITA:  gravar o bytearray em um arquivo binario (with open)
  - LEITURA:  ler o arquivo de volta para um bytearray (with open)
  - LIMPEZA:  apagar o arquivo temporario e liberar o bytearray (del)

Parametros do teste:
  - Tamanhos de 100 MB ate 1000 MB, em passos de 100 MB (10 tamanhos: 100,200,...,1000)
  - Para cada tamanho, sao executados 100 testes (repeticoes)
  - Resultados gravados em um CSV, uma linha por (tamanho, repeticao)

Uso:
  python benchmark_memoria.py
"""

import os
import time
import csv

# ---------------------- Configuracoes ----------------------
MB = 1024 * 1024
TAMANHO_INICIAL_MB = 100
TAMANHO_FINAL_MB = 1000
PASSO_MB = 100
TESTES_POR_TAMANHO = 100

ARQUIVO_TEMP = "temp_benchmark.bin"
ARQUIVO_CSV = "resultados_benchmark.csv"


def alocar(tamanho_bytes: int):
    """Aloca um bytearray de 'tamanho_bytes' bytes. Retorna (bytearray, tempo_ns)."""
    inicio = time.perf_counter_ns()
    buffer = bytearray(tamanho_bytes)
    fim = time.perf_counter_ns()
    return buffer, (fim - inicio)


def escrever(caminho: str, buffer: bytearray):
    """Escreve o bytearray em disco. Retorna tempo_ns."""
    inicio = time.perf_counter_ns()
    with open(caminho, "wb") as f:
        f.write(buffer)
    fim = time.perf_counter_ns()
    return fim - inicio


def ler(caminho: str, tamanho_bytes: int):
    """Le o arquivo de volta para um bytearray. Retorna (bytearray, tempo_ns)."""
    inicio = time.perf_counter_ns()
    with open(caminho, "rb") as f:
        dados = bytearray(f.read())
    fim = time.perf_counter_ns()
    return dados, (fim - inicio)


def limpar(caminho: str, buffer: bytearray):
    """Remove o arquivo temporario e libera o bytearray. Retorna tempo_ns."""
    inicio = time.perf_counter_ns()
    if os.path.exists(caminho):
        os.remove(caminho)
    del buffer
    fim = time.perf_counter_ns()
    return fim - inicio


def executar_benchmark():
    tamanhos_mb = list(range(TAMANHO_INICIAL_MB, TAMANHO_FINAL_MB + 1, PASSO_MB))

    with open(ARQUIVO_CSV, "w", newline="") as csv_file:
        escritor = csv.writer(csv_file)
        escritor.writerow([
            "tamanho_mb",
            "repeticao",
            "alocacao_ns",
            "escrita_ns",
            "leitura_ns",
            "limpeza_ns",
            "total_ns",
        ])

        for tamanho_mb in tamanhos_mb:
            tamanho_bytes = tamanho_mb * MB
            print(f"Executando {TESTES_POR_TAMANHO} testes para {tamanho_mb} MB...")

            for repeticao in range(1, TESTES_POR_TAMANHO + 1):
                buffer, t_alocacao = alocar(tamanho_bytes)
                t_escrita = escrever(ARQUIVO_TEMP, buffer)
                buffer_lido, t_leitura = ler(ARQUIVO_TEMP, tamanho_bytes)
                t_limpeza = limpar(ARQUIVO_TEMP, buffer)
                del buffer_lido

                total_ns = t_alocacao + t_escrita + t_leitura + t_limpeza

                escritor.writerow([
                    tamanho_mb,
                    repeticao,
                    t_alocacao,
                    t_escrita,
                    t_leitura,
                    t_limpeza,
                    total_ns,
                ])

                if repeticao % 20 == 0:
                    print(f"  {tamanho_mb} MB - repeticao {repeticao}/{TESTES_POR_TAMANHO} concluida")

    print(f"\nBenchmark concluido. Resultados salvos em '{ARQUIVO_CSV}'.")


if __name__ == "__main__":
    executar_benchmark()
