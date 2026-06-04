"""
dataset_matopiba.py — Cenário B: Triagem de Risco de Seca no MATOPIBA
Global Solution 2026 | FIAP — Estruturas de Dados e Algoritmos

MATOPIBA = Maranhão, Tocantins, Piauí, Bahia — fronteira agrícola brasileira.
Índice de risco derivado de NDVI (Normalized Difference Vegetation Index) e
precipitação INMET. BST organiza municípios por criticidade de seca.
Dijkstra determina ordem de atendimento dado orçamento de deslocamento.

Dados: sintéticos, calibrados com NDVI MODIS/NASA (2023) e INMET precipitação.
Referências:
  - NASA MODIS NDVI: https://earthdata.nasa.gov
  - INMET BDMEP: https://bdmep.inmet.gov.br
  - IBGE Malha Municipal MATOPIBA: https://ibge.gov.br/geociencias
"""

from src.data_structures import criar_vertice, Grafo, BinarySearchTree


def construir_dataset_matopiba():
    """
    Constrói grafo + BST do MATOPIBA com 18 municípios.

    Vértice: (id_ibge, nome, indice_risco_seca, custo_atendimento_R$mil, populacao)
    Aresta: horas de deslocamento (BR-230, BR-010, BR-020, BR-135)

    Risco de seca = 1 - (NDVI_normalizado * 0.6 + precip_normalizada * 0.4)
    Quanto maior o risco, menor a cobertura vegetal e menor a precipitação.
    """
    municipios_raw = [
        # (id_ibge, nome,              risco, custo_R$mil, populacao)
        # Maranhão
        (2111300, "São Luís",          0.28,  980.0,  1_100_000),
        (2105302, "Imperatriz",        0.42,  320.0,    260_000),
        (2109502, "Presidente Dutra",  0.71,  180.0,     58_000),
        (2115200, "Tuntum",            0.78,  140.0,     35_000),
        # Tocantins
        (1721000, "Palmas",            0.35,  450.0,    320_000),
        (1713700, "Gurupi",            0.47,  190.0,     90_000),
        (1707405, "Dianópolis",        0.69,  150.0,     22_000),
        (1716109, "Natividade",        0.82,  120.0,     10_000),
        # Piauí
        (2211001, "Teresina",          0.31,  520.0,    880_000),
        (2207702, "Parnaíba",          0.44,  210.0,    155_000),
        (2209153, "Picos",             0.73,  160.0,     78_000),
        (2204550, "Corrente",          0.87,  130.0,     26_000),
        # Bahia
        (2927408, "Salvador",          0.22,  1200.0, 2_900_000),
        (2910800, "Feira de Santana",  0.38,  410.0,    640_000),
        (2903201, "Barreiras",         0.61,  280.0,    160_000),
        (2917334, "Luis Eduardo Mag.", 0.74,  220.0,     75_000),
        (2928703, "São Desidério",     0.83,  170.0,     28_000),
        (2919553, "Palmas de Monte A.",0.91,  145.0,     16_000),
    ]

    vertices = [criar_vertice(*m) for m in municipios_raw]

    grafo = Grafo()
    for v in vertices:
        grafo.adicionar_vertice(v)

    # Arestas: rodovias principais do MATOPIBA (horas de deslocamento)
    arestas = [
        # Maranhão
        (2111300, 2105302, 5.5),   # São Luís — Imperatriz (BR-010)
        (2105302, 2109502, 2.5),   # Imperatriz — Presidente Dutra
        (2109502, 2115200, 1.8),   # Presidente Dutra — Tuntum
        # Tocantins
        (1721000, 1713700, 2.0),   # Palmas — Gurupi (TO-070)
        (1713700, 1707405, 3.5),   # Gurupi — Dianópolis
        (1707405, 1716109, 2.2),   # Dianópolis — Natividade
        # Piauí
        (2211001, 2207702, 3.8),   # Teresina — Parnaíba
        (2211001, 2209153, 3.2),   # Teresina — Picos (BR-020)
        (2209153, 2204550, 4.5),   # Picos — Corrente
        # Bahia
        (2927408, 2910800, 1.5),   # Salvador — Feira de Santana (BR-116)
        (2910800, 2903201, 5.0),   # Feira — Barreiras (BR-242)
        (2903201, 2917334, 1.0),   # Barreiras — Luis Eduardo M.
        (2917334, 2928703, 1.8),   # Luis Eduardo — São Desidério
        (2928703, 2919553, 2.5),   # São Desidério — Palmas Monte Alto
        # Ligações inter-estados (eixo MATOPIBA)
        (2105302, 1721000, 6.0),   # Imperatriz — Palmas (BR-010/TO)
        (2115200, 1716109, 4.0),   # Tuntum — Natividade
        (1707405, 2209153, 5.5),   # Dianópolis — Picos (PI)
        (2204550, 2919553, 3.5),   # Corrente — Palmas Monte Alto (BA)
        (2903201, 2209153, 4.8),   # Barreiras — Picos
    ]
    for u, v, peso in arestas:
        grafo.adicionar_aresta(u, v, peso)

    bst = BinarySearchTree()
    for v in vertices:
        bst.inserir(v)

    return grafo, bst, vertices


if __name__ == "__main__":
    from src.greedy import Dijkstra, Prim

    grafo, bst, _ = construir_dataset_matopiba()
    print(f"\n{'='*60}")
    print("CENÁRIO B — MATOPIBA: Triagem de Risco de Seca")
    print(f"{'='*60}")
    print(grafo)
    print(bst)

    print("\n Top 5 municípios de MAIOR risco de seca:")
    for v in bst.percurso_in_order()[-5:]:
        print(f"   {v[1]:<30} risco={v[2]:.2f}  pop={v[4]:>9,}")

    print("\n Municípios com risco de seca ≥ 0.75:")
    for v in bst.alto_risco(0.75):
        print(f"   {v[1]:<30} risco={v[2]:.2f}")

    # Dijkstra a partir de Palmas (TO) — hub logístico central
    ORIGEM = 1721000
    dijk = Dijkstra(grafo, bst)
    agenda, res = dijk.rota_prioritaria(ORIGEM, limiar_risco=0.60)

    print(f"\n Agenda de atendimento a partir de Palmas (TO):")
    print(f"   {'Município':<30} {'Risco':>6} {'Dist(h)':>8}")
    print(f"   {'-'*48}")
    for item in agenda:
        dist = f"{item['custo_h']:.1f}" if item['custo_h'] < float('inf') else '∞'
        print(f"   {item['nome']:<30} {item['risco']:>6.2f} {dist:>8}")
