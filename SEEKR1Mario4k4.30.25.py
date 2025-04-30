import pygame
import random
from pygame.math import Vector2

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
LEVEL_WIDTH = 4000
WORLD_COUNT = 8
LEVELS_PER_WORLD = 5
PLAYER_SPEED = 6
GRAVITY = 0.6
JUMP_FORCE = -13
DOUBLE_JUMP_FORCE = -10
MAX_HEALTH = 100

# Colors
SKY_BLUE = (135, 206, 235)
GROUND_GREEN = (34, 139, 34)
PLATFORM_BROWN = (139, 69, 19)
ENEMY_RED = (255, 0, 0)
COIN_YELLOW = (255, 215, 0)
PLAYER_BLUE = (0, 120, 255)
BACKGROUND_COLORS = [(175, 216, 230), (150, 200, 215), (125, 180, 200)]

class ProceduralGenerator:
    def __init__(self, seed=None):
        self.seed = seed or random.randint(0, 999999)
        random.seed(self.seed)
        
    def generate_world(self, world_num):
        return {
            'theme': ['ground', 'underground', 'sky', 'water'][world_num % 4],
            'levels': [self.generate_level(world_num, lvl+1) 
                      for lvl in range(LEVELS_PER_WORLD)]
        }
    
    def generate_level(self, world_num, level_num):
        level_length = 1500 + (world_num * 300)
        return {
            'platforms': self._generate_platforms(world_num, level_length),
            'enemies': self._generate_enemies(world_num, level_length),
            'collectibles': self._generate_collectibles(level_length)
        }
    
    def _generate_platforms(self, world_num, length):
        platforms = []
        y = SCREEN_HEIGHT - 100
        x = 0
        
        while x < length:
            span = random.randint(100, 200)
            gap = random.randint(50, 100 + world_num*20)
            
            if random.random() < 0.3:
                y = max(200, y - random.randint(50, 150))
            
            # Add different platform types
            if random.random() < 0.1:
                # Moving platform
                platforms.append({
                    'type': 'moving',
                    'rect': pygame.Rect(x, y, span, 20),
                    'direction': random.choice([-1, 1]),
                    'speed': random.randint(1, 3)
                })
            elif random.random() < 0.05:
                # Bounce platform
                platforms.append({
                    'type': 'bounce',
                    'rect': pygame.Rect(x, y, span, 20),
                    'strength': 15
                })
            else:
                # Regular platform
                platforms.append({
                    'type': 'normal',
                    'rect': pygame.Rect(x, y, span, 20)
                })
            
            x += span + gap
            
        return platforms
    
    def _generate_enemies(self, world_num, length):
        enemies = []
        for _ in range(5 + world_num*2):
            x = random.randint(100, length-100)
            y = SCREEN_HEIGHT-120
            enemy_type = random.choice(['walker', 'jumper', 'shooter'])
            enemies.append({
                'type': enemy_type,
                'rect': pygame.Rect(x, y, 30, 50),
                'direction': random.choice([-1, 1]),
                'jump_timer': 0,
                'shoot_timer': 0
            })
        return enemies
    
    def _generate_collectibles(self, length):
        return [{
            'type': 'coin',
            'rect': pygame.Rect(
                random.randint(100, length-100), 
                random.randint(200, SCREEN_HEIGHT-200),
                20, 20
            ),
            'collected': False
        } for _ in range(10)]

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self._create_images()
        self.image = self.normal_image
        self.rect = self.image.get_rect(center=(100, SCREEN_HEIGHT-150))
        self.velocity = Vector2(0, 0)
        self.on_ground = True
        self.double_jump_available = True
        self.facing_right = True
        self.score = 0
        self.health = MAX_HEALTH
        
    def _create_images(self):
        # Normal state
        self.normal_image = pygame.Surface((30, 50))
        self.normal_image.fill(PLAYER_BLUE)
        
        # Jumping state
        self.jump_image = pygame.Surface((25, 45))
        self.jump_image.fill(PLAYER_BLUE)
        
        # Damaged state
        self.damaged_image = pygame.Surface((30, 50))
        self.damaged_image.fill((255, 0, 0))

    def update(self, platforms, enemies, collectibles, dt):
        self._handle_input()
        self._update_physics(platforms, dt)
        self._handle_enemy_collisions(enemies)
        self._handle_collectibles(collectibles)
        self._update_sprite()

    def _handle_input(self):
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        if keys[pygame.K_LEFT]:
            self.velocity.x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.velocity.x = PLAYER_SPEED
            self.facing_right = True

    def jump(self):
        if self.on_ground:
            self.velocity.y = JUMP_FORCE
            self.on_ground = False
        elif self.double_jump_available:
            self.velocity.y = DOUBLE_JUMP_FORCE
            self.double_jump_available = False

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health <= 0:
            self.respawn()

    def respawn(self):
        self.rect.topleft = (100, SCREEN_HEIGHT-150)
        self.health = MAX_HEALTH

    def _update_physics(self, platforms, dt):
        self.velocity.y += GRAVITY
        prev_pos = self.rect.copy()
        
        # Horizontal movement
        self.rect.x += self.velocity.x
        for plat in platforms:
            if not self.rect.colliderect(plat['rect']):
                continue
            if self.velocity.x > 0:
                self.rect.right = plat['rect'].left
            elif self.velocity.x < 0:
                self.rect.left = plat['rect'].right
        
        # Vertical movement
        self.rect.y += self.velocity.y
        self.on_ground = False
        for plat in platforms:
            if not self.rect.colliderect(plat['rect']):
                continue
            
            if self.velocity.y > 0:
                if plat['type'] == 'bounce':
                    self.velocity.y = -plat['strength']
                else:
                    self.rect.bottom = plat['rect'].top
                    self.on_ground = True
                    self.velocity.y = 0
                    self.double_jump_available = True
            elif self.velocity.y < 0:
                self.rect.top = plat['rect'].bottom
                self.velocity.y = 0
        
        # Update moving platforms
        for plat in platforms:
            if plat['type'] == 'moving':
                plat['rect'].x += plat['direction'] * plat['speed']
                if random.random() < 0.01:
                    plat['direction'] *= -1
                if self.rect.colliderect(plat['rect']):
                    self.rect.x += plat['direction'] * plat['speed']

    def _handle_enemy_collisions(self, enemies):
        for enemy in enemies:
            if self.rect.colliderect(enemy['rect']):
                if self.velocity.y > 0 and self.rect.bottom <= enemy['rect'].top + 10:
                    enemy['type'] = 'dead'
                    self.velocity.y = JUMP_FORCE * 0.5
                    self.score += 100
                else:
                    self.take_damage(10)

    def _handle_collectibles(self, collectibles):
        for coin in collectibles:
            if not coin['collected'] and self.rect.colliderect(coin['rect']):
                coin['collected'] = True
                self.score += 50
                self.health = min(MAX_HEALTH, self.health + 10)

    def _update_sprite(self):
        if self.health < 30:
            self.image = self.damaged_image
        elif not self.on_ground:
            self.image = self.jump_image
        else:
            self.image = self.normal_image
            
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultramario3 Tech Demo")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.generator = ProceduralGenerator()
        self.world = self.generator.generate_world(1)
        self.player = Player()
        self.current_level = None
        self.camera_x = 0
        self.load_level(self.world['levels'][0])
        
    def load_level(self, level_data):
        self.current_level = level_data
        self.camera_x = 0
        
    def draw_hud(self):
        health_bar_width = 200
        current_health_width = (self.player.health / MAX_HEALTH) * health_bar_width
        
        # Health bar
        pygame.draw.rect(self.screen, (255, 0, 0), (20, 20, health_bar_width, 20))
        pygame.draw.rect(self.screen, (0, 255, 0), (20, 20, current_health_width, 20))
        
        # Score
        score_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 50))
        
    def draw_parallax_background(self):
        for i, color in enumerate(BACKGROUND_COLORS):
            pygame.draw.rect(
                self.screen, 
                color,
                (-self.camera_x * (0.2 * (i+1)), 0, SCREEN_WIDTH + self.camera_x, SCREEN_HEIGHT)
            )

    def run(self):
        running = True
        last_time = pygame.time.get_ticks()
        
        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000
            last_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Update game state
            self.player.update(
                self.current_level['platforms'],
                self.current_level['enemies'],
                self.current_level['collectibles'],
                dt
            )
            
            # Update camera
            self.camera_x = max(0, self.player.rect.centerx - SCREEN_WIDTH//2)
            self.camera_x = min(self.camera_x, LEVEL_WIDTH - SCREEN_WIDTH)
            
            # Draw everything
            self.screen.fill(SKY_BLUE)
            self.draw_parallax_background()
            
            # Draw platforms
            for plat in self.current_level['platforms']:
                color = PLATFORM_BROWN
                if plat['type'] == 'bounce':
                    color = (200, 150, 50)
                elif plat['type'] == 'moving':
                    color = (100, 50, 20)
                pygame.draw.rect(
                    self.screen, 
                    color,
                    (plat['rect'].x - self.camera_x, plat['rect'].y, 
                     plat['rect'].width, plat['rect'].height)
                )
            
            # Draw enemies
            for enemy in self.current_level['enemies']:
                if enemy['type'] == 'dead':
                    continue
                color = ENEMY_RED
                if enemy['type'] == 'jumper':
                    color = (200, 0, 0)
                elif enemy['type'] == 'shooter':
                    color = (150, 0, 0)
                pygame.draw.rect(
                    self.screen,
                    color,
                    (enemy['rect'].x - self.camera_x, enemy['rect'].y,
                     enemy['rect'].width, enemy['rect'].height)
                )
            
            # Draw collectibles
            for coin in self.current_level['collectibles']:
                if not coin['collected']:
                    pygame.draw.circle(
                        self.screen,
                        COIN_YELLOW,
                        (coin['rect'].centerx - self.camera_x, coin['rect'].centery),
                        coin['rect'].width // 2
                    )
            
            # Draw player
            self.screen.blit(
                self.player.image, 
                (self.player.rect.x - self.camera_x, self.player.rect.y)
            )
            
            # Draw HUD
            self.draw_hud()
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
