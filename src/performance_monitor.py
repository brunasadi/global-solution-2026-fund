"""
performance_monitor.py — Monitoramento de Desempenho
Global Solution 2026 | FIAP — Estruturas de Dados e Algoritmos

Mede e compara Força Bruta vs Dijkstra (Guloso) para instâncias de tamanho
N = 3, 4, 5, 6, 7, 8, 9, 10, 12.

Métricas registradas por instância:
  - Tempo de execução (ms) via time.perf_counter()
  - Memória alocada (MB) via tracemalloc
  - Número de operações elementares (chamadas rec. / arestas relaxadas)
  - Gap de otimalidade: |custo_FB - custo_Greedy| / custo_FB * 100%
"""

from __future__ import annotations
import time
import tracemalloc
import random
import json
from collections import deque
from typing import Dict, List, Tuple, Any

from src.data_structures import Grafo, BinarySearchTree, criar_vertice
from src.brute_force import ForcaBruta
from src.greedy import Dijkstra


# ---------------------------------------------------------------------------
# GREEDY INGÊNUO — para gerar gap real de comparação
# ---------------------------------------------------------------------------

def dijkstra_ingenuo(grafo: Grafo, origem_id: int, destino_id: int) -> float:
    """
    Greedy Ingênuo (Nearest Neighbor): a cada passo, vai para o vizinho
    de MENOR PESO da aresta atual — sem manter acumulado global.
    Não usa heap nem rastreamento de distâncias mínimas globais.

    Esta abordagem é SUBÓTIMA: escolhe o menor salto local sem considerar
    o custo total do caminho, podendo cair em becos sem saída ou tomar
    rotas mais longas. Serve para demonstrar que 'ganância local' sem
    estrutura adequada não garante ótimo global.

    Complexidade: O(V * grau_max) — sem heap
    """
    visitados = {origem_id}
    atual = origem_id
    custo_total = 0.0
    max_passos = grafo.num_vertices() + 1

    for _ in range(max_passos):
        if atual == destino_id:
            return custo_total
        vizinhos_nao_visit = [
            (viz, peso) for viz, peso in grafo.vizinhos(atual)
            if viz not in visitados
        ]
        if not vizinhos_nao_visit:
            return float('inf')  # beco sem saída
        # Decisão gulosa ingênua: menor aresta LOCAL (não custo acumulado)
        proximo, peso = min(vizinhos_nao_visit, key=lambda x: x[1])
        visitados.add(proximo)
        custo_total += peso
        atual = proximo

    return float('inf')


# ---------------------------------------------------------------------------
# GERADOR DE GRAFO SINTÉTICO PARA BENCHMARKS
# ---------------------------------------------------------------------------

def gerar_grafo_sintetico(n: int, seed: int = 42) -> Tuple[Grafo, int, int]:
    """
    Gera um grafo conexo sintético com N vértices e arestas aleatórias.
    Garante conexidade via spanning tree aleatória + arestas extras.

    Retorna: (grafo, origem_id, destino_id)
    """
    random.seed(seed)
    g = Grafo()
    ids = list(range(1, n + 1))

    for i in ids:
        risco = round(random.uniform(0.3, 0.95), 3)
        v = criar_vertice(i, f"Mun_{i}", risco, random.uniform(100, 500),
                          random.randint(5000, 500000))
        g.adicionar_vertice(v)

    # Spanning tree aleatória para garantir conexidade
    random.shuffle(ids)
    for i in range(1, n):
        peso = round(random.uniform(0.2, 3.5), 2)
        g.adicionar_aresta(ids[i - 1], ids[i], peso)

    # Arestas extras (densidade ~1.5x)
    n_extras = max(0, n // 2)
    for _ in range(n_extras):
        u = random.choice(ids)
        v = random.choice(ids)
        if u != v:
            peso = round(random.uniform(0.2, 3.5), 2)
            g.adicionar_aresta(u, v, peso)

    return g, ids[0], ids[-1]


# ---------------------------------------------------------------------------
# BENCHMARK INDIVIDUAL
# ---------------------------------------------------------------------------

def benchmark_par(n: int) -> Dict[str, Any]:
    """
    Executa FB e Dijkstra para uma instância de tamanho N.
    Retorna dict com todas as métricas.
    """
    grafo, origem, destino = gerar_grafo_sintetico(n)
    resultado = {"n": n}

    # ---- Força Bruta -------------------------------------------------------
    fb = ForcaBruta(grafo)
    if n <= 12:
        res_fb = fb.encontrar_caminho_minimo(origem, destino, guardar_todos=False)
        resultado["fb_tempo_ms"]   = res_fb.tempo_ms
        resultado["fb_memoria_mb"] = res_fb.memoria_mb
        resultado["fb_chamadas"]   = res_fb.num_chamadas_rec
        resultado["fb_caminhos"]   = res_fb.num_caminhos_avaliados
        resultado["fb_custo"]      = res_fb.custo_otimo
    else:
        resultado["fb_tempo_ms"]   = None
        resultado["fb_memoria_mb"] = None
        resultado["fb_chamadas"]   = None
        resultado["fb_caminhos"]   = None
        resultado["fb_custo"]      = None

    # ---- Dijkstra (Guloso) -------------------------------------------------
    bst = BinarySearchTree()
    for vid in grafo.todos_ids():
        bst.inserir(grafo.get_vertice(vid))

    dijk = Dijkstra(grafo, bst)
    res_dijk = dijk.executar(origem)

    resultado["dijk_tempo_ms"]   = res_dijk.tempo_ms
    resultado["dijk_memoria_mb"] = res_dijk.memoria_mb
    resultado["dijk_relaxamentos"] = res_dijk.arestas_relaxadas
    resultado["dijk_heap_ops"]   = res_dijk.insercoes_heap
    resultado["dijk_custo"]      = res_dijk.distancias.get(destino, float('inf'))

    # ---- Gap de otimalidade ------------------------------------------------
    if (resultado["fb_custo"] is not None and
            resultado["fb_custo"] < float('inf') and
            resultado["dijk_custo"] < float('inf') and
            resultado["fb_custo"] > 0):
        gap = abs(resultado["fb_custo"] - resultado["dijk_custo"])
        gap_pct = (gap / resultado["fb_custo"]) * 100
        resultado["gap_pct"] = round(gap_pct, 4)
    else:
        resultado["gap_pct"] = None

    # ---- Greedy Ingênuo (para demonstrar gap real) -------------------------
    custo_ingenuo = dijkstra_ingenuo(grafo, origem, destino)
    resultado["ingenuo_custo"] = custo_ingenuo if custo_ingenuo < float('inf') else None
    if (resultado["fb_custo"] is not None and
            resultado["fb_custo"] < float('inf') and
            custo_ingenuo < float('inf') and
            resultado["fb_custo"] > 0):
        gap_ing = abs(resultado["fb_custo"] - custo_ingenuo) / resultado["fb_custo"] * 100
        resultado["gap_ingenuo_pct"] = round(gap_ing, 2)
    else:
        resultado["gap_ingenuo_pct"] = None

    return resultado


# ---------------------------------------------------------------------------
# SUITE COMPLETA DE BENCHMARKS
# ---------------------------------------------------------------------------

NS_BENCHMARK = [3, 4, 5, 6, 7, 8, 9, 10, 12, 20, 50, 100]


def executar_benchmarks(ns: List[int] = None) -> List[Dict]:
    """Executa benchmarks para todos os tamanhos em ns."""
    if ns is None:
        ns = NS_BENCHMARK

    resultados = []
    print(f"\n{'N':>5} | {'FB Tempo(ms)':>13} | {'Dijk Tempo(ms)':>14} | "
          f"{'FB Chamadas':>12} | {'Dijk Relax.':>11} | {'Gap%':>8}")
    print("-" * 75)

    for n in ns:
        r = benchmark_par(n)
        resultados.append(r)

        fb_t  = f"{r['fb_tempo_ms']:.3f}"  if r['fb_tempo_ms']  else "inviável"
        dijk_t = f"{r['dijk_tempo_ms']:.3f}"
        fb_c  = f"{r['fb_chamadas']:,}"    if r['fb_chamadas']  else "—"
        dijk_r = f"{r['dijk_relaxamentos']:,}"
        gap   = f"{r['gap_pct']:.2f}%"     if r['gap_pct'] is not None else "—"

        print(f"{n:>5} | {fb_t:>13} | {dijk_t:>14} | "
              f"{fb_c:>12} | {dijk_r:>11} | {gap:>8}")

    return resultados


# ---------------------------------------------------------------------------
# ANÁLISE DO PONTO DE CRUZAMENTO
# ---------------------------------------------------------------------------

def ponto_cruzamento(resultados: List[Dict]) -> int:
    """
    Identifica N a partir do qual FB supera Dijkstra em tempo.
    Retorna o menor N onde FB_tempo > 10 * Dijkstra_tempo.
    """
    for r in resultados:
        if r['fb_tempo_ms'] is not None and r['fb_tempo_ms'] > 0:
            ratio = r['fb_tempo_ms'] / max(r['dijk_tempo_ms'], 0.001)
            if ratio > 10:
                return r['n']
    return -1  # não encontrado no range testado


# ---------------------------------------------------------------------------
# EXECUÇÃO DIRETA
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 75)
    print("MONITOR DE DESEMPENHO — Global Solution 2026")
    print("Força Bruta vs. Dijkstra (Guloso)")
    print("=" * 75)

    resultados = executar_benchmarks()

    n_critico = ponto_cruzamento(resultados)
    if n_critico > 0:
        print(f"\n  Ponto de cruzamento: Força Bruta se torna ~10x mais lenta "
              f"que Dijkstra a partir de N={n_critico}")
    else:
        print("\n  FB inviável para N > 12 (não executa na suite de benchmark)")

    # Salva resultados em JSON
    import os
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print("\n Resultados salvos em data/processed/benchmark_results.json")