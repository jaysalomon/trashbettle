"""SIM-STR-MODAL: Modal & stiffness approximation for lattice vs solid plate.

Initial surrogate model (analytical scaling) -- NOT a full FEA.

Approach:
 - Model first bending mode frequency of a rectangular plate f ~ (k * t / L^2) * sqrt(E/ρ)
 - Lattice introduces: porosity φ, effective modulus E_eff = E*(1-φ)^n, effective density ρ_eff = ρ*(1-φ)
 - Empirical exponent n ~ 2 for many open lattices (adjustable).
 - We sweep porosity and thickness ratios to estimate frequency gain and mass savings.

Metrics:
 - f_ratio = f_lattice / f_solid
 - mass_ratio = m_lattice / m_solid
 - stiffness_index = f_ratio / mass_ratio (proxy for dynamic performance per mass)

Future upgrades:
 - Replace with SfePy shell model.
 - Damping estimation via joint/micro-structure friction model.
"""
from __future__ import annotations
import argparse, os, math
import matplotlib.pyplot as plt
from sim_utils import build_metadata, save_results, register_figure

def compute_frequency(E, rho, t, L, k_coeff=1.0):
    return k_coeff * t / (L*L) * math.sqrt(E / rho)

def run_sweep(E: float, rho: float, L: float, t: float, porosities, thickness_ratios, n_exp: float, k_coeff: float):
    base_f = compute_frequency(E, rho, t, L, k_coeff)
    base_mass = rho * t  # per unit area (ignore area multiplicative constant)
    results = []
    for phi in porosities:
        E_eff = E * (1 - phi)**n_exp
        rho_eff = rho * (1 - phi)
        for tr in thickness_ratios:
            t_eff = t * tr
            f_lat = compute_frequency(E_eff, rho_eff, t_eff, L, k_coeff)
            mass_lat = rho_eff * t_eff
            f_ratio = f_lat / base_f
            mass_ratio = mass_lat / base_mass
            stiffness_index = f_ratio / mass_ratio if mass_ratio>0 else 0
            results.append({
                'porosity': phi,
                'thickness_ratio': tr,
                'f_ratio': f_ratio,
                'mass_ratio': mass_ratio,
                'stiffness_index': stiffness_index
            })
    return results

def plot_results(results, fig_dir):
    os.makedirs(fig_dir, exist_ok=True)
    # Scatter of f_ratio vs mass_ratio colored by porosity
    import matplotlib.pyplot as plt
    por = [r['porosity'] for r in results]
    fr = [r['f_ratio'] for r in results]
    mr = [r['mass_ratio'] for r in results]
    si = [r['stiffness_index'] for r in results]
    plt.figure(figsize=(6,4))
    sc = plt.scatter(mr, fr, c=por, cmap='viridis', s=40, edgecolor='k')
    plt.xlabel('Mass Ratio (lattice/solid)')
    plt.ylabel('Frequency Ratio (lattice/solid)')
    plt.title('Modal Frequency vs Mass Trade Space')
    cbar = plt.colorbar(sc); cbar.set_label('Porosity')
    plt.grid(alpha=.3)
    fig1 = os.path.join(fig_dir, 'modal_frequency_trade.png')
    plt.tight_layout(); plt.savefig(fig1, dpi=140); plt.close()
    # Stiffness index heatmap (porosity vs thickness_ratio)
    import numpy as np
    por_vals = sorted(set(por))
    th_vals = sorted(set(r['thickness_ratio'] for r in results))
    M = np.zeros((len(por_vals), len(th_vals)))
    for r in results:
        i = por_vals.index(r['porosity'])
        j = th_vals.index(r['thickness_ratio'])
        M[i,j] = r['stiffness_index']
    plt.figure(figsize=(6,4))
    im = plt.imshow(M, origin='lower', aspect='auto', cmap='magma',
                    extent=[min(th_vals), max(th_vals), min(por_vals), max(por_vals)])
    plt.xlabel('Thickness Ratio')
    plt.ylabel('Porosity')
    plt.title('Stiffness Index f_ratio/mass_ratio')
    cbar = plt.colorbar(im); cbar.set_label('Stiffness Index')
    fig2 = os.path.join(fig_dir, 'stiffness_index_heatmap.png')
    plt.tight_layout(); plt.savefig(fig2, dpi=140); plt.close()
    return [fig1, fig2]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--E', type=float, default=2.5e9, help='Base material modulus (Pa)')
    ap.add_argument('--rho', type=float, default=1100.0, help='Base density (kg/m3)')
    ap.add_argument('--L', type=float, default=0.25, help='Plate length (m)')
    ap.add_argument('--t', type=float, default=0.004, help='Plate thickness (m)')
    ap.add_argument('--porosities', type=float, nargs='+', default=[0.3,0.4,0.5,0.6,0.7])
    ap.add_argument('--thickness_ratios', type=float, nargs='+', default=[0.6,0.7,0.8,0.9,1.0])
    ap.add_argument('--n_exp', type=float, default=2.0)
    ap.add_argument('--k_coeff', type=float, default=1.0)
    ap.add_argument('--fig_dir', type=str, default='paper/figures/simulations')
    ap.add_argument('--output_dir', type=str, default='simulations/results')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()
    results = run_sweep(args.E, args.rho, args.L, args.t, args.porosities, args.thickness_ratios, args.n_exp, args.k_coeff)
    figs = plot_results(results, args.fig_dir)
    # Identify best stiffness index
    best = max(results, key=lambda r: r['stiffness_index'])
    md = build_metadata('SIM-STR-MODAL', params={
        'E': args.E, 'rho': args.rho, 'L': args.L, 't': args.t,
        'porosities': args.porosities, 'thickness_ratios': args.thickness_ratios,
        'n_exp': args.n_exp
    }, notes='Analytical scaling surrogate for first modal frequency & mass.')
    md['metrics']['best_config'] = best
    # Summary stats
    md['metrics']['max_f_ratio'] = max(r['f_ratio'] for r in results)
    md['metrics']['min_mass_ratio'] = min(r['mass_ratio'] for r in results)
    for f in figs: register_figure(md, f)
    out = save_results(md, args.output_dir)
    if args.verbose:
        print('Saved metadata:', out)

if __name__ == '__main__':
    main()
