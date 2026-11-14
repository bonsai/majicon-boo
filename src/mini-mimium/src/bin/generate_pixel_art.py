"""
Generate pixel art / dot-style images for video art
Creates retro-style visuals perfect for lofi/RPG/game music videos
"""

from PIL import Image, ImageDraw, ImageFilter
import math
import random
import os

# Create output directory
os.makedirs("pixel_art", exist_ok=True)

def create_gradient_background(width, height, colors):
    """Create a gradient background"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        ratio = y / height
        r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
        g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
        b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return img

def create_sunset_scene(width, height):
    """Create a pixel art sunset scene"""
    img = create_gradient_background(width, height, 
        [(255, 150, 100), (100, 50, 150)])
    draw = ImageDraw.Draw(img)
    
    # Sun
    sun_x, sun_y = width // 2, height // 2
    sun_radius = 40
    draw.ellipse([sun_x - sun_radius, sun_y - sun_radius,
                  sun_x + sun_radius, sun_y + sun_radius],
                 fill=(255, 200, 50))
    
    # Mountains
    mountain_color = (50, 30, 80)
    points = [
        (0, height),
        (width * 0.2, height * 0.4),
        (width * 0.4, height * 0.7),
        (width * 0.6, height * 0.35),
        (width * 0.8, height * 0.6),
        (width, height * 0.45),
        (width, height)
    ]
    draw.polygon(points, fill=mountain_color)
    
    # Stars
    random.seed(42)
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height // 2)
        size = random.randint(1, 3)
        draw.rectangle([x, y, x + size, y + size], fill=(255, 255, 200))
    
    return img

def create_rpg_landscape(width, height):
    """Create an RPG-style landscape"""
    img = create_gradient_background(width, height,
        [(135, 206, 235), (100, 180, 135)])
    draw = ImageDraw.Draw(img)
    
    # Ground
    draw.rectangle([0, height * 0.6, width, height], fill=(80, 160, 80))
    
    # Hills
    hill_points = [
        (0, height * 0.6),
        (width * 0.15, height * 0.45),
        (width * 0.3, height * 0.55),
        (width * 0.45, height * 0.4),
        (width * 0.6, height * 0.5),
        (width * 0.75, height * 0.35),
        (width, height * 0.45),
        (width, height * 0.6),
    ]
    draw.polygon(hill_points, fill=(60, 140, 60))
    
    # Trees (pixel style)
    tree_positions = [width * 0.2, width * 0.5, width * 0.75, width * 0.9]
    for tx in tree_positions:
        ty = height * 0.55 + random.randint(-20, 20)
        # Trunk
        draw.rectangle([tx - 5, ty, tx + 5, ty + 30], fill=(101, 67, 33))
        # Leaves (triangle-ish)
        draw.polygon([
            (tx, ty - 40),
            (tx - 25, ty + 10),
            (tx + 25, ty + 10)
        ], fill=(34, 139, 34))
        draw.polygon([
            (tx, ty - 55),
            (tx - 20, ty - 5),
            (tx + 20, ty - 5)
        ], fill=(34, 139, 34))
    
    # Clouds
    cloud_positions = [(width * 0.2, height * 0.15),
                       (width * 0.5, height * 0.1),
                       (width * 0.75, height * 0.2)]
    for cx, cy in cloud_positions:
        draw.ellipse([cx - 30, cy - 15, cx + 30, cy + 15], fill=(255, 255, 255))
        draw.ellipse([cx - 20, cy - 25, cx + 20, cy - 5], fill=(255, 255, 255))
        draw.ellipse([cx + 10, cy - 15, cx + 50, cy + 15], fill=(255, 255, 255))
    
    return img

def create_lofi_room(width, height):
    """Create a lofi bedroom scene"""
    img = Image.new('RGB', (width, height), (60, 50, 70))
    draw = ImageDraw.Draw(img)
    
    # Wall
    draw.rectangle([0, 0, width, height * 0.7], fill=(80, 70, 90))
    
    # Floor
    draw.rectangle([0, height * 0.7, width, height], fill=(70, 50, 40))
    
    # Window with night sky
    draw.rectangle([width * 0.6, height * 0.1, width * 0.9, height * 0.5],
                   fill=(20, 15, 40))
    # Window frame
    draw.line([(width * 0.75, height * 0.1), (width * 0.75, height * 0.5)],
              fill=(100, 80, 60), width=3)
    draw.line([(width * 0.6, height * 0.3), (width * 0.9, height * 0.3)],
              fill=(100, 80, 60), width=3)
    
    # Stars in window
    random.seed(123)
    for _ in range(20):
        x = int(width * 0.62 + random.random() * width * 0.25)
        y = int(height * 0.12 + random.random() * height * 0.35)
        draw.point((x, y), fill=(255, 255, 200))
    
    # Moon
    draw.ellipse([width * 0.8, height * 0.15, width * 0.87, height * 0.22],
                 fill=(255, 250, 200))
    
    # Desk
    draw.rectangle([width * 0.1, height * 0.55, width * 0.45, height * 0.75],
                   fill=(101, 67, 33))
    
    # Computer/monitor
    draw.rectangle([width * 0.2, height * 0.45, width * 0.35, height * 0.55],
                   fill=(40, 40, 50))
    # Screen glow
    draw.rectangle([width * 0.21, height * 0.46, width * 0.34, height * 0.54],
                   fill=(100, 150, 200))
    
    # Plant
    draw.rectangle([width * 0.38, height * 0.5, width * 0.42, height * 0.55],
                   fill=(139, 90, 43))
    draw.ellipse([width * 0.36, height * 0.42, width * 0.44, height * 0.51],
                 fill=(34, 139, 34))
    
    # Chair
    draw.rectangle([width * 0.15, height * 0.65, width * 0.25, height * 0.75],
                   fill=(50, 50, 60))
    
    # Lamp (hanging)
    draw.line([(width * 0.5, height * 0.2), (width * 0.5, height * 0.35)],
              fill=(80, 80, 80), width=2)
    draw.ellipse([width * 0.45, height * 0.35, width * 0.55, height * 0.42],
                 fill=(255, 220, 150))
    
    # Bookshelf
    draw.rectangle([width * 0.02, height * 0.3, width * 0.12, height * 0.65],
                   fill=(101, 67, 33))
    # Books (colored rectangles)
    book_colors = [(200, 100, 100), (100, 150, 100), (100, 100, 200),
                   (200, 200, 100), (150, 100, 200)]
    for i, color in enumerate(book_colors):
        draw.rectangle([width * 0.03 + i * 0.015 * width, height * 0.35,
                       width * 0.045 + i * 0.015 * width, height * 0.42],
                      fill=color)
    
    return img

def create_abstract_dots(width, height, style="flow"):
    """Create abstract dot patterns for visualizers"""
    img = Image.new('RGB', (width, height), (10, 10, 30))
    draw = ImageDraw.Draw(img)
    
    if style == "flow":
        # Flowing dot patterns
        for i in range(200):
            x = random.randint(0, width)
            base_y = random.randint(0, height)
            
            # Create wave pattern
            points = []
            for j in range(20):
                px = x + j * 10
                py = base_y + math.sin(j * 0.3) * 30 + math.cos(j * 0.5) * 20
                if 0 <= px <= width and 0 <= py <= height:
                    points.append((px, py))
            
            # Draw dots along the path
            for px, py in points:
                size = random.randint(2, 5)
                hue = (i * 5 + j * 10) % 360
                r = int(128 + 127 * math.sin(hue * math.pi / 180))
                g = int(128 + 127 * math.sin((hue + 120) * math.pi / 180))
                b = int(128 + 127 * math.sin((hue + 240) * math.pi / 180))
                draw.ellipse([px - size//2, py - size//2,
                             px + size//2, py + size//2],
                            fill=(r, g, b))
    
    elif style == "circles":
        # Concentric circles of dots
        center_x, center_y = width // 2, height // 2
        for radius in range(20, min(width, height) // 2, 15):
            num_dots = radius
            for i in range(num_dots):
                angle = (2 * math.pi * i) / num_dots
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                size = 4
                hue = (radius * 2 + i * 10) % 360
                r = int(128 + 127 * math.sin(hue * math.pi / 180))
                g = int(128 + 127 * math.sin((hue + 120) * math.pi / 180))
                b = int(128 + 127 * math.sin((hue + 240) * math.pi / 180))
                draw.ellipse([x - size//2, y - size//2,
                             x + size//2, y + size//2],
                            fill=(r, g, b))
    
    elif style == "rain":
        # Matrix-style rain
        columns = width // 15
        for col in range(columns):
            x = col * 15 + 7
            y_start = random.randint(-200, 0)
            length = random.randint(20, 100)
            
            for i in range(length):
                y = y_start + i * 3
                if 0 <= y <= height:
                    brightness = 255 - i * 2
                    g_val = max(0, brightness)
                    draw.rectangle([x - 2, y, x + 2, y + 2],
                                  fill=(0, g_val, 50))
    
    return img

def create_equalizer_bars(width, height, num_bars=16):
    """Create animated equalizer bar visualization"""
    img = Image.new('RGB', (width, height), (20, 20, 40))
    draw = ImageDraw.Draw(img)
    
    bar_width = (width - (num_bars + 1) * 10) // num_bars
    
    random.seed(42)
    for i in range(num_bars):
        x = 10 + i * (bar_width + 10)
        bar_height = int(height * 0.3 * random.random()) + 20
        
        # Gradient color based on position
        hue = i * (360 / num_bars)
        r = int(128 + 127 * math.sin(hue * math.pi / 180))
        g = int(128 + 127 * math.sin((hue + 120) * math.pi / 180))
        b = int(128 + 127 * math.sin((hue + 240) * math.pi / 180))
        
        # Draw bar from bottom
        y = height - bar_height
        draw.rectangle([x, y, x + bar_width, height - 10],
                      fill=(r, g, b))
        
        # Add glow effect
        draw.rectangle([x, y - 5, x + bar_width, y],
                      fill=(min(255, r + 50), min(255, g + 50), min(255, b + 50)))
    
    return img

def create_pixel_heart(width, height):
    """Create a pixel art heart"""
    img = Image.new('RGB', (width, height), (20, 10, 30))
    draw = ImageDraw.Draw(img)
    
    # Heart shape using circles and polygons
    center_x, center_y = width // 2, height // 2
    
    # Main heart body (two circles for top)
    left_bump = [(center_x - 40, center_y - 20), (center_x - 10, center_y + 30)]
    right_bump = [(center_x + 10, center_y - 20), (center_x + 40, center_y + 30)]
    
    draw.ellipse([center_x - 50, center_y - 50, center_x - 10, center_y - 10],
                 fill=(255, 50, 80))
    draw.ellipse([center_x + 10, center_y - 50, center_x + 50, center_y - 10],
                 fill=(255, 50, 80))
    
    # Bottom triangle
    draw.polygon([
        (center_x - 50, center_y - 20),
        (center_x, center_y + 50),
        (center_x + 50, center_y - 20)
    ], fill=(255, 50, 80))
    
    # Highlight
    draw.ellipse([center_x - 35, center_y - 40, center_x - 20, center_y - 25],
                 fill=(255, 150, 160))
    
    # Sparkles around
    sparkle_positions = [
        (center_x - 70, center_y - 60),
        (center_x + 70, center_y - 60),
        (center_x, center_y - 80),
        (center_x - 60, center_y + 40),
        (center_x + 60, center_y + 40),
    ]
    for sx, sy in sparkle_positions:
        draw.line([(sx - 5, sy), (sx + 5, sy)], fill=(255, 255, 200), width=2)
        draw.line([(sx, sy - 5), (sx, sy + 5)], fill=(255, 255, 200), width=2)
    
    return img

def create_chromatic_dots(width, height):
    """Create chromatic aberration style dots"""
    img = Image.new('RGB', (width, height), (5, 5, 10))
    draw = ImageDraw.Draw(img)
    
    random.seed(999)
    for _ in range(300):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(3, 8)
        
        # Draw RGB separated dots
        offset = random.randint(1, 4)
        # Red channel
        draw.ellipse([x - offset - size//2, y - size//2,
                     x - offset + size//2, y + size//2],
                    fill=(255, 0, 0))
        # Green channel
        draw.ellipse([x - size//2, y - size//2,
                     x + size//2, y + size//2],
                    fill=(0, 255, 0))
        # Blue channel
        draw.ellipse([x + offset - size//2, y - size//2,
                     x + offset + size//2, y + size//2],
                    fill=(0, 0, 255))
    
    return img

def create_vaporwave_grid(width, height):
    """Create vaporwave-style perspective grid"""
    img = create_gradient_background(width, height,
        [(255, 100, 150), (100, 50, 150)])
    draw = ImageDraw.Draw(img)
    
    # Sun
    sun_y = height // 3
    for i in range(20):
        y = sun_y + i * 3
        alpha = 255 - i * 12
        draw.line([(width * 0.3, y), (width * 0.7, y)],
                  fill=(255, 200, 100, alpha))
    
    # Perspective grid (floor)
    horizon = height // 2
    
    # Vertical lines converging to center
    center_x = width // 2
    for i in range(-20, 21):
        x_offset = i * 40
        draw.line([(center_x + x_offset, horizon),
                  (center_x + x_offset * 3, height)],
                 fill=(255, 0, 255), width=2)
    
    # Horizontal lines
    for i in range(10):
        y = horizon + int((i / 10) ** 2 * (height - horizon))
        draw.line([(0, y), (width, y)], fill=(0, 255, 255), width=1)
    
    return img

def main():
    """Generate all pixel art images"""
    print("🎨 Generating pixel art images for video...")
    
    images = {
        "sunset_scene.png": create_sunset_scene(800, 600),
        "rpg_landscape.png": create_rpg_landscape(800, 600),
        "lofi_room.png": create_lofi_room(800, 600),
        "abstract_dots_flow.png": create_abstract_dots(800, 600, "flow"),
        "abstract_dots_circles.png": create_abstract_dots(800, 600, "circles"),
        "abstract_dots_rain.png": create_abstract_dots(800, 600, "rain"),
        "equalizer_bars.png": create_equalizer_bars(800, 600),
        "pixel_heart.png": create_pixel_heart(800, 600),
        "chromatic_dots.png": create_chromatic_dots(800, 600),
        "vaporwave_grid.png": create_vaporwave_grid(800, 600),
    }
    
    # Also create smaller thumbnail versions
    for name, img in images.items():
        # Save full size
        img.save(f"pixel_art/{name}")
        
        # Create thumbnail
        thumb = img.copy()
        thumb.thumbnail((400, 300))
        thumb.save(f"pixel_art/thumb_{name}")
        
        print(f"  ✓ Created {name}")
    
    # Create animated frames for equalizer
    print("\n🎬 Creating animated equalizer frames...")
    for frame in range(30):
        random.seed(frame * 100)
        img = create_equalizer_bars(800, 600)
        img.save(f"pixel_art/equalizer_frame_{frame:03d}.png")
    
    print(f"\n✅ Generated {len(images) + 30} images in pixel_art/ folder")
    print("\n📊 Image types:")
    print("   - Sunset scene (lofi aesthetic)")
    print("   - RPG landscape (field music)")
    print("   - Lofi bedroom room")
    print("   - Abstract dot patterns (flow, circles, rain)")
    print("   - Equalizer bars (animated frames)")
    print("   - Pixel heart")
    print("   - Chromatic dots")
    print("   - Vaporwave grid")

if __name__ == "__main__":
    main()