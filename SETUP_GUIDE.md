# Bio-Hybrid Systems Experimental Setup

This directory contains the complete experimental framework for bio-hybrid autonomous systems research on Windows PC.

## Environment Setup

### 1. Conda Environment
```bash
# Environment already created: biohybrid
conda activate biohybrid
```

### 2. Installed Packages
- **GPU Computing**: PyTorch with CUDA 12.1 support
- **Scientific Computing**: NumPy, SciPy, Pandas
- **Visualization**: Matplotlib, Seaborn, Plotly, PyVista
- **3D Modeling**: Trimesh, Meshio, GMSH
- **CFD Support**: VTK, PyGMSH
- **Jupyter**: Notebooks with IPython kernel

## Available Scripts

### 1. `heat_solver_gpu.py`
GPU-accelerated heat equation solver for micro-combustion chambers
- Validates thermal coupling efficiency claims
- Compares different chamber sizes (2-12mm)
- Uses RTX 5000 for high-resolution simulations

**Usage:**
```bash
python heat_solver_gpu.py
```

### 2. `pressure_drop_analysis.py`
Hagen-Poiseuille flow analysis for honeycomb lattices
- Calculates pressure drop vs flow rate
- Designs lattice for target flow rates
- Validates laminar flow assumptions

**Usage:**
```bash
python pressure_drop_analysis.py
```

### 3. `lattice_generator.py`
3D lattice structure generator for prototyping
- Creates hexagonal honeycomb patterns
- Exports STL files for 3D printing
- Calculates flow and heat transfer properties

**Usage:**
```bash
python lattice_generator.py
```

## Hardware Requirements Met

✅ **GPU**: Quadro RTX 5000 (16GB VRAM) - Detected and working  
✅ **CUDA**: Version 12.1 installed and functional  
✅ **Python**: 3.11 in dedicated conda environment  
✅ **Memory**: Sufficient for large-scale simulations  

## Experimental Validation Plan

### Phase 1: Simulation Validation
1. **Heat Transfer**: Run GPU simulations to validate Q ∝ 1/d scaling
2. **Pressure Drop**: Verify Hagen-Poiseuille predictions for lattice
3. **Lattice Design**: Optimize channel size vs heat transfer efficiency

### Phase 2: Physical Prototyping
1. **Micro-chambers**: 3D print 4mm diameter test chambers
2. **Flow Lattice**: Create honeycomb structures with 2mm channels
3. **Heat Sources**: Test with resistive heating elements
4. **Measurement**: Use thermocouples and pressure gauges

### Phase 3: Bio-integration Tests
1. **Algae Bioreactor**: Test heat delivery to biological systems
2. **Actuator Integration**: Nitinol wire activation from waste heat
3. **Solar Integration**: Combined energy harvesting experiments

## Safety Guidelines

⚠️ **Electrical Safety**: Use 12V DC supplies, proper grounding  
⚠️ **Heat Protection**: Heat-resistant gloves, ventilated workspace  
⚠️ **Chemical Safety**: Proper handling of algae cultures  
⚠️ **Fire Safety**: Fire extinguisher nearby, no open flames  

## Next Steps

1. **Test Environment**: Run sample scripts to verify installation
2. **OpenFOAM Setup**: Install CFD software for advanced analysis
3. **Hardware Procurement**: Order components for physical prototypes
4. **Measurement Equipment**: Acquire thermocouples, pressure sensors

## Expected Outcomes

- Validation of 3× heat delivery improvement for 4mm vs 12mm chambers
- Optimized lattice designs for specific flow rates
- Proof-of-concept prototypes for bio-hybrid integration
- Quantitative data supporting theoretical framework

## Troubleshooting

### Common Issues:
- **CUDA not detected**: Check driver installation
- **Import errors**: Ensure conda environment is activated
- **Memory errors**: Reduce simulation grid size for initial testing
- **STL export fails**: Install additional mesh processing libraries

### Performance Optimization:
- Use GPU for all tensor operations
- Batch process multiple configurations
- Export intermediate results for analysis
- Use efficient data structures for large lattices
