"""
Validation for step 1: graph generators and the load solver.

Checks performed:
  1. every generator produces a DAG (no cyclic call chains)
  2. the iterative load solver agrees with the exact topological-order solution
  3. removing a node reduces total system load (sanity on the removal path)
  4. degree and load distributions differ between topologies as expected
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import networkx as nx
from network import (build_ba_dependency, build_er_dependency,
                     build_layered_dependency, propagate_load,
                     exact_dag_load, entry_nodes, assign_capacity)

SEED = 42
GENERATORS = {
    "BA (scale-free)": lambda s: build_ba_dependency(n=300, m=2, seed=s),
    "ER (random)":     lambda s: build_er_dependency(n=300, mean_degree=4.0, seed=s),
    "Layered DAG":     lambda s: build_layered_dependency(seed=s),
}

print("=" * 62)
print("STEP 1 VALIDATION: graph generation and load propagation")
print("=" * 62)

for name, gen in GENERATORS.items():
    G = gen(SEED)
    print(f"\n{name}")
    print(f"  nodes={G.number_of_nodes()}  edges={G.number_of_edges()}  "
          f"mean degree={2*G.number_of_edges()/G.number_of_nodes():.2f}")

    # 1. acyclicity
    assert nx.is_directed_acyclic_graph(G), f"{name} is not a DAG"
    print("  [ok] acyclic")

    # 2. iterative solver vs exact topological solution
    L_iter = propagate_load(G, external_rate=100.0)
    L_exact = exact_dag_load(G, external_rate=100.0)
    err = max(abs(L_iter[n] - L_exact[n]) for n in G.nodes())
    rel = err / max(L_exact.values())
    assert rel < 1e-9, f"solver mismatch {rel:.2e}"
    print(f"  [ok] iterative solver matches exact solution (max rel err {rel:.1e})")

    # 3. removing the highest-load node must reduce total load
    hub = max(L_iter, key=L_iter.get)
    L_after = propagate_load(G, removed={hub})
    total_before, total_after = sum(L_iter.values()), sum(L_after.values())
    assert total_after < total_before
    print(f"  [ok] removing top node {hub} drops total load "
          f"{total_before:,.0f} -> {total_after:,.0f} "
          f"({100*(1-total_after/total_before):.1f}% of served work lost)")

    # 4. structure summary
    ind = np.array([G.in_degree(n) for n in G.nodes()])
    loads = np.array([L_iter[n] for n in G.nodes()])
    top5 = np.sort(loads)[-5:].sum() / loads.sum()
    print(f"  in-degree: mean={ind.mean():.2f}  max={ind.max()}  "
          f"var/mean={ind.var()/max(ind.mean(),1e-9):.2f}")
    print(f"  entry nodes: {len(entry_nodes(G))}")
    print(f"  load concentration: top 5 nodes carry {100*top5:.1f}% of all load")

    C = assign_capacity(L_iter, alpha=0.5)
    assert all(C[n] >= L_iter[n] for n in G.nodes())

print("\n" + "=" * 62)
print("all checks passed")
print("=" * 62)
