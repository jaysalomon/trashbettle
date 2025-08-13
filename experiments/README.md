# Experiments Directory

Contains protocols, calibration templates, and (to be added) raw / processed data supporting physical validation of the simulation and theoretical framework.

## Structure

- `protocols/` — Markdown protocols for each experimental domain
- `calibration_log_template.csv` — Standardized per-run logging template
- `data/` — (Populate) raw logs (CSV/JSON), intermediate processed files
- `photos/` — Setup and configuration images

## Protocol Overview

| Domain | File | Primary Goals | Key Metrics |
|--------|------|---------------|-------------|
| Micro-chamber thermal | protocol_micro_chamber_thermal.md | Calibrate coupling efficiency & h | Global/local efficiency, peak T |
| Multi-chamber overlap | protocol_multi_chamber_overlap.md | Validate P/D threshold | Efficiency per chamber, overlap gain |
| Flow lattice ΔP–Q | protocol_flow_lattice_dpq.md | Hydraulic resistance & Re bounds | ΔP–Q curve, Cf vs Re |
| PCM buffering | protocol_pcm_buffering.md | Variance reduction realism | RMS reduction, latent utilization |
| Energy balance field | protocol_energy_balance_field.md | Empirical joint distributions | Daily energy components, correlations |
| Resilience fault injection | protocol_resilience_fault_injection.md | Degradation curve vs failures | Capacity P10/P50, slope |

## Calibration Workflow

1. Run protocol; log measurements into a copy of `calibration_log_template.csv`.
2. Place updated log in `experiments/data/calibration_logs/YYYYMMDD_<experiment>.csv`.
3. (Future) Run calibration script to update model parameter JSON (coming soon).
4. Re-run reduced simulation suite with updated parameters to generate revised metrics.

## Suggested Minimal Tooling

- Python environment with pandas, numpy, matplotlib for processing.
- Jupyter notebooks in `experiments/data/notebooks/` for exploratory calibration.

## Next Additions

- `calibration/` directory with parameters YAML & update script
- Automated summary generator merging latest experimental vs simulated metrics

## Contribution Notes

Maintain versioned changes: any alteration to a protocol should include a date stamp and rationale at the end of the file.
