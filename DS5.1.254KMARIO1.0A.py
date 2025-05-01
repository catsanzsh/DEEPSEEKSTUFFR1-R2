import pygame
import sys
import math
from pygame.math import Vector2

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
JUMP_FORCE = -16
PLAYER_SPEED = 5

# Colors
SKY_BLUE = (107, 140, 255)
GROUND_COLOR = (94, 54, 21)
PLAYER_RED = (214, 40, 40)
ENEMY_COLOR = (148, 104, 58)
COIN_YELLOW = (255, 213, 43)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 48))
        self.rect = self.image.get_rect(midbottom=(100, 500))
        self.vel = Vector2(0, 0)
        self.frame = 0
        self.lives = 3
        self.score = 0
        self.update_sprite()
        
    def update_sprite(self):
        self.image.fill((0,0,0,0))
        # Body
        pygame.draw.rect(self.image, PLAYER_RED, (8, 8, 16, 32))
        # Head
        pygame.draw.circle(self.image, (255, 206, 158), (16, 12), 8)
        # Legs
        if math.sin(self.frame * 0.2) > 0:
            pygame.draw.rect(self.image, (50, 50, 200), (8, 36, 8, 12))
            pygame.draw.rect(self.image, (50, 50, 200), (16, 40, 8, 12))
        else:
            pygame.draw.rect(self.image, (50, 50, 200), (8, 40, 8, 12))
            pygame.draw.rect(self.image, (50, 50, 200), (16, 36, 8, 12))

    def update(self):
        self.vel.y += GRAVITY
        self.rect.y += self.vel.y
        self.rect.x += self.vel.x
        self.frame += 1
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - 32))
        if self.frame % 5 == 0:
            self.update_sprite()

    def jump(self):
        if self.rect.bottom >= SCREEN_HEIGHT - 40:
            self.vel.y = JUMP_FORCE

class Goomba(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.direction = 1
        self.update_sprite()
        
    def update_sprite(self):
        self.image.fill(ENEMY_COLOR)
        pygame.draw.circle(self.image, (0,0,0), (8, 8), 4)
        pygame.draw.circle(self.image, (0,0,0), (24, 8), 4)

    def update(self):
        self.rect.x += self.direction * 2
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.direction *= -1

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.rect = self.image.get_rect(center=(x, y))
        self.frame = 0
        
    def update(self):
        self.frame += 1
        self.image.fill((0,0,0,0))
        color = COIN_YELLOW if math.sin(self.frame * 0.5) > 0 else (255,215,0)
        pygame.draw.circle(self.image, color, (8,8), 8)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.reset_level()
        
    def reset_level(self):
        self.player = Player()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        
        # Platforms
        platforms = [
            (0, SCREEN_HEIGHT-40, SCREEN_WIDTH, 40),
            (200, 500, 160, 40),
            (400, 400, 160, 40),
            (600, 300, 160, 40)
        ]
        for x, y, w, h in platforms:
            block = pygame.sprite.Sprite()
            block.image = pygame.Surface((w, h))
            block.image.fill(GROUND_COLOR)
            block.rect = block.image.get_rect(topleft=(x, y))
            self.platforms.add(block)
            
        # Enemies
        for pos in [(300, 560), (500, 500)]:
            self.enemies.add(Goomba(*pos))
            
        # Coins
        for pos in [(250, 460), (450, 360)]:
            self.coins.add(Coin(*pos))
            
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.player.jump()
                    
            # Movement
            keys = pygame.key.get_pressed()
            self.player.vel.x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * PLAYER_SPEED
            
            # Collisions
            for platform in pygame.sprite.spritecollide(self.player, self.platforms, False):
                if self.player.vel.y > 0:
                    self.player.rect.bottom = platform.rect.top
                    self.player.vel.y = 0
                    
            for enemy in pygame.sprite.spritecollide(self.player, self.enemies, False):
                if self.player.vel.y > 0:
                    enemy.kill()
                    self.player.score += 100
                    self.player.vel.y = JUMP_FORCE * 0.5
                else:
                    self.player.lives -= 1
                    if self.player.lives > 0:
                        self.reset_level()
                        
            for coin in pygame.sprite.spritecollide(self.player, self.coins, True):
                self.player.score += 50
                
            # Update
            self.player.update()
            self.enemies.update()
            self.coins.update()
            
            # Draw
            self.screen.fill(SKY_BLUE)
            self.platforms.draw(self.screen)
            self.enemies.draw(self.screen)
            self.coins.draw(self.screen)
            self.screen.blit(self.player.image, self.player.rect)
            
            # HUD
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {self.player.score}", True, (255,255,255))
            lives_text = font.render(f"Lives: {self.player.lives}", True, (255,255,255))
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(lives_text, (10, 50))
            
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
