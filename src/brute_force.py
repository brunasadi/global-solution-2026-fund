"""
brute_force.py — Força Bruta por Enumeração Exaustiva
Global Solution 2026 | FIAP — Estruturas de Dados e Algoritmos
Cenário A: Rede de Resposta a Enchentes no Rio Grande do Sul
 
Papel no sistema:
  - Enumera TODOS os caminhos simples entre origem e destino em instâncias
    pequenas (N ≤ 12), usando recursão com backtracking.
  - Serve como oráculo de validação: qualquer instância pequena pode ter seu
    resultado comparado com o Dijkstra para calcular o gap de otimalidade.
  - Demonstra empiricamente a explosão combinatória de O(N!) no pior caso.
 
Complexidade:
  - Tempo: O(N!) no pior caso (grafo completo, todos caminhos hamiltonianos)
  - Espaço: O(N) para a pilha recursiva + O(P) para armazenar caminhos
"""
 
from __future__ import annotations
import time
import tracemalloc
from typing import List, Tuple, Optional, Dict
 
from src.data_structures import Grafo, id_v, nome_v, risco_v
 
 
# ---------------------------------------------------------------------------
# RESULTADO DA FORÇA BRUTA
# ---------------------------------------------------------------------------
 
class ResultadoFB:
    def __init__(self):
        self.caminho_otimo: List[int] = []
        self.custo_otimo: float = float('inf')
        self.todos_caminhos: List[Tuple[List[int], float]] = []
        self.num_chamadas_rec: int = 0
        self.num_caminhos_avaliados: int = 0
        self.tempo_ms: float = 0.0
        self.memoria_mb: float = 0.0
 
    def __repr__(self):
        return (f"ResultadoFB(custo_ótimo={self.custo_otimo:.3f}, "
                f"caminhos={self.num_caminhos_avaliados}, "
                f"chamadas_rec={self.num_chamadas_rec})")
 
 
# ---------------------------------------------------------------------------
# FORÇA BRUTA — BUSCA EXAUSTIVA
# ---------------------------------------------------------------------------
 
class ForcaBruta:
    """
    Enumeração completa de todos os caminhos simples no grafo.
 
    Algoritmo:
      1. A partir da origem, explora recursivamente todos os vizinhos.
      2. Mantém conjunto 'visitados' para evitar ciclos (backtracking).
      3. Ao atingir o destino, registra o caminho e seu custo total.
      4. Após enumerar tudo, seleciona o caminho de menor custo.
    """
 
    def __init__(self, grafo: Grafo):
        self.grafo = grafo
 
    def encontrar_caminho_minimo(
        self,
        origem_id: int,
        destino_id: int,
        guardar_todos: bool = True
    ) -> ResultadoFB:
        """
        Encontra o caminho de menor custo entre origem e destino.
 
        Parâmetros
        ----------
        origem_id    : ID do município de origem
        destino_id   : ID do município de destino
        guardar_todos: se True, registra todos os caminhos (memória extra)
 
        Retorno
        -------
        ResultadoFB com o caminho ótimo e estatísticas
        """
        resultado = ResultadoFB()
 
        tracemalloc.start()
        inicio = time.perf_counter()
 
        # Estado mutável compartilhado com a recursão (via lista)
        _counter = [0, 0]  # [chamadas_rec, caminhos_avaliados]
 
        caminho_atual: List[int] = [origem_id]
        visitados: set = {origem_id}
 
        def _backtrack(no_atual: int, custo_acum: float) -> None:
            _counter[0] += 1  # conta chamada recursiva
 
            if no_atual == destino_id:
                _counter[1] += 1  # conta caminho completo avaliado
                if custo_acum < resultado.custo_otimo:
                    resultado.custo_otimo = custo_acum
                    resultado.caminho_otimo = list(caminho_atual)
                if guardar_todos:
                    resultado.todos_caminhos.append(
                        (list(caminho_atual), custo_acum)
                    )
                return
 
            # Poda: se já superou o melhor custo conhecido, abandona
            if custo_acum >= resultado.custo_otimo:
                return
 
            for vizinho, peso in self.grafo.vizinhos(no_atual):
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    caminho_atual.append(vizinho)
                    _backtrack(vizinho, custo_acum + peso)
                    # backtrack: desfaz a escolha
                    caminho_atual.pop()
                    visitados.remove(vizinho)
 
        _backtrack(origem_id, 0.0)
 
        fim = time.perf_counter()
        mem_atual, mem_pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
 
        resultado.num_chamadas_rec = _counter[0]
        resultado.num_caminhos_avaliados = _counter[1]
        resultado.tempo_ms = (fim - inicio) * 1000
        resultado.memoria_mb = mem_pico / (1024 * 1024)
 
        return resultado
 
    def encontrar_arvore_geradora_minima_exaustiva(
        self, ids_vertices: Optional[List[int]] = None
    ) -> ResultadoFB:
        """
        Para grafos muito pequenos (N ≤ 10), enumera todas as árvores
        geradoras possíveis e seleciona a de menor custo total.
        Complexidade: O(N^(N-2)) pelo teorema de Cayley.
        """
        resultado = ResultadoFB()
        if ids_vertices is None:
            ids_vertices = self.grafo.todos_ids()
 
        n = len(ids_vertices)
        if n > 10:
            raise ValueError(
                f"MST exaustiva inviável para N={n}. Use N ≤ 10."
            )
 
        tracemalloc.start()
        inicio = time.perf_counter()
        _counter = [0, 0]
 
        # Enumera subconjuntos de (N-1) arestas que formam árvore geradora
        from itertools import combinations
 
        # Coleta todas as arestas do subgrafo
        arestas = []
        id_set = set(ids_vertices)
        vistos = set()
        for uid in ids_vertices:
            for viz, peso in self.grafo.vizinhos(uid):
                if viz in id_set:
                    chave = (min(uid, viz), max(uid, viz))
                    if chave not in vistos:
                        arestas.append((uid, viz, peso))
                        vistos.add(chave)
 
        def forma_arvore_geradora(subset_arestas):
            """Verifica se N-1 arestas formam uma árvore geradora (conexa, acíclica)."""
            _counter[0] += 1
            if len(subset_arestas) != n - 1:
                return False
            # Union-Find simplificado
            pai = {v: v for v in ids_vertices}
            def find(x):
                while pai[x] != x:
                    pai[x] = pai[pai[x]]
                    x = pai[x]
                return x
            def union(x, y):
                rx, ry = find(x), find(y)
                if rx == ry:
                    return False  # ciclo!
                pai[rx] = ry
                return True
 
            for u, v, _ in subset_arestas:
                if not union(u, v):
                    return False
            # Verifica conexidade
            raiz = find(ids_vertices[0])
            return all(find(v) == raiz for v in ids_vertices)
 
        melhor_custo = float('inf')
        melhor_arvore = []
 
        for subset in combinations(range(len(arestas)), n - 1):
            selecionadas = [arestas[i] for i in subset]
            if forma_arvore_geradora(selecionadas):
                _counter[1] += 1
                custo = sum(e[2] for e in selecionadas)
                if custo < melhor_custo:
                    melhor_custo = custo
                    melhor_arvore = selecionadas
 
        fim = time.perf_counter()
        mem_atual, mem_pico = tracemalloc.get_traced_memory()
        tracemalloc.stop()
 
        resultado.custo_otimo = melhor_custo
        resultado.caminho_otimo = [(e[0], e[1]) for e in melhor_arvore]
        resultado.num_chamadas_rec = _counter[0]
        resultado.num_caminhos_avaliados = _counter[1]
        resultado.tempo_ms = (fim - inicio) * 1000
        resultado.memoria_mb = mem_pico / (1024 * 1024)
 
        return resultado
 
 
# ---------------------------------------------------------------------------
# CONTAGEM EMPÍRICA DE CRESCIMENTO COMBINATÓRIO
# ---------------------------------------------------------------------------
 
def contar_caminhos_por_n(grafo: Grafo, origem_id: int,
                           ns: List[int]) -> Dict[int, Dict]:
    """
    Para cada N em ns, mede a quantidade de caminhos e tempo de execução.
    Usa subgrafos crescentes a partir da origem (BFS para obter N vértices).
 
    Retorna dict: {N: {'caminhos': int, 'chamadas': int, 'tempo_ms': float}}
    """
    from collections import deque
 
    resultados = {}
 
    for n in ns:
        if n > 12:
            # Para N > 12, não executa FB para evitar travar
            resultados[n] = {
                'caminhos': None,
                'chamadas': None,
                'tempo_ms': None,
                'nota': 'N > 12: FB inviável'
            }
            continue
 
        # BFS para coletar exatamente N vértices conectados à origem
        fila = deque([origem_id])
        visitados = [origem_id]
        while fila and len(visitados) < n:
            atual = fila.popleft()
            for viz, _ in grafo.vizinhos(atual):
                if viz not in visitados and len(visitados) < n:
                    visitados.append(viz)
                    fila.append(viz)
 
        if len(visitados) < n:
            resultados[n] = {
                'caminhos': None,
                'chamadas': None,
                'tempo_ms': None,
                'nota': f'Grafo tem apenas {len(visitados)} vértices acessíveis'
            }
            continue
 
        sub = grafo.subgrafo(visitados)
        fb = ForcaBruta(sub)
        destino = visitados[-1]
 
        res = fb.encontrar_caminho_minimo(
            origem_id, destino, guardar_todos=False
        )
        resultados[n] = {
            'caminhos': res.num_caminhos_avaliados,
            'chamadas': res.num_chamadas_rec,
            'tempo_ms': res.tempo_ms,
            'nota': 'OK'
        }
 
    return resultados
 
 
# ---------------------------------------------------------------------------
# EXECUÇÃO DIRETA
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from src.dataset_rs import construir_dataset_rs
 
    grafo, bst, _ = construir_dataset_rs()
 
    ORIGEM  = 4314902  # Porto Alegre
    DESTINO = 4311403  # Cruzeiro do Sul RS
 
    print("=" * 60)
    print("FORÇA BRUTA — Caminho Mínimo")
    print(f"Origem:  Porto Alegre  (id={ORIGEM})")
    print(f"Destino: Cruzeiro do Sul (id={DESTINO})")
    print("=" * 60)
 
    fb = ForcaBruta(grafo)
    res = fb.encontrar_caminho_minimo(ORIGEM, DESTINO)
 
    print(f"\n Custo ótimo:       {res.custo_otimo:.3f} h")
    print(f" Caminho ótimo:     "
          f"{' → '.join(grafo.get_vertice(v)[1] for v in res.caminho_otimo)}")
    print(f" Chamadas rec.:     {res.num_chamadas_rec:,}")
    print(f"  Caminhos avaliados: {res.num_caminhos_avaliados:,}")
    print(f"  Tempo:             {res.tempo_ms:.3f} ms")
    print(f" Memória pico:      {res.memoria_mb:.4f} MB")
 
    print("\n Crescimento combinatório por N:")
    ns = [3, 4, 5, 6, 7, 8, 9, 10, 12]
    stats = contar_caminhos_por_n(grafo, ORIGEM, ns)
    print(f"  {'N':>4}  {'Caminhos':>10}  {'Chamadas':>12}  {'Tempo(ms)':>10}")
    for n, d in stats.items():
        if d['nota'] == 'OK':
            print(f"  {n:>4}  {d['caminhos']:>10,}  {d['chamadas']:>12,}  "
                  f"{d['tempo_ms']:>10.3f}")
        else:
            print(f"  {n:>4}  {'—':>10}  {'—':>12}  {'inviável':>10}  ({d['nota']})")