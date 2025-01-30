import pygame
import sys
import tkinter as tk
from tkinter import simpledialog

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

# Font for rendering numbers
pygame.font.init()
FONT = pygame.font.SysFont("Arial", 16)

TILE_SIZE = 20
GRID_WIDTH, GRID_HEIGHT = 10, 10

numWarps = 0  # Amount of "11 divisible"

def initialize_grid():
    grid = [[1 for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if x == 0 or x == GRID_WIDTH - 1 or y == 0 or y == GRID_HEIGHT - 1:
                grid[x][y] = 2
    return grid

grid = initialize_grid()

def getTextUser():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Get the filename from the user
    filename = simpledialog.askstring("Input", "Enter the filename to save the grid:", parent=root)

    if filename is None:  # User canceled the input
        return None

    # Initialize the result list
    res = [filename, ""]

    # Construct the Areas string
    res[1] = f"Areas.append(Area(\"{filename}\", ["

    for i in range(1, numWarps + 1):
        ii = i * 11
        part1 = simpledialog.askstring("Input", f"What Place Does Warp {ii} go to:", parent=root)
        part2 = simpledialog.askstring("Input", f"Which Warp Zone of {part1}:", parent=root)

        if part1 is None or part2 is None:  # User canceled the input
            return None

        res[1] += f"({ii}, (\"{part1}\", {part2}))"
        if i < numWarps:
            res[1] += ", "

    res[1] += "]))"

    root.destroy()
    return res

def save_grid_to_file():
    userText = getTextUser()

    if userText is None:  # Check if the user canceled the input
        print("Save canceled.")
        return

    filename = userText[0] + ".txt"

    warps = []
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if grid[x][y] >= 11 and grid[x][y] <= 99 and grid[x][y] % 11 == 0:
                warps.append((x, y, grid[x][y]))

    try:
        with open(filename, 'w') as f:
            for y in range(GRID_HEIGHT):
                row = [str(grid[x][y]) for x in range(GRID_WIDTH)]
                f.write(" ".join(row) + "\n")

            if warps:
                f.write("\n" + userText[1] + "\n")

        print(f"Grid saved to {filename}")
    except IOError as e:
        print(f"Error saving file: {e}")

def draw_grid():
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            # Draw the tile background
            tile_color = TILE_COLORS[grid[x][y] % len(TILE_COLORS)]
            pygame.draw.rect(screen, tile_color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

            # Draw the number on the tile
            number = grid[x][y]
            if number >= 11 and number <= 99 and number % 11 == 0:
                text_surface = FONT.render(str(number), True, BLACK)
            else:
                text_surface = FONT.render(str(number % 12), True, BLACK)
            text_rect = text_surface.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
            screen.blit(text_surface, text_rect)

def handle_mouse_click():
    global numWarps
    mouse_x, mouse_y = pygame.mouse.get_pos()
    grid_x = mouse_x // TILE_SIZE
    grid_y = mouse_y // TILE_SIZE

    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
        current_value = grid[grid_x][grid_y]
        
        # Case 1: If the value is divisible by 11 (11, 22, 33,...), reset it to 0
        if current_value % 11 == 0 and current_value != 0:
            numWarps -= 1
            grid[grid_x][grid_y] = 1 if not (grid_x == 0 or grid_x == GRID_WIDTH - 1 or grid_y == 0 or grid_y == GRID_HEIGHT - 1) else 2
        
        # Case 2: If the value is less than 11, increment it
        elif current_value < 11:
            grid[grid_x][grid_y] += 1

            if grid[grid_x][grid_y] == 11:
                numWarps += 1
                grid[grid_x][grid_y] *= numWarps
        
        # Case 3: If the value is 0, and we want to set a new divisible by 11 number
        elif current_value == 0:
            # Find the first available divisible by 11 number (11, 22, 33, ..., 99)
            for num in range(11, 100, 11):
                if not any(num == grid[x][y] for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)):
                    grid[grid_x][grid_y] = num
                    break

def makeWarp():
    global numWarps
    mouse_x, mouse_y = pygame.mouse.get_pos()
    grid_x = mouse_x // TILE_SIZE
    grid_y = mouse_y // TILE_SIZE

    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
        current_value = grid[grid_x][grid_y]
        if current_value == 0:
            grid[grid_x][grid_y] = 6
        elif current_value == 6:
            grid[grid_x][grid_y] = 11
            numWarps += 1
            grid[grid_x][grid_y] *= numWarps
        else:
            if current_value % 11 == 0:
                numWarps -= 1
            grid[grid_x][grid_y] = 0

def renumber_warps():
    warps = []
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if grid[x][y] >= 11 and grid[x][y] <= 99 and grid[x][y] % 11 == 0:
                warps.append((x, y, grid[x][y]))

    warps.sort(key=lambda w: w[2])  # Sort by warp number
    for i, (x, y, _) in enumerate(warps):
        grid[x][y] = 11 * (i + 1)  # Renumber warps sequentially

def main():
    global GRID_WIDTH, GRID_HEIGHT, grid

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    handle_mouse_click()
                elif event.button == 3:  # Right click
                    makeWarp()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if GRID_HEIGHT > 1:
                        GRID_HEIGHT -= 1
                        grid = initialize_grid()
                elif event.key == pygame.K_DOWN:
                    GRID_HEIGHT += 1
                    grid = initialize_grid()
                elif event.key == pygame.K_LEFT:
                    if GRID_WIDTH > 1:
                        GRID_WIDTH -= 1
                        grid = initialize_grid()
                elif event.key == pygame.K_RIGHT:
                    GRID_WIDTH += 1
                    grid = initialize_grid()
                elif event.key == pygame.K_s:
                    save_grid_to_file()

        screen.fill(WHITE)

        draw_grid()

        pygame.display.flip()

        clock.tick(30)

if __name__ == "__main__":
    main()