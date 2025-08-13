"""Lightweight numeric sanity checks for key simulation relationships.
Run: python simulations/scripts/sanity_tests.py
"""
from __future__ import annotations
import json, glob, os, subprocess, sys, math

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..'))
RES_DIR = os.path.join(ROOT,'simulations','results')
SCRIPT_DIR = os.path.join(ROOT,'simulations','scripts')

EXPECT = {
    'SIM-HT-CONJ_ratio_min': 1.5,  # 2mm vs 12mm peak temperature ratio target (rough early threshold)
    'SIM-EN-MC_P50_min': 0.3,
    'SIM-ACT-NIT_max_reduction_min': 0.2,
    'SIM-RES-FAIL_capacity_0.1_min': 0.8
}

def latest(sim_id):
    files = sorted(glob.glob(os.path.join(RES_DIR, f'sim_{sim_id}_*.json')))
    return files[-1] if files else None

def load(sim_id):
    f = latest(sim_id)
    if not f:
        return None
    with open(f,'r') as fh:
        return json.load(fh)

failures = []

# Heat conjugate peak T ratio
hc = load('SIM-HT-CONJ')
if hc:
    maxT = hc['metrics']['max_temperatures_K']
    try:
        r = maxT['2mm']/maxT['12mm']
        if r < EXPECT['SIM-HT-CONJ_ratio_min']:
            failures.append(f'Coupling peak T ratio {r:.2f} < {EXPECT["SIM-HT-CONJ_ratio_min"]}')
    except Exception as e:
        failures.append(f'HT-CONJ ratio calc error {e}')

# Energy Monte Carlo P50
mc = load('SIM-EN-MC')
if mc:
    if mc['metrics']['P50'] < EXPECT['SIM-EN-MC_P50_min']:
        failures.append(f'Energy P50 {mc["metrics"]["P50"]:.2f} < {EXPECT["SIM-EN-MC_P50_min"]}')

# Nitinol reduction
ni = load('SIM-ACT-NIT')
if ni:
    if ni['metrics']['max_reduction_fraction'] < EXPECT['SIM-ACT-NIT_max_reduction_min']:
        failures.append('Nitinol max reduction below expectation')

# Resilience 10% failures
rs = load('SIM-RES-FAIL')
if rs:
    cap = rs['metrics']['capacity_vs_failure'].get('0.1')
    if cap is not None and cap < EXPECT['SIM-RES-FAIL_capacity_0.1_min']:
        failures.append(f'Resilience capacity at 10% {cap:.2f} < 0.8')

if failures:
    print('SANITY CHECK FAILURES:')
    for f in failures:
        print(' -', f)
    sys.exit(1)
else:
    print('All sanity checks passed.')
