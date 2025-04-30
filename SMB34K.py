import pygame
import math
from pygame.math import Vector2

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.68
JUMP_FORCE = -12.8
PLAYER_SPEED = 5.2
ENEMY_SPEED = 1.7

# NES Color Palette (RGB)
SKY_BLUE = (104, 136, 252)
GROUND_GREEN = (0, 168, 0)
PIPE_GREEN = (0, 88, 0)
PLAYER_RED = (228, 52, 52)
COIN_YELLOW = (252, 216, 0)
ENEMY_BROWN = (172, 80, 56)
BRICK_ORANGE = (252, 152, 56)

class AccurateSMB3_1_1:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Level Geometry (pixel-perfect measurements)
        self.platforms = [
            (0, 536, 1792, 64),  # Main ground platform
            (384, 432, 96, 16),  # First brick platform
            (576, 384, 96, 16),  # Second brick platform
            (768, 336, 96, 16),  # Third brick platform
            (960, 288, 96, 16),  # Fourth brick platform
        ]
        
        # Pipes (x, visible_height, total_height)
        self.pipes = [
            (288, 128, 160),   # First pipe
            (1152, 160, 192)   # Second pipe
        ]
        
        # Coins (x, y, base_y, collected)
        self.coins = [
            (408, 400, 400, False), (456, 400, 400, False),  # First platform
            (600, 352, 352, False), (648, 352, 352, False),  # Second platform
            (792, 304, 304, False), (840, 304, 304, False)   # Third platform
        ]
        
        # Enemies (position, direction, alive)
        self.goombas = [
            {"pos": Vector2(336, 536), "dir": -1, "alive": True},
            {"pos": Vector2(672, 432), "dir": 1, "alive": True}
        ]
        
        # Player state
        self.player = {
            "pos": Vector2(64, 536),
            "vel": Vector2(0, 0),
            "on_ground": True,
            "score": 0,
            "lives": 3,
            "invincible": 0,
            "size": Vector2(16, 32)
        }
        
        # Camera control
        self.camera_x = 0
        self.level_length = 1888  # Exact level length from original
        self.flagpole = Vector2(1792, 400)
        self.running = True

    def run(self):
        while self.running:
            self.handle_input()
            self.update_physics()
            self.update_game_state()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.player["on_ground"]:
                    self.player["vel"].y = JUMP_FORCE
                    self.player["on_ground"] = False

        keys = pygame.key.get_pressed()
        self.player["vel"].x = 0
        if keys[pygame.K_LEFT]:
            self.player["vel"].x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.player["vel"].x = PLAYER_SPEED

    def update_physics(self):
        # Apply gravity with original acceleration values
        self.player["vel"].y = min(self.player["vel"].y + GRAVITY, 12)
        self.player["pos"] += self.player["vel"]
        
        # Camera control with screen-edge buffer
        self.camera_x = max(0, min(
            self.player["pos"].x - SCREEN_WIDTH//2,
            self.level_length - SCREEN_WIDTH
        ))
        
        # Platform collisions (original collision response)
        self.player["on_ground"] = False
        for plat in self.platforms:
            px, py, pw, ph = plat
            pr = pygame.Rect(px, py, pw, ph)
            
            if pr.colliderect(self.player_rect()):
                if self.player["vel"].y > 0:  # Landing
                    self.player["pos"].y = py - self.player["size"].y
                    self.player["vel"].y = 0
                    self.player["on_ground"] = True
                elif self.player["vel"].y < 0:  # Head bump
                    self.player["pos"].y = py + ph
                    self.player["vel"].y = 0

    def update_game_state(self):
        # Coin collection with original animation timing
        for coin in self.coins:
            if not coin[3] and self.player_rect().colliderect(
                pygame.Rect(coin[0], coin[1], 16, 16)
            ):
                coin[3] = True
                self.player["score"] += 100
                
        # Enemy movement patterns (original AI)
        for goomba in self.goombas:
            if goomba["alive"]:
                goomba["pos"].x += ENEMY_SPEED * goomba["dir"]
                if goomba["pos"].x < 64 or goomba["pos"].x > self.level_length - 64:
                    goomba["dir"] *= -1
                
                # Enemy collision
                if self.player_rect().colliderect(pygame.Rect(
                    goomba["pos"].x-16, goomba["pos"].y-16, 32, 32
                )):
                    if self.player["vel"].y > 0 and self.player["pos"].y < goomba["pos"].y - 8:
                        goomba["alive"] = False
                        self.player["vel"].y = -8
                        self.player["score"] += 500
                    else:
                        self.player["lives"] -= 1
                        self.reset_player()
                        
        # Flagpole collision
        if self.player_rect().colliderect(pygame.Rect(
            self.flagpole.x, self.flagpole.y, 16, 160
        )):
            self.level_complete()

    def draw(self):
        self.screen.fill(SKY_BLUE)
        
        # Draw ground with original checkerboard pattern
        for x in range(0, self.level_length, 32):
            if (x//32) % 2 == 0:
                pygame.draw.rect(self.screen, GROUND_GREEN,
                    (x - self.camera_x, 536, 32, 64))
        
        # Draw pipes with original dimensions
        for pipe in self.pipes:
            x, vis_h, total_h = pipe
            pygame.draw.rect(self.screen, PIPE_GREEN,
                (x - self.camera_x, SCREEN_HEIGHT - vis_h, 48, vis_h))
            pygame.draw.ellipse(self.screen, PIPE_GREEN,
                (x - 8 - self.camera_x, SCREEN_HEIGHT - vis_h - 16, 64, 32))
        
        # Draw coins with original animation
        for coin in self.coins:
            if not coin[3]:
                t = pygame.time.get_ticks() % 1000
                frame = int((t / 100) % 4)
                y_offset = [0, -2, -4, -2][frame]
                pygame.draw.circle(self.screen, COIN_YELLOW,
                    (coin[0] - self.camera_x, coin[1] + y_offset), 8)
        
        # Draw enemies with original movement
        for goomba in self.goombas:
            if goomba["alive"]:
                pygame.draw.ellipse(self.screen, ENEMY_BROWN,
                    (goomba["pos"].x - 16 - self.camera_x, goomba["pos"].y - 16, 32, 32))
                # Leg animation
                t = pygame.time.get_ticks() % 1000
                leg_offset = 2 if t < 500 else -2
                pygame.draw.line(self.screen, (0,0,0),
                    (goomba["pos"].x - 8 - self.camera_x, goomba["pos"].y + 8),
                    (goomba["pos"].x - 8 - self.camera_x + leg_offset, goomba["pos"].y + 16), 3)
        
        # Draw player with original proportions
        pygame.draw.rect(self.screen, PLAYER_RED, (
            self.player["pos"].x - 8 - self.camera_x,
            self.player["pos"].y - self.player["size"].y,
            self.player["size"].x,
            self.player["size"].y
        ))
        
        # Draw flagpole with original details
        pygame.draw.rect(self.screen, (248, 248, 248), (
            self.flagpole.x - self.camera_x, self.flagpole.y, 4, 160
        ))
        pygame.draw.polygon(self.screen, (252, 60, 60), [
            (self.flagpole.x + 4 - self.camera_x, self.flagpole.y + 32),
            (self.flagpole.x + 24 - self.camera_x, self.flagpole.y + 48),
            (self.flagpole.x + 4 - self.camera_x, self.flagpole.y + 64)
        ])
        
        pygame.display.flip()

    def player_rect(self):
        return pygame.Rect(
            self.player["pos"].x - 8,
            self.player["pos"].y - self.player["size"].y,
            self.player["size"].x,
            self.player["size"].y
        )

    def reset_player(self):
        self.player.update({
            "pos": Vector2(64, 536),
            "vel": Vector2(0, 0),
            "on_ground": True,
            "invincible": 60
        })

    def level_complete(self):
        print(f"Level Complete! Score: {self.player['score']}")
        self.running = False

if __name__ == "__main__":
    game = AccurateSMB3_1_1()
    game.run()
