import pygame
import math
from pygame.math import Vector2

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.6
JUMP_FORCE = -12
PLAYER_SPEED = 5

# Colors
SKY_BLUE = (92, 148, 252)
GROUND_GREEN = (92, 168, 64)
PIPE_GREEN = (0, 168, 0)
PLAYER_RED = (228, 52, 52)
COIN_YELLOW = (252, 252, 0)
ENEMY_BROWN = (184, 124, 56)

class MarioLevel1_1:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Platform layout (x, y, width, height)
        self.platforms = [
            (0, SCREEN_HEIGHT-40, 2500, 40),  # Ground
            (400, 450, 120, 20),  # First platform
            (600, 400, 120, 20),  # Second platform
            (800, 350, 120, 20),  # Third platform
            (1000, 300, 120, 20), # Fourth platform
        ]
        
        # Pipes (x, height)
        self.pipes = [
            (300, 160),  # First pipe
            (1200, 200)  # Second pipe
        ]
        
        # Coins (x, y, base_y)
        self.coins = [
            (420, 400, 400), (500, 400, 400),  # First platform coins
            (620, 350, 350), (700, 350, 350),  # Second platform coins
            (820, 300, 300), (900, 300, 300)   # Third platform coins
        ]
        
        # Enemy positions
        self.goombas = [
            {"pos": Vector2(350, SCREEN_HEIGHT-80), "dir": -1},
            {"pos": Vector2(700, 430), "dir": 1}
        ]
        
        # Player setup
        self.player = {
            "pos": Vector2(100, SCREEN_HEIGHT-80),
            "vel": Vector2(0, 0),
            "on_ground": True,
            "score": 0,
            "lives": 3
        }
        
        self.camera_x = 0
        self.flag_pos = Vector2(1800, SCREEN_HEIGHT-160)
        self.running = True

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
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

    def update(self):
        # Physics
        self.player["vel"].y += GRAVITY
        self.player["pos"] += self.player["vel"]
        
        # Camera follow
        self.camera_x = max(0, self.player["pos"].x - SCREEN_WIDTH//2)
        
        # Platform collisions
        self.player["on_ground"] = False
        for plat in self.platforms:
            px, py, pw, ph = plat
            pr = pygame.Rect(px, py, pw, ph)
            
            if pr.colliderect(self.player_rect()):
                if self.player["vel"].y > 0:
                    self.player["pos"].y = py - 30
                    self.player["vel"].y = 0
                    self.player["on_ground"] = True
                elif self.player["vel"].y < 0:
                    self.player["pos"].y = py + ph
                    self.player["vel"].y = 0
        
        # Coin collection
        for coin in self.coins[:]:
            cx, cy, base_y = coin
            coin_rect = pygame.Rect(cx, cy, 20, 20)
            if self.player_rect().colliderect(coin_rect):
                self.coins.remove(coin)
                self.player["score"] += 100
                cy = base_y + math.sin(pygame.time.get_ticks()/200) * 20
        
        # Enemy movement
        for goomba in self.goombas:
            goomba["pos"].x += goomba["dir"] * 2
            if goomba["pos"].x < 200 or goomba["pos"].x > 1800:
                goomba["dir"] *= -1

    def draw(self):
        self.screen.fill(SKY_BLUE)
        
        # Draw ground
        for plat in self.platforms:
            pygame.draw.rect(self.screen, GROUND_GREEN, 
                            (plat[0]-self.camera_x, plat[1], plat[2], plat[3]))
        
        # Draw pipes
        for pipe in self.pipes:
            x, height = pipe
            pygame.draw.rect(self.screen, PIPE_GREEN,
                            (x-self.camera_x, SCREEN_HEIGHT-height, 60, height))
            pygame.draw.ellipse(self.screen, (0, 200, 0),
                            (x-10-self.camera_x, SCREEN_HEIGHT-height-20, 80, 40))
        
        # Draw coins
        for coin in self.coins:
            cx, cy, base_y = coin
            animated_y = base_y + math.sin(pygame.time.get_ticks()/200) * 20
            pygame.draw.circle(self.screen, COIN_YELLOW,
                            (int(cx-self.camera_x), int(animated_y)), 10)
        
        # Draw enemies
        for goomba in self.goombas:
            pygame.draw.ellipse(self.screen, ENEMY_BROWN,
                            (goomba["pos"].x-15-self.camera_x, goomba["pos"].y-20, 30, 40))
        
        # Draw player
        pygame.draw.rect(self.screen, PLAYER_RED, 
                        (self.player["pos"].x-15-self.camera_x, self.player["pos"].y-30, 30, 30))
        
        # Draw flag
        pygame.draw.rect(self.screen, (200, 200, 200),
                        (self.flag_pos.x-self.camera_x, self.flag_pos.y, 10, 160))
        pygame.draw.polygon(self.screen, (252, 60, 60), [
            (self.flag_pos.x+10-self.camera_x, self.flag_pos.y+40),
            (self.flag_pos.x+50-self.camera_x, self.flag_pos.y+60),
            (self.flag_pos.x+10-self.camera_x, self.flag_pos.y+80)
        ])
        
        pygame.display.flip()

    def player_rect(self):
        return pygame.Rect(self.player["pos"].x-15, self.player["pos"].y-30, 30, 30)

if __name__ == "__main__":
    game = MarioLevel1_1()
    game.run()
