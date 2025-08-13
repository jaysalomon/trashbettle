"""Append a new cycle section to RESULTS_SUMMARY.md while archiving prior version.

Usage (invoked by run_all):
  python update_results_summary.py --cycle_tag DEV_CYCLE_3 \
      --summary_json simulations/results/sim_summary_latest.json \
      --results_markdown RESULTS_SUMMARY.md

Logic:
  * Archive existing RESULTS_SUMMARY.md into simulations/results/summary_history/RESULTS_SUMMARY_<timestamp>.md
  * Extract highlight metrics from latest summary JSON.
  * Prepend a new '## Cycle <tag> (ISO timestamp)' section with bullet highlights.
  * Preserve full historical content below.
"""
from __future__ import annotations
import argparse, os, json, datetime
from textwrap import shorten

HISTORY_DIR = os.path.join('simulations','results','summary_history')


def load_json(path):
    try:
        with open(path,'r') as f: return json.load(f)
    except Exception as e:
        return None


def metric_or(d, path, default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur: return default
        cur = cur[p]
    return cur


def extract_highlights(summary):
    sims = {s['id']: s for s in summary.get('simulations',[])}
    hl = []
    # Multi-chamber threshold & overlap
    multi = sims.get('SIM-HT-MULTI')
    if multi:
        thr = metric_or(multi,'metrics threshold_PD'.split(), None) or metric_or(multi,['metrics','threshold_PD'],None)
        gains = metric_or(multi,['metrics','overlap_gain'],{})
        max_gain = max(gains.values()) if gains else None
        if thr and max_gain is not None:
            hl.append(f"Multi-chamber: overlap gain peak {max_gain:.2f}; threshold P/D={thr}.")
    # Energy sensitivity
    energy = sims.get('SIM-EN-MC')
    if energy:
        ranks = metric_or(energy,['metrics','influence_rank'],[])
        if ranks:
            top = ranks[0]
            hl.append(f"Energy sensitivity: top driver {top[0]} (Δmedian {top[1]:.3f}).")
        fp = metric_or(energy,['metrics','failure_prob'])
        if fp is not None:
            hl.append(f"Energy failure prob <0 surplus: {fp*100:.2f}%.")
    # PCM variance reduction peak
    pcm = sims.get('SIM-PCM-BUF')
    if pcm:
        vr = metric_or(pcm,['metrics','variance_reduction'])
        sweep = metric_or(pcm,['metrics','variance_reduction_sweep'],{})
        if vr is not None:
            hl.append(f"PCM variance reduction baseline: {vr*100:.1f}%.")
        if sweep:
            peak = max(sweep.values())
            hl.append(f"PCM sweep peak: {peak*100:.1f}%.")
    # Resilience P10 at 0.15 failure
    res = sims.get('SIM-RES-FAIL')
    if res:
        p10 = metric_or(res,['metrics','capacity_p10'],{})
        if p10 and '0.15' in p10:
            hl.append(f"Resilience capacity P10 at 15% fail: {p10['0.15']:.3f}.")
    # Lattice optimizer front size & HV proxy
    lat = sims.get('SIM-OPT-LAT')
    if lat:
        fs = metric_or(lat,['metrics','front_size'])
        hv = metric_or(lat,['metrics','hypervolume_proxy'])
        if fs is not None:
            hl.append(f"Lattice GA front size: {fs} (proxy HV {hv:.1f}).")
    return hl


def prepend_cycle_section(md_path, cycle_tag, summary):
    ts = datetime.datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    highlights = extract_highlights(summary)
    section_lines = [f"## Cycle {cycle_tag} ({ts})","", "Highlights:"]
    if highlights:
        section_lines += ["- " + h for h in highlights]
    else:
        section_lines.append("- (No highlights extracted)")
    section_lines.append("")
    section_block = "\n".join(section_lines) + "\n"
    if os.path.isfile(md_path):
        with open(md_path,'r',encoding='utf-8') as f: existing = f.read()
    else:
        existing = "# Results Summary History\n\n"
    # Avoid duplicate insertion for same cycle tag
    if f"## Cycle {cycle_tag} " in existing:
        return False
    new_content = section_block + existing
    with open(md_path,'w',encoding='utf-8') as f: f.write(new_content)
    return True


def archive_previous(md_path):
    if not os.path.isfile(md_path):
        return None
    os.makedirs(HISTORY_DIR, exist_ok=True)
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')
    dest = os.path.join(HISTORY_DIR, f'RESULTS_SUMMARY_{ts}.md')
    with open(md_path,'r',encoding='utf-8') as fsrc, open(dest,'w',encoding='utf-8') as fdst:
        fdst.write(fsrc.read())
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cycle_tag', required=True)
    ap.add_argument('--summary_json', default=os.path.join('simulations','results','sim_summary_latest.json'))
    ap.add_argument('--results_markdown', default='RESULTS_SUMMARY.md')
    args = ap.parse_args()
    data = load_json(args.summary_json)
    if data is None:
        print('[WARN] Could not load summary JSON; skipping results summary update.')
        return
    archived = archive_previous(args.results_markdown)
    updated = prepend_cycle_section(args.results_markdown, args.cycle_tag, data)
    if updated:
        print(f'[SUMMARY-APPEND] Added cycle section {args.cycle_tag} | archived previous -> {archived}')
    else:
        print(f'[SUMMARY-APPEND] Cycle {args.cycle_tag} already present; no changes.')

if __name__ == '__main__':
    main()
