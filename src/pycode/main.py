import os
import sys
import pygame

# Add veep directory to path to import play_hive
current_dir = os.path.dirname(os.path.abspath(__file__))
veep_dir = os.path.join(current_dir, 'veep')
sys.path.append(veep_dir)

try:
    import play_hive
except ImportError as e:
    print(f"Error importing play_hive: {e}")
    play_hive = None

try:
    import pynvow
except ImportError as e:
    print(f"Error importing pynvow: {e}")
    pynvow = None

# --- Configuration ---
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 192 * 2  # Dual screen
FPS = 60

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (100, 100, 100)
COLOR_BLUE = (0, 120, 215)
COLOR_BLUE_HOVER = (50, 150, 240)

class MainLauncher:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("VDS Launcher")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14)
        
        # Load Logo
        self.logo = None
        logo_path = os.path.join(current_dir, 'vonsai.png')
        if os.path.exists(logo_path):
            try:
                self.logo = pygame.image.load(logo_path)
                # Scale logo to fit top screen if needed
                # Assuming top screen is 256x192
                # Keep aspect ratio
                rect = self.logo.get_rect()
                scale = min(256 / rect.width, 192 / rect.height)
                new_size = (int(rect.width * scale * 0.8), int(rect.height * scale * 0.8))
                self.logo = pygame.transform.scale(self.logo, new_size)
            except Exception as e:
                print(f"Failed to load logo: {e}")
        
        # UI Elements
        self.buttons = []
        self.setup_ui()
        
    def setup_ui(self):
        # Bottom screen starts at 192
        btn_w = 200
        btn_h = 40
        x = (SCREEN_WIDTH - btn_w) // 2
        
        # Calculate Y for two buttons with spacing
        spacing = 20
        total_h = btn_h * 2 + spacing
        start_y = 192 + (192 - total_h) // 2
        
        self.buttons.append({
            'rect': pygame.Rect(x, start_y, btn_w, btn_h),
            'text': "Start VEEP Player",
            'action': 'veep',
            'color': COLOR_BLUE
        })
        
        self.buttons.append({
            'rect': pygame.Rect(x, start_y + btn_h + spacing, btn_w, btn_h),
            'text': "Start PYNVOW",
            'action': 'pynvow',
            'color': (0, 100, 0) # Dark Green
        })

    def run(self):
        running = True
        while running:
            self.screen.fill(COLOR_BLACK)
            
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    action = self.handle_click(event.pos)
                    if action == 'veep':
                        self.launch_veep()
                        self.reset_display()
                    elif action == 'pynvow':
                        self.launch_pynvow()
                        self.reset_display()

            # Draw Top Screen (Logo)
            if self.logo:
                logo_rect = self.logo.get_rect(center=(SCREEN_WIDTH // 2, 192 // 2))
                self.screen.blit(self.logo, logo_rect)
            else:
                text = self.font.render("Vonsai Logo Not Found", True, COLOR_WHITE)
                rect = text.get_rect(center=(SCREEN_WIDTH // 2, 192 // 2))
                self.screen.blit(text, rect)

            # Draw Bottom Screen (Controls)
            # Hinge
            pygame.draw.rect(self.screen, (30, 30, 30), (0, 192, SCREEN_WIDTH, 2))
            
            mx, my = pygame.mouse.get_pos()
            
            for btn in self.buttons:
                color = btn['color']
                if btn['rect'].collidepoint(mx, my):
                    color = COLOR_BLUE_HOVER
                
                pygame.draw.rect(self.screen, color, btn['rect'], border_radius=8)
                pygame.draw.rect(self.screen, COLOR_WHITE, btn['rect'], 2, border_radius=8)
                
                text_surf = self.font.render(btn['text'], True, COLOR_WHITE)
                text_rect = text_surf.get_rect(center=btn['rect'].center)
                self.screen.blit(text_surf, text_rect)

            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

    def handle_click(self, pos):
        for btn in self.buttons:
            if btn['rect'].collidepoint(pos):
                return btn['action']
        return None

    def reset_display(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("VDS Launcher")

    def launch_veep(self):
        if play_hive:
            print("Launching VEEP...")
            # We can run VEEP's run method.
            # Assuming VEEP_NDS class in play_hive.py
            try:
                app = play_hive.VEEP_NDS()
                app.run()
                print("Returned from VEEP")
            except Exception as e:
                print(f"Error running VEEP: {e}")
        else:
            print("VEEP module not loaded")

    def launch_pynvow(self):
        if pynvow:
            print("Launching PYNVOW...")
            try:
                app = pynvow.PYNVOW()
                app.run()
                print("Returned from PYNVOW")
            except Exception as e:
                print(f"Error running PYNVOW: {e}")
        else:
            print("PYNVOW module not loaded")

if __name__ == "__main__":
    launcher = MainLauncher()
    launcher.run()
