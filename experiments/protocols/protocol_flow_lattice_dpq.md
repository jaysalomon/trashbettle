# Protocol: Flow Lattice Pressure–Flow (ΔP–Q) Characterization

Objective: Measure pressure drop vs volumetric flow for lattice tiles to validate hydraulic assumptions, identify onset of transitional/turbulent regime, and calibrate effective friction factor.

## Key Metrics

- ΔP at specified Q (e.g., 0.5, 1.0, 2.0 L/min)
- Reynolds number per channel
- Flow uniformity (optional dye or multi-point measurement CV)
- Effective hydraulic resistance R = ΔP / Q
- Deviation from laminar Hagen–Poiseuille prediction (% error)

## Equipment

- Test lattice tiles (record geometry: channel diameter, length, pitch, count)
- Constant-flow pump (0–3 L/min range) OR gravity head apparatus
- Differential pressure transducer (0–5 kPa, ±1% FS)
- Flow meter (±2% or better) or timed volumetric collection
- Thermometer for fluid temperature (viscosity reference)
- Dye (optional uniformity tracing)
- Data logger / acquisition script

## Setup

1. Mount lattice tile in sealed fixture with straight inlet/outlet headers (≥10 diameters entrance length if possible).
2. Fill system with degassed water; purge bubbles.
3. Calibrate zero on ΔP transducer at no-flow condition.
4. Record fluid temperature.

## Procedure

1. Step flow from low to high in ~8 increments (log Q and ΔP steady values, hold ≥10 s each).
2. Repeat descending sequence to detect hysteresis or heating effects.
3. Optional: introduce dye pulse; video record exit distribution for qualitative uniformity.
4. For at least two tiles (different channel counts), repeat full sequence.

## Data Processing

1. Compute per-channel velocity v = Q_total / (N_channels * area).
2. Compute Reynolds Re = ρ v d / μ.
3. Compare measured ΔP vs theoretical laminar ΔP_lam = 128 μ L Q_single /(π d^4) aggregated.
4. Fit empirical correction factor Cf = ΔP_meas / ΔP_lam vs Re (store curve).
5. Identify Re at which |Cf−1| > 0.1 (10% deviation) as laminar validity bound.

## Acceptance Criteria

- Re_laminar_bound within ±20% of simulation design target (<2300) OR mitigation plan recorded.
- Measurement repeatability: ΔP differences between up/down sequences <5% at each Q.

## Risks / Mitigations

- Bubble entrapment → angled purge ports, recirculation flush.
- Pump pulsation → add damping reservoir or average over cycles.
- Temperature drift → measure before/after; adjust viscosity.

## Follow-up

Update hydraulic calibration JSON (experiments/calibration/hydraulics.json) with Cf vs Re. Re-run pressure_drop_analysis using corrected laminar segments only.
