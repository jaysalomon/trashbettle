"""
Advanced Fluidic Control Visualization for Bio-Hybrid Lattice
Shows Tesla valves, vortex valves, and other passive flow control elements
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle, FancyBboxPatch, PathPatch
from matplotlib.path import Path
import matplotlib.patches as mpatches

def draw_tesla_valve(ax, x, y, scale=1.0, rotation=0):
    """Draw a Tesla valve schematic"""
    # Tesla valve has characteristic loop-back design
    # Main channel
    main_width = 2 * scale
    main_height = 0.5 * scale
    
    # Main flow path
    rect1 = Rectangle((x-main_width/2, y-main_height/2), main_width, main_height,
                      facecolor='lightblue', edgecolor='darkblue', linewidth=2)
    ax.add_patch(rect1)
    
    # Loop-back channels (characteristic Tesla valve feature)
    for i in range(3):
        offset = (i - 1) * 0.7 * scale
        # Upper loop
        loop_path = Path([
            (x + offset - 0.2*scale, y),
            (x + offset - 0.2*scale, y + 0.8*scale),
            (x + offset + 0.2*scale, y + 0.8*scale),
            (x + offset + 0.2*scale, y + 0.3*scale),
            (x + offset, y + 0.3*scale),
            (x + offset, y)
        ])
        loop_patch = PathPatch(loop_path, facecolor='lightcyan', 
                              edgecolor='blue', linewidth=1.5)
        ax.add_patch(loop_patch)
        
        # Direction preference arrow
        ax.arrow(x + offset - 0.3*scale, y, 0.5*scale, 0,
                head_width=0.1*scale, head_length=0.1*scale,
                fc='green', ec='green', alpha=0.7)
    
    # Reverse flow resistance indicator
    ax.arrow(x + main_width/2 + 0.2*scale, y, -0.3*scale, 0,
            head_width=0.1*scale, head_length=0.1*scale,
            fc='red', ec='red', alpha=0.5, linestyle='--')
    ax.text(x + main_width/2 + 0.5*scale, y, 'High R', fontsize=8, color='red')
    
    # Forward flow indicator
    ax.text(x - main_width/2 - 0.7*scale, y, 'Low R', fontsize=8, color='green')

def draw_vortex_valve(ax, x, y, scale=1.0):
    """Draw a vortex valve (fluidic diode)"""
    # Circular chamber
    chamber = Circle((x, y), scale, facecolor='lightgray', 
                    edgecolor='black', linewidth=2)
    ax.add_patch(chamber)
    
    # Tangential inlet (creates vortex)
    inlet_x = x - scale
    inlet_y = y + scale * 0.7
    ax.arrow(inlet_x - 0.5*scale, inlet_y, 0.4*scale, -0.2*scale,
            head_width=0.15*scale, head_length=0.1*scale,
            fc='blue', ec='blue', linewidth=2)
    ax.text(inlet_x - 0.7*scale, inlet_y + 0.2*scale, 'Tangential\nInput', 
           fontsize=8, ha='right')
    
    # Radial inlet (disrupts vortex)
    radial_x = x
    radial_y = y - scale
    ax.arrow(radial_x, radial_y - 0.5*scale, 0, 0.4*scale,
            head_width=0.15*scale, head_length=0.1*scale,
            fc='orange', ec='orange', linewidth=2)
    ax.text(radial_x, radial_y - 0.7*scale, 'Radial\nControl', 
           fontsize=8, ha='center')
    
    # Outlet
    ax.arrow(x + scale, y, 0.5*scale, 0,
            head_width=0.15*scale, head_length=0.1*scale,
            fc='green', ec='green', linewidth=2)
    ax.text(x + scale + 0.7*scale, y, 'Output', fontsize=8)
    
    # Vortex flow lines
    theta = np.linspace(0, 4*np.pi, 100)
    r = np.linspace(0.2, 0.8, 100) * scale
    spiral_x = x + r * np.cos(theta)
    spiral_y = y + r * np.sin(theta)
    ax.plot(spiral_x, spiral_y, 'b-', alpha=0.3, linewidth=1)

def draw_acoustic_resonator(ax, x, y, scale=1.0):
    """Draw an acoustic resonator for pressure pulse communication"""
    # Main chamber
    chamber_width = 1.5 * scale
    chamber_height = 1.0 * scale
    chamber = Rectangle((x-chamber_width/2, y-chamber_height/2), 
                        chamber_width, chamber_height,
                        facecolor='lightyellow', edgecolor='darkorange', linewidth=2)
    ax.add_patch(chamber)
    
    # Helmholtz neck
    neck_width = 0.3 * scale
    neck_height = 0.5 * scale
    neck = Rectangle((x-neck_width/2, y-chamber_height/2-neck_height), 
                    neck_width, neck_height,
                    facecolor='yellow', edgecolor='darkorange', linewidth=2)
    ax.add_patch(neck)
    
    # Sound waves
    for i in range(3):
        wave_radius = (i+1) * 0.3 * scale
        wave = Circle((x, y-chamber_height/2-neck_height), wave_radius,
                     fill=False, edgecolor='orange', alpha=0.5-i*0.15, 
                     linestyle='--', linewidth=1)
        ax.add_patch(wave)
    
    ax.text(x, y, 'f₀', fontsize=10, ha='center', fontweight='bold')

def draw_bifurcation_mixer(ax, x, y, scale=1.0):
    """Draw a bifurcation mixer for enhanced mixing"""
    # Y-shaped splitter/mixer
    # Main channel
    main_line = plt.Line2D([x-scale, x], [y, y], 
                          color='blue', linewidth=3*scale)
    ax.add_line(main_line)
    
    # Split channels
    upper_line = plt.Line2D([x, x+scale*0.7], [y, y+scale*0.5],
                           color='blue', linewidth=2*scale)
    lower_line = plt.Line2D([x, x+scale*0.7], [y, y-scale*0.5],
                           color='blue', linewidth=2*scale)
    ax.add_line(upper_line)
    ax.add_line(lower_line)
    
    # Recombination
    recomb_upper = plt.Line2D([x+scale*0.7, x+scale*1.4], [y+scale*0.5, y],
                             color='blue', linewidth=2*scale)
    recomb_lower = plt.Line2D([x+scale*0.7, x+scale*1.4], [y-scale*0.5, y],
                             color='blue', linewidth=2*scale)
    ax.add_line(recomb_upper)
    ax.add_line(recomb_lower)
    
    # Output
    output_line = plt.Line2D([x+scale*1.4, x+scale*2], [y, y],
                            color='blue', linewidth=3*scale)
    ax.add_line(output_line)
    
    # Mixing vortices
    vortex1 = Circle((x+scale*0.35, y+scale*0.25), 0.1*scale,
                    facecolor='none', edgecolor='cyan', linestyle=':')
    vortex2 = Circle((x+scale*0.35, y-scale*0.25), 0.1*scale,
                    facecolor='none', edgecolor='cyan', linestyle=':')
    vortex3 = Circle((x+scale*1.05, y), 0.15*scale,
                    facecolor='none', edgecolor='cyan', linestyle=':')
    ax.add_patch(vortex1)
    ax.add_patch(vortex2)
    ax.add_patch(vortex3)

def plot_integrated_fluidics():
    """Show how advanced fluidic elements integrate into the lattice"""
    fig = plt.figure(figsize=(18, 12))
    
    # Main lattice with embedded fluidic elements
    ax_main = plt.subplot(2, 3, (1, 4))
    
    # Draw hexagonal lattice background
    hex_centers = []
    for row in range(5):
        for col in range(5):
            x = col * 3
            if row % 2 == 1:
                x += 1.5
            y = row * 2.6
            hex_centers.append([x, y])
            
            # Draw hexagon
            angles = np.linspace(0, 2*np.pi, 7)
            hex_x = x + 1.5 * np.cos(angles)
            hex_y = y + 1.5 * np.sin(angles)
            hex_patch = Polygon(list(zip(hex_x, hex_y)), 
                              fill=True, facecolor='lightgray', alpha=0.3,
                              edgecolor='black', linewidth=1)
            ax_main.add_patch(hex_patch)
    
    # Add different fluidic elements at specific locations
    # Tesla valve in one channel
    draw_tesla_valve(ax_main, 6, 5, scale=1.5)
    ax_main.text(6, 3.5, 'Tesla Valve\n(Directional Flow)', 
                ha='center', fontsize=9, fontweight='bold')
    
    # Vortex valve at intersection
    draw_vortex_valve(ax_main, 3, 8, scale=1.2)
    ax_main.text(3, 6, 'Vortex Valve\n(Flow Control)', 
                ha='center', fontsize=9, fontweight='bold')
    
    # Acoustic resonator
    draw_acoustic_resonator(ax_main, 9, 10, scale=1.0)
    ax_main.text(9, 8.5, 'Acoustic\nResonator', 
                ha='center', fontsize=9, fontweight='bold')
    
    # Bifurcation mixer
    draw_bifurcation_mixer(ax_main, 10, 2, scale=1.0)
    ax_main.text(11, 0.5, 'Mixing\nZone', ha='center', fontsize=9, fontweight='bold')
    
    ax_main.set_xlim(-1, 15)
    ax_main.set_ylim(-1, 14)
    ax_main.set_aspect('equal')
    ax_main.set_title('Integrated Passive Fluidic Control Elements', 
                     fontsize=14, fontweight='bold')
    ax_main.axis('off')
    
    # Individual element details
    # Tesla Valve detail
    ax_tesla = plt.subplot(2, 3, 2)
    draw_tesla_valve(ax_tesla, 0, 0, scale=3)
    ax_tesla.set_xlim(-5, 5)
    ax_tesla.set_ylim(-2, 3)
    ax_tesla.set_aspect('equal')
    ax_tesla.set_title('Tesla Valve Detail', fontsize=12, fontweight='bold')
    ax_tesla.text(0, -1.5, 'No moving parts\n10:1 flow resistance ratio\nSelf-cleaning design', 
                 ha='center', fontsize=9)
    ax_tesla.axis('off')
    
    # Vortex Valve detail
    ax_vortex = plt.subplot(2, 3, 3)
    draw_vortex_valve(ax_vortex, 0, 0, scale=2.5)
    ax_vortex.set_xlim(-4, 4)
    ax_vortex.set_ylim(-4, 4)
    ax_vortex.set_aspect('equal')
    ax_vortex.set_title('Vortex Valve Detail', fontsize=12, fontweight='bold')
    ax_vortex.text(0, -3.5, 'Fluidic switching\nPressure-activated\n100:1 turn-down ratio', 
                  ha='center', fontsize=9)
    ax_vortex.axis('off')
    
    # Acoustic Communication detail
    ax_acoustic = plt.subplot(2, 3, 5)
    draw_acoustic_resonator(ax_acoustic, 0, 0, scale=3)
    # Add frequency response
    freq = np.linspace(100, 2000, 100)
    response = np.exp(-((freq-800)/200)**2)
    ax_freq = ax_acoustic.twinx()
    ax_freq.plot(freq/100-10, response*3-1.5, 'r-', alpha=0.7, linewidth=2)
    ax_freq.set_ylim(-2, 2)
    ax_freq.axis('off')
    
    ax_acoustic.set_xlim(-4, 4)
    ax_acoustic.set_ylim(-4, 4)
    ax_acoustic.set_aspect('equal')
    ax_acoustic.set_title('Acoustic State Signaling', fontsize=12, fontweight='bold')
    ax_acoustic.text(0, -3.5, 'Pressure pulse comm.\n800 Hz resonance\nDistributed sensing', 
                    ha='center', fontsize=9)
    ax_acoustic.axis('off')
    
    # Flow routing schematic
    ax_routing = plt.subplot(2, 3, 6)
    
    # Show complex routing possibilities
    # Input manifold
    ax_routing.add_patch(Rectangle((-4, -2), 0.5, 4, 
                                  facecolor='blue', alpha=0.7))
    ax_routing.text(-4.5, 0, 'IN', fontsize=10, fontweight='bold', ha='right')
    
    # Multiple paths with different elements
    # Path 1: Direct with Tesla valve
    ax_routing.arrow(-3.5, 1.5, 2, 0, head_width=0.2, head_length=0.2,
                    fc='blue', ec='blue', alpha=0.7)
    ax_routing.text(-2.5, 2, 'Tesla', fontsize=8)
    
    # Path 2: Through vortex valve
    ax_routing.arrow(-3.5, 0, 1, 0, head_width=0.2, head_length=0.2,
                    fc='blue', ec='blue', alpha=0.7)
    draw_vortex_valve(ax_routing, -1, 0, scale=0.5)
    ax_routing.arrow(-0.5, 0, 1, 0, head_width=0.2, head_length=0.2,
                    fc='blue', ec='blue', alpha=0.7)
    
    # Path 3: Bifurcation mixing
    ax_routing.arrow(-3.5, -1.5, 2, 0, head_width=0.2, head_length=0.2,
                    fc='blue', ec='blue', alpha=0.7)
    draw_bifurcation_mixer(ax_routing, -0.5, -1.5, scale=0.5)
    
    # Convergence
    for y in [1.5, 0, -1.5]:
        ax_routing.arrow(1, y, 1, 0, head_width=0.2, head_length=0.2,
                        fc='green', ec='green', alpha=0.7)
    
    # Output manifold
    ax_routing.add_patch(Rectangle((2.5, -2), 0.5, 4, 
                                  facecolor='green', alpha=0.7))
    ax_routing.text(3.5, 0, 'OUT', fontsize=10, fontweight='bold')
    
    ax_routing.set_xlim(-5, 4)
    ax_routing.set_ylim(-3, 3)
    ax_routing.set_aspect('equal')
    ax_routing.set_title('Smart Flow Routing', fontsize=12, fontweight='bold')
    ax_routing.text(0, -2.5, 'Self-regulating • No electronics • Passive control', 
                   ha='center', fontsize=9, style='italic')
    ax_routing.axis('off')
    
    plt.suptitle('Advanced Passive Fluidic Control in Bio-Hybrid Lattice', 
                fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    return fig

def plot_comparison_table():
    """Create comparison of fluidic elements"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Table data
    headers = ['Element', 'Function', 'Key Advantage', 'No Moving Parts', 'Self-Cleaning']
    
    data = [
        ['Tesla Valve', 'Directional flow control', '10:1 resistance ratio', '✓', '✓'],
        ['Vortex Valve', 'Flow switching/throttling', '100:1 turn-down', '✓', '✓'],
        ['Acoustic Resonator', 'State communication', 'Distributed sensing', '✓', '✓'],
        ['Bifurcation Mixer', 'Enhanced mixing', 'Passive turbulence', '✓', '✓'],
        ['Coanda Nozzle', 'Flow attachment control', 'Bistable switching', '✓', '✓'],
        ['Venturi Restrictor', 'Pressure regulation', 'Self-limiting flow', '✓', '✓']
    ]
    
    # Create table
    table = ax.table(cellText=data, colLabels=headers, 
                    cellLoc='center', loc='center',
                    colWidths=[0.15, 0.25, 0.25, 0.15, 0.15])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)
    
    # Style header
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style cells
    for i in range(1, len(data) + 1):
        for j in range(len(headers)):
            if j >= 3:  # Checkmark columns
                table[(i, j)].set_facecolor('#E8F5E9')
            else:
                table[(i, j)].set_facecolor('#F5F5F5')
    
    plt.title('Passive Fluidic Elements for Autonomous Operation', 
             fontsize=14, fontweight='bold', pad=20)
    
    # Add note
    plt.text(0.5, 0.1, 
            'All elements operate without external power or electronic control\n' +
            'Manufacturing: Compatible with 3D printing (FDM/SLA/SLS)\n' +
            'Scale: Optimized for 1-5mm channel diameters',
            ha='center', fontsize=10, style='italic',
            transform=ax.transAxes)
    
    return fig

def main():
    """Generate advanced fluidics visualizations"""
    
    print("Generating integrated fluidics visualization...")
    fig1 = plot_integrated_fluidics()
    save_path1 = 'C:/Users/Jay/My Drive/ROBOTICS/TB/paper/figures/simulations/advanced_fluidics_integration.png'
    fig1.savefig(save_path1, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path1}")
    
    print("Generating fluidic elements comparison table...")
    fig2 = plot_comparison_table()
    save_path2 = 'C:/Users/Jay/My Drive/ROBOTICS/TB/paper/figures/simulations/fluidic_elements_table.png'
    fig2.savefig(save_path2, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path2}")
    
    plt.show()
    
    print("\nAdvanced fluidics visualizations complete!")
    print("Tesla valves and other passive elements integrated into design")

if __name__ == "__main__":
    main()