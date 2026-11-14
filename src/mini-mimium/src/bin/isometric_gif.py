#!/usr/bin/env python3
"""
3D Isometric Structure GIF Generator
Generates rotating isometric structure animations as GIFs
"""

import numpy as np
from PIL import Image, ImageDraw
import math
import os

def create_isometric_gif(width=512, height=512, frames=36, output_path="outputs/png/isometric_structure.gif"):
    """Create a rotating isometric structure GIF"""
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    bg = (15, 20, 30)
    structure_color = (100, 180, 220)
    beam_color = (180, 140, 100)
    joint_color = (220, 220, 220)
    accent_color = (255, 100, 150)
    
    num_levels = 5
    base_size = 120
    level_height = 35
    
    frames_list = []
    
    for frame in range(frames):
        angle = (frame / frames) * 2 * math.pi
        img = Image.new('RGB', (width, height), color=bg)
        draw = ImageDraw.Draw(img)
        
        def iso_project(x, y, z):
            xr = x * math.cos(angle) - z * math.sin(angle)
            zr = x * math.sin(angle) + z * math.cos(angle)
            px = width / 2 + xr * 0.866 - zr * 0.866
            py = height / 2 - y + (xr + zr) * 0.25
            return (px, py)
        
        lines = []
        joints = []
        
        for level in range(num_levels):
            y = level * level_height
            size = base_size * (1 - level / num_levels * 0.4)
            
            corners = [
                (-size/2, y, -size/2),
                (size/2, y, -size/2),
                (size/2, y, size/2),
                (-size/2, y, size/2),
            ]
            
            for i in range(4):
                p1 = corners[i]
                p2 = corners[(i+1) % 4]
                lines.append((p1, p2, beam_color, 4))
            
            if level < num_levels - 1:
                for corner in corners:
                    p1 = corner
                    p2 = (corner[0], corner[1] + level_height, corner[2])
                    lines.append((p1, p2, structure_color, 5))
            
            for corner in corners:
                joints.append(corner)
            
            if level % 2 == 0 and level > 0:
                lines.append((corners[0], corners[2], accent_color, 2))
                lines.append((corners[1], corners[3], accent_color, 2))
        
        for p1, p2, color, w in lines:
            pt1 = iso_project(*p1)
            pt2 = iso_project(*p2)
            draw.line([pt1, pt2], fill=color, width=w)
        
        for joint in joints:
            px, py = iso_project(*joint)
            draw.ellipse([px-5, py-5, px+5, py+5], fill=joint_color)
        
        draw.text((20, 20), "Isometric Structure", fill=(180, 200, 220))
        frames_list.append(img)
        print(f"  Frame {frame+1}/{frames}")
    
    frames_list[0].save(output_path, save_all=True, append_images=frames_list[1:], duration=100, loop=0, optimize=True)
    print(f"✅ {output_path}")

def create_crystal_gif(width=512, height=512, frames=24, output_path="outputs/png/crystal_structure.gif"):
    """Create a rotating crystal structure GIF"""
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    bg = (10, 15, 25)
    frames_list = []
    num_crystals = 7
    crystal_height = 80
    
    for frame in range(frames):
        angle = (frame / frames) * 2 * math.pi
        img = Image.new('RGB', (width, height), color=bg)
        draw = ImageDraw.Draw(img)
        
        def project(x, y, z):
            xr = x * math.cos(angle) - z * math.sin(angle)
            zr = x * math.sin(angle) + z * math.cos(angle)
            px = width / 2 + xr * 0.9
            py = height / 2 + 100 - y - zr * 0.3
            return (px, py)
        
        for i in range(num_crystals):
            theta = (i / num_crystals) * 2 * math.pi
            radius = 80
            cx = radius * math.cos(theta)
            cz = radius * math.sin(theta)
            
            base_y = 0
            top_y = -crystal_height * (0.5 + 0.5 * math.sin(frame * 0.3 + i))
            
            base_points = [(cx + 15, base_y, cz), (cx, base_y, cz - 15), (cx - 15, base_y, cz), (cx, base_y, cz + 15)]
            top_point = (cx, top_y, cz)
            
            crystal_color = (int(100 + 100 * math.sin(frame * 0.2 + i)), int(180 + 50 * math.cos(frame * 0.3 + i)), int(220 + 35 * math.sin(frame * 0.4 + i)))
            
            for j in range(4):
                p1 = base_points[j]
                p2 = base_points[(j+1) % 4]
                p3 = top_point
                pt1, pt2, pt3 = project(*p1), project(*p2), project(*p3)
                draw.polygon([pt1, pt2, pt3], fill=crystal_color, outline=(255, 255, 255))
        
        draw.text((20, 20), "Crystal Structure", fill=(200, 220, 255))
        frames_list.append(img)
        print(f"  Frame {frame+1}/{frames}")
    
    frames_list[0].save(output_path, save_all=True, append_images=frames_list[1:], duration=120, loop=0, optimize=True)
    print(f"✅ {output_path}")

if __name__ == "__main__":
    print("🎨 3D Isometric GIF Generator\n" + "=" * 40)
    create_isometric_gif()
    create_crystal_gif()
    print("\n✨ Done!")
