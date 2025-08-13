"""
Orchestration script for 3D visualizations
Handles both Blender and Manim rendering
"""

import os
import subprocess
import sys
from pathlib import Path

def check_dependencies():
    """Check if required tools are installed."""
    dependencies = {
        'blender': 'Blender (3D modeling)',
        'manim': 'Manim (mathematical animations)'
    }
    
    missing = []
    
    # Check Blender
    try:
        result = subprocess.run(['blender', '--version'], capture_output=True, text=True)
        print(f"✓ Blender found: {result.stdout.split()[1]}")
    except FileNotFoundError:
        missing.append('blender')
        print("✗ Blender not found in PATH")
    
    # Check Manim
    try:
        import manim
        print(f"✓ Manim found: {manim.__version__}")
    except ImportError:
        missing.append('manim')
        print("✗ Manim not installed")
    
    if missing:
        print("\n⚠️  Missing dependencies:")
        for dep in missing:
            print(f"  - {dependencies[dep]}")
        print("\nInstallation instructions:")
        if 'blender' in missing:
            print("  Blender: Download from https://www.blender.org/download/")
        if 'manim' in missing:
            print("  Manim: pip install manim")
        return False
    
    return True

def run_blender_visualization():
    """Execute Blender lattice visualization."""
    print("\n" + "="*60)
    print("Running Blender 3D Lattice Visualization")
    print("="*60)
    
    script_path = Path(__file__).parent / "blender_lattice_viz.py"
    output_dir = Path(__file__).parent.parent.parent / "paper" / "figures" / "schematics"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run Blender in background mode
    cmd = [
        'blender',
        '--background',
        '--python', str(script_path)
    ]
    
    try:
        print("Generating 3D lattice structure...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Lattice visualization complete!")
            print(f"  Output: {output_dir}/lattice_structure_3d.png")
        else:
            print("✗ Blender rendering failed:")
            print(result.stderr)
            
    except Exception as e:
        print(f"✗ Error running Blender: {e}")

def run_manim_animations():
    """Execute Manim animations."""
    print("\n" + "="*60)
    print("Running Manim Technical Animations")
    print("="*60)
    
    script_path = Path(__file__).parent / "manim_thermal_animation.py"
    output_dir = Path(__file__).parent.parent.parent / "paper" / "figures" / "simulations"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scenes = [
        "HeatTransferScene",
        "FlowLatticeAnimation",
        "EnergyBalanceVisualization"
    ]
    
    for scene in scenes:
        print(f"\nRendering {scene}...")
        cmd = [
            sys.executable, '-m', 'manim',
            '-ql',  # Low quality for quick preview (change to -qh for high quality)
            '--media_dir', str(output_dir.parent.parent / "manim_output"),
            str(script_path),
            scene
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✓ {scene} rendered successfully")
            else:
                print(f"  ✗ {scene} failed:")
                print(f"    {result.stderr}")
                
        except Exception as e:
            print(f"  ✗ Error running Manim: {e}")

def generate_matplotlib_3d():
    """Generate 3D plots using matplotlib as a fallback."""
    print("\n" + "="*60)
    print("Generating Matplotlib 3D Visualizations")
    print("="*60)
    
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    
    output_dir = Path(__file__).parent.parent.parent / "paper" / "figures" / "schematics"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 3D Surface plot of heat distribution
    fig = plt.figure(figsize=(12, 5))
    
    # Heat distribution surface
    ax1 = fig.add_subplot(121, projection='3d')
    
    # Create mesh
    x = np.linspace(-10, 10, 100)
    y = np.linspace(-10, 10, 100)
    X, Y = np.meshgrid(x, y)
    
    # Multiple heat sources (micro-chambers)
    Z = np.zeros_like(X)
    chambers = [(0, 0), (-5, -5), (5, 5), (-5, 5), (5, -5)]
    for cx, cy in chambers:
        R = np.sqrt((X - cx)**2 + (Y - cy)**2)
        Z += 50 * np.exp(-R**2 / 4)  # Gaussian heat distribution
    
    surf = ax1.plot_surface(X, Y, Z, cmap=cm.hot, alpha=0.8)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.set_zlabel('Temperature (°C)')
    ax1.set_title('Multi-Chamber Heat Distribution')
    fig.colorbar(surf, ax=ax1, shrink=0.5)
    
    # 2. 3D Lattice structure
    ax2 = fig.add_subplot(122, projection='3d')
    
    # Create honeycomb lattice points
    hex_points = []
    for i in range(5):
        for j in range(5):
            x = j * 1.5
            y = i * np.sqrt(3)
            if j % 2 == 1:
                y += np.sqrt(3) / 2
            
            # Create hexagon vertices
            for k in range(6):
                angle = k * np.pi / 3
                hx = x + np.cos(angle)
                hy = y + np.sin(angle)
                hex_points.append([hx, hy, 0])
                hex_points.append([hx, hy, 5])
    
    # Plot lattice edges
    for i in range(0, len(hex_points), 2):
        if i + 1 < len(hex_points):
            xs = [hex_points[i][0], hex_points[i+1][0]]
            ys = [hex_points[i][1], hex_points[i+1][1]]
            zs = [hex_points[i][2], hex_points[i+1][2]]
            ax2.plot(xs, ys, zs, 'b-', alpha=0.6, linewidth=1)
    
    ax2.set_xlabel('X (mm)')
    ax2.set_ylabel('Y (mm)')
    ax2.set_zlabel('Z (mm)')
    ax2.set_title('Honeycomb Lattice Structure')
    ax2.view_init(elev=30, azim=45)
    
    plt.tight_layout()
    output_path = output_dir / "matplotlib_3d_visualization.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: {output_path}")
    plt.close()
    
    # 3. Flow velocity field
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create flow field
    x = np.linspace(0, 10, 10)
    y = np.linspace(0, 10, 10)
    z = np.linspace(0, 5, 5)
    X, Y, Z = np.meshgrid(x, y, z)
    
    # Velocity components (example: flow through channels)
    U = np.ones_like(X) * 2  # Constant x-velocity
    V = 0.5 * np.sin(X/2)   # Sinusoidal y-component
    W = 0.2 * np.cos(Y/2)   # Small z-component
    
    # Normalize for better visualization
    speed = np.sqrt(U**2 + V**2 + W**2)
    
    # Plot velocity vectors
    ax.quiver(X, Y, Z, U, V, W, length=0.5, normalize=True, 
             color=plt.cm.viridis(speed.flatten()/speed.max()), alpha=0.6)
    
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title('Flow Velocity Field in Lattice Channels')
    ax.view_init(elev=20, azim=30)
    
    output_path = output_dir / "flow_field_3d.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved: {output_path}")
    plt.close()

def main():
    """Main execution."""
    print("="*60)
    print("3D VISUALIZATION GENERATOR")
    print("="*60)
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚠️  Installing missing dependencies first...")
        # Optionally auto-install manim
        response = input("Install Manim automatically? (y/n): ")
        if response.lower() == 'y':
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'manim'])
    
    # Always generate matplotlib visualizations (no dependencies)
    generate_matplotlib_3d()
    
    # Try Blender if available
    try:
        run_blender_visualization()
    except:
        print("⚠️  Blender visualization skipped")
    
    # Try Manim if available
    try:
        run_manim_animations()
    except:
        print("⚠️  Manim animations skipped")
    
    print("\n" + "="*60)
    print("VISUALIZATION GENERATION COMPLETE")
    print("="*60)
    print("\nGenerated files are in:")
    print("  - paper/figures/schematics/  (3D structures)")
    print("  - paper/figures/simulations/ (animations)")
    print("  - manim_output/             (video files)")

if __name__ == "__main__":
    main()