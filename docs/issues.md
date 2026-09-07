# Build backlog

Copy each as a GitHub issue. Ordering is the build order; each has a gate that
must pass before the next begins.

---

**#1  Step 1 — dependency graph and load propagation**  `done`
Three generators (layered, BA, ER) producing DAGs. Steady-state load solver.
Gate: iterative solver matches exact topological solution; all graphs acyclic.
Deliverable: notebooks/01_graphs_and_load.ipynb

**#2  Step 2 — worm spreading**  `validation`
SIS/SIR-style lateral movement along trust edges.
Gate: measured epidemic threshold matches lambda_c ~ <k>/<k^2>.
Deliverable: notebooks/02_worm_spreading.ipynb

**#3  Step 3 — capacity cascade baseline**  `validation`
Node removal, load redistribution, overload failure, iterate to fixed point.
Gate: sharp transition in failed fraction as alpha decreases; reproduces the
published load-redistribution result.
Deliverable: notebooks/03_cascade_baseline.ipynb

**#4  Step 4 — detector and quarantine response**
ROC-characterised detector, load-to-telemetry coupling, quarantine with blast
radius. THIS IS THE CRUX: verify early that load-induced anomalies actually
trigger the detector. If the coupling is too weak there is no autoimmune
mechanism and the project needs rescoping.
Gate: measured false-positive rate matches the chosen ROC operating point.
Deliverable: notebooks/04_detector_and_response.ipynb

**#5  Step 5 — sensitivity sweep and the U-curve**
Sweep theta. Decompose damage into compromise / overload / false-positive
quarantine. Tests H1.
Deliverable: notebooks/05_u_curve.ipynb + experiments/sweep_theta.py

**#6  Step 6 — attacker-absent control**
Same sweep with the attacker disabled. Isolates self-inflicted damage. Tests H2.
Look for a susceptibility peak to locate the critical threshold numerically.
Deliverable: notebooks/06_defender_criticality.ipynb

**#7  Phase diagram over (theta, beta)**
Heatmap with worm-dominated / controlled / autoimmune regimes labelled.
Deliverable: notebooks/07_phase_diagram.ipynb

**#8  Avalanche-size distributions**
Maximum-likelihood power-law fitting with likelihood-ratio tests against
lognormal and exponential. Use the `powerlaw` package. Do NOT straight-line-fit
on log-log axes.

**#9  Sensitivity analysis on the load-to-telemetry coupling constant**
Mandatory robustness check — the U-curve could otherwise be an artefact of this
one parameter. See assumptions A11.

**#10  H3 — decoupling the two cascade mechanisms**  `stretch`
Set alpha high enough that overload failure is impossible; check whether the
false-positive cascade still runs.

**#11  H4 — adaptive attacker**  `future work`
Attacker adjusts stealth between episodes based on observed time-to-detection.
Only if well ahead of schedule.

**#12  Report and Checkpoint 3 demo**
Three headline figures: validation plots, U-curve, phase diagram. Plus a live
side-by-side of a worm cascade and an autoimmune cascade.
