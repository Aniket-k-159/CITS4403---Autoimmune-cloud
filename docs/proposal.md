# Checkpoint 1 — project proposal

CITS4403 Computational Modelling. Solo project.

---

## 1. System and motivation

A microservice platform is a directed graph. Nodes are services, an edge
`i -> j` means "service `i` calls service `j`". Two properties drive everything
that follows:

- **Services have finite capacity.** When one is removed, its traffic
  redistributes to the survivors, which can push them past their own limits.
  This is the load-redistribution cascade mechanism, the same family as
  power-grid blackouts.
- **Services trust each other.** Internal calls are not re-authenticated, so a
  compromised service can reach whatever it is trusted by. Attacks spread
  laterally along trust edges, which is a contagion process.

Nobody manually monitors hundreds of services, so platforms deploy machine
learning anomaly detection with **automated** response: a flagged workload is
quarantined, its credentials revoked, its container killed. No human in the
loop.

Every statistical detector has an unavoidable trade-off. The score
distributions for "under attack" and "having a busy Tuesday" overlap, so any
threshold trades false positives against false negatives. This is not a defect
of a particular model; it is geometry.

The motivating observation is what a false positive *costs* once response is
automated. In a monitored system it costs an engineer's attention. In an
automated system it deletes a healthy service — and deleting a loaded node in a
dependency graph redistributes its traffic onto its neighbours, which makes
those neighbours look anomalous, which triggers further quarantines.

**The defence is itself a contagion process on the same graph.** It spreads, it
removes services, and it feeds itself. That is positive feedback, and positive
feedback is what turns a local incident into a system-wide outage.

The biological parallel is autoimmunity: a more aggressive immune response
clears pathogens faster, but past a point destroys healthy tissue, and a
cytokine storm can kill the patient faster than the infection would have. The
optimal response is not the most aggressive one.

## 2. Research question

> How do detector sensitivity, response aggressiveness, and infrastructure
> topology jointly determine total system damage in an automated cloud defence
> system?

## 3. Hypotheses

**H1 (core).** Total damage as a function of detector sensitivity is U-shaped.
Too insensitive and the worm cascades; too sensitive and false-positive
quarantine cascades. The minimum is interior, and its location depends on spare
capacity and topology, not on detector accuracy alone.

**H2 (core).** There exists a critical sensitivity above which the *defender
alone* is supercritical: it produces a system-wide outage with no attacker
present. Tested directly by sweeping sensitivity with the attacker disabled.

**H3 (stretch).** The detector-driven cascade is a mechanism distinct from the
capacity cascade: it persists even when spare capacity is set high enough that
overload failure is impossible. If so, over-provisioning — the standard defence
against cascading failure — does not protect against this one.

**H4 (extension, likely future work).** An adaptive attacker that shifts toward
stealth as sensitivity rises lowers the optimal sensitivity, inverting the
"more detection is better" intuition.

### Falsification conditions

- H1 fails if damage is monotone in sensitivity with no interior minimum.
- H2 fails if attacker-absent damage rises smoothly with no sharp transition.
- H3 fails if the cascade disappears once capacity failure is made impossible.
- H4 fails if the optimum is unchanged between static and adaptive attackers.

## 4. Modelling approach

Discrete-time simulation on a directed acyclic dependency graph.

**Substrate.** Layered DAG (gateway -> business logic -> platform -> data) as
the primary topology, with Barabási–Albert and Erdős–Rényi graphs as the
topology-comparison arm. Load originates at entry services and propagates
downstream with per-edge call multiplicities. Capacity is `C_i = (1+alpha) L_i`,
where `alpha` is spare capacity.

**Attack layer.** Compromise spreads along trust edges with per-step
probability `beta`, conditional on the target sharing a vulnerable base image.
The attacker chooses a stealth level `s`: louder attacks spread faster but are
easier to detect.

**Detector.** Characterised by its **ROC curve** rather than as a trained model.
Benign and malicious telemetry are two overlapping score distributions with
separability `d'`; the threshold `theta` selects an operating point on the
resulting curve. This is deliberate — it makes detector *quality* and detector
*operating point* independently sweepable, which a single trained model does
not permit.

**Response.** A flagged node is quarantined for `T_q` steps. Two aggressiveness
knobs: the threshold `theta` and the quarantine blast radius (node only,
node plus neighbours, or whole trust zone).

**The coupling that closes the loop.** Telemetry score depends on load. A
service that absorbs redistributed traffic emits elevated latency, error rate
and resource use — exactly the signature the detector was built to flag. This
coupling is what makes the defence a cascade rather than a series of
independent mistakes.

### Three damage sources, tracked separately

1. **Compromise** — the worm reached the service.
2. **Overload** — the service genuinely exceeded capacity after a neighbour was
   removed.
3. **False-positive quarantine** — the service was healthy and had headroom, and
   was removed because its telemetry looked anomalous.

Keeping these decomposed is what makes the U-curve interpretable. Collapsed into
one number, the shape is visible but not explicable.

## 5. Experimental design

| Variable | Range | Purpose |
|---|---|---|
| Detector threshold `theta` | full ROC sweep | H1, H2 |
| Detector quality `d'` | 1, 2, 3 | separates "better AI" from "more aggressive AI" |
| Blast radius | node / +1 hop / zone | H2 |
| Spare capacity `alpha` | 0.1 – 1.0 | locates the cascade transition; H3 |
| Topology | layered / BA / ER | structural factor |
| Attacker | absent / static / adaptive | H2, H4 |
| Infection rate `beta` | sweep | phase diagram axis |

**Controls.** Matched node count and mean degree across topologies. Fixed and
logged seeds. The **attacker-absent** condition is run at every threshold — this
is the central control and the direct test of H2.

**Replicates.** 30 per cell for means and confidence intervals; 1000+ triggers
per cell for avalanche-size distributions, which are tail-hungry.

## 6. Validation before extension

Two published baselines must be reproduced before anything novel is added:

| Baseline | Gate |
|---|---|
| SIS/SIR spreading on a network | measured epidemic threshold matches `lambda_c ~ <k>/<k^2>` |
| Load-redistribution cascade | sharp transition in failed fraction as `alpha` falls |

If these do not reproduce, the extensions mean nothing.

## 7. Analysis

**Quantitative.** Damage-decomposition U-curve. Phase diagram over
(`theta`, `beta`) with worm-dominated, controlled and autoimmune regimes
labelled. Susceptibility (variance across replicates) to locate transitions
numerically rather than by eye. Avalanche-size distributions fitted by
maximum-likelihood with likelihood-ratio tests against lognormal and exponential
alternatives — not straight-line fits on log-log axes.

**Qualitative.** Cascade timelines. Network snapshots contrasting a
worm-dominated cascade (spreading along trust edges) with an autoimmune cascade
(spreading along load edges) — these should look visibly different.

## 8. Scope tiering

Solo project, roughly five weeks of build time.

- **Core:** H1 and H2.
- **Stretch:** H3.
- **Future work:** H4, stated in the report as the primary extension.

**Stop rule.** If the U-curve is not clean by the start of week 11, drop the
stretch goals and spend the time on sensitivity analysis and distribution
fitting instead. Depth on two hypotheses beats thin coverage of four.

**Fallback design.** If three layers is judged too ambitious for one person,
drop the worm and ask purely "when does automated remediation cause more outage
than it prevents?" This retains the cascade, the detector, and the entire
autoimmune mechanism — the attack layer is the part contributing least novelty.

## 9. Progress at Checkpoint 1

Step 1 is complete and validated (`notebooks/01_graphs_and_load.ipynb`):

- three graph generators, all producing DAGs
- steady-state load propagation, validated against an exact topological-order
  solution to machine precision (max relative error 4e-16)
- topology comparison showing the robust-yet-fragile property

Matched on node count and mean degree, removing a single service costs **47%**
of served work on the scale-free graph versus **5%** on the random graph. No
attacker and no detector are in the model yet — this is structure alone.

## 10. Questions for the facilitator

1. Does reproducing the two published baselines count toward the contribution,
   or is it treated as prerequisite work?
2. Is the ROC abstraction acceptable, or would a trained detector be preferred
   even at the cost of the sensitivity sweep?
3. Working solo, is it better to go broad across the three layers or deep on the
   autoimmune mechanism with a simpler attack model?
