"""
Multi-Functional Flow Lattice Visualization
Generates comprehensive visualizations of the bio-hybrid system's internal architecture
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle, Polygon, Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.patches as mpatches
from matplotlib import cm
import matplotlib.colors as mcolors

def create_hexagonal_pattern(rows=7, cols=7, channel_diameter=2.0, wall_thickness=0.5):
    """Create hexagonal honeycomb pattern coordinates"""
    spacing = channel_diameter + wall_thickness
    centers = []
    
    for row in range(rows):
        for col in range(cols):
            # Hexagonal offset pattern
            x = col * spacing * np.sqrt(3)
            if row % 2 == 1:
                x += spacing * np.sqrt(3) / 2
            y = row * spacing * 1.5
            centers.append([x, y])
    
    return np.array(centers), spacing

def plot_lattice_cross_section():
    """Create cross-section view of the lattice structure"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Left: Top view of hexagonal channels
    ax1 = axes[0]
    centers, spacing = create_hexagonal_pattern(7, 7, 2.0, 0.5)
    
    # Draw hexagonal cells
    for center in centers:
        # Create hexagon vertices
        angles = np.linspace(0, 2*np.pi, 7)
        hex_x = center[0] + spacing * np.cos(angles)
        hex_y = center[1] + spacing * np.sin(angles)
        
        # Draw outer hexagon (wall)
        hex_patch = Polygon(list(zip(hex_x, hex_y)), 
                          fill=True, facecolor='lightgray', 
                          edgecolor='black', linewidth=1.5)
        ax1.add_patch(hex_patch)
        
        # Draw inner circle (channel)
        circle = Circle((center[0], center[1]), 1.0, 
                       fill=True, facecolor='white', 
                       edgecolor='darkblue', linewidth=1)
        ax1.add_patch(circle)
    
    ax1.set_xlim(-2, 23)
    ax1.set_ylim(-2, 17)
    ax1.set_aspect('equal')
    ax1.set_title('Top View: Hexagonal Channel Array\n(2mm channels, 0.5mm walls)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Width (mm)')
    ax1.set_ylabel('Height (mm)')
    ax1.grid(True, alpha=0.3)
    
    # Middle: Side view showing channel depth and micro-combustion chambers
    ax2 = axes[1]
    
    # Draw lattice structure from side
    depth = 20  # mm
    n_channels = 7
    
    for i in range(n_channels):
        x = i * 2.5
        # Main channel
        rect = Rectangle((x-1, 0), 2, depth, 
                        facecolor='lightblue', edgecolor='black', linewidth=1)
        ax2.add_patch(rect)
        
        # Micro-combustion chambers (small cavities)
        for j in range(4):
            y_pos = 3 + j * 4
            chamber = Circle((x, y_pos), 0.3, 
                           facecolor='red', edgecolor='darkred', alpha=0.7)
            ax2.add_patch(chamber)
            
            # Heat flow arrows
            ax2.arrow(x, y_pos, 0.8, 0, head_width=0.2, 
                     head_length=0.1, fc='orange', ec='orange', alpha=0.5)
            ax2.arrow(x, y_pos, -0.8, 0, head_width=0.2, 
                     head_length=0.1, fc='orange', ec='orange', alpha=0.5)
    
    ax2.set_xlim(-2, 17)
    ax2.set_ylim(-1, 21)
    ax2.set_aspect('equal')
    ax2.set_title('Side View: Channels with Micro-Combustion Sites\n(Red dots = heat sources)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Width (mm)')
    ax2.set_ylabel('Depth (mm)')
    ax2.grid(True, alpha=0.3)
    
    # Right: 3D isometric view
    ax3 = fig.add_subplot(1, 3, 3, projection='3d')
    
    # Create 3D hexagonal lattice
    centers_3d, _ = create_hexagonal_pattern(5, 5, 2.0, 0.5)
    
    for center in centers_3d:
        # Draw vertical channels
        z = np.linspace(0, 15, 50)
        theta = np.linspace(0, 2*np.pi, 50)
        
        for i in range(len(theta)):
            x = center[0] + 1.0 * np.cos(theta[i])
            y = center[1] + 1.0 * np.sin(theta[i])
            ax3.plot([x, x], [y, y], [0, 15], 'b-', alpha=0.3, linewidth=0.5)
    
    ax3.set_xlim(0, 15)
    ax3.set_ylim(0, 12)
    ax3.set_zlim(0, 15)
    ax3.set_xlabel('X (mm)')
    ax3.set_ylabel('Y (mm)')
    ax3.set_zlabel('Z (mm)')
    ax3.set_title('3D View: Lattice Structure\n(Parallel flow channels)', fontsize=12, fontweight='bold')
    ax3.view_init(elev=25, azim=45)
    
    plt.suptitle('Multi-Functional Flow Lattice Architecture', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    return fig

def plot_functional_integration():
    """Show how multiple functions are integrated in the lattice"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 14))
    
    # Function 1: Structural (load bearing)
    ax1 = axes[0, 0]
    centers, spacing = create_hexagonal_pattern(5, 5, 2.0, 0.5)
    
    for center in centers:
        angles = np.linspace(0, 2*np.pi, 7)
        hex_x = center[0] + spacing * np.cos(angles)
        hex_y = center[1] + spacing * np.sin(angles)
        
        hex_patch = Polygon(list(zip(hex_x, hex_y)), 
                          fill=True, facecolor='gray', alpha=0.7,
                          edgecolor='black', linewidth=2)
        ax1.add_patch(hex_patch)
        
        # Show stress lines
        ax1.arrow(center[0], center[1]+2, 0, -1.5, 
                 head_width=0.3, head_length=0.2, fc='blue', ec='blue')
    
    ax1.set_xlim(-2, 17)
    ax1.set_ylim(-2, 14)
    ax1.set_aspect('equal')
    ax1.set_title('STRUCTURAL FUNCTION\nLoad-bearing honeycomb geometry', fontsize=12, fontweight='bold')
    ax1.text(8, -1, 'Compressive loads distributed\nthrough lattice walls', ha='center', fontsize=10)
    
    # Function 2: Thermal (heat delivery)
    ax2 = axes[0, 1]
    
    for center in centers:
        # Channel
        circle = Circle((center[0], center[1]), 1.0, 
                       fill=True, facecolor='lightblue', 
                       edgecolor='black', linewidth=1)
        ax2.add_patch(circle)
        
        # Heat source (micro-combustion)
        heat = Circle((center[0], center[1]), 0.3, 
                     fill=True, facecolor='red', edgecolor='darkred')
        ax2.add_patch(heat)
        
        # Heat flow radial arrows
        for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
            dx = 0.7 * np.cos(angle)
            dy = 0.7 * np.sin(angle)
            ax2.arrow(center[0], center[1], dx, dy, 
                     head_width=0.15, head_length=0.1, 
                     fc='orange', ec='orange', alpha=0.6)
    
    ax2.set_xlim(-2, 17)
    ax2.set_ylim(-2, 14)
    ax2.set_aspect('equal')
    ax2.set_title('THERMAL FUNCTION\nDistributed micro-combustion chambers', fontsize=12, fontweight='bold')
    ax2.text(8, -1, 'Heat delivered directly to\nsurrounding bio-reactor volume', ha='center', fontsize=10)
    
    # Function 3: Fluidic (transport and control)
    ax3 = axes[1, 0]
    
    for i, center in enumerate(centers):
        # Channel with flow
        circle = Circle((center[0], center[1]), 1.0, 
                       fill=True, facecolor='lightcyan', 
                       edgecolor='blue', linewidth=1)
        ax3.add_patch(circle)
        
        # Flow direction indicators
        if i % 3 == 0:  # Show flow in some channels
            ax3.arrow(center[0]-0.7, center[1], 1.4, 0, 
                     head_width=0.2, head_length=0.2, 
                     fc='blue', ec='blue', alpha=0.7)
    
    # Add manifold connections
    ax3.plot([-1, -1], [-1, 13], 'b-', linewidth=3)  # Input manifold
    ax3.plot([16, 16], [-1, 13], 'b-', linewidth=3)  # Output manifold
    
    ax3.set_xlim(-3, 18)
    ax3.set_ylim(-2, 14)
    ax3.set_aspect('equal')
    ax3.set_title('FLUIDIC FUNCTION\nMass transport and pressure-based control', fontsize=12, fontweight='bold')
    ax3.text(8, -1, 'Self-regulating flow through\nvortex valves and acoustic signaling', ha='center', fontsize=10)
    
    # Function 4: Integrated system
    ax4 = axes[1, 1]
    
    # Create color map for different functions
    for i, center in enumerate(centers):
        angles = np.linspace(0, 2*np.pi, 7)
        hex_x = center[0] + spacing * np.cos(angles)
        hex_y = center[1] + spacing * np.sin(angles)
        
        # Multi-colored hexagon showing integration
        if i % 4 == 0:
            color = 'red'  # Thermal emphasis
            alpha = 0.6
        elif i % 4 == 1:
            color = 'blue'  # Flow emphasis
            alpha = 0.6
        elif i % 4 == 2:
            color = 'green'  # Bio-reactor
            alpha = 0.6
        else:
            color = 'gray'  # Structural
            alpha = 0.4
            
        hex_patch = Polygon(list(zip(hex_x, hex_y)), 
                          fill=True, facecolor=color, alpha=alpha,
                          edgecolor='black', linewidth=1.5)
        ax4.add_patch(hex_patch)
        
        circle = Circle((center[0], center[1]), 0.8, 
                       fill=False, edgecolor='white', linewidth=1)
        ax4.add_patch(circle)
    
    # Legend
    red_patch = mpatches.Patch(color='red', alpha=0.6, label='Thermal zones')
    blue_patch = mpatches.Patch(color='blue', alpha=0.6, label='Flow channels')
    green_patch = mpatches.Patch(color='green', alpha=0.6, label='Bio-processing')
    gray_patch = mpatches.Patch(color='gray', alpha=0.4, label='Structural support')
    
    ax4.legend(handles=[red_patch, blue_patch, green_patch, gray_patch], 
              loc='upper right', fontsize=9)
    
    ax4.set_xlim(-2, 17)
    ax4.set_ylim(-2, 14)
    ax4.set_aspect('equal')
    ax4.set_title('INTEGRATED MULTI-FUNCTIONAL SYSTEM\nAll functions in single monolithic structure', fontsize=12, fontweight='bold')
    ax4.text(8, -1, 'Eliminates discrete subsystems\n82% mass reduction', ha='center', fontsize=10)
    
    plt.suptitle('Multi-Functional Integration in Flow Lattice Architecture', 
                fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    return fig

def plot_scale_comparison():
    """Show the scale advantage of distributed micro-chambers"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    
    # Left: Traditional single large chamber
    ax1 = axes[0]
    
    # Large chamber
    large_chamber = Circle((5, 5), 4, fill=True, facecolor='lightcoral', 
                          edgecolor='darkred', linewidth=2)
    ax1.add_patch(large_chamber)
    
    # Heat gradient (poor distribution)
    for r in np.linspace(0.5, 3.5, 8):
        alpha = 1.0 - (r/4.0)
        gradient = Circle((5, 5), r, fill=False, 
                        edgecolor='red', alpha=alpha, linewidth=1)
        ax1.add_patch(gradient)
    
    # Annotations
    ax1.annotate('', xy=(9, 5), xytext=(5, 5),
                arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax1.text(7, 5.5, 'R = 4mm', fontsize=10)
    ax1.text(5, 1, 'Poor heat distribution\nLow surface/volume ratio\nη ≈ 60%', 
            ha='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5))
    
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.set_aspect('equal')
    ax1.set_title('CONVENTIONAL: Single Large Chamber (d=8mm)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Right: Distributed micro-chambers
    ax2 = axes[1]
    
    # Multiple small chambers
    centers, _ = create_hexagonal_pattern(4, 4, 1.0, 0.3)
    centers = centers * 0.5 + 2  # Scale and position
    
    for center in centers:
        # Small chamber
        small_chamber = Circle((center[0], center[1]), 0.5, 
                              fill=True, facecolor='lightgreen', 
                              edgecolor='darkgreen', linewidth=1)
        ax2.add_patch(small_chamber)
        
        # Excellent heat distribution
        for r in np.linspace(0.1, 0.4, 4):
            gradient = Circle((center[0], center[1]), r, 
                            fill=False, edgecolor='green', 
                            alpha=0.8, linewidth=0.5)
            ax2.add_patch(gradient)
    
    # Highlight one chamber
    ax2.annotate('', xy=(centers[5][0]+0.5, centers[5][1]), 
                xytext=(centers[5][0], centers[5][1]),
                arrowprops=dict(arrowstyle='->', color='green', lw=2))
    ax2.text(centers[5][0]+0.7, centers[5][1], 'R = 0.5mm', fontsize=10)
    
    ax2.text(5, 1, 'Excellent heat distribution\nHigh surface/volume ratio\nη > 95%', 
            ha='center', fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.5))
    
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_aspect('equal')
    ax2.set_title('DISTRIBUTED: Multiple Micro-Chambers (d=1mm)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle('Thermal Efficiency Scaling: η ∝ 1/diameter', 
                fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    return fig

def main():
    """Generate all lattice visualizations"""
    
    # Create main lattice structure visualization
    print("Generating lattice cross-section views...")
    fig1 = plot_lattice_cross_section()
    save_path1 = 'C:/Users/Jay/My Drive/ROBOTICS/TB/paper/figures/simulations/lattice_structure_views.png'
    fig1.savefig(save_path1, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path1}")
    
    # Create functional integration diagram
    print("Generating functional integration diagram...")
    fig2 = plot_functional_integration()
    save_path2 = 'C:/Users/Jay/My Drive/ROBOTICS/TB/paper/figures/simulations/lattice_functional_integration.png'
    fig2.savefig(save_path2, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path2}")
    
    # Create scale comparison
    print("Generating scale comparison...")
    fig3 = plot_scale_comparison()
    save_path3 = 'C:/Users/Jay/My Drive/ROBOTICS/TB/paper/figures/simulations/chamber_scale_comparison.png'
    fig3.savefig(save_path3, dpi=300, bbox_inches='tight')
    print(f"Saved: {save_path3}")
    
    plt.show()
    
    print("\nVisualizations saved to paper/figures/simulations/")
    print("- lattice_structure_views.png")
    print("- lattice_functional_integration.png")
    print("- chamber_scale_comparison.png")

if __name__ == "__main__":
    main()