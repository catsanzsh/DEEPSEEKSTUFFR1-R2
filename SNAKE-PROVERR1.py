import pygame
import random
import sys
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

# Define basic colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Initialize sound
pygame.mixer.init(44100, -16, 1, 512)

def generate_square_wave(freq, duration=0.1):
    sample_rate = pygame.mixer.get_init()[0]
    period = int(sample_rate / freq)
    amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
    tone = np.zeros((int(sample_rate * duration)), dtype=np.int16)
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    tone = (amplitude * 0.5 * np.sign(np.sin(2 * np.pi * freq * t))).astype(np.int16)
    sound = pygame.mixer.Sound(tone)
    return sound

eat_sound = generate_square_wave(400, 0.1)
game_over_sound = generate_square_wave(200, 0.5)

# Define game objects
snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
snake_direction = (0, 0)
food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
score = 0

# Set up the clock
clock = pygame.time.Clock()

# Main game loop
running = True
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_UP and snake_direction != (0, 1):
                    snake_direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake_direction != (0, -1):
                    snake_direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake_direction != (1, 0):
                    snake_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake_direction != (-1, 0):
                    snake_direction = (1, 0)
            else:
                if event.key == pygame.K_RETURN:
                    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
                    snake_direction = (0, 0)
                    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                    score = 0
                    game_over = False

    if not game_over:
        # Move the snake
        new_head = (snake[0][0] + snake_direction[0], snake[0][1] + snake_direction[1])
        snake.insert(0, new_head)

        # Check if the snake eats the food
        if snake[0] == food:
            score += 1
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            eat_sound.play()
        else:
            snake.pop()

        # Check for collisions with walls or itself
        if (
            snake[0][0] < 0 or snake[0][0] >= GRID_WIDTH or
            snake[0][1] < 0 or snake[0][1] >= GRID_HEIGHT or
            snake[0] in snake[1:]
        ):
            game_over = True
            game_over_sound.play()

        # Draw the grid and game objects
        screen.fill(BLACK)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, WHITE, rect, 1)

        for segment in snake:
            x, y = segment
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GREEN, rect)

        x, y = food
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, RED, rect)

        # Display the score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
    else:
        # Display game over text
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("Game Over", True, WHITE)
        restart_text = font.render("Press Enter to Restart", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + restart_text.get_height()))

    # Update the display
    pygame.display.update()

    # Control the frame rate
    clock.tick(10)

# Quit Pygame properly
pygame.quit()
sys.exit()
