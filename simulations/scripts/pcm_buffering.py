"""SIM-PCM-BUF: PCM thermal buffering simulation (lumped enthalpy model).

Simplified periodic heat input with latent heat region.

State Variables:
 - T (K)
 - Melt fraction f (0-1) when in phase change band [T_m - dT/2, T_m + dT/2]

Energy Balance (lumped):
 C_eff(T) dT/dt = Q_in(t) - hA (T - T_env) - Q_sink
 where C_eff includes latent heat contribution within melting band.

Variance reduction measured as RMS(T) compared to no-PCM case.
"""
from __future__ import annotations
import argparse, os, math
import numpy as np
import matplotlib.pyplot as plt
from sim_utils import build_metadata, save_results, register_figure

def run_sim(params, with_pcm: bool):
    dt = params.dt
    steps = int(params.t_end / dt)
    T = params.T_init
    f = 0.0  # melt fraction
    T_hist = []
    env = params.T_env
    band_low = params.T_m - params.dT_band/2
    band_high = params.T_m + params.dT_band/2
    for i in range(steps):
        t = i * dt
        # Periodic heat input (square wave duty)
        Q_in = params.Q_high if (t % params.period) < (params.duty * params.period) else params.Q_low
        # Effective heat capacity
        C = params.C_base
        if with_pcm and band_low <= T <= band_high:
            # Latent contribution scaled by fraction of band
            C += params.L_latent / params.dT_band
        # Convective loss
        Q_loss = params.hA * (T - env)
        # PCM phase change tracking
        if with_pcm and band_low <= T <= band_high:
            # Adjust melt fraction derivative approximate
            # df/dt * L_latent ≈ energy allocated to latent = min(Q_in, remaining latent capacity/time step)
            pass  # implicit via augmented C (Schumann approximation)
        dTdt = (Q_in - Q_loss)/C
        T += dTdt * dt
        T_hist.append(T)
    return np.array(T_hist)

def rms(arr):
    return np.sqrt(np.mean((arr - np.mean(arr))**2))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dt', type=float, default=0.5)
    ap.add_argument('--t_end', type=float, default=24*3600)
    ap.add_argument('--T_init', type=float, default=304.0)
    ap.add_argument('--T_env', type=float, default=300.0)
    ap.add_argument('--Q_high', type=float, default=180.0)
    ap.add_argument('--Q_low', type=float, default=10.0)
    ap.add_argument('--period', type=float, default=3600.0)
    ap.add_argument('--duty', type=float, default=0.5)
    ap.add_argument('--C_base', type=float, default=400.0)
    ap.add_argument('--L_latent', type=float, default=15000.0)
    ap.add_argument('--T_m', type=float, default=306.0)
    ap.add_argument('--dT_band', type=float, default=2.0)
    ap.add_argument('--latent_multipliers', type=float, nargs='*', default=[0.5,1.0,1.5,2.0], help='Sweep latent capacity scaling factors')
    ap.add_argument('--hA', type=float, default=15.0)
    ap.add_argument('--fig_dir', type=str, default='paper/figures/simulations')
    ap.add_argument('--output_dir', type=str, default='simulations/results')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()
    base = run_sim(args, with_pcm=False)
    pcm = run_sim(args, with_pcm=True)
    os.makedirs(args.fig_dir, exist_ok=True)
    t = np.arange(len(base))*args.dt/3600.0
    plt.figure(figsize=(8,4))
    plt.plot(t, base, label='No PCM', alpha=0.7)
    plt.plot(t, pcm, label='With PCM', lw=2)
    plt.xlabel('Time (h)')
    plt.ylabel('Temperature (K)')
    plt.title('PCM Buffering Effect')
    plt.legend(); plt.grid(alpha=.3)
    fig1 = os.path.join(args.fig_dir, 'pcm_buffering_temperature.png')
    plt.tight_layout(); plt.savefig(fig1, dpi=140); plt.close()
    # RMS comparison
    rms_base = rms(base)
    rms_pcm = rms(pcm)
    reduction = 1 - rms_pcm/rms_base if rms_base>0 else 0
    md = build_metadata('SIM-PCM-BUF', params={k: getattr(args,k) for k in ['dt','t_end','Q_high','Q_low','period','duty','C_base','L_latent','T_m','dT_band','hA']}, notes='Lumped enthalpy PCM buffering (approx latent via augmented C).')
    md['metrics']['rms_base'] = float(rms_base)
    md['metrics']['rms_pcm'] = float(rms_pcm)
    md['metrics']['variance_reduction'] = float(reduction)
    register_figure(md, fig1)
    # Sweep latent multipliers for variance reduction curve
    sweep_results=[]
    from types import SimpleNamespace
    for m in args.latent_multipliers:
        P = SimpleNamespace(**args.__dict__)
        P.L_latent = args.L_latent * m
        pcm_sweep=run_sim(P, with_pcm=True)
        rms_pcm_s = rms(pcm_sweep)
        reduction_s = 1 - rms_pcm_s/rms_base if rms_base>0 else 0
        sweep_results.append((m, reduction_s))
    # Plot sweep
    if len(sweep_results)>1:
        plt.figure(figsize=(6,4))
        plt.plot([m for m,_ in sweep_results],[r*100 for _,r in sweep_results],'o-',lw=2)
        plt.xlabel('Latent Capacity Multiplier')
        plt.ylabel('Variance Reduction (%)')
        plt.title('PCM Capacity Sensitivity')
        plt.grid(alpha=.3)
        fig2=os.path.join(args.fig_dir,'pcm_variance_reduction_sweep.png')
        plt.tight_layout(); plt.savefig(fig2, dpi=140); plt.close()
        register_figure(md, fig2)
        md['metrics']['variance_reduction_sweep']={str(m): r for m,r in sweep_results}
    out = save_results(md, args.output_dir)
    if args.verbose:
        print('Saved metadata:', out, '| Reduction:', reduction)

if __name__ == '__main__':
    main()
