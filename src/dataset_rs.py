"""
dataset_rs.py — Dados Sintéticos do Rio Grande do Sul
Global Solution 2026 | FIAP — Estruturas de Dados e Algoritmos
Cenário A: Rede de Resposta a Enchentes no Rio Grande do Sul

Os dados de risco são sintéticos, porém calibrados com base em:
  - Defesa Civil RS (2024): municípios afetados
  - IBGE: população estimada 2024
  - Malha viária DNIT: distâncias em horas de deslocamento

Justificativa da síntese: os dados reais da Defesa Civil RS em formato
estruturado não estão disponíveis em API pública gratuita. Os valores
de índice de risco foram estimados com base nos boletins oficiais de 2024
que apontaram Lajeado, Cruzeiro do Sul e São Leopoldo como os municípios
mais críticos (risco ≈ 0.85–0.95), e Porto Alegre como hub central.

Referência: https://www.defesacivil.rs.gov.br/boletins-2024
"""

from src.data_structures import criar_vertice, Grafo, BinarySearchTree


def construir_dataset_rs() -> tuple:
    """
    Constrói e retorna (grafo, bst) com 20 municípios do RS.

    Vértice: (id_ibge, nome, indice_risco, custo_atendimento_R$mil, populacao)
    Aresta: (u, v, horas_deslocamento)
    """

    # -----------------------------------------------------------------------
    # VÉRTICES — municípios selecionados (afetados em 2024)
    # -----------------------------------------------------------------------
    municipios_raw = [
        # (id_ibge, nome,           risco, custo_R$mil, populacao)
        (4314902, "Porto Alegre",   0.62,  1850.0, 1_400_000),
        (4316808, "São Leopoldo",   0.81,   420.0,   230_000),
        (4300406, "Alvorada",       0.74,   210.0,   200_000),
        (4307005, "Canoas",         0.70,   560.0,   340_000),
        (4318705, "Sapucaia do Sul",0.77,   280.0,   145_000),
        (4306403, "Campo Bom",      0.68,   190.0,    65_000),
        (4312401, "Lajeado",        0.91,   350.0,    82_000),
        (4304606, "Bento Gonçalves",0.43,   300.0,   120_000),
        (4304200, "Caxias do Sul",  0.38,   750.0,   545_000),
        (4313409, "Montenegro",     0.83,   260.0,    62_000),
        (4313375, "Muçum",          0.95,   180.0,     5_000),
        (4311403, "Lajeado" + "2",  0.88,   200.0,     8_000),  # Cruzeiro do Sul
        (4307203, "Candelária",     0.72,   220.0,    31_000),
        (4319505, "Triunfo",        0.65,   170.0,    25_000),
        (4302303, "Bom Retiro RS",  0.57,   140.0,    11_000),
        (4302105, "Boa Vista RS",   0.51,   120.0,    10_000),
        (4317202, "Santa Cruz RS",  0.46,   310.0,   130_000),
        (4321501, "Venâncio Aires", 0.69,   240.0,    68_000),
        (4306106, "Cachoeirinha",   0.73,   380.0,   130_000),
        (4308706, "Esteio",         0.78,   290.0,    84_000),
    ]

    # Corrigir nome duplicado
    municipios_raw[11] = (4311403, "Cruzeiro do Sul RS", 0.88, 200.0, 8_000)

    # Criar vértices como tuplas imutáveis
    vertices = [criar_vertice(*m) for m in municipios_raw]

    # -----------------------------------------------------------------------
    # GRAFO
    # -----------------------------------------------------------------------
    grafo = Grafo()
    for v in vertices:
        grafo.adicionar_vertice(v)

    # Arestas: (id_u, id_v, horas_deslocamento)
    # Baseadas na malha viária BR-116, BR-386, BR-470 e RS-010
    arestas = [
        (4314902, 4316808, 0.4),   # POA — São Leopoldo
        (4314902, 4300406, 0.3),   # POA — Alvorada
        (4314902, 4307005, 0.4),   # POA — Canoas
        (4314902, 4306106, 0.3),   # POA — Cachoeirinha
        (4316808, 4318705, 0.2),   # São Leopoldo — Sapucaia
        (4316808, 4313409, 0.5),   # São Leopoldo — Montenegro
        (4307005, 4318705, 0.3),   # Canoas — Sapucaia
        (4307005, 4308706, 0.2),   # Canoas — Esteio
        (4308706, 4306106, 0.2),   # Esteio — Cachoeirinha
        (4318705, 4306403, 0.3),   # Sapucaia — Campo Bom
        (4306403, 4317202, 1.2),   # Campo Bom — Santa Cruz RS
        (4317202, 4307203, 0.9),   # Santa Cruz — Candelária
        (4307203, 4321501, 0.5),   # Candelária — Venâncio Aires
        (4321501, 4312401, 0.4),   # Venâncio — Lajeado
        (4312401, 4311403, 0.3),   # Lajeado — Cruzeiro do Sul
        (4312401, 4313409, 0.6),   # Lajeado — Montenegro
        (4313409, 4319505, 0.4),   # Montenegro — Triunfo
        (4319505, 4302303, 0.7),   # Triunfo — Bom Retiro
        (4304606, 4304200, 0.5),   # Bento G. — Caxias
        (4304200, 4317202, 1.8),   # Caxias — Santa Cruz
        (4312401, 4304606, 1.4),   # Lajeado — Bento G.
        (4311403, 4313409, 0.8),   # Cruzeiro — Montenegro
        (4312401, 4313375, 0.5),   # Lajeado — Muçum (BR-386)
        (4302303, 4302105, 0.5),   # Bom Retiro — Boa Vista
        (4302105, 4304606, 1.1),   # Boa Vista — Bento G.
    ]

    for u, v, peso in arestas:
        grafo.adicionar_aresta(u, v, peso)

    # -----------------------------------------------------------------------
    # BST — ordenada por índice de risco
    # -----------------------------------------------------------------------
    bst = BinarySearchTree()
    for v in vertices:
        bst.inserir(v)

    return grafo, bst, vertices


def construir_subgrafo_n(n: int) -> "Grafo":
    """
    Constrói subgrafo com exatamente N vértices para testes de escalabilidade.
    Os vértices são os de maior risco (piores casos para triagem).
    """
    grafo_completo, bst, _ = construir_dataset_rs()
    # Pega os N de maior risco
    todos = bst.percurso_in_order()
    selecionados = [v[0] for v in todos[-n:]]
    return grafo_completo.subgrafo(selecionados)


if __name__ == "__main__":
    g, bst, verts = construir_dataset_rs()
    print(f"\n{'='*60}")
    print("GRAFO DO RIO GRANDE DO SUL — Enchentes 2024")
    print(f"{'='*60}")
    print(g)
    print(bst)
    print("\n Top 5 municípios de MAIOR risco (BST in-order):")
    for v in bst.percurso_in_order()[-5:]:
        print(f"   {v[1]:<25} risco={v[2]:.2f}  pop={v[4]:>9,}")
    print("\n Municípios com risco ≥ 0.80:")
    for v in bst.alto_risco(0.80):
        print(f"   {v[1]:<25} risco={v[2]:.2f}  custo=R${v[3]:,.0f}k")
