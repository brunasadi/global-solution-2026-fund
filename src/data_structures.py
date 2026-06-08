"""
data_structures.py — Estruturas de Dados Fundamentais
Global Solution 2026 | FIAP — Estruturas de Dados e Algoritmos
Cenário A: Rede de Resposta a Enchentes no Rio Grande do Sul

Implementa:
  - Nó de grafo como tupla imutável
  - Grafo como dicionário de listas de adjacência
  - Árvore Binária de Busca (BST) por índice de risco
  - Fila de prioridade via heapq
"""

from _future_ import annotations
import heapq
from collections import deque
from typing import Optional, List, Tuple, Dict, Set


# ---------------------------------------------------------------------------
# 1. REPRESENTAÇÃO DE VÉRTICE (tupla imutável)
# ---------------------------------------------------------------------------
# vertice = (id_municipio, nome, indice_risco, custo_atendimento, populacao)
# Usar tupla garante imutabilidade e menor overhead de memória que dict/objeto.

def criar_vertice(id_mun: int, nome: str, risco: float,
                  custo: float, pop: int) -> tuple:
    """Cria um vértice como tupla imutável com 5 campos."""
    return (id_mun, nome, round(risco, 4), round(custo, 2), pop)


def id_v(v: tuple) -> int:       return v[0]
def nome_v(v: tuple) -> str:     return v[1]
def risco_v(v: tuple) -> float:  return v[2]
def custo_v(v: tuple) -> float:  return v[3]
def pop_v(v: tuple) -> int:      return v[4]


# ---------------------------------------------------------------------------
# 2. GRAFO — dicionário de listas de adjacência
# ---------------------------------------------------------------------------
# Escolha justificada: lista de adjacência ocupa O(V+E) espaço, enquanto
# matriz de adjacência ocuparia O(V²). Para grafos esparsos (municípios têm
# poucas estradas entre si), a lista é muito mais eficiente.

class Grafo:
    """
    Grafo ponderado não-direcionado representado como dicionário de
    listas de adjacência.

    Complexidade:
      - Espaço: O(V + E)
      - Adicionar vértice: O(1)
      - Adicionar aresta:  O(1)
      - Vizinhos de v:     O(grau(v))
    """

    def _init_(self):
        # dict: id_municipio -> tupla do vértice
        self.vertices: Dict[int, tuple] = {}
        # dict: id_municipio -> lista de (id_vizinho, peso)
        self.adjacencia: Dict[int, List[Tuple[int, float]]] = {}

    # ---- Construção --------------------------------------------------------

    def adicionar_vertice(self, v: tuple) -> None:
        """Insere vértice; O(1)."""
        vid = id_v(v)
        self.vertices[vid] = v
        if vid not in self.adjacencia:
            self.adjacencia[vid] = []

    def adicionar_aresta(self, u_id: int, v_id: int, peso: float) -> None:
        """Insere aresta bidirecional com peso; O(1)."""
        self.adjacencia[u_id].append((v_id, peso))
        self.adjacencia[v_id].append((u_id, peso))

    # ---- Consultas ---------------------------------------------------------

    def vizinhos(self, v_id: int) -> List[Tuple[int, float]]:
        """Retorna lista de (vizinho_id, peso); O(grau(v))."""
        return self.adjacencia.get(v_id, [])

    def num_vertices(self) -> int:
        return len(self.vertices)

    def num_arestas(self) -> int:
        total = sum(len(adj) for adj in self.adjacencia.values())
        return total // 2

    def todos_ids(self) -> List[int]:
        return list(self.vertices.keys())

    def get_vertice(self, v_id: int) -> Optional[tuple]:
        return self.vertices.get(v_id)

    def bfs(self, origem_id: int) -> List[int]:
        """Busca em largura; retorna ordem de visita. O(V+E)."""
        visitados: Set[int] = set()
        fila: deque = deque([origem_id])
        ordem: List[int] = []
        visitados.add(origem_id)
        while fila:
            atual = fila.popleft()
            ordem.append(atual)
            for viz, _ in self.adjacencia[atual]:
                if viz not in visitados:
                    visitados.add(viz)
                    fila.append(viz)
        return ordem

    def dfs(self, origem_id: int) -> List[int]:
        """Busca em profundidade iterativa; O(V+E)."""
        visitados: Set[int] = set()
        pilha: List[int] = [origem_id]
        ordem: List[int] = []
        while pilha:
            atual = pilha.pop()
            if atual not in visitados:
                visitados.add(atual)
                ordem.append(atual)
                for viz, _ in self.adjacencia[atual]:
                    if viz not in visitados:
                        pilha.append(viz)
        return ordem

    def subgrafo(self, ids: List[int]) -> "Grafo":
        """Cria subgrafo com apenas os vértices em ids."""
        s = Grafo()
        id_set = set(ids)
        for vid in ids:
            s.adicionar_vertice(self.vertices[vid])
        for uid in ids:
            for viz, peso in self.adjacencia[uid]:
                if viz in id_set and uid < viz:   # evita duplicatas
                    s.adicionar_aresta(uid, viz, peso)
        return s

    def _repr_(self):
        return (f"Grafo(vértices={self.num_vertices()}, "
                f"arestas={self.num_arestas()})")


# ---------------------------------------------------------------------------
# 3. NÓ DA BST
# ---------------------------------------------------------------------------

class Node:
    """
    Nó da Árvore Binária de Busca.
    Chave = índice de risco (float); valor = tupla do município.
    """
    def _init_(self, vertice: tuple):
        self.risco: float = risco_v(vertice)
        self.vertice: tuple = vertice
        self.esquerda: Optional[Node] = None
        self.direita: Optional[Node] = None

    def _repr_(self):
        return f"Node(risco={self.risco}, mun={nome_v(self.vertice)})"


# ---------------------------------------------------------------------------
# 4. ÁRVORE BINÁRIA DE BUSCA (BST)
# ---------------------------------------------------------------------------

class BinarySearchTree:
    """
    BST de municípios ordenada por índice de risco.

    Propriedade: r_esquerda < r_pai <= r_direita

    Complexidade média (árvore balanceada):
      - Inserção:  O(log N)
      - Busca:     O(log N)
      - In-order:  O(N)
      - Altura:    O(N) pior caso, O(log N) média
      - Remoção:   O(log N)
    """

    def _init_(self):
        self.raiz: Optional[Node] = None
        self._tamanho: int = 0

    # ---- Inserção ----------------------------------------------------------

    def inserir(self, vertice: tuple) -> None:
        """Insere município mantendo propriedade BST. O(log N) médio."""
        self.raiz = self._inserir_rec(self.raiz, vertice)
        self._tamanho += 1

    def _inserir_rec(self, no: Optional[Node], vertice: tuple) -> Node:
        if no is None:
            return Node(vertice)
        r = risco_v(vertice)
        if r < no.risco:
            no.esquerda = self._inserir_rec(no.esquerda, vertice)
        else:
            no.direita = self._inserir_rec(no.direita, vertice)
        return no

    # ---- Busca por intervalo -----------------------------------------------

    def buscar(self, r_min: float, r_max: float) -> List[tuple]:
        """
        Retorna todos os municípios com risco em [r_min, r_max].
        O(k + log N), onde k = número de resultados.
        """
        resultado: List[tuple] = []
        self._buscar_rec(self.raiz, r_min, r_max, resultado)
        return resultado

    def _buscar_rec(self, no: Optional[Node], r_min: float,
                    r_max: float, resultado: List[tuple]) -> None:
        if no is None:
            return
        if no.risco >= r_min:
            self._buscar_rec(no.esquerda, r_min, r_max, resultado)
        if r_min <= no.risco <= r_max:
            resultado.append(no.vertice)
        if no.risco <= r_max:
            self._buscar_rec(no.direita, r_min, r_max, resultado)

    # ---- Percurso in-order -------------------------------------------------

    def percurso_in_order(self) -> List[tuple]:
        """
        Retorna municípios em ordem crescente de risco.
        Útil para priorização de atendimento. O(N).
        """
        resultado: List[tuple] = []
        self._in_order_rec(self.raiz, resultado)
        return resultado

    def _in_order_rec(self, no: Optional[Node], resultado: List[tuple]) -> None:
        if no is None:
            return
        self._in_order_rec(no.esquerda, resultado)
        resultado.append(no.vertice)
        self._in_order_rec(no.direita, resultado)

    # ---- Altura ------------------------------------------------------------

    def altura(self) -> int:
        """Altura da árvore. O(N)."""
        return self._altura_rec(self.raiz)

    def _altura_rec(self, no: Optional[Node]) -> int:
        if no is None:
            return -1
        return 1 + max(self._altura_rec(no.esquerda),
                       self._altura_rec(no.direita))

    def balanceamento(self) -> str:
        """Avalia qualidade do balanceamento."""
        h = self.altura()
        import math
        ideal = math.log2(self._tamanho + 1) if self._tamanho > 0 else 0
        ratio = h / ideal if ideal > 0 else 0
        if ratio < 1.5:
            return f"Balanceada (h={h}, ideal≈{ideal:.1f})"
        elif ratio < 2.5:
            return f"Moderada (h={h}, ideal≈{ideal:.1f})"
        else:
            return f"Desbalanceada (h={h}, ideal≈{ideal:.1f})"

    # ---- Remoção -----------------------------------------------------------

    def remover(self, v_id: int) -> bool:
        """Remove município por id. O(log N) médio."""
        self.raiz, removido = self._remover_rec(self.raiz, v_id)
        if removido:
            self._tamanho -= 1
        return removido

    def _remover_rec(self, no: Optional[Node],
                     v_id: int) -> Tuple[Optional[Node], bool]:
        if no is None:
            return None, False
        if id_v(no.vertice) == v_id:
            # Caso 1: folha
            if no.esquerda is None and no.direita is None:
                return None, True
            # Caso 2: apenas filho direito
            if no.esquerda is None:
                return no.direita, True
            # Caso 3: apenas filho esquerdo
            if no.direita is None:
                return no.esquerda, True
            # Caso 4: dois filhos → substituir pelo sucessor in-order
            sucessor = self._min_no(no.direita)
            no.risco = sucessor.risco
            no.vertice = sucessor.vertice
            no.direita, _ = self._remover_rec(no.direita, id_v(sucessor.vertice))
            return no, True
        # Busca recursiva
        if v_id < id_v(no.vertice):
            no.esquerda, r = self._remover_rec(no.esquerda, v_id)
        else:
            no.direita, r = self._remover_rec(no.direita, v_id)
        return no, r

    def _min_no(self, no: Node) -> Node:
        while no.esquerda is not None:
            no = no.esquerda
        return no

    # ---- Utilidades --------------------------------------------------------

    def tamanho(self) -> int:
        return self._tamanho

    def alto_risco(self, limiar: float = 0.7) -> List[tuple]:
        """Retorna municípios com risco >= limiar. Atalho conveniente."""
        return self.buscar(limiar, 1.0)

    def _repr_(self):
        return (f"BST(tamanho={self._tamanho}, "
                f"altura={self.altura()}, {self.balanceamento()})")


# ---------------------------------------------------------------------------
# 5. FILA DE PRIORIDADE (wrapper sobre heapq)
# ---------------------------------------------------------------------------

class FilaPrioridade:
    """
    Min-heap baseado em heapq nativo.
    Usado no Dijkstra e Prim para extrair o vértice de menor custo.

    Complexidade:
      - push: O(log N)
      - pop:  O(log N)
      - peek: O(1)
    """

    def _init_(self):
        self._heap: List[Tuple[float, int]] = []
        self._contador = 0  # desempate FIFO

    def push(self, prioridade: float, item: int) -> None:
        heapq.heappush(self._heap, (prioridade, self._contador, item))
        self._contador += 1

    def pop(self) -> Tuple[float, int]:
        pri, _, item = heapq.heappop(self._heap)
        return pri, item

    def vazia(self) -> bool:
        return len(self._heap) == 0

    def _len_(self) -> int:
        return len(self._heap)