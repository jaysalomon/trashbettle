# Interim Simulation Findings (2025-08-13 Update Cycle 2)

## Cycle DEV_CYCLE_4 (2025-08-13T09:26Z)

Highlights:

- (Placeholder highlights already captured in archived JSON; future cycles auto-prepended.)

This document captures the current state of quantitative evidence from the implemented simulation suite prior to the next refinement cycle.


## 1. Thermal – Conjugate Heat (SIM-HT-CONJ)
Current tuned parameters (h=150 W/m²K, power=6–8 W, temperature cap 500 K) yield plausible peak temperatures (300–497 K) and near-unity global energy retention; localized (annulus) efficiency differentiates diameters (2 mm ≈ 0.995 vs 12 mm ≈ 0.81). Time-series efficiency now available.

Key metrics (Cycle 2):

- Local coupling efficiency input (2–12 mm): 0.995 → 0.81 (decreasing with diameter)
- Peak T range: 302–498 K (below cap)

Remaining limitations:

- No material property temperature dependence yet.
- Global efficiency saturates at ~1 (domain still large compared to heated region); focus shifts to local metric.

Next actions:

1. Add conduction/convection balance validation vs analytical transient solution.
2. Consider adding mild property variation or conduction into substrate layer.
3. Annotate figures with local efficiency labels.

## 2. Thermal – Multi-Chamber Interaction (SIM-HT-MULTI)

Revised metrics separate constructive overlap (gain) from detrimental interaction (penalty):

- overlap_gain = max(0, eff-1)
- penalty = max(0, 1-eff)

Observed (Cycle 2 revised):

- Peak overlap gain at tightest spacing (P/D 1.5) ≈ 0.34 (34% boost) decaying toward 0 beyond P/D ≈ 3.5.
- No penalty region encountered in current parameter sweep (eff never < 1 across range studied).

Planned refinements:

1. Introduce slight random power perturbations (±3–5%) to generate variability bands for gain.
2. Auto-detect threshold spacing where overlap_gain < 0.05 (5%).
3. Extend spacing sweep to larger P/D until penalty emerges or convergence confirmed.

\n## 3. Flow Uniformity (SIM-FL-NET)
Monte Carlo (±5% resistance) produces CV percentile bands; pronounced spikes remain at specific ratios (e.g., r=0.05 median CV≈5.67, P90≈5.76) while low ratios stay low (median CV≈0.028 at r=0.0).

Next actions:

1. Expand r resolution around spike for precise exclusion window.
2. Compute safe design band r where CV_P90 < 0.3.

\n## 4. Energy Balance Monte Carlo (SIM-EN-MC)
Surplus distribution robust.

- P5 ≈ 0.28 kWh, P50 ≈ 0.62 kWh, P95 ≈ 0.97 kWh
- Failure probability (surplus < 0) ≈ 0.64%

Interpretation: High likelihood of meeting storage and load profile with current sizing.

Actions Planned:

1. Sensitivity / variance decomposition (e.g., Sobol or one-at-a-time) to attribute tail risk.
2. Add correlation scenarios (e.g., low solar coinciding with high actuator demand).

\n## 5. PCM Buffering (SIM-PCM-BUF)
Tuned window (raised ambient / init, narrowed band) yields ~5% variance reduction baseline; latent multiplier sweep shows up to ~10% at 2× capacity.

Next actions:

1. Optimize for ≥25% reduction by adjusting duty & Q_high/Q_low schedule.
2. Add automatic param sweep selection logging top configurations.

\n## 6. Nitinol Actuation Energy (SIM-ACT-NIT)
Energy per cycle declines almost linearly with preheat.

- Max reduction at 320 K ≈ 58.7% vs ambient baseline.
- Clear diminishing-return region to identify (marginal saving per degree).

Actions Planned:

1. Compute marginal d(reduction)/dT_preheat curve; choose optimal preheat setpoint.
2. Add cooling recovery / cycle time constraint modeling.

\n## 7. Resilience / Failure Capacity (SIM-RES-FAIL)
Heterogeneous capacities & overlap variability added; percentile band now meaningful (P10–P90 spread increases with fail fraction).

Next actions:

1. Define target: capacity_P10 ≥0.80 at 15% failure; adjust design if unmet.
2. Add risk curve (prob(capacity < threshold) vs fail frac).

\n## 8. Structural Modal Surrogate (SIM-STR-MODAL)
Best trade point (porosity 0.7, thickness ratio 0.6) yields significant stiffness index with lowest mass ratio (0.18). Max frequency ratio found at a different thickness/porosity pairing.

Limitations: Analytical scaling surrogate not yet validated via FEA samples.

Actions Planned:

1. Run 1–2 representative FEA verifications to calibrate surrogate error.
2. Add constraint filters (max deflection, manufacturability limits).

\n## 9. Lattice Optimizer (SIM-OPT-LAT)
Lightweight NSGA-II style GA implemented (SBX crossover + mutation). Outputs first-front set and a hypervolume proxy.

Cycle 2 outcomes (example run):

- Front size: (see latest JSON; typically O(40–60) for pop=100, gens=25)
- Hypervolume proxy (inverse crowd sum) recorded for comparison across cycles.

Next actions:

1. Add true hypervolume (reference point) and generational convergence trace figure.
2. Enforce manufacturing constraints (min strut thickness ratio, porosity bounds tightening) as filters.
3. Allow multi-run seeding for statistical robustness (median front metrics).

\n## 10. Cross-Cutting Gaps

- Lack of uncertainty representation (error bars, percentile bands) in most plots.
- Some thermal outputs physically implausible (very high peak temperatures) — requires normalization before publication.
- Efficiency metrics (thermal, PCM) need redefinition to be meaningful.
- Missing sensitivity analyses on key stochastic models.

\n## 11. Immediate Next-Step Priorities (Ordered)

1. Fix thermal efficiency definition (localized & global) and re-run conjugate heat with realistic parameters.
2. Full-duration multi-chamber run to establish spacing threshold (add slight perturbations for variability band).
3. Tune PCM model to demonstrate meaningful buffering (≥30% variance reduction target).
4. Add resistance perturbations to flow model and produce CV vs ratio with percentile bands.
5. Introduce stochasticity into resilience model for percentile curves.
6. Sensitivity analysis for energy balance; identify top two drivers.
7. Implement minimal evolutionary lattice optimizer (replace stub).
8. Validate structural surrogate with at least one FEA reference (placeholder or external tool if available).

\n## 12. Publication Readiness Status

| Domain | Core Metric Credible? | Visualization Ready? | Needs Action |
|--------|-----------------------|-----------------------|-------------|
| Conjugate Heat | Yes (local metric) | Yes | Analytical validation |
| Multi-Chamber | Partial (needs variability threshold) | Partially | Threshold & variability |
| Flow Network | Yes (bands added) | Yes | Fine resolution sweep |
| Energy Balance | Yes | Yes | Sensitivity attribution (deep) |
| PCM Buffering | Emerging (5–10%) | Yes | Improve to ≥25% |
| Nitinol | Yes | Yes | Marginal optimization |
| Resilience | Yes (bands) | Yes | Risk curve |
| Structural Modal | Surrogate only | Yes | FEA validation |
| Lattice Optimizer | Early GA | Yes | Convergence & true HV |

\n## 13. Risk Notes

- Thermal credibility risk if high absolute temperatures shown without context.
- PCM claim unsupported until variance reduction demonstrated.
- Optimizer and resilience sections may need labeling as preliminary unless upgraded.

\n## 14. Data & Reproducibility

All JSON outputs stored under `simulations/results/` with timestamps; figures under `paper/figures/simulations/`. Next summary refresh should overwrite or version this document (append date).

---
Prepared: 2025-08-13
