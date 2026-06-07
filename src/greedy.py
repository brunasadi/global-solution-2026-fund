"""
greedy.py — Algoritmo Guloso: Dijkstra + Prim
Global Solution 2026 | FIAP — Estruturas de Dados e Algoritmos
Cenário A: Rede de Resposta a Enchentes no Rio Grande do Sul

Algoritmo escolhido: Dijkstra (Caminho Mínimo de Fonte Única)
Justificativa: o problema central é determinar a ROTA DE MENOR CUSTO de
atendimento a partir de Porto Alegre (hub de recursos) até todos os
municípios afetados, priorizando os de maior risco (consultados via BST).
Dijkstra é exatamente o algoritmo guloso para esse cenário: a cada passo
escolhe localmente o vértice de menor custo acumulado ainda não finalizado
(decisão gulosa), garantindo o ótimo global para grafos com pesos positivos.

Também é implementado Prim para construir a MST (Árvore Geradora Mínima),
útil para o planejamento de cobertura mínima de todas as rotas de suprimento.

Complexidade Dijkstra com heap binário:
  - Tempo: O((V + E) log V)
  - Espaço: O(V)

Complexidade Prim com heap binário:
  - Tempo: O(E log V)
  - Espaço: O(V + E)
"""

from __future__ import annotations
import heapq
import time
import tracemalloc
from typing import List, Tuple, Dict, Optional, Set

from src.data_structures import Grafo, BinarySearchTree, FilaPrioridade
from src.data_structures import id_v, nome_v, risco_v


# ---------------------------------------------------------------------------
# RESULTADO DO ALGORITMO GULOSO
# ---------------------------------------------------------------------------

class ResultadoGreedy:
    def __init__(self):
        self.distancias: Dict[int, float] = {}       # id -> custo mín. acum.
        self.predecessores: Dict[int, Optional[int]] = {}  # id -> pred.
        self.arestas_relaxadas: int = 0
        self.insercoes_heap: int = 0
        self.tempo_ms: float = 0.0
        self.memoria_mb: float = 0.0
        # Para MST
        self.arestas_mst: List[Tuple[int, int, float]] = []
        self.custo_mst: float = 0.0

    def caminho_ate(self, destino_id: int) -> List[int]:
        """Reconstrói o caminho da origem até destino via predecessores."""
        caminho = []
        atual = destino_id
        while atual is not None:
            caminho.append(atual)
            atual = self.predecessores.get(atual)
        return list(reversed(caminho))

    def custo_ate(self, destino_id: int) -> float:
        return self.distancias.get(destino_id, float('inf'))

    def __repr__(self):
        return (f"ResultadoGreedy(vértices_alcançados={len(self.distancias)}, "
                f"arestas_relaxadas={self.arestas_relaxadas}, "
                f"insercoes_heap={self.insercoes_heap})")


# ---------------------------------------------------------------------------
# DIJKSTRA — Caminho Mínimo de Fonte Única
# ---------------------------------------------------------------------------

class Dijkstra:
    """
    Implementação de Dijkstra com heap binário (heapq).

    Decisão gulosa: a cada passo, extrai o vértice u com menor dist[u]
    do heap (escolha local ótima). Para grafos com pesos positivos, essa
    escolha garante que dist[u] seja o custo mínimo global ao finalizá-lo.

    Prova informal de corretude:
      - Invariante: ao extrair u do heap, dist[u] é mínimo e definitivo.
      - Razão: se houvesse caminho mais curto via outro vértice v ainda não
        finalizado, v teria custo ≥ dist[u], logo qualquer extensão seria
        ainda maior (pesos positivos). Contradição. ✓

    Integração com BST:
      - Antes de iniciar, consulta bst.alto_risco() para obter lista de
        municípios prioritários.
      - O resultado de Dijkstra pode ser filtrado apenas para esses destinos,
        gerando uma ordem de atendimento por urgência.
    """

    def __init__(self, grafo: Grafo, bst: Optional[BinarySearchTree] = None):
        self.grafo = grafo
        self.bst = bst

    def executar(self, origem_id: int) -> ResultadoGreedy:
        """
        Executa Dijkstra a partir de origem_id para TODOS os vértices.

        Retorna ResultadoGreedy com distâncias e predecessores.
        """
        resultado = ResultadoGreedy()

        tracemalloc.start()
        inicio = time.perf_counter()

        # Inicialização
        INF = float('inf')
        dist: Dict[int, float] = {v: INF for v in self.grafo.todos_ids()}
        pred: Dict[int, Optional[int]] = {v: None for v in self.grafo.todos_ids()}
        dist[origem_id] = 0.0
        finalizado: Set[int] = set()

        # Heap: (custo_acumulado, id_municipio)
        heap: List[Tuple[float, int]] = [(0.0, origem_id)]
        resultado.insercoes_heap += 1

        while heap:
            custo_u, u = heapq.heappop(heap)

            # Vértice já finalizado? Entrada obsoleta no heap — ignora
            if u in finalizado:
                continue
            finalizado.add(u)

            # Relaxamento das arestas saindo de u
            for v, peso in self.grafo.vizinhos(u):
                resultado.arestas_relaxadas += 1
                novo_custo = custo_u + peso
                if novo_custo < dist[v]:
                    dist[v] = novo_custo
                    pred[v] = u
                    heapq.heappush(heap, (novo_custo, v))
                    resultado.insercoes_heap += 1

        fim = time.perf_counter()
        mem_atual, mem_pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        resultado.distancias = dist
        resultado.predecessores = pred
        resultado.tempo_ms = (fim - inicio) * 1000
        resultado.memoria_mb = mem_pico / (1024 * 1024)

        return resultado

    def rota_prioritaria(self, origem_id: int,
                         limiar_risco: float = 0.70) -> List[Dict]:
        """
        Combina Dijkstra com consulta à BST para gerar ordem de atendimento.
        Retorna lista de municípios de alto risco ordenados por
        (risco_decrescente, custo_crescente) — prioritários recebem primeiro.

        Integração BST → Dijkstra:
          1. BST.buscar(limiar, 1.0) → municípios críticos (O(k + log N))
          2. Dijkstra determina custo de deslocamento até cada um (O((V+E)logV))
          3. Ordena por risco (decrescente) para compor a agenda de atendimento
        """
        res = self.executar(origem_id)

        criticos = []
        if self.bst:
            municipios_risco = self.bst.buscar(limiar_risco, 1.0)
        else:
            municipios_risco = [
                self.grafo.get_vertice(v) for v in self.grafo.todos_ids()
            ]

        for mun in municipios_risco:
            if mun is None:
                continue
            vid = id_v(mun)
            custo = res.distancias.get(vid, float('inf'))
            caminho = res.caminho_ate(vid)
            criticos.append({
                'id': vid,
                'nome': nome_v(mun),
                'risco': risco_v(mun),
                'custo_h': custo,
                'caminho': caminho,
                'caminho_nomes': [
                    self.grafo.get_vertice(c)[1] for c in caminho
                    if self.grafo.get_vertice(c)
                ],
            })

        # Ordena: maior risco primeiro; empate → menor custo
        criticos.sort(key=lambda x: (-x['risco'], x['custo_h']))
        return criticos, res


# ---------------------------------------------------------------------------
# PRIM — Árvore Geradora Mínima
# ---------------------------------------------------------------------------

class Prim:
    """
    Algoritmo de Prim para MST.

    Decisão gulosa: a cada passo adiciona a aresta de menor peso que
    conecta um vértice FORA da árvore a um vértice JÁ na árvore.
    Útil para o planejamento de cobertura mínima de rotas de suprimento.

    Complexidade: O(E log V) com heap binário.
    """

    def __init__(self, grafo: Grafo):
        self.grafo = grafo

    def executar(self, raiz_id: int) -> ResultadoGreedy:
        """
        Constrói a MST a partir de raiz_id.
        """
        resultado = ResultadoGreedy()

        tracemalloc.start()
        inicio = time.perf_counter()

        INF = float('inf')
        na_arvore: Set[int] = set()
        chave: Dict[int, float] = {v: INF for v in self.grafo.todos_ids()}
        pred: Dict[int, Optional[int]] = {v: None for v in self.grafo.todos_ids()}
        chave[raiz_id] = 0.0

        # heap: (custo_aresta, id_vertice)
        heap: List[Tuple[float, int]] = [(0.0, raiz_id)]
        resultado.insercoes_heap += 1

        while heap:
            custo, u = heapq.heappop(heap)
            if u in na_arvore:
                continue
            na_arvore.add(u)

            if pred[u] is not None:
                resultado.arestas_mst.append((pred[u], u, custo))
                resultado.custo_mst += custo

            for v, peso in self.grafo.vizinhos(u):
                resultado.arestas_relaxadas += 1
                if v not in na_arvore and peso < chave[v]:
                    chave[v] = peso
                    pred[v] = u
                    heapq.heappush(heap, (peso, v))
                    resultado.insercoes_heap += 1

        fim = time.perf_counter()
        mem_atual, mem_pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        resultado.distancias = chave
        resultado.predecessores = pred
        resultado.tempo_ms = (fim - inicio) * 1000
        resultado.memoria_mb = mem_pico / (1024 * 1024)

        return resultado


# ---------------------------------------------------------------------------
# EXECUÇÃO DIRETA
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from src.dataset_rs import construir_dataset_rs

    grafo, bst, _ = construir_dataset_rs()
    ORIGEM = 4314902  # Porto Alegre

    print("=" * 65)
    print("DIJKSTRA — Rota Prioritária de Atendimento (Enchentes RS)")
    print(f"Hub de origem: Porto Alegre")
    print("=" * 65)

    dijk = Dijkstra(grafo, bst)
    agenda, res_dijk = dijk.rota_prioritaria(ORIGEM, limiar_risco=0.65)

    print(f"\n{'Município':<25} {'Risco':>6} {'Custo(h)':>9}  Rota")
    print("-" * 75)
    for item in agenda:
        rota_str = " → ".join(item['caminho_nomes'])
        print(f"{item['nome']:<25} {item['risco']:>6.2f} "
              f"{item['custo_h']:>9.2f}  {rota_str}")

    print(f"\n Estatísticas Dijkstra:")
    print(f"   Arestas relaxadas:  {res_dijk.arestas_relaxadas}")
    print(f"   Inserções no heap:  {res_dijk.insercoes_heap}")
    print(f"   Tempo de execução:  {res_dijk.tempo_ms:.4f} ms")
    print(f"   Memória pico:       {res_dijk.memoria_mb:.4f} MB")

    print("\n" + "=" * 65)
    print("PRIM — Árvore Geradora Mínima (cobertura de rotas de suprimento)")
    print("=" * 65)

    prim = Prim(grafo)
    res_prim = prim.executar(ORIGEM)

    print(f"\n Custo total MST: {res_prim.custo_mst:.2f} h")
    print(f"\nArestas da MST:")
    for u, v, peso in res_prim.arestas_mst:
        nu = grafo.get_vertice(u)[1]
        nv = grafo.get_vertice(v)[1]
        print(f"   {nu:<25} ↔ {nv:<25}  {peso:.2f} h")
    print(f"\n Estatísticas Prim:")
    print(f"   Arestas relaxadas:  {res_prim.arestas_relaxadas}")
    print(f"   Inserções no heap:  {res_prim.insercoes_heap}")
    print(f"   Tempo de execução:  {res_prim.tempo_ms:.4f} ms")
    print(f"   Memória pico:       {res_prim.memoria_mb:.4f} MB")
