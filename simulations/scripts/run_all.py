"""Run all implemented simulation scripts with default parameters and build a summary JSON.

This orchestrator executes each simulation as a subprocess so argument parsers work unchanged.
It then scans `simulations/results` for the most recent JSON per SIM ID and aggregates
selected metrics into `simulations/results/sim_summary_latest.json`.

Prerequisites: python -m pip install -r requirements.txt
"""
from __future__ import annotations
import subprocess, json, os, datetime, glob, sys, argparse

SIM_SCRIPTS = [
    ('SIM-HT-CONJ', 'conjugate_heat.py'),
    ('SIM-HT-MULTI', 'multi_chamber_heat.py'),
    ('SIM-FL-NET', 'hydraulic_network.py'),
    ('SIM-STR-MODAL', 'structural_modal.py'),
    ('SIM-EN-MC', 'energy_balance_mc.py'),
    ('SIM-PCM-BUF', 'pcm_buffering.py'),
    ('SIM-ACT-NIT', 'nitinol_coupling.py'),
    ('SIM-RES-FAIL', 'resilience_study.py'),
    ('SIM-OPT-LAT', 'lattice_optimizer.py'),
]

RESULT_DIR = os.path.join('simulations','results')
SCRIPT_DIR = os.path.dirname(__file__)

def run_script(script_name: str, extra_args):
    path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.isfile(path):
        print(f"[WARN] Missing script {script_name}")
        return False
    print(f"[RUN] python {script_name}")
    try:
        cmd = [sys.executable, path] + extra_args
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {script_name} failed: {e}")
        return False

def latest_json_for(sim_id: str):
    pattern = os.path.join(RESULT_DIR, f"sim_{sim_id}_*.json")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def extract_metrics(fpath: str):
    try:
        with open(fpath,'r') as f:
            data = json.load(f)
        return {
            'id': data.get('id'),
            'timestamp': data.get('timestamp'),
            'metrics': data.get('metrics', {}),
            'figures': data.get('figures', [])
        }
    except Exception as e:
        return {'error': str(e), 'file': fpath}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--device', type=str, default='auto', help='Forward device to GPU-capable sims')
    ap.add_argument('--cycle_tag', type=str, default=None, help='Label for this batch (embedded in figure filenames via suffix)')
    args = ap.parse_args()
    os.makedirs(RESULT_DIR, exist_ok=True)
    summary = {
        'generated_at': datetime.datetime.utcnow().isoformat()+"Z",
        'simulations': []
    }
    tag = args.cycle_tag or datetime.datetime.utcnow().strftime('CYCLE%Y%m%dT%H%M%S')
    os.environ['SIM_CYCLE_TAG'] = tag
    for sim_id, script in SIM_SCRIPTS:
        extra = []
        if script in ('conjugate_heat.py','multi_chamber_heat.py'):
            extra += ['--device', args.device]
        # Parameter tuning for realism (override defaults)
        if script == 'conjugate_heat.py':
            extra += ['--h','150','--power_W','6','--max_temperature_cap','500']
        if script == 'multi_chamber_heat.py':
            extra += ['--steps','1500']
        if script == 'hydraulic_network.py':
            extra += ['--variance','0.05','--trials','80']
        if script == 'pcm_buffering.py':
            extra += ['--Q_high','180','--Q_low','10','--L_latent','15000','--T_m','306','--dT_band','2']
        if script == 'energy_balance_mc.py':
            extra += ['--sensitivity']
        if script == 'lattice_optimizer.py':
            extra += ['--gens','25','--pop','100']
        ok = run_script(script, extra)
        latest = latest_json_for(sim_id)
        if latest:
            summary['simulations'].append(extract_metrics(latest))
        else:
            summary['simulations'].append({'id': sim_id, 'error': 'no results json', 'ran': ok})
    out_path = os.path.join(RESULT_DIR, 'sim_summary_latest.json')
    with open(out_path,'w') as f:
        json.dump(summary, f, indent=2)
    print('[SUMMARY] Wrote', out_path, '| Cycle tag:', tag)
    # Build composites after run
    try:
        subprocess.check_call([sys.executable, os.path.join(SCRIPT_DIR,'build_composites.py')])
    except Exception as e:
        print('[WARN] composite build failed', e)
    # Append cycle section to RESULTS_SUMMARY.md (archiving previous)
    try:
        subprocess.check_call([
            sys.executable,
            os.path.join(SCRIPT_DIR,'update_results_summary.py'),
            '--cycle_tag', tag,
            '--summary_json', os.path.join(RESULT_DIR,'sim_summary_latest.json'),
            '--results_markdown', os.path.join(os.path.dirname(SCRIPT_DIR),'RESULTS_SUMMARY.md')
        ])
    except Exception as e:
        print('[WARN] summary append failed', e)

if __name__ == '__main__':
    main()
