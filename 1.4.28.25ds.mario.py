import pygame
import sys

# Initialize Pygame
pygame.init()

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.6
JUMP_FORCE = -13
PLAYER_ACCEL = 0.5
PLAYER_FRICTION = -0.35
MAX_SPEED = 7
AIR_RESISTANCE = 0.02
WALL_SLIDE_SPEED = 3

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (34, 139, 34)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
PINK = (255, 192, 203)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario Forever CE")
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.rect = pygame.Rect(100, HEIGHT - 100, 32, 48)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.facing_right = True
        self.on_ground = False
        self.jump_buffer = 0
        self.coyote_time = 0
        self.powerup = 0  # 0=small, 1=big

class Enemy:
    def __init__(self, x, y, type):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = -1
        self.type = type  # 0=goomba, 1=koopa

# Game state
player = Player()
enemies = [Enemy(600, HEIGHT - 60, 0)]
platforms = [
    pygame.Rect(0, HEIGHT - 40, WIDTH, 40),
    pygame.Rect(300, HEIGHT - 150, 200, 20),
    pygame.Rect(500, HEIGHT - 250, 200, 20)
]
coins = []
powerups = []
camera_x = 0
score = 0
lives = 3
invincible = 0

def respawn():
    player.rect.topleft = (100, HEIGHT - 100)
    player.velocity = pygame.math.Vector2(0, 0)
    global camera_x
    camera_x = 0

def handle_movement():
    keys = pygame.key.get_pressed()
    
    # Horizontal movement
    if keys[pygame.K_LEFT]:
        if player.velocity.x > 0:
            player.acceleration.x = -PLAYER_ACCEL * 2
        else:
            player.acceleration.x = -PLAYER_ACCEL
        player.facing_right = False
    elif keys[pygame.K_RIGHT]:
        if player.velocity.x < 0:
            player.acceleration.x = PLAYER_ACCEL * 2
        else:
            player.acceleration.x = PLAYER_ACCEL
        player.facing_right = True
    else:
        player.acceleration.x = 0

    # Apply friction
    if player.on_ground:
        player.velocity.x += player.velocity.x * PLAYER_FRICTION
    else:
        player.velocity.x += player.velocity.x * AIR_RESISTANCE

    # Jump buffer and coyote time
    if keys[pygame.K_SPACE]:
        player.jump_buffer = 6
    if player.jump_buffer > 0 and (player.on_ground or player.coyote_time > 0):
        player.velocity.y = JUMP_FORCE
        player.jump_buffer = 0
        player.coyote_time = 0

    # Variable jump height
    if not keys[pygame.K_SPACE] and player.velocity.y < -4:
        player.velocity.y = -4

    # Update physics
    player.velocity.x += player.acceleration.x
    player.velocity.x = max(-MAX_SPEED, min(player.velocity.x, MAX_SPEED))
    player.velocity.y += GRAVITY

def handle_collisions():
    player.on_ground = False
    player.coyote_time = max(0, player.coyote_time - 1)
    
    # Horizontal movement
    player.rect.x += player.velocity.x
    for platform in platforms:
        if player.rect.colliderect(platform):
            if player.velocity.x > 0:
                player.rect.right = platform.left
            elif player.velocity.x < 0:
                player.rect.left = platform.right
            player.velocity.x = 0

    # Vertical movement
    player.rect.y += player.velocity.y
    for platform in platforms:
        if player.rect.colliderect(platform):
            if player.velocity.y > 0:
                player.rect.bottom = platform.top
                player.velocity.y = 0
                player.on_ground = True
                player.coyote_time = 6
            elif player.velocity.y < 0:
                player.rect.top = platform.bottom
                player.velocity.y = 0

def enemy_ai():
    for enemy in enemies:
        # Simple patrol AI
        enemy.velocity.x = enemy.direction * 2
        enemy.rect.x += enemy.velocity.x
        
        # Check platform edges
        on_platform = False
        for platform in platforms:
            if enemy.rect.colliderect(platform):
                on_platform = True
                # Check if at platform edge
                test_rect = pygame.Rect(
                    enemy.rect.x + enemy.direction * 20,
                    enemy.rect.bottom,
                    enemy.rect.width,
                    2
                )
                if not any(test_rect.colliderect(p) for p in platforms):
                    enemy.direction *= -1
        if not on_platform:
            enemy.direction *= -1

# Game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    handle_movement()
    handle_collisions()
    enemy_ai()
    
    # Camera system
    camera_x += (player.rect.x - camera_x - WIDTH/2) * 0.05
    camera_x = max(0, min(camera_x, 3000 - WIDTH))
    
    # Drawing
    screen.fill(SKY_BLUE)
    
    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, GROUND_GREEN, platform.move(-camera_x, 0))
    
    # Draw player
    color = RED if invincible % 4 < 2 else PINK
    if player.powerup == 1:
        pygame.draw.rect(screen, color, player.rect.move(-camera_x + 4, -20), 0, 5)
    pygame.draw.rect(screen, color, player.rect.move(-camera_x, 0), 0, 5)
    
    # Draw enemies
    for enemy in enemies:
        color = BROWN if enemy.type == 0 else (0, 128, 0)
        pygame.draw.rect(screen, color, enemy.rect.move(-camera_x, 0), 0, 3)
    
    # UI
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score} Lives: {lives}", True, (0, 0, 0))
    screen.blit(text, (10 - camera_x, 10))
    
    pygame.display.flip()
    clock.tick(FPS)
