# Timeline

| Week | Work | Gate |
|---|---|---|
| 6  | Repo, step 1 complete | solver validated |
| 7-8 | **CHECKPOINT 1** — proposal discussion, repo demo | |
| 8  | Step 2 worm spreading | epidemic threshold matches theory |
| 8  | Step 3 cascade baseline | sharp transition in alpha |
| 9  | Step 4 detector + quarantine, end to end | load-to-telemetry coupling verified |
| 9  | Coarse U-curve, low replicate count | shape visible |
| 9-10 | **CHECKPOINT 2** — model demo, sweep plan, runtime estimate | |
| 10 | Full sweep, phase diagram, susceptibility | |
| 11 | Distribution fitting, sensitivity analysis | |
| 11 | H3 if on track, else deepen H1/H2 analysis | **STOP RULE** applies here |
| 12 | **CHECKPOINT 3** — demo and report | |

## Stop rule

If the U-curve is not clean by the start of week 11, drop H3 and H4 entirely.
Spend the time on sensitivity analysis and avalanche-distribution fitting
instead. Depth on two hypotheses beats thin coverage of four.

## Runtime budget

Estimate before launching the full sweep. Example: 20 thresholds x 3 detector
qualities x 5 alphas x 30 replicates = 9,000 runs. At 2s per run that is 5
hours. Work this out at Checkpoint 2 and have a parallelisation plan ready.
Long sweeps run as scripts in experiments/, never inside a notebook cell.
