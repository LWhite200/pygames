from collections import deque
import pygame # type: ignore
import math
import random
pygame.init()

width, height = 1000, 600
wth, hth = (height // 100) * 2, (width // 100) * 2
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Final War')
clock = pygame.time.Clock()

world = [[0 for _ in range(wth)] for _ in range(hth)]
worldScore = [0, 0]

font = pygame.font.Font('font/Pixeltype.ttf', 80)

background = pygame.Surface((width, height))
background.fill('Black')
background_rect = background.get_rect(center = (width // 2, height // 2))

player = pygame.Surface((25, 25))
player.fill('White')
player_rect = player.get_rect(topleft = (200, 200))

EnemyObjs = []

class enemObj:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.surface = pygame.Surface((25, 25))
        self.surface.fill('White')
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))

    def moveRandom(self):
        ranStep = random.randint(1, 4)

        if ranStep == 1 and self.x >= 50:
            self.x -= 50
        elif ranStep == 2 and self.x < width - 50:
            self.x += 50
        elif ranStep == 3 and self.y < height - 50:
            self.y += 50
        elif ranStep == 4 and self.y >= 50:
            self.y -= 50

        self.rect.topleft = (self.x, self.y)

EnemyObjs.append(enemObj(300, 200))
EnemyObjs.append(enemObj(500, 300))
EnemyObjs.append(enemObj(700, 100))

def updateBoard():
    q = deque()
    visit = [[False for _ in range(wth)] for _ in range(hth)]
    worldScore[0], worldScore[1] = 0, 0

    

    for enemy in EnemyObjs:
        enemX = enemy.rect.x // 50
        enemY = enemy.rect.y // 50
        q.append((enemX, enemY))
        world[enemX][enemY] = 0  # Mark enemy positions as 0 initially
        visit[enemX][enemY] = True
        worldScore[world[enemX][enemY]] += 1

    playX = player_rect.x // 50
    playY = player_rect.y // 50
    q.append((playX, playY))
    world[playX][playY] = 1  # Player's starting position
    visit[playX][playY] = True
    worldScore[world[playX][playY]] += 1

    while q:
        px, py = q.popleft()
        color = world[px][py]

        # Explore the 4 possible directions (up, down, left, right)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = px + dx, py + dy

            # Ensure the new position is within bounds and hasn't been visited
            if 0 <= nx < hth and 0 <= ny < wth and not visit[nx][ny]:
                visit[nx][ny] = True
                world[nx][ny] = color  # Update the board with the correct color
                q.append((nx, ny))  # Add the position to the queue for further exploration
                worldScore[color] += 1




updateBoard()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            moved = False
            if event.key == pygame.K_w:
                if player_rect.top >= 50:
                    player_rect.y -= 50
                    moved = True
            if event.key == pygame.K_s:
                if player_rect.bottom < height - 50:
                    player_rect.y += 50
                    moved = True
            if event.key == pygame.K_a:
                if player_rect.left >= 50:
                    player_rect.x -= 50
                    moved = True
            if event.key == pygame.K_d:
                if player_rect.right < width - 50:
                    player_rect.x += 50
                    moved = True
            if moved: 
                EnemyObjs[0].moveRandom()
                updateBoard() 
                

    screen.blit(background, background_rect)

    for i in range(0, hth):
        for j in range(0, wth):
            
            color = "Red" if world[i][j] == 0 else "Blue"
            pygame.draw.rect(screen, color, pygame.Rect(i * 50, j * 50, 25, 25))

    screen.blit(player, player_rect)

    for enemy in EnemyObjs:
        screen.blit(enemy.surface, enemy.rect)

    scoreText = str(str(worldScore[1]) + "  :  " + str(worldScore[0]))
    score_surf = font.render(scoreText, False, (254, 254, 254))
    score_rect = score_surf.get_rect(center = (500, 550))
    screen.blit(score_surf, score_rect)
    
    pygame.display.update()
    clock.tick(60)