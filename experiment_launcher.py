"""
Bio-Hybrid Systems Experiment Launcher
Quick access to all experimental tools
"""

import os
import sys
import subprocess

def print_header():
    print("""
🔬 Bio-Hybrid Systems Experimental Framework
==========================================

GPU-accelerated simulations for autonomous bio-hybrid organisms
Based on distributed micro-combustion and flow lattice architecture

Hardware Detected:
- GPU: Quadro RTX 5000 (16GB VRAM) ✅
- CUDA: Version 12.1 ✅
- Python: 3.11 in biohybrid environment ✅
""")

def main_menu():
    while True:
        print("""
📋 Available Experiments:

1. 🔥 Heat Transfer Simulation (GPU-accelerated)
   - Validate Q ∝ 1/d scaling law
   - Compare 2-12mm chamber sizes
   - GPU-accelerated heat equation solver

2. 💧 Pressure Drop Analysis
   - Hagen-Poiseuille flow calculations  
   - Honeycomb lattice design optimization
   - Flow rate vs pressure drop relationships

3. 🏗️ 3D Lattice Generator
   - Hexagonal honeycomb structures
   - STL export for 3D printing
   - Heat transfer surface analysis

4. 🧪 Installation Check
   - Verify all components working
   - Performance benchmarks
   - Troubleshooting diagnostics

5. 📊 Jupyter Notebook
   - Interactive analysis environment
   - Custom experiment design
   - Real-time visualization

6. 📁 Open Results Folder
   - View generated files
   - Export data and plots

0. Exit

Enter choice (0-6): """, end="")

        choice = input().strip()
        
        if choice == "1":
            run_heat_simulation()
        elif choice == "2":
            run_pressure_analysis()
        elif choice == "3":
            run_lattice_generator()
        elif choice == "4":
            run_installation_check()
        elif choice == "5":
            launch_jupyter()
        elif choice == "6":
            open_results_folder()
        elif choice == "0":
            print("\n👋 Goodbye! Happy experimenting!")
            break
        else:
            print("❌ Invalid choice. Please enter 0-6.")

def run_heat_simulation():
    """Launch heat transfer simulation"""
    print("\n🔥 Starting Heat Transfer Simulation...")
    print("This will run GPU-accelerated heat diffusion simulations")
    print("comparing different micro-chamber sizes.\n")
    
    try:
        subprocess.run([sys.executable, "heat_solver_gpu.py"], check=True)
        print("\n✅ Heat simulation completed successfully!")
        input("Press Enter to continue...")
    except subprocess.CalledProcessError:
        print("❌ Heat simulation failed. Check installation.")
        input("Press Enter to continue...")
    except FileNotFoundError:
        print("❌ heat_solver_gpu.py not found. Ensure you're in the correct directory.")
        input("Press Enter to continue...")

def run_pressure_analysis():
    """Launch pressure drop analysis"""
    print("\n💧 Starting Pressure Drop Analysis...")
    print("This will analyze flow characteristics of honeycomb lattices")
    print("using Hagen-Poiseuille equations.\n")
    
    try:
        subprocess.run([sys.executable, "pressure_drop_analysis.py"], check=True)
        print("\n✅ Pressure analysis completed successfully!")
        input("Press Enter to continue...")
    except subprocess.CalledProcessError:
        print("❌ Pressure analysis failed. Check installation.")
        input("Press Enter to continue...")
    except FileNotFoundError:
        print("❌ pressure_drop_analysis.py not found.")
        input("Press Enter to continue...")

def run_lattice_generator():
    """Launch 3D lattice generator"""
    print("\n🏗️ Starting 3D Lattice Generator...")
    print("This will create hexagonal honeycomb structures")
    print("and export STL files for 3D printing.\n")
    
    try:
        subprocess.run([sys.executable, "lattice_generator.py"], check=True)
        print("\n✅ Lattice generation completed successfully!")
        input("Press Enter to continue...")
    except subprocess.CalledProcessError:
        print("❌ Lattice generation failed. Check installation.")
        input("Press Enter to continue...")
    except FileNotFoundError:
        print("❌ lattice_generator.py not found.")
        input("Press Enter to continue...")

def run_installation_check():
    """Run installation diagnostics"""
    print("\n🧪 Running Installation Check...")
    print("This will verify all components are properly installed.\n")
    
    try:
        subprocess.run([sys.executable, "installation_check.py"], check=True)
        input("Press Enter to continue...")
    except subprocess.CalledProcessError:
        print("❌ Installation check failed.")
        input("Press Enter to continue...")
    except FileNotFoundError:
        print("❌ installation_check.py not found.")
        input("Press Enter to continue...")

def launch_jupyter():
    """Launch Jupyter notebook"""
    print("\n📊 Launching Jupyter Notebook...")
    print("This will open the interactive analysis environment.")
    print("You can create custom experiments and visualizations.\n")
    
    try:
        print("Starting Jupyter server...")
        subprocess.run(["jupyter", "notebook"], check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to launch Jupyter. Check installation.")
        input("Press Enter to continue...")
    except FileNotFoundError:
        print("❌ Jupyter not found. Install with: pip install jupyter")
        input("Press Enter to continue...")

def open_results_folder():
    """Open results folder in file explorer"""
    print("\n📁 Opening results folder...")
    
    try:
        current_dir = os.getcwd()
        subprocess.run(["explorer", current_dir], check=True)
        print("✅ Results folder opened in Windows Explorer")
        input("Press Enter to continue...")
    except subprocess.CalledProcessError:
        print("❌ Failed to open folder.")
        print(f"Manual path: {os.getcwd()}")
        input("Press Enter to continue...")

if __name__ == "__main__":
    try:
        print_header()
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your installation and try again.")
