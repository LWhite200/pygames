import pygame  # type: ignore
import os
import random
import worldMap  # Assuming worldMap.py is in the same directory

# Initialize pygame
pygame.init()

# Set up the window size
WINDOW_SIZE = (1080, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Tile Map")

# Load the 2D array from the worldMap.py file
tile_size = 120  # Size of each tile (you can adjust it)

# Player properties
player_pos = [3, 3]  # Initial position of the player on the map (row, col)
player_image_path = "grid Maker/tiles/player.png"  # Path to the player's image
player_speed = 1  # Player movement speed (tiles per frame)

# Load player image
def load_player_image():
    if os.path.exists(player_image_path):
        player_image = pygame.image.load(player_image_path).convert_alpha()
        # Resize player image to fit the tile size
        player_image = pygame.transform.scale(player_image, (tile_size, tile_size))
        return player_image
    else:
        # If the player image doesn't exist, use a red square as placeholder
        player_surface = pygame.Surface((tile_size, tile_size))
        player_surface.fill((255, 0, 0))  # Red color
        return player_surface

# Load tile images
def load_tile_image(tile):
    tile_number = ''.join([char for char in tile if char.isdigit()])
    tile_image_path = f"grid Maker/tiles/{tile_number}.png"
    
    if os.path.exists(tile_image_path):
        tile_image = pygame.image.load(tile_image_path).convert_alpha()
        tile_image = pygame.transform.scale(tile_image, (tile_size, tile_size))
        return tile_image
    else:
        color = (random.randint(0, 100), random.randint(200, 255), random.randint(0, 100))
        tile_surface = pygame.Surface((tile_size, tile_size))
        tile_surface.fill(color)
        return tile_surface

# Draw the map and the player
def draw_map(map_data, player_pos):
    # Draw the map tiles
    for y, row in enumerate(map_data):
        for x, tile in enumerate(row):
            tile_image = load_tile_image(tile)
            screen.blit(tile_image, (x * tile_size, y * tile_size))
    
    # Draw the player character
    player_image = load_player_image()
    screen.blit(player_image, (player_pos[1] * tile_size, player_pos[0] * tile_size))

# Main game loop
def main():
    global player_pos
    
    # Get the map data (2D array)
    map_data = worldMap.getMap("start")  # Assuming this returns a 2D list like ['33f', '44w', ...]

    running = True
    while running:
        screen.fill((0, 0, 0))  # Fill screen with black background
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Key press events to move the player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:  # Move up (W)
            if player_pos[0] > 0:
                player_pos[0] -= player_speed
        if keys[pygame.K_s]:  # Move down (S)
            if player_pos[0] < len(map_data) - 1:
                player_pos[0] += player_speed
        if keys[pygame.K_a]:  # Move left (A)
            if player_pos[1] > 0:
                player_pos[1] -= player_speed
        if keys[pygame.K_d]:  # Move right (D)
            if player_pos[1] < len(map_data[0]) - 1:
                player_pos[1] += player_speed
        
        # Draw the map and player
        draw_map(map_data, player_pos)
        
        pygame.display.flip()  # Update the screen

    pygame.quit()

if __name__ == "__main__":
    main()
