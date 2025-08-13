"""SIM-EN-MC: Energy balance Monte Carlo simulation.

Models daily net energy surplus distribution given stochastic inputs.

Random Variables (independent for initial version):
 - Solar insolation factor S ~ Normal(mu_S, sigma_S) truncated >=0
 - Biomass / chemical energy yield B ~ LogNormal(mu_B, sigma_B)
 - Actuator duty cycle fraction D ~ Beta(a_D, b_D)
 - Baseline parasitic load L (constant)

Net Energy (kWh) = (S * solar_capacity_kWh + B * biomass_capacity_kWh) - (D * actuator_load_kWh + L)

Outputs percentiles and failure probability (net < 0).
Future: introduce correlations, time-series storage, seasonal variation.
"""
from __future__ import annotations
import argparse, os, math, random, statistics
import numpy as np
import matplotlib.pyplot as plt
from sim_utils import build_metadata, save_results, register_figure

def truncated_normal(mu, sigma):
    while True:
        x = random.gauss(mu, sigma)
        if x >= 0:
            return x

def run_mc(n_samples: int, params):
    vals = []
    for _ in range(n_samples):
        # Optionally impose adversarial correlation pattern:
        # - Low solar S coincides with low biomass B and high actuator duty D (worst-case net energy)
        # Implemented by drawing a shared latent u and mapping to tails.
        if getattr(params, 'adverse_correlation', False):
            u = random.random()
            # Skew solar lower (invert CDF quantile weighting)
            S = truncated_normal(params.mu_S, params.sigma_S) * (0.3 + 0.7*u)  # scaled by u (favor lower average)
            # Biomass: lognormal, bias toward lower by mixing with u
            base_ln = random.gauss(params.mu_B, params.sigma_B)
            B = math.exp(base_ln) * (0.3 + 0.7*u)
            # Actuator: higher when solar is low -> use (1-u)
            # Generate beta via inverse-gamma trick but modulate shape
            D = random.gammavariate(params.a_D, 1) / (random.gammavariate(params.a_D,1) + random.gammavariate(params.b_D,1))
            D = min(0.999, max(0.0, 0.5*D + 0.5*(1-u)))
        else:
            S = truncated_normal(params.mu_S, params.sigma_S)
            B = math.exp(random.gauss(params.mu_B, params.sigma_B))  # lognormal
            # Beta(a,b)
            D = random.gammavariate(params.a_D, 1) / (random.gammavariate(params.a_D,1) + random.gammavariate(params.b_D,1))
        net = (S * params.solar_capacity_kWh + B * params.biomass_capacity_kWh) - (D * params.actuator_load_kWh + params.parasitic_load_kWh)
        vals.append(net)
    return vals

def summarize(vals):
    arr = sorted(vals)
    n = len(arr)
    def pct(p):
        k = int(p/100 * (n-1))
        return arr[k]
    failure_prob = sum(1 for v in arr if v < 0)/n
    return {
        'P5': pct(5), 'P50': pct(50), 'P95': pct(95), 'failure_prob': failure_prob,
        'mean': statistics.mean(arr), 'std': statistics.pstdev(arr)
    }

def plot_hist(vals, fig_dir):
    os.makedirs(fig_dir, exist_ok=True)
    plt.figure(figsize=(6,4))
    plt.hist(vals, bins=40, color='slateblue', alpha=0.85)
    plt.xlabel('Daily Net Energy (kWh)')
    plt.ylabel('Count')
    plt.title('Net Energy Distribution')
    plt.grid(alpha=.3)
    fig1 = os.path.join(fig_dir, 'energy_surplus_hist.png')
    plt.tight_layout(); plt.savefig(fig1, dpi=140); plt.close()
    return fig1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--samples', type=int, default=10000)
    ap.add_argument('--mu_S', type=float, default=1.0)
    ap.add_argument('--sigma_S', type=float, default=0.2)
    ap.add_argument('--mu_B', type=float, default=-0.3)
    ap.add_argument('--sigma_B', type=float, default=0.5)
    ap.add_argument('--a_D', type=float, default=2.0)
    ap.add_argument('--b_D', type=float, default=5.0)
    ap.add_argument('--solar_capacity_kWh', type=float, default=0.6)
    ap.add_argument('--biomass_capacity_kWh', type=float, default=0.3)
    ap.add_argument('--actuator_load_kWh', type=float, default=0.4)
    ap.add_argument('--parasitic_load_kWh', type=float, default=0.1)
    ap.add_argument('--fig_dir', type=str, default='paper/figures/simulations')
    ap.add_argument('--output_dir', type=str, default='simulations/results')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--sensitivity', action='store_true', help='Perform one-at-a-time sensitivity sweep (±10%) for key parameters')
    ap.add_argument('--adverse_correlation', action='store_true', help='Enable adversarial correlation stress test (low generation aligned with high loads)')
    ap.add_argument('--compare_adverse', action='store_true', help='If set, run both independent and adverse correlation scenarios and report delta in failure probability')
    args = ap.parse_args()
    random.seed(args.seed)
    vals = run_mc(args.samples, args)
    stats = summarize(vals)
    fig1 = plot_hist(vals, args.fig_dir)
    adverse_delta = None
    adverse_stats = None
    if args.compare_adverse and not args.adverse_correlation:
        adverse_args = argparse.Namespace(**vars(args))
        adverse_args.adverse_correlation = True
        adverse_vals = run_mc(args.samples, adverse_args)
        adverse_stats = summarize(adverse_vals)
        adverse_delta = adverse_stats['failure_prob'] - stats['failure_prob']
    sens_results = {}
    if args.sensitivity:
        base_params = ['solar_capacity_kWh','biomass_capacity_kWh','actuator_load_kWh','parasitic_load_kWh']
        delta = 0.10
        for p in base_params:
            original = getattr(args, p)
            for sign,label in [(1,'up'),(-1,'down')]:
                setattr(args, p, original * (1 + sign*delta))
                v2 = run_mc(int(args.samples/2), args)  # fewer samples for speed
                s2 = summarize(v2)
                sens_results[f'{p}_{label}'] = s2['P50']
            setattr(args, p, original)
        # Compute approximate influence as |Δ median| / baseline median
        influences = {}
        base_med = stats['P50']
        for p in base_params:
            up = sens_results[f'{p}_up']
            dn = sens_results[f'{p}_down']
            influences[p] = max(abs(up-base_med), abs(dn-base_med)) / base_med if base_med!=0 else 0
        # Rank influences
        ranked = sorted(influences.items(), key=lambda x: x[1], reverse=True)
    md = build_metadata('SIM-EN-MC', params={k: getattr(args,k) for k in ['samples','mu_S','sigma_S','mu_B','sigma_B','a_D','b_D','solar_capacity_kWh','biomass_capacity_kWh','actuator_load_kWh','parasitic_load_kWh','seed','adverse_correlation','compare_adverse'] if hasattr(args,k)}, notes='Energy balance Monte Carlo with optional adverse correlation stress test.')
    md['metrics'].update(stats)
    if adverse_stats:
        md['metrics']['adverse_stats'] = adverse_stats
        md['metrics']['adverse_failure_delta'] = adverse_delta
    if sens_results:
        md['metrics']['sensitivity_median'] = sens_results
        md['metrics']['influence_rank'] = ranked
    register_figure(md, fig1)
    out = save_results(md, args.output_dir)
    if args.verbose:
        print('Saved metadata:', out, '| Stats:', stats)

if __name__ == '__main__':
    main()
