import pygame
import random
import array
import asyncio
import platform
import math

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Famicom Edition")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Define game variables
ball_radius = 10
paddle_width = 10
paddle_height = 100
paddle_speed = 5
FPS = 60

# Initialize scores and ball speeds
score1 = 0
score2 = 0

# Define the paddles and ball
paddle1 = pygame.Rect(50, HEIGHT // 2 - paddle_height // 2, paddle_width, paddle_height)
paddle2 = pygame.Rect(WIDTH - 50 - paddle_width, HEIGHT // 2 - paddle_height // 2, paddle_width, paddle_height)
ball = pygame.Rect(WIDTH // 2 - ball_radius, HEIGHT // 2 - ball_radius, ball_radius * 2, ball_radius * 2)

class FamicomSoundEngine:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        pygame.mixer.set_num_channels(4)
        self.sample_rate = 44100
        
        # Pre-generate common waveforms
        self.square_wave = self.generate_square(523, 0.1)
        self.noise_wave = self.generate_noise(0.1)
        self.arpeggio_wave = self.generate_arpeggio()

    def generate_square(self, freq, duration, duty=0.5):
        samples = int(self.sample_rate * duration)
        wave = array.array('h')
        period = self.sample_rate / freq
        high_samples = int(period * duty)
        
        for i in range(samples):
            value = 32767 if (i % period) < high_samples else -32767
            wave.append(int(value * 0.2))  # 20% volume for authenticity
        return pygame.mixer.Sound(buffer=wave)

    def generate_noise(self, duration):
        samples = int(self.sample_rate * duration)
        wave = array.array('h')
        for _ in range(samples):
            val = random.randint(-32767, 32767) * 0.1  # 10% volume
            wave.append(int(val))
        return pygame.mixer.Sound(buffer=wave)

    def generate_arpeggio(self):
        wave = array.array('h')
        for freq in [523, 659, 784]:  # C5, E5, G5
            period = self.sample_rate / freq
            for i in range(int(self.sample_rate * 0.05)):
                val = 32767 if (i % period) < (period/2) else -32767
                wave.append(int(val * 0.15))
        return pygame.mixer.Sound(buffer=wave)

    def play_bounce(self):
        self.square_wave.play()

    def play_score(self):
        self.arpeggio_wave.play()

    def play_wall(self):
        self.noise_wave.play()

sound_engine = FamicomSoundEngine()

def reset_ball():
    global ball_speed_x, ball_speed_y
    ball.center = (WIDTH//2, HEIGHT//2)
    ball_speed_x = 5 * random.choice([-1, 1])
    ball_speed_y = 5 * random.choice([-1, 1])

# Initialize font
pygame.font.init()
font = pygame.font.Font(pygame.font.get_default_font(), 24)

async def main():
    global score1, score2, ball_speed_x, ball_speed_y
    clock = pygame.time.Clock()
    running = True

    reset_ball()

    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Move paddles
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and paddle1.top > 0:
            paddle1.y -= paddle_speed
        if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
            paddle1.y += paddle_speed
        if keys[pygame.K_UP] and paddle2.top > 0:
            paddle2.y -= paddle_speed
        if keys[pygame.K_DOWN] and paddle2.bottom < HEIGHT:
            paddle2.y += paddle_speed

        # Update ball position
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Wall collisions
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_speed_y *= -1
            sound_engine.play_wall()

        # Paddle collisions
        if ball.colliderect(paddle1) and ball_speed_x < 0:
            ball_speed_x *= -1
            sound_engine.play_bounce()
        elif ball.colliderect(paddle2) and ball_speed_x > 0:
            ball_speed_x *= -1
            sound_engine.play_bounce()

        # Scoring
        if ball.left <= 0:
            score2 += 1
            sound_engine.play_score()
            reset_ball()
        if ball.right >= WIDTH:
            score1 += 1
            sound_engine.play_score()
            reset_ball()

        # Drawing
        win.fill(BLACK)
        pygame.draw.rect(win, WHITE, paddle1)
        pygame.draw.rect(win, WHITE, paddle2)
        pygame.draw.ellipse(win, WHITE, ball)
        pygame.draw.aaline(win, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))
        
        # Retro-style score display
        score_text = font.render(f"{score1}   {score2}", True, WHITE)
        win.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 10))
        
        pygame.display.flip()
        await asyncio.sleep(0)

    if platform.system() != "Emscripten":
        pygame.quit()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pygame.quit()
