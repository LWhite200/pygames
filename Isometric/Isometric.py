import pygame
import os
import worldMap

# Initialize pygame
pygame.init()

# Set up the window size
WINDOW_SIZE = (1080, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Tile Map")

tile_size = 120

# Player properties
player_pos = [3, 3]  # [x, y]
player_image_path = "grid Maker/tiles/player.png"
player_speed = 1

def load_player_image():
    if os.path.exists(player_image_path):
        player_image = pygame.image.load(player_image_path).convert_alpha()
        # Resize player image to fit the tile size
        player_image = pygame.transform.scale(player_image, (tile_size, tile_size))
        return player_image
    else:
        player_surface = pygame.Surface((tile_size, tile_size))
        player_surface.fill((255, 0, 0))
        return player_surface

def load_tile_images(map_data):
    tile_images = {}
    for row in map_data:
        for tile in row:
            tile_number = ''.join([char for char in tile if char.isdigit()])
            if tile_number not in tile_images:
                tile_image_path = f"grid Maker/tiles/{tile_number}.png"
                if os.path.exists(tile_image_path):
                    tile_image = pygame.image.load(tile_image_path).convert_alpha()
                    tile_image = pygame.transform.scale(tile_image, (tile_size, tile_size))
                    tile_images[tile_number] = tile_image
                else:
                    color = (0, 200, 100)
                    tile_surface = pygame.Surface((tile_size, tile_size))
                    tile_surface.fill(color)
                    tile_images[tile_number] = tile_surface
    return tile_images

def draw_map(map_data, player_pos, camera_offset, tile_images):
    start_x = max(0, int(camera_offset[0]))
    start_y = max(0, int(camera_offset[1]))
    end_x = min(len(map_data[0]), int(camera_offset[0] + WINDOW_SIZE[0] / tile_size + 1))
    end_y = min(len(map_data), int(camera_offset[1] + WINDOW_SIZE[1] / tile_size + 1))

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile = map_data[y][x]
            tile_number = ''.join([char for char in tile if char.isdigit()])
            tile_image = tile_images.get(tile_number, None)
            if tile_image:
                screen.blit(tile_image, ((x - camera_offset[0]) * tile_size, (y - camera_offset[1]) * tile_size))

    player_image = load_player_image()
    screen.blit(player_image, ((player_pos[0] - camera_offset[0]) * tile_size, (player_pos[1] - camera_offset[1]) * tile_size))

def main():
    global player_pos

    map_data = worldMap.getMap("start")
    player_pos[0], player_pos[1] = worldMap.getCoordinates("startDoor")  # [x, y]
    curMap = "start"

    tile_images = load_tile_images(map_data)

    camera_pos = [player_pos[0] - (WINDOW_SIZE[0] // (2 * tile_size)), player_pos[1] - (WINDOW_SIZE[1] // (2 * tile_size))]  # [x, y]

    movement_cooldown = 200  # Reduced cooldown for smoother movement
    last_move_time = pygame.time.get_ticks()

    teleporting = False  # Variable to control teleportation state
    teleport_time = 0    # Time when teleportation started
    fade_alpha = 0      # Alpha value for fade (0 is transparent, 255 is opaque)
    fade_duration = 500  # Fade duration in milliseconds
    hold_duration = 500  # Duration to hold black screen after fading
    fade_direction = 1   # 1 for fade-in, -1 for fade-out

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if current_time - last_move_time >= movement_cooldown and not teleporting:
            newX, newY = player_pos[0], player_pos[1]  # [x, y]

            if keys[pygame.K_w]:
                if player_pos[1] > 0:
                    newY -= 1
            if keys[pygame.K_s]:
                if player_pos[1] < len(map_data) - 1:
                    newY += 1
            if keys[pygame.K_a]:
                if player_pos[0] > 0:
                    newX -= 1
            if keys[pygame.K_d]:
                if player_pos[0] < len(map_data[0]) - 1:
                    newX += 1

            if newX != player_pos[0] or newY != player_pos[1]:
                if 'd' in map_data[newY][newX]:
                    curDoor = worldMap.getCurDoorName(newX, newY)  # The name of the door we are going to
                    nextDoor = worldMap.getNextDoorName(curDoor)
                    mapName = worldMap.getMapNameFromDoor(nextDoor)

                    if not(curDoor == nextDoor and mapName == curMap):
                        curMap = mapName
                        # Update the map to be the map of the area we are traveling to
                        map_data = worldMap.getMap(mapName)

                        player_pos[0], player_pos[1] = worldMap.getCoordinates(nextDoor)  # Put the player on the door we traveled to
                        
                        teleporting = True  # Start the teleportation effect
                        teleport_time = current_time  # Record the start time
                        fade_alpha = 0  # Reset fade
                        fade_direction = 1  # Start with fade-in (alpha increasing)
                        tile_images = load_tile_images(map_data)  # Reload tile images for the new map
                        last_move_time = current_time
                    else:
                        player_pos[0], player_pos[1] = newX, newY
                        last_move_time = current_time
                elif 's' not in map_data[newY][newX] and 'w' not in map_data[newY][newX]:
                    player_pos[0], player_pos[1] = newX, newY
                    last_move_time = current_time

        # Update camera position to follow the player smoothly
        target_camera_x = player_pos[0] - (WINDOW_SIZE[0] // (2 * tile_size))
        target_camera_y = player_pos[1] - (WINDOW_SIZE[1] // (2 * tile_size))
        camera_pos[0] += (target_camera_x - camera_pos[0]) * 0.01
        camera_pos[1] += (target_camera_y - camera_pos[1]) * 0.01

        # If teleporting, create a smooth transition to black and back
        if teleporting:
            # Fade to black (fade-in)
            if fade_direction == 1:  
                if current_time - teleport_time < fade_duration:
                    fade_alpha = int(255 * (current_time - teleport_time) / fade_duration)  # Gradually increase alpha
                else:
                    fade_alpha = 255  # Reach full black
                    fade_direction = -1  # Start fading out (fade-out)
                    teleport_time = current_time  # Reset teleport time for fade-out

            # Fade out (return to normal)
            elif fade_direction == -1:
                if current_time - teleport_time < fade_duration:
                    fade_alpha = 255 - int(255 * (current_time - teleport_time) / fade_duration)  # Gradually decrease alpha
                else:
                    fade_alpha = 0  # Fully transparent, teleportation complete
                    teleporting = False  # End the teleportation effect

        # Draw the fade effect (if teleporting)
        if teleporting:
            screen.fill((0, 0, 0))  # Fill with black
            surface = pygame.Surface(WINDOW_SIZE)
            surface.set_alpha(fade_alpha)  # Apply alpha to create the fade effect
            surface.fill((255, 255, 255))  # Black color
            screen.blit(surface, (0, 0))  # Blit the fade surface onto the screen

        # If not teleporting, draw the map
        if not teleporting:
            draw_map(map_data, player_pos, camera_pos, tile_images)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
