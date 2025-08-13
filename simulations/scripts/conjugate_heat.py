"""SIM-HT-CONJ: Conjugate heat transfer & coupling efficiency simulation."""
from __future__ import annotations
import torch, numpy as np, argparse, os, math, matplotlib.pyplot as plt, copy, statistics
from publication_style import set_pub_style, save_fig
from sim_utils import build_metadata, save_results, register_figure

def stability_dt(dx, alpha):
    return 0.24 * dx * dx / alpha

def apply_convective_boundary(T, h, dx, rho, cp, dt, T_inf):
    """Approximate convective cooling by relaxing boundary cells toward ambient.

    NOTE: This mutates T in place. The factor derives from lumped node energy balance:
        (rho*cp*dx^2) dT/dt = - h * dx * (T - T_inf)  =>  dT = - h/(rho*cp*dx) * (T-T_inf) dt
    """
    coeff = h * dt / (rho * cp * dx)
    for sl in ( (0, slice(None)), (-1, slice(None)), (slice(None), 0), (slice(None), -1) ):
        T[sl] -= coeff * (T[sl] - T_inf)

def run_sim(diam_mm: float, args, device):
    Lx = args.domain_mm * 1e-3
    nx = ny = args.grid
    dx = Lx / nx
    alpha, rho, cp, h = args.alpha, args.rho, args.cp, args.h
    T_inf, power_W, steps = args.ambient_K, args.power_W, args.steps
    diam = diam_mm * 1e-3
    dt = min(stability_dt(dx, alpha), args.dt)
    if args.verbose:
        print(f"[D={diam_mm}mm] dt={dt:.3e}s")
    T = torch.full((nx, ny), T_inf, device=device)
    x = torch.linspace(0, Lx, nx, device=device)
    y = torch.linspace(0, Lx, ny, device=device)
    X, Y = torch.meshgrid(x, y, indexing='ij')
    cx = cy = Lx/2
    r = diam/2
    chamber_mask = (X - cx)**2 + (Y - cy)**2 <= r*r
    area = math.pi * r * r
    # Volumetric heat source (W/m^3)
    thickness = globals().get('_SIM_THICKNESS_M', 5e-3)
    q_vol = power_W / (area * thickness)
    # Temperature rise rate (K/s)
    source_coeff = q_vol / (rho * cp)
    kernel = torch.tensor([[0.,1.,0.],[1.,-4.,1.],[0.,1.,0.]], device=device).view(1,1,3,3)
    thickness = globals().get('_SIM_THICKNESS_M', 5e-3)
    vol_elem = dx * dx * thickness
    total_input = 0.0
    conv_loss = 0.0
    # Baseline stored energy (should be ~0 because initialized at ambient, kept for clarity)
    baseline_energy = 0.0
    times=[]; eff_series=[]; maxTs=[]; stored_series=[]; loss_series=[]; local_eff_series=[]
    boundary_mask = torch.zeros_like(T, dtype=torch.bool)
    boundary_mask[0,:]=True; boundary_mask[-1,:]=True; boundary_mask[:,0]=True; boundary_mask[:,-1]=True
    for step in range(steps):
        # Source deposition
        T[chamber_mask] += source_coeff * dt
        total_input += power_W * dt
        # Diffusion
        lap = torch.nn.functional.conv2d(T.unsqueeze(0).unsqueeze(0), kernel, padding=1).squeeze()
        T = T + alpha * dt / (dx * dx) * lap
        # Convection loss accounting
        if h > 0:
            E_before = ((T[boundary_mask]-T_inf) * rho * cp * vol_elem).sum().item()
            apply_convective_boundary(T, h, dx, rho, cp, dt, T_inf)
            E_after = ((T[boundary_mask]-T_inf) * rho * cp * vol_elem).sum().item()
            delta = E_before - E_after
            if delta > 0:
                conv_loss += delta
        else:
            apply_convective_boundary(T, h, dx, rho, cp, dt, T_inf)
        if step % args.save_interval == 0 or step == steps-1:
            stored_field = (T - T_inf).clamp(min=0)
            stored = (stored_field * rho * cp * vol_elem).sum().item()
            usable = max(0.0, stored - baseline_energy)
            # Local (chamber + annulus) mask
            annulus_factor = getattr(args, 'local_annulus_factor', 1.5)
            r_local = r * annulus_factor
            local_mask = (X - cx)**2 + (Y - cy)**2 <= r_local * r_local
            local_stored = (stored_field[local_mask] * rho * cp * vol_elem).sum().item()
            local_usable = max(0.0, local_stored)
            eff_input = min(1.0, max(0.0, usable/total_input if total_input>0 else 0))
            eff_loss = min(1.0, max(0.0, usable/(usable+conv_loss) if (usable+conv_loss)>0 else 0))
            eff_input_local = min(1.0, max(0.0, local_usable/total_input if total_input>0 else 0))
            eff_loss_local = min(1.0, max(0.0, local_usable/(local_usable+conv_loss) if (local_usable+conv_loss)>0 else 0))
            times.append(step*dt); eff_series.append({'input_eff': eff_input, 'retained_vs_loss': eff_loss}); local_eff_series.append({'input_eff_local': eff_input_local,'retained_vs_loss_local': eff_loss_local}); maxTs.append(float(T.max().item())); stored_series.append(usable); loss_series.append(conv_loss)
            if args.verbose:
                print(f"Step {step:5d} | MaxT {maxTs[-1]:.1f}K | Glob η_in={eff_input*100:5.2f}% | Loc η_in={eff_input_local*100:5.2f}%")
        # Safety: stop if runaway temperature reached
        if float(T.max().item()) > args.max_temperature_cap:
            if args.verbose:
                print(f"Stopping early at step {step} due to temperature cap {args.max_temperature_cap}K exceeded.")
            break
    return {
        'diameter_mm': diam_mm,
        'final_coupling_eff_input': eff_series[-1]['input_eff'],
        'final_coupling_eff_loss': eff_series[-1]['retained_vs_loss'],
        'final_local_eff_input': local_eff_series[-1]['input_eff_local'],
        'final_local_eff_loss': local_eff_series[-1]['retained_vs_loss_local'],
        'max_temperature_K': maxTs[-1],
        'time_s': times,
        'coupling_series': eff_series,
        'local_coupling_series': local_eff_series,
        'maxT_series': maxTs,
        'total_input_J': total_input,
        'conv_loss_J': conv_loss,
        'retained_J': eff_series[-1]['input_eff']*total_input,
        'stored_J_series': stored_series,
        'conv_loss_J_series': loss_series
    }

def plot_results(results, fig_dir, h):
    os.makedirs(fig_dir, exist_ok=True)
    set_pub_style()
    diam=[r['diameter_mm'] for r in results]
    coup_in=[r['final_coupling_eff_input']*100 for r in results]
    coup_loss=[r['final_coupling_eff_loss']*100 for r in results]
    coup_in_local=[r['final_local_eff_input']*100 for r in results]

    # Optional uncertainty (std) if replicate stats present
    coup_in_std=[(r.get('replicate_stats') or {}).get('global_input_eff_std_pct') for r in results]
    coup_in_local_std=[(r.get('replicate_stats') or {}).get('local_input_eff_std_pct') for r in results]

    plt.figure(figsize=(6,4));
    if any(s is not None for s in coup_in_std):
        # Error bars
        plt.errorbar(diam, coup_in, yerr=coup_in_std, fmt='o-', lw=2, capsize=4, label='Global Stored/Input (mean±1σ)')
    else:
        plt.plot(diam, coup_in, 'o-', lw=2, label='Global Stored/Input')
    if any(s is not None for s in coup_in_local_std):
        plt.errorbar(diam, coup_in_local, yerr=coup_in_local_std, fmt='s--', lw=2, capsize=4, label='Local Stored/Input (mean±1σ)')
    else:
        plt.plot(diam, coup_in_local, 's--', lw=2, label='Local Stored/Input')
    plt.xlabel('Chamber Diameter (mm)'); plt.ylabel('Efficiency (%)'); plt.title(f'Coupling vs Diameter (h={h})'); plt.legend(); plt.grid(alpha=.3)
    base1=os.path.join(fig_dir, f'coupling_vs_diameter_h{h}'); save_fig(plt.gcf(), base1); plt.close(); f1=base1+'.png'
    maxT=[r['max_temperature_K'] for r in results]
    plt.figure(figsize=(6,4)); plt.plot(diam, maxT, 's--', color='crimson', lw=2); plt.xlabel('Chamber Diameter (mm)'); plt.ylabel('Peak T (K)'); plt.title(f'Peak T vs Diameter (h={h})'); plt.grid(alpha=.3)
    base2=os.path.join(fig_dir, f'peakT_vs_diameter_h{h}'); save_fig(plt.gcf(), base2); plt.close(); f2=base2+'.png'
    # Time-series efficiency plot for first diameter (assumes same sampling times)
    if results:
        t = results[0]['time_s']
        glob = [pt['input_eff']*100 for pt in results[0]['coupling_series']]
        loc = [pt['input_eff_local']*100 for pt in results[0]['local_coupling_series']]
        plt.figure(figsize=(6,4))
        plt.plot(t, glob, 'o-', lw=2, label='Global Stored/Input')
        plt.plot(t, loc, 's--', lw=2, label='Local Stored/Input')
        plt.xlabel('Time (s)'); plt.ylabel('Efficiency (%)'); plt.title(f'Efficiency Evolution (h={h})'); plt.grid(alpha=.3); plt.legend()
        base3=os.path.join(fig_dir, f'coupling_timeseries_h{h}')
        save_fig(plt.gcf(), base3); plt.close(); f3=base3+'.png'
    else:
        f3=None
    return [f for f in [f1,f2,f3] if f]

def save_field_snapshot(T_tensor, fig_dir, tag):
    set_pub_style()
    plt.figure(figsize=(4,4))
    plt.imshow(T_tensor.cpu(), cmap='inferno')
    plt.colorbar(label='T (K)')
    plt.title(f'T Field {tag}')
    base=os.path.join(fig_dir, f'field_{tag}')
    save_fig(plt.gcf(), base)
    plt.close()
    return base+'.png'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--diameters', type=float, nargs='+', default=[2,4,8,12])
    ap.add_argument('--h', type=float, default=150.0)
    ap.add_argument('--alpha', type=float, default=1.4e-7)
    ap.add_argument('--rho', type=float, default=1000.0)
    ap.add_argument('--cp', type=float, default=4180.0)
    ap.add_argument('--ambient_K', type=float, default=298.0)
    ap.add_argument('--power_W', type=float, default=8.0)
    ap.add_argument('--domain_mm', type=float, default=80.0)
    ap.add_argument('--thickness_mm', type=float, default=5.0, help='Assumed slab thickness for energy accounting')
    ap.add_argument('--grid', type=int, default=256)
    ap.add_argument('--steps', type=int, default=3000)
    ap.add_argument('--dt', type=float, default=0.05)
    ap.add_argument('--save_interval', type=int, default=200)
    ap.add_argument('--snapshots', type=int, nargs='*', default=[-1], help='Time step indices (or -1 for final) to output field images for smallest diameter run')
    ap.add_argument('--local_annulus_factor', type=float, default=1.5, help='Multiplier on radius defining local energy capture region')
    ap.add_argument('--max_temperature_cap', type=float, default=500.0, help='Early stop if max T exceeds this (K) to prevent runaway unphysical values')
    ap.add_argument('--output_dir', type=str, default='simulations/results')
    ap.add_argument('--fig_dir', type=str, default='paper/figures/simulations')
    ap.add_argument('--device', type=str, default='auto')
    ap.add_argument('--verbose', action='store_true')
    # New validation / uncertainty arguments
    ap.add_argument('--replicates', type=int, default=1, help='Number of replicate stochastic runs (with param jitter) per diameter')
    ap.add_argument('--param_jitter_frac', type=float, default=0.02, help='Std dev fraction for Gaussian jitter applied to h and alpha for uncertainty')
    ap.add_argument('--refine_diameters', type=float, nargs='*', default=[], help='Diameters (mm) for which to perform grid refinement check')
    ap.add_argument('--refine_factor', type=int, default=2, help='Multiplicative factor for grid refinement (e.g., 2 -> 2x resolution)')
    ap.add_argument('--monotonic_tol', type=float, default=0.002, help='Tolerance for detecting monotonic violations in global efficiency (absolute fractional drop)')
    args=ap.parse_args()
    device=torch.device('cuda' if (args.device=='auto' and torch.cuda.is_available()) else ('cuda' if args.device=='cuda' else 'cpu'))
    if args.verbose: print('Device:', device)
    # Inject thickness into run_sim via closure (simpler than refactor): monkey patch global used volume element scaling
    global _SIM_THICKNESS_M
    _SIM_THICKNESS_M = args.thickness_mm * 1e-3
    results=[]
    field_figs=[]
    # Implement snapshot capture for smallest diameter by re-running with recording if needed
    snapshot_diams = set()
    want_snapshots = any(s >= 0 for s in args.snapshots) or (-1 in args.snapshots)
    for idx, d in enumerate(args.diameters):
        if idx==0 and want_snapshots:
            # temporary inline recorder: run simulation while storing specified steps
            Lx = args.domain_mm * 1e-3
            nx = ny = args.grid
            dx = Lx / nx
            alpha, rho, cp, h = args.alpha, args.rho, args.cp, args.h
            T_inf, power_W, steps = args.ambient_K, args.power_W, args.steps
            diam = d * 1e-3
            dt = min(stability_dt(dx, alpha), args.dt)
            T = torch.full((nx, ny), T_inf, device=device)
            x = torch.linspace(0, Lx, nx, device=device)
            y = torch.linspace(0, Lx, ny, device=device)
            X, Y = torch.meshgrid(x, y, indexing='ij')
            cx = cy = Lx/2
            r = diam/2
            chamber_mask = (X - cx)**2 + (Y - cy)**2 <= r*r
            area = math.pi * r * r
            thickness = _SIM_THICKNESS_M
            q_vol = power_W / (area * thickness)
            source_coeff = q_vol / (rho * cp)
            kernel = torch.tensor([[0.,1.,0.],[1.,-4.,1.],[0.,1.,0.]], device=device).view(1,1,3,3)
            vol_elem = dx * dx * thickness
            total_input = 0.0; conv_loss=0.0; baseline_energy=0.0
            boundary_mask = torch.zeros_like(T, dtype=torch.bool)
            boundary_mask[0,:]=True; boundary_mask[-1,:]=True; boundary_mask[:,0]=True; boundary_mask[:,-1]=True
            snapshot_steps = set([s for s in args.snapshots if s>=0])
            for step in range(steps):
                T[chamber_mask] += source_coeff * dt
                total_input += power_W * dt
                lap = torch.nn.functional.conv2d(T.unsqueeze(0).unsqueeze(0), kernel, padding=1).squeeze()
                T = T + alpha * dt / (dx * dx) * lap
                if h>0:
                    E_before = ((T[boundary_mask]-T_inf) * rho * cp * vol_elem).sum().item()
                    apply_convective_boundary(T, h, dx, rho, cp, dt, T_inf)
                    E_after = ((T[boundary_mask]-T_inf) * rho * cp * vol_elem).sum().item()
                    delta = E_before - E_after
                    if delta>0: conv_loss += delta
                else:
                    apply_convective_boundary(T, h, dx, rho, cp, dt, T_inf)
                if step in snapshot_steps:
                    tag=f'd{d}mm_t{step}'
                    fp=save_field_snapshot(T, args.fig_dir, tag)
                    field_figs.append(fp)
            # final snapshot
            if -1 in args.snapshots:
                tag=f'd{d}mm_final'
                fp=save_field_snapshot(T, args.fig_dir, tag)
                field_figs.append(fp)
            # compute metrics equivalent to run_sim for consistency (reuse code path by calling run_sim to avoid divergence)
            res = run_sim(d, args, device)
        else:
            res = run_sim(d, args, device)

        # Replicates with jitter for uncertainty quantification
        if args.replicates > 1:
            glob_eff=[]; loc_eff=[]
            for r_id in range(args.replicates-1):  # already have one base run
                jitter_alpha = args.alpha * (1.0 + np.random.normal(0, args.param_jitter_frac))
                jitter_h = args.h * (1.0 + np.random.normal(0, args.param_jitter_frac))
                jitter_args = copy.deepcopy(args)
                jitter_args.alpha = float(jitter_alpha)
                jitter_args.h = float(jitter_h)
                jitter_res = run_sim(d, jitter_args, device)
                glob_eff.append(jitter_res['final_coupling_eff_input'])
                loc_eff.append(jitter_res['final_local_eff_input'])
            # include base run
            glob_eff.append(res['final_coupling_eff_input'])
            loc_eff.append(res['final_local_eff_input'])
            mean_glob = float(np.mean(glob_eff)); std_glob = float(np.std(glob_eff))
            mean_loc = float(np.mean(loc_eff)); std_loc = float(np.std(loc_eff))
            res['replicate_stats']={
                'global_input_eff_mean': mean_glob,
                'global_input_eff_std': std_glob,
                'global_input_eff_std_pct': std_glob*100.0,
                'local_input_eff_mean': mean_loc,
                'local_input_eff_std': std_loc,
                'local_input_eff_std_pct': std_loc*100.0,
                'replicates': args.replicates
            }

        # Optional grid refinement study
        if d in args.refine_diameters:
            refine_args = copy.deepcopy(args)
            refine_args.grid = int(refine_args.grid * args.refine_factor)
            refine_res = run_sim(d, refine_args, device)
            res['refine']={
                'grid': args.grid,
                'refined_grid': refine_args.grid,
                'base_eff': res['final_coupling_eff_input'],
                'refined_eff': refine_res['final_coupling_eff_input'],
                'abs_diff': abs(refine_res['final_coupling_eff_input'] - res['final_coupling_eff_input']),
                'rel_diff_frac': abs(refine_res['final_coupling_eff_input'] - res['final_coupling_eff_input'])/max(1e-9,res['final_coupling_eff_input'])
            }
        results.append(res)
    figs=plot_results(results, args.fig_dir, args.h)
    md=build_metadata('SIM-HT-CONJ', params={
        'diameters_mm': args.diameters,'h_Wm2K': args.h,'alpha': args.alpha,'rho': args.rho,'cp': args.cp,
    'power_W': args.power_W,'domain_mm': args.domain_mm,'grid': args.grid,'steps': args.steps,'dt': args.dt,'thickness_mm': args.thickness_mm
    }, notes='Initial conjugate heat explicit solver.')
    md['metrics']['coupling_efficiency_input']={f"{r['diameter_mm']}mm": r['final_coupling_eff_input'] for r in results}
    md['metrics']['coupling_efficiency_loss']={f"{r['diameter_mm']}mm": r['final_coupling_eff_loss'] for r in results}
    md['metrics']['local_coupling_efficiency_input']={f"{r['diameter_mm']}mm": r['final_local_eff_input'] for r in results}
    md['metrics']['local_coupling_efficiency_loss']={f"{r['diameter_mm']}mm": r['final_local_eff_loss'] for r in results}
    md['metrics']['max_temperatures_K']={f"{r['diameter_mm']}mm": r['max_temperature_K'] for r in results}
    # Replicate & refinement metrics
    for r in results:
        tag=f"{r['diameter_mm']}mm"
        if 'replicate_stats' in r:
            md['metrics'][f'replicate_stats_{tag}']=r['replicate_stats']
        if 'refine' in r:
            md['metrics'][f'refine_{tag}']=r['refine']
    # Monotonicity diagnostics (global input efficiency expected non-decreasing with diameter; relaxed tolerance)
    effs=[r['final_coupling_eff_input'] for r in results]
    violations=[]
    for i in range(len(effs)-1):
        if effs[i+1] + args.monotonic_tol < effs[i]:
            violations.append({'index': i, 'd1_mm': results[i]['diameter_mm'], 'd2_mm': results[i+1]['diameter_mm'], 'drop': effs[i]-effs[i+1]})
    md['metrics']['monotonic_expected']='non-decreasing'
    md['metrics']['monotonic_violations_count']=len(violations)
    if violations:
        md['metrics']['monotonic_violations']=violations
    # Aggregate refinement summary
    refine_rel_diffs=[r['refine']['rel_diff_frac'] for r in results if 'refine' in r]
    if refine_rel_diffs:
        md['metrics']['refinement_max_rel_diff']=max(refine_rel_diffs)
        md['metrics']['refinement_mean_rel_diff']=float(np.mean(refine_rel_diffs))
    for fp in figs: register_figure(md, fp)
    for fp in field_figs: register_figure(md, fp)
    out=save_results(md, args.output_dir)
    if args.verbose: print('Saved:', out)

if __name__=='__main__':
    main()
