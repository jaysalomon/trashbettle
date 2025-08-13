# Figure Status for Paper
Generated: 2025-08-13

## Figures Currently Used in Paper

### ✅ Publication-Ready (Used in Updated Sections)

| Figure | Section | Caption Summary | Status |
|--------|---------|-----------------|--------|
| `energy_surplus_hist.png` | Simulations 4.1 | Monte Carlo energy balance distribution | **Ready** - Shows P5/P50/P95 values |
| `nitinol_energy_savings.png` | Simulations 4.2 | Energy reduction vs pre-heat temperature | **Ready** - Clear trend, exceeds targets |
| `flow_uniformity_vs_header_ratio.png` | Simulations 4.3 | CV vs header ratio | **Ready** - Shows design window |
| `modal_frequency_trade.png` | Simulations 4.4 | Porosity-thickness trade space | **Ready** - With FEA validation caveat |
| `resilience_capacity_curve.png` | Simulations 4.5 | Capacity vs failure fraction | **Partial** - Needs stochastic bands |

### ⚠️ Problematic Figures (Not Used - Need Fixes)

| Figure | Issue | Action Required |
|--------|-------|-----------------|
| `field_d2.0mm_*.png` | Peak temps ~1488K (unrealistic) | Reduce power, increase convection |
| `coupling_vs_diameter_*.png` | Shows 0% efficiency (metric error) | Redefine efficiency calculation |
| `peakT_vs_diameter_*.png` | Temps too high (>1000K) | Fix boundary conditions |
| `pcm_buffering_temperature.png` | Shows 0% improvement | Tune PCM parameters |

### 📊 Additional Available Figures (Not Currently Used)

| Figure | Quality | Potential Use |
|--------|---------|---------------|
| `stiffness_index_heatmap.png` | Good | Could add to structural section |
| `multi_chamber_efficiency.png` | Needs longer run | After re-simulation |
| `flow_distribution_worst_case.png` | Good | Could show maldistribution example |
| `lattice_optimizer_stub.png` | Placeholder only | Not for publication |

## Figures Needed But Missing

1. **Corrected thermal coupling** - After fixing efficiency definition
2. **PCM buffering with proper parameters** - Showing 30%+ reduction
3. **Multi-chamber spacing analysis** - Full duration run
4. **3D lattice structure** - From Blender script
5. **Experimental validation photos** - When prototypes built

## LaTeX Figure References

### Currently Valid References
```latex
\ref{fig:energy_surplus}      % Energy balance histogram
\ref{fig:nitinol_savings}      % Nitinol energy reduction
\ref{fig:flow_uniformity}      % Flow CV analysis
\ref{fig:modal_trade}          % Structural optimization
\ref{fig:resilience}           % Failure cascade
```

### Commented Out (Awaiting Fixed Figures)
```latex
% \ref{fig:heat_transfer}      % Needs realistic temperatures
% \ref{fig:chamber_comparison}  % Needs corrected efficiency
% \ref{fig:pcm_buffering}      % Needs working PCM model
```

## Recommendations

### Immediate Actions
1. **Fix thermal simulations** - Priority 1 (core claim)
2. **Fix PCM model** - Priority 2 (supporting claim)
3. **Run full multi-chamber** - Priority 3 (spacing optimization)

### For Final Paper
- Add error bars/confidence intervals to all plots
- Ensure consistent color scheme across figures
- Add scale bars where appropriate
- Consider combining related plots into multi-panel figures

### Quality Checklist
- [ ] Font size ≥ 10pt in all figures
- [ ] Axes labeled with units
- [ ] Legend visible and clear
- [ ] Resolution ≥ 150 DPI for print
- [ ] Colorblind-friendly palette