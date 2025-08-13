"""Manim simulation scenes: physics-informed animations (options 1–3).

Scenes:
  1. PhysicsHeatFieldScene        – Live diffusion of a single hot spot (small grid) with HUD metrics.
  2. MultiDiameterComparisonScene – Parallel diffusion fields for multiple diameters + dynamic bar chart of relative heat flux.
  3. MultiChamberSpacingScene     – Animated transition of multi‑chamber array from tight to loose spacing (P/D sweep) with efficiency curve buildup.

Run examples (from repo root):
  manim -ql simulations/scripts/manim_simulations.py PhysicsHeatFieldScene
  manim -ql simulations/scripts/manim_simulations.py MultiDiameterComparisonScene
  manim -ql simulations/scripts/manim_simulations.py MultiChamberSpacingScene

Use -pqh for higher quality preview.

Implementation notes:
 - Uses lightweight NumPy explicit diffusion (no torch) for speed inside Manim.
 - Thermal parameters illustrative; matches qualitative behaviors only.
 - Small grids keep render time reasonable; increase GRID for sharper visuals.
"""
from __future__ import annotations
from manim import *
import numpy as np
import math

try:
    import matplotlib.cm as cm
    _CMAP = cm.get_cmap('inferno')
except Exception:  # fallback
    _CMAP = None

# ------------------------------------------------------------
# Utility functions
# ------------------------------------------------------------

def diffusion_step(T: np.ndarray, alpha: float, dt: float, dx: float):
    """Single explicit 2D diffusion step (5-point Laplacian)."""
    lap = (
        np.roll(T, 1, 0) + np.roll(T, -1, 0) + np.roll(T, 1, 1) + np.roll(T, -1, 1) - 4 * T
    ) / (dx * dx)
    return T + alpha * dt * lap

def to_image_array(field: np.ndarray, vmin: float, vmax: float) -> np.ndarray:
    data = np.clip((field - vmin) / max(1e-9, (vmax - vmin)), 0, 1)
    if _CMAP is not None:
        rgba = _CMAP(data)
        rgb = (rgba[:, :, :3] * 255).astype(np.uint8)
    else:  # grayscale fallback
        rgb = (np.stack([data]*3, axis=-1) * 255).astype(np.uint8)
    return rgb

# ------------------------------------------------------------
# Scene 1: Single heat field with HUD
# ------------------------------------------------------------
class PhysicsHeatFieldScene(Scene):
    """Single hot spot diffusion with dynamic color field + HUD metrics."""
    def construct(self):
        GRID = 96
        ambient = 298.0
        hot = 350.0
        alpha = 1.4e-7  # m^2/s (illustrative)
        dx = 1e-3       # 1 mm
        dt = 0.6 * dx*dx / (4*alpha)  # stable fraction of CFL
        steps_per_frame = 2
        total_frames = 180  # ~6 seconds at 30fps playback (ql profile ~15fps)

        T = np.full((GRID, GRID), ambient, dtype=np.float32)
        cx = cy = GRID // 2
        r_cells = 8
        Y, X = np.ogrid[:GRID, :GRID]
        mask = (X - cx) ** 2 + (Y - cy) ** 2 <= r_cells * r_cells
        T[mask] = hot

        # Initial image
        img = to_image_array(T, ambient, hot)
        image_mobject = ImageMobject(img).scale(4 / GRID * 5)  # scale heuristically
        self.play(FadeIn(image_mobject))

        # HUD text placeholders
        time_txt = Text("t = 0.00 s", font_size=24).to_corner(UL)
        flux_txt = Text("Flux* = --", font_size=24).next_to(time_txt, DOWN)
        self.play(FadeIn(time_txt), FadeIn(flux_txt))

        k_eff = 0.6  # W/mK

        def boundary_flux(field: np.ndarray) -> float:
            # Approx radial gradient at boundary as avg outward difference
            ring = np.logical_xor(
                (X - cx) ** 2 + (Y - cy) ** 2 <= (r_cells + 1) ** 2,
                (X - cx) ** 2 + (Y - cy) ** 2 <= (r_cells - 1) ** 2,
            )
            if not np.any(ring):
                return 0.0
            grad = (field[mask].mean() - field[ring].mean()) / (dx * r_cells)
            return k_eff * grad

        elapsed = 0.0
        for f in range(1, total_frames + 1):
            for _ in range(steps_per_frame):
                T = diffusion_step(T, alpha, dt, dx)
            elapsed += steps_per_frame * dt
            flux = boundary_flux(T)
            img = to_image_array(T, ambient, hot)
            image_mobject.set_image(img)
            time_txt.become(Text(f"t = {elapsed:.2f} s", font_size=24).to_corner(UL))
            flux_txt.become(
                Text(f"Flux* ≈ {flux:6.1f}", font_size=24).next_to(time_txt, DOWN)
            )
            self.wait(1/30)  # pacing

        self.wait(0.5)

# ------------------------------------------------------------
# Scene 2: Multi-diameter comparative diffusion
# ------------------------------------------------------------
class MultiDiameterComparisonScene(Scene):
    """Side-by-side diffusion for several diameters with dynamic relative flux bars."""
    def construct(self):
        GRID = 72
        diameters = [3, 6, 9]  # mm
        ambient, hot = 298.0, 348.0
        alpha = 1.4e-7
        dx = 1e-3
        dt = 0.55 * dx*dx / (4*alpha)
        steps_per_frame = 2
        frames = 150

        fields = []
        masks = []
        centers = []
        for d in diameters:
            T = np.full((GRID, GRID), ambient, dtype=np.float32)
            cx = cy = GRID // 2
            r_cells = max(2, int((d/2) / (dx*1000)))  # convert mm to cells
            Y, X = np.ogrid[:GRID, :GRID]
            mask = (X - cx) ** 2 + (Y - cy) ** 2 <= r_cells * r_cells
            T[mask] = hot
            fields.append(T)
            masks.append(mask)
            centers.append((cx, cy, r_cells))

        # Image grid
        images = []
        group = VGroup()
        for T in fields:
            img = to_image_array(T, ambient, hot)
            im = ImageMobject(img).scale(3 / GRID * 5)
            images.append(im)
            group.add(im)
        group.arrange(RIGHT, buff=0.6).move_to(ORIGIN).shift(UP*1.5)
        self.play(*[FadeIn(im) for im in images])

        # Bar chart baseline
        bar_axis = NumberLine(x_range=[0, 1.2, 0.2], length=5).to_edge(DOWN).shift(LEFT*1.5)
        bar_labels = VGroup(*[Text(f"{d}mm", font_size=24) for d in diameters])
        for i, lbl in enumerate(bar_labels):
            lbl.next_to(bar_axis, UP).shift(RIGHT * (i - 1) * 1.6 + DOWN*0.3)
        self.play(Create(bar_axis), *[Write(l) for l in bar_labels])

        flux_text = Text("Relative Flux", font_size=28).to_edge(DOWN).shift(RIGHT*3)
        self.play(Write(flux_text))

        k_eff = 0.6
        Y, X = np.ogrid[:GRID, :GRID]

        bars = [Line(bar_axis.n2p(0), bar_axis.n2p(0), color=YELLOW, stroke_width=14) for _ in diameters]
        for i, b in enumerate(bars):
            b.shift(RIGHT * (i - 1) * 1.6 + UP*0.15)
            self.add(b)

        ref_flux = None
        for f in range(1, frames + 1):
            rel_fluxes = []
            for idx, T in enumerate(fields):
                for _ in range(steps_per_frame):
                    fields[idx] = diffusion_step(fields[idx], alpha, dt, dx)
                # approximate flux
                cx, cy, r_cells = centers[idx]
                ring = np.logical_xor(
                    (X - cx) ** 2 + (Y - cy) ** 2 <= (r_cells + 1) ** 2,
                    (X - cx) ** 2 + (Y - cy) ** 2 <= (r_cells - 1) ** 2,
                )
                grad = (fields[idx][masks[idx]].mean() - fields[idx][ring].mean()) / (dx * r_cells)
                flux = k_eff * grad
                if ref_flux is None and idx == 0:
                    ref_flux = flux
                rel = flux / max(1e-9, ref_flux)
                rel_fluxes.append(rel)
                img = to_image_array(fields[idx], ambient, hot)
                images[idx].set_image(img)
            # Update bars
            for b, val in zip(bars, rel_fluxes):
                end = bar_axis.n2p(min(val, 1.2))
                start = bar_axis.n2p(0)
                b.put_start_and_end_on(start, end)
            self.wait(1/30)
        self.wait(0.5)

# ------------------------------------------------------------
# Scene 3: Multi-chamber spacing evolution
# ------------------------------------------------------------
class MultiChamberSpacingScene(Scene):
    """Animate pitch (P/D) increasing over time with efficiency curve building."""
    def construct(self):
        diam_mm = 4.0
        alpha = 1.4e-7
        ambient, hot = 298.0, 344.0
        dx = 1e-3
        GRID = 96
        dt = 0.55 * dx*dx / (4*alpha)
        steps_per_frame = 2
        frames = 170
        pitches = np.linspace(1.0, 4.0, frames)  # P/D sweep

        # Base arrays
        base_field = np.full((GRID, GRID), ambient, dtype=np.float32)
        cx = cy = GRID // 2
        diam_cells = int((diam_mm/1000)/dx)
        r_cells = max(2, diam_cells//2)

        # Efficiency tracking (simplified proxy: average peak rise over centers / single center peak)
        eff_points = []
        single_peak_ref = None

        # Axes for efficiency curve
        ax = Axes(x_range=[1,4,0.5], y_range=[0.8,1.25,0.1], x_length=5, y_length=3)
        ax.to_corner(UR).shift(LEFT*0.5+DOWN*0.5)
        axes_labels = ax.get_axis_labels(Text("P/D"), Text("Eff")).scale(0.6)
        self.play(Create(ax), FadeIn(axes_labels))
        curve = VMobject(color=GREEN)
        curve.set_points_as_corners([ax.coords_to_point(1,1)])
        self.add(curve)

        # Field display
        img = to_image_array(base_field, ambient, hot)
        im_obj = ImageMobject(img).scale(4 / GRID * 5).to_edge(LEFT).shift(RIGHT*0.5)
        self.play(FadeIn(im_obj))

        title = Text("Multi-Chamber Spacing Evolution", font_size=32).to_edge(UP)
        self.play(Write(title))

        for frame, PD in enumerate(pitches, start=1):
            # Reset field each frame (quasi steady snapshot after short burn-in)
            T = np.full((GRID, GRID), ambient, dtype=np.float32)
            pitch_cells = PD * diam_cells
            centers = []
            start_offset = -((2) / 2.0) * pitch_cells  # 3x3 => index 0..2
            for i in range(3):
                for j in range(3):
                    x = cx + start_offset + i * pitch_cells
                    y = cy + start_offset + j * pitch_cells
                    centers.append((int(x), int(y)))
            # Apply heat for a mini burn-in
            for _ in range(40):
                for (ix, iy) in centers:
                    if 0 <= ix < GRID and 0 <= iy < GRID:
                        rr = r_cells
                        T[max(0,ix-rr):ix+rr+1, max(0,iy-rr):iy+rr+1] = np.maximum(
                            T[max(0,ix-rr):ix+rr+1, max(0,iy-rr):iy+rr+1], hot
                        )
                T = diffusion_step(T, alpha, dt, dx)
            # Measure pseudo-efficiency
            peaks = []
            for (ix, iy) in centers:
                if 0 <= ix < GRID and 0 <= iy < GRID:
                    peaks.append(T[ix, iy] - ambient)
            mean_peak = np.mean(peaks) if peaks else 0.0
            if single_peak_ref is None:
                single_peak_ref = mean_peak  # first frame acts as reference (tight spacing)
            eff = mean_peak / max(1e-9, single_peak_ref)
            eff_points.append((PD, eff))
            # Update field image
            im_obj.set_image(to_image_array(T, ambient, hot))
            # Update curve
            if len(eff_points) > 1:
                pts = [ax.coords_to_point(p,e) for (p,e) in eff_points]
                curve.set_points_as_corners(pts)
            self.wait(1/30)

        # Final annotate plateau
        plateau = Text("Plateau after ~P/D 2", font_size=24, color=YELLOW).next_to(ax, DOWN)
        self.play(Write(plateau))
        self.wait(1)

# End of file
