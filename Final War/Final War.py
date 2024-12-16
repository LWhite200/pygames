" Things to add: barriers, types, ranged attacks, enemy a.i."

from collections import deque
import pygame  # type: ignore
import random
pygame.init()

width, height = 1000, 600
wth, hth = (height // 100) * 2, (width // 100) * 2
wrdDiv = 50 # translate phyiscal location to world grid
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Final War')
clock = pygame.time.Clock()

world = [[0 for _ in range(wth)] for _ in range(hth)]  # 0: red enemy, 1: blue player, 2: white being dragged, 3: Magenta can be placed
wObj = [[None for _ in range(wth)] for _ in range(hth)]
worldScore = [0, 0]
curTurn = 0
toDisplayText = "The Game Has Begun"

font = pygame.font.Font('font/Pixeltype.ttf', 40)

background = pygame.Surface((width, height))
background.fill('Black')
background_rect = background.get_rect(center=(width // 2, height // 2))

# ------------------------------------------------------
# ------------------------------------------------------

buttonObjs = []
class Buttons:
    def __init__(self, x, y, name, onForever):
        self.x = x
        self.y = y
        self.name = name
        self.onForever = onForever
        self.isOn = onForever
        # All sideMenu will have onForever be false
        self.surface = pygame.Surface((100, 30))
        self.surface.fill('White')
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))

buttonObjs.append(Buttons(0, 0, "Attack", False))
buttonObjs.append(Buttons(0, 0, "Build", False))
buttonObjs.append(Buttons(0, 0, "Endure", False))
buttonObjs.append(Buttons(0, 0, "Split", False))

PlayerObjs = []
class playObj:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.surface = pygame.Surface((25, 25))
        self.surface.fill('Orange')
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))
        self.hasMoved = False
        self.doneAttack = False
        self.inRange = False
        self.isAttacking = False
        self.maxHP = 0
        self.curHP = 0
        self.power = 0
        self.moveDistance = 1
        self.getStats(type)
    
    def getStats(self, type):
        if type == "norm":
            self.maxHP = 100
            self.curHP = 100
            self.power = 50
            self.moveDistance = 3

    def moveRandom(self):
        ranStep = random.randint(1, 5)
        if ranStep == 1 and self.x >= wrdDiv:
            self.x -= wrdDiv
        elif ranStep == 2 and self.x < width - wrdDiv:
            self.x += wrdDiv
        elif ranStep == 3 and self.y < height - wrdDiv:
            self.y += wrdDiv
        elif ranStep == 4 and self.y >= wrdDiv:
            self.y -= wrdDiv
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
        xx, yy = self.x // wrdDiv, self.y // wrdDiv
        ranStep = random.randint(1, 4)
        if ranStep == 1 and self.x >= wrdDiv and not wObj[xx - 1][yy]:
            wObj[xx][yy] = None
            wObj[xx - 1][yy] = self
            self.x -= wrdDiv
        elif ranStep == 2 and self.x < width - wrdDiv and not wObj[xx + 1][yy]:
            wObj[xx][yy] = None
            wObj[xx + 1][yy] = self
            self.x += wrdDiv
        elif ranStep == 3 and self.y < height - wrdDiv and not wObj[xx][yy + 1]:
            wObj[xx][yy] = None
            wObj[xx][yy + 1] = self
            self.y += wrdDiv
        elif ranStep == 4 and self.y >= wrdDiv and not wObj[xx][yy - 1]:
            wObj[xx][yy] = None
            wObj[xx][yy - 1] = self
            self.y -= wrdDiv
        self.rect.topleft = (self.x, self.y)

    def attackPlayer(self):

        directions = [
            (-wrdDiv, 0), (wrdDiv, 0), (0, -wrdDiv), (0, wrdDiv), 
            (-wrdDiv, -wrdDiv), (wrdDiv, -wrdDiv), (-wrdDiv, wrdDiv), (wrdDiv, wrdDiv) ]

        for dx, dy in directions:
            adj_x = (self.x + dx) // wrdDiv
            adj_y = (self.y + dy) // wrdDiv

            if 0 <= adj_x < hth and 0 <= adj_y < wth:
                adjObj = wObj[adj_x][adj_y]
                if isinstance(adjObj, playObj):
                    global toDisplayText
                    toDisplayText = str(f"Enemy at ({self.x},{self.y}) attacking player at ({adjObj.x},{adjObj.y})")
                    adjObj.curHP -= wrdDiv

                    if adjObj.curHP <= 0:
                        PlayerObjs.remove(adjObj)
                        updateBoard()
                        break
                    break

PlayerObjs.append(playObj(400, 200, "norm"))
PlayerObjs.append(playObj(400, 300, "norm"))
PlayerObjs.append(playObj(400, 400, "norm"))
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
        playX = player.rect.x // wrdDiv
        playY = player.rect.y // wrdDiv
        q.append((playX, playY))
        world[playX][playY] = 1
        visit[playX][playY] = True
        worldScore[world[playX][playY]] += 1
        wObj[playX][playY] = player

    for enemy in EnemyObjs:
        enemX = enemy.rect.x // wrdDiv
        enemY = enemy.rect.y // wrdDiv
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

# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------

sideMenu = [False, None]

def displayBoard():
    # World Grid display
    for i in range(0, hth):
        for j in range(0, wth):
            color = "Red" if world[i][j] == 0 else "Blue" if world[i][j] == 1 else "White" if world[i][j] == 2 else "Magenta"
            pygame.draw.rect(screen, color, pygame.Rect(i * wrdDiv, j * wrdDiv, 25, 25))

    # Enemy Display
    for enemy in EnemyObjs:
        screen.blit(enemy.surface, enemy.rect)
        if enemy.canBeAttacked:
            color = "White"
            nm_surf = pygame.Surface((12, 12))
            nm_surf.fill(color)
            nm_rect = nm_surf.get_rect(center=enemy.rect.center)
            screen.blit(nm_surf, nm_rect)

        enemy.canBeAttacked = False

    # Player Display
    for player in PlayerObjs:
        player.canAttack = False

        surrounding_positions = [
            (-wrdDiv, 0), (wrdDiv, 0), (0, -wrdDiv), (0, wrdDiv), 
            (-wrdDiv, -wrdDiv), (wrdDiv, -wrdDiv), (-wrdDiv, wrdDiv), (wrdDiv, wrdDiv) 
        ]
        
        for dx, dy in surrounding_positions:
            adjacent_x = (player.x + dx) // wrdDiv
            adjacent_y = (player.y + dy) // wrdDiv

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


    textArea = pygame.Surface((width // 2.5, height // 6))
    textArea.fill('Grey')
    screen.blit(textArea, (width - (width // 2.5), height - (height // 6)))

    scoreText = str("Turn  " + str(curTurn) + "     Score  " + str(worldScore[1]) + "  :  " + str(worldScore[0]))
    score_surf = font.render(scoreText, False, (254, 254, 254))
    screen.blit(score_surf, (width - (width // 2.5) + 5, height - (height // 6) + 5))

    scoreText = str(toDisplayText)
    score_surf = font.render(scoreText, False, (254, 254, 254))
    screen.blit(score_surf, (width - (width // 2.5) + 5, height - (height // 6) + 35))

    if sideMenu[0]:  # When a player is selected
        curPlay = sideMenu[1]

        idx = 0
        for button in buttonObjs:
            if not button.onForever:
                button.rect.x = curPlay.rect.x + 15
                button.rect.y = curPlay.rect.y + (idx * 35) + 10
                button.isOn = True
                idx += 1

            # Draw the button background
            pygame.draw.rect(screen, "Grey", button.rect)
            # Draw the button text
            score_surf = font.render(button.name, False, (0, 0, 0))
            screen.blit(score_surf, (button.rect.x + 10, button.rect.y + 10))

        
def closeSideMenu():
    sideMenu[0], sideMenu[1] = False, None
    for button in buttonObjs:
            if not button.onForever:
                button.isOn = False


        



# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------


playerAttacking = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            sideMenu[0], sideMenu[1] = False, None
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
                if playerAttacking:
                    for enemy in EnemyObjs:
                        if enemy.rect.collidepoint(event.pos) and playerAttacking:  
                            if abs(playerAttacking.x - enemy.x) <= wrdDiv and abs(playerAttacking.y - enemy.y) <= wrdDiv:
                                toDisplayText = "Enemy Was Attacked"
                                enemy.curHP -= playerAttacking.power
                                playerAttacking.doneAttack = True 
                                playerAttacking.hasMoved = True
                                playerAttacking.isAttacking = False
                                playerAttacking = None

                                if enemy.curHP <= 0:
                                    EnemyObjs.remove(enemy)
                                    updateBoard()
                                    break
                            break 
                for button in buttonObjs:
                    if button.rect.collidepoint(event.pos) and button.isOn:
                        if button.name == "Attack":
                            if sideMenu[1].inRange:
                                toDisplayText = "Attack clicked!"
                                playerAttacking = sideMenu[1]
                                playerAttacking.isAttacking = True
                            else:
                                toDisplayText = "Not In Range"
                        elif button.name == "Build":
                            toDisplayText = "Build clicked!"
                        elif button.name == "Endure":
                            toDisplayText = "Endure clicked!"
                        elif button.name == "Split":
                            toDisplayText = "Split clicked!"
                        closeSideMenu()
                for player in PlayerObjs:
                    if player.rect.collidepoint(event.pos) and not player.hasMoved:  
                        dragging_player = player
                        original_x, original_y = player.x, player.y
                        drag_offset_x = player.rect.x - event.pos[0]
                        drag_offset_y = player.rect.y - event.pos[1]
                        break
                closeSideMenu()
            elif event.button == 3:  
                for player in PlayerObjs:
                    if player.rect.collidepoint(event.pos) and not player.doneAttack:
                        sideMenu[0], sideMenu[1] = True, player
                    else:
                        player.isAttacking = False

        if event.type == pygame.MOUSEMOTION: 
            if dragging_player:
                mouse_x, mouse_y = event.pos
                new_x = mouse_x + drag_offset_x
                new_y = mouse_y + drag_offset_y
                new_x = (new_x // wrdDiv) * wrdDiv
                new_y = (new_y // wrdDiv) * wrdDiv

                max_dist = dragging_player.moveDistance  # Movement distance limit
                if abs(new_x - original_x) > max_dist * wrdDiv:
                    new_x = original_x + max_dist * wrdDiv if new_x > original_x else original_x - max_dist * wrdDiv
                if abs(new_y - original_y) > max_dist * wrdDiv:
                    new_y = original_y + max_dist * wrdDiv if new_y > original_y else original_y - max_dist * wrdDiv

                dragging_player.rect.topleft = (new_x, new_y)

                for dx in range(-max_dist, max_dist + 1):
                    for dy in range(-max_dist, max_dist + 1):
                        if 0 <= (original_x // wrdDiv + dx) < hth and 0 <= (original_y // wrdDiv + dy) < wth:
                            if abs(dx) <= max_dist and abs(dy) <= max_dist:
                                if (dx == 0 and dy == 0):
                                    world[(original_x // wrdDiv) + dx][(original_y // wrdDiv) + dy] = 2
                                else:
                                    world[(original_x // wrdDiv) + dx][(original_y // wrdDiv) + dy] = 3
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and dragging_player:
                if dragging_player:
                    new_x = dragging_player.rect.x // wrdDiv
                    new_y = dragging_player.rect.y // wrdDiv
                    for i, player in enumerate(PlayerObjs):
                        if player == dragging_player:
                            PlayerObjs[i].x = new_x * wrdDiv
                            PlayerObjs[i].y = new_y * wrdDiv
                            PlayerObjs[i].hasMoved = True
                            PlayerObjs[i].isAttacking = False
                            PlayerObjs[i].inRange = False
                            break
                updateBoard()
                dragging_player = None

    screen.blit(background, background_rect)

    displayBoard()

    pygame.display.update()
    clock.tick(60)