import pygame # type: ignore
import os
import worldMap

# Initialize pygame
pygame.init()

# Set up the window size
WINDOW_SIZE = (1080, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Tile Map")

tile_size = 64

# Player properties
player_pos = [3, 3]  # [x, y]
player_speed = 1

# Directions
DIRECTIONS = {
    'UP': 'up',
    'DOWN': 'down',
    'LEFT': 'left',
    'RIGHT': 'right',
}

# Player sprite paths for walking animation (multiple frames for each direction)
player_sprites = {
    'up': ["grid Maker/tiles/player/up1.png", "grid Maker/tiles/player/up2.png", "grid Maker/tiles/player/up3.png"],
    'down': ["grid Maker/tiles/player/down1.png", "grid Maker/tiles/player/down2.png", "grid Maker/tiles/player/down3.png"],
    'left': ["grid Maker/tiles/player/left1.png", "grid Maker/tiles/player/left2.png", "grid Maker/tiles/player/left3.png"],
    'right': ["grid Maker/tiles/player/right1.png", "grid Maker/tiles/player/right2.png", "grid Maker/tiles/player/right3.png"]
}

current_direction = DIRECTIONS['DOWN']  # Default facing direction

# Animation control
animation_frame = 0
animation_speed = 150  # Milliseconds between frame changes
last_animation_time = pygame.time.get_ticks()  # Initialize here to avoid referencing before assignment
is_moving = False  # Track if the player is moving

def load_person_image(person_id, direction):

    direction = direction.upper()
    if direction not in ["L", "U", "D", "R"]:
        direction = "D"

    tile_image_path = f"grid Maker/tiles/{person_id}_{direction}.png"
    if os.path.exists(tile_image_path):
        tile_image = pygame.image.load(tile_image_path).convert_alpha()
        tile_image = pygame.transform.scale(tile_image, (tile_size, tile_size))
    else:
        # Placeholder image if person image is missing
        color = (0, 200, 100)
        tile_surface = pygame.Surface((tile_size, tile_size))
        tile_surface.fill(color)
        tile_image = tile_surface
    return tile_image



def load_player_image(direction):
    global animation_frame, last_animation_time, is_moving
    current_time = pygame.time.get_ticks()
    
    # Update the frame if enough time has passed and the player is moving
    if is_moving and current_time - last_animation_time >= animation_speed:
        animation_frame = (animation_frame + 1) % len(player_sprites[direction])  # Cycle through frames
        last_animation_time = current_time
    elif not is_moving:
        animation_frame = 0  # Reset to the first frame when not moving

    player_image_path = player_sprites.get(direction, player_sprites['down'])[animation_frame]  # Get current frame for direction
    if os.path.exists(player_image_path):
        player_image = pygame.image.load(player_image_path).convert_alpha()
        # Resize player image to fit the tile size
        player_image = pygame.transform.scale(player_image, (tile_size, tile_size))
        return player_image
    else:
        player_surface = pygame.Surface((tile_size, tile_size))
        player_surface.fill((255, 0, 0))  # Red square if image is missing
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

def draw_map(map_data, player_pos, camera_offset, tile_images, direction):
    start_x = max(0, int(camera_offset[0]))
    start_y = max(0, int(camera_offset[1]))
    end_x = min(len(map_data[0]), int(camera_offset[0] + WINDOW_SIZE[0] / tile_size + 1))
    end_y = min(len(map_data), int(camera_offset[1] + WINDOW_SIZE[1] / tile_size + 1))

    player_image = load_player_image(direction)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile = map_data[y][x]
            tile_number = ''.join([char for char in tile if char.isdigit()])
            tile_image = tile_images.get(tile_number, None)


            if tile_image:
                screen.blit(tile_image, ((x - camera_offset[0]) * tile_size, (y - camera_offset[1]) * tile_size))

            if worldMap.checkForPerson(x, y):
                person_id = worldMap.get_person_id(x,y)
                personDirection = worldMap.get_person_direction(x,y)

                person_image = load_person_image(person_id, personDirection)
                screen.blit(person_image, ((x - camera_offset[0]) * tile_size, (y - camera_offset[1]) * tile_size))

    # Get the current player image based on direction
    
    screen.blit(player_image, ((player_pos[0] - camera_offset[0]) * tile_size, (player_pos[1] - camera_offset[1]) * tile_size))

def main():
    global player_pos, current_direction, is_moving

    map_data = worldMap.getMap("start")
    player_pos[0], player_pos[1] = worldMap.getCoordinates("startDoor")  # [x, y]
    curMap = "start"

    target_pos = player_pos.copy()  # Add a target position
    player_speed = 0.0075  # Adjust speed here

    tile_images = load_tile_images(map_data)

    camera_pos = [player_pos[0] - (WINDOW_SIZE[0] // (2 * tile_size)), player_pos[1] - (WINDOW_SIZE[1] // (2 * tile_size))]  # [x, y]

    movement_cooldown = 200  # Milliseconds between moves (cooldown)
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

        # Movement Logic
        if player_pos != target_pos:
            direction_x = target_pos[0] - player_pos[0]
            direction_y = target_pos[1] - player_pos[1]

            # Normalize the direction vector to move in the correct direction
            distance = (direction_x**2 + direction_y**2) ** 0.5
            if distance != 0:
                direction_x /= distance
                direction_y /= distance

            # Move the player towards the target
            player_pos[0] += direction_x * player_speed
            player_pos[1] += direction_y * player_speed

            # Stop the movement once the player reaches the target
            if abs(player_pos[0] - target_pos[0]) < 0.1 and abs(player_pos[1] - target_pos[1]) < 0.1:
                player_pos = target_pos.copy()

                
        elif current_time - last_move_time >= movement_cooldown and not teleporting:
            newX, newY = player_pos[0], player_pos[1]  # [x, y]
            is_moving = False  # Assume the player is not moving initially

           
            if keys[pygame.K_a]:
                if player_pos[0] > 0:
                    newX -= 1
                    current_direction = DIRECTIONS['LEFT']
                    is_moving = True
            if keys[pygame.K_d]:
                if player_pos[0] < len(map_data[0]) - 1:
                    newX += 1
                    current_direction = DIRECTIONS['RIGHT']
                    is_moving = True
            if keys[pygame.K_w]:
                if player_pos[1] > 0:
                    newY -= 1
                    current_direction = DIRECTIONS['UP']
                    is_moving = True
            if keys[pygame.K_s]:
                if player_pos[1] < len(map_data) - 1:
                    newY += 1
                    current_direction = DIRECTIONS['DOWN']
                    is_moving = True

            if (newX != player_pos[0] or newY != player_pos[1]) and not worldMap.checkForPerson(newX, newY):

                if 'd' in map_data[int(newY)][int(newX)]:
                    curDoor = worldMap.getCurDoorName(newX, newY)  # The name of the door we are going to
                    nextDoor = worldMap.getNextDoorName(curDoor)
                    mapName = worldMap.getMapNameFromDoor(nextDoor)

                    if not(curDoor == nextDoor and mapName == curMap):
                        curMap = mapName
                        # Update the map to be the map of the area we are traveling to
                        map_data = worldMap.getMap(mapName)

                        player_pos[0], player_pos[1] = worldMap.getCoordinates(nextDoor)  # Put the player on the door we traveled to
                        target_pos = player_pos.copy()

                        teleporting = True  # Start the teleportation effect
                        teleport_time = current_time  # Record the start time
                        fade_alpha = 0  # Reset fade
                        fade_direction = 1  # Start with fade-in (alpha increasing)
                        tile_images = load_tile_images(map_data)  # Reload tile images for the new map
                        last_move_time = current_time
                    else:
                        target_pos = [int(newX), int(newY)]
                        last_move_time = current_time
                elif 's' not in map_data[int(newY)][int(newX)] and 'w' not in map_data[int(newY)][int(newX)]:
                    target_pos = [int(newX), int(newY)]
                    last_move_time = current_time


        

        # Update camera position to follow the player smoothly
        target_camera_x = player_pos[0] - (WINDOW_SIZE[0] // (2 * tile_size))
        target_camera_y = player_pos[1] - (WINDOW_SIZE[1] // (2 * tile_size))
        camera_pos[0] += (target_camera_x - camera_pos[0]) * 0.025
        camera_pos[1] += (target_camera_y - camera_pos[1]) * 0.025

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
            surface.fill((100, 100, 255))  # Black color
            screen.blit(surface, (0, 0))  # Blit the fade surface onto the screen

        # If not teleporting, draw the map
        if not teleporting:
            draw_map(map_data, player_pos, camera_pos, tile_images, current_direction)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
