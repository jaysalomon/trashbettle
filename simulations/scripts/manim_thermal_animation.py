"""
Manim Animations for Heat / Flow / Energy Visualizations
Usage examples (inside repo root):
    manim -ql simulations/scripts/manim_thermal_animation.py HeatTransferScene
    manim -ql simulations/scripts/manim_thermal_animation.py MultiChamberOverlapScene
    manim -ql simulations/scripts/manim_thermal_animation.py EnergyCorrelationScene

Scenes:
    HeatTransferScene          – Conceptual heat diffusion & non‑monotonic diameter efficiency with uncertainty + refinement annotation.
    FlowLatticeAnimation       – Lattice flow / pressure visualization (unchanged concept).
    EnergyBalanceVisualization – Daily generation vs consumption bars (baseline scenario).
    MultiChamberOverlapScene   – Efficiency gain vs P/D spacing with plateau & threshold annotation.
    EnergyCorrelationScene     – Failure probability shift under adverse correlation vs independent.

Note: Numerical values are illustrative & aligned qualitatively with manuscript (non-monotonic, small refinement deltas, threshold P/D≈2, adverse failure increase ~15%).
"""

from manim import *
import numpy as np

class HeatTransferScene(Scene):
    """Animated visualization of heat transfer; updated to show non-monotonic, near-flat efficiency with uncertainty."""
    
    def construct(self):
        # Title
        title = Text("Heat Transfer Efficiency vs Diameter", font_size=48)
        subtitle = Text("Non-monotonic with small refinement uncertainty", font_size=24)
        subtitle.next_to(title, DOWN)

        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(title), FadeOut(subtitle))

        # Create comparison of chamber sizes
        self.show_chamber_comparison()
        self.wait(1)

        # Show heat flow animation
        self.animate_heat_flow()
        self.wait(1)

        # Show efficiency scaling
        self.show_efficiency_graph()
        self.wait(2)
    
    def show_chamber_comparison(self):
        """Compare different chamber sizes."""
        
        # Create chambers of different sizes
        small_chamber = Circle(radius=0.5, color=RED)
        medium_chamber = Circle(radius=1.0, color=ORANGE)
        large_chamber = Circle(radius=1.5, color=YELLOW)
        
        # Labels
        small_label = Text("4mm", font_size=20).next_to(small_chamber, DOWN)
        medium_label = Text("8mm", font_size=20).next_to(medium_chamber, DOWN)
        large_label = Text("12mm", font_size=20).next_to(large_chamber, DOWN)
        
        # Position chambers
        chambers = VGroup(small_chamber, medium_chamber, large_chamber)
        labels = VGroup(small_label, medium_label, large_label)
        chambers.arrange(RIGHT, buff=1.5)
        labels.arrange(RIGHT, buff=1.5)
        
        VGroup(chambers, labels).move_to(ORIGIN)
        
        self.play(
            Create(small_chamber),
            Create(medium_chamber),
            Create(large_chamber),
            Write(small_label),
            Write(medium_label),
            Write(large_label)
        )
        
        # Add heat flux indicators
        self.add_heat_flux_arrows(small_chamber, 12, RED)
        self.add_heat_flux_arrows(medium_chamber, 8, ORANGE)
        self.add_heat_flux_arrows(large_chamber, 4, YELLOW)
        
        self.wait(2)
        self.play(FadeOut(chambers), FadeOut(labels))
    
    def add_heat_flux_arrows(self, chamber, num_arrows, color):
        """Add animated arrows showing heat flux."""
        arrows = []
        for i in range(num_arrows):
            angle = i * 2 * PI / num_arrows
            start = chamber.get_center() + chamber.radius * np.array([np.cos(angle), np.sin(angle), 0])
            end = start + 0.5 * np.array([np.cos(angle), np.sin(angle), 0])
            arrow = Arrow(start, end, color=color, stroke_width=2)
            arrows.append(arrow)
        
        self.play(*[GrowArrow(arrow) for arrow in arrows], run_time=0.5)
    
    def animate_heat_flow(self):
        """Animate heat diffusion through the lattice."""
        
        # Create lattice grid
        lattice = VGroup()
        rows, cols = 5, 5
        for i in range(rows):
            for j in range(cols):
                hex = RegularPolygon(6, radius=0.3, color=BLUE)
                hex.move_to(np.array([j * 0.7 - 1.4, i * 0.6 - 1.2, 0]))
                if i % 2 == 1:
                    hex.shift(RIGHT * 0.35)
                lattice.add(hex)
        
        self.play(Create(lattice))
        
        # Create heat source in center
        center_hex = lattice[12]  # Middle of 5x5 grid
        heat_source = Circle(radius=0.15, color=RED, fill_opacity=1)
        heat_source.move_to(center_hex.get_center())
        
        self.play(FadeIn(heat_source))
        
        # Animate heat propagation
        heat_waves = []
        for i in range(3):
            wave = Circle(
                radius=0.15 + i * 0.4,
                color=interpolate_color(RED, BLUE, i/3),
                stroke_width=3,
                fill_opacity=0
            )
            wave.move_to(heat_source.get_center())
            heat_waves.append(wave)
        
        self.play(
            *[Create(wave) for wave in heat_waves],
            *[wave.animate.scale(2).set_stroke(width=1).set_opacity(0.3) for wave in heat_waves],
            run_time=2
        )
        
        # Color change to show temperature
        for i, hex in enumerate(lattice):
            distance = np.linalg.norm(hex.get_center() - heat_source.get_center())
            if distance < 1.5:
                color = interpolate_color(RED, BLUE, distance / 1.5)
                self.play(hex.animate.set_color(color), run_time=0.1)
        
        self.wait(1)
        self.play(FadeOut(lattice), FadeOut(heat_source), *[FadeOut(wave) for wave in heat_waves])
    
    def show_efficiency_graph(self):
        """Display efficiency vs diameter graph (non-monotonic + error bars + refinement note)."""
        
        # Create axes
        axes = Axes(
            x_range=[3, 13, 1],
            y_range=[85, 96, 2],
            x_length=6,
            y_length=4,
            axis_config={"include_tip": True},
            x_axis_config={"numbers_to_include": [4,6,8,10,12]},
            y_axis_config={"numbers_to_include": [86,88,90,92,94,96]},
        )
        
        x_label = Text("Chamber Diameter (mm)", font_size=20)
        y_label = Text("Coupling Efficiency (%)", font_size=20)
        x_label.next_to(axes.x_axis, DOWN)
        y_label.next_to(axes.y_axis, LEFT).rotate(PI/2)
        
        # Synthetic non-monotonic dataset (illustrative)
        diameters = [4,6,8,10,12]
        efficiencies = [92.0, 93.1, 91.4, 92.6, 90.8]
        errors = [0.8, 0.9, 1.0, 0.7, 0.9]  # replicate std dev style

        # Plot polyline connecting means
        points = [axes.coords_to_point(d, e) for d, e in zip(diameters, efficiencies)]
        polyline = VMobject(color=GREEN)
        polyline.set_points_as_corners(points)

        dots = VGroup()
        error_bars = VGroup()
        for d, e, err in zip(diameters, efficiencies, errors):
            pt = axes.coords_to_point(d, e)
            dot = Dot(pt, color=YELLOW)
            err_top = axes.coords_to_point(d, e + err)
            err_bot = axes.coords_to_point(d, e - err)
            bar = Line(err_bot, err_top, stroke_width=2, color=YELLOW)
            cap_top = Line(err_top + LEFT*0.07, err_top + RIGHT*0.07, stroke_width=2, color=YELLOW)
            cap_bot = Line(err_bot + LEFT*0.07, err_bot + RIGHT*0.07, stroke_width=2, color=YELLOW)
            error_bars.add(bar, cap_top, cap_bot)
            label = Text(f"{e:.1f}±{err:.1f}%", font_size=14).next_to(dot, UP*0.4)
            dots.add(dot, label)

        # Annotation text
        note = Text("Non-monotonic variation within ±1% replicate σ", font_size=20, color=WHITE)
        note.to_corner(UR)
        refine_note = Text("Grid refinement Δ ≤ 3% (max)", font_size=18, color=BLUE).next_to(note, DOWN*1.2)
        
        # Animation
        self.play(Create(axes), Write(x_label), Write(y_label))
        self.play(Create(polyline))
        self.play(FadeIn(error_bars))
        self.play(*[FadeIn(m) for m in dots])
        self.play(Write(note))
        self.play(Write(refine_note))
        plateau = Text("Near-flat plateau", font_size=18, color=GREEN).to_corner(UL)
        self.play(Write(plateau))
        
        self.wait(2)


class FlowLatticeAnimation(Scene):
    """Animate flow through the honeycomb lattice."""
    
    def construct(self):
        # Title
        title = Text("Multi-Functional Flow Lattice", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
        
        # Create honeycomb lattice
        self.create_honeycomb_lattice()
        
        # Animate flow
        self.animate_fluid_flow()
        
        # Show pressure distribution
        self.show_pressure_field()
    
    def create_honeycomb_lattice(self):
        """Create animated honeycomb structure."""
        
        self.hexagons = VGroup()
        rows, cols = 7, 7
        
        for i in range(rows):
            for j in range(cols):
                hex = RegularPolygon(
                    6,
                    radius=0.4,
                    color=BLUE,
                    stroke_width=3,
                    fill_opacity=0.2
                )
                hex.move_to(np.array([j * 0.7 - 2.1, i * 0.7 - 2.1, 0]))
                if j % 2 == 1:
                    hex.shift(UP * 0.35)
                self.hexagons.add(hex)
        
        self.play(Create(self.hexagons), run_time=2)
    
    def animate_fluid_flow(self):
        """Show fluid particles flowing through channels."""
        
        particles = VGroup()
        for _ in range(20):
            particle = Dot(
                radius=0.05,
                color=BLUE_E,
                fill_opacity=0.8
            )
            # Random starting position on left side
            start_y = np.random.uniform(-2.5, 2.5)
            particle.move_to(np.array([-3.5, start_y, 0]))
            particles.add(particle)
        
        # Animate particles moving through lattice
        paths = []
        for particle in particles:
            # Create wavy path through lattice
            points = [particle.get_center()]
            for x in np.linspace(-3.5, 3.5, 8):
                y = particle.get_center()[1] + 0.3 * np.sin(2 * x)
                points.append(np.array([x, y, 0]))
            
            path = VMobject()
            path.set_points_smoothly(points)
            paths.append(path)
        
        animations = []
        for particle, path in zip(particles, paths):
            animations.append(
                MoveAlongPath(particle, path, run_time=3, rate_func=linear)
            )
        
        self.play(FadeIn(particles))
        self.play(*animations)
        self.play(FadeOut(particles))
    
    def show_pressure_field(self):
        """Visualize pressure distribution."""
        
        # Create pressure gradient
        pressure_field = Rectangle(
            width=6,
            height=5,
            fill_opacity=0.5,
            stroke_width=0
        )
        pressure_field.set_color_by_gradient(RED, YELLOW, GREEN)
        
        # Pressure label
        pressure_label = Text("Pressure Distribution", font_size=24)
        pressure_label.to_edge(UP)
        
        # Pressure scale
        scale = VGroup()
        for i, (color, label) in enumerate([(RED, "High"), (YELLOW, "Medium"), (GREEN, "Low")]):
            box = Square(side_length=0.3, color=color, fill_opacity=0.8)
            text = Text(label, font_size=16)
            text.next_to(box, RIGHT)
            item = VGroup(box, text)
            item.move_to(np.array([3, 2 - i * 0.8, 0]))
            scale.add(item)
        
        self.play(
            FadeIn(pressure_field, shift=UP),
            Write(pressure_label),
            FadeIn(scale)
        )
        
        self.wait(2)


class EnergyBalanceVisualization(Scene):
    """Visualize the energy balance of the system."""
    
    def construct(self):
        # Title
        title = Text("Daily Energy Balance", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))
        
        # Create energy sources
        self.show_energy_sources()
        
        # Show energy consumption
        self.show_energy_consumption()
        
        # Display net surplus
        self.show_net_surplus()
    
    def show_energy_sources(self):
        """Display energy generation sources."""
        
        sources_title = Text("Energy Generation", font_size=32, color=GREEN)
        sources_title.move_to(np.array([-3, 2, 0]))
        
        # Solar
        solar_bar = Rectangle(width=2, height=0.5, color=YELLOW, fill_opacity=0.8)
        solar_text = Text("Solar: 0.20 kWh", font_size=20)
        solar = VGroup(solar_bar, solar_text).arrange(RIGHT)
        
        # Bio-reactor
        bio_bar = Rectangle(width=3.6, height=0.5, color=GREEN, fill_opacity=0.8)
        bio_text = Text("Bio: 0.72 kWh", font_size=20)
        bio = VGroup(bio_bar, bio_text).arrange(RIGHT)
        
        # Chemical
        chem_bar = Rectangle(width=1.2, height=0.5, color=ORANGE, fill_opacity=0.8)
        chem_text = Text("Chemical: 0.24 kWh", font_size=20)
        chem = VGroup(chem_bar, chem_text).arrange(RIGHT)
        
        sources = VGroup(solar, bio, chem).arrange(DOWN, buff=0.3)
        sources.next_to(sources_title, DOWN)
        
        self.play(Write(sources_title))
        self.play(
            *[GrowFromEdge(bar, LEFT) for bar in [solar_bar, bio_bar, chem_bar]],
            *[Write(text) for text in [solar_text, bio_text, chem_text]]
        )
        
        # Total generation
        total_gen = Text("Total: 1.16 kWh", font_size=24, color=GREEN)
        total_gen.next_to(sources, DOWN, buff=0.5)
        self.play(Write(total_gen))
    
    def show_energy_consumption(self):
        """Display energy consumption."""
        
        consumption_title = Text("Energy Consumption", font_size=32, color=RED)
        consumption_title.move_to(np.array([3, 2, 0]))
        
        # Components
        components = [
            ("Core: 0.24 kWh", 1.2, BLUE),
            ("Sensors: 0.12 kWh", 0.6, PURPLE),
            ("Locomotion: 0.10 kWh", 0.5, TEAL),
            ("Processing: 0.24 kWh", 1.2, MAROON)
        ]
        
        consumption_bars = VGroup()
        for text, width, color in components:
            bar = Rectangle(width=width, height=0.5, color=color, fill_opacity=0.8)
            label = Text(text, font_size=20)
            item = VGroup(bar, label).arrange(RIGHT)
            consumption_bars.add(item)
        
        consumption_bars.arrange(DOWN, buff=0.3)
        consumption_bars.next_to(consumption_title, DOWN)
        
        self.play(Write(consumption_title))
        self.play(*[GrowFromEdge(item[0], LEFT) for item in consumption_bars])
        self.play(*[Write(item[1]) for item in consumption_bars])
        
        # Total consumption
        total_cons = Text("Total: 0.70 kWh", font_size=24, color=RED)
        total_cons.next_to(consumption_bars, DOWN, buff=0.5)
        self.play(Write(total_cons))
    
    def show_net_surplus(self):
        """Display the net energy surplus."""
        
        # Draw balance arrow
        arrow = DoubleArrow(
            np.array([-1, -2, 0]),
            np.array([1, -2, 0]),
            color=WHITE,
            stroke_width=5
        )
        
        surplus_text = Text("Net Surplus: +0.46 kWh", font_size=36, color=GOLD)
        surplus_text.next_to(arrow, DOWN)
        
        self.play(GrowArrow(arrow))
        self.play(Write(surplus_text))
        self.play(surplus_text.animate.scale(1.2), run_time=0.5)
        self.wait(2)


class MultiChamberOverlapScene(Scene):
    """Show efficiency gain vs chamber spacing (P/D) with plateau and threshold annotation."""

    def construct(self):
        title = Text("Multi-Chamber Spacing (P/D) vs Added Efficiency", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))

        axes = Axes(
            x_range=[0.8, 4.5, 0.4],
            y_range=[0, 6, 1],
            x_length=6,
            y_length=3.5,
            axis_config={"include_tip": True}
        )
        xlab = Text("Pitch / Diameter (P/D)", font_size=20).next_to(axes.x_axis, DOWN)
        ylab = Text("Incremental Efficiency (%)", font_size=20).next_to(axes.y_axis, LEFT).rotate(PI/2)
        self.play(Create(axes), Write(xlab), Write(ylab))

        # Illustrative diminishing returns dataset
        pd_vals = [1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 4.0]
        gains =   [0.8, 2.1, 3.4, 4.2, 4.4, 4.5, 4.6]
        points = [axes.coords_to_point(x,y) for x,y in zip(pd_vals, gains)]
        line = VMobject(color=ORANGE)
        line.set_points_smoothly(points)
        dots = VGroup(*[Dot(p, color=ORANGE) for p in points])
        self.play(Create(line))
        self.play(FadeIn(dots))

        # Threshold annotation at ~2.0
        thresh_x = 2.0
        thresh_line = DashedLine(
            axes.coords_to_point(thresh_x, 0),
            axes.coords_to_point(thresh_x, 6),
            color=YELLOW
        )
        thresh_label = Text("Plateau ~P/D 2", font_size=18, color=YELLOW).next_to(thresh_line, UP)
        self.play(Create(thresh_line), Write(thresh_label))

        plateau_note = Text("Marginal gains <0.3% beyond", font_size=18, color=WHITE).to_corner(UR)
        self.play(Write(plateau_note))
        self.wait(2)


class EnergyCorrelationScene(Scene):
    """Visualize independent vs adverse correlated energy failure probability."""

    def construct(self):
        title = Text("Energy Failure Probability: Independent vs Adverse", font_size=40)
        title.to_edge(UP)
        self.play(Write(title))

        # Axes for bar chart
        axes = Axes(
            x_range=[0,3,1],
            y_range=[0,0.18,0.03],
            x_length=6,
            y_length=4,
            axis_config={"include_tip": True},
            y_axis_config={"decimal_number_config": {"num_decimal_places":2}}
        )
        xlab = Text("Scenario", font_size=20).next_to(axes.x_axis, DOWN)
        ylab = Text("Failure Probability", font_size=20).next_to(axes.y_axis, LEFT).rotate(PI/2)
        self.play(Create(axes), Write(xlab), Write(ylab))

        # Bars
        scenarios = ["Independent", "Adverse"]
        probs = [0.006, 0.152]
        bars = VGroup()
        for i,(label, p) in enumerate(zip(scenarios, probs), start=1):
            x_center = i
            bar_top = axes.coords_to_point(x_center, p)
            bar_bottom = axes.coords_to_point(x_center, 0)
            bar = Rectangle(
                width=0.6,
                height=bar_top[1]-bar_bottom[1],
                fill_opacity=0.8,
                stroke_width=0,
                color=GREEN if i==1 else RED
            )
            bar.move_to([(bar_top[0]+bar_bottom[0])/2, (bar_top[1]+bar_bottom[1])/2, 0])
            txt = Text(f"{p*100:.1f}%", font_size=24, color=WHITE).next_to(bar, UP*0.3)
            lbl = Text(label, font_size=20).next_to(bar, DOWN*0.3)
            group = VGroup(bar, txt, lbl)
            bars.add(group)
        self.play(*[FadeIn(g) for g in bars])

        delta_arrow = Arrow(
            bars[0][0].get_top()+UP*0.2,
            bars[1][0].get_top()+UP*0.2,
            buff=0.1,
            color=YELLOW,
            stroke_width=4
        )
        delta_text = Text("Δ ≈ +14.6%", font_size=28, color=YELLOW).next_to(delta_arrow, UP)
        self.play(GrowArrow(delta_arrow), Write(delta_text))

        note = Text("Correlation stress test widens risk bounds", font_size=20).to_corner(UR)
        self.play(Write(note))
        self.wait(2)


if __name__ == "__main__":
    # Run with: manim -pql manim_thermal_animation.py HeatTransferScene
    pass