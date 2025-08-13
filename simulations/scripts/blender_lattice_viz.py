"""
Blender Python Script for 3D Lattice Structure Visualization
Run this script in Blender's Python console or as: blender --python blender_lattice_viz.py
"""

import bpy
import math
import random
from mathutils import Vector
import os

def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Clear mesh data
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

def create_material(name, color, metallic=0.5, roughness=0.5):
    """Create a material with specified properties."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (*color, 1.0)  # Base Color
    bsdf.inputs[4].default_value = metallic  # Metallic
    bsdf.inputs[7].default_value = roughness  # Roughness
    return mat

def create_hexagonal_lattice(rows=5, cols=5, channel_diameter=0.002, wall_thickness=0.001, height=0.018):
    """Create a hexagonal honeycomb lattice structure."""
    
    # Material for the lattice
    lattice_mat = create_material("Lattice_Steel", (0.7, 0.7, 0.8), metallic=0.9, roughness=0.3)
    
    # Calculate hexagon parameters
    hex_radius = channel_diameter / 2 + wall_thickness
    hex_spacing = hex_radius * math.sqrt(3)
    
    channels = []
    
    for row in range(rows):
        for col in range(cols):
            # Calculate position with hexagonal offset
            x = col * hex_spacing * 1.5
            y = row * hex_spacing
            if col % 2 == 1:
                y += hex_spacing / 2
            
            # Create cylinder for channel
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=6,  # Hexagonal
                radius=channel_diameter/2,
                depth=height,
                location=(x, y, height/2)
            )
            channel = bpy.context.active_object
            channel.name = f"Channel_{row}_{col}"
            channels.append(channel)
    
    # Create outer structure
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(cols * hex_spacing * 0.75, rows * hex_spacing / 2, height/2)
    )
    outer = bpy.context.active_object
    outer.name = "Outer_Structure"
    outer.scale = (cols * hex_spacing * 0.8, rows * hex_spacing * 0.6, height)
    
    # Boolean operations to create channels
    for channel in channels:
        modifier = outer.modifiers.new(name="Boolean", type='BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.object = channel
        # Apply modifier
        bpy.context.view_layer.objects.active = outer
        bpy.ops.object.modifier_apply(modifier="Boolean")
        # Delete channel object
        bpy.data.objects.remove(channel, do_unlink=True)
    
    # Apply material
    outer.data.materials.append(lattice_mat)
    
    return outer

def create_micro_combustion_chambers(lattice, num_chambers=9, chamber_diameter=0.004):
    """Add micro-combustion chambers to the lattice."""
    
    # Material for combustion chambers (hot zones)
    chamber_mat = create_material("Combustion_Chamber", (1.0, 0.3, 0.1), metallic=0.2, roughness=0.8)
    
    # Get lattice dimensions
    lattice_dim = lattice.dimensions
    
    chambers = []
    for i in range(num_chambers):
        row = i // 3
        col = i % 3
        
        x = (col - 1) * lattice_dim.x / 3
        y = (row - 1) * lattice_dim.y / 3
        z = lattice_dim.z / 2
        
        # Create sphere for combustion chamber
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=chamber_diameter/2,
            location=(x, y, z)
        )
        chamber = bpy.context.active_object
        chamber.name = f"Combustion_Chamber_{i}"
        chamber.data.materials.append(chamber_mat)
        chambers.append(chamber)
    
    return chambers

def create_flow_arrows(lattice):
    """Create flow direction arrows through the lattice."""
    arrow_mat = create_material("Flow_Arrow", (0.1, 0.5, 1.0), metallic=0.0, roughness=0.9)
    
    arrows = []
    for i in range(3):
        y_pos = (i - 1) * lattice.dimensions.y / 3
        
        # Create arrow using cone and cylinder
        bpy.ops.mesh.primitive_cone_add(
            radius1=0.002,
            radius2=0,
            depth=0.004,
            location=(-lattice.dimensions.x * 0.7, y_pos, lattice.dimensions.z/2)
        )
        arrow_head = bpy.context.active_object
        
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.001,
            depth=0.01,
            location=(-lattice.dimensions.x * 0.7 - 0.007, y_pos, lattice.dimensions.z/2)
        )
        arrow_shaft = bpy.context.active_object
        
        # Join arrow parts
        arrow_head.select_set(True)
        arrow_shaft.select_set(True)
        bpy.context.view_layer.objects.active = arrow_shaft
        bpy.ops.object.join()
        
        arrow_shaft.name = f"Flow_Arrow_{i}"
        arrow_shaft.data.materials.append(arrow_mat)
        arrow_shaft.rotation_euler = (0, math.pi/2, 0)
        arrows.append(arrow_shaft)
    
    return arrows

def setup_camera_and_lighting():
    """Configure camera and lighting for optimal visualization."""
    
    # Add camera
    bpy.ops.object.camera_add(location=(0.15, -0.15, 0.1))
    camera = bpy.context.active_object
    camera.rotation_euler = (math.pi/3, 0, math.pi/4)
    
    # Set camera as active
    bpy.context.scene.camera = camera
    
    # Add sun light
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 2
    sun.rotation_euler = (-math.pi/4, -math.pi/4, 0)
    
    # Add area light for soft shadows
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
    area = bpy.context.active_object
    area.data.energy = 50
    area.data.size = 5
    
    # Add HDRI environment (if available)
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (0.05, 0.05, 0.05, 1.0)  # Dark gray background

def render_lattice_visualization(output_path="../../paper/figures/schematics/"):
    """Render the lattice visualization."""
    
    # Configure render settings
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'  # or 'BLENDER_EEVEE' for faster renders
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Set output path
    os.makedirs(output_path, exist_ok=True)
    scene.render.filepath = os.path.join(output_path, "lattice_structure_3d.png")
    
    # Render
    bpy.ops.render.render(write_still=True)
    print(f"Rendered to: {scene.render.filepath}")

def create_cutaway_view(lattice):
    """Create a cutaway view of the lattice."""
    
    # Create a cube to cut away part of the lattice
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(lattice.dimensions.x * 0.25, 0, lattice.dimensions.z/2)
    )
    cutter = bpy.context.active_object
    cutter.scale = (lattice.dimensions.x * 0.5, lattice.dimensions.y * 2, lattice.dimensions.z * 2)
    
    # Boolean modifier
    modifier = lattice.modifiers.new(name="Cutaway", type='BOOLEAN')
    modifier.operation = 'DIFFERENCE'
    modifier.object = cutter
    
    # Apply modifier
    bpy.context.view_layer.objects.active = lattice
    bpy.ops.object.modifier_apply(modifier="Cutaway")
    
    # Delete cutter
    bpy.data.objects.remove(cutter, do_unlink=True)

def main():
    """Main execution function."""
    print("Creating 3D Lattice Visualization...")
    
    # Clear the scene
    clear_scene()
    
    # Create hexagonal lattice
    lattice = create_hexagonal_lattice(rows=7, cols=7)
    
    # Add micro-combustion chambers
    chambers = create_micro_combustion_chambers(lattice)
    
    # Add flow arrows
    arrows = create_flow_arrows(lattice)
    
    # Create cutaway view for better visualization
    create_cutaway_view(lattice)
    
    # Setup camera and lighting
    setup_camera_and_lighting()
    
    # Render the visualization
    render_lattice_visualization()
    
    print("Lattice visualization complete!")

if __name__ == "__main__":
    main()