"""
test_algorithms.py — Testes Unitários
Global Solution 2026 | FIAP — Estruturas de Dados e Algoritmos

Cobertura:
  - BST: inserção, busca, in-order, remoção, altura
  - Grafo: construção, BFS, DFS, subgrafo
  - Força Bruta: caminho mínimo, backtracking
  - Dijkstra: distâncias, predecessores, gap vs FB
  - Prim: MST, conexidade, custo
"""

import pytest
import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_structures import (
    Grafo, BinarySearchTree, FilaPrioridade,
    criar_vertice, id_v, nome_v, risco_v
)
from src.brute_force import ForcaBruta
from src.greedy import Dijkstra, Prim
from src.dataset_rs import construir_dataset_rs


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def grafo_simples():
    """Grafo de 5 vértices para testes básicos."""
    g = Grafo()
    for i in range(1, 6):
        g.adicionar_vertice(criar_vertice(i, f"Cidade{i}",
                            round(0.1 * i + 0.3, 2), 100.0 * i, 10000 * i))
    g.adicionar_aresta(1, 2, 1.0)
    g.adicionar_aresta(1, 3, 4.0)
    g.adicionar_aresta(2, 3, 2.0)
    g.adicionar_aresta(2, 4, 5.0)
    g.adicionar_aresta(3, 5, 1.0)
    g.adicionar_aresta(4, 5, 2.0)
    return g


@pytest.fixture
def bst_simples():
    """BST com 7 municípios de riscos variados."""
    bst = BinarySearchTree()
    dados = [
        (10, "Alpha",   0.50, 100.0, 1000),
        (20, "Beta",    0.30, 200.0, 2000),
        (30, "Gamma",   0.70, 300.0, 3000),
        (40, "Delta",   0.90, 400.0, 4000),
        (50, "Epsilon", 0.20, 500.0, 5000),
        (60, "Zeta",    0.80, 600.0, 6000),
        (70, "Eta",     0.60, 700.0, 7000),
    ]
    for d in dados:
        bst.inserir(criar_vertice(*d))
    return bst


@pytest.fixture
def grafo_rs():
    grafo, bst, verts = construir_dataset_rs()
    return grafo, bst, verts


# ============================================================
# TESTES — GRAFO
# ============================================================

class TestGrafo:
    def test_vertices_inseridos(self, grafo_simples):
        assert grafo_simples.num_vertices() == 5

    def test_arestas_inseridas(self, grafo_simples):
        assert grafo_simples.num_arestas() == 6

    def test_vizinhos(self, grafo_simples):
        vizs = dict(grafo_simples.vizinhos(1))
        assert 2 in vizs and 3 in vizs
        assert vizs[2] == 1.0
        assert vizs[3] == 4.0

    def test_bfs_alcanca_todos(self, grafo_simples):
        ordem = grafo_simples.bfs(1)
        assert set(ordem) == {1, 2, 3, 4, 5}

    def test_dfs_alcanca_todos(self, grafo_simples):
        ordem = grafo_simples.dfs(1)
        assert set(ordem) == {1, 2, 3, 4, 5}

    def test_subgrafo(self, grafo_simples):
        sub = grafo_simples.subgrafo([1, 2, 3])
        assert sub.num_vertices() == 3
        assert 4 not in sub.vertices
        assert 5 not in sub.vertices

    def test_grafo_rs_tamanho(self, grafo_rs):
        grafo, bst, _ = grafo_rs
        assert grafo.num_vertices() == 20
        assert grafo.num_arestas() > 10

    def test_grafo_rs_conexo(self, grafo_rs):
        grafo, _, _ = grafo_rs
        origem = grafo.todos_ids()[0]
        visitados = set(grafo.bfs(origem))
        assert len(visitados) == grafo.num_vertices()


# ============================================================
# TESTES — BST
# ============================================================

class TestBST:
    def test_tamanho(self, bst_simples):
        assert bst_simples.tamanho() == 7

    def test_in_order_crescente(self, bst_simples):
        in_order = [risco_v(v) for v in bst_simples.percurso_in_order()]
        assert in_order == sorted(in_order)

    def test_busca_intervalo(self, bst_simples):
        resultado = bst_simples.buscar(0.60, 0.85)
        riscos = [risco_v(v) for v in resultado]
        assert all(0.60 <= r <= 0.85 for r in riscos)
        # 0.60, 0.70, 0.80 estão no intervalo
        assert len(resultado) >= 3

    def test_alto_risco(self, bst_simples):
        criticos = bst_simples.alto_risco(0.75)
        assert all(risco_v(v) >= 0.75 for v in criticos)

    def test_altura_positiva(self, bst_simples):
        assert bst_simples.altura() >= 0

    def test_altura_minima(self, bst_simples):
        h_min = math.floor(math.log2(bst_simples.tamanho()))
        assert bst_simples.altura() >= h_min

    def test_remocao(self, bst_simples):
        tam_antes = bst_simples.tamanho()
        bst_simples.remover(10)  # id=10 (risco=0.50)
        assert bst_simples.tamanho() == tam_antes - 1
        # in-order ainda é crescente
        in_order = [risco_v(v) for v in bst_simples.percurso_in_order()]
        assert in_order == sorted(in_order)

    def test_remocao_inexistente(self, bst_simples):
        resultado = bst_simples.remover(9999)
        assert resultado is False

    def test_busca_vazia(self, bst_simples):
        resultado = bst_simples.buscar(0.96, 1.0)
        assert resultado == []

    def test_bst_rs(self, grafo_rs):
        _, bst, _ = grafo_rs
        assert bst.tamanho() == 20
        in_order = [risco_v(v) for v in bst.percurso_in_order()]
        assert in_order == sorted(in_order)


# ============================================================
# TESTES — FILA DE PRIORIDADE
# ============================================================

class TestFilaPrioridade:
    def test_ordem_extracao(self):
        fila = FilaPrioridade()
        fila.push(3.0, 30)
        fila.push(1.0, 10)
        fila.push(2.0, 20)
        pri1, item1 = fila.pop()
        pri2, item2 = fila.pop()
        pri3, item3 = fila.pop()
        assert pri1 <= pri2 <= pri3

    def test_vazia(self):
        fila = FilaPrioridade()
        assert fila.vazia()
        fila.push(1.0, 1)
        assert not fila.vazia()


# ============================================================
# TESTES — FORÇA BRUTA
# ============================================================

class TestForcaBruta:
    def test_caminho_minimo_existe(self, grafo_simples):
        fb = ForcaBruta(grafo_simples)
        res = fb.encontrar_caminho_minimo(1, 5)
        assert res.custo_otimo < float('inf')
        assert res.caminho_otimo[0] == 1
        assert res.caminho_otimo[-1] == 5

    def test_caminho_minimo_correto(self, grafo_simples):
        fb = ForcaBruta(grafo_simples)
        res = fb.encontrar_caminho_minimo(1, 5)
        # Caminho ótimo: 1→2→3→5 = 1+2+1 = 4.0
        assert abs(res.custo_otimo - 4.0) < 1e-9

    def test_conta_chamadas(self, grafo_simples):
        fb = ForcaBruta(grafo_simples)
        res = fb.encontrar_caminho_minimo(1, 5)
        assert res.num_chamadas_rec > 0
        assert res.num_caminhos_avaliados > 0

    def test_mede_tempo(self, grafo_simples):
        fb = ForcaBruta(grafo_simples)
        res = fb.encontrar_caminho_minimo(1, 5)
        assert res.tempo_ms >= 0.0

    def test_sem_caminho(self):
        g = Grafo()
        g.adicionar_vertice(criar_vertice(1, "A", 0.5, 100, 1000))
        g.adicionar_vertice(criar_vertice(2, "B", 0.5, 100, 1000))
        # Sem aresta entre 1 e 2
        fb = ForcaBruta(g)
        res = fb.encontrar_caminho_minimo(1, 2)
        assert res.custo_otimo == float('inf')


# ============================================================
# TESTES — DIJKSTRA
# ============================================================

class TestDijkstra:
    def test_distancia_origem_zero(self, grafo_simples):
        dijk = Dijkstra(grafo_simples)
        res = dijk.executar(1)
        assert res.distancias[1] == 0.0

    def test_distancia_otima(self, grafo_simples):
        dijk = Dijkstra(grafo_simples)
        res = dijk.executar(1)
        # 1→5: mínimo é 4.0 (1→2→3→5)
        assert abs(res.distancias[5] - 4.0) < 1e-9

    def test_predecessor_reconstroi_caminho(self, grafo_simples):
        dijk = Dijkstra(grafo_simples)
        res = dijk.executar(1)
        caminho = res.caminho_ate(5)
        assert caminho[0] == 1
        assert caminho[-1] == 5

    def test_gap_zero_vs_fb(self, grafo_simples):
        """Dijkstra deve ser ótimo (gap = 0%) para pesos positivos."""
        fb = ForcaBruta(grafo_simples)
        res_fb = fb.encontrar_caminho_minimo(1, 5)

        dijk = Dijkstra(grafo_simples)
        res_dijk = dijk.executar(1)

        assert abs(res_fb.custo_otimo - res_dijk.distancias[5]) < 1e-9

    def test_conta_operacoes(self, grafo_simples):
        dijk = Dijkstra(grafo_simples)
        res = dijk.executar(1)
        assert res.arestas_relaxadas > 0
        assert res.insercoes_heap > 0

    def test_rota_prioritaria_rs(self, grafo_rs):
        grafo, bst, _ = grafo_rs
        dijk = Dijkstra(grafo, bst)
        agenda, res = dijk.rota_prioritaria(4314902, limiar_risco=0.65)
        assert len(agenda) > 0
        # Ordenação: risco decrescente
        riscos = [item['risco'] for item in agenda]
        assert riscos == sorted(riscos, reverse=True)


# ============================================================
# TESTES — PRIM (MST)
# ============================================================

class TestPrim:
    def test_mst_n_menos_1_arestas(self, grafo_simples):
        prim = Prim(grafo_simples)
        res = prim.executar(1)
        assert len(res.arestas_mst) == grafo_simples.num_vertices() - 1

    def test_mst_custo_positivo(self, grafo_simples):
        prim = Prim(grafo_simples)
        res = prim.executar(1)
        assert res.custo_mst > 0

    def test_mst_rs_conecta_todos(self, grafo_rs):
        grafo, _, _ = grafo_rs
        prim = Prim(grafo)
        res = prim.executar(4314902)
        assert len(res.arestas_mst) == grafo.num_vertices() - 1

    def test_gap_prim_vs_fb_mst(self):
        """Para N=5, verifica que Prim produz MST ótima."""
        g = Grafo()
        for i in range(1, 6):
            g.adicionar_vertice(criar_vertice(i, f"C{i}", 0.5, 100, 1000))
        g.adicionar_aresta(1, 2, 1.0)
        g.adicionar_aresta(1, 3, 3.0)
        g.adicionar_aresta(2, 3, 1.0)
        g.adicionar_aresta(2, 4, 4.0)
        g.adicionar_aresta(3, 5, 2.0)
        g.adicionar_aresta(4, 5, 1.0)

        fb = ForcaBruta(g)
        res_fb = fb.encontrar_arvore_geradora_minima_exaustiva()

        prim = Prim(g)
        res_prim = prim.executar(1)

        assert abs(res_fb.custo_otimo - res_prim.custo_mst) < 1e-9


# ============================================================
# TESTES DE INTEGRAÇÃO
# ============================================================

class TestIntegracao:
    def test_bst_alimenta_dijkstra(self, grafo_rs):
        """BST.alto_risco() → Dijkstra prioriza municípios corretos."""
        grafo, bst, _ = grafo_rs
        criticos_bst = set(id_v(v) for v in bst.alto_risco(0.80))

        dijk = Dijkstra(grafo, bst)
        agenda, _ = dijk.rota_prioritaria(4314902, limiar_risco=0.80)
        ids_agenda = set(item['id'] for item in agenda)

        assert ids_agenda == criticos_bst

    def test_fb_valida_dijkstra_grafo_pequeno(self):
        """Para instância pequena, FB e Dijkstra devem concordar no custo."""
        from src.performance_monitor import gerar_grafo_sintetico
        grafo, origem, destino = gerar_grafo_sintetico(7, seed=99)

        fb = ForcaBruta(grafo)
        res_fb = fb.encontrar_caminho_minimo(origem, destino)

        dijk = Dijkstra(grafo)
        res_dijk = dijk.executar(origem)

        if res_fb.custo_otimo < float('inf') and res_dijk.distancias[destino] < float('inf'):
            assert abs(res_fb.custo_otimo - res_dijk.distancias[destino]) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
