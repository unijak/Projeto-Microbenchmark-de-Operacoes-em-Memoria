# Microbenchmark de memória e arquivo: Windows × Linux

Experimento que mede, em Python, quatro operações sobre um `bytearray` de 100 MB a 1000 MB e compara o desempenho entre **Windows** e **Linux**. Os dois sistemas rodaram como máquinas virtuais no **VirtualBox**, no mesmo computador físico.

## O que é medido

Cada repetição executa, em sequência, as etapas abaixo e cronometra cada uma com `time.perf_counter_ns()` (resultado em nanossegundos):

| Etapa | O que mede |
|---|---|
| Alocação | criar um `bytearray` de N bytes |
| Escrita | gravar o `bytearray` em um arquivo binário (`with open(..., "wb")`) |
| Leitura | ler o arquivo de volta para um `bytearray` (`with open(..., "rb")`) |
| Limpeza | apagar o arquivo temporário e liberar o buffer (`del`) |

- Tamanhos: 100, 200, ..., 1000 MB (10 tamanhos, `1 MB = 1024 × 1024` bytes).
- 100 repetições por tamanho, em cada sistema: 1000 linhas por CSV.
- O `total_ns` é a soma das quatro etapas.

## Estrutura do repositório

```
.
├── benchmark_memoria.py        # código-fonte do microbenchmark
├── benchmark.py                # comparação Windows x Linux e gráfico de barras (Figura 1 do resumo)
├── analise_benchmark.py        # análise: estatísticas, tabelas e gráficos
├── requirements.txt            # dependências da análise
├── dados/
│   ├── resultados_windows.csv  # coletado no Windows
│   └── resultados_linux.csv    # coletado no Linux
├── tabelas/                    # tabelas geradas pela análise (CSV)
├── graficos/                   # gráficos gerados pela análise (PNG)
├── resumo_expandido/           # resumo expandido (.docx) e prévia em PDF
└── README.md
```

> Os CSVs foram renomeados em relação à coleta original: `resultados_benchmark.csv` virou `resultados_windows.csv` e `resultados_benchmarkLinux.csv` virou `resultados_linux.csv`. O conteúdo é idêntico.

## Protocolo do experimento

| Item | Definição do grupo |
|---|---|
| Integrantes | Arthur Merljak, Julia Schäfer e Lariane Mihlbeier |
| Responsável pelo protocolo | Arthur Merljak, Julia Schäfer e Lariane Mihlbeier |
| Responsável pela execução | Julia Schäfer |
| Responsável pela validação | Lariane Mihlbeier |
| Responsável pelo GitHub | Arthur Merljak |
| Repositório | `git@github.com:unijak/Projeto-Microbenchmark-de-Operacoes-em-Memoria.git` |
| Sistemas | Windows e Linux |
| Operações e ordem | alocar → escrever → ler → liberar |
| Blocos | 100 a 1000 MB, em passos de 100 MB |
| Repetições | 100 por tamanho |
| Unidade e formato | milissegundos (a coleta grava ns), CSV |
| Variável independente | sistema operacional |
| Variável dependente | tempo de resposta |
| Variável controlada | número de repetições |

Condições mantidas constantes: mesmo hardware físico, mesmo código, mesma versão do Python, mesmos blocos, mesmo número de repetições, aplicações desnecessárias fechadas e um único ambiente em execução por vez. O grupo previu verificar o código e a versão do Python por captura ou gravação de tela antes de cada coleta.

## Ambiente do experimento

**Modalidade:** duas máquinas virtuais no mesmo computador. O grupo considerou a opção mais viável porque os integrantes têm dispositivos diferentes e não quiseram instalar dual boot.

### Hardware físico (comum às duas máquinas virtuais)

| Item | Configuração |
|---|---|
| Processador | Apple M5 |
| Memória RAM | 16 GB |
| Armazenamento | 512 GB |
| Sistema hospedeiro | macOS |

### Máquinas virtuais

| Item | Windows | Linux |
|---|---|---|
| Sistema operacional | Windows 11 | Ubuntu (versão: `[PREENCHER]`) |
| Arquitetura | 64 bits (`[CONFERIR]`, ver nota) | 64 bits |
| Versão do Python | 3.14.7 | 3.14.7 |
| vCPUs | 2 | 2 |
| RAM atribuída | 8 GB | 8 GB |
| VirtualBox | 7.2.18 | 7.2.18 |
| Disco virtual (tipo e tamanho) | `[PREENCHER]` | `[PREENCHER]` |
| Sistema de arquivos | `[PREENCHER]` (ex.: NTFS) | `[PREENCHER]` (ex.: ext4) |

> **Nota sobre a arquitetura:** o protocolo registra "x86-64 / AMD64" para o Windows, mas o processador do hospedeiro (Apple M5) é ARM64. Até onde sei, o VirtualBox em Macs com Apple Silicon executa apenas sistemas convidados ARM64. Confirme a arquitetura real das duas máquinas virtuais (`uname -m` no Linux, `echo %PROCESSOR_ARCHITECTURE%` no Windows) antes de publicar.

Para consultar os dados que faltam: `lsb_release -a`, `lsblk -f` (Linux) e `Get-ComputerInfo` (PowerShell, Windows).

## Como reproduzir

### 1. Requisitos

- Python 3.9 ou superior
- Espaço livre em disco de pelo menos **1 GB** (o benchmark grava um arquivo temporário de até 1000 MB)
- RAM livre suficiente para manter o buffer de até 1000 MB, mais a cópia lida do disco, ao mesmo tempo

O benchmark usa apenas a biblioteca padrão. Apenas a análise precisa de pacotes externos.

### 2. Executar o benchmark

Em **cada** sistema operacional, a partir da pasta do projeto:

```bash
# Linux
python3 benchmark_memoria.py

# Windows
python benchmark_memoria.py
```

Isso gera `resultados_benchmark.csv` na pasta atual (1000 linhas) e leva alguns minutos. Depois, copie o arquivo para `dados/` com o nome do sistema:

```bash
# no Linux
cp resultados_benchmark.csv dados/resultados_linux.csv

# no Windows (PowerShell)
Copy-Item resultados_benchmark.csv dados\resultados_windows.csv
```

Para que a comparação seja justa, mantenha as mesmas condições nas duas coletas: mesma configuração de VM, nenhum outro programa pesado aberto e o mesmo número de repetições.

### 3. Executar a análise

Dois scripts usam os CSVs de `dados/`:

- `analise_benchmark.py` gera todas as tabelas e gráficos (instruções abaixo).
- `benchmark.py` gera o gráfico de barras com a média por operação (Figura 1 do resumo expandido). Ele lê os CSVs por caminhos absolutos da máquina de quem o escreveu (`/Users/juliakellerschafer/Downloads/...`); troque-os por `dados/resultados_windows.csv` e `dados/resultados_linux.csv` antes de rodar.


```bash
pip install -r requirements.txt
python analise_benchmark.py
```

O script valida os dados (sem valores ausentes, 100 repetições por tamanho e sistema, `total_ns` igual à soma das etapas), imprime um resumo no terminal e grava as tabelas em `tabelas/` e os gráficos em `graficos/`.

## Resultados

### Média geral por operação (todas as 1000 repetições)

| Operação | Windows (ms) | Linux (ms) | Razão Win/Lin |
|---|---:|---:|---:|
| Alocação | 304,04 | 64,98 | 4,68 |
| Escrita | 563,51 | 63,96 | 8,81 |
| Leitura | 817,87 | 191,31 | 4,27 |
| Limpeza | 35,00 | 7,73 | 4,53 |
| **Total** | **1720,42** | **327,99** | **5,25** |

### Tempo total por tamanho (mediana, em ms)

| Tamanho (MB) | Windows | Linux | Razão Win/Lin |
|---:|---:|---:|---:|
| 100 | 240,7 | 49,2 | 4,89 |
| 200 | 495,9 | 98,6 | 5,03 |
| 300 | 751,5 | 148,0 | 5,08 |
| 400 | 983,2 | 196,8 | 5,00 |
| 500 | 1240,0 | 245,6 | 5,05 |
| 600 | 1684,3 | 300,5 | 5,60 |
| 700 | 2217,7 | 356,1 | 6,23 |
| 800 | 2683,0 | 452,2 | 5,93 |
| 900 | 3113,9 | 641,3 | 4,86 |
| 1000 | 3521,5 | 726,8 | 4,85 |

### Observações

- **O Linux foi mais rápido em todas as operações e em todos os tamanhos**, entre 4,8 e 6,2 vezes no tempo total. As distribuições não se sobrepõem: o teste de Mann-Whitney dá p ≈ 2,6 × 10⁻³⁴ em todos os tamanhos, que é o menor valor possível com 100 contra 100 amostras quando os grupos estão totalmente separados.
- **A escrita é a etapa com maior diferença** (de 7,3 a 10,5 vezes, conforme o tamanho). Até 500 MB, o tempo cresce de forma aproximadamente linear com o tamanho nos dois sistemas.
- **A partir de 600 MB o comportamento muda.** No Windows, a razão sobe até 6,2 em 700 MB; no Linux, os tempos passam a variar muito mais, principalmente em 900 e 1000 MB (veja `graficos/03_boxplot_total.png` e a coluna `cv_%` em `tabelas/02_estatisticas_total.csv`). Uma hipótese compatível com isso é pressão de memória na VM (cache de páginas, swap), mas os dados deste experimento não permitem confirmá-la.
- **A primeira repetição de cada tamanho costuma ser mais lenta**, em especial no Linux (de 1,3 a 2,1 vezes a mediana das demais; veja `tabelas/05_primeira_repeticao_vs_demais.csv`). Isso é coerente com efeito de execução "a frio" (cache de arquivos ainda vazio). As análises usam todas as repetições, como no script original; por isso a mediana é uma medida mais robusta que a média neste conjunto.
- **Há outliers nos dois sistemas** (`tabelas/06_outliers_total.csv`), que puxam a média para cima.

### Limitações

- O experimento mede **sistema operacional convidado + configuração da VM**, não o sistema operacional isoladamente. Diferenças de driver de disco, de configuração do disco virtual, de antivírus (por exemplo, o Windows Defender no Windows) e de Guest Additions podem explicar parte da diferença. Para atribuir o efeito ao sistema operacional, seria preciso repetir o teste em máquina física ou comprovar que as duas VMs têm configuração equivalente.
- Cada máquina foi medida em uma única sessão, o que não separa variação entre execuções de variação entre sistemas.
- O benchmark mede o tempo de uma chamada de escrita e de leitura via Python. O sistema operacional pode manter os dados no cache de páginas, de modo que "escrita" e "leitura" nem sempre refletem acesso físico ao disco.

## Arquivos gerados

**Tabelas** (`tabelas/`)

| Arquivo | Conteúdo |
|---|---|
| `01_media_geral_por_operacao.csv` | média geral por operação, Windows × Linux |
| `02_estatisticas_<operação>.csv` | média, mediana, desvio-padrão, mínimo, máximo e CV por tamanho e sistema (uma tabela por operação e uma para o total) |
| `03_comparativo_total_por_tamanho.csv` | tempo total por tamanho, razões e p-valor do teste de Mann-Whitney |
| `04_razao_windows_linux_por_operacao.csv` | razão das medianas Windows/Linux por operação e tamanho |
| `05_primeira_repeticao_vs_demais.csv` | repetição 1 comparada à mediana das repetições 2 a 100 |
| `06_outliers_total.csv` | contagem de outliers (critério de Tukey, 1,5 × IQR) |

**Gráficos** (`graficos/`)

| Arquivo | Conteúdo |
|---|---|
| `01_total_por_tamanho.png` | mediana e intervalo interquartil do tempo total por tamanho |
| `02_operacoes_por_tamanho.png` | mediana de cada operação por tamanho |
| `03_boxplot_total.png` | distribuição do tempo total por tamanho |
| `04_composicao_tempo.png` | composição do tempo total por operação |
| `05_razao_windows_linux.png` | razão Windows/Linux por tamanho e operação |
| `06_serie_repeticoes.png` | tempo total ao longo das repetições (100 MB e 1000 MB) |
