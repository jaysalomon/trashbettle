"""Utility helpers for simulation metadata, saving results, and figure management."""
from __future__ import annotations
import os, json, subprocess, datetime, hashlib, inspect
from typing import Dict, Any

def get_git_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "nogit"

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def script_name(frame_depth: int = 1) -> str:
    try:
        frame = inspect.stack()[frame_depth]
        return os.path.basename(frame.filename)
    except Exception:
        return "unknown.py"

def build_metadata(sim_id: str, params: Dict[str, Any], notes: str = "") -> Dict[str, Any]:
    return {
        "id": sim_id,
        "script": script_name(2),
        "git_hash": get_git_hash(),
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "params": params,
        "metrics": {},
        "figures": [],
        "notes": notes,
        "schema_version": 1
    }

def save_results(metadata: Dict[str, Any], results_dir: str = "simulations/results") -> str:
    ensure_dir(results_dir)
    fname = f"sim_{metadata['id']}_{metadata['timestamp'].replace(':','').replace('-','')}.json"
    fpath = os.path.join(results_dir, fname)
    with open(fpath, 'w') as f:
        json.dump(metadata, f, indent=2)
    return fpath

def register_figure(metadata: Dict[str, Any], fig_path: str):
    rel = os.path.relpath(fig_path).replace('\\', '/')
    metadata.setdefault('figures', []).append(rel)

def hash_array(arr) -> str:
    try:
        import numpy as np
        if isinstance(arr, (list, tuple)):
            arr = np.array(arr)
        return hashlib.sha1(arr.tobytes()).hexdigest()[:10]
    except Exception:
        return "nohash"
