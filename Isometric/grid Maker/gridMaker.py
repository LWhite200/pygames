import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tile Grid Interaction")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TILE_COLORS = [(200, 200, 200), (100, 100, 255), (50, 255, 50), (255, 100, 100)]

# Grid settings
TILE_SIZE = 64
GRID_WIDTH, GRID_HEIGHT = 10, 10  # Default grid size

# Define the grid (initialized to 0)
grid = [[0 for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]

# Function to save the grid to a text file
def save_grid_to_file(filename="grid.txt"):
    with open(filename, 'w') as f:
        for row in grid:
            f.write(" ".join(map(str, row)) + "\n")
    print(f"Grid saved to {filename}")

# Draw the grid on the screen
def draw_grid():
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            # Draw each tile with its respective color
            tile_color = TILE_COLORS[grid[x][y] % len(TILE_COLORS)]
            pygame.draw.rect(screen, tile_color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)  # Border

# Handle mouse click to increase tile value
def handle_mouse_click():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    grid_x = mouse_x // TILE_SIZE
    grid_y = mouse_y // TILE_SIZE

    # Ensure coordinates are within grid bounds
    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
        grid[grid_x][grid_y] = (grid[grid_x][grid_y] + 1) % 3  # Cycle between 0, 1, 2

def main():
    global GRID_WIDTH, GRID_HEIGHT, grid

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button clicked
                    handle_mouse_click()

            # Check for key press to resize the grid (for testing)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    GRID_HEIGHT += 1
                    grid = [[0 for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]  # Reinitialize grid
                elif event.key == pygame.K_DOWN:
                    if GRID_HEIGHT > 1:
                        GRID_HEIGHT -= 1
                        grid = [[0 for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]  # Reinitialize grid
                elif event.key == pygame.K_LEFT:
                    if GRID_WIDTH > 1:
                        GRID_WIDTH -= 1
                        grid = [[0 for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]  # Reinitialize grid
                elif event.key == pygame.K_RIGHT:
                    GRID_WIDTH += 1
                    grid = [[0 for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]  # Reinitialize grid
                elif event.key == pygame.K_s:  # Press 's' to save the grid
                    save_grid_to_file()

        # Fill the screen with a background color
        screen.fill(WHITE)

        # Draw the grid
        draw_grid()

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(30)

if __name__ == "__main__":
    main()
