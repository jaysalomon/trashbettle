"""SIM-OPT-LAT: Multi-objective lattice optimization (lightweight GA).

Objectives (all minimized; we negate stiffness to transform to minimization):
 1. pressure_proxy = 1/d^4 (minimize)
 2. inv_surface_density = 1/(1/(d * t)) => effectively minimizing inverse surface density maximizes real surface density
 3. neg_stiffness_index = -stiffness_index so minimizing gives maximal stiffness

Enhancements in this revision:
 - Properly named Pareto front figure (`lattice_pareto_front.png`).
 - Added Monte Carlo hypervolume estimate ("hv_estimate") for the non-dominated front relative to a reference point
     automatically chosen as 1.05 * max(objective) along each axis (slightly outside worst point) unless overridden.
 - CLI parameters: --hv_samples, --ref_pressure, --ref_inv_surface, --ref_neg_stiffness for reproducible HV calculations.
"""
from __future__ import annotations
import argparse, os, random, math
import matplotlib.pyplot as plt
from sim_utils import build_metadata, save_results, register_figure
from typing import List, Dict, Any

def random_ind(rng):
    cell_d = rng.uniform(1.5e-3, 6e-3)
    strut_t = rng.uniform(0.3e-3, 1.2e-3)
    porosity = rng.uniform(0.3, 0.7)
    return {'cell_d': cell_d, 'strut_t': strut_t, 'porosity': porosity}

def evaluate(ind):
    cell_d = ind['cell_d']; strut_t = ind['strut_t']; porosity = ind['porosity']
    pressure_proxy = 1 / (cell_d**4)
    surface_density = 1 / (cell_d * strut_t)
    stiffness_index = (1-porosity)**2 * (strut_t / cell_d)
    ind['pressure_proxy'] = pressure_proxy
    ind['inv_surface_density'] = 1/surface_density
    ind['neg_stiffness_index'] = -stiffness_index
    return ind

def pareto_filter(designs):
    front = []
    for d in designs:
        dominated = False
        for e in designs:
            if e is d: continue
            # e dominates d if all objectives <= and one strictly <
            if (e['pressure_proxy'] <= d['pressure_proxy'] and
                e['inv_surface_density'] <= d['inv_surface_density'] and
                e['neg_stiffness_index'] <= d['neg_stiffness_index'] and
                (e['pressure_proxy'] < d['pressure_proxy'] or e['inv_surface_density'] < d['inv_surface_density'] or e['neg_stiffness_index'] < d['neg_stiffness_index'])):
                dominated = True
                break
        if not dominated:
            front.append(d)
    return front

def plot_front(front: List[Dict[str,Any]], fig_dir: str):
    os.makedirs(fig_dir, exist_ok=True)
    pp = [d['pressure_proxy'] for d in front]
    isd = [d['inv_surface_density'] for d in front]
    sti = [-d['neg_stiffness_index'] for d in front]
    plt.figure(figsize=(6,4))
    sc = plt.scatter(pp, isd, c=sti, cmap='plasma', edgecolor='k')
    plt.xlabel('Pressure Drop Proxy')
    plt.ylabel('Inverse Surface Density')
    cbar = plt.colorbar(sc); cbar.set_label('Stiffness Index (proxy)')
    plt.title('Lattice Pareto Front')
    plt.grid(alpha=.3)
    fig1 = os.path.join(fig_dir, 'lattice_pareto_front.png')
    plt.tight_layout(); plt.savefig(fig1, dpi=140); plt.close()
    return fig1

def estimate_hypervolume(front: List[Dict[str,Any]], ref_point: tuple, samples: int, rng: random.Random) -> float:
    """Monte Carlo estimate of 3D hypervolume (objectives minimized) dominated by the front.

    We uniformly sample the axis-aligned box between the ideal point (component-wise min across front)
    and the reference point (ref_point). The fraction of samples dominated by at least one Pareto point
    times the box volume gives an HV estimate. This is coarse but stable enough for tracking relative improvement.
    """
    if not front:
        return 0.0
    # Construct ideal point and ensure reference point is worse in all objectives
    p_min = min(d['pressure_proxy'] for d in front)
    s_min = min(d['inv_surface_density'] for d in front)
    n_min = min(d['neg_stiffness_index'] for d in front)
    p_ref, s_ref, n_ref = ref_point
    # Guard: if ref_point is not strictly worse, expand it slightly
    eps = 1e-9
    if p_ref <= p_min: p_ref = p_min + abs(p_min)*0.05 + eps
    if s_ref <= s_min: s_ref = s_min + abs(s_min)*0.05 + eps
    if n_ref <= n_min: n_ref = n_min + abs(n_min)*0.05 + eps
    vol_box = (p_ref - p_min) * (s_ref - s_min) * (n_ref - n_min)
    if vol_box <= 0:
        return 0.0
    dominated = 0
    for _ in range(samples):
        rp = p_min + rng.random() * (p_ref - p_min)
        rs = s_min + rng.random() * (s_ref - s_min)
        rn = n_min + rng.random() * (n_ref - n_min)
        # A sample point is dominated if some front point has all objectives <=
        for d in front:
            if (d['pressure_proxy'] <= rp and d['inv_surface_density'] <= rs and d['neg_stiffness_index'] <= rn):
                dominated += 1
                break
    return dominated / samples * vol_box

def sbx_crossover(a, b, rng, eta=15):
    child = {}
    for k in ['cell_d','strut_t','porosity']:
        x1, x2 = a[k], b[k]
        if rng.random() < 0.5:
            if abs(x1 - x2) < 1e-12:
                child[k] = x1
            else:
                x_low, x_high = min(x1,x2), max(x1,x2)
                u = rng.random()
                beta = (2*u)**(1/(eta+1)) if u <= 0.5 else (1/(2*(1-u)))**(1/(eta+1))
                child_val = 0.5*((x1+x2) - beta*(x2 - x1)) if rng.random()<0.5 else 0.5*((x1+x2) + beta*(x2 - x1))
                child[k] = child_val
        else:
            child[k] = x1
    # parameter bounds
    child['cell_d'] = min(max(child['cell_d'],1.5e-3),6e-3)
    child['strut_t'] = min(max(child['strut_t'],0.3e-3),1.2e-3)
    child['porosity'] = min(max(child['porosity'],0.3),0.7)
    return child

def mutate(ind, rng, p=0.2):
    for k, (lo, hi) in {'cell_d':(1.5e-3,6e-3),'strut_t':(0.3e-3,1.2e-3),'porosity':(0.3,0.7)}.items():
        if rng.random()<p:
            ind[k] = rng.uniform(lo, hi)
    return ind

def dominates(a,b):
    better_or_eq = (a['pressure_proxy'] <= b['pressure_proxy'] and a['inv_surface_density'] <= b['inv_surface_density'] and a['neg_stiffness_index'] <= b['neg_stiffness_index'])
    strictly_better = (a['pressure_proxy'] < b['pressure_proxy'] or a['inv_surface_density'] < b['inv_surface_density'] or a['neg_stiffness_index'] < b['neg_stiffness_index'])
    return better_or_eq and strictly_better

def fast_non_dominated(pop):
    N=len(pop)
    S=[[] for _ in range(N)]
    n=[0]*N
    fronts=[]
    for i,p in enumerate(pop):
        for j,q in enumerate(pop):
            if i==j: continue
            if dominates(p,q):
                S[i].append(j)
            elif dominates(q,p):
                n[i]+=1
        if n[i]==0:
            p['rank']=0
    current=[i for i in range(N) if n[i]==0]
    rank=0
    while current:
        front=[pop[i] for i in current]
        fronts.append(front)
        next_indices=[]
        for i_idx in current:
            for q_idx in S[i_idx]:
                n[q_idx]-=1
                if n[q_idx]==0:
                    pop[q_idx]['rank']=rank+1
                    next_indices.append(q_idx)
        current=next_indices
        rank+=1
    return fronts

def crowding(front):
    for p in front:
        p['crowd']=0.0
    for key in ['pressure_proxy','inv_surface_density','neg_stiffness_index']:
        front.sort(key=lambda x:x[key])
        front[0]['crowd']=front[-1]['crowd']=float('inf')
        vals=[f[key] for f in front]
        vmin,vmax=min(vals),max(vals)
        if vmax==vmin: continue
        for i in range(1,len(front)-1):
            front[i]['crowd'] += (vals[i+1]-vals[i-1])/(vmax-vmin)
    return front

def select(pop, rng, size):
    chosen=[]
    while len(chosen)<size:
        a,b=rng.sample(pop,2)
        # Tournament by rank then crowding
        if (a['rank']<b['rank']) or (a['rank']==b['rank'] and a['crowd']>b['crowd']):
            chosen.append(a)
        else:
            chosen.append(b)
    return chosen

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pop', type=int, default=120)
    ap.add_argument('--gens', type=int, default=40)
    ap.add_argument('--seed', type=int, default=2025)
    ap.add_argument('--fig_dir', type=str, default='paper/figures/simulations')
    ap.add_argument('--output_dir', type=str, default='simulations/results')
    ap.add_argument('--verbose', action='store_true')
    ap.add_argument('--hv_samples', type=int, default=20000, help='Samples for Monte Carlo hypervolume estimate')
    ap.add_argument('--ref_pressure', type=float, default=None, help='Override reference point pressure objective')
    ap.add_argument('--ref_inv_surface', type=float, default=None, help='Override reference point inv surface objective')
    ap.add_argument('--ref_neg_stiffness', type=float, default=None, help='Override reference point neg stiffness objective')
    args=ap.parse_args()
    rng=random.Random(args.seed)
    pop=[evaluate(random_ind(rng)) for _ in range(args.pop)]
    for g in range(args.gens):
        fronts=fast_non_dominated(pop)
        for f in fronts:
            crowding(f)
        parents=select(pop, rng, args.pop)
        children=[]
        for i in range(0,args.pop,2):
            a=parents[i]; b=parents[min(i+1,args.pop-1)]
            c1=mutate(evaluate(sbx_crossover(a,b,rng)), rng)
            c2=mutate(evaluate(sbx_crossover(b,a,rng)), rng)
            children.append(c1); children.append(c2)
        pop=parents+children
        # Environmental selection
        new_pop=[]
        fronts=fast_non_dominated(pop)
        for f in fronts:
            crowding(f)
            if len(new_pop)+len(f) <= args.pop:
                new_pop.extend(f)
            else:
                f.sort(key=lambda x:(x['rank'],-x['crowd']))
                needed=args.pop-len(new_pop)
                new_pop.extend(f[:needed])
                break
        pop=new_pop
        if args.verbose and g%10==0:
            print(f'Gen {g} | Front0 size={len([p for p in pop if p.get("rank",99)==0])}')
    final_front=[p for p in pop if p.get('rank',99)==0]
    fig1=plot_front(final_front, args.fig_dir)
    # Determine reference point (worst objectives * 1.05) unless overridden
    p_worst=max(d['pressure_proxy'] for d in final_front)
    s_worst=max(d['inv_surface_density'] for d in final_front)
    n_worst=max(d['neg_stiffness_index'] for d in final_front)
    ref_point=(
        args.ref_pressure if args.ref_pressure is not None else p_worst*1.05,
        args.ref_inv_surface if args.ref_inv_surface is not None else s_worst*1.05,
        args.ref_neg_stiffness if args.ref_neg_stiffness is not None else n_worst*1.05,
    )
    hv_est=estimate_hypervolume(final_front, ref_point, args.hv_samples, rng)
    md=build_metadata('SIM-OPT-LAT', params={'pop':args.pop,'gens':args.gens,'seed':args.seed,'hv_samples':args.hv_samples}, notes='GA multi-objective lattice optimizer (NSGA-II lite) with Monte Carlo HV estimate.')
    md['metrics']['front_size']=len(final_front)
    md['metrics']['hypervolume_mc']=hv_est
    md['metrics']['hypervolume_ref_point']={'pressure':ref_point[0],'inv_surface':ref_point[1],'neg_stiffness':ref_point[2]}
    # Legacy proxy retained for trend continuity
    hv_proxy=sum(1.0/(1.0+p['crowd'] if p['crowd']!=float('inf') else 1.0) for p in final_front)
    md['metrics']['hypervolume_proxy']=hv_proxy
    register_figure(md, fig1)
    out=save_results(md, args.output_dir)
    if args.verbose:
        print('Saved metadata:', out, '| Front size:', len(final_front), '| HV_est:', hv_est, '| HV_proxy:', hv_proxy)

if __name__ == '__main__':
    main()
