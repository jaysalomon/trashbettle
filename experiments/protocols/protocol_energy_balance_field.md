# Protocol: Field Energy Balance Data Collection

Objective: Collect empirical daily energy generation and load data (solar, biomass/chemical, actuator, parasitic) to build joint distributions and validate Monte Carlo energy balance model including correlation structure.

## Key Metrics

- Daily solar energy (Wh) & irradiance profile
- Biomass / waste-to-energy yield (Wh equivalent)
- Actuator energy consumption (Wh) & duty cycle timeline
- Parasitic baseline load (Wh)
- Net surplus (Wh)
- Empirical failure indicator (net < 0) frequency
- Correlation matrix among primary drivers (Pearson & Spearman)

## Equipment

- PV panel with calibrated current/voltage logger (1–5 min interval)
- Biomass reactor: gas volume or thermal output sensor (convert to Wh)
- Actuator controller with energy metering
- Inline power meters for parasitic electronics
- Environmental sensors: ambient T, humidity, light (lux or W/m²)
- Data logger / SD card / cloud gateway

## Deployment Setup

1. Install sensors; verify time synchronization (NTP or manual alignment).
2. Perform 24 h dry run to ensure data integrity.
3. Calibrate solar logger vs reference pyranometer (if available) or manufacturer spec at noon.
4. Record initial reactor substrate mass / composition.

## Data Collection Procedure

1. Log continuously for ≥14 full days (capture weather variability).
2. Perform daily integrity check (missing timestamps, sensor saturation).
3. Note any intervention events (maintenance, recalibration) in log.
4. If actuator usage is event-driven, add manual annotations or digital triggers.

## Data Processing

1. Aggregate raw logs to daily totals; align by day boundary (midnight local time).
2. Compute net surplus per day; label deficit days.
3. Build joint dataset of (Solar, Biomass, Actuator, Parasitic) daily values.
4. Calculate correlation matrix (Pearson & Spearman).
5. Fit marginal distributions (e.g., solar ~ truncated normal, biomass ~ lognormal, actuator duty ~ beta) using MLE.
6. Construct copula (Gaussian or empirical rank) to model correlations.
7. Re-run Monte Carlo with fitted joint model; compute new failure probability & percentile statistics.
8. Compare baseline independent vs empirical vs adverse correlation scenarios.

## Acceptance Criteria

- Data completeness ≥95% of expected samples per sensor.
- Time synchronization error <60 s across all streams.
- Empirical failure probability lies within simulated [independent, adverse] interval.

## Risks / Mitigations

- Sensor drift → weekly calibration spot-check.
- Data loss → redundant logging (SD + live stream) and daily backup.
- Bio-reactor variability → maintain consistent feed schedule.

## Follow-up

Update energy_balance_mc parameters JSON (experiments/calibration/energy_model.json) with fitted distributions and correlation matrix; regenerate manuscript figure if material change in failure probability.
