"""SIM-RES-FAIL: Resilience under random channel failures.

Approach:
 - Assume baseline network of N channels each contributing equally to heat & flow capacity.
 - Randomly remove a fraction p of channels; remaining capacity ~ (active/N) * (1 - interaction_loss(active)).
 - Simple interaction loss model: efficiency = 1 - k_overlap*(1 - active/N) with k_overlap small.
 - Repeat trials per p to compute mean retained capacity & variance.

Future improvements:
 - Graph-based percolation on spatial lattice.
 - Separate heat vs flow network dependencies.
"""
from __future__ import annotations
import argparse, os, random, statistics
import matplotlib.pyplot as plt
from sim_utils import build_metadata, save_results, register_figure

def trial_capacity(N: int, fail_frac: float, k_overlap: float, rng: random.Random, sigma_capacity: float, sigma_overlap: float):
    fails = int(fail_frac * N)
    active = N - fails
    # Heterogeneous per-channel capacity factors ~ N(1, sigma_capacity)
    if sigma_capacity > 0:
        caps = [max(0.0, rng.gauss(1.0, sigma_capacity)) for _ in range(N)]
    else:
        caps = [1.0]*N
    # Remove failed channels (assume worst-case random subset; choose first fails entries after shuffle)
    rng.shuffle(caps)
    active_caps = caps[fails:]
    raw_capacity = sum(active_caps) / (sum(caps) if sum(caps)>0 else 1.0)
    # Randomize overlap coefficient slightly per trial
    k_eff = max(0.0, k_overlap + (rng.gauss(0, sigma_overlap) if sigma_overlap>0 else 0))
    eff = 1 - k_eff * (1 - active / N)
    return raw_capacity * eff

def run_failure_curve(N: int, fail_fracs, trials: int, k_overlap: float, seed: int, sigma_capacity: float, sigma_overlap: float):
    rng = random.Random(seed)
    stats = []
    for f in fail_fracs:
        vals = [trial_capacity(N, f, k_overlap, rng, sigma_capacity, sigma_overlap) for _ in range(trials)]
        vals_sorted = sorted(vals)
        p10_idx = max(0, int(0.1*trials)-1)
        p90_idx = max(0, int(0.9*trials)-1)
        stats.append({
            'fail_frac': f,
            'mean_capacity': statistics.mean(vals),
            'p10': vals_sorted[p10_idx],
            'p90': vals_sorted[p90_idx],
            'std': statistics.pstdev(vals)
        })
    return stats

def plot(stats, fig_dir):
    os.makedirs(fig_dir, exist_ok=True)
    f = [s['fail_frac'] for s in stats]
    m = [s['mean_capacity'] for s in stats]
    p10 = [s['p10'] for s in stats]
    p90 = [s['p90'] for s in stats]
    plt.figure(figsize=(6,4))
    plt.plot(f, m, 'o-', lw=2, label='Mean')
    plt.fill_between(f, p10, p90, color='orange', alpha=0.3, label='P10-P90')
    plt.xlabel('Failure Fraction')
    plt.ylabel('Retained Capacity')
    plt.title('Capacity Retention vs Random Failures')
    plt.grid(alpha=.3); plt.legend()
    fig1 = os.path.join(fig_dir, 'resilience_capacity_curve.png')
    plt.tight_layout(); plt.savefig(fig1, dpi=140); plt.close()
    return fig1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--N', type=int, default=400)
    ap.add_argument('--fail_fracs', type=float, nargs='+', default=[0.0,0.02,0.05,0.08,0.1,0.15,0.2])
    ap.add_argument('--trials', type=int, default=300)
    ap.add_argument('--k_overlap', type=float, default=0.15)
    ap.add_argument('--seed', type=int, default=123)
    ap.add_argument('--sigma_capacity', type=float, default=0.08, help='Std dev of per-channel capacity factor')
    ap.add_argument('--sigma_overlap', type=float, default=0.03, help='Std dev on overlap coefficient per trial')
    ap.add_argument('--fig_dir', type=str, default='paper/figures/simulations')
    ap.add_argument('--output_dir', type=str, default='simulations/results')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()
    stats = run_failure_curve(args.N, args.fail_fracs, args.trials, args.k_overlap, args.seed, args.sigma_capacity, args.sigma_overlap)
    fig1 = plot(stats, args.fig_dir)
    md = build_metadata('SIM-RES-FAIL', params={k:getattr(args,k) for k in ['N','fail_fracs','trials','k_overlap','seed','sigma_capacity','sigma_overlap']}, notes='Simple probabilistic resilience capacity model with heterogeneity.')
    md['metrics']['capacity_vs_failure'] = {str(s['fail_frac']): s['mean_capacity'] for s in stats}
    md['metrics']['capacity_p10'] = {str(s['fail_frac']): s['p10'] for s in stats}
    md['metrics']['capacity_p90'] = {str(s['fail_frac']): s['p90'] for s in stats}
    for k in ['mean_capacity']:
        pass
    register_figure(md, fig1)
    out = save_results(md, args.output_dir)
    if args.verbose:
        print('Saved metadata:', out)

if __name__ == '__main__':
    main()
