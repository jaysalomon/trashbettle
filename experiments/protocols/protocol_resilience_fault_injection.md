# Protocol: Resilience Fault Injection Test

Objective: Empirically measure system capacity retention curve under incremental component failures (heaters/chambers or flow channels) to validate stochastic resilience model.

## Key Metrics

- Normalized capacity (thermal output or flow performance) vs failure fraction
- P10 / P50 bands if multiple random sequences performed
- Degradation slope (Δcapacity / Δfailure_fraction)
- Critical failure threshold (capacity <0.5)

## Equipment

- Multi-chamber or multi-channel prototype with individually switchable elements
- Power control matrix (MOSFET board) or mechanical blocking inserts for flow
- Temperature / flow sensors (aggregate + per-zone optional)
- Data acquisition & control script

## Setup

1. Verify baseline capacity (all components active) over stabilization interval.
2. Implement randomized failure order list (seed stored for reproducibility).
3. Calibrate measurement (e.g., convert average ΔT field to normalized capacity 1.0 baseline).

## Procedure

1. Iterate failure fractions (e.g., 0%, 5%, 10%, ..., 30%).
2. At each step, deactivate randomly selected additional components to reach target fraction.
3. Allow system to reach steady or pseudo-steady state; record capacity metric.
4. Repeat for N≥5 random sequences to build distribution (if time-limited, prioritize early fractions).

## Data Processing

1. Normalize each curve by its 0% value.
2. Compute median (P50) and band (P10–P90) vs failure fraction.
3. Fit linear or piecewise model to degradation region; extract slope.
4. Compare to resilience_study simulation JSON; report absolute/relative deviations.

## Acceptance Criteria

- Median capacity error vs simulation ≤10% absolute at each sampled fraction.
- Observed slope within simulation ±15%.
- Critical threshold (capacity <0.5) not reached before modeled projection; if earlier, update model assumptions.

## Risks / Mitigations

- Thermal inertia delaying steady state → define time cutoff + moving average criteria.
- Non-random localized clustering → track spatial distribution of failed components.
- Sensor drift → periodic baseline recheck between injections.

## Follow-up

Update resilience model parameters (heterogeneity distribution) and re-run resilience_study to align simulation with empirical distribution.
