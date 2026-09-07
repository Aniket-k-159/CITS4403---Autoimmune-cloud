"""
Dependency graph generation and steady-state load propagation.

A microservice platform is modelled as a directed acyclic graph where an edge
i -> j means "service i calls service j". Load originates at entry nodes
(in-degree zero) and propagates downstream, amplified by per-edge call
multiplicities.

All generators produce DAGs. Edge orientation follows the real-world pattern
that newer / higher-level services call older / shared ones (auth, config,
data stores), which makes those shared services high in-degree hubs.
"""

import numpy as np
import networkx as nx


def _assign_edge_weights(G, rng, lo=0.6, hi=1.6):
    """Call multiplicity: expected calls to j per request served by i."""
    for u, v in G.edges():
        G[u][v]["w"] = rng.uniform(lo, hi)
    return G


def build_ba_dependency(n=300, m=2, seed=None):
    """
    Barabasi-Albert preferential attachment, oriented new -> old.

    Produces a DAG with a heavy-tailed IN-degree distribution: a small number
    of shared services are called by very many others. This is the topology
    that matches observed microservice deployments.
    """
    rng = np.random.default_rng(seed)
    und = nx.barabasi_albert_graph(n, m, seed=int(rng.integers(1 << 30)))
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for u, v in und.edges():
        # orient from the later-arriving node to the earlier one
        caller, callee = (u, v) if u > v else (v, u)
        G.add_edge(caller, callee)
    return _assign_edge_weights(G, rng)


def build_er_dependency(n=300, mean_degree=4.0, seed=None):
    """
    Erdos-Renyi random graph, oriented high-index -> low-index.

    Same node count and (in expectation) the same mean degree as the BA graph,
    so topology can be varied while holding density fixed.
    """
    rng = np.random.default_rng(seed)
    p = mean_degree / (n - 1)
    G = nx.DiGraph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i):
            if rng.random() < p:
                G.add_edge(i, j)
    return _assign_edge_weights(G, rng)


def build_layered_dependency(layer_sizes=(20, 60, 120, 60, 40), fanout=3, seed=None):
    """
    Layered DAG: gateway -> business logic -> platform -> data.

    Each node calls `fanout` nodes chosen from the next layer with
    preferential attachment, plus occasionally from the layer after that.
    This is the most realistic of the three generators.
    """
    rng = np.random.default_rng(seed)
    G = nx.DiGraph()
    layers, node_id = [], 0
    for size in layer_sizes:
        layer = list(range(node_id, node_id + size))
        node_id += size
        layers.append(layer)
    G.add_nodes_from(range(node_id))
    for li in range(len(layers) - 1):
        targets = layers[li + 1]
        skip = layers[li + 2] if li + 2 < len(layers) else None
        counts = np.ones(len(targets))
        for caller in layers[li]:
            k = min(fanout, len(targets))
            probs = counts / counts.sum()
            chosen = rng.choice(len(targets), size=k, replace=False, p=probs)
            for idx in chosen:
                G.add_edge(caller, targets[idx])
                counts[idx] += 1.0
            if skip is not None and rng.random() < 0.25:
                G.add_edge(caller, skip[rng.integers(len(skip))])
    for n_ in G.nodes():
        G.nodes[n_]["layer"] = next(i for i, L in enumerate(layers) if n_ in L)
    return _assign_edge_weights(G, rng)


def entry_nodes(G):
    """Services that receive external traffic: nothing internal calls them."""
    return [n for n in G.nodes() if G.in_degree(n) == 0]


def propagate_load(G, external_rate=100.0, removed=None, max_iter=500, tol=1e-9):
    """
    Steady-state per-node request rate.

    L_j = external_j + sum over live callers i of L_i * w_ij

    Solved by iteration to a fixed point. On a DAG this converges exactly;
    the iterative form is kept so the same code works if cycles are added
    later (retry loops, sidecars).

    `removed` is a set of nodes that are down (failed or quarantined). They
    carry no load and forward none.
    """
    removed = set() if removed is None else set(removed)
    live = [n for n in G.nodes() if n not in removed]
    entries = set(entry_nodes(G))

    L = {n: (external_rate if n in entries else 0.0) for n in live}
    for _ in range(max_iter):
        new = {n: (external_rate if n in entries else 0.0) for n in live}
        for i in live:
            li = L[i]
            if li == 0.0:
                continue
            for j in G.successors(i):
                if j not in removed:
                    new[j] += li * G[i][j]["w"]
        delta = max(abs(new[n] - L[n]) for n in live) if live else 0.0
        L = new
        if delta < tol:
            break
    else:
        raise RuntimeError("load propagation did not converge")
    for n in removed:
        L[n] = 0.0
    return L


def exact_dag_load(G, external_rate=100.0):
    """Reference solution via topological order. Used only to validate
    the iterative solver -- not used in the simulation."""
    entries = set(entry_nodes(G))
    L = {n: (external_rate if n in entries else 0.0) for n in G.nodes()}
    for i in nx.topological_sort(G):
        for j in G.successors(i):
            L[j] += L[i] * G[i][j]["w"]
    return L


def assign_capacity(L, alpha):
    """C_i = (1 + alpha) * L_i. alpha is the spare-capacity (tolerance)
    parameter -- the primary control parameter for cascade models."""
    return {n: (1.0 + alpha) * l for n, l in L.items()}
