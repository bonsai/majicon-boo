#!/usr/bin/env python3
"""
3D Architecture Mesh Drawing Generator
Generates 3D architectural mesh drawings with building structures
"""

import numpy as np
from PIL import Image, ImageDraw
import math
import os

def create_3d_mesh_drawing(width=800, height=600, output_path="outputs/architecture_mesh.png"):
    """Create a 3D architectural mesh drawing"""
    
    # Create image with dark background
    img = Image.new('RGB', (width, height), color=(15, 15, 25))
    draw = ImageDraw.Draw(img)
    
    # Perspective projection parameters
    fov = 500
    viewer_distance = 5
    
    # Rotation angles
    rot_x = math.radians(20)
    rot_y = math.radians(30)
    
    def rotate_x(point, angle):
        x, y, z = point
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        return (x, y * cos_a - z * sin_a, y * sin_a + z * cos_a)
    
    def rotate_y(point, angle):
        x, y, z = point
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        return (x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a)
    
    def project(point):
        x, y, z = point
        scale = fov / (viewer_distance + z)
        px = int(width / 2 + x * scale)
        py = int(height / 2 + y * scale)
        return (px, py)
    
    def transform(point):
        p = rotate_x(point, rot_x)
        p = rotate_y(p, rot_y)
        return p
    
    def draw_line_3d(p1, p2, color, width=1):
        tp1 = transform(p1)
        tp2 = transform(p2)
        proj1 = project(tp1)
        proj2 = project(tp2)
        draw.line([proj1, proj2], fill=color, width=width)
    
    # Building grid parameters
    grid_size = 8
    cell_size = 1.5
    building_heights = np.random.uniform(1, 4, (grid_size, grid_size))
    
    # Smooth heights for more natural look
    from scipy.ndimage import gaussian_filter
    building_heights = gaussian_filter(building_heights, sigma=1.5)
    building_heights = np.clip(building_heights, 0.5, 5)
    
    # Color palette
    grid_color = (100, 150, 200)
    building_colors = [
        (80, 120, 180),
        (100, 140, 200),
        (120, 160, 220),
        (60, 100, 160),
    ]
    highlight_color = (150, 200, 255)
    window_color = (200, 220, 255)
    
    # Draw ground grid
    for i in range(grid_size + 1):
        x = i * cell_size - grid_size * cell_size / 2
        draw_line_3d((x, 0, -grid_size * cell_size / 2), 
                     (x, 0, grid_size * cell_size / 2), 
                     (50, 70, 100), 1)
        draw_line_3d((-grid_size * cell_size / 2, 0, x), 
                     (grid_size * cell_size / 2, 0, x), 
                     (50, 70, 100), 1)
    
    # Draw buildings
    buildings = []
    for i in range(grid_size):
        for j in range(grid_size):
            if building_heights[i, j] > 0.8:
                x = i * cell_size - grid_size * cell_size / 2 + cell_size / 2
                z = j * cell_size - grid_size * cell_size / 2 + cell_size / 2
                h = building_heights[i, j]
                buildings.append((x, z, h, i, j))
    
    # Sort by depth for proper rendering
    buildings.sort(key=lambda b: b[0] + b[1], reverse=True)
    
    # Draw each building
    for x, z, h, i, j in buildings:
        half = cell_size / 2 * 0.9
        color_idx = int(h) % len(building_colors)
        color = building_colors[color_idx]
        
        # Building base corners
        corners = [
            (x - half, 0, z - half),
            (x + half, 0, z - half),
            (x + half, 0, z + half),
            (x - half, 0, z + half),
        ]
        
        # Building top corners
        top_corners = [(c[0], h, c[2]) for c in corners]
        
        # Draw vertical edges
        for base, top in zip(corners, top_corners):
            draw_line_3d(base, top, color, 1)
        
        # Draw top edges
        for k in range(4):
            draw_line_3d(top_corners[k], top_corners[(k+1) % 4], color, 1)
        
        # Draw windows (grid pattern on building)
        if h > 1.5:
            num_windows = int(h)
            for wy in range(1, num_windows):
                window_y = wy * h / num_windows
                for wx in range(2):
                    for wz in range(2):
                        if np.random.random() > 0.3:  # Some windows lit
                            face_idx = wz * 2 + wx
                            if face_idx == 0:  # Front face
                                wx_pos = x - half + cell_size / 4
                                wz_pos = z - half + cell_size / 6
                            elif face_idx == 1:  # Right face
                                wx_pos = x + half - cell_size / 6
                                wz_pos = z - half + cell_size / 4
                            else:
                                continue
                            draw_line_3d(
                                (wx_pos, window_y - 0.1, wz_pos),
                                (wx_pos, window_y + 0.1, wz_pos),
                                window_color, 1
                            )
    
    # Add title and info
    title_font_size = 24
    draw.text((20, 20), "3D Architecture Mesh", fill=(150, 180, 220))
    draw.text((20, 45), f"Buildings: {len(buildings)}", fill=(100, 130, 160))
    draw.text((20, 65), f"Grid: {grid_size}x{grid_size}", fill=(100, 130, 160))
    
    # Add coordinate axes
    origin = (0, 0, 0)
    axis_length = 3
    draw_line_3d(origin, (axis_length, 0, 0), (255, 100, 100), 2)  # X axis (red)
    draw_line_3d(origin, (0, axis_length, 0), (100, 255, 100), 2)  # Y axis (green)
    draw_line_3d(origin, (0, 0, axis_length), (100, 100, 255), 2)  # Z axis (blue)
    
    # Save image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"✅ {output_path}")
    
    # Also create thumbnail
    thumb = img.copy()
    thumb.thumbnail((200, 150))
    thumb_path = output_path.replace('.png', '_thumb.png')
    thumb.save(thumb_path)
    print(f"✅ {thumb_path}")
    
    return img

def create_wireframe_building(width=600, height=400, output_path="outputs/wireframe_building.png"):
    """Create a detailed wireframe building drawing"""
    
    img = Image.new('RGB', (width, height), color=(10, 10, 15))
    draw = ImageDraw.Draw(img)
    
    # Building parameters
    num_floors = 12
    floor_height = 20
    building_width = 200
    building_depth = 150
    
    # Perspective
    vanishing_point_x = width / 2
    vanishing_point_y = height / 3
    
    def project_2p(x, y, z):
        """Two-point perspective projection"""
        scale = 1 / (1 + z / 500)
        px = vanishing_point_x + x * scale
        py = vanishing_point_y + y * scale
        return (px, py)
    
    # Draw main building structure
    base_y = height - 50
    
    # Front face vertical lines
    for i in range(num_floors + 1):
        y = base_y - i * floor_height
        # Left edge
        x1 = vanishing_point_x - building_width / 2
        x2 = vanishing_point_x - building_width / 4
        draw.line([(x1, base_y), (x2, y)], fill=(100, 150, 200), width=1)
        # Right edge
        x1 = vanishing_point_x + building_width / 2
        x2 = vanishing_point_x + building_width / 4
        draw.line([(x1, base_y), (x2, y)], fill=(100, 150, 200), width=1)
    
    # Horizontal lines (floors)
    for i in range(num_floors + 1):
        y = base_y - i * floor_height
        x_left = vanishing_point_x - building_width / 2 + i * 10
        x_right = vanishing_point_x + building_width / 2 - i * 10
        draw.line([(x_left, y), (x_right, y)], fill=(80, 130, 180), width=1)
    
    # Windows
    for floor in range(num_floors):
        y_top = base_y - (floor + 1) * floor_height + 3
        y_bottom = base_y - floor * floor_height - 3
        
        for col in range(4):
            x_offset = (col - 1.5) * 40
            x_left = vanishing_point_x + x_offset - 15
            x_right = vanishing_point_x + x_offset + 15
            
            # Window frame
            window_color = (150, 200, 255) if np.random.random() > 0.4 else (60, 80, 120)
            draw.rectangle([x_left, y_top, x_right, y_bottom], outline=window_color, width=1)
            
            # Window cross
            draw.line([(x_left + (x_right-x_left)/2, y_top), 
                       (x_left + (x_right-x_left)/2, y_bottom)], 
                      fill=window_color, width=1)
            draw.line([(x_left, y_top + (y_bottom-y_top)/2), 
                       (x_right, y_top + (y_bottom-y_top)/2)], 
                      fill=window_color, width=1)
    
    # Roof structure
    roof_y = base_y - num_floors * floor_height
    draw.line([(vanishing_point_x - 60, roof_y), 
               (vanishing_point_x + 60, roof_y)], fill=(120, 170, 220), width=2)
    draw.line([(vanishing_point_x - 60, roof_y), 
               (vanishing_point_x - 50, roof_y - 30)], fill=(120, 170, 220), width=2)
    draw.line([(vanishing_point_x + 60, roof_y), 
               (vanishing_point_x + 50, roof_y - 30)], fill=(120, 170, 220), width=2)
    draw.line([(vanishing_point_x - 50, roof_y - 30), 
               (vanishing_point_x + 50, roof_y - 30)], fill=(120, 170, 220), width=2)
    
    # Add title
    draw.text((20, 20), "Wireframe Building", fill=(120, 160, 200))
    draw.text((20, 40), f"Floors: {num_floors}", fill=(80, 120, 160))
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"✅ {output_path}")
    
    return img

def create_floor_plan(width=700, height=500, output_path="outputs/floor_plan.png"):
    """Create an architectural floor plan drawing"""
    
    img = Image.new('RGB', (width, height), color=(245, 240, 235))
    draw = ImageDraw.Draw(img)
    
    # Grid
    grid_spacing = 50
    for x in range(0, width, grid_spacing):
        draw.line([(x, 80), (x, height)], fill=(200, 200, 200), width=1)
    for y in range(80, height, grid_spacing):
        draw.line([(50, y), (width - 50, y)], fill=(200, 200, 200), width=1)
    
    # Outer walls
    margin = 80
    outer_rect = [margin, margin, width - margin, height - margin]
    draw.rectangle(outer_rect, outline=(50, 50, 50), width=4)
    
    # Internal walls
    wall_color = (80, 80, 80)
    
    # Vertical walls
    draw.line([(width/2, margin), (width/2, height - margin)], fill=wall_color, width=3)
    draw.line([(width/3, margin + 100), (width/3, height/2)], fill=wall_color, width=3)
    draw.line([(2*width/3, height/2), (2*width/3, height - margin)], fill=wall_color, width=3)
    
    # Horizontal walls
    draw.line([(margin, height/2), (width/2 - 30, height/2)], fill=wall_color, width=3)
    draw.line([(width/2 + 30, height/3), (width - margin, height/3)], fill=wall_color, width=3)
    
    # Doors (gaps in walls with arc)
    door_positions = [
        (width/2, height/2 + 50),
        (width/3, height/2 - 30),
        (width/2 + 80, height/3),
    ]
    
    for dx, dy in door_positions:
        # Door arc
        draw.arc([dx - 20, dy - 20, dx + 20, dy + 20], 0, 90, fill=(150, 100, 50), width=2)
        draw.line([(dx, dy), (dx, dy + 20)], fill=(150, 100, 50), width=2)
    
    # Windows
    window_color = (100, 150, 200)
    window_positions = [
        (margin + 60, margin),
        (margin + 140, margin),
        (width - margin - 60, margin),
        (width - margin - 140, margin),
        (margin, margin + 100),
        (margin, height - margin - 100),
        (width - margin, margin + 150),
        (width - margin, height - margin - 50),
    ]
    
    for wx, wy in window_positions:
        draw.rectangle([wx - 15, wy - 3, wx + 15, wy + 3], fill=window_color, outline=(70, 100, 130))
    
    # Room labels
    room_labels = [
        (width/4, height/4, "Living Room"),
        (3*width/4, height/4, "Bedroom"),
        (width/4, 3*height/4, "Kitchen"),
        (3*width/4, 3*height/4, "Bathroom"),
    ]
    
    for rx, ry, label in room_labels:
        draw.text((rx - 40, ry), label, fill=(60, 60, 60))
    
    # Dimension lines
    dim_color = (120, 120, 120)
    # Top dimension
    draw.line([(margin, margin - 20), (width - margin, margin - 20)], fill=dim_color, width=1)
    draw.line([(margin, margin - 25), (margin, margin - 15)], fill=dim_color, width=1)
    draw.line([(width - margin, margin - 25), (width - margin, margin - 15)], fill=dim_color, width=1)
    draw.text((width/2 - 20, margin - 40), f"{width - 2*margin}mm", fill=dim_color)
    
    # Left dimension
    draw.line([(margin - 20, margin), (margin - 20, height - margin)], fill=dim_color, width=1)
    draw.line([(margin - 25, margin), (margin - 15, margin)], fill=dim_color, width=1)
    draw.line([(margin - 25, height - margin), (margin - 15, height - margin)], fill=dim_color, width=1)
    draw.text((margin - 70, height/2 - 20), f"{height - 2*margin}mm", fill=dim_color)
    
    # Title block
    draw.rectangle([width - 200, height - 60, width - 20, height - 20], outline=(50, 50, 50), width=2)
    draw.text((width - 180, height - 50), "Floor Plan", fill=(50, 50, 50))
    draw.text((width - 180, height - 35), "Scale: 1:100", fill=(80, 80, 80))
    
    # Main title
    draw.text((50, 20), "Architectural Floor Plan", fill=(40, 40, 40))
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"✅ {output_path}")
    
    return img

def create_isometric_structure(width=800, height=600, output_path="outputs/isometric_structure.png"):
    """Create an isometric structural drawing"""
    
    img = Image.new('RGB', (width, height), color=(20, 25, 30))
    draw = ImageDraw.Draw(img)
    
    # Isometric angles
    iso_angle = math.radians(30)
    
    def iso_project(x, y, z):
        """Convert 3D coordinates to isometric 2D"""
        # Rotate around Y axis
        xr = x * math.cos(iso_angle) - z * math.sin(iso_angle)
        zr = x * math.sin(iso_angle) + z * math.cos(iso_angle)
        
        # Project to 2D
        px = width / 2 + xr
        py = height / 2 - y + zr * 0.5
        return (px, py)
    
    # Structure parameters
    num_levels = 6
    level_height = 40
    base_size = 200
    
    # Colors
    structure_color = (100, 180, 220)
    beam_color = (180, 140, 100)
    joint_color = (220, 220, 220)
    
    # Draw each level
    for level in range(num_levels):
        y = level * level_height
        size = base_size * (1 - level / num_levels * 0.5)
        
        # Corner positions
        corners = [
            (-size/2, y, -size/2),
            (size/2, y, -size/2),
            (size/2, y, size/2),
            (-size/2, y, size/2),
        ]
        
        # Draw floor beams
        for i in range(4):
            p1 = iso_project(*corners[i])
            p2 = iso_project(*corners[(i+1) % 4])
            draw.line([p1, p2], fill=beam_color, width=3)
        
        # Draw vertical columns (except top level)
        if level < num_levels - 1:
            for corner in corners:
                p1 = iso_project(*corner)
                p2 = iso_project(corner[0], corner[1] + level_height, corner[2])
                draw.line([p1, p2], fill=structure_color, width=4)
        
        # Draw joints
        for corner in corners:
            px, py = iso_project(*corner)
            draw.ellipse([px-4, py-4, px+4, py+4], fill=joint_color)
        
        # Add diagonal bracing on alternating levels
        if level % 2 == 0 and level > 0:
            p1 = iso_project(-size/2, y, -size/2)
            p2 = iso_project(size/2, y, size/2)
            draw.line([p1, p2], fill=(150, 150, 150), width=1)
            
            p3 = iso_project(size/2, y, -size/2)
            p4 = iso_project(-size/2, y, size/2)
            draw.line([p3, p4], fill=(150, 150, 150), width=1)
    
    # Add foundation
    foundation_y = num_levels * level_height
    foundation_size = base_size * 1.2
    foundation_corners = [
        (-foundation_size/2, foundation_y, -foundation_size/2),
        (foundation_size/2, foundation_y, -foundation_size/2),
        (foundation_size/2, foundation_y, foundation_size/2),
        (-foundation_size/2, foundation_y, foundation_size/2),
    ]
    
    for i in range(4):
        p1 = iso_project(*foundation_corners[i])
        p2 = iso_project(*foundation_corners[(i+1) % 4])
        draw.line([p1, p2], fill=(120, 100, 80), width=5)
    
    # Title
    draw.text((30, 30), "Isometric Structure", fill=(150, 200, 220))
    draw.text((30, 55), f"Levels: {num_levels}", fill=(100, 150, 180))
    
    # Legend
    legend_y = height - 100
    draw.line([(30, legend_y), (60, legend_y)], fill=structure_color, width=4)
    draw.text((70, legend_y - 8), "Column", fill=(180, 180, 180))
    
    draw.line([(30, legend_y + 25), (60, legend_y + 25)], fill=beam_color, width=3)
    draw.text((70, legend_y + 17), "Beam", fill=(180, 180, 180))
    
    draw.ellipse([35, legend_y + 45, 45, legend_y + 55], fill=joint_color)
    draw.text((70, legend_y + 42), "Joint", fill=(180, 180, 180))
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"✅ {output_path}")
    
    return img

if __name__ == "__main__":
    print("🏗️  3D Architecture Mesh Drawing Generator")
    print("=" * 45)
    print()
    
    # Generate all drawings
    create_3d_mesh_drawing()
    create_wireframe_building()
    create_floor_plan()
    create_isometric_structure()
    
    print()
    print("📐 Architecture mesh drawings generated!")
    print()
    print("📊 Output files:")
    print("   1. outputs/architecture_mesh.png - 3D city mesh")
    print("   2. outputs/wireframe_building.png - Wireframe building")
    print("   3. outputs/floor_plan.png - Floor plan")
    print("   4. outputs/isometric_structure.png - Isometric structure")