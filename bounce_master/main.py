import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bounce Master")
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.width = 100
        self.height = 20
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 50
        self.speed = 8
        self.color = BLUE

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def move(self, direction):
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        if direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.move("left")
        if keys[pygame.K_RIGHT]:
            self.move("right")

class Ball:
    def __init__(self):
        self.radius = 15
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.speed_x = random.choice([-4, -3, 3, 4])
        self.speed_y = -5
        self.gravity = 0.2
        self.color = RED

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def update(self):
        # Apply gravity
        self.speed_y += self.gravity

        # Update position
        self.x += self.speed_x
        self.y += self.speed_y

        # Bounce off walls
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.speed_x *= -1

        # Bounce off ceiling
        if self.y <= self.radius:
            self.speed_y *= -1

    def check_paddle_collision(self, player):
        if (self.y + self.radius >= player.y and
            self.y - self.radius <= player.y + player.height and
            self.x >= player.x and
            self.x <= player.x + player.width):

            # Calculate bounce angle based on where the ball hit the paddle
            relative_intersect_x = (player.x + (player.width / 2)) - self.x
            normalized_intersect_x = relative_intersect_x / (player.width / 2)
            bounce_angle = normalized_intersect_x * (math.pi / 3)  # Max angle: 60 degrees

            # Calculate new velocity
            speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
            self.speed_x = -speed * math.sin(bounce_angle)
            self.speed_y = -speed * math.cos(bounce_angle)

            # Ensure the ball is above the paddle
            self.y = player.y - self.radius

            return True
        return False

    def is_out_of_bounds(self):
        return self.y > SCREEN_HEIGHT + self.radius

class Obstacle:
    def __init__(self):
        self.width = random.randint(30, 80)
        self.height = random.randint(10, 30)
        self.x = random.choice([0 - self.width, SCREEN_WIDTH])
        self.y = random.randint(100, SCREEN_HEIGHT - 200)
        self.speed = random.randint(3, 7)
        if self.x < 0:
            self.direction = 1  # Moving right
        else:
            self.direction = -1  # Moving left
        self.color = GREEN

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def update(self):
        self.x += self.speed * self.direction

    def is_off_screen(self):
        return (self.direction == 1 and self.x > SCREEN_WIDTH) or (self.direction == -1 and self.x + self.width < 0)

    def check_ball_collision(self, ball):
        # Simple rectangular collision detection
        if (ball.x + ball.radius > self.x and
            ball.x - ball.radius < self.x + self.width and
            ball.y + ball.radius > self.y and
            ball.y - ball.radius < self.y + self.height):

            # Determine which side of the obstacle was hit
            # This is a simplified collision response
            overlap_left = ball.x + ball.radius - self.x
            overlap_right = self.x + self.width - (ball.x - ball.radius)
            overlap_top = ball.y + ball.radius - self.y
            overlap_bottom = self.y + self.height - (ball.y - ball.radius)

            # Find the smallest overlap
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

            if min_overlap == overlap_left or min_overlap == overlap_right:
                ball.speed_x *= -1.1  # Reverse x direction and add a little speed
            else:
                ball.speed_y *= -1.1  # Reverse y direction and add a little speed

            return True
        return False

def main():
    player = Player()
    ball = Ball()
    obstacles = []
    score = 0
    game_over = False
    obstacle_timer = 0
    obstacle_spawn_delay = 120  # Frames between obstacle spawns

    font = pygame.font.SysFont(None, 36)

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_SPACE:
                    # Reset game
                    player = Player()
                    ball = Ball()
                    obstacles = []
                    score = 0
                    game_over = False
                    obstacle_timer = 0

        # Get key states
        keys = pygame.key.get_pressed()

        if not game_over:
            # Update game objects
            player.update(keys)
            ball.update()

            # Check for paddle collision
            if ball.check_paddle_collision(player):
                score += 10

            # Update obstacles
            for obstacle in obstacles[:]:
                obstacle.update()
                if obstacle.is_off_screen():
                    obstacles.remove(obstacle)
                elif obstacle.check_ball_collision(ball):
                    score += 5

            # Spawn new obstacles
            obstacle_timer += 1
            if obstacle_timer >= obstacle_spawn_delay:
                obstacles.append(Obstacle())
                obstacle_timer = 0
                # Make obstacles spawn faster as score increases
                obstacle_spawn_delay = max(60, 120 - (score // 100))

            # Check if ball is out of bounds
            if ball.is_out_of_bounds():
                game_over = True

        # Draw everything
        screen.fill(BLACK)

        # Draw game objects
        player.draw()
        ball.draw()
        for obstacle in obstacles:
            obstacle.draw()

        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw game over message
        if game_over:
            game_over_text = font.render("GAME OVER - Press SPACE to restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2))

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
