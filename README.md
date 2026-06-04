# global-solution-2026-fund
lobal Solution 2026 — Monitoramento de Riscos Ambientais
# 🌊 Global Solution 2026 — FIAP
## Monitoramento de Riscos Ambientais com Árvores, Grafos e Algoritmos

**Disciplina:** Estruturas de Dados e Algoritmos  
**Curso:** TDSAT — FIAP | 1º Semestre de 2026  
**Professor:** André Marques

---

## 👥 Integrantes

| RM | Nome |
|---|---|
| RM 561870 | Bruna Sadi |
| RM 563671 | Dennis Generoso |
| RM 566309 | Francisco Nogueira |
| RM 566310 | Rhariel Permanhani |
| RM 563807 | Sara Marangon |

---

## 📋 Descrição do Projeto

Sistema computacional de triagem e roteamento de recursos de emergência para municípios brasileiros em situação de risco ambiental. O projeto instancia dois cenários reais:

- **Cenário A — Enchentes no Rio Grande do Sul (2024):** grafo baseado nos municípios afetados pelas enchentes de 2024, com Porto Alegre como hub central. O Dijkstra determina a rota de menor custo até cada município crítico; o Prim (MST) define a cobertura mínima de rotas para posicionamento de equipes.
- **Cenário B — Seca no MATOPIBA:** grafo de municípios do MATOPIBA (MA, TO, PI, BA) com índice de risco derivado de NDVI e precipitação INMET. A BST organiza os municípios por criticidade e o Dijkstra gera a agenda de atendimento a partir de Palmas (TO).

Alinhamento ODS: **ODS 2** (fome zero), **ODS 9** (infraestrutura), **ODS 11** (cidades resilientes), **ODS 13** (ação climática).

---

## 🗂️ Estrutura do Repositório

```
global-solution-2026/
│
├── main.py                        # Orquestrador principal — executa a pipeline completa
├── requirements.txt               # Dependências Python
│
├── src/
│   ├── data_structures.py         # Grafo, BST (Node + BinarySearchTree), FilaPrioridade
│   ├── brute_force.py             # Força Bruta com backtracking — baseline de validação
│   ├── greedy.py                  # Dijkstra e Prim com heapq — solução eficiente
│   ├── performance_monitor.py     # Benchmark: tempo (perf_counter) e memória (tracemalloc)
│   ├── visualizations.py          # Geração das 5 figuras obrigatórias (matplotlib/networkx)
│   ├── dataset_rs.py              # Dataset Cenário A — municípios RS, enchentes 2024
│   └── dataset_matopiba.py        # Dataset Cenário B — municípios MATOPIBA, seca 2023
│
├── data/
│   ├── raw/
│   │   ├── municipios_rs_enchentes_2024.csv      # Dados brutos RS
│   │   └── municipios_matopiba_seca_2023.csv     # Dados brutos MATOPIBA
│   └── processed/
│       ├── grafo_rs.json                         # Grafo RS serializado
│       ├── grafo_matopiba.json                   # Grafo MATOPIBA serializado
│       ├── bst_rs_inorder.json                   # BST RS em percurso in-order
│       └── benchmark_results.json               # Resultados dos benchmarks
│
├── figures/
│   ├── fig1_grafo_mst.png         # Grafo RS com arestas da MST destacadas
│   ├── fig2_bst.png               # BST de municípios por índice de risco
│   ├── fig3_desempenho.png        # Tempo de execução × N (FB vs Dijkstra)
│   ├── fig3b_explosao_combinatoria.png  # Crescimento de caminhos × N
│   ├── fig4_gap.png               # Gap de otimalidade FB vs Greedy Ingênuo
│   └── fig5_estruturas.png        # Tabela de estruturas de dados utilizadas
│
├── notebooks/
│   └── analise_resultados.ipynb   # Análise interativa com parâmetros ajustáveis
│
├── tests/
│   └── test_algorithms.py         # Testes unitários com pytest (BST, grafo, FB, Dijkstra, Prim)
│
└── report/
    └── relatorio_final.pdf        # Relatório técnico final (≤ 5 páginas)
```

---

## ⚙️ Instalação e Execução

### Pré-requisitos

- Python 3.10 ou superior

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Executar a pipeline completa

```bash
python main.py
```

A execução realiza, em sequência:
1. Construção do grafo (Cenário A — RS) e da BST
2. Demonstração das operações da BST (in-order, busca por intervalo, altura)
3. Força Bruta em subinstância N=8 com contagem de chamadas recursivas
4. Dijkstra no grafo completo + agenda de atendimento prioritário
5. Prim — Árvore Geradora Mínima (cobertura mínima de rotas)
6. Benchmark de desempenho: FB vs Dijkstra para N = 3 a 100
7. Geração das figuras obrigatórias em `./figures/`

### 3. Executar os testes unitários

```bash
pytest tests/ -v
```

Cobertura: BST (inserção, busca, remoção, in-order, altura), Grafo (BFS, DFS, subgrafo), Força Bruta (caminho mínimo, backtracking), Dijkstra (distâncias, predecessores, gap vs FB), Prim (MST, conexidade, custo).

### 4. Explorar o notebook interativo

```bash
jupyter notebook notebooks/analise_resultados.ipynb
```

---

## 🧠 Decisões de Projeto

### Por que lista de adjacência e não matriz?
Para grafos esparsos como redes viárias municipais (cada município tem em média 3–4 vizinhos), a lista de adjacência ocupa O(V+E) contra O(V²) da matriz — muito mais eficiente em memória e nas operações de travessia.

### Por que Dijkstra como algoritmo guloso principal?
Dijkstra garante gap de otimalidade = 0% para pesos positivos (provado por indução). Sua complexidade O((V+E) log V) é viável para os 478 municípios do RS, ao contrário da Força Bruta que se torna inviável para N > 12 (explosão O(N!)).

### Por que BST e não lista ordenada?
A BST permite busca por intervalo de risco em O(k + log N), onde k é o número de resultados. Uma lista ordenada exigiria O(k + log N) para localizar o início, mas a inserção custaria O(N) — ineficiente para atualizações frequentes dos dados de satélite.

---

## 📊 Resultados Principais

| Algoritmo | Gap Otim. | Complexidade | Viável até |
|---|---|---|---|
| Dijkstra (heap) | 0% | O((V+E) log V) | N = 100+ |
| Prim MST | 0% | O(E log V) | N = 100+ |
| Força Bruta c/ poda | 0% | O(N!) | N ≤ 12 |
| Greedy Ingênuo (sem heap) | ~55–231% | O(V²) | — |

---

## 📚 Referências

- CORMEN, T. et al. *Introduction to Algorithms*, 4ª ed. MIT Press, 2022. Caps. 22–25.
- SEDGEWICK, R.; WAYNE, K. *Algorithms*, 4ª ed. Addison-Wesley, 2011. Parte 4.
- SKIENA, S. *The Algorithm Design Manual*, 3ª ed. Springer, 2020.
- Defesa Civil RS. Boletins de Enchentes 2024. https://www.defesacivil.rs.gov.br
- NASA Earthdata. MODIS NDVI MYD13A3 2023. https://earthdata.nasa.gov
- INMET. Banco de Dados Meteorológicos (BDMEP) 2023. https://bdmep.inmet.gov.br
- IBGE. Malha Municipal e Dados Socioeconômicos 2024. https://ibge.gov.br/geociencias
- DNIT. Malha Viária Federal RS. https://dnit.gov.br