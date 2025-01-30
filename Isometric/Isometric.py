" The main game function that handles movement, visuals, and game logic"

import worldMap
import pygame
import sys
import math

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
GRID_WIDTH, GRID_HEIGHT = 0, 0

# Define the grid
grid = []

# Player position
player_pos = [1, 1]
player_health = 100
player_score = 0

# Camera offset
camera_offset = [0, 0]

# Zoom level
zoom_level = 1.2

# Day/Night cycle
day_time = 0
day_duration = 1000

def iso_to_screen(x, y):
    """Convert isometric grid coordinates to screen coordinates."""
    screen_x = (y - x) * (TILE_WIDTH // 2) * zoom_level + SCREEN_WIDTH // 2 + camera_offset[0]
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





def draw_wall(x, y):
    """Draw an isometric wall with three visible faces (top and two sides)."""
    screen_x, screen_y = iso_to_screen(x, y)
    wall_height = TILE_HEIGHT * zoom_level

    cenY = screen_y - wall_height // 2

    # Wall left
    left_face_points = [
        (screen_x - TILE_WIDTH // 2 * zoom_level,    cenY),
        (screen_x - TILE_WIDTH // 2 * zoom_level,    cenY + wall_height // 2),
        (screen_x,                                   cenY + wall_height),
        (screen_x,                                   cenY + wall_height // 2)
    ]
    pygame.draw.polygon(screen, (30, 90, 30), left_face_points) 
    pygame.draw.polygon(screen, BLACK, left_face_points, 2)     

    # Wall right
    right_face_points = [
        (screen_x + TILE_WIDTH // 2 * zoom_level,      cenY),
        (screen_x + TILE_WIDTH // 2 * zoom_level,      cenY + wall_height // 2),
        (screen_x,                                     cenY + wall_height),
        (screen_x,                                     cenY + wall_height // 2)
    ]
    pygame.draw.polygon(screen, (20, 70, 20), right_face_points)  
    pygame.draw.polygon(screen, BLACK, right_face_points, 2)     

    # Wall top face
    top_face_points = [
        (screen_x - TILE_WIDTH // 2 * zoom_level, screen_y - wall_height // 2),
        (screen_x, screen_y - wall_height),
        (screen_x + TILE_WIDTH // 2 * zoom_level, screen_y - wall_height // 2),
        (screen_x, screen_y)
    ]
    pygame.draw.polygon(screen, DARK_GREEN, top_face_points)  
    pygame.draw.polygon(screen, BLACK, top_face_points, 2)   



    





def draw_grid():
    """Draw the isometric grid with shaded tiles and walls."""

    pX, pY = player_pos[0], player_pos[1]
    doNot = []

    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if grid[x][y] == 1:  # Floor tile
                if (x + y) % 2 == 0:
                    tile_color = LIGHT_GREEN
                else:
                    tile_color = GREEN
                draw_tile(x, y, tile_color)
            elif grid[x][y] == 2:  # Wall
                if y <= player_pos[1] and x <= player_pos[0]:
                    draw_wall(x, y)
                else:
                    doNot.append((x, y))


    return doNot


def draw_infront(doNot):
    """Draw the isometric grid with shaded tiles and walls."""

    pX, pY = player_pos[0], player_pos[1]

    for x, y in doNot:
        if grid[x][y] == 2:  # Wall
            draw_wall(x, y)

def draw_player():
    """Draw the player with a shadow, a black outline, and a more detailed appearance."""
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
    
    # Draw the black outline (slightly larger ellipse)
    outline_width = 18 * zoom_level  # Horizontal radius for the outline
    outline_height = 30 * zoom_level  # Vertical radius for the outline (taller than player)
    pygame.draw.ellipse(screen, BLACK, 
                        (screen_x - outline_width // 2, screen_y - outline_height // 2, outline_width, outline_height))
    
    # Draw player (as an ellipse, with less "fatness")
    player_width = 14 * zoom_level  # Horizontal radius of the player
    player_height = 28 * zoom_level  # Vertical radius of the player (height)
    pygame.draw.ellipse(screen, BLUE, 
                        (screen_x - player_width // 2, screen_y - player_height // 2, player_width, player_height))



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

def updateCamera():
    global player_pos, camera_offset
    # Calculate the player's screen position
    screen_x, screen_y = iso_to_screen(player_pos[0], player_pos[1])
    
    # Adjust the camera offset to center the player on the screen
    camera_offset[0] += (SCREEN_WIDTH // 2 - screen_x) * 0.1
    camera_offset[1] += (SCREEN_HEIGHT // 2 - screen_y) * 0.1




def main():
    global player_pos, player_health, player_score, camera_offset, zoom_level, day_time, grid, GRID_WIDTH, GRID_HEIGHT

    clock = pygame.time.Clock()
    worldMap.main()

    gridName = "start"
    warpedFrom = 11
    grid = worldMap.getArea(gridName)  # not working
    GRID_WIDTH, GRID_HEIGHT = len(grid), len(grid[0])
    sx, sy = worldMap.getPosition(gridName, warpedFrom)
    player_pos = [sx, sy]
    # Initial camera offset setup (center player on screen)
    screen_x, screen_y = iso_to_screen(player_pos[0], player_pos[1])
    camera_offset[0] = SCREEN_WIDTH // 2 - screen_x  # Center horizontally
    camera_offset[1] = SCREEN_HEIGHT // 2 - screen_y  # Center vertically

    # Key states dictionary
    keys = {
        pygame.K_RIGHT: False,
        pygame.K_LEFT: False,
        pygame.K_UP: False,
        pygame.K_DOWN: False
    }

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle key down events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    keys[pygame.K_RIGHT] = True
                if event.key == pygame.K_LEFT:
                    keys[pygame.K_LEFT] = True
                if event.key == pygame.K_UP:
                    keys[pygame.K_UP] = True
                if event.key == pygame.K_DOWN:
                    keys[pygame.K_DOWN] = True

                warpedFrom = -1

            # Handle key up events
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    keys[pygame.K_RIGHT] = False
                if event.key == pygame.K_LEFT:
                    keys[pygame.K_LEFT] = False
                if event.key == pygame.K_UP:
                    keys[pygame.K_UP] = False
                if event.key == pygame.K_DOWN:
                    keys[pygame.K_DOWN] = False

            # Handle zoom
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    zoom_level = min(2.0, zoom_level + 0.1)
                if event.button == 5:  # Scroll down
                    zoom_level = max(0.5, zoom_level - 0.1)

        # Update player position based on key states
        new_pos = player_pos.copy()
        if keys[pygame.K_RIGHT]:
            new_pos[0] -= 1
        if keys[pygame.K_LEFT]:
            new_pos[0] += 1
        if keys[pygame.K_UP]:
            new_pos[1] -= 1
        if keys[pygame.K_DOWN]:
            new_pos[1] += 1

        # Check if new position is within bounds and not a wall
        if 0 <= new_pos[0] < GRID_WIDTH and 0 <= new_pos[1] < GRID_HEIGHT and grid[new_pos[0]][new_pos[1]] != 2:
            player_pos = new_pos

            # Check if the player is on a warp tile and not already warping
            if grid[new_pos[0]][new_pos[1]] % 11 == 0 and grid[new_pos[0]][new_pos[1]] != warpedFrom and warpedFrom == -1:
                gridName, warpedFrom = worldMap.getNameWarp(gridName, grid[new_pos[0]][new_pos[1]])
                grid = worldMap.getArea(gridName)
                GRID_WIDTH, GRID_HEIGHT = len(grid), len(grid[0])
                sx, sy = worldMap.getPosition(gridName, warpedFrom)
                player_pos = [sx, sy]


        updateCamera()

        # Update day/night cycle
        day_time = (day_time + 1) % day_duration
        if day_time < day_duration // 2:
            screen.fill((50, 50, 100))  # Night
        else:
            screen.fill((135, 206, 250))  # Day

        # Draw the grid, player, and UI
        doNot = draw_grid()
        draw_player()
        draw_infront(doNot)
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