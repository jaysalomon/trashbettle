"""
Installation and Testing Checklist for Bio-Hybrid Systems Experiments
Run this script to verify all components are properly installed
"""

import sys
import subprocess

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and version.minor >= 11:
        return True
    else:
        print("❌ Python 3.11+ required")
        return False

def check_imports():
    """Test all required imports"""
    packages = [
        'torch', 'torchvision', 'numpy', 'matplotlib', 'scipy', 
        'pandas', 'seaborn', 'jupyter', 'plotly', 'dash',
        'meshio', 'trimesh', 'vtk', 'cv2', 'skimage'
    ]
    
    results = {}
    for package in packages:
        try:
            if package == 'cv2':
                import cv2
                results[package] = f"✅ {cv2.__version__}"
            elif package == 'skimage':
                import skimage
                results[package] = f"✅ {skimage.__version__}"
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'unknown')
                results[package] = f"✅ {version}"
        except ImportError as e:
            results[package] = f"❌ Not installed: {e}"
    
    return results

def check_cuda():
    """Test CUDA functionality"""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0)
            memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            cuda_version = torch.version.cuda
            
            print(f"✅ CUDA {cuda_version}")
            print(f"✅ GPU: {device_name}")
            print(f"✅ VRAM: {memory:.1f} GB")
            print(f"✅ Device count: {device_count}")
            
            # Test GPU computation
            x = torch.randn(1000, 1000, device='cuda')
            y = torch.matmul(x, x)
            print("✅ GPU computation test passed")
            
            return True
        else:
            print("❌ CUDA not available")
            return False
    except Exception as e:
        print(f"❌ CUDA test failed: {e}")
        return False

def test_heat_solver():
    """Test heat solver functionality"""
    try:
        print("\n🧪 Testing Heat Solver...")
        import torch
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Small test simulation
        nx, ny = 64, 64
        T = torch.full((nx, ny), 298.0, device=device)
        
        # Add small heat source
        center = (nx//2, ny//2)
        radius = 5
        mask = ((torch.arange(nx, device=device)[:,None] - center[0])**2 + 
                (torch.arange(ny, device=device)[None,:] - center[1])**2) <= radius**2
        T[mask] = 350.0
        
        # Simple diffusion step
        kernel = torch.tensor([[0., 1., 0.], [1., -4., 1.], [0., 1., 0.]], 
                             device=device).unsqueeze(0).unsqueeze(0)
        
        for _ in range(10):
            laplace = torch.nn.functional.conv2d(
                T.unsqueeze(0).unsqueeze(0), kernel, padding=1
            )
            T = T + 0.01 * laplace.squeeze()
        
        max_temp = T.max().item()
        print(f"✅ Heat solver test: Max temp = {max_temp:.1f}K")
        return True
        
    except Exception as e:
        print(f"❌ Heat solver test failed: {e}")
        return False

def test_visualization():
    """Test matplotlib functionality"""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend for testing
        import matplotlib.pyplot as plt
        import numpy as np
        
        # Simple plot test
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        plt.figure(figsize=(6, 4))
        plt.plot(x, y)
        plt.title("Test Plot")
        plt.savefig("test_plot.png", dpi=150, bbox_inches='tight')
        plt.close()
        
        print("✅ Matplotlib visualization test passed")
        return True
        
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        return False

def test_3d_capabilities():
    """Test 3D modeling capabilities"""
    try:
        import trimesh
        import numpy as np
        
        # Create simple cylinder
        cylinder = trimesh.creation.cylinder(radius=0.001, height=0.01)
        
        # Test basic properties
        volume = cylinder.volume
        area = cylinder.area
        
        print(f"✅ 3D modeling test: Volume = {volume*1e9:.3f} mm³")
        return True
        
    except Exception as e:
        print(f"❌ 3D modeling test failed: {e}")
        return False

def performance_benchmark():
    """Run performance benchmark"""
    try:
        import torch
        import time
        
        print("\n⚡ Performance Benchmark...")
        
        # CPU benchmark
        x_cpu = torch.randn(2000, 2000)
        start = time.time()
        y_cpu = torch.matmul(x_cpu, x_cpu)
        cpu_time = time.time() - start
        
        print(f"CPU: {cpu_time:.3f} seconds")
        
        # GPU benchmark (if available)
        if torch.cuda.is_available():
            x_gpu = torch.randn(2000, 2000, device='cuda')
            torch.cuda.synchronize()
            start = time.time()
            y_gpu = torch.matmul(x_gpu, x_gpu)
            torch.cuda.synchronize()
            gpu_time = time.time() - start
            
            speedup = cpu_time / gpu_time
            print(f"GPU: {gpu_time:.3f} seconds")
            print(f"GPU Speedup: {speedup:.1f}x")
            
            if speedup > 5:
                print("✅ GPU acceleration is working well")
            else:
                print("⚠️  GPU speedup is lower than expected")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        return False

def main():
    """Run complete installation check"""
    print("Bio-Hybrid Systems Installation Check")
    print("=" * 50)
    
    # Basic checks
    print("\n📋 Basic System Check:")
    python_ok = check_python_version()
    
    print(f"\n📦 Package Check:")
    package_results = check_imports()
    for package, status in package_results.items():
        print(f"  {package}: {status}")
    
    # CUDA check
    print(f"\n🚀 GPU/CUDA Check:")
    cuda_ok = check_cuda()
    
    # Functional tests
    print(f"\n🧪 Functional Tests:")
    heat_ok = test_heat_solver()
    viz_ok = test_visualization()
    mesh_ok = test_3d_capabilities()
    
    # Performance test
    perf_ok = performance_benchmark()
    
    # Summary
    print(f"\n📊 Installation Summary:")
    print("=" * 30)
    
    all_checks = [
        ("Python 3.11+", python_ok),
        ("Required packages", all("✅" in status for status in package_results.values())),
        ("CUDA/GPU", cuda_ok),
        ("Heat solver", heat_ok),
        ("Visualization", viz_ok),
        ("3D modeling", mesh_ok),
        ("Performance", perf_ok)
    ]
    
    passed = sum(1 for _, status in all_checks if status)
    total = len(all_checks)
    
    for check_name, status in all_checks:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check_name}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All systems ready! You can begin experiments.")
        print("\nNext steps:")
        print("1. Run: python heat_solver_gpu.py")
        print("2. Run: python pressure_drop_analysis.py") 
        print("3. Run: python lattice_generator.py")
        print("4. Open Jupyter notebook for interactive analysis")
    else:
        print(f"\n⚠️  {total-passed} issues found. Please resolve before proceeding.")
        print("\nTroubleshooting:")
        print("- Ensure conda environment 'biohybrid' is activated")
        print("- Check NVIDIA drivers are up to date")
        print("- Reinstall failed packages with conda/pip")

if __name__ == "__main__":
    main()
