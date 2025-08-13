"""SIM-FL-NET: Hydraulic manifold flow uniformity network model.

Simplified resistive header + parallel channel model.

Model Assumptions:
 - Each of N = nx * ny channels has identical resistance R_c.
 - Inlet header segments between taps each add resistance R_h (swept via ratio r = R_h/R_c).
 - Outlet header assumed ideal (0 resistance) for simplicity.
 - Total inlet pressure P_in fixed to 1 (arbitrary units); flows scale linearly.

Iterative Solution:
 1. Start with uniform channel flows.
 2. Compute header segment flows (cumulative downstream flows) & pressure at each tap.
  3. Update channel flows = P_tap / R_c.
 4. Iterate until convergence.

Metrics:
 - Coefficient of Variation (CV) of channel flows for each r.
 - Pressure drop (min tap pressure) indicates maldistribution severity.

Planned refinements:
 - Include outlet header resistance & both-side maldistribution.
 - Non-uniform channel resistances (manufacturing variance).
 - Coupling to thermal performance weighting.
"""
from __future__ import annotations
import argparse, os, statistics
import matplotlib.pyplot as plt
from sim_utils import build_metadata, save_results, register_figure
import random

def solve_network(nx: int, ny: int, r_ratio: float, max_iter: int = 500, tol: float = 1e-6, variance: float = 0.0):
    N = nx * ny
    # Base resistances
    base_R_c = 1.0
    R_c_list = [base_R_c * (1.0 + random.uniform(-variance, variance)) for _ in range(N)] if variance>0 else [base_R_c]*N
    R_h = r_ratio * base_R_c
    flows = [1.0 / N] * N
    for it in range(max_iter):
        downstream_cum = 0.0
        pressures = []
        P_in = 1.0
        for k in range(N):
            if k == 0:
                P_before = P_in
            else:
                P_before = pressures[-1] - downstream_cum * R_h
            pressures.append(P_before)
            downstream_cum += flows[k]
        new_flows = [p / Rc for p,Rc in zip(pressures, R_c_list)]
        diff = max(abs(a-b) for a,b in zip(flows, new_flows))
        flows = new_flows
        if diff < tol:
            break
    mean_f = sum(flows)/len(flows)
    std_f = statistics.pstdev(flows) if len(flows)>1 else 0.0
    cv = std_f / mean_f if mean_f>0 else 0.0
    min_pressure = min(pressures)
    return {
        'flows': flows,
        'pressures': pressures,
        'cv': cv,
        'min_pressure': min_pressure,
        'iterations': it+1
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--nx', type=int, default=6)
    ap.add_argument('--ny', type=int, default=6)
    ap.add_argument('--r_ratios', type=float, nargs='+', default=[0.0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1])
    ap.add_argument('--max_iter', type=int, default=800)
    ap.add_argument('--tol', type=float, default=1e-7)
    ap.add_argument('--variance', type=float, default=0.05, help='Uniform ±fractional variation in channel resistances')
    ap.add_argument('--trials', type=int, default=100, help='Monte Carlo trials for variability bands')
    ap.add_argument('--fig_dir', type=str, default='paper/figures/simulations')
    ap.add_argument('--output_dir', type=str, default='simulations/results')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()

    # Monte Carlo across resistance variability for each ratio
    stats = []
    for r in args.r_ratios:
        cvs=[]; minPs=[]
        for _ in range(args.trials):
            res = solve_network(args.nx, args.ny, r, args.max_iter, args.tol, args.variance)
            cvs.append(res['cv']); minPs.append(res['min_pressure'])
        cvs_sorted=sorted(cvs)
        p10=cvs_sorted[max(0,int(0.10*len(cvs_sorted))-1)]
        p50=cvs_sorted[int(0.50*len(cvs_sorted))-1]
        p90=cvs_sorted[int(0.90*len(cvs_sorted))-1]
        stats.append({'r_ratio': r,'cv_p10':p10,'cv_p50':p50,'cv_p90':p90,'min_pressure_mean': sum(minPs)/len(minPs)})
        if args.verbose:
            print(f'r={r:.4f} CV50={p50:.4f} (P10={p10:.3f}, P90={p90:.3f})')

    os.makedirs(args.fig_dir, exist_ok=True)
    ratios = [s['r_ratio'] for s in stats]
    cv_p10=[s['cv_p10'] for s in stats]
    cv_p50=[s['cv_p50'] for s in stats]
    cv_p90=[s['cv_p90'] for s in stats]
    plt.figure(figsize=(6,4))
    plt.fill_between(ratios, cv_p10, cv_p90, color='lightgray', alpha=0.6, label='P10–P90')
    plt.plot(ratios, cv_p50, 'o-', lw=2, label='Median')
    plt.xlabel('Header Segment Resistance Ratio (R_h / R_c)')
    plt.ylabel('Flow CV')
    plt.title('Flow Uniformity vs Header Resistance Ratio')
    plt.grid(alpha=.3); plt.legend()
    fig1 = os.path.join(args.fig_dir, 'flow_uniformity_vs_header_ratio.png')
    plt.tight_layout(); plt.savefig(fig1, dpi=140); plt.close()

    # Use median worst-case ratio by median CV
    worst = max(stats, key=lambda x: x['cv_p50'])
    # Generate one representative distribution sample at worst ratio
    sample = solve_network(args.nx, args.ny, worst['r_ratio'], args.max_iter, args.tol, args.variance)
    plt.figure(figsize=(6,4))
    plt.hist(sample['flows'], bins=12, color='teal', alpha=0.8)
    plt.xlabel('Channel Flow (arb)')
    plt.ylabel('Count')
    plt.title(f'Flow Distribution (r={worst["r_ratio"]})')
    plt.grid(alpha=.3)
    fig2 = os.path.join(args.fig_dir, 'flow_distribution_worst_case.png')
    plt.tight_layout(); plt.savefig(fig2, dpi=140); plt.close()

    md = build_metadata('SIM-FL-NET', params={
        'nx': args.nx,
        'ny': args.ny,
        'r_ratios': args.r_ratios,
        'max_iter': args.max_iter,
        'tol': args.tol,
        'variance': args.variance,
        'trials': args.trials
    }, notes='Initial hydraulic manifold uniformity resistive network.')
    md['metrics']['cv_p10']={str(r):v for r,v in zip(ratios, cv_p10)}
    md['metrics']['cv_p50']={str(r):v for r,v in zip(ratios, cv_p50)}
    md['metrics']['cv_p90']={str(r):v for r,v in zip(ratios, cv_p90)}
    md['metrics']['worst_case_ratio'] = worst['r_ratio']
    md['metrics']['worst_case_cv50'] = worst['cv_p50']
    for f in (fig1, fig2):
        register_figure(md, f)
    out = save_results(md, args.output_dir)
    if args.verbose:
        print('Saved metadata:', out)

if __name__ == '__main__':
    main()
