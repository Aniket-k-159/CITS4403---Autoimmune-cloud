# Autoimmune cloud

CITS4403 research project. Solo.

**Claim under test:** automated defence is itself a contagion process on the
infrastructure it protects, and past a critical detector sensitivity it causes
more outage than the attack it prevents.

## Research question

How do detector sensitivity, response aggressiveness, and infrastructure
topology jointly determine total system damage in an automated cloud defence
system?

## Hypotheses

- **H1 (core).** Total damage as a function of detector sensitivity is
  U-shaped. Too insensitive and the worm cascades; too sensitive and
  false-positive quarantine cascades. The minimum is interior and its location
  depends on spare capacity, not on detector accuracy alone.
- **H2 (core).** There exists a critical sensitivity above which the defender
  alone is supercritical: it produces a system-wide outage with no attacker
  present. Tested directly by running with the attacker disabled.
- **H3 (stretch).** The detector-driven cascade is a mechanism distinct from
  capacity cascade: it persists even when spare capacity is made large enough
  that overload failure is impossible.
- **H4 (extension, likely future work).** An adaptive attacker that shifts
  toward stealth as sensitivity rises lowers the optimal sensitivity.

## Three damage sources, tracked separately

1. **Compromise** — the worm reached the service.
2. **Overload** — the service genuinely exceeded capacity after a neighbour
   was removed.
3. **False-positive quarantine** — the service was healthy and capable, and
   was removed because its telemetry looked anomalous.

Keeping these separate is what makes the U-curve interpretable.

## Validation baselines (reproduced before any extension)

- Load-redistribution cascade: sharp transition in failed fraction as spare
  capacity alpha decreases.
- SIS/SIR spreading on a network: measured epidemic threshold matches
  lambda_c ~ <k> / <k^2>.

## Layout

```
notebooks/    numbered by build step -- the primary deliverable
src/          reusable model code, imported by notebooks and sweeps
experiments/  headless scripts for long parameter sweeps
results/      generated output (gitignored)
docs/         assumptions and decisions logs
```

## Reproduce

```
pip install -r requirements.txt
jupyter lab   # then run notebooks/01_graphs_and_load.ipynb
```

## Status

- [x] Step 1: graph generators (BA, ER, layered), load propagation, validated
      -> `notebooks/01_graphs_and_load.ipynb`
- [ ] Step 2: worm spreading, epidemic threshold validation
- [ ] Step 3: capacity cascade baseline
- [ ] Step 4: detector (ROC) and quarantine response
- [ ] Step 5: sensitivity sweep, U-curve
- [ ] Step 6: attacker-absent control, phase diagram
