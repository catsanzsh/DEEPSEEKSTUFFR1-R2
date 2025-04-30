import pygame
import sys

# Constants
NES_WIDTH, NES_HEIGHT = 256, 240
SCALE = 3
WIDTH, HEIGHT = NES_WIDTH * SCALE, NES_HEIGHT * SCALE
TILE_SIZE = 16
GRAVITY = 0.6875
JUMP_FORCE = -10.5
PLAYER_SPEED = 2.5
COLORS = {
    'sky': (104, 136, 252),
    'ground': (0, 168, 0),
    'pipe': (0, 88, 0),
    'player': (228, 52, 52),
    'goomba': (172, 80, 56),
    'brick': (252, 152, 56)
}

class Entity(pygame.sprite.Sprite):
    def __init__(self, pos, size, color):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)
        self.velocity = pygame.Vector2(0, 0)

class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos, (TILE_SIZE, TILE_SIZE*2), COLORS['player'])
        self.jump_buffer = False
        self.on_ground = False
        self.coyote_time = 0

    def update(self, dt, platforms):
        self.velocity.x = 0
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT]: self.velocity.x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]: self.velocity.x = PLAYER_SPEED
        
        # Jump mechanics
        jump_pressed = keys[pygame.K_SPACE]
        if jump_pressed and (self.on_ground or self.coyote_time > 0):
            self.velocity.y = JUMP_FORCE
            self.on_ground = False
            self.coyote_time = 0
            
        # Variable jump height
        if not jump_pressed and self.velocity.y < JUMP_FORCE * 0.5:
            self.velocity.y = JUMP_FORCE * 0.5

        # Apply physics
        self.velocity.y = min(self.velocity.y + GRAVITY, 12)
        self.rect.x += self.velocity.x * dt * 60
        self.resolve_collisions(platforms, 'horizontal')
        
        self.rect.y += self.velocity.y * dt * 60
        self.resolve_collisions(platforms, 'vertical')
        
        # Coyote time
        if self.on_ground:
            self.coyote_time = 0.1
        else:
            self.coyote_time = max(0, self.coyote_time - dt)

    def resolve_collisions(self, platforms, direction):
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == 'horizontal':
                    if self.velocity.x > 0:
                        self.rect.right = platform.rect.left
                    elif self.velocity.x < 0:
                        self.rect.left = platform.rect.right
                elif direction == 'vertical':
                    if self.velocity.y > 0:
                        self.rect.bottom = platform.rect.top
                        self.velocity.y = 0
                        self.on_ground = True
                    elif self.velocity.y < 0:
                        self.rect.top = platform.rect.bottom
                        self.velocity.y = 0

class Goomba(Entity):
    def __init__(self, pos):
        super().__init__(pos, (TILE_SIZE, TILE_SIZE), COLORS['goomba'])
        self.direction = 1
        self.speed = 1.25

    def update(self, dt, platforms):
        self.rect.x += self.direction * self.speed * dt * 60
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                self.direction *= -1
                break

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.nes_surf = pygame.Surface((NES_WIDTH, NES_HEIGHT))
        
        # Level setup
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player = Player((NES_WIDTH//2, NES_HEIGHT-TILE_SIZE))
        
        self.load_level()
        self.camera_x = 0

    def load_level(self):
        # Ground
        self.platforms.add(Entity((0, NES_HEIGHT-TILE_SIZE), (NES_WIDTH, TILE_SIZE), COLORS['ground']))
        
        # Platforms
        platform_data = [
            (3*TILE_SIZE, 10*TILE_SIZE, 3*TILE_SIZE, TILE_SIZE),
            (6*TILE_SIZE, 8*TILE_SIZE, 3*TILE_SIZE, TILE_SIZE),
            (9*TILE_SIZE, 6*TILE_SIZE, 3*TILE_SIZE, TILE_SIZE)
        ]
        for x, y, w, h in platform_data:
            self.platforms.add(Entity((x, y), (w, h), COLORS['brick']))
        
        # Enemies
        self.enemies.add(Goomba((5*TILE_SIZE, NES_HEIGHT-2*TILE_SIZE)))
        self.enemies.add(Goomba((9*TILE_SIZE, 6*TILE_SIZE)))

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000
            self.handle_input()
            self.update(dt)
            self.draw()
            
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def update(self, dt):
        self.player.update(dt, self.platforms)
        self.enemies.update(dt, self.platforms)
        
        # Enemy collision
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                if self.player.velocity.y > 0:
                    enemy.kill()
                    self.player.velocity.y = JUMP_FORCE * 0.75
                else:
                    self.player.rect.midbottom = (NES_WIDTH//2, NES_HEIGHT-TILE_SIZE)
                    self.player.velocity.y = 0
        
        # Camera follow
        self.camera_x = max(0, self.player.rect.centerx - NES_WIDTH//2)
        self.camera_x = min(self.camera_x, NES_WIDTH - NES_WIDTH)

    def draw(self):
        self.nes_surf.fill(COLORS['sky'])
        
        # Draw platforms
        for platform in self.platforms:
            self.nes_surf.blit(platform.image, (platform.rect.x - self.camera_x, platform.rect.y))
        
        # Draw entities
        self.nes_surf.blit(self.player.image, (self.player.rect.x - self.camera_x, self.player.rect.y))
        for enemy in self.enemies:
            self.nes_surf.blit(enemy.image, (enemy.rect.x - self.camera_x, enemy.rect.y))
        
        # Scale to display
        scaled = pygame.transform.scale(self.nes_surf, (WIDTH, HEIGHT))
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

if __name__ == "__main__":
    Game().run()
