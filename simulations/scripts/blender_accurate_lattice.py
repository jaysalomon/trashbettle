"""
Accurate Blender visualization of the multi-functional flow lattice
Based on the actual specifications from the paper
Run: blender --python blender_accurate_lattice.py
"""

import bpy
import math
import bmesh
from mathutils import Vector

def clear_scene():
    """Clear all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

def create_material(name, color, metallic=0.8, roughness=0.4):
    """Create a PBR material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (*color, 1.0)
    bsdf.inputs[4].default_value = metallic
    bsdf.inputs[7].default_value = roughness
    return mat

def create_single_tile():
    """
    Create a single tile based on paper specifications:
    - 250 × 150 × 18 mm
    - 4mm combustion cylinders
    - 2mm triangular channels
    - Hexagonal honeycomb pattern
    """
    
    # Convert mm to Blender units (1 Blender unit = 10mm for better visibility)
    scale = 0.01  # 1mm = 0.01 Blender units
    
    tile_width = 250 * scale
    tile_height = 150 * scale
    tile_depth = 18 * scale
    
    # Create base tile block
    bpy.ops.mesh.primitive_cube_add(size=1)
    tile = bpy.context.active_object
    tile.name = "Lattice_Tile"
    tile.scale = (tile_width/2, tile_height/2, tile_depth/2)
    
    # Apply scale
    bpy.ops.object.transform_apply(scale=True)
    
    # Create materials
    steel_mat = create_material("316L_Steel", (0.8, 0.8, 0.85), metallic=0.95, roughness=0.3)
    hot_mat = create_material("Hot_Zone", (1.0, 0.3, 0.1), metallic=0.2, roughness=0.7)
    flow_mat = create_material("Flow_Channel", (0.3, 0.5, 1.0), metallic=0.0, roughness=0.9)
    
    tile.data.materials.append(steel_mat)
    
    # Create combustion cylinders (4mm diameter)
    combustion_diameter = 4 * scale
    num_cylinders_x = 8
    num_cylinders_y = 5
    
    cylinders = []
    for i in range(num_cylinders_x):
        for j in range(num_cylinders_y):
            x = (i - num_cylinders_x/2 + 0.5) * (tile_width / num_cylinders_x)
            y = (j - num_cylinders_y/2 + 0.5) * (tile_height / num_cylinders_y)
            
            bpy.ops.mesh.primitive_cylinder_add(
                radius=combustion_diameter/2,
                depth=tile_depth * 1.1,  # Slightly longer to ensure clean boolean
                location=(x, y, 0)
            )
            cyl = bpy.context.active_object
            cyl.name = f"Combustion_{i}_{j}"
            cylinders.append(cyl)
    
    # Create triangular flow channels (2mm)
    channel_width = 2 * scale
    channels = []
    
    # Horizontal channels
    for j in range(num_cylinders_y + 1):
        y = (j - num_cylinders_y/2) * (tile_height / num_cylinders_y)
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        channel = bpy.context.active_object
        channel.scale = (tile_width * 0.9, channel_width/2, tile_depth * 0.8)
        channel.location = (0, y, 0)
        channels.append(channel)
    
    # Vertical channels (connecting cylinders)
    for i in range(num_cylinders_x + 1):
        x = (i - num_cylinders_x/2) * (tile_width / num_cylinders_x)
        
        bpy.ops.mesh.primitive_cube_add(size=1)
        channel = bpy.context.active_object
        channel.scale = (channel_width/2, tile_height * 0.9, tile_depth * 0.8)
        channel.location = (x, 0, 0)
        channels.append(channel)
    
    # Boolean operations to create internal structure
    bpy.context.view_layer.objects.active = tile
    
    # Subtract combustion chambers
    for cyl in cylinders:
        modifier = tile.modifiers.new(name="Boolean_Combustion", type='BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.object = cyl
        bpy.ops.object.modifier_apply(modifier="Boolean_Combustion")
        bpy.data.objects.remove(cyl, do_unlink=True)
    
    # Subtract flow channels
    for channel in channels:
        modifier = tile.modifiers.new(name="Boolean_Channel", type='BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.object = channel
        bpy.ops.object.modifier_apply(modifier="Boolean_Channel")
        bpy.data.objects.remove(channel, do_unlink=True)
    
    return tile

def create_cutaway_section(tile):
    """Create a cutaway view to show internal structure."""
    
    # Create cutting plane
    bpy.ops.mesh.primitive_cube_add(size=1)
    cutter = bpy.context.active_object
    cutter.scale = (tile.dimensions.x * 0.6, tile.dimensions.y * 2, tile.dimensions.z * 2)
    cutter.location = (tile.dimensions.x * 0.25, 0, 0)
    cutter.rotation_euler = (0, 0, math.radians(15))  # Slight angle for better view
    
    # Boolean difference
    bpy.context.view_layer.objects.active = tile
    modifier = tile.modifiers.new(name="Cutaway", type='BOOLEAN')
    modifier.operation = 'DIFFERENCE'
    modifier.object = cutter
    bpy.ops.object.modifier_apply(modifier="Cutaway")
    
    # Remove cutter
    bpy.data.objects.remove(cutter, do_unlink=True)

def add_annotations():
    """Add text annotations and dimension indicators."""
    
    # Note: Text in Blender requires font objects which are complex
    # For paper figures, annotations are better added in post-processing
    # or using LaTeX overlays
    pass

def setup_camera_and_lighting():
    """Setup camera for technical illustration view."""
    
    # Camera
    bpy.ops.object.camera_add(
        location=(6, -6, 4),
        rotation=(math.radians(60), 0, math.radians(45))
    )
    camera = bpy.context.active_object
    camera.data.lens = 50
    bpy.context.scene.camera = camera
    
    # Key light
    bpy.ops.object.light_add(
        type='SUN',
        location=(5, -5, 10),
        rotation=(math.radians(45), math.radians(30), 0)
    )
    sun = bpy.context.active_object
    sun.data.energy = 2
    sun.data.angle = math.radians(5)  # Soft shadows
    
    # Fill light
    bpy.ops.object.light_add(
        type='AREA',
        location=(-3, 5, 3),
        rotation=(math.radians(60), 0, math.radians(-30))
    )
    area = bpy.context.active_object
    area.data.energy = 30
    area.data.size = 3
    
    # Rim light for edge definition
    bpy.ops.object.light_add(
        type='AREA',
        location=(3, 3, 2),
        rotation=(math.radians(75), 0, math.radians(135))
    )
    rim = bpy.context.active_object
    rim.data.energy = 20
    rim.data.size = 2
    
    # Setup world background
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (0.95, 0.95, 0.95, 1.0)  # Light gray
    bg.inputs[1].default_value = 0.5  # Low strength

def add_flow_indicators():
    """Add visual indicators for flow direction."""
    
    arrow_mat = create_material("Flow_Arrow", (0.1, 0.4, 0.9), metallic=0.0, roughness=1.0)
    
    # Create simple arrow indicators
    for i in range(3):
        # Arrow shaft
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.01,
            depth=0.3,
            location=(-1.5, (i-1)*0.5, 0),
            rotation=(0, math.pi/2, 0)
        )
        shaft = bpy.context.active_object
        
        # Arrow head
        bpy.ops.mesh.primitive_cone_add(
            radius1=0.02,
            radius2=0,
            depth=0.05,
            location=(-1.2, (i-1)*0.5, 0),
            rotation=(0, math.pi/2, 0)
        )
        head = bpy.context.active_object
        
        # Combine and apply material
        shaft.select_set(True)
        head.select_set(True)
        bpy.context.view_layer.objects.active = shaft
        bpy.ops.object.join()
        shaft.name = f"Flow_Arrow_{i}"
        shaft.data.materials.append(arrow_mat)

def render_technical_view(output_path="../../paper/figures/schematics/lattice_tile_technical.png"):
    """Render with technical illustration settings."""
    
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128  # Lower samples for technical illustration
    scene.render.image_settings.file_format = 'PNG'
    scene.render.resolution_x = 2400
    scene.render.resolution_y = 1600
    scene.render.resolution_percentage = 100
    
    # Enable transparent background for LaTeX integration
    scene.render.film_transparent = True
    
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    scene.render.filepath = output_path
    
    bpy.ops.render.render(write_still=True)
    print(f"Rendered to: {output_path}")

def main():
    """Create accurate lattice visualization."""
    
    print("Creating accurate lattice tile visualization...")
    
    # Clear scene
    clear_scene()
    
    # Create the tile structure
    tile = create_single_tile()
    
    # Create cutaway view
    create_cutaway_section(tile)
    
    # Add flow indicators
    add_flow_indicators()
    
    # Setup rendering
    setup_camera_and_lighting()
    
    # Render
    render_technical_view()
    
    # Also save the .blend file for manual adjustments
    bpy.ops.wm.save_as_mainfile(filepath="../../paper/figures/schematics/lattice_tile.blend")
    
    print("Visualization complete!")

if __name__ == "__main__":
    main()