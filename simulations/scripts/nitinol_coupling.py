"""SIM-ACT-NIT: Nitinol actuation energy reduction via preheating.

Model:
 - Lumped thermal mass for actuator: C_th (J/K)
 - Ambient T_env; target actuation temperature T_active
 - Waste heat provides baseline preheat raising T_base above T_env.
 - Electrical pulse supplies remaining energy to reach T_active, then hold for t_hold with losses hA (T - T_env).

We compare electrical energy per cycle with and without waste heat preheating.
Simplified (no phase transformation hysteresis modeling).
"""
from __future__ import annotations
import argparse, os
import numpy as np
import matplotlib.pyplot as plt
from sim_utils import build_metadata, save_results, register_figure

def energy_per_cycle(C_th, hA, T_env, T_base, T_active, t_ramp, t_hold):
    # Energy to raise from T_base to T_active
    dT = max(0.0, T_active - T_base)
    E_ramp = C_th * dT
    # Holding losses approximated linear over hold period (constant temp maintained)
    E_hold = hA * (T_active - T_env) * t_hold
    return E_ramp + E_hold

def sweep(params):
    ratios = []
    bases = []
    improved = []
    for T_base in params.preheat_range:
        E_base = energy_per_cycle(params.C_th, params.hA, params.T_env, params.T_env, params.T_active, params.t_ramp, params.t_hold)
        E_pre  = energy_per_cycle(params.C_th, params.hA, params.T_env, T_base, params.T_active, params.t_ramp, params.t_hold)
        ratio = E_pre / E_base if E_base>0 else 0
        ratios.append(ratio)
        bases.append(T_base)
        improved.append(E_base - E_pre)
    return bases, ratios, improved

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--C_th', type=float, default=25.0)
    ap.add_argument('--hA', type=float, default=0.4)
    ap.add_argument('--T_env', type=float, default=295.0)
    ap.add_argument('--T_active', type=float, default=335.0)
    ap.add_argument('--t_ramp', type=float, default=2.0)
    ap.add_argument('--t_hold', type=float, default=4.0)
    ap.add_argument('--preheat_range', type=float, nargs='+', default=[295,300,305,310,315,320])
    ap.add_argument('--fig_dir', type=str, default='paper/figures/simulations')
    ap.add_argument('--output_dir', type=str, default='simulations/results')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()
    bases, ratios, improved = sweep(args)
    os.makedirs(args.fig_dir, exist_ok=True)
    plt.figure(figsize=(6,4))
    plt.plot(bases, [1-r for r in ratios], 'o-', lw=2)
    plt.xlabel('Preheat Temperature (K)')
    plt.ylabel('Electrical Energy Reduction Fraction')
    plt.title('Nitinol Actuation Energy Savings vs Preheat')
    plt.grid(alpha=.3)
    fig1 = os.path.join(args.fig_dir, 'nitinol_energy_savings.png')
    plt.tight_layout(); plt.savefig(fig1, dpi=140); plt.close()
    md = build_metadata('SIM-ACT-NIT', params={k:getattr(args,k) for k in ['C_th','hA','T_env','T_active','t_ramp','t_hold','preheat_range']}, notes='Simplified nitinol energy per cycle vs preheat temperature.')
    md['metrics']['energy_reduction_vs_preheat'] = {str(b): 1-r for b,r in zip(bases, ratios)}
    md['metrics']['max_reduction_fraction'] = max(1-r for r in ratios)
    register_figure(md, fig1)
    out = save_results(md, args.output_dir)
    if args.verbose:
        print('Saved metadata:', out)

if __name__ == '__main__':
    main()
