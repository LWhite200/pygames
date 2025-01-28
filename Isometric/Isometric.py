import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Improved Isometric Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (50, 150, 50)
DARK_GREEN = (30, 90, 30)
LIGHT_GREEN = (100, 200, 100)
SHADOW_COLOR = (0, 0, 0, 100)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Grid settings
TILE_WIDTH, TILE_HEIGHT = 64, 32
GRID_WIDTH, GRID_HEIGHT = 10, 10

# Player position
player_pos = [0, 0]
player_health = 100
player_score = 0

# Camera offset
camera_offset = [0, 0]

# Zoom level
zoom_level = 1.0

# Obstacles and collectibles
obstacles = [(2, 2), (3, 3), (4, 4)]
collectibles = [(5, 5), (6, 6), (7, 7)]

# Day/Night cycle
day_time = 0
day_duration = 1000

def iso_to_screen(x, y):
    """Convert isometric grid coordinates to screen coordinates."""
    screen_x = (x - y) * (TILE_WIDTH // 2) * zoom_level + SCREEN_WIDTH // 2 + camera_offset[0]
    screen_y = (x + y) * (TILE_HEIGHT // 2) * zoom_level + SCREEN_HEIGHT // 4 + camera_offset[1]
    return screen_x, screen_y

def draw_tile(x, y, color):
    """Draw a single isometric tile with shading."""
    screen_x, screen_y = iso_to_screen(x, y)
    points = [
        (screen_x, screen_y + TILE_HEIGHT // 2 * zoom_level),
        (screen_x + TILE_WIDTH // 2 * zoom_level, screen_y),
        (screen_x, screen_y - TILE_HEIGHT // 2 * zoom_level),
        (screen_x - TILE_WIDTH // 2 * zoom_level, screen_y)
    ]
    # Draw the base tile
    pygame.draw.polygon(screen, color, points)
    # Draw a darker border for depth
    pygame.draw.polygon(screen, DARK_GREEN, points, 2)

def draw_grid():
    """Draw the isometric grid with shaded tiles."""
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            # Alternate tile colors for a checkerboard effect
            if (x + y) % 2 == 0:
                tile_color = LIGHT_GREEN
            else:
                tile_color = GREEN
            draw_tile(x, y, tile_color)

def draw_player():
    """Draw the player with a shadow and a more detailed appearance."""
    screen_x, screen_y = iso_to_screen(player_pos[0], player_pos[1])
    
    # Draw shadow
    shadow_offset = 5 * zoom_level
    shadow_points = [
        (screen_x - shadow_offset, screen_y + TILE_HEIGHT // 2 * zoom_level + shadow_offset),
        (screen_x + TILE_WIDTH // 2 * zoom_level - shadow_offset, screen_y + shadow_offset),
        (screen_x - shadow_offset, screen_y - TILE_HEIGHT // 2 * zoom_level + shadow_offset),
        (screen_x - TILE_WIDTH // 2 * zoom_level - shadow_offset, screen_y + shadow_offset)
    ]
    shadow_surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(shadow_surface, SHADOW_COLOR, shadow_points)
    screen.blit(shadow_surface, (0, 0))
    
    # Draw player
    pygame.draw.circle(screen, BLUE, (screen_x, screen_y), 10 * zoom_level)

def draw_obstacles():
    """Draw obstacles on the grid."""
    for obstacle in obstacles:
        screen_x, screen_y = iso_to_screen(obstacle[0], obstacle[1])
        pygame.draw.rect(screen, RED, (screen_x - 10 * zoom_level, screen_y - 10 * zoom_level, 20 * zoom_level, 20 * zoom_level))

def draw_collectibles():
    """Draw collectibles on the grid."""
    for collectible in collectibles:
        screen_x, screen_y = iso_to_screen(collectible[0], collectible[1])
        pygame.draw.circle(screen, YELLOW, (screen_x, screen_y), 5 * zoom_level)

def draw_ui():
    """Draw the UI elements."""
    font = pygame.font.Font(None, 36)
    health_text = font.render(f"Health: {player_health}", True, WHITE)
    score_text = font.render(f"Score: {player_score}", True, WHITE)
    screen.blit(health_text, (10, 10))
    screen.blit(score_text, (10, 50))

def draw_game_over():
    """Draw the game over screen."""
    font = pygame.font.Font(None, 72)
    game_over_text = font.render("Game Over", True, RED)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))

def main():
    global player_pos, player_health, player_score, camera_offset, zoom_level, day_time

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle player movement
            if event.type == pygame.KEYDOWN:
                new_pos = player_pos.copy()
                if event.key == pygame.K_UP:
                    new_pos[1] -= 1
                if event.key == pygame.K_DOWN:
                    new_pos[1] += 1
                if event.key == pygame.K_LEFT:
                    new_pos[0] -= 1
                if event.key == pygame.K_RIGHT:
                    new_pos[0] += 1

                # Check if new position is within bounds and not an obstacle
                if 0 <= new_pos[0] < GRID_WIDTH and 0 <= new_pos[1] < GRID_HEIGHT and (new_pos[0], new_pos[1]) not in obstacles:
                    player_pos = new_pos

            # Handle zoom
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    zoom_level = min(2.0, zoom_level + 0.1)
                if event.button == 5:  # Scroll down
                    zoom_level = max(0.5, zoom_level - 0.1)

        # Update camera offset to follow the player
        screen_x, screen_y = iso_to_screen(player_pos[0], player_pos[1])
        camera_offset[0] += (SCREEN_WIDTH // 2 - screen_x) * 0.1
        camera_offset[1] += (SCREEN_HEIGHT // 4 - screen_y) * 0.1

        # Check for collectibles
        for collectible in collectibles[:]:
            if (player_pos[0], player_pos[1]) == collectible:
                collectibles.remove(collectible)
                player_score += 10

        # Update day/night cycle
        day_time = (day_time + 1) % day_duration
        if day_time < day_duration // 2:
            screen.fill((50, 50, 100))  # Night
        else:
            screen.fill((135, 206, 250))  # Day

        # Draw the grid, player, obstacles, and collectibles
        draw_grid()
        draw_obstacles()
        draw_collectibles()
        draw_player()
        draw_ui()

        # Check for game over
        if player_health <= 0:
            draw_game_over()

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(30)

if __name__ == "__main__":
    main()