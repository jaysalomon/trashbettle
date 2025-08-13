# Protocol: Multi-Chamber Thermal Overlap Array Test

Objective: Empirically quantify constructive thermal overlap vs spacing (P/D) for a 3×3 micro-chamber array and validate diminishing returns threshold.

## Key Metrics

- Mean peak center temperature per chamber
- Normalized efficiency per chamber (mean peak / isolated peak)
- Overlap gain (eff − 1)+ and penalty (1 − eff)+
- Temperature uniformity (std dev across 9 centers)
- Time to 90% of peak per chamber

## Equipment

- Interchangeable array plates with P/D = 1.5, 2.0, 2.5, 3.0, 3.5, 4.0
- Uniform resistive micro-heaters (identical power) or coupled fuel micro-burners
- Power distribution board (per-channel current logging)
- IR camera or 9 embedded thermocouples (center each chamber)
- Data acquisition system
- Insulation shroud to reduce ambient drafts

## Setup

1. Calibrate heater power uniformity (±2%).
2. Mount array plate; verify spacing geometry.
3. Place IR camera overhead (or verify thermocouple seating).
4. Log ambient temperature for baseline (5 min).

## Procedure

For each spacing:

1. Simultaneously energize all 9 chambers (constant power step).
2. Record temperature fields / center temperatures every 2–5 s until quasi-steady.
3. Allow partial cooldown (to within 5 K of ambient) before next spacing.
4. Repeat a second run for reproducibility.

## Data Processing

1. For each chamber compute peak ΔT_center and time to 90%.
2. Average peaks across 9 chambers → mean_peak.
3. Normalize: efficiency_per_chamber = mean_peak / isolated_peak (from single-chamber test of same diameter & power).
4. Compute overlap gain and penalty metrics.
5. Fit diminishing returns point: smallest P/D where incremental gain <5% of previous efficiency.
6. Aggregate replicate statistics (mean, std) per spacing.

## Acceptance Criteria

- Measured threshold P/D within 0.5 of simulation prediction (~2.0–2.5).
- Run-to-run peak mean difference <5%.

## Risks / Mitigations

- Unequal heater outputs → pre-calibrate resistances & power supply channels.
- Edge cooling bias → add reflective or insulating side barrier; record notes.

## Follow-up

Update simulation validation table; if threshold deviates significantly, re-fit diffusion + convection parameters and re-run multi_chamber_heat sensitivity sweep.
