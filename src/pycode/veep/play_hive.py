import os
import pygame
import glob
import time
import math

# --- Configuration ---
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 192 * 2  # Dual screen
SCREEN_GAP = 10          # Gap between screens (simulated)
FPS = 60

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (255, 200, 0)
COLOR_GOLD = (218, 165, 32)
COLOR_GRAY = (50, 50, 50)
COLOR_DARK_GRAY = (30, 30, 30)
COLOR_BUTTON_ACTIVE = (255, 220, 50)
COLOR_BUTTON_INACTIVE = (100, 100, 100)

class VEEP_NDS:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("VEEP - NDS Mode")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 12)
        self.title_font = pygame.font.SysFont("Arial", 24, bold=True)
        
        # Load Sounds
        self.sounds = self.load_sounds()
        self.current_sound = None
        self.current_sound_name = "Ready"
        
        # UI State
        self.state = "LOGO"  # LOGO, PLAYER
        self.logo_timer = 0
        self.buttons = []
        self.setup_buttons()
        
        # Visualizer State
        self.angle = 0

    def load_sounds(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # HIVE is in veep/HIVE
        hive_dir = os.path.join(base_dir, 'veep', 'HIVE')
        if not os.path.exists(hive_dir):
            # Fallback if HIVE is in local directory
            hive_dir = os.path.join(base_dir, 'HIVE')
            
        sound_files = glob.glob(os.path.join(hive_dir, '*.wav'))
        sounds = []
        for f in sound_files:
            try:
                name = os.path.basename(f).replace('.wav', '')
                sound = pygame.mixer.Sound(f)
                sounds.append({'name': name, 'sound': sound, 'path': f})
            except Exception as e:
                print(f"Error loading {f}: {e}")
        return sounds

    def setup_buttons(self):
        # Create grid of buttons for bottom screen
        # Bottom screen starts at y=192
        start_y = 192
        cols = 2
        rows = 6
        btn_w = 120
        btn_h = 25
        padding = 5
        
        for i, sound_data in enumerate(self.sounds):
            col = i % cols
            row = i // cols
            x = padding + col * (btn_w + padding)
            y = start_y + padding + row * (btn_h + padding)
            
            # Use short name for display
            display_name = sound_data['name'].replace('nes_', '')[:15]
            
            self.buttons.append({
                'rect': pygame.Rect(x, y, btn_w, btn_h),
                'color': COLOR_BUTTON_INACTIVE,
                'text': display_name,
                'sound_index': i
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
                    if self.state == "PLAYER":
                        self.handle_click(event.pos)
            
            # Update & Draw based on State
            if self.state == "LOGO":
                self.update_logo()
                self.draw_logo()
            elif self.state == "PLAYER":
                self.update_player()
                self.draw_player()
                
            # Draw Hinge/Gap
            pygame.draw.rect(self.screen, (20, 20, 20), (0, 192, SCREEN_WIDTH, 2))

            pygame.display.flip()
            self.clock.tick(FPS)
            
        # pygame.quit() # Don't quit if running from launcher

    def update_logo(self):
        self.logo_timer += 1
        if self.logo_timer > 120: # 2 seconds
            self.state = "PLAYER"

    def draw_logo(self):
        # Top Screen Center
        text = self.title_font.render("Nintendo DS", True, COLOR_WHITE)
        rect = text.get_rect(center=(SCREEN_WIDTH//2, 192//2))
        self.screen.blit(text, rect)
        
        # Bottom Screen Center
        text_btm = self.font.render("Touch to Start", True, COLOR_YELLOW)
        rect_btm = text_btm.get_rect(center=(SCREEN_WIDTH//2, 192 + 192//2))
        
        # Blink effect
        if (self.logo_timer // 30) % 2 == 0:
            self.screen.blit(text_btm, rect_btm)

    def update_player(self):
        self.angle += 2
        
    def draw_player(self):
        # --- Top Screen (Visuals) ---
        # Draw "Vinyl" spinning
        center_x = SCREEN_WIDTH // 2
        center_y = 192 // 2
        radius = 70
        
        # Vinyl Record
        pygame.draw.circle(self.screen, (10, 10, 10), (center_x, center_y), radius)
        pygame.draw.circle(self.screen, (30, 30, 30), (center_x, center_y), radius, 2)
        
        # Label
        pygame.draw.circle(self.screen, COLOR_YELLOW, (center_x, center_y), 25)
        
        # Rotating marker
        marker_x = center_x + int(math.cos(math.radians(self.angle)) * 50)
        marker_y = center_y + int(math.sin(math.radians(self.angle)) * 50)
        pygame.draw.line(self.screen, (50, 50, 50), (center_x, center_y), (marker_x, marker_y), 2)
        
        # Info Text
        title_surf = self.font.render(f"Now Playing:", True, COLOR_WHITE)
        self.screen.blit(title_surf, (10, 10))
        
        name_surf = self.font.render(self.current_sound_name, True, COLOR_GOLD)
        self.screen.blit(name_surf, (10, 30))

        # --- Bottom Screen (Controls) ---
        # Background
        # pygame.draw.rect(self.screen, COLOR_DARK_GRAY, (0, 192, SCREEN_WIDTH, 192))
        
        # Buttons
        for btn in self.buttons:
            # Highlight on hover (simulated touch hover not really a thing on DS but good for PC)
            mx, my = pygame.mouse.get_pos()
            color = btn['color']
            if btn['rect'].collidepoint(mx, my):
                color = (color[0]+30, color[1]+30, color[2])
                
            pygame.draw.rect(self.screen, color, btn['rect'], border_radius=5)
            pygame.draw.rect(self.screen, COLOR_BLACK, btn['rect'], 2, border_radius=5)
            
            text_surf = self.font.render(btn['text'], True, COLOR_WHITE)
            text_rect = text_surf.get_rect(center=btn['rect'].center)
            self.screen.blit(text_surf, text_rect)

    def handle_click(self, pos):
        # Check buttons
        for btn in self.buttons:
            if btn['rect'].collidepoint(pos):
                self.play_sound(btn['sound_index'])
                
    def play_sound(self, index):
        if 0 <= index < len(self.sounds):
            # Stop current
            pygame.mixer.stop()
            
            # Play new
            sound_data = self.sounds[index]
            sound_data['sound'].play()
            self.current_sound_name = sound_data['name']
            
            # Visual feedback
            self.buttons[index]['color'] = COLOR_BUTTON_ACTIVE
            # Reset others
            for i, btn in enumerate(self.buttons):
                if i != index:
                    btn['color'] = COLOR_BUTTON_INACTIVE

if __name__ == "__main__":
    app = VEEP_NDS()
    app.run()
