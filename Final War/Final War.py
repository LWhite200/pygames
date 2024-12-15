from collections import deque
import pygame  # type: ignore
import random
pygame.init()

width, height = 1000, 600
wth, hth = (height // 100) * 2, (width // 100) * 2
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Final War')
clock = pygame.time.Clock()

world = [[0 for _ in range(wth)] for _ in range(hth)]  # 0: red enemy, 1: blue player, 2: white being dragged, 3: Magenta can be placed
wObj = [[None for _ in range(wth)] for _ in range(hth)]
worldScore = [0, 0]
curTurn = 0

font = pygame.font.Font('font/Pixeltype.ttf', 80)

background = pygame.Surface((width, height))
background.fill('Black')
background_rect = background.get_rect(center=(width // 2, height // 2))

# ------------------------------------------------------
# ------------------------------------------------------

PlayerObjs = []
class playObj:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.surface = pygame.Surface((25, 25))
        self.surface.fill('Orange')
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))
        self.hasMoved = False
        self.doneAttack = False
        self.inRange = False
        self.isAttacking = False
        self.maxHP = 100
        self.curHP = 100

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

EnemyObjs = []
class enemObj:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.surface = pygame.Surface((25, 25))
        self.surface.fill('Purple')
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))
        self.canBeAttacked = False
        self.maxHP = 100
        self.curHP = 100

    def moveRandom(self):
        xx, yy = self.x // 50, self.y // 50
        ranStep = random.randint(1, 4)
        if ranStep == 1 and self.x >= 50 and not wObj[xx - 1][yy]:
            wObj[xx][yy] = None
            wObj[xx - 1][yy] = self
            self.x -= 50
        elif ranStep == 2 and self.x < width - 50 and not wObj[xx + 1][yy]:
            wObj[xx][yy] = None
            wObj[xx + 1][yy] = self
            self.x += 50
        elif ranStep == 3 and self.y < height - 50 and not wObj[xx][yy + 1]:
            wObj[xx][yy] = None
            wObj[xx][yy + 1] = self
            self.y += 50
        elif ranStep == 4 and self.y >= 50 and not wObj[xx][yy - 1]:
            wObj[xx][yy] = None
            wObj[xx][yy - 1] = self
            self.y -= 50
        self.rect.topleft = (self.x, self.y)

    def attackPlayer(self):

        directions = [
            (-50, 0), (50, 0), (0, -50), (0, 50), 
            (-50, -50), (50, -50), (-50, 50), (50, 50) ]

        for dx, dy in directions:
            adj_x = (self.x + dx) // 50
            adj_y = (self.y + dy) // 50

            if 0 <= adj_x < hth and 0 <= adj_y < wth:
                adjObj = wObj[adj_x][adj_y]
                if isinstance(adjObj, playObj):
                    print(f"Enemy at ({self.x},{self.y}) attacking player at ({adjObj.x},{adjObj.y})")
                    adjObj.curHP -= 50

                    if adjObj.curHP <= 0:
                        PlayerObjs.remove(adjObj)
                        updateBoard()
                        break
                    break

PlayerObjs.append(playObj(400, 200))
PlayerObjs.append(playObj(400, 300))
PlayerObjs.append(playObj(400, 400))
EnemyObjs.append(enemObj(550, 200))
EnemyObjs.append(enemObj(550, 300))
EnemyObjs.append(enemObj(550, 400))

dragging_player = None
drag_offset_x = 0
drag_offset_y = 0
original_x = 0
original_y = 0

def updateBoard():
    
    q = deque()
    visit = [[False for _ in range(wth)] for _ in range(hth)]
    worldScore[0], worldScore[1] = 0, 0

    for i in range(hth):
        for j in range(wth):
            world[i][j] = 0 
            wObj[i][j] = None

    for player in PlayerObjs:
        playX = player.rect.x // 50
        playY = player.rect.y // 50
        q.append((playX, playY))
        world[playX][playY] = 1
        visit[playX][playY] = True
        worldScore[world[playX][playY]] += 1
        wObj[playX][playY] = player

    for enemy in EnemyObjs:
        enemX = enemy.rect.x // 50
        enemY = enemy.rect.y // 50
        q.append((enemX, enemY))
        world[enemX][enemY] = 0
        visit[enemX][enemY] = True
        worldScore[world[enemX][enemY]] += 1
        wObj[enemX][enemY] = enemy

    while q:
        px, py = q.popleft()
        color = world[px][py]

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = px + dx, py + dy

            if 0 <= nx < hth and 0 <= ny < wth and not visit[nx][ny]:
                visit[nx][ny] = True
                world[nx][ny] = color
                q.append((nx, ny))
                worldScore[color] += 1

updateBoard()

# ------------------------------------------------------
# ------------------------------------------------------

playerAttacking = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            for enemy in EnemyObjs:
                enemy.moveRandom()
                enemy.attackPlayer()
                enemy.canBeAttacked = False

            for player in PlayerObjs:
                player.hasMoved = False
                player.doneAttack = False
                player.isAttacking = False
                player.inRange = False  # Reset the range flag

            playerAttacking = None
            curTurn += 1
            updateBoard()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                for player in PlayerObjs:
                    if player.rect.collidepoint(event.pos) and not player.hasMoved:  
                        dragging_player = player
                        original_x, original_y = player.x, player.y
                        drag_offset_x = player.rect.x - event.pos[0]
                        drag_offset_y = player.rect.y - event.pos[1]
                        break
            elif event.button == 3:  
                for player in PlayerObjs:
                    if player.rect.collidepoint(event.pos) and not player.doneAttack and player.inRange:  
                        player.isAttacking = True
                        playerAttacking = player  
                    else:
                        player.isAttacking = False

                for enemy in EnemyObjs:
                    if enemy.rect.collidepoint(event.pos) and playerAttacking:  
                        if abs(playerAttacking.x - enemy.x) <= 50 and abs(playerAttacking.y - enemy.y) <= 50:
                            print("Enemy Was Attacked Successfully")
                            enemy.curHP -= 50
                            playerAttacking.doneAttack = True 
                            playerAttacking.hasMoved = True
                            playerAttacking.isAttacking = False
                            playerAttacking = None

                            if enemy.curHP <= 0:
                                EnemyObjs.remove(enemy)
                                updateBoard()
                                break
      

                        break

        if event.type == pygame.MOUSEMOTION: 
            if dragging_player:
                mouse_x, mouse_y = event.pos
                new_x = mouse_x + drag_offset_x
                new_y = mouse_y + drag_offset_y
                new_x = (new_x // 50) * 50
                new_y = (new_y // 50) * 50

                max_dist = 3  # Movement distance limit
                if abs(new_x - original_x) > max_dist * 50:
                    new_x = original_x + max_dist * 50 if new_x > original_x else original_x - max_dist * 50
                if abs(new_y - original_y) > max_dist * 50:
                    new_y = original_y + max_dist * 50 if new_y > original_y else original_y - max_dist * 50

                dragging_player.rect.topleft = (new_x, new_y)

                for dx in range(-max_dist, max_dist + 1):
                    for dy in range(-max_dist, max_dist + 1):
                        if 0 <= (original_x // 50 + dx) < hth and 0 <= (original_y // 50 + dy) < wth:
                            if abs(dx) <= max_dist and abs(dy) <= max_dist:
                                if (dx == 0 and dy == 0):
                                    world[(original_x // 50) + dx][(original_y // 50) + dy] = 2
                                else:
                                    world[(original_x // 50) + dx][(original_y // 50) + dy] = 3
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and dragging_player:
                if dragging_player:
                    new_x = dragging_player.rect.x // 50
                    new_y = dragging_player.rect.y // 50
                    for i, player in enumerate(PlayerObjs):
                        if player == dragging_player:
                            PlayerObjs[i].x = new_x * 50
                            PlayerObjs[i].y = new_y * 50
                            PlayerObjs[i].hasMoved = True
                            PlayerObjs[i].isAttacking = False
                            PlayerObjs[i].inRange = False
                            break
                updateBoard()
                dragging_player = None

    screen.blit(background, background_rect)

    # World Grid display
    for i in range(0, hth):
        for j in range(0, wth):
            color = "Red" if world[i][j] == 0 else "Blue" if world[i][j] == 1 else "White" if world[i][j] == 2 else "Magenta"
            pygame.draw.rect(screen, color, pygame.Rect(i * 50, j * 50, 25, 25))

    # Enemy
    for enemy in EnemyObjs:
        screen.blit(enemy.surface, enemy.rect)
        if enemy.canBeAttacked:
            color = "White"
            nm_surf = pygame.Surface((12, 12))
            nm_surf.fill(color)
            nm_rect = nm_surf.get_rect(center=enemy.rect.center)
            screen.blit(nm_surf, nm_rect)

        enemy.canBeAttacked = False

    for player in PlayerObjs:
        player.canAttack = False
        surrounding_positions = [
            (-50, 0), (50, 0), (0, -50), (0, 50), 
            (-50, -50), (50, -50), (-50, 50), (50, 50) 
        ]
        
        for dx, dy in surrounding_positions:
            adjacent_x = (player.x + dx) // 50
            adjacent_y = (player.y + dy) // 50

            if 0 <= adjacent_x < hth and 0 <= adjacent_y < wth:
                obj = wObj[adjacent_x][adjacent_y]
                if isinstance(obj, enemObj):  
                    player.inRange = True
                    if not player.doneAttack:
                        obj.canBeAttacked = True

        screen.blit(player.surface, player.rect)
        if not player.hasMoved or (player.inRange and not player.doneAttack) or (player.inRange and player.isAttacking):
            color = "Red" if player.isAttacking else "White"
            nm_surf = pygame.Surface((12, 12))
            nm_surf.fill(color)
            nm_rect = nm_surf.get_rect(center=player.rect.center)
            screen.blit(nm_surf, nm_rect)

    scoreText = str("Turn  " + str(curTurn) + "     Score  " + str(worldScore[1]) + "  :  " + str(worldScore[0]))
    score_surf = font.render(scoreText, False, (254, 254, 254))
    score_rect = score_surf.get_rect(center=(500, 550))
    screen.blit(score_surf, score_rect)

    pygame.display.update()
    clock.tick(60)
