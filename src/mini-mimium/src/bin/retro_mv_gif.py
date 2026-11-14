#!/usr/bin/env python3
"""
Retro 80s/90s CG Music Video Style GIF Generator
Inspired by "Ugokugo Ruga" era - wireframe, chrome, neon, geometric transforms
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import math
import os

def create_retro_grid_gif(width=512, height=512, frames=48, output_path="outputs/png/retro_grid_mv.gif"):
    """Create a retro synthwave grid music video GIF"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    frames_list = []
    
    for frame in range(frames):
        # Deep purple/pink gradient background
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Gradient background
        for y in range(height):
            t = y / height
            r = int(20 + 40 * t)
            g = int(10 + 20 * t)
            b = int(40 + 60 * t)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Sun on horizon
        sun_y = height // 2 - 20
        sun_radius = 80
        
        # Sun gradient (pink to orange)
        for r in range(sun_radius, 0, -2):
            t = r / sun_radius
            color = (int(255), int(200 - 50 * t), int(100 + 100 * t))
            draw.ellipse([width//2 - r, sun_y - r, width//2 + r, sun_y + r], fill=color)
        
        # Sun stripes (retro style)
        for i in range(8):
            stripe_y = sun_y + i * 6 - 20
            if stripe_y > sun_y - 30:
                draw.rectangle([width//2 - sun_radius, stripe_y, width//2 + sun_radius, stripe_y + 3], fill=(40, 10, 50))
        
        # Moving grid (perspective floor)
        grid_offset = (frame * 5) % 40
        horizon_y = height // 2
        
        # Vertical grid lines (perspective)
        vanishing_x = width // 2
        vanishing_y = horizon_y
        
        for i in range(-20, 21):
            x_offset = i * 30
            # Lines fan out from vanishing point
            top_x = vanishing_x + x_offset // 10
            bottom_x = vanishing_x + x_offset * 3
            
            # Neon purple grid lines
            draw.line([(top_x, vanishing_y), (bottom_x, height)], fill=(255, 100, 255), width=2)
        
        # Horizontal grid lines (moving)
        for i in range(20):
            y = horizon_y + (i * i + grid_offset) % (height - horizon_y)
            if y > horizon_y:
                alpha = min(255, int(100 + 155 * (y - horizon_y) / (height - horizon_y)))
                draw.line([(0, y), (width, y)], fill=(alpha, 50, alpha), width=1)
        
        # Horizon glow line
        draw.line([(0, horizon_y), (width, horizon_y)], fill=(255, 200, 255), width=3)
        
        # Floating chrome wireframe shapes
        angle = frame * 0.1
        for shape_i in range(3):
            shape_angle = angle + shape_i * (2 * math.pi / 3)
            cx = width // 2 + int(150 * math.cos(shape_angle))
            cy = horizon_y - 50 + int(50 * math.sin(shape_angle * 2))
            
            # Rotating wireframe cube
            cube_size = 30
            rot = frame * 0.15 + shape_i
            
            points = []
            for corner in [(1,1,1), (-1,1,1), (-1,-1,1), (1,-1,1), (1,1,-1), (-1,1,-1), (-1,-1,-1), (1,-1,-1)]:
                x, y, z = corner
                # Rotate
                rx = x * math.cos(rot) - z * math.sin(rot)
                rz = x * math.sin(rot) + z * math.cos(rot)
                ry = y * math.cos(rot * 0.5) - z * math.sin(rot * 0.5)
                points.append((cx + rx * cube_size, cy - ry * cube_size + rz * cube_size * 0.3))
            
            # Draw wireframe edges (chrome/cyan)
            edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
            for e in edges:
                draw.line([points[e[0]], points[e[1]]], fill=(100, 255, 255), width=1)
        
        # Title text (retro font style)
        draw.text((20, 20), "RETRO GRID", fill=(255, 100, 255))
        draw.text((20, 40), f"FRAME {frame:03d}", fill=(100, 255, 255))
        
        frames_list.append(img)
        print(f"  Grid frame {frame+1}/{frames}")
    
    frames_list[0].save(output_path, save_all=True, append_images=frames_list[1:], duration=80, loop=0, optimize=True)
    print(f"✅ {output_path}")


def create_wireframe_sphere_gif(width=512, height=512, frames=36, output_path="outputs/png/wireframe_sphere_mv.gif"):
    """Create a rotating wireframe sphere - classic 80s CG"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    frames_list = []
    bg = (5, 5, 15)
    
    for frame in range(frames):
        img = Image.new('RGB', (width, height), color=bg)
        draw = ImageDraw.Draw(img)
        
        # Sphere parameters
        sphere_radius = 150
        cx, cy = width // 2, height // 2
        
        # Rotation angles
        rot_x = frame * 0.15
        rot_y = frame * 0.1
        
        # Latitude/longitude lines
        num_lat = 12
        num_lon = 16
        
        # Collect all points
        points = []
        for lat in range(num_lat + 1):
            lat_angle = math.pi * lat / num_lat - math.pi / 2
            row = []
            for lon in range(num_lon + 1):
                lon_angle = 2 * math.pi * lon / num_lon
                
                # 3D point on sphere
                x = sphere_radius * math.cos(lat_angle) * math.cos(lon_angle)
                y = sphere_radius * math.sin(lat_angle)
                z = sphere_radius * math.cos(lat_angle) * math.sin(lon_angle)
                
                # Rotate around X axis
                y2 = y * math.cos(rot_x) - z * math.sin(rot_x)
                z2 = y * math.sin(rot_x) + z * math.cos(rot_x)
                
                # Rotate around Y axis
                x2 = x * math.cos(rot_y) + z2 * math.sin(rot_y)
                z3 = -x * math.sin(rot_y) + z2 * math.cos(rot_y)
                
                # Simple perspective
                scale = 200 / (200 + z3)
                px = cx + x2 * scale
                py = cy + y2 * scale
                
                row.append((px, py, z3))
            points.append(row)
        
        # Draw longitude lines
        for lon in range(num_lon + 1):
            for lat in range(num_lat):
                p1 = points[lat][lon]
                p2 = points[lat + 1][lon]
                
                # Color based on depth
                depth = (p1[2] + p2[2]) / 2
                brightness = int(155 + 100 * (depth + sphere_radius) / (2 * sphere_radius))
                color = (brightness, min(255, brightness + 100), 255)
                
                draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=color, width=1)
        
        # Draw latitude lines
        for lat in range(num_lat + 1):
            for lon in range(num_lon):
                p1 = points[lat][lon]
                p2 = points[lat][(lon + 1) % (num_lon + 1)]
                
                depth = (p1[2] + p2[2]) / 2
                brightness = int(155 + 100 * (depth + sphere_radius) / (2 * sphere_radius))
                color = (brightness, min(255, brightness + 100), 255)
                
                draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=color, width=1)
        
        # Inner glow core
        for r in range(40, 0, -5):
            alpha = r / 40
            glow_color = (int(100 * alpha), int(200 * alpha), int(255 * alpha))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=glow_color)
        
        # Orbiting particles
        for i in range(8):
            orbit_angle = frame * 0.2 + i * (2 * math.pi / 8)
            orbit_radius = 220
            px = cx + orbit_radius * math.cos(orbit_angle)
            py = cy + 50 * math.sin(orbit_angle)
            
            draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 255, 200))
        
        draw.text((20, 20), "WIREFRAME SPHERE", fill=(100, 255, 255))
        
        frames_list.append(img)
        print(f"  Sphere frame {frame+1}/{frames}")
    
    frames_list[0].save(output_path, save_all=True, append_images=frames_list[1:], duration=100, loop=0, optimize=True)
    print(f"✅ {output_path}")


def create_chrome_torus_gif(width=512, height=512, frames=40, output_path="outputs/png/chrome_torus_mv.gif"):
    """Create a chrome torus - classic 80s/90s CG"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    frames_list = []
    
    for frame in range(frames):
        img = Image.new('RGB', (width, height), color=(10, 5, 20))
        draw = ImageDraw.Draw(img)
        
        # Torus parameters
        major_radius = 120
        minor_radius = 40
        cx, cy = width // 2, height // 2
        
        # Rotation
        rot_x = frame * 0.12
        rot_y = frame * 0.08
        rot_z = frame * 0.05
        
        num_major = 24
        num_minor = 16
        
        # Generate torus points
        points = []
        for i in range(num_major):
            theta = 2 * math.pi * i / num_major
            row = []
            for j in range(num_minor):
                phi = 2 * math.pi * j / num_minor
                
                # Torus parametric
                x = (major_radius + minor_radius * math.cos(phi)) * math.cos(theta)
                y = (major_radius + minor_radius * math.cos(phi)) * math.sin(theta)
                z = minor_radius * math.sin(phi)
                
                # Rotate X
                y2 = y * math.cos(rot_x) - z * math.sin(rot_x)
                z2 = y * math.sin(rot_x) + z * math.cos(rot_x)
                
                # Rotate Y
                x2 = x * math.cos(rot_y) + z2 * math.sin(rot_y)
                z3 = -x * math.sin(rot_y) + z2 * math.cos(rot_y)
                
                # Rotate Z
                x3 = x2 * math.cos(rot_z) - y2 * math.sin(rot_z)
                y3 = x2 * math.sin(rot_z) + y2 * math.cos(rot_z)
                
                # Project
                scale = 300 / (300 + z3)
                px = cx + x3 * scale
                py = cy - y3 * scale
                
                row.append((px, py, z3))
            points.append(row)
        
        # Draw torus rings (major)
        for i in range(num_major):
            for j in range(num_minor):
                p1 = points[i][j]
                p2 = points[(i + 1) % num_major][j]
                
                # Chrome gradient based on depth and position
                depth = (p1[2] + p2[2]) / 2
                t = (depth + minor_radius * 2) / (minor_radius * 4)
                
                r = int(150 + 105 * t)
                g = int(150 + 105 * (1 - t))
                b = int(200 + 55 * math.sin(t * math.pi))
                
                draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=(r, g, b), width=2)
        
        # Draw torus rings (minor)
        for i in range(num_major):
            for j in range(num_minor):
                p1 = points[i][j]
                p2 = points[i][(j + 1) % num_minor]
                
                depth = (p1[2] + p2[2]) / 2
                t = (depth + minor_radius * 2) / (minor_radius * 4)
                
                r = int(150 + 105 * t)
                g = int(150 + 105 * (1 - t))
                b = int(200 + 55 * math.sin(t * math.pi))
                
                draw.line([(p1[0], p1[1]), (p2[0], p2[1])], fill=(r, g, b), width=2)
        
        # Background stars
        np.random.seed(frame)
        for _ in range(50):
            sx = np.random.randint(0, width)
            sy = np.random.randint(0, height)
            brightness = np.random.randint(100, 255)
            draw.point((sx, sy), fill=(brightness, brightness, brightness))
        
        draw.text((20, 20), "CHROME TORUS", fill=(255, 200, 150))
        
        frames_list.append(img)
        print(f"  Torus frame {frame+1}/{frames}")
    
    frames_list[0].save(output_path, save_all=True, append_images=frames_list[1:], duration=100, loop=0, optimize=True)
    print(f"✅ {output_path}")


def create_neon_tunnel_gif(width=512, height=512, frames=30, output_path="outputs/png/neon_tunnel_mv.gif"):
    """Create a flying through neon tunnel effect"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    frames_list = []
    
    for frame in range(frames):
        img = Image.new('RGB', (width, height), color=(0, 0, 5))
        draw = ImageDraw.Draw(img)
        
        cx, cy = width // 2, height // 2
        
        # Tunnel segments
        num_segments = 20
        tunnel_twist = frame * 0.2
        
        for seg in range(num_segments - 1, -1, -1):
            # Depth-based sizing
            z = seg * 30 + (frame * 10) % 30
            scale = 400 / (z + 100)
            
            # Hexagon tunnel
            hex_size = 150 * scale
            rotation = tunnel_twist + seg * 0.3
            
            points = []
            for i in range(6):
                angle = 2 * math.pi * i / 6 + rotation
                px = cx + hex_size * math.cos(angle)
                py = cy + hex_size * math.sin(angle)
                points.append((px, py))
            
            # Neon color cycling
            hue = (frame * 10 + seg * 20) % 360
            if hue < 60:
                color = (255, hue * 4, 100)
            elif hue < 120:
                color = (255 - (hue - 60) * 4, 255, 100)
            elif hue < 180:
                color = (100, 255, (hue - 120) * 4)
            elif hue < 240:
                color = (100, 255 - (hue - 180) * 4, 255)
            else:
                color = (100 + (hue - 240) * 4, 100, 255)
            
            # Draw hexagon
            for i in range(6):
                draw.line([points[i], points[(i + 1) % 6]], fill=color, width=3)
        
        # Center glow
        for r in range(50, 0, -5):
            alpha = r / 50
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(int(100 * alpha), 0, int(200 * alpha)))
        
        draw.text((20, 20), "NEON TUNNEL", fill=(255, 100, 255))
        
        frames_list.append(img)
        print(f"  Tunnel frame {frame+1}/{frames}")
    
    frames_list[0].save(output_path, save_all=True, append_images=frames_list[1:], duration=120, loop=0, optimize=True)
    print(f"✅ {output_path}")


if __name__ == "__main__":
    print("🎬 Retro 80s/90s CG MV GIF Generator")
    print("=" * 45)
    print()
    
    create_retro_grid_gif()
    create_wireframe_sphere_gif()
    create_chrome_torus_gif()
    create_neon_tunnel_gif()
    
    print()
    print("✨ All retro MV GIFs generated!")
    print()
    print("📊 Output files:")
    print("   1. outputs/png/retro_grid_mv.gif - Synthwave grid")
    print("   2. outputs/png/wireframe_sphere_mv.gif - Classic wireframe sphere")
    print("   3. outputs/png/chrome_torus_mv.gif - Chrome torus")
    print("   4. outputs/png/neon_tunnel_mv.gif - Neon tunnel flythrough")
