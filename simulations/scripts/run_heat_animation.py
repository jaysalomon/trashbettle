"""Run a real-time style heat diffusion animation and save MP4 / GIF.

Usage (from repo root PowerShell):
  # Quick small demo
  python simulations/scripts/run_heat_animation.py --diameter 6 --steps 240 --capture-every 2 --downsample 2 --outfile heat_demo.mp4

  # 6 second composite dashboard (~6s at 25fps)
  python simulations/scripts/run_heat_animation.py --composite --diameter 8 --outfile heat_composite.mp4

  # Higher resolution / longer
  python simulations/scripts/run_heat_animation.py --nx 512 --ny 512 --diameter 8 --steps 1000 --capture-every 5 --downsample 4 --outfile heat_8mm.mp4

If ffmpeg is unavailable the script falls back to saving a GIF.
"""
import argparse
import os
from heat_solver import HeatTransferSimulator

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--nx', type=int, default=256)
    p.add_argument('--ny', type=int, default=256)
    p.add_argument('--diameter', type=float, default=6.0, help='Chamber diameter (mm)')
    p.add_argument('--temp', type=float, default=360.0, help='Initial hotspot temperature (K)')
    p.add_argument('--steps', type=int, default=400, help='Total simulation steps to advance (simple mode)')
    p.add_argument('--capture-every', type=int, default=2, dest='capture_every', help='Capture a frame every N steps (simple mode)')
    p.add_argument('--downsample', type=int, default=2, help='Spatial downsample factor for frames')
    p.add_argument('--outfile', type=str, default='heat_diffusion.mp4', help='Output filename placed in output directory')
    p.add_argument('--outdir', type=str, default='simulations/results', help='Directory for outputs')
    p.add_argument('--composite', action='store_true', help='Produce 6s composite dashboard animation instead of raw field animation')
    return p.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    sim = HeatTransferSimulator(nx=args.nx, ny=args.ny, chamber_diameter_mm=args.diameter, output_dir=args.outdir)
    sim.setup_hot_spot(temperature_K=args.temp)

    if args.composite:
        out_path = sim.generate_composite_dashboard(outfile=args.outfile)
    else:
        out_path = sim.generate_animation(
            n_steps=args.steps,
            capture_every=args.capture_every,
            downsample=args.downsample,
            outfile=args.outfile
        )
    print(f"Animation written to: {out_path}")

if __name__ == '__main__':
    main()
