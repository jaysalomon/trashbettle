# Protocol: PCM Thermal Buffering Test

Objective: Quantify temperature variance reduction achievable by a selected PCM configuration under periodic heat input and compare to lumped enthalpy simulation predictions.

## Key Metrics

- RMS temperature (baseline vs PCM)
- Variance reduction (%) = 1 − RMS_PCM / RMS_base
- Peak temperature reduction
- Phase plateau duration per cycle
- Effective latent utilization fraction

## Equipment

- Test cell with integrated heater and PCM cavity (known mass & geometry)
- Selected PCM (document supplier, latent heat, melt range)
- Control cell without PCM (same thermal mass)
- Thermocouples (center, near wall, ambient)
- Data logger (≥1 Hz)
- Programmable power supply (square wave heat profile)

## Setup

1. Assemble PCM cell ensuring void-free fill; record PCM mass.
2. Install thermocouples; verify response and calibration.
3. Program heat input: high power (Q_high), low power (Q_low), period, duty cycle matching simulation.
4. Record ambient baseline 5–10 min.

## Procedure

1. Run baseline (no PCM) sequence for ≥4 full periods; log temperatures & power.
2. Run PCM cell under identical conditions for ≥6 periods (ensure at least 3 consistent cycles after initial melt transient).
3. (Optional) Repeat with modified latent mass (partial fill) to examine scaling.

## Data Processing

1. Segment steady cycles; compute RMS(T_center) and compare.
2. Detect phase plateau intervals where |dT/dt| < threshold while power high.
3. Estimate latent utilization = (Average plateau duration * (Q_high − Q_loss_est)) / (m_PCM * L_latent).
4. Compute variance reduction curve vs latent multiplier (if multiple fills).
5. Compare to sim_SIM-PCM-BUF variance_reduction_sweep; calculate absolute and relative errors.

## Acceptance Criteria

- Measured variance reduction within ±5% (absolute) of simulation prediction for nominal latent mass.
- Plateau detection reproducible across ≥3 cycles.

## Risks / Mitigations

- PCM leakage → ensure containment & secondary tray.
- Incomplete melting → extend run or adjust duty cycle.
- Sensor lag → use fine-gauge thermocouples and correct for known lag if necessary.

## Follow-up

Update PCM model parameters (effective C_base, latent scaling) and regenerate sweep; revise manuscript claim if reduction <5% persists.
