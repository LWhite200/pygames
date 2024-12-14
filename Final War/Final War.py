import pygame
import math
pygame.init()

width, height = 1000, 600
wth, hth = (height // 100) * 2, (width // 100) * 2
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Final War')
clock = pygame.time.Clock()

world = [[0 for _ in range(wth)] for _ in range(hth)]

font = pygame.font.Font('font/Pixeltype.ttf', 50)
score_surf = font.render("", False, (64, 64, 64))
score_rect = score_surf.get_rect(center = (400, 50))

background = pygame.Surface((width, height))
background.fill('Black')
background_rect = background.get_rect(center = (400, 200))

player = pygame.Surface((25, 25))
player.fill('White')
player_rect = player.get_rect(topleft = (200, 200))

enemy = pygame.Surface((25, 25))
enemy.fill('White')
enemy_rect = enemy.get_rect(topleft = (300, 200))

def updateBoard():
    playX = player_rect.x // 50
    playY = player_rect.y // 50

    enemX = enemy_rect.x // 50
    enemY = enemy_rect.y // 50

    for i in range(hth):
        for j in range(wth):
            playDist = math.sqrt((i - playX)**2 + (j - playY)**2)
            enemDist = math.sqrt((i - enemX)**2 + (j - enemY)**2)

            if enemDist < playDist:
                world[i][j] = 0
            else:
                world[i][j] = 1

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
            if moved: updateBoard()

    screen.blit(background, background_rect)

    for i in range(0, hth):
        for j in range(0, wth):
            
            color = "Red" if world[i][j] == 0 else "Blue"
            pygame.draw.rect(screen, color, pygame.Rect(i * 50, j * 50, 25, 25))

    screen.blit(player, player_rect)
    screen.blit(enemy, enemy_rect)
    screen.blit(score_surf, score_rect)
    
    pygame.display.update()
    clock.tick(60)