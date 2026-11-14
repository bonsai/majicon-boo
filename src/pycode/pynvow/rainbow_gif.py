import pyvista as pv
import numpy as np
import imageio
import os

# Create directory for output if it doesn't exist
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
output_filename = os.path.join(output_dir, "soap_bubble.gif")

print("Generating soap bubble geometry...")

# Use a high resolution sphere for smooth look
resolution = 200
sphere = pv.Sphere(radius=2.0, phi_resolution=resolution, theta_resolution=resolution)

# Base points to calculate deformation from
base_points = sphere.points.copy()
# Normals for deformation (pointing outwards)
normals = base_points / np.linalg.norm(base_points, axis=1)[:, None]

# Initialize scalars with dummy data so add_mesh doesn't complain
sphere["scalars"] = np.zeros(sphere.n_points)

print("Setting up plotter...")
plotter = pv.Plotter(off_screen=True)

# Initial mesh add
# We will update the mesh in the loop
plotter.add_mesh(
    sphere, 
    scalars="scalars", 
    cmap="gist_ncar",  # A colorful map often used for interferometry/fluids
    show_edges=False, 
    smooth_shading=True, 
    show_scalar_bar=False,
    specular=0.5,      # Add shininess
    specular_power=15
)

plotter.set_background("black")
plotter.view_isometric()

# Animation settings
n_frames = 60
images = []

print("Rendering frames...")
plotter.show(auto_close=False)

for i in range(n_frames):
    # Time parameter t goes from 0 to 2*pi for seamless loop
    t = i / n_frames * 2 * np.pi
    
    # Generate fluid-like pattern using wave synthesis
    # We mix coordinates and time to create moving swirls
    x = base_points[:, 0]
    y = base_points[:, 1]
    z = base_points[:, 2]
    
    # Wave synthesis for pattern (scalars) and deformation
    # Using sin/cos with different frequencies and phase shifts based on t
    
    # Low frequency movement
    w1 = np.sin(2 * x + t) * np.cos(2 * y + np.cos(t))
    # Medium frequency
    w2 = np.sin(5 * z - t) * np.cos(5 * x + np.sin(t))
    # High frequency ripples
    w3 = np.sin(10 * (x + y) + 2*t) * 0.2
    
    # Combine waves
    noise = w1 + w2 + w3
    
    # Update scalars for color
    # Add a swirling gradient effect
    sphere["scalars"] = noise
    
    # Deform the sphere slightly based on the noise to make it look wobbly/liquid
    # Amplitude of deformation
    amp = 0.15
    sphere.points = base_points + normals * noise[:, None] * amp
    
    # Rotate camera slightly for dynamic view
    plotter.camera.azimuth += 360 / n_frames
    
    # Render
    img = plotter.screenshot(return_img=True)
    images.append(img)
    
    if (i + 1) % 10 == 0:
        print(f"  Frame {i + 1}/{n_frames}")

plotter.close()

print(f"Saving GIF to {output_filename}...")
imageio.mimsave(output_filename, images, fps=20, loop=0)

print("Done!")
