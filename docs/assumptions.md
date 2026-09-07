# Assumptions

Every modelling assumption, with the direction it biases results. Stating the
bias direction is what distinguishes a limitations section from a disclaimer.

## Substrate

**A1. Capacity is a scalar.**
Real services are multi-resource (CPU, memory, connection pool, file handles)
and can exhaust one while having slack in others.
*Bias:* understates failure. Real services fail earlier than modelled.

**A2. Requests are homogeneous.**
Every request costs the same. Real traffic is a mix of cheap reads and expensive
writes.
*Bias:* understates variance. Real load spikes are burstier.

**A3. Topology is static during an episode.**
No autoscaling, no deployments, no service discovery changes mid-cascade.
*Bias:* removes a negative feedback loop. Autoscaling with a provisioning lag
would be delayed negative feedback and could produce oscillation instead of
collapse. Named as the primary extension.

**A4. Redistribution is instantaneous.**
Load moves to survivors within one timestep; no queueing delay, no connection
draining.
*Bias:* accelerates the cascade relative to reality, but does not change whether
one occurs.

**A5. Services are binary — up or down.**
Real services degrade: they shed load, serve cached responses, return partial
results.
*Bias:* overstates damage per failure, understates the duration over which a
degraded system emits anomalous telemetry.

## Attack layer

**A6. One vulnerability class per base image.**
A shared image implies a shared vulnerability.
*Bias:* makes the monoculture effect cleaner than reality, where images share
some dependencies but not all.

**A7. The attacker knows the topology.**
*Bias:* overstates attacker capability for the static attacker; realistic for a
persistent adversary that has already done reconnaissance.

**A8. Trust edges coincide with call edges.**
If `i` calls `j`, `i` can compromise `j`. Real platforms have partial mTLS,
scoped tokens, and network policies that break this correspondence.
*Bias:* overstates lateral movement. A zero-trust mesh would be a separate
trust graph and is a natural extension.

## Detector

**A9. Detector characterised by its ROC curve, not trained.**
Benign and malicious telemetry are two overlapping distributions with
separability `d'`.
*Bias:* the significant one. A real detector's errors are **correlated across
similar workloads** — services running the same image under the same load
pattern produce similar scores, so false positives cluster rather than arriving
independently. Clustered false positives make the autoimmune cascade *worse*.
Results under this assumption are therefore conservative on H2.

**A10. Telemetry noise is independent across nodes.**
Follows from A9 and carries the same conservative bias.

**A11. Telemetry score is a monotone function of load ratio.**
The coupling that closes the feedback loop. The functional form (and its
strength constant) is a modelling choice, not an empirical measurement.
*Mitigation:* sensitivity analysis on this constant is mandatory, because the
U-curve could otherwise be an artefact of it. This is the single most important
robustness check in the project.

## Response

**A12. Quarantine is instantaneous and complete.**
No credential-revocation propagation delay, no partial isolation.
*Bias:* makes the defence more effective than reality on the attack side and
faster-acting on the autoimmune side. Roughly neutral overall.

**A13. No human in the loop.**
No operator reviews, overrides, or halts the automation.
*Bias:* this is the point, not a flaw. A human-approval delay on high-blast-radius
actions is a named extension and would test whether slowing the defender helps.

**A14. Fixed quarantine duration `T_q`.**
Real remediation time varies widely.
*Bias:* understates variance in recovery.

## Timing

**A15. Synchronous discrete-time updates.**
All nodes update simultaneously each step; no event queue, no continuous time.
*Bias:* can synchronise failures that would be staggered in reality, potentially
sharpening the observed transition. An event-driven reimplementation (SimPy) is
listed as an extension specifically to test whether this changed any conclusion.
