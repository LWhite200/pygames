import pygame
import sys
import tkinter as tk
from tkinter import simpledialog
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tile Grid Interaction")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 255, 50)  # f
ORANGE = (255, 165, 0)  # w
GRAY = (200, 200, 200)  # d
RED = (255, 100, 100)  # z

# Font for rendering numbers
pygame.font.init()
FONT = pygame.font.SysFont("Arial", 16)

TILE_SIZE = 15
GRID_WIDTH, GRID_HEIGHT = 30, 30

numWarps = 0  # Amount of "11 divisible"

# Initialize selected tile, option, and object type
selected_tile = 1  # Default selected tile
selected_option = 'f'  # Default selected option
selected_object = 'n'  # Default object type (none)

def initialize_grid():
    """Initialize the grid with 'f' for 1 and 'w' for 2, and no objects."""
    grid = [[{"tile": f"1f", "object": "n", "metadata": None} for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if x == 0 or x == GRID_WIDTH - 1 or y == 0 or y == GRID_HEIGHT - 1:
                grid[x][y]["tile"] = f"2w"  # Border tiles are 'w'
    return grid

grid = initialize_grid()

def get_area_name():
    """Prompts the user for the area name."""
    root = tk.Tk()
    root.withdraw()
    area_name = simpledialog.askstring("Input", "Enter the area name:", parent=root)
    root.destroy()
    return area_name

def save_grid_to_file():
    """Saves the grid to a file with the specified area name."""
    area_name = get_area_name()
    if area_name is None:  # User canceled the input
        print("Save canceled.")
        return

    filename = f"{area_name}.txt"

    try:
        with open(filename, 'w') as f:
            for y in range(GRID_HEIGHT):
                row = []
                for x in range(GRID_WIDTH):
                    tile_data = grid[x][y]
                    tile_number = tile_data["tile"][:-1]  # Remove the option character
                    tile_option = tile_data["tile"][-1]  # Get the option character (f, w, d, z)
                    object_data = tile_data["object"]
                    metadata = tile_data["metadata"]

                    # Format the object field
                    if tile_option == 'd':
                        door_id = metadata["door_id"]
                        place = metadata["place"]
                        place_door_id = metadata["place_door_id"]
                        object_str = f"{{d,{door_id},{place},{place_door_id}}}"
                    elif object_data == 'n':
                        object_str = "{n}"
                    elif object_data == 'p':
                        person_id = metadata["person_id"]
                        direction = metadata["direction"]
                        object_str = f"{{p,{person_id},{direction}}}"
                    elif object_data == 'i':
                        item_id = metadata["item_id"]
                        num_items = metadata["num_items"]
                        object_str = f"{{i,{item_id},{num_items}}}"

                    # Save the tile in the format [tile number],[f,w,z,d],[{object}]
                    row.append(f"{tile_number},{tile_option},{object_str}")
                f.write(" ".join(row) + "\n")

        print(f"Grid saved to {filename}")
    except IOError as e:
        print(f"Error saving file: {e}")

def get_tile_color(tile_value):
    """Returns the color based on the tile's option (f, w, d, z)."""
    if isinstance(tile_value, str):
        option = tile_value[-1]  # Get the last character (f, w, d, z)
        if option == 'f':
            return GREEN
        elif option == 'w':
            return ORANGE
        elif option == 'd':
            return GRAY
        elif option == 'z':
            return RED
    return WHITE  # Default color

def draw_grid():
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            # Draw the tile background
            tile_data = grid[x][y]
            tile_color = get_tile_color(tile_data["tile"])
            pygame.draw.rect(screen, tile_color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

            # Draw the number on the tile
            if isinstance(tile_data["tile"], str):
                number = tile_data["tile"][:-1]  # Remove the option character
            else:
                number = str(tile_data["tile"])
            text_surface = FONT.render(number, True, BLACK)
            text_rect = text_surface.get_rect(center=(x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2))
            screen.blit(text_surface, text_rect)

            # Draw the object (if any)
            if tile_data["object"] == 'p':  # Person (white circle)
                pygame.draw.circle(screen, WHITE, (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 3)
            elif tile_data["object"] == 'i':  # Item (black circle)
                pygame.draw.circle(screen, BLACK, (x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2), TILE_SIZE // 3)

def draw_tile_panel():
    panel_x = GRID_WIDTH * TILE_SIZE + 20
    panel_y = 20
    for i in range(100):
        tile_x = panel_x + (i % 10) * 30
        tile_y = panel_y + (i // 10) * 30
        pygame.draw.rect(screen, WHITE, (tile_x, tile_y, 25, 25))
        pygame.draw.rect(screen, BLACK, (tile_x, tile_y, 25, 25), 2)
        text_surface = FONT.render(str(i), True, BLACK)
        text_rect = text_surface.get_rect(center=(tile_x + 12, tile_y + 12))
        screen.blit(text_surface, text_rect)
        if i == selected_tile:
            pygame.draw.rect(screen, (255, 0, 0), (tile_x, tile_y, 25, 25), 3)  # Highlight selected tile

def draw_radio_buttons():
    # Tile options (f, w, d, z)
    options = ['f', 'w', 'd', 'z']
    panel_x = GRID_WIDTH * TILE_SIZE + 20
    panel_y = 400
    for i, option in enumerate(options):
        option_x = panel_x
        option_y = panel_y + i * 30
        pygame.draw.rect(screen, WHITE, (option_x, option_y, 25, 25))
        pygame.draw.rect(screen, BLACK, (option_x, option_y, 25, 25), 2)
        if option == selected_option:
            pygame.draw.circle(screen, BLACK, (option_x + 12, option_y + 12), 10)
        text_surface = FONT.render(option, True, BLACK)
        text_rect = text_surface.get_rect(center=(option_x + 40, option_y + 12))
        screen.blit(text_surface, text_rect)

    # Object options (p, i, n)
    object_options = ['p', 'i', 'n']
    panel_y = 550
    for i, option in enumerate(object_options):
        option_x = panel_x
        option_y = panel_y + i * 30
        pygame.draw.rect(screen, WHITE, (option_x, option_y, 25, 25))
        pygame.draw.rect(screen, BLACK, (option_x, option_y, 25, 25), 2)
        if option == selected_object:
            pygame.draw.circle(screen, BLACK, (option_x + 12, option_y + 12), 10)
        text_surface = FONT.render(option, True, BLACK)
        text_rect = text_surface.get_rect(center=(option_x + 40, option_y + 12))
        screen.blit(text_surface, text_rect)

def prompt_door_info():
    """Prompts the user for door information."""
    root = tk.Tk()
    root.withdraw()
    door_id = simpledialog.askstring("Input", "Enter Door ID:", parent=root)
    place = simpledialog.askstring("Input", "Enter PLACE:", parent=root)
    place_door_id = simpledialog.askstring("Input", "Enter PLACE DOOR ID:", parent=root)
    root.destroy()
    return {"door_id": door_id, "place": place, "place_door_id": place_door_id}

def prompt_item_info():
    """Prompts the user for item information."""
    root = tk.Tk()
    root.withdraw()
    item_id = simpledialog.askstring("Input", "Enter ITEM ID:", parent=root)
    num_items = simpledialog.askstring("Input", "Enter NUMBER OF ITEMS:", parent=root)
    root.destroy()
    return {"item_id": item_id, "num_items": num_items}

def prompt_person_info():
    """Prompts the user for person information."""
    root = tk.Tk()
    root.withdraw()
    person_id = simpledialog.askstring("Input", "Enter PERSON ID:", parent=root)
    direction = simpledialog.askstring("Input", "Enter DIRECTION (L, R, U, D):", parent=root)
    root.destroy()
    return {"person_id": person_id, "direction": direction}

# Add this variable to track the last click time
last_click_time = 0
CLICK_COOLDOWN = 0.2  # Minimum time in seconds between two consecutive clicks (200ms)

def handle_mouse_click(processed_tiles):
    global numWarps, selected_tile, selected_option, selected_object, last_click_time
    current_time = time.time()

    # Check if enough time has passed since the last click
    if current_time - last_click_time < CLICK_COOLDOWN:
        print("Click ignored due to cooldown.")
        return  # Ignore this click if it happens too soon after the last one

    last_click_time = current_time  # Update the last click time

    mouse_x, mouse_y = pygame.mouse.get_pos()
    print(f"Mouse clicked at: {mouse_x}, {mouse_y}")

    # Check if the click is on the main grid
    if 0 <= mouse_x < GRID_WIDTH * TILE_SIZE and 0 <= mouse_y < GRID_HEIGHT * TILE_SIZE:
        grid_x = mouse_x // TILE_SIZE
        grid_y = mouse_y // TILE_SIZE
        print(f"Clicked on grid tile: {grid_x}, {grid_y}")

        # If this tile has already been processed in this drag, skip it
        if (grid_x, grid_y) in processed_tiles:
            print(f"Tile ({grid_x}, {grid_y}) has already been processed, skipping.")
            return  # Skip if this tile has already been processed during this drag

        # Check for invalid combinations
        if (selected_option == 'd' and grid[grid_x][grid_y]["object"] != 'n') or \
           (selected_object != 'n' and grid[grid_x][grid_y]["tile"][-1] == 'd'):
            print(f"Invalid tile combination at ({grid_x}, {grid_y}), skipping.")
            return  # Cannot place a door on an object or an object on a door

        # Update the tile value and object
        grid[grid_x][grid_y]["tile"] = f"{selected_tile}{selected_option}"
        grid[grid_x][grid_y]["object"] = selected_object

        # Prevent prompting for the same tile multiple times by checking if metadata is set
        if selected_option == 'd' and grid[grid_x][grid_y]["metadata"] is None:
            print(f"Prompting for door info at ({grid_x}, {grid_y})")
            grid[grid_x][grid_y]["metadata"] = prompt_door_info()  # Prompt once for door info
        elif selected_object == 'i' and grid[grid_x][grid_y]["metadata"] is None:
            print(f"Prompting for item info at ({grid_x}, {grid_y})")
            grid[grid_x][grid_y]["metadata"] = prompt_item_info()  # Prompt once for item info
        elif selected_object == 'p' and grid[grid_x][grid_y]["metadata"] is None:
            print(f"Prompting for person info at ({grid_x}, {grid_y})")
            grid[grid_x][grid_y]["metadata"] = prompt_person_info()  # Prompt once for person info

        # Mark this tile as processed for the current drag to avoid re-triggering the prompt
        processed_tiles.add((grid_x, grid_y))
        print(f"Tile ({grid_x}, {grid_y}) added to processed_tiles.")

    # Check if the click is on the tile panel (the tile selection part of the UI)
    elif GRID_WIDTH * TILE_SIZE + 20 <= mouse_x <= GRID_WIDTH * TILE_SIZE + 320 and 20 <= mouse_y <= 320:
        tile_x = (mouse_x - (GRID_WIDTH * TILE_SIZE + 20)) // 30
        tile_y = (mouse_y - 20) // 30
        selected_tile = tile_y * 10 + tile_x  # Update selected tile
        print(f"Selected tile updated to: {selected_tile}")

    # Check if the click is on the tile options radio buttons
    elif GRID_WIDTH * TILE_SIZE + 20 <= mouse_x <= GRID_WIDTH * TILE_SIZE + 70 and 400 <= mouse_y <= 520:
        option_index = (mouse_y - 400) // 30
        options = ['f', 'w', 'd', 'z']
        if 0 <= option_index < len(options):
            selected_option = options[option_index]
            print(f"Selected option updated to: {selected_option}")
            if selected_option == 'd':
                selected_object = 'n'  # Lock object to 'n' when 'd' is selected

    # Check if the click is on the object options radio buttons
    elif GRID_WIDTH * TILE_SIZE + 20 <= mouse_x <= GRID_WIDTH * TILE_SIZE + 70 and 550 <= mouse_y <= 640:
        if selected_option != 'd':  # Only allow object selection if 'd' is not selected
            option_index = (mouse_y - 550) // 30
            object_options = ['p', 'i', 'n']
            if 0 <= option_index < len(object_options):
                selected_object = object_options[option_index]
                print(f"Selected object updated to: {selected_object}")


def main():
    global GRID_WIDTH, GRID_HEIGHT, grid

    clock = pygame.time.Clock()
    mouse_dragging = False
    processed_tiles = set()  # Tracks tiles processed during the current drag

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_dragging = True
                    processed_tiles.clear()  # Reset processed tiles at the start of a new drag
                    handle_mouse_click(processed_tiles)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left button released
                    mouse_dragging = False

            if event.type == pygame.MOUSEMOTION:
                if mouse_dragging:
                    handle_mouse_click(processed_tiles)

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
        draw_tile_panel()
        draw_radio_buttons()

        pygame.display.flip()

        clock.tick(30)

if __name__ == "__main__":
    main()