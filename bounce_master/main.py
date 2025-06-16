import pygame
import sys
import random
import math
import os
from leaderboard import initialize_leaderboard

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
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)

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
        self.original_width = 100
        self.original_speed = 8
        self.power_up_timer = 0
        self.active_power_ups = []
        
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
            
        # Update power-up timers
        if self.power_up_timer > 0:
            self.power_up_timer -= 1
            if self.power_up_timer == 0:
                self.reset_power_ups()
                
    def apply_power_up(self, power_up_type):
        self.active_power_ups.append(power_up_type)
        self.power_up_timer = 300  # 5 seconds at 60 FPS
        
        if power_up_type == "speed":
            self.speed = self.original_speed * 1.5
            self.color = YELLOW
        elif power_up_type == "size":
            self.width = self.original_width * 1.5
            self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))  # Keep paddle on screen
            self.color = CYAN
            
    def reset_power_ups(self):
        self.speed = self.original_speed
        self.width = self.original_width
        self.color = BLUE
        self.active_power_ups = []

class Ball:
    def __init__(self, x=None, y=None):
        self.radius = 15
        self.x = x if x is not None else SCREEN_WIDTH // 2
        self.y = y if y is not None else SCREEN_HEIGHT // 2
        self.speed_x = random.choice([-4, -3, 3, 4])
        self.speed_y = -5
        self.gravity = 0.2
        self.color = RED
        self.original_gravity = 0.2
        self.power_up_timer = 0
        self.active_power_ups = []
        
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
    def update(self):
        # Update power-up timers
        if self.power_up_timer > 0:
            self.power_up_timer -= 1
            if self.power_up_timer == 0:
                self.reset_power_ups()
        
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
    
    def apply_power_up(self, power_up_type):
        self.active_power_ups.append(power_up_type)
        self.power_up_timer = 300  # 5 seconds at 60 FPS
        
        if power_up_type == "slow":
            # Slow down the ball
            self.speed_x *= 0.6
            self.speed_y *= 0.6
            self.color = PURPLE
        elif power_up_type == "antigravity":
            # Reduce gravity effect
            self.gravity = -0.05  # Slight upward drift
            self.color = CYAN
            
    def reset_power_ups(self):
        self.gravity = self.original_gravity
        self.color = RED
        self.active_power_ups = []

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

class PowerUp:
    def __init__(self):
        self.radius = 10
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = random.randint(100, SCREEN_HEIGHT - 200)
        self.speed_y = 2
        
        # Choose a random power-up type
        self.types = ["speed", "size", "slow", "multiball", "antigravity"]
        self.type = random.choice(self.types)
        
        # Set color based on type
        if self.type == "speed":
            self.color = YELLOW  # Speed boost
        elif self.type == "size":
            self.color = CYAN    # Paddle size increase
        elif self.type == "slow":
            self.color = PURPLE  # Ball slowdown
        elif self.type == "multiball":
            self.color = ORANGE  # Multi-ball
        elif self.type == "antigravity":
            self.color = WHITE   # Anti-gravity
            
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        # Draw a small inner circle to make it look like a power-up
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius // 2)
        
    def update(self):
        self.y += self.speed_y
        
    def is_out_of_bounds(self):
        return self.y > SCREEN_HEIGHT + self.radius
    
    def check_paddle_collision(self, player):
        # Check if power-up collides with paddle
        if (self.y + self.radius >= player.y and 
            self.y - self.radius <= player.y + player.height and
            self.x >= player.x and 
            self.x <= player.x + player.width):
            return True
        return False

def main():
    # Try to initialize the leaderboard
    try:
        leaderboard = initialize_leaderboard()
        leaderboard_available = True
    except Exception as e:
        print(f"Could not initialize leaderboard: {e}")
        leaderboard_available = False
    
    player = Player()
    player.width = 200  # Increased paddle width as suggested
    player.original_width = 200
    balls = [Ball()]
    obstacles = []
    power_ups = []
    score = 0
    game_over = False
    obstacle_timer = 0
    power_up_timer = 0
    obstacle_spawn_delay = 120  # Frames between obstacle spawns
    power_up_spawn_delay = 300  # Frames between power-up spawns
    
    # Game states
    GAME_PLAYING = 0
    GAME_OVER = 1
    ENTER_NAME = 2
    SHOW_LEADERBOARD = 3
    game_state = GAME_PLAYING
    
    # Player name input
    player_name = ""
    name_submitted = False
    
    # Leaderboard data
    top_scores = []
    
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    
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
                
                if game_state == GAME_PLAYING:
                    pass  # No special key handling during gameplay
                
                elif game_state == GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        if leaderboard_available and score > 0:
                            game_state = ENTER_NAME
                            player_name = ""
                        else:
                            # Reset game
                            player = Player()
                            player.width = 200
                            player.original_width = 200
                            balls = [Ball()]
                            obstacles = []
                            power_ups = []
                            score = 0
                            game_over = False
                            obstacle_timer = 0
                            power_up_timer = 0
                            game_state = GAME_PLAYING
                
                elif game_state == ENTER_NAME:
                    if event.key == pygame.K_RETURN and player_name.strip():
                        # Submit score to leaderboard
                        if leaderboard_available:
                            try:
                                leaderboard.submit_score(player_name, score)
                                top_scores = leaderboard.get_top_scores(10)
                                game_state = SHOW_LEADERBOARD
                            except Exception as e:
                                print(f"Error submitting score: {e}")
                                # Reset game if leaderboard submission fails
                                player = Player()
                                player.width = 200
                                player.original_width = 200
                                balls = [Ball()]
                                obstacles = []
                                power_ups = []
                                score = 0
                                game_over = False
                                obstacle_timer = 0
                                power_up_timer = 0
                                game_state = GAME_PLAYING
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif len(player_name) < 15 and event.unicode.isalnum() or event.unicode == ' ':
                        player_name += event.unicode
                
                elif game_state == SHOW_LEADERBOARD:
                    if event.key == pygame.K_SPACE:
                        # Reset game
                        player = Player()
                        player.width = 200
                        player.original_width = 200
                        balls = [Ball()]
                        obstacles = []
                        power_ups = []
                        score = 0
                        game_over = False
                        obstacle_timer = 0
                        power_up_timer = 0
                        game_state = GAME_PLAYING
        
        # Get key states
        keys = pygame.key.get_pressed()
        
        if game_state == GAME_PLAYING:
            # Update player
            player.update(keys)
            
            # Update balls
            for ball in balls[:]:
                ball.update()
                
                # Check for paddle collision
                if ball.check_paddle_collision(player):
                    score += 10
                
                # Check if ball is out of bounds
                if ball.is_out_of_bounds():
                    balls.remove(ball)
                    if len(balls) == 0:
                        game_over = True
                        game_state = GAME_OVER
            
            # Update obstacles
            for obstacle in obstacles[:]:
                obstacle.update()
                if obstacle.is_off_screen():
                    obstacles.remove(obstacle)
                else:
                    for ball in balls:
                        if obstacle.check_ball_collision(ball):
                            score += 5
            
            # Update power-ups
            for power_up in power_ups[:]:
                power_up.update()
                if power_up.is_out_of_bounds():
                    power_ups.remove(power_up)
                elif power_up.check_paddle_collision(player):
                    # Apply power-up effect
                    if power_up.type == "speed" or power_up.type == "size":
                        player.apply_power_up(power_up.type)
                    elif power_up.type == "slow" or power_up.type == "antigravity":
                        for ball in balls:
                            ball.apply_power_up(power_up.type)
                    elif power_up.type == "multiball" and len(balls) < 3:  # Limit to 3 balls max
                        # Create a new ball at a random position
                        new_ball = Ball(
                            x=random.randint(50, SCREEN_WIDTH - 50),
                            y=random.randint(100, 300)
                        )
                        balls.append(new_ball)
                    
                    power_ups.remove(power_up)
                    score += 20
            
            # Spawn new obstacles
            obstacle_timer += 1
            if obstacle_timer >= obstacle_spawn_delay:
                obstacles.append(Obstacle())
                obstacle_timer = 0
                # Make obstacles spawn faster as score increases
                obstacle_spawn_delay = max(60, 120 - (score // 100))
            
            # Spawn new power-ups
            power_up_timer += 1
            if power_up_timer >= power_up_spawn_delay:
                power_ups.append(PowerUp())
                power_up_timer = 0
        
        # Draw everything
        screen.fill(BLACK)
        
        # Draw game objects
        if game_state == GAME_PLAYING or game_state == GAME_OVER:
            player.draw()
            for ball in balls:
                ball.draw()
            for obstacle in obstacles:
                obstacle.draw()
            for power_up in power_ups:
                power_up.draw()
            
            # Draw score
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            
            # Draw active power-ups
            if player.active_power_ups:
                power_up_text = font.render(f"Active: {', '.join(player.active_power_ups)}", True, WHITE)
                screen.blit(power_up_text, (10, 50))
            
            # Draw ball count
            ball_text = font.render(f"Balls: {len(balls)}", True, WHITE)
            screen.blit(ball_text, (SCREEN_WIDTH - 120, 10))
            
            # Draw game over message
            if game_state == GAME_OVER:
                game_over_text = font.render("GAME OVER", True, WHITE)
                screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
                
                if leaderboard_available and score > 0:
                    submit_text = font.render("Press SPACE to submit your score", True, WHITE)
                    screen.blit(submit_text, (SCREEN_WIDTH//2 - submit_text.get_width()//2, SCREEN_HEIGHT//2))
                else:
                    restart_text = font.render("Press SPACE to restart", True, WHITE)
                    screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2))
        
        elif game_state == ENTER_NAME:
            # Draw name entry screen
            title_text = font.render("Enter Your Name:", True, WHITE)
            screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//3))
            
            # Draw input box
            input_box = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 20, 300, 40)
            pygame.draw.rect(screen, WHITE, input_box, 2)
            
            # Draw entered name
            name_text = font.render(player_name, True, WHITE)
            screen.blit(name_text, (input_box.x + 10, input_box.y + 10))
            
            # Draw instructions
            instructions = small_font.render("Press ENTER to submit", True, GRAY)
            screen.blit(instructions, (SCREEN_WIDTH//2 - instructions.get_width()//2, input_box.y + 60))
            
            # Draw final score
            score_text = font.render(f"Your Score: {score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, input_box.y - 60))
        
        elif game_state == SHOW_LEADERBOARD:
            # Draw leaderboard screen
            title_text = font.render("LEADERBOARD", True, WHITE)
            screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 50))
            
            # Draw leaderboard entries
            y_pos = 120
            for i, entry in enumerate(top_scores):
                rank_text = font.render(f"{i+1}.", True, WHITE)
                name_text = font.render(entry.get('player_name', 'Unknown'), True, WHITE)
                score_text = font.render(str(entry.get('score', 0)), True, WHITE)
                
                screen.blit(rank_text, (SCREEN_WIDTH//4 - 30, y_pos))
                screen.blit(name_text, (SCREEN_WIDTH//4, y_pos))
                screen.blit(score_text, (SCREEN_WIDTH*3//4, y_pos))
                
                y_pos += 40
            
            # Draw instructions
            instructions = font.render("Press SPACE to play again", True, WHITE)
            screen.blit(instructions, (SCREEN_WIDTH//2 - instructions.get_width()//2, SCREEN_HEIGHT - 100))
            
            # Highlight player's score if it's in the leaderboard
            for i, entry in enumerate(top_scores):
                if entry.get('player_name') == player_name and entry.get('score') == score:
                    highlight_rect = pygame.Rect(SCREEN_WIDTH//4 - 40, 120 + i*40 - 5, SCREEN_WIDTH//2 + 100, 40)
                    pygame.draw.rect(screen, BLUE, highlight_rect, 2)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
