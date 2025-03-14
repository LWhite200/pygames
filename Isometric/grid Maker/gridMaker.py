" Features Needed: "
" Loading maps from text file "
" Stop deleting maps when changing size "
" Size of cursor/how many blocks places "
" Visual to show what type a tile is on the main grid "

import pygame
import sys
import tkinter as tk
from tkinter import simpledialog
import os

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
BLUE = (0, 0, 255)  # s 

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

# Load tile images
tile_images = {}
tiles_folder = "tiles"
if os.path.exists(tiles_folder):
    for filename in os.listdir(tiles_folder):
        if filename.endswith(".png"):
            tile_number = filename.split(".")[0]
            try:
                tile_number = int(tile_number)
                tile_images[tile_number] = pygame.image.load(os.path.join(tiles_folder, filename))
            except ValueError:
                pass  # Ignore files that don't have a numeric name

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
    """Saves the grid to a file with the specified area name in 2D array format."""
    area_name = get_area_name()
    if area_name is None:  # User canceled the input
        print("Save canceled.")
        return

    filename = f"{area_name}.txt"

    try:
        with open(filename, 'w') as f:
            f.write(f"{area_name} = [\n")  # Use the area name as the variable name
            for y in range(GRID_HEIGHT):
                row = []
                for x in range(GRID_WIDTH):
                    tile_data = grid[x][y]
                    tile_number = tile_data["tile"][:-1]  # Remove the option character
                    tile_option = tile_data["tile"][-1]  # Get the option character (f, w, d, z)
                    object_data = tile_data["object"]
                    metadata = tile_data["metadata"]

                    # Format the object field using | instead of {}
                    if tile_option == 'd':
                        door_id = metadata["door_id"]
                        place = metadata["place"]
                        place_door_id = metadata["place_door_id"]
                        object_str = f"|d|{door_id}|{place}|{place_door_id}|"
                    elif object_data == 'n':
                        object_str = "|n|"
                    elif object_data == 'p':
                        person_id = metadata["person_id"]
                        direction = metadata["direction"]
                        object_str = f"|p|{person_id}|{direction}|"
                    elif object_data == 'i':
                        item_id = metadata["item_id"]
                        num_items = metadata["num_items"]
                        object_str = f"|i|{item_id}|{num_items}|"

                    # Save the tile in the format "tile_number+tile_option+object_str"
                    row.append(f'"{tile_number}{tile_option}{object_str}"')

                # Write row as a list of strings, each one quoted
                f.write("    [" + ", ".join(row) + "],\n")

            f.write("]\n")

        print(f"Grid saved to {filename}")
    except IOError as e:
        print(f"Error saving file: {e}")





def get_tile_color(tile_value):
    """Returns the color based on the tile's option (f, w, d, z, s)."""
    if isinstance(tile_value, str):
        option = tile_value[-1]  # Get the last character (f, w, d, z, s)
        if option == 'f':
            return GREEN
        elif option == 'w':
            return ORANGE
        elif option == 'd':
            return GRAY
        elif option == 'z':
            return RED
        elif option == 's':
            return BLUE  # New color for 's'
    return WHITE  # Default color

def draw_grid():
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            # Draw the tile background
            tile_data = grid[x][y]
            tile_color = get_tile_color(tile_data["tile"])
            pygame.draw.rect(screen, tile_color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

            # Draw the number on the tile or the tile image
            if isinstance(tile_data["tile"], str):
                number = int(tile_data["tile"][:-1])  # Remove the option character
            else:
                number = tile_data["tile"]

            if number in tile_images:
                # Scale the image to fit the tile size
                image = pygame.transform.scale(tile_images[number], (TILE_SIZE, TILE_SIZE))
                screen.blit(image, (x * TILE_SIZE, y * TILE_SIZE))
            else:
                # Draw the number on the tile
                text_surface = FONT.render(str(number), True, BLACK)
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

        # Draw the tile background
        pygame.draw.rect(screen, WHITE, (tile_x, tile_y, 25, 25))
        pygame.draw.rect(screen, BLACK, (tile_x, tile_y, 25, 25), 2)

        # If an image exists for this tile number, draw it
        if i in tile_images:
            image = pygame.transform.scale(tile_images[i], (25, 25))  # Scale the image to fit the panel
            screen.blit(image, (tile_x, tile_y))
        else:
            # Otherwise, draw the number on the tile
            text_surface = FONT.render(str(i), True, BLACK)
            text_rect = text_surface.get_rect(center=(tile_x + 12, tile_y + 12))
            screen.blit(text_surface, text_rect)

        # Highlight the selected tile
        if i == selected_tile:
            pygame.draw.rect(screen, (255, 0, 0), (tile_x, tile_y, 25, 25), 3)

def draw_radio_buttons():
    # Tile options (f, w, d, z, s)
    options = ['f', 'w', 'd', 'z', 's']
    panel_x = GRID_WIDTH * TILE_SIZE + 20  # Starting X position for tile options
    panel_y = 400  # Starting Y position for tile options
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
    panel_x = GRID_WIDTH * TILE_SIZE + 120  # Move object options to the right of tile options
    panel_y = 400  # Align object options with tile options vertically
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

def handle_mouse_click(processed_tiles):
    global numWarps, selected_tile, selected_option, selected_object
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Check if the click is on the main grid
    if 0 <= mouse_x < GRID_WIDTH * TILE_SIZE and 0 <= mouse_y < GRID_HEIGHT * TILE_SIZE:
        grid_x = mouse_x // TILE_SIZE
        grid_y = mouse_y // TILE_SIZE

        if (grid_x, grid_y) in processed_tiles:
            return  # Skip if this tile has already been processed during this drag

        # Check for invalid combinations
        if (selected_option == 'd' and grid[grid_x][grid_y]["object"] != 'n') or \
           (selected_object != 'n' and grid[grid_x][grid_y]["tile"][-1] == 'd'):
            return  # Cannot place a door on an object or an object on a door

        # Update the tile value and object
        grid[grid_x][grid_y]["tile"] = f"{selected_tile}{selected_option}"
        grid[grid_x][grid_y]["object"] = selected_object

        # Prompt for additional information
        if selected_option == 'd':
            grid[grid_x][grid_y]["metadata"] = prompt_door_info()
        elif selected_object == 'i':
            grid[grid_x][grid_y]["metadata"] = prompt_item_info()
        elif selected_object == 'p':
            grid[grid_x][grid_y]["metadata"] = prompt_person_info()

        processed_tiles.add((grid_x, grid_y))

    # Check if the click is on the tile panel
    elif GRID_WIDTH * TILE_SIZE + 20 <= mouse_x <= GRID_WIDTH * TILE_SIZE + 320 and 20 <= mouse_y <= 320:
        tile_x = (mouse_x - (GRID_WIDTH * TILE_SIZE + 20)) // 30
        tile_y = (mouse_y - 20) // 30
        selected_tile = tile_y * 10 + tile_x

    # Check if the click is on the tile options radio buttons
    elif GRID_WIDTH * TILE_SIZE + 20 <= mouse_x <= GRID_WIDTH * TILE_SIZE + 70 and 400 <= mouse_y <= 550:
        option_index = (mouse_y - 400) // 30
        options = ['f', 'w', 'd', 'z', 's']
        if 0 <= option_index < len(options):
            selected_option = options[option_index]
            if selected_option == 'd':
                selected_object = 'n'  # Lock object to 'n' when 'd' is selected

    # Check if the click is on the object options radio buttons
    elif GRID_WIDTH * TILE_SIZE + 120 <= mouse_x <= GRID_WIDTH * TILE_SIZE + 170 and 400 <= mouse_y <= 490:
        if selected_option != 'd':  # Only allow object selection if 'd' is not selected
            option_index = (mouse_y - 400) // 30
            object_options = ['p', 'i', 'n']
            if 0 <= option_index < len(object_options):
                selected_object = object_options[option_index]

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

            # Ensure the selected option is not for placing door (d), person (p), or item (i)
            if event.type == pygame.MOUSEMOTION:
                if mouse_dragging:
                    
                    if selected_option != 'd' and selected_object == 'n':
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