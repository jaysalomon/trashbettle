"""Central publication plotting style utilities."""
from __future__ import annotations
import matplotlib as mpl
import matplotlib.pyplot as plt
import os

CB_PALETTE = ['#0072B2','#E69F00','#D55E00','#009E73','#CC79A7','#56B4E9','#F0E442','#999999']

def set_pub_style():
    mpl.rcParams.update({
        'figure.dpi': 120,
        'savefig.dpi': 300,
        'figure.figsize': (6,4),
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'legend.fontsize': 9,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans','Arial','Helvetica'],
        'axes.prop_cycle': mpl.cycler(color=CB_PALETTE)
    })

def save_fig(fig, base_path: str):
    fig.tight_layout()
    suffix = os.environ.get('SIM_CYCLE_TAG')
    if suffix:
        base_path = f"{base_path}_{suffix}"
    fig.savefig(base_path + '.png', dpi=300)
    fig.savefig(base_path + '.pdf')
