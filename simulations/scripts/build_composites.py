"""Build composite multi-panel figures for manuscript from generated individual plots."""
from __future__ import annotations
import os, argparse, matplotlib.pyplot as plt
from publication_style import set_pub_style, save_fig

FIG_SRC = 'paper/figures/simulations'
OUT_DIR = 'paper/figures/simulations'

PANELS = [
    {
        'id': 'FIG_HEAT_SCALING',
        'files': ['coupling_vs_diameter_h50.0.png','peakT_vs_diameter_h50.0.png'],
        'layout': (1,2),
        'titles': ['Coupling Efficiency','Peak Temperature']
    },
    {
        'id': 'FIG_MULTI_CHAMBER',
        'files': ['multi_chamber_efficiency.png','multi_chamber_gain_penalty.png'],
        'layout': (1,2),
        'titles': ['Efficiency per Chamber','Overlap Gain / Penalty']
    },
    {
        'id': 'FIG_FLOW_UNIFORMITY',
        'files': ['flow_uniformity_vs_header_ratio.png','flow_distribution_worst_case.png'],
        'layout': (1,2),
        'titles': ['CV vs Header Ratio','Worst Case Distribution']
    }
]

def build(panel):
    set_pub_style()
    rows, cols = panel['layout']
    fig, axes = plt.subplots(rows, cols, figsize=(6*cols/2,4*rows/1.2))
    axes_list = axes.flatten() if hasattr(axes,'flatten') else [axes]
    for ax, fname, title in zip(axes_list, panel['files'], panel['titles']):
        path = os.path.join(FIG_SRC, fname)
        if os.path.isfile(path):
            img = plt.imread(path)
            ax.imshow(img)
            ax.set_title(title)
        else:
            ax.text(0.5,0.5,'Missing '+fname, ha='center', va='center')
        ax.axis('off')
    out_base = os.path.join(OUT_DIR, panel['id'].lower())
    save_fig(fig, out_base)
    print('Wrote composite', out_base+'.png')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', nargs='*', help='Subset panel IDs')
    args = ap.parse_args()
    selected = [p for p in PANELS if (not args.only or p['id'] in args.only)]
    for p in selected:
        build(p)

if __name__ == '__main__':
    main()
