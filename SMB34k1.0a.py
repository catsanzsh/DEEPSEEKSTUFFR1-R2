import pygame
import math
from pygame.math import Vector2

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5  # More realistic gravity
JUMP_FORCE = 10  # Slightly reduced for better feel
PLAYER_SPEED = 3  # More controlled speed
GROUND_Y = 208

# NES hardware constants
TILE_SIZE = 16  # Standard NES tile size
SCREEN_TILES_W = 16  # 256/16
SCREEN_TILES_H = 15  # 240/16

# NES color palette (simplified)
PALETTES = {
    'sky': [(104, 136, 252), (88, 120, 252)],
    'ground': [(0, 168, 0), (0, 144, 0)],
    'player': [(228, 52, 52), (196, 20, 20)],
    'enemy': [(172, 80, 56), (140, 48, 24)],
    'coin': [(252, 216, 0), (220, 184, 0)]
}

class NESPPU:
    def __init__(self):
        self.nametable = [[(0, 'ground')] * SCREEN_TILES_W for _ in range(SCREEN_TILES_H)]
        self.pattern_table = {}
        self.init_patterns()
        
    def init_patterns(self):
        # Ground tile pattern
        self.pattern_table[0] = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1]
        ]
        
        # Pipe pattern
        self.pattern_table[1] = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        
    def render_tile(self, surface, tile_x, tile_y, pattern, palette):
        tile_data = self.pattern_table[pattern]
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                color_idx = tile_data[y][x]
                color = PALETTES[palette][color_idx]
                rect = (tile_x * TILE_SIZE + x, tile_y * TILE_SIZE + y, 1, 1)
                surface.fill(color, rect)

class SuperMarioBros3:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros. 3 Simulation")
        self.clock = pygame.time.Clock()
        self.ppu = NESPPU()
        self.init_nes_memory()
        
        # Player state
        self.player = {
            "x": 64, "y": GROUND_Y,
            "vel_x": 0, "vel_y": 0,
            "grounded": True,
            "facing_right": True,
            "width": 16, "height": 32
        }
        
        self.camera_x = 0
        self.running = True

    def init_nes_memory(self):
        # Initialize ground
        for y in range(13, SCREEN_TILES_H):
            for x in range(SCREEN_TILES_W):
                self.ppu.nametable[y][x] = (0, 'ground')
                
        # Add platforms
        self.set_tile(4, 10, 1, 'ground')
        self.set_tile(8, 8, 1, 'ground')
        self.set_tile(12, 6, 1, 'ground')
        self.set_tile(16, 8, 1, 'ground')

    def set_tile(self, x, y, pattern, palette):
        if 0 <= x < SCREEN_TILES_W and 0 <= y < SCREEN_TILES_H:
            self.ppu.nametable[y][x] = (pattern, palette)

    def run(self):
        while self.running:
            self.handle_input()
            self.update_physics()
            self.update_camera()
            self.render_frame()
            self.clock.tick(FPS)
        pygame.quit()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.player["grounded"]:
                    self.player["vel_y"] = -JUMP_FORCE
                    self.player["grounded"] = False
        
        keys = pygame.key.get_pressed()
        self.player["vel_x"] = PLAYER_SPEED * (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT])
        if self.player["vel_x"] > 0:
            self.player["facing_right"] = True
        elif self.player["vel_x"] < 0:
            self.player["facing_right"] = False

    def update_physics(self):
        # Apply gravity
        self.player["vel_y"] = min(self.player["vel_y"] + GRAVITY, 12)
        
        # Update position
        self.player["x"] += self.player["vel_x"]
        self.player["y"] += self.player["vel_y"]
        
        # Keep player in bounds
        self.player["x"] = max(0, min(self.player["x"], SCREEN_TILES_W * TILE_SIZE - self.player["width"]))
        
        # Ground collision
        if self.player["y"] >= GROUND_Y:
            self.player["y"] = GROUND_Y
            self.player["vel_y"] = 0
            self.player["grounded"] = True
            
        # Platform collisions
        player_rect = pygame.Rect(
            self.player["x"] - self.camera_x, 
            self.player["y"], 
            self.player["width"], 
            self.player["height"]
        )
        
        for y in range(SCREEN_TILES_H):
            for x in range(SCREEN_TILES_W):
                tile = self.ppu.nametable[y][x]
                if tile[0] == 1:  # Only check platform tiles
                    tile_rect = pygame.Rect(
                        x * TILE_SIZE, 
                        y * TILE_SIZE, 
                        TILE_SIZE, 
                        TILE_SIZE
                    )
                    
                    if player_rect.colliderect(tile_rect):
                        # Check if collision is from above
                        if player_rect.bottom > tile_rect.top and self.player["vel_y"] > 0:
                            self.player["y"] = tile_rect.top - self.player["height"]
                            self.player["vel_y"] = 0
                            self.player["grounded"] = True

    def update_camera(self):
        # Simple camera follows player
        self.camera_x = max(0, self.player["x"] - SCREEN_WIDTH // 3)

    def render_frame(self):
        # Create NES resolution surface
        nes_surface = pygame.Surface((SCREEN_TILES_W * TILE_SIZE, SCREEN_TILES_H * TILE_SIZE))
        
        # Render background
        for y in range(SCREEN_TILES_H):
            for x in range(SCREEN_TILES_W):
                pattern, palette = self.ppu.nametable[y][x]
                self.ppu.render_tile(nes_surface, x, y, pattern, palette)
        
        # Render player (simplified)
        player_rect = pygame.Rect(
            self.player["x"] - self.camera_x, 
            self.player["y"], 
            self.player["width"], 
            self.player["height"]
        )
        pygame.draw.rect(nes_surface, PALETTES['player'][0], player_rect)
        
        # Draw eyes to show direction
        eye_x = player_rect.right - 4 if self.player["facing_right"] else player_rect.left + 4
        pygame.draw.circle(nes_surface, (255, 255, 255), (eye_x, player_rect.top + 8), 2)
        
        # Scale to window
        scaled_surface = pygame.transform.scale(nes_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled_surface, (0, 0))
        
        pygame.display.flip()

if __name__ == "__main__":
    game = SuperMarioBros3()
    game.run()
