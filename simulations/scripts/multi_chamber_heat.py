"""SIM-HT-MULTI: Multi-chamber thermal interaction & spacing efficiency.

Goal: Identify pitch (P/D) beyond which efficiency gain per added chamber < threshold.

Efficiency per chamber defined here as normalized peak temperature rise at chamber centers
relative to the single isolated chamber case (proxy for delivered heat density).

This is an INITIAL lightweight implementation (explicit 2-D diffusion) intended to
produce quantitative overlap metrics & figure for planning. Further refinements:
 - Switch to Green's function / FFT superposition for speed
 - Energy accounting like SIM-HT-CONJ
 - Convection & PCM layers (optional)
"""
from __future__ import annotations
import torch, argparse, math, os, matplotlib.pyplot as plt
from sim_utils import build_metadata, save_results, register_figure

def run_single(diam_mm: float, domain_mm: float, grid: int, steps: int, alpha: float, dt: float, power_W: float, rho: float, cp: float, ambient: float, device):
    """Return peak center temperature rise for an isolated chamber (baseline)."""
    L = domain_mm * 1e-3
    dx = L / grid
    diam = diam_mm * 1e-3
    r = diam/2
    dt_stable = 0.24 * dx * dx / alpha
    dt_use = min(dt, dt_stable)
    T = torch.full((grid, grid), ambient, device=device)
    x = torch.linspace(0, L, grid, device=device)
    X, Y = torch.meshgrid(x, x, indexing='ij')
    cx = cy = L/2
    mask = (X-cx)**2 + (Y-cy)**2 <= r*r
    area = math.pi * r * r
    source_coeff = (power_W / area) / (rho * cp) * dt_use
    k = torch.tensor([[0.,1.,0.],[1.,-4.,1.],[0.,1.,0.]], device=device).view(1,1,3,3)
    for _ in range(steps):
        T[mask] += source_coeff
        lap = torch.nn.functional.conv2d(T.unsqueeze(0).unsqueeze(0), k, padding=1).squeeze()
        T = T + alpha * dt_use / (dx*dx) * lap
    peak = float(T[grid//2, grid//2].item()) - ambient
    return peak, dt_use

def run_multi(diam_mm: float, pitch_mult: float, n_side: int, domain_mm: float, grid: int, steps: int, alpha: float, dt: float, power_W: float, rho: float, cp: float, ambient: float, device):
    """Return mean peak center temperature rise across all chamber centers for given pitch multiple."""
    L = domain_mm * 1e-3
    dx = L / grid
    diam = diam_mm * 1e-3
    pitch = pitch_mult * diam
    dt_stable = 0.24 * dx * dx / alpha
    dt_use = min(dt, dt_stable)
    T = torch.full((grid, grid), ambient, device=device)
    x = torch.linspace(0, L, grid, device=device)
    X, Y = torch.meshgrid(x, x, indexing='ij')
    # Arrange n_side x n_side grid centered
    start_offset = - ( (n_side-1) / 2.0 ) * pitch
    centers = []
    for i in range(n_side):
        for j in range(n_side):
            cx = L/2 + start_offset + i * pitch
            cy = L/2 + start_offset + j * pitch
            centers.append((cx, cy))
    r = diam/2
    masks = [ (X-cx)**2 + (Y-cy)**2 <= r*r for (cx,cy) in centers ]
    area = math.pi * r * r
    # Per chamber power
    source_coeff = (power_W / area) / (rho * cp) * dt_use
    k = torch.tensor([[0.,1.,0.],[1.,-4.,1.],[0.,1.,0.]], device=device).view(1,1,3,3)
    for _ in range(steps):
        for m in masks:
            T[m] += source_coeff
        lap = torch.nn.functional.conv2d(T.unsqueeze(0).unsqueeze(0), k, padding=1).squeeze()
        T = T + alpha * dt_use / (dx*dx) * lap
    peaks = []
    for (cx,cy) in centers:
        ix = min(grid-1, max(0, int(cx / L * (grid-1))))
        iy = min(grid-1, max(0, int(cy / L * (grid-1))))
        peaks.append(float(T[ix, iy].item()) - ambient)
    return sum(peaks)/len(peaks), peaks, dt_use

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--diam_mm', type=float, default=4.0)
    ap.add_argument('--pitches', type=float, nargs='+', default=[1.5,2.0,2.5,3.0,3.5,4.0])
    ap.add_argument('--n_side', type=int, default=3)
    ap.add_argument('--domain_mm', type=float, default=80.0)
    ap.add_argument('--grid', type=int, default=256)
    ap.add_argument('--steps', type=int, default=1500)
    ap.add_argument('--alpha', type=float, default=1.4e-7)
    ap.add_argument('--rho', type=float, default=1000.0)
    ap.add_argument('--cp', type=float, default=4180.0)
    ap.add_argument('--power_W', type=float, default=5.0)
    ap.add_argument('--ambient_K', type=float, default=298.0)
    ap.add_argument('--dt', type=float, default=0.05)
    ap.add_argument('--device', type=str, default='auto')
    ap.add_argument('--fig_dir', type=str, default='paper/figures/simulations')
    ap.add_argument('--output_dir', type=str, default='simulations/results')
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--refine_pitches', type=float, nargs='*', default=[], help='Subset of P/D values to perform grid refinement on')
    ap.add_argument('--refine_factor', type=int, default=2, help='Grid refinement multiplicative factor')
    args = ap.parse_args()
    device = torch.device('cuda' if (args.device=='auto' and torch.cuda.is_available()) else ('cuda' if args.device=='cuda' else 'cpu'))
    if args.verbose:
        print('Device:', device)
    baseline_peak, dt_used = run_single(args.diam_mm, args.domain_mm, args.grid, args.steps, args.alpha, args.dt, args.power_W, args.rho, args.cp, args.ambient_K, device)
    if args.verbose:
        print(f'Baseline peak rise: {baseline_peak:.2f} K (dt={dt_used:.3e})')
    eff_per_chamber = []
    overlap_gain = []  # max(0, eff-1)
    penalty = []       # max(0, 1-eff)
    refinement_results = {}
    for p in args.pitches:
        multi_mean_peak, peaks, dt_used = run_multi(args.diam_mm, p, args.n_side, args.domain_mm, args.grid, args.steps, args.alpha, args.dt, args.power_W, args.rho, args.cp, args.ambient_K, device)
        eff = multi_mean_peak / baseline_peak if baseline_peak>0 else 0
        g = max(0.0, eff - 1.0)
        pval = max(0.0, 1.0 - eff)
        eff_per_chamber.append(eff)
        overlap_gain.append(g)
        penalty.append(pval)
        if args.verbose:
            print(f'P/D={p:.2f} | mean peak {multi_mean_peak:.2f} K | eff={eff:.3f} | gain={g:.3f} | penalty={pval:.3f}')
        if p in args.refine_pitches:
            refined_grid = args.grid * args.refine_factor
            multi_mean_peak_ref, _, _ = run_multi(args.diam_mm, p, args.n_side, args.domain_mm, refined_grid, args.steps, args.alpha, args.dt, args.power_W, args.rho, args.cp, args.ambient_K, device)
            eff_ref = multi_mean_peak_ref / baseline_peak if baseline_peak>0 else 0
            refinement_results[str(p)] = {
                'base_grid': args.grid,
                'refined_grid': refined_grid,
                'eff_base': eff,
                'eff_refined': eff_ref,
                'abs_diff': abs(eff_ref - eff),
                'rel_diff_frac': abs(eff_ref - eff) / max(1e-9, eff)
            }
    os.makedirs(args.fig_dir, exist_ok=True)
    plt.figure(figsize=(6,4))
    plt.plot(args.pitches, eff_per_chamber, 'o-', lw=2)
    plt.xlabel('Pitch / Diameter (P/D)')
    plt.ylabel('Efficiency per Chamber (norm peak rise)')
    plt.title('Thermal Interaction vs Spacing')
    plt.grid(alpha=.3)
    fig1 = os.path.join(args.fig_dir, 'multi_chamber_efficiency.png')
    plt.tight_layout(); plt.savefig(fig1, dpi=140); plt.close()
    plt.figure(figsize=(6,4))
    plt.plot(args.pitches, overlap_gain, 'o-', color='green', lw=2, label='Overlap Gain (eff-1)+')
    plt.plot(args.pitches, penalty, 's--', color='crimson', lw=2, label='Penalty (1-eff)+')
    plt.xlabel('Pitch / Diameter (P/D)')
    plt.ylabel('Normalized Deviation')
    plt.title('Overlap Gain & Penalty vs Spacing')
    plt.legend(); plt.grid(alpha=.3)
    fig2 = os.path.join(args.fig_dir, 'multi_chamber_gain_penalty.png')
    plt.tight_layout(); plt.savefig(fig2, dpi=140); plt.close()
    threshold_pd = None
    for i in range(1, len(args.pitches)):
        gain = eff_per_chamber[i] - eff_per_chamber[i-1]
        if gain < 0.05 * eff_per_chamber[i-1]:
            threshold_pd = args.pitches[i]
            break
    md = build_metadata('SIM-HT-MULTI', params={
        'diam_mm': args.diam_mm,
        'pitches_PD': args.pitches,
        'n_side': args.n_side,
        'grid': args.grid,
        'steps': args.steps,
        'alpha': args.alpha,
        'power_W_per_chamber': args.power_W,
        'dt_requested': args.dt
    }, notes='Initial multi-chamber spacing efficiency simulation (explicit).')
    md['metrics']['efficiency_per_chamber'] = {str(p): v for p,v in zip(args.pitches, eff_per_chamber)}
    md['metrics']['overlap_gain'] = {str(p): v for p,v in zip(args.pitches, overlap_gain)}
    md['metrics']['penalty'] = {str(p): v for p,v in zip(args.pitches, penalty)}
    md['metrics']['threshold_PD'] = threshold_pd
    for f in (fig1, fig2):
        register_figure(md, f)
    if refinement_results:
        md['metrics']['refinement'] = refinement_results
    out = save_results(md, args.output_dir)
    if args.verbose:
        print('Saved metadata:', out)

if __name__ == '__main__':
    main()
