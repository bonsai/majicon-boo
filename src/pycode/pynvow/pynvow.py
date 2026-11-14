import pygame
import sys
import os
import threading
from PIL import Image, ImageSequence

class PYNVOW:
    def __init__(self):
        self.running = True
        self.screen_width = 256
        self.screen_height = 192 * 2
        self.gif_frames = []
        self.show_gif = False
        self.current_frame = 0
        self.last_frame_time = 0
        self.frame_delay = 100 # Default delay
        
        # Absolute path to the GIF
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.img_dir = os.path.join(base_dir, "img")
        self.gif_path = os.path.join(self.img_dir, "soap_bubble.gif")
        
        self.generating = False
        self.gen_status = ""

    def load_gif(self):
        if not os.path.exists(self.gif_path):
            print(f"GIF not found at {self.gif_path}")
            return False
            
        try:
            pil_image = Image.open(self.gif_path)
            self.gif_frames = []
            
            # Get duration if available, default to 100ms
            self.frame_delay = pil_image.info.get('duration', 100)
            
            for frame in ImageSequence.Iterator(pil_image):
                frame = frame.convert('RGBA')
                
                # Resize to fit screen (256x192) keeping aspect ratio
                target_height = 192
                aspect_ratio = frame.width / frame.height
                target_width = int(target_height * aspect_ratio)
                
                if target_width > 256:
                    target_width = 256
                    target_height = int(target_width / aspect_ratio)
                
                frame = frame.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                mode = frame.mode
                size = frame.size
                data = frame.tobytes()
                
                pygame_surface = pygame.image.fromstring(data, size, mode)
                self.gif_frames.append(pygame_surface)
            
            print(f"Loaded {len(self.gif_frames)} frames.")
            return True
        except Exception as e:
            print(f"Error loading GIF: {e}")
            return False

    def generate_gif_thread(self):
        self.generating = True
        self.gen_status = "Initializing..."
        try:
            import pyvista as pv
            import numpy as np
            import imageio
            
            self.gen_status = "Generating Geometry..."
            
            if not os.path.exists(self.img_dir):
                os.makedirs(self.img_dir)
            
            # Use a high resolution sphere for smooth look
            resolution = 200
            sphere = pv.Sphere(radius=2.0, phi_resolution=resolution, theta_resolution=resolution)

            # Base points to calculate deformation from
            base_points = sphere.points.copy()
            # Normals for deformation (pointing outwards)
            normals = base_points / np.linalg.norm(base_points, axis=1)[:, None]

            # Initialize scalars with dummy data so add_mesh doesn't complain
            sphere["scalars"] = np.zeros(sphere.n_points)

            self.gen_status = "Setting up Plotter..."
            plotter = pv.Plotter(off_screen=True)

            # Initial mesh add
            plotter.add_mesh(
                sphere, 
                scalars="scalars", 
                cmap="gist_ncar",
                show_edges=False, 
                smooth_shading=True, 
                show_scalar_bar=False,
                specular=0.5,
                specular_power=15
            )

            plotter.set_background("black")
            plotter.view_isometric()

            # Animation settings
            n_frames = 60
            images = []

            self.gen_status = "Rendering Frames..."
            plotter.show(auto_close=False)

            for i in range(n_frames):
                self.gen_status = f"Rendering {i+1}/{n_frames}..."
                
                t = i / n_frames * 2 * np.pi
                
                x = base_points[:, 0]
                y = base_points[:, 1]
                z = base_points[:, 2]
                
                w1 = np.sin(2 * x + t) * np.cos(2 * y + np.cos(t))
                w2 = np.sin(5 * z - t) * np.cos(5 * x + np.sin(t))
                w3 = np.sin(10 * (x + y) + 2*t) * 0.2
                
                noise = w1 + w2 + w3
                sphere["scalars"] = noise
                
                amp = 0.15
                sphere.points = base_points + normals * noise[:, None] * amp
                
                plotter.camera.azimuth += 360 / n_frames
                
                img = plotter.screenshot(return_img=True)
                images.append(img)
            
            plotter.close()

            self.gen_status = "Saving GIF..."
            imageio.mimsave(self.gif_path, images, fps=20, loop=0)
            
            self.gen_status = "Done!"
            
            # Auto reload
            self.load_gif()
            self.show_gif = True
            
        except Exception as e:
            print(f"Error generating GIF: {e}")
            self.gen_status = f"Error: {str(e)[:20]}"
        finally:
            self.generating = False

    def run(self):
        screen = pygame.display.get_surface()
        if screen is None:
            pygame.init()
            screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            
        font = pygame.font.SysFont("Arial", 20)
        small_font = pygame.font.SysFont("Arial", 14)
        clock = pygame.time.Clock()
        
        while self.running:
            screen.fill((0, 50, 0)) # Dark Green background
            
            # Update animation state
            current_frame_surface = None
            if self.show_gif and self.gif_frames:
                current_time = pygame.time.get_ticks()
                if current_time - self.last_frame_time > self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
                    self.last_frame_time = current_time
                current_frame_surface = self.gif_frames[self.current_frame]

            # --- Top Screen (0-191) ---
            if current_frame_surface:
                frame_rect_top = current_frame_surface.get_rect(center=(128, 96))
                screen.blit(current_frame_surface, frame_rect_top)
            else:
                title = font.render("PYNVOW - Python Vow", True, (255, 255, 255))
                screen.blit(title, (20, 50))
                msg = font.render("Coming Soon...", True, (200, 200, 200))
                screen.blit(msg, (20, 80))
            
            # --- Bottom Screen (192-383) ---
            pygame.draw.line(screen, (100, 100, 100), (0, 192), (256, 192), 2)
            
            if current_frame_surface:
                frame_rect_bottom = current_frame_surface.get_rect(center=(128, 192 + 96))
                screen.blit(current_frame_surface, frame_rect_bottom)

            # GIF Play Button
            play_btn = pygame.Rect(28, 192 + 20, 200, 30)
            btn_color = (0, 100, 100) if not self.show_gif else (0, 150, 150)
            pygame.draw.rect(screen, btn_color, play_btn)
            play_text = font.render("Play Bubble GIF", True, (255, 255, 255))
            screen.blit(play_text, (play_btn.x + 35, play_btn.y + 5))
            
            # Generate Button
            gen_btn = pygame.Rect(28, 192 + 60, 200, 30)
            gen_color = (100, 100, 0) if not self.generating else (50, 50, 0)
            pygame.draw.rect(screen, gen_color, gen_btn)
            gen_text = font.render("Generate New GIF", True, (255, 255, 255))
            screen.blit(gen_text, (gen_btn.x + 20, gen_btn.y + 5))
            
            if self.generating:
                status_text = small_font.render(self.gen_status, True, (255, 255, 0))
                screen.blit(status_text, (28, 192 + 95))

            # Back Button
            back_btn = pygame.Rect(28, 192 + 120, 200, 30)
            pygame.draw.rect(screen, (100, 0, 0), back_btn)
            btn_text = font.render("Back to Launcher", True, (255, 255, 255))
            screen.blit(btn_text, (back_btn.x + 20, back_btn.y + 5))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_btn.collidepoint(event.pos):
                        self.running = False
                    elif play_btn.collidepoint(event.pos):
                        if not self.gif_frames:
                            loaded = self.load_gif()
                            if loaded:
                                self.show_gif = True
                        else:
                            self.show_gif = not self.show_gif
                    elif gen_btn.collidepoint(event.pos):
                        if not self.generating:
                            t = threading.Thread(target=self.generate_gif_thread)
                            t.start()
                        
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    app = PYNVOW()
    app.run()
