"""
main.py — Orquestrador Principal
Global Solution 2026 | FIAP — Estruturas de Dados e Algoritmos
Cenário A: Rede de Resposta a Enchentes no Rio Grande do Sul

Executa a pipeline completa:
  1. Constrói grafo + BST com dados do RS
  2. Demonstra operações da BST
  3. Força Bruta (subinstância N=8)
  4. Dijkstra (grafo completo) + agenda de atendimento
  5. Prim (MST) — cobertura de rotas
  6. Benchmark de desempenho FB vs Dijkstra
  7. Gera todas as figuras obrigatórias

Uso:
  cd global-solution-2026
  python main.py
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def separador(titulo: str):
    print(f"\n{'='*65}")
    print(f"  {titulo}")
    print(f"{'='*65}")


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║    GLOBAL SOLUTION 2026 — FIAP                               ║
║    Monitoramento de Riscos Ambientais                        ║
║    Cenário A: Enchentes no Rio Grande do Sul                 ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # ------------------------------------------------------------------
    # 1. DATASET
    # ------------------------------------------------------------------
    separador("1. CONSTRUÇÃO DO GRAFO E DA BST")
    from src.dataset_rs import construir_dataset_rs
    grafo, bst, vertices = construir_dataset_rs()

    print(f"\n  {grafo}")
    print(f"  {bst}")
    print(f"\n  Municípios de ALTO RISCO (≥ 0.80) — BST in-order:")
    for v in bst.alto_risco(0.80):
        print(f"    {v[1]:<25}  risco={v[2]:.2f}  pop={v[4]:>9,}")

    # ------------------------------------------------------------------
    # 2. BST — OPERAÇÕES
    # ------------------------------------------------------------------
    separador("2. OPERAÇÕES DA BST")

    print("\n   Percurso in-order (risco crescente):")
    io = bst.percurso_in_order()
    for v in io:
        print(f"    r={v[2]:.2f}  {v[1]}")

    print(f"\n   Busca por intervalo [0.65, 0.80]:")
    intervalo = bst.buscar(0.65, 0.80)
    for v in intervalo:
        print(f"    {v[1]:<25}  risco={v[2]:.2f}")

    print(f"\n   Altura da BST: {bst.altura()} | {bst.balanceamento()}")

    # ------------------------------------------------------------------
    # 3. FORÇA BRUTA — subinstância
    # ------------------------------------------------------------------
    separador("3. FORÇA BRUTA — Caminho Mínimo (N=8)")

    from src.brute_force import ForcaBruta, contar_caminhos_por_n
    from src.dataset_rs import construir_subgrafo_n

    sub8 = construir_subgrafo_n(8)
    ids_sub = sub8.todos_ids()
    origem_fb  = ids_sub[0]
    destino_fb = ids_sub[-1]

    print(f"\n  Subgrafo: {sub8}")
    print(f"  Origem:  {sub8.get_vertice(origem_fb)[1]}")
    print(f"  Destino: {sub8.get_vertice(destino_fb)[1]}")

    fb = ForcaBruta(sub8)
    res_fb = fb.encontrar_caminho_minimo(origem_fb, destino_fb)

    if res_fb.custo_otimo < float('inf'):
        rota = " → ".join(sub8.get_vertice(v)[1] for v in res_fb.caminho_otimo)
        print(f"\n   Custo ótimo:  {res_fb.custo_otimo:.3f} h")
        print(f"   Rota:         {rota}")
    else:
        print(f"\n  ⚠ Destino inacessível neste subgrafo.")
    print(f"   Chamadas recursivas:   {res_fb.num_chamadas_rec:,}")
    print(f"   Caminhos avaliados:    {res_fb.num_caminhos_avaliados:,}")
    print(f"   Tempo:                 {res_fb.tempo_ms:.3f} ms")
    print(f"   Memória pico:          {res_fb.memoria_mb:.5f} MB")

    # Crescimento combinatório
    print("\n   Crescimento combinatório por N:")
    ns = [3, 4, 5, 6, 7, 8, 9, 10, 12]
    stats = contar_caminhos_por_n(grafo, 4314902, ns)
    print(f"  {'N':>4}  {'Caminhos':>10}  {'Chamadas':>12}  {'Tempo(ms)':>10}")
    for n, d in stats.items():
        if d['nota'] == 'OK':
            print(f"  {n:>4}  {d['caminhos']:>10,}  "
                  f"{d['chamadas']:>12,}  {d['tempo_ms']:>10.3f}")
        else:
            print(f"  {n:>4}  {'—':>10}  {'—':>12}  {'inviável':>10}")

    # ------------------------------------------------------------------
    # 4. DIJKSTRA — grafo completo
    # ------------------------------------------------------------------
    separador("4. DIJKSTRA — Rota de Atendimento Prioritário")

    from src.greedy import Dijkstra, Prim
    ORIGEM = 4314902  # Porto Alegre

    dijk = Dijkstra(grafo, bst)
    agenda, res_dijk = dijk.rota_prioritaria(ORIGEM, limiar_risco=0.65)

    print(f"\n  {'Município':<25} {'Risco':>6} {'Custo(h)':>9}  Rota (primeiros 3 hops)")
    print(f"  {'-'*70}")
    for item in agenda:
        rota_curta = " → ".join(item['caminho_nomes'][:4])
        if len(item['caminho_nomes']) > 4:
            rota_curta += " → ..."
        print(f"  {item['nome']:<25} {item['risco']:>6.2f} "
              f"{item['custo_h']:>9.2f}  {rota_curta}")

    print(f"\n   Estatísticas Dijkstra:")
    print(f"     Arestas relaxadas:   {res_dijk.arestas_relaxadas}")
    print(f"     Inserções no heap:   {res_dijk.insercoes_heap}")
    print(f"     Tempo:               {res_dijk.tempo_ms:.4f} ms")
    print(f"     Memória pico:        {res_dijk.memoria_mb:.5f} MB")

    # GAP vs FB (instância N=8)
    if res_fb.custo_otimo < float('inf'):
        dijk_sub = Dijkstra(sub8)
        res_dijk_sub = dijk_sub.executar(origem_fb)
        custo_dijk_sub = res_dijk_sub.distancias.get(destino_fb, float('inf'))
        if custo_dijk_sub < float('inf') and res_fb.custo_otimo > 0:
            gap = abs(res_fb.custo_otimo - custo_dijk_sub) / res_fb.custo_otimo * 100
            print(f"\n   Gap de Otimalidade (FB vs Dijkstra, N=8):")
            print(f"     FB custo:      {res_fb.custo_otimo:.4f} h")
            print(f"     Dijkstra custo:{custo_dijk_sub:.4f} h")
            print(f"     Gap:           {gap:.4f}%")
            if gap < 0.001:
                print(f"     ✅ Dijkstra encontrou a solução ÓTIMA!")

    # ------------------------------------------------------------------
    # 5. PRIM — MST
    # ------------------------------------------------------------------
    separador("5. PRIM — Árvore Geradora Mínima (Cobertura Mínima de Rotas)")

    prim = Prim(grafo)
    res_prim = prim.executar(ORIGEM)

    print(f"\n   Custo total da MST: {res_prim.custo_mst:.2f} h")
    print(f"  Número de arestas:   {len(res_prim.arestas_mst)} "
          f"(= N-1 = {grafo.num_vertices()-1})")
    print(f"\n  Arestas da MST:")
    for u, v, peso in sorted(res_prim.arestas_mst, key=lambda x: x[2]):
        nu = grafo.get_vertice(u)[1]
        nv = grafo.get_vertice(v)[1]
        print(f"    {nu:<25} ↔ {nv:<25}  {peso:.2f} h")

    print(f"\n   Estatísticas Prim:")
    print(f"     Arestas relaxadas:   {res_prim.arestas_relaxadas}")
    print(f"     Inserções no heap:   {res_prim.insercoes_heap}")
    print(f"     Tempo:               {res_prim.tempo_ms:.4f} ms")

    # ------------------------------------------------------------------
    # 6. BENCHMARK
    # ------------------------------------------------------------------
    separador("6. BENCHMARK DE DESEMPENHO — FB vs Dijkstra")

    from src.performance_monitor import (
        executar_benchmarks, ponto_cruzamento, NS_BENCHMARK
    )
    resultados = executar_benchmarks(NS_BENCHMARK)

    n_crit = ponto_cruzamento(resultados)
    if n_crit > 0:
        print(f"\n  ⚠️  Ponto crítico: FB ≫ Dijkstra a partir de N={n_crit}")
    else:
        print(f"\n  ⚠️  FB inviável para N > 12 (explosão combinatória O(N!))")

    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    # ------------------------------------------------------------------
    # 7. FIGURAS
    # ------------------------------------------------------------------
    separador("7. GERANDO FIGURAS OBRIGATÓRIAS")

    from src.visualizations import (
        fig1_grafo_mst, fig2_bst, fig3_desempenho,
        fig4_gap, fig5_tabela_estruturas
    )

    fig1_grafo_mst(grafo, res_prim.arestas_mst, ORIGEM)
    fig2_bst(bst, max_nos=13)
    fig3_desempenho(resultados)
    fig4_gap(resultados)
    fig5_tabela_estruturas()

    # ------------------------------------------------------------------
    # RESUMO FINAL
    # ------------------------------------------------------------------
    separador("RESUMO FINAL — Escala de Decisão")

    print("""
  ┌─────────────────────────────────────────────────────────────┐
  │           ESCALA DE DECISÃO (4 níveis)                      │
  ├──────┬──────────────┬────────────┬──────────────────────────┤
  │ Nível│  Algoritmo   │  Gap Ótim. │  Aplicabilidade Prática  │
  ├──────┼──────────────┼────────────┼──────────────────────────┤
  │  ★★★★│ Dijkstra(G.) │   ≈ 0 %   │  Viável até N=100+     │
  │  ★★★ │ Prim MST     │   ≈ 0 %   │  Cobertura completa     │
  │  ★★  │ Força Bruta  │   = 0 %   │  Apenas N ≤ 12          │
  │  ★   │ FB sem poda  │   = 0 %   │  Inviável N > 8         │
  └──────┴──────────────┴────────────┴──────────────────────────┘

  Recomendação: Dijkstra é a escolha ideal para o cenário RS.
  Combina solução ótima (gap = 0% para pesos positivos) com
  eficiência O((V+E) log V), sendo viável para os 478 municípios
  do RS. A BST garante consulta eficiente dos municípios críticos
  em O(k + log N), alimentando a agenda de atendimento da Defesa Civil.

  Conexão ODS:
    ODS 2  — Segurança alimentar: rota mínima a cooperativas agrícolas
    ODS 11 — Cidades resilientes: triagem de risco por BST
    ODS 13 — Ação climática: monitoramento via dados de satélite
    """)

    print("\n Pipeline completo concluído! Figuras em ./figures/")


if __name__ == "__main__":
    main()
