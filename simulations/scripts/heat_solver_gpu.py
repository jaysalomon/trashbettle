"""
GPU-accelerated Heat Equation Solver for Bio-Hybrid Systems
Based on the experimental framework document - Section 1.2

This script simulates heat diffusion from micro-combustion chambers
to validate the thermal coupling efficiency claims.
"""

import torch
import matplotlib.pyplot as plt
import numpy as np
import time

def create_heat_solver():
    """
    Creates a GPU-accelerated heat equation solver for micro-chamber analysis
    """
    # Check GPU availability
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    if device.type == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    
    # 2D grid parameters (adjust based on available VRAM)
    nx, ny = 512, 512  # Can increase to 1024x1024 for RTX 5000
    dx, dy = 0.001, 0.001  # 1 mm spacing → fine enough to resolve a 4 mm chamber
    dt = 0.01  # time step (s)
    
    # Physical parameters
    alpha = 1e-5  # thermal diffusivity of water (m²/s)
    
    # Initial temperature field (K)
    T = torch.full((nx, ny), 298.0, device=device, dtype=torch.float32)  # ambient
    
    return T, device, nx, ny, dx, dy, dt, alpha

def add_heat_source(T, device, nx, ny, dx, chamber_diameter_mm=4, temperature=350):
    """
    Add a circular heat source to simulate micro-combustion chamber
    """
    center = (nx//2, ny//2)
    radius = int(chamber_diameter_mm / (dx * 1000))  # Convert mm to grid points
    
    # Create circular mask
    y_indices, x_indices = torch.meshgrid(
        torch.arange(ny, device=device), 
        torch.arange(nx, device=device), 
        indexing='ij'
    )
    
    mask = ((x_indices - center[0])**2 + (y_indices - center[1])**2) <= radius**2
    T[mask] = temperature
    
    return T, mask

def create_laplacian_kernel(device):
    """
    Create convolution kernel for Laplacian (5-point stencil)
    """
    kernel = torch.tensor([[0., 1., 0.],
                          [1., -4., 1.],
                          [0., 1., 0.]], device=device).unsqueeze(0).unsqueeze(0)
    return kernel

def heat_diffusion_step(T, kernel, alpha, dt, dx, dy):
    """
    Single time step of heat diffusion equation
    """
    laplace = torch.nn.functional.conv2d(
        T.unsqueeze(0).unsqueeze(0), kernel, padding=1
    )
    return T + alpha * dt / (dx * dy) * laplace.squeeze()

def run_heat_simulation(chamber_diameter=4, num_steps=200, save_animation=False):
    """
    Run complete heat simulation for given chamber diameter
    """
    print(f"Running simulation for {chamber_diameter}mm chamber...")
    
    # Initialize solver
    T, device, nx, ny, dx, dy, dt, alpha = create_heat_solver()
    
    # Add heat source
    T, heat_mask = add_heat_source(T, device, nx, ny, dx, chamber_diameter)
    
    # Create Laplacian kernel
    kernel = create_laplacian_kernel(device)
    
    # Storage for results
    if save_animation:
        temperature_history = []
    
    # Run simulation
    start_time = time.time()
    
    for step in range(num_steps):
        T = heat_diffusion_step(T, kernel, alpha, dt, dx, dy)
        
        if save_animation and step % 10 == 0:
            temperature_history.append(T.cpu().numpy().copy())
        
        if step % 50 == 0:
            print(f"Step {step}/{num_steps}, Max temp: {T.max():.1f}K")
    
    simulation_time = time.time() - start_time
    print(f"Simulation completed in {simulation_time:.2f} seconds")
    
    # Calculate heat delivery metrics
    final_temp = T.cpu().numpy()
    heat_delivered = np.sum(final_temp - 298.0)  # Total heat above ambient
    heat_per_area = heat_delivered / (np.pi * (chamber_diameter/2)**2)
    
    print(f"Total heat delivered: {heat_delivered:.1f} K·pixels")
    print(f"Heat per unit area: {heat_per_area:.3f} K·pixels/mm²")
    
    return final_temp, heat_delivered, heat_per_area, temperature_history if save_animation else None

def visualize_results(temperature_field, chamber_diameter):
    """
    Create visualization of temperature field
    """
    plt.figure(figsize=(10, 8))
    im = plt.imshow(temperature_field, cmap='hot', origin='lower', 
                   extent=[0, 512, 0, 512])  # mm scale
    plt.colorbar(im, label='Temperature (K)')
    plt.title(f'Heat diffusion from {chamber_diameter}mm micro-chamber')
    plt.xlabel('Position (grid points)')
    plt.ylabel('Position (grid points)')
    plt.show()

def compare_chamber_sizes():
    """
    Compare heat delivery efficiency for different chamber sizes
    Validates the Q_delivery ∝ 1/d claim from the paper
    """
    chamber_sizes = [2, 4, 6, 8, 12]  # mm
    heat_delivered = []
    heat_per_area = []
    
    for diameter in chamber_sizes:
        _, heat_total, heat_area, _ = run_heat_simulation(diameter, num_steps=100)
        heat_delivered.append(heat_total)
        heat_per_area.append(heat_area)
    
    # Plot results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Total heat delivered
    ax1.plot(chamber_sizes, heat_delivered, 'bo-')
    ax1.set_xlabel('Chamber Diameter (mm)')
    ax1.set_ylabel('Total Heat Delivered')
    ax1.set_title('Heat Delivery vs Chamber Size')
    ax1.grid(True)
    
    # Heat per unit area (should show 1/d relationship)
    ax2.plot(chamber_sizes, heat_per_area, 'ro-')
    ax2.plot(chamber_sizes, [heat_per_area[0] * chamber_sizes[0] / d for d in chamber_sizes], 
             'r--', label='1/d scaling')
    ax2.set_xlabel('Chamber Diameter (mm)')
    ax2.set_ylabel('Heat per Unit Area')
    ax2.set_title('Heat Efficiency vs Chamber Size')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    return chamber_sizes, heat_delivered, heat_per_area

if __name__ == "__main__":
    print("Bio-Hybrid Systems Heat Solver")
    print("=" * 40)
    
    # Single simulation for 4mm chamber
    final_temp, _, _, _ = run_heat_simulation(chamber_diameter=4, num_steps=200)
    visualize_results(final_temp, 4)
    
    # Comparative analysis
    print("\nRunning comparative analysis...")
    sizes, heat_total, heat_area = compare_chamber_sizes()
    
    print("\nResults Summary:")
    for i, size in enumerate(sizes):
        print(f"{size}mm chamber: {heat_area[i]:.3f} heat/area")
        if i > 0:
            efficiency_ratio = heat_area[0] / heat_area[i]
            size_ratio = size / sizes[0]
            print(f"  Efficiency vs {sizes[0]}mm: {efficiency_ratio:.2f}x (theory: {size_ratio:.2f}x)")
