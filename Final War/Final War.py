" Working on overworld right now do not freak out "

import pygame # type: ignore
import random

pygame.init()

width, height = 1000, 600
wth, hth = (width // 100) * 3, (height // 100) * 3
wD = 50 
tileSize = wD - 2

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Final War')
clock = pygame.time.Clock()

world = [[0 for _ in range(hth)] for _ in range(wth)]
wObj = [[None for _ in range(hth)] for _ in range(wth)]
curTurn = 0

font = pygame.font.Font('font/Pixeltype.ttf', 80)

background = pygame.Surface((width, height))
background.fill('Cyan')

camera_x, camera_y = 0, 0
camera_speed = 5  

def updateBoard():
    screen.blit(background, (0, 0))
    
    for i in range(wth):
        for j in range(hth):
            color = "Blue" if world[i][j] == 0 else "Red" if world[i][j] == 1 else "White"
            pygame.draw.rect(screen, color, pygame.Rect((i * wD) - camera_x, (j * wD) - camera_y, tileSize, tileSize))

    for player in PlayerObjs:
        # Calculate the new positions considering the camera offset
        player_rect = player.rect.move(-camera_x, -camera_y)  # Apply the camera offset here
        screen.blit(player.surface, player_rect.topleft)

    for enemy in EnemyObjs:
        # Calculate the new positions considering the camera offset
        enemy_rect = enemy.rect.move(-camera_x, -camera_y)  # Apply the camera offset here
        screen.blit(enemy.surface, enemy_rect.topleft)
    
    scoreText = "Turn: " + str(curTurn)
    score_surf = font.render(scoreText, False, (254, 254, 254))
    score_rect = score_surf.get_rect(center=(500, 550))
    screen.blit(score_surf, score_rect)

PlayerObjs = []
class playObj:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.surface = pygame.Surface((25, 25))
        self.surface.fill('Orange')
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))

EnemyObjs = []
class enemObj:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.surface = pygame.Surface((25, 25))
        self.surface.fill('Purple')
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))

def updateObjs():
    for i in range(wth):
        for j in range(hth):
            world[i][j] = 0 
            wObj[i][j] = None

    for player in PlayerObjs:
        playX = player.rect.x // wD
        playY = player.rect.y // wD
        wObj[playX][playY] = player

    for enemy in EnemyObjs:
        enemX = enemy.rect.x // wD
        enemY = enemy.rect.y // wD
        wObj[enemX][enemY] = enemy


def reset():
    global PlayerObjs, EnemyObjs
    PlayerObjs, EnemyObjs = [], []

    PlayerObjs.append(playObj(400, 200))
    PlayerObjs.append(playObj(400, 300))
    PlayerObjs.append(playObj(400, 400))

    EnemyObjs.append(enemObj(600, 200))
    EnemyObjs.append(enemObj(600, 300))
    EnemyObjs.append(enemObj(600, 400))
    updateObjs()

dragging_player = None
drag_offset_x = 0
drag_offset_y = 0
original_x = 0
original_y = 0


start_pos = None
end_pos = None

reset()
updateBoard()

playerAttacking = None
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  
                mouse_x, mouse_y = event.pos
                mouse_x += camera_x
                mouse_y += camera_y
                grid_x = mouse_x // wD 
                grid_y = mouse_y // wD
                
                if 0 <= grid_x < wth and 0 <= grid_y < hth and wObj[grid_x][grid_y]:
                    if start_pos is None:
                        start_pos = (grid_x, grid_y)
                        world[grid_x][grid_y] = 1  
                    elif end_pos is None:  
                        end_pos = (grid_x, grid_y)
                        world[grid_x][grid_y] = 1
                    else:
                        end_pos = None
                        start_pos = (grid_x, grid_y)
                        world[grid_x][grid_y] = 1  

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        camera_x -= camera_speed
    if keys[pygame.K_RIGHT]:
        camera_x += camera_speed
    if keys[pygame.K_UP]:
        camera_y -= camera_speed
    if keys[pygame.K_DOWN]:
        camera_y += camera_speed

    updateBoard()

    if start_pos:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x += camera_x
        mouse_y += camera_y
        grid_x = mouse_x // wD 
        grid_y = mouse_y // wD

        if start_pos and end_pos:

            pygame.draw.line(screen, (255, 0, 0), 
                             (start_pos[0] * wD + wD // 2 - camera_x, start_pos[1] * wD + wD // 2 - camera_y),
                             (end_pos[0] * wD + wD // 2 - camera_x, end_pos[1] * wD + wD // 2 - camera_y))
            # (grid_x * wD + wD // 2 - camera_x, grid_y * wD + wD // 2 - camera_y), 5)

    pygame.display.update()
    clock.tick(60)
