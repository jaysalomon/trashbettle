"""
3D Lattice Structure Generator for Bio-Hybrid Systems
Creates hexagonal honeycomb lattice structures for 3D printing and CFD analysis
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import trimesh

def create_hexagonal_lattice(width, height, depth, channel_diameter, wall_thickness):
    """
    Generate hexagonal honeycomb lattice structure
    
    Parameters:
    - width, height, depth: overall dimensions (mm)
    - channel_diameter: diameter of flow channels (mm)
    - wall_thickness: thickness of lattice walls (mm)
    """
    # Convert to meters for calculations
    w, h, d = width/1000, height/1000, depth/1000
    r = channel_diameter/2000  # radius in meters
    t = wall_thickness/1000
    
    # Hexagonal spacing
    spacing = channel_diameter + wall_thickness  # center-to-center distance
    spacing_m = spacing/1000
    
    # Calculate number of hexagons that fit
    nx = int(w / (spacing_m * np.sqrt(3)/2))
    ny = int(h / (spacing_m * 1.5))
    
    print(f"Creating {nx}×{ny} hexagonal lattice")
    print(f"Total channels: {nx * ny}")
    print(f"Channel spacing: {spacing:.2f} mm")
    
    # Generate hexagon centers
    centers = []
    for i in range(nx):
        for j in range(ny):
            x = i * spacing_m * np.sqrt(3)/2
            y = j * spacing_m * 1.5
            if j % 2 == 1:  # Offset every other row
                x += spacing_m * np.sqrt(3)/4
            centers.append([x, y])
    
    return np.array(centers), nx, ny, spacing_m

def generate_stl_mesh(centers, channel_radius, depth, filename):
    """
    Generate STL mesh for 3D printing
    """
    print(f"Generating STL mesh: {filename}")
    
    # Create cylinder for each channel
    cylinders = []
    for center in centers:
        cylinder = trimesh.creation.cylinder(
            radius=channel_radius,
            height=depth/1000,
            transform=trimesh.transformations.translation_matrix([center[0], center[1], 0])
        )
        cylinders.append(cylinder)
    
    # Combine all cylinders
    combined = trimesh.util.concatenate(cylinders)
    
    # Create bounding box
    bounds = combined.bounds
    box_size = [bounds[1,0] - bounds[0,0] + 0.01,  # Add 5mm margin
                bounds[1,1] - bounds[0,1] + 0.01,
                depth/1000]
    
    bounding_box = trimesh.creation.box(box_size)
    
    # Subtract channels from bounding box to create lattice
    lattice = bounding_box.difference(combined)
    
    # Export to STL
    lattice.export(filename)
    print(f"STL exported: {filename}")
    
    return lattice

def calculate_lattice_properties(centers, channel_diameter, depth, wall_thickness):
    """
    Calculate flow and structural properties of the lattice
    """
    n_channels = len(centers)
    channel_radius = channel_diameter/2000  # m
    
    # Flow properties
    channel_area = np.pi * channel_radius**2  # m²
    total_flow_area = n_channels * channel_area
    
    # Structural properties  
    spacing = (channel_diameter + wall_thickness)/1000  # m
    lattice_area = len(centers) * spacing**2 * np.sqrt(3)/2  # hexagonal packing
    
    porosity = total_flow_area / lattice_area
    
    # Surface area for heat transfer
    channel_circumference = 2 * np.pi * channel_radius
    surface_area_per_channel = channel_circumference * depth/1000
    total_surface_area = n_channels * surface_area_per_channel
    
    properties = {
        'n_channels': n_channels,
        'total_flow_area_mm2': total_flow_area * 1e6,
        'lattice_area_mm2': lattice_area * 1e6,
        'porosity': porosity,
        'total_surface_area_mm2': total_surface_area * 1e6,
        'surface_area_per_volume': total_surface_area / (lattice_area * depth/1000)
    }
    
    return properties

def plot_lattice_2d(centers, channel_radius, title="Hexagonal Lattice"):
    """
    Create 2D visualization of lattice structure
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot channels as circles
    for center in centers:
        circle = plt.Circle((center[0]*1000, center[1]*1000), 
                          channel_radius*1000, 
                          fill=False, color='blue', linewidth=1)
        ax.add_patch(circle)
    
    ax.set_xlim(-5, max(centers[:,0])*1000 + 5)
    ax.set_ylim(-5, max(centers[:,1])*1000 + 5)
    ax.set_aspect('equal')
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def create_lattice_variants():
    """
    Create different lattice configurations for comparison
    """
    configurations = [
        {"name": "Fine_2mm", "width": 50, "height": 50, "depth": 10, 
         "channel_diameter": 2.0, "wall_thickness": 0.5},
        {"name": "Standard_4mm", "width": 50, "height": 50, "depth": 10, 
         "channel_diameter": 4.0, "wall_thickness": 1.0},
        {"name": "Coarse_6mm", "width": 50, "height": 50, "depth": 10, 
         "channel_diameter": 6.0, "wall_thickness": 1.5},
    ]
    
    results = []
    
    for config in configurations:
        print(f"\nProcessing {config['name']} configuration...")
        print("=" * 50)
        
        # Generate lattice
        centers, nx, ny, spacing = create_hexagonal_lattice(
            config["width"], config["height"], config["depth"],
            config["channel_diameter"], config["wall_thickness"]
        )
        
        # Calculate properties
        props = calculate_lattice_properties(
            centers, config["channel_diameter"], 
            config["depth"], config["wall_thickness"]
        )
        
        # Add configuration info
        props.update(config)
        results.append(props)
        
        # Create visualization
        plot_lattice_2d(centers, config["channel_diameter"]/2000, 
                       f"{config['name']} Lattice")
        
        # Generate STL (optional - comment out if trimesh not available)
        try:
            stl_filename = f"lattice_{config['name']}.stl"
            lattice_mesh = generate_stl_mesh(
                centers, config["channel_diameter"]/2000, 
                config["depth"], stl_filename
            )
        except Exception as e:
            print(f"STL generation failed: {e}")
        
        # Print properties
        print(f"Channels: {props['n_channels']}")
        print(f"Flow area: {props['total_flow_area_mm2']:.1f} mm²")
        print(f"Porosity: {props['porosity']:.1%}")
        print(f"Surface area: {props['total_surface_area_mm2']:.1f} mm²")
        print(f"Surface/volume ratio: {props['surface_area_per_volume']:.1f} m⁻¹")
    
    return results

def compare_lattice_performance(results):
    """
    Compare performance metrics across different lattice configurations
    """
    import pandas as pd
    
    df = pd.DataFrame(results)
    
    print("\nLattice Comparison Summary:")
    print("=" * 60)
    
    comparison_cols = ['name', 'channel_diameter', 'n_channels', 'porosity', 
                      'total_flow_area_mm2', 'surface_area_per_volume']
    print(df[comparison_cols].round(3))
    
    # Performance plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Channel count vs diameter
    ax1.bar(df['name'], df['n_channels'])
    ax1.set_ylabel('Number of Channels')
    ax1.set_title('Channel Count by Configuration')
    ax1.tick_params(axis='x', rotation=45)
    
    # Porosity comparison
    ax2.bar(df['name'], df['porosity'])
    ax2.set_ylabel('Porosity')
    ax2.set_title('Porosity by Configuration')
    ax2.tick_params(axis='x', rotation=45)
    
    # Flow area vs surface area
    ax3.scatter(df['total_flow_area_mm2'], df['total_surface_area_mm2'], 
               c=df['channel_diameter'], cmap='viridis', s=100)
    ax3.set_xlabel('Total Flow Area (mm²)')
    ax3.set_ylabel('Total Surface Area (mm²)')
    ax3.set_title('Flow Area vs Surface Area')
    cbar = plt.colorbar(ax3.collections[0], ax=ax3)
    cbar.set_label('Channel Diameter (mm)')
    
    # Surface area per volume
    ax4.bar(df['name'], df['surface_area_per_volume'])
    ax4.set_ylabel('Surface Area per Volume (m⁻¹)')
    ax4.set_title('Heat Transfer Surface Density')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.show()
    
    return df

if __name__ == "__main__":
    print("3D Lattice Structure Generator")
    print("=" * 50)
    print("Generating lattice variants for bio-hybrid systems...")
    
    # Create different lattice configurations
    results = create_lattice_variants()
    
    # Compare performance
    comparison_df = compare_lattice_performance(results)
    
    # Save results
    comparison_df.to_csv('lattice_comparison.csv', index=False)
    print(f"\nComparison data saved to lattice_comparison.csv")
    
    print("\nNext steps:")
    print("1. Import STL files into your 3D printer slicer")
    print("2. Use STL files for CFD analysis in OpenFOAM")
    print("3. Run pressure drop analysis on generated geometries")
    print("4. Test heat transfer performance experimentally")
