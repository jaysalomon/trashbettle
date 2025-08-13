"""
Pressure Drop Analysis for Flow Lattice Systems
Based on experimental framework document - Section 1.4

This script analyzes pressure drop in honeycomb lattice structures
using Hagen-Poiseuille equation for laminar flow.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def hagen_poiseuille_flow(diameter, length, viscosity, pressure_drop):
    """
    Calculate flow rate through circular pipe using Hagen-Poiseuille equation
    
    Parameters:
    - diameter: pipe diameter (m)
    - length: pipe length (m) 
    - viscosity: dynamic viscosity (Pa·s)
    - pressure_drop: pressure difference (Pa)
    
    Returns:
    - flow_rate: volumetric flow rate (m³/s)
    """
    return (np.pi * diameter**4 * pressure_drop) / (128 * viscosity * length)

def lattice_flow_analysis():
    """
    Analyze flow characteristics of honeycomb lattice structure
    """
    # Physical parameters
    d = 0.002  # 2 mm channel diameter (m)
    L = 0.1    # length of a tile (m)
    mu = 8e-4  # dynamic viscosity of water at 25°C (Pa·s)
    
    # Lattice parameters
    N_channels = np.array([1000, 5000, 10000, 15000, 20000])  # number of parallel channels
    target_pressure_drops = np.array([500, 1000, 1500, 2000, 2500])  # Pa
    
    results = []
    
    print("Flow Lattice Analysis")
    print("=" * 50)
    print(f"Channel diameter: {d*1000:.1f} mm")
    print(f"Channel length: {L*100:.1f} cm")
    # Avoid Unicode mu to prevent Windows console encoding issues
    print(f"Fluid: Water (mu = {mu*1000:.1f} mPa·s)")
    print()
    
    for N in N_channels:
        for dp in target_pressure_drops:
            # Single channel flow rate
            Q_single = hagen_poiseuille_flow(d, L, mu, dp)
            
            # Total flow rate for N parallel channels
            Q_total = N * Q_single
            
            # Flow velocity in single channel
            area_single = np.pi * (d/2)**2
            velocity = Q_single / area_single
            
            # Reynolds number
            rho = 1000  # water density kg/m³
            Re = (rho * velocity * d) / mu
            
            results.append({
                'N_channels': N,
                'pressure_drop_Pa': dp,
                'Q_single_m3s': Q_single,
                'Q_total_m3s': Q_total,
                'Q_total_Lmin': Q_total * 60 * 1000,  # L/min
                'velocity_ms': velocity,
                'reynolds_number': Re
            })
    
    return pd.DataFrame(results)

def design_lattice_for_target_flow(target_flow_Lmin=10, max_pressure_drop=1500):
    """
    Design lattice to achieve target flow rate
    """
    # Convert target flow to m³/s
    target_flow = target_flow_Lmin / (60 * 1000)
    
    # Physical parameters
    d = 0.002  # 2 mm channel diameter (m)
    L = 0.1    # length of a tile (m)
    mu = 8e-4  # dynamic viscosity of water at 25°C (Pa·s)
    
    # Calculate required number of channels
    Q_single = hagen_poiseuille_flow(d, L, mu, max_pressure_drop)
    N_required = int(np.ceil(target_flow / Q_single))
    
    # Actual performance
    Q_actual = N_required * Q_single
    
    print(f"\nLattice Design for {target_flow_Lmin} L/min:")
    print("=" * 40)
    print(f"Required channels: {N_required:,}")
    print(f"Actual flow rate: {Q_actual * 60 * 1000:.2f} L/min")
    print(f"Pressure drop: {max_pressure_drop} Pa")
    print(f"Single channel flow: {Q_single * 1e6:.2f} uL/s")
    
    # Calculate lattice geometry
    # Assuming hexagonal packing with 2.5mm spacing between centers
    spacing = 0.0025  # m
    area_per_channel = spacing**2 * np.sqrt(3)/2  # hexagonal unit cell
    total_area = N_required * area_per_channel
    lattice_size = np.sqrt(total_area)
    
    print(f"Lattice area: {total_area*1e4:.1f} cm²")
    print(f"Lattice size: {lattice_size*100:.1f} cm × {lattice_size*100:.1f} cm")
    
    return N_required, Q_actual, lattice_size

def plot_pressure_flow_relationships(df):
    """
    Create visualization of pressure-flow relationships
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot 1: Flow rate vs pressure drop for different channel counts
    channel_counts = df['N_channels'].unique()
    for N in channel_counts:
        subset = df[df['N_channels'] == N]
        ax1.plot(subset['pressure_drop_Pa'], subset['Q_total_Lmin'], 
                'o-', label=f'{N:,} channels')
    
    ax1.set_xlabel('Pressure Drop (Pa)')
    ax1.set_ylabel('Total Flow Rate (L/min)')
    ax1.set_title('Flow Rate vs Pressure Drop')
    ax1.legend()
    ax1.grid(True)
    
    # Plot 2: Scaling with number of channels
    pressure_drops = df['pressure_drop_Pa'].unique()
    for dp in [1000, 2000]:  # Select representative pressure drops
        subset = df[df['pressure_drop_Pa'] == dp]
        ax2.plot(subset['N_channels'], subset['Q_total_Lmin'], 
                'o-', label=f'{dp} Pa')
    
    ax2.set_xlabel('Number of Channels')
    ax2.set_ylabel('Total Flow Rate (L/min)')
    ax2.set_title('Flow Scaling with Channel Count')
    ax2.legend()
    ax2.grid(True)
    
    # Plot 3: Reynolds number analysis
    ax3.scatter(df['velocity_ms'], df['reynolds_number'], 
               c=df['pressure_drop_Pa'], cmap='viridis', alpha=0.6)
    ax3.axhline(y=2300, color='r', linestyle='--', label='Laminar limit')
    ax3.set_xlabel('Velocity (m/s)')
    ax3.set_ylabel('Reynolds Number')
    ax3.set_title('Flow Regime Analysis')
    ax3.legend()
    ax3.grid(True)
    cbar = plt.colorbar(ax3.collections[0], ax=ax3)
    cbar.set_label('Pressure Drop (Pa)')
    
    # Plot 4: Efficiency analysis (flow per unit pressure)
    df['efficiency'] = df['Q_total_Lmin'] / df['pressure_drop_Pa']
    for N in channel_counts:
        subset = df[df['N_channels'] == N]
        ax4.plot(subset['pressure_drop_Pa'], subset['efficiency'], 
                'o-', label=f'{N:,} channels')
    
    ax4.set_xlabel('Pressure Drop (Pa)')
    ax4.set_ylabel('Flow Efficiency (L/min/Pa)')
    ax4.set_title('Hydraulic Efficiency')
    ax4.legend()
    ax4.grid(True)
    
    plt.tight_layout()
    plt.show()

def validate_laminar_assumption(df, export_path: str | None = None):
    """
    Check that flow remains laminar (Re < 2300)
    """
    max_reynolds = df['reynolds_number'].max()
    laminar_fraction = (df['reynolds_number'] < 2300).mean()
    
    print(f"\nFlow Regime Validation:")
    print("=" * 30)
    print(f"Maximum Reynolds number: {max_reynolds:.1f}")
    print(f"Fraction in laminar regime: {laminar_fraction*100:.1f}%")
    
    summary = {
        'max_reynolds': float(max_reynolds),
        'laminar_fraction': float(laminar_fraction)
    }
    if export_path:
        try:
            import json, os
            with open(export_path, 'w') as f:
                json.dump(summary, f, indent=2)
        except Exception:
            pass
    if laminar_fraction < 0.95:
        print("Warning: Some configurations may be transitional/turbulent")
        print("Hagen-Poiseuille equation may not be accurate for those cases")
    else:
        print("All configurations are laminar - analysis is valid")

if __name__ == "__main__":
    # Run complete analysis
    df = lattice_flow_analysis()
    
    # Display summary table
    print("\nSample Results:")
    print(df.head(10).round(6))
    
    # Design specific lattice
    design_lattice_for_target_flow(target_flow_Lmin=5, max_pressure_drop=1000)
    design_lattice_for_target_flow(target_flow_Lmin=20, max_pressure_drop=2000)
    
    # Validate assumptions
    validate_laminar_assumption(df, export_path='simulations/results/pressure_flow_reynolds_summary.json')
    
    # Create visualizations
    plot_pressure_flow_relationships(df)
    
    # Export results
    df.to_csv('lattice_flow_analysis.csv', index=False)
    print(f"\nResults saved to lattice_flow_analysis.csv")
