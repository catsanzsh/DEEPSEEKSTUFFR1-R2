import pygame
import random
import math
from pygame.math import Vector2

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.6
JUMP_HEIGHT = -13
PLAYER_SPEED = 6
ENEMY_SPASE = 2  # Base enemy speed
FPS = 60
LEVEL_WIDTH = 3000
WORLDS = 8
LEVELS_PER_WORLD = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
YELLOW = (255, 215, 0)
RED = (255, 0, 0)
BLUE = (30, 144, 255)
PINK = (255, 20, 147)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
SKY_BLUE = (135, 206, 235)

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

class GameState:
    def __init__(self):
        self.world = 1
        self.level = 1
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.time = 400
        self.active = True

    def next_level(self):
        if self.level < LEVELS_PER_WORLD:
            self.level += 1
        else:
            if self.world < WORLDS:
                self.world += 1
                self.level = 1
            else:
                print("You won the game!")
                pygame.quit()
                sys.exit()
        self.reset_level()

    def reset_level(self):
        self.time = 400
        self.active = True

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            print("Game Over!")
            pygame.quit()
            sys.exit()
        self.reset_level()

class Camera:
    def __init__(self):
        self.offset = Vector2(0, 0)
    
    def update(self, target):
        self.offset.x = target.rect.centerx - SCREEN_WIDTH // 2
        self.offset.x = max(0, min(self.offset.x, LEVEL_WIDTH - SCREEN_WIDTH))

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = Vector2(40, 60)
        self.image = pygame.Surface(self.size)
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.vel = Vector2(0, 0)
        self.on_ground = False
        self.state = "small"
        self.direction = "right"

    def update(self, platforms, enemies):
        self.vel.y += GRAVITY
        self.rect.x += self.vel.x
        self.check_collisions_x(platforms)
        self.rect.y += self.vel.y
        self.check_collisions_y(platforms)
        self.check_enemy_collisions(enemies)

    def jump(self):
        if self.on_ground:
            self.vel.y = JUMP_HEIGHT
            self.on_ground = False

    def check_collisions_x(self, platforms):
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.x > 0:
                    self.rect.right = plat.rect.left
                elif self.vel.x < 0:
                    self.rect.left = plat.rect.right

    def check_collisions_y(self, platforms):
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel.y > 0:
                    self.rect.bottom = plat.rect.top
                    self.on_ground = True
                    self.vel.y = 0
                elif self.vel.y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel.y = 0

    def check_enemy_collisions(self, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                if self.vel.y > 0 and self.rect.bottom < enemy.rect.centery:
                    enemy.kill()
                    self.vel.y = JUMP_HEIGHT * 0.7
                else:
                    if self.state == "small":
                        game.lose_life()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, world):
        super().__init__()
        self.size = Vector2(40, 40)
        self.image = pygame.Surface(self.size)
        self.color = RED if world % 2 else PURPLE
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = ENEMY_BASE + (world-1)*0.5
        self.direction = 1

    def update(self, platforms):
        self.rect.x += self.speed * self.direction
        if not any([self.rect.colliderect(p.rect) for p in platforms]):
            self.direction *= -1
            self.rect.x += self.speed * self.direction * 2

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = 0

    def update(self):
        self.angle = (self.angle + 5) % 360
        self.rect.y += math.sin(math.radians(self.angle)) * 0.5

def generate_level(world, level):
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()

    # Generate ground
    ground_height = 40
    platforms.add(Platform(0, SCREEN_HEIGHT - ground_height, LEVEL_WIDTH, ground_height, GREEN))

    # Procedural platforms
    num_platforms = 15 + world * 2
    for _ in range(num_platforms):
        x = random.randint(100, LEVEL_WIDTH-200)
        y = random.randint(200, SCREEN_HEIGHT-200)
        width = random.randint(80, 200)
        height = 20
        color = BROWN if random.random() < 0.3 else GREEN
        plat = Platform(x, y, width, height, color)
        platforms.add(plat)

        # Add enemies
        if random.random() < 0.4:
            enemies.add(Enemy(x + width//2, y - 40, world))

        # Add coins
        if random.random() < 0.6:
            coins.add(Coin(x + width//2, y - 60))

    return platforms, enemies, coins

def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

# Game setup
game = GameState()
camera = Camera()
player = Player()

def reset_game():
    global player
    player = Player()
    game.reset_level()

# Main loop
running = True
platforms, enemies, coins = generate_level(game.world, game.level)

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game.active:
                player.jump()

    # Player movement
    keys = pygame.key.get_pressed()
    if game.active:
        player.vel.x = 0
        if keys[pygame.K_LEFT]:
            player.vel.x = -PLAYER_SPEED
            player.direction = "left"
        if keys[pygame.K_RIGHT]:
            player.vel.x = PLAYER_SPEED
            player.direction = "right"

    # Update
    if game.active:
        game.time -= 1/60
        if game.time <= 0:
            game.lose_life()
        
        player.update(platforms, enemies)
        enemies.update(platforms)
        coins.update()
        camera.update(player)

    # Check level completion
    if len(coins) == 0 and game.active:
        game.active = False
        game.score += 100 * game.time
        game.next_level()
        platforms, enemies, coins = generate_level(game.world, game.level)
        player.rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

    # Drawing
    screen.fill(SKY_BLUE)
    
    # Draw platforms
    for plat in platforms:
        screen.blit(plat.image, (plat.rect.x - camera.offset.x, plat.rect.y))
    
    # Draw entities
    for enemy in enemies:
        screen.blit(enemy.image, (enemy.rect.x - camera.offset.x, enemy.rect.y))
    for coin in coins:
        screen.blit(coin.image, (coin.rect.x - camera.offset.x, coin.rect.y))
    screen.blit(player.image, (player.rect.x - camera.offset.x, player.rect.y))

    # UI
    draw_text(f"World {game.world}-{game.level}", 40, WHITE, 10, 10)
    draw_text(f"Coins: {game.coins}", 40, YELLOW, 10, 50)
    draw_text(f"Lives: {game.lives}", 40, RED, SCREEN_WIDTH-200, 10)
    draw_text(f"Time: {int(game.time)}", 40, WHITE, SCREEN_WIDTH-200, 50)

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
