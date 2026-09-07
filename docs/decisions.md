# Decisions log

## D1. Edge orientation in the BA generator
Preferential attachment is undirected. Oriented new -> old so early-arriving
nodes become high IN-degree shared services (auth, config, data). Reproduces the
observed microservice pattern and keeps the graph acyclic.

## D2. Iterative load solver rather than topological
The graphs are DAGs, so a topological pass is exact and cheaper. The iterative
fixed-point solver is used anyway so the same code still works if cycles are
introduced later (retry loops, sidecar meshes). Validated against the exact
solution: max relative error 4e-16.

## D3. RESOLVED -- fan-out amplification
Load is multiplicative (L_j = sum_i L_i * w_ij, w ~ U(0.6, 1.6)), so it compounds
along call chains. Measured amplification over injected load: BA 148x (longest
chain 15 hops), Layered 57x (4 hops), ER 41x (10 hops). Direction is correct --
data-layer services do serve far more QPS than gateways -- but the BA magnitude
is driven by chain depth rather than by anything realistic.

Decision: use the LAYERED graph as the primary topology for the main
experiments; its bounded depth keeps amplification reasonable and it is the
realistic generator. BA and ER are retained for the topology-comparison arm,
where extreme concentration is precisely the finding. Damage is reported both as
a fraction of nodes and as a share of served work, so concentration is visible
rather than hidden.

## D4. Notebook as the primary deliverable
Analysis lives in notebooks/, numbered by build step, each ending in a
validation gate. Reusable model code is duplicated into src/ as importable
modules once it stops changing, so later sweeps can run headless.
