import pygame
import sys

# Initialize Pygame
pygame.init()

# Game settings
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_FORCE = -12
PLAYER_SPEED = 5

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (34, 139, 34)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario Forever Remake")
clock = pygame.time.Clock()

# Player properties
player = pygame.Rect(100, HEIGHT - 100, 40, 60)
player_velocity = 0
on_ground = False

# Platforms
platforms = [
    pygame.Rect(0, HEIGHT - 40, WIDTH, 40),
    pygame.Rect(300, HEIGHT - 150, 200, 20),
    pygame.Rect(500, HEIGHT - 250, 200, 20)
]

# Coins
coins = [
    pygame.Rect(350, HEIGHT - 170, 20, 20),
    pygame.Rect(550, HEIGHT - 270, 20, 20)
]

# Enemies
enemies = [
    {'rect': pygame.Rect(600, HEIGHT - 60, 40, 40), 'dir': -1}
]

score = 0

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                player_velocity = JUMP_FORCE
                on_ground = False

    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        player.x += PLAYER_SPEED

    # Apply gravity
    player_velocity += GRAVITY
    player.y += player_velocity

    # Collision with platforms
    on_ground = False
    for platform in platforms:
        if player.colliderect(platform):
            if player_velocity > 0:
                player.y = platform.y - player.height
                player_velocity = 0
                on_ground = True
            elif player_velocity < 0:
                player.y = platform.y + platform.height
                player_velocity = 0

    # Coin collection
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            score += 10

    # Enemy movement
    for enemy in enemies:
        enemy['rect'].x += 2 * enemy['dir']
        if enemy['rect'].x <= 0 or enemy['rect'].x >= WIDTH - 40:
            enemy['dir'] *= -1

    # Enemy collision
    for enemy in enemies:
        if player.colliderect(enemy['rect']):
            running = False

    # Keep player in bounds
    player.x = max(0, min(player.x, WIDTH - player.width))

    # Drawing
    screen.fill(SKY_BLUE)
    
    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, GROUND_GREEN, platform)
    
    # Draw coins
    for coin in coins:
        pygame.draw.circle(screen, YELLOW, coin.center, 10)
    
    # Draw player
    pygame.draw.rect(screen, RED, player)
    
    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, BROWN, enemy['rect'])
    
    # Draw score
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
