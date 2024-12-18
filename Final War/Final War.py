" Things to add: barriers, types, ranged attacks, enemy a.i."

from collections import deque
from fractions import Fraction
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
buttonObjs.append(Buttons(0, 0, "Defend", False))
buttonObjs.append(Buttons(0, 0, "Push", False))
buttonObjs.append(Buttons(0, 0, "Pull", False))
buttonObjs.append(Buttons(0, 0, "Build", False))
buttonObjs.append(Buttons(900, 550, "Reset", True)) # always appear

fenceObjs = []
class Fences:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.HP = 100
        self.surface = pygame.Surface((45, 45))
        self.surface.fill('Yellow')
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))



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
        self.isDefending = False
        self.maxHP = 0
        self.curHP = 0
        self.power = 0
        self.moveDistance = 1
        self.getStats(type)
    
    def getStats(self, type):
        if type == "norm":
            self.maxHP = 150
            self.curHP = 150
            self.power = 100
            self.moveDistance = 2

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
        self.surface.fill((0, 141, 0))
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))
        self.canBeAttacked = False
        self.isDefending = False
        self.maxHP = 150
        self.curHP = 150
        self.power = 100

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
                player = wObj[adj_x][adj_y]
                if isinstance(player, playObj) and random.random() < 0.5:
                    attackFunct(player, self, False)
                    break

PlayerObjs.append(playObj(350, 200, "norm"))
PlayerObjs.append(playObj(400, 300, "norm"))
PlayerObjs.append(playObj(350, 400, "norm"))
EnemyObjs.append(enemObj(600, 200))
EnemyObjs.append(enemObj(550, 300))
EnemyObjs.append(enemObj(600, 400))

dragging_player = None
drag_offset_x = 0
drag_offset_y = 0
original_x = 0
original_y = 0

def updateBoard():
    
    worldScore[0], worldScore[1] = 0, 0

    for i in range(hth):
        for j in range(wth):
            world[i][j] = 0 
            wObj[i][j] = None
    
    for fence in fenceObjs:
        fX = fence.rect.x // wrdDiv
        fY = fence.rect.y // wrdDiv
        wObj[fX][fY] = fence

    for player in PlayerObjs:
        playX = player.rect.x // wrdDiv
        playY = player.rect.y // wrdDiv
        worldScore[world[playX][playY]] += 1
        wObj[playX][playY] = player

    for enemy in EnemyObjs:
        enemX = enemy.rect.x // wrdDiv
        enemY = enemy.rect.y // wrdDiv
        worldScore[world[enemX][enemY]] += 1
        wObj[enemX][enemY] = enemy

    fstThird = hth * Fraction(1, 5)
    sndThird = (hth - fstThird) - 1

    for i in range(0, hth):
        for j in range(0, wth):
            if i == fstThird or i == sndThird:
                world[i][j] = 1
            else:
                world[i][j] = 0
    

updateBoard()


battleText = ["Battle 0", "Battle 1", 0]
showAttackScreen = False

def attackFunct(pla, ene, who):
    global showAttackScreen, battleText
    pAta, eAta = pla.power, ene.power
    if not who: # enemy attacked
        if pla.isDefending:
            eAta = eAta // 4
            pAta = pAta // 3
        else:
            pAta = pAta // 4
    else: # player attacked
        if ene.isDefending:
            pAta = pAta // 4
            eAta = eAta // 3
        else:
            eAta = eAta // 4
    pla.curHP -= eAta
    ene.curHP -= pAta
    battleText[0] = str("Enemy Lost  " + str(pAta) + "  :   (" + str(ene.curHP) + " / " + str(ene.maxHP) + ")")
    battleText[1] = str("Player Lost  " + str(eAta) + "  :   (" + str(pla.curHP) + " / " + str(pla.maxHP) + ")")
    showAttackScreen = True
    global toDisplayText
    toDisplayText = str("Attack Happened")
    if ene.curHP <= 0 and pla.curHP <= 0:
        battleText[2] = 3
        PlayerObjs.remove(pla)
        EnemyObjs.remove(ene)
    elif ene.curHP <= 0:
        EnemyObjs.remove(ene)
        battleText[2] = 2
    elif pla.curHP <= 0:
        battleText[2] = 1
        PlayerObjs.remove(pla)
    updateBoard()


def battleScreen():
    screen.blit(background, background_rect)

    pA_surf = font.render(str(battleText[0]), False, (254, 254, 254))
    pA_rect = pA_surf.get_rect(center=(width // 2, height * Fraction(2, 5)))
    screen.blit(pA_surf, pA_rect)

    eA_surf = font.render(str(battleText[1]), False, (254, 254, 254))
    eA_rect = eA_surf.get_rect(center=(width // 2, height * Fraction(3, 5)))
    screen.blit(eA_surf, eA_rect)

    p = pygame.Surface((100, 200))
    p.fill('Orange')
    p_rect = p.get_rect(center=(width * Fraction(1, 4), height // 2))
    screen.blit(p, p_rect)

    e = pygame.Surface((100, 200))
    e.fill('Purple')
    e_rect = e.get_rect(center=(width * Fraction(3, 4), height // 2))
    screen.blit(e, e_rect)

    if battleText[2] > 0:
        deathNotice = ""
        if battleText[2] == 1:
            deathNotice = "Player Died"
        elif battleText[2] == 2:
            deathNotice = "Enemy Died"
        elif battleText[2] == 3:
            deathNotice = "Both Died"

        eA_surf = font.render(deathNotice, False, (254, 254, 254))
        eA_rect = eA_surf.get_rect(center=(width // 2, height * Fraction(4, 5)))
        screen.blit(eA_surf, eA_rect)

# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------

sideMenu = [False, None]
buttonMoveUp = False

def displayBoard():

    screen.blit(background, background_rect)

    # World Grid display
    for i in range(0, hth):
        for j in range(0, wth):
            color = "Blue" if world[i][j] == 0 else "Cyan" if world[i][j] == 1 else "Green" if world[i][j] == 2 else "Magenta"
            pygame.draw.rect(screen, color, pygame.Rect(i * wrdDiv, j * wrdDiv, 45, 45))

    for fence in fenceObjs:
        pygame.draw.rect(screen, "Yellow", fence.rect)



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


    idx = 0
    moveUp = False
    global buttonMoveUp
    for button in buttonObjs:
        if not button.onForever:
            if sideMenu[0]:
                button.rect.x = sideMenu[1].rect.x + 15
                button.rect.y = sideMenu[1].rect.y + (idx * 35) + 10
                button.isOn = True
                idx += 1

                if button.rect.y >= height:
                    moveUp = True

                if buttonMoveUp:
                    button.rect.y -= 100

                pygame.draw.rect(screen, "Grey", button.rect)
                score_surf = font.render(button.name, False, (0, 0, 0))
                screen.blit(score_surf, (button.rect.x + 10, button.rect.y + 10))
        else:
            # Draw the button background
            pygame.draw.rect(screen, "Grey", button.rect)
            # Draw the button text
            score_surf = font.render(button.name, False, (0, 0, 0))
            screen.blit(score_surf, (button.rect.x + 10, button.rect.y + 10))  
    if moveUp: 
        buttonMoveUp = True 
    else: 
        buttonMoveUp = False  
        
def closeSideMenu():
    sideMenu[0], sideMenu[1] = False, None
    for button in buttonObjs:
            if not button.onForever:
                button.isOn = False


def reset():
    global PlayerObjs, EnemyObjs, fenceObjs, world, wObj, worldScore, curTurn, toDisplayText
    world = [[0 for _ in range(wth)] for _ in range(hth)]
    wObj = [[None for _ in range(wth)] for _ in range(hth)]
    worldScore = [0, 0]
    curTurn = 0
    toDisplayText = "The Game Has Begun"
    PlayerObjs = []
    EnemyObjs = []
    fenceObjs = []
    PlayerObjs.append(playObj(350, 200, "norm"))
    PlayerObjs.append(playObj(400, 300, "norm"))
    PlayerObjs.append(playObj(350, 400, "norm"))
    EnemyObjs.append(enemObj(600, 200))
    EnemyObjs.append(enemObj(550, 300))
    EnemyObjs.append(enemObj(600, 400))
    updateBoard()

# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------

playerAttacking = None
buildMode = False
pushMode = False

while True:

    if pushMode and not showAttackScreen:
        dir = [(wrdDiv, 0), (-wrdDiv, 0), (0, wrdDiv), (0, -wrdDiv)]
        newDir = []
        px, py = playerAttacking.rect.x, playerAttacking.rect.y 

        for dx, dy in dir:
            newX, newY = (px + dx) // wrdDiv, (py + dy) // wrdDiv
            if newX in range(0, hth - 1) and newY in range(0, wth - 1) and wObj[newX][newY]:
                enemy = wObj[newX][newY]
                if isinstance(enemy, enemObj):
                    newDir.append((newX, newY))
                    world[newX][newY] = 3

        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = (mouse_x // wrdDiv) * wrdDiv
        grid_y = (mouse_y // wrdDiv) * wrdDiv

        if not newDir:
            toDisplayText = "Nobody can be pushes"
            pushMode = False
            playerAttacking = None
            closeSideMenu()
            updateBoard()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                playerAttacking = None
                pushMode = False 
                closeSideMenu()
                updateBoard()
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if wObj[grid_x // wrdDiv][grid_y // wrdDiv] and (grid_x // wrdDiv, grid_y // wrdDiv) in newDir:

                        for enemy in EnemyObjs:
                            if enemy.rect.x == grid_x and enemy.rect.y == grid_y:
                                enemy.rect.x += 50
                                playerAttacking.hasMoved, playerAttacking.doneAttack = True, True
                                break

                    pushMode = False
                    playerAttacking = None
                    closeSideMenu()
                    updateBoard()

    elif buildMode and not showAttackScreen and not pushMode:
        dir = [(wrdDiv, 0), (-wrdDiv, 0), (0, wrdDiv), (0, -wrdDiv)]
        newDir = []
        px, py = playerAttacking.rect.x, playerAttacking.rect.y 

        for dx, dy in dir:
            newX, newY = (px + dx) // wrdDiv, (py + dy) // wrdDiv
            if newX in range(0, hth) and newY in range(0, wth) and not wObj[newX][newY]:
                newDir.append((newX, newY))
                world[newX][newY] = 3 
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = (mouse_x // wrdDiv) * wrdDiv
        grid_y = (mouse_y // wrdDiv) * wrdDiv
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                playerAttacking = None
                buildMode = False 
                closeSideMenu()
                updateBoard()
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    if wObj[grid_x // wrdDiv][grid_y // wrdDiv] is None and (grid_x // wrdDiv, grid_y // wrdDiv) in newDir: 
                        new_fence = Fences(grid_x, grid_y, True) 
                        fenceObjs.append(new_fence)
                        wObj[grid_x // wrdDiv][grid_y // wrdDiv] = new_fence
                        world[grid_x // wrdDiv][grid_y // wrdDiv] = 2
                        playerAttacking.hasMoved, playerAttacking.doneAttack = True, True
                    buildMode = False
                    playerAttacking = None
                    closeSideMenu()
                    updateBoard()

    elif showAttackScreen:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                showAttackScreen = False
                battleText[0], battleText[1] = "", ""
                battleText[2] = 0
            if event.type == pygame.QUIT:
                pygame.quit()
                    
    if not buildMode and not showAttackScreen and not pushMode:
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
                                    attackFunct(playerAttacking, enemy, True)
                                    playerAttacking.doneAttack = True 
                                    playerAttacking.hasMoved = True
                                    playerAttacking.isAttacking = False
                                    playerAttacking.curHP -= enemy.power // 4
                                    playerAttacking = None

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
                                playerAttacking = sideMenu[1]
                                buildMode = True
                            elif button.name == "Defend":
                                toDisplayText = "Player Defending!"
                                sideMenu[1].isDefending = True
                                sideMenu[1].hasMoved = True
                                sideMenu[1].doneAttack = True
                                sideMenu[1].isAttacking = False
                                sideMenu[1].inRange = False
                            elif button.name == "Push":
                                toDisplayText = "Push pressed!"
                                playerAttacking = sideMenu[1]
                                pushMode = True
                            elif button.name == "Reset":
                                reset()
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

    if not showAttackScreen:
        displayBoard()
    else:
        battleScreen()
    pygame.display.update()
    clock.tick(60)