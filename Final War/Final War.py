from collections import deque
from fractions import Fraction
import pygame  # type: ignore
import random
import battle # type: ignore
import math
pygame.init()

# fstThird = int(wth * Fraction(1, 5))
# sndThird = int((wth - fstThird))

width, height = 1200, 700
wth, hth = int((width // 100) * 5), int((height // 100) * 4)
wrdDiv = 20 # translate phyiscal location to world grid
tileSize = wrdDiv - 4
objSize = tileSize - 4
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Final War')
clock = pygame.time.Clock()

world = [[0 for _ in range(hth)] for _ in range(wth)]  # 0: red enemy, 1: blue player, 2: white being dragged, 3: Magenta can be placed
wObj = [[None for _ in range(hth)] for _ in range(wth)]
worldScore = [0, 0]
curTurn = 1
toDisplayText = "The Game Has Begun"

font = pygame.font.Font('font/Pixeltype.ttf', 40)

background = pygame.Surface((width, height))
background.fill((0, 50, 210))
background_rect = background.get_rect(center=(width // 2, height // 2))

# ------------------------------------------------------
# ------------------------------------------------------

fences = []
class Fences:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.HP = 151
        self.surface = pygame.Surface((tileSize, tileSize))
        self.surface.fill("Yellow" if team else "Purple")
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))

buttons = []
buttons2 = []
class Buttons:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name
        self.surface = pygame.Surface((100, 30))
        self.surface.fill('White')
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))

btnsName = ["Attack", "Defend", "Push / Pull", "Build / Fix", "Stats", "Reset"]
for btn in btnsName: buttons.append(Buttons(0, 0, btn))

btns2Name = ["Fence", "Mine", "Hospital"]
for btn in btns2Name: buttons2.append(Buttons(0, 0, btn))

Players = []
Enemies = []
class playObj:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.surface = pygame.Surface((objSize, objSize))
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
        self.maxDist = 2
        self.getStats(type)
    
    def getStats(self, type):
        if type == "norm":
            self.maxHP = 150
            self.curHP = 150
            self.power = 100
            self.moveDistance = 3
        elif type == "God":
            self.maxHP = 1500
            self.curHP = 1500
            self.power = 1000
            self.moveDistance = 20

class enemObj:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.surface = pygame.Surface((objSize, objSize))
        self.surface.fill('Purple')
        self.rect = self.surface.get_rect(topleft=(self.x, self.y))
        self.hasMoved = False
        self.doneAttack = False
        self.inRange = False
        self.isAttacking = False
        self.isDefending = False
        self.maxHP = 0
        self.curHP = 0
        self.power = 0
        self.maxDist = 2
        self.getStats(type)
    
    def getStats(self, type):
        if type == "norm":
            self.maxHP = 150
            self.curHP = 150
            self.power = 100
            self.moveDistance = 3
        elif type == "God":
            self.maxHP = 1500
            self.curHP = 1500
            self.power = 1000
            self.moveDistance = 20


# Follow player's behind the enemy barrior
def moveMid(ene):

    playerBehind = None
    closestDist, closestBehind = width, width
    targX, targY = wth // 2, hth // 2
    beefX, beefY = wth // 2, hth // 2

    for play in Players:
        dist = math.sqrt((play.x - ene.x)**2 + (play.y - ene.y)**2)

        # If there is nobody behind the player
        if play.x < ene.x + 8 and not playerBehind and dist <= closestDist:
            if dist < closestDist or (dist == closestDist and random.random() > .45):
                closestDist = dist
                targX, targY = play.x, play.y
        elif play.x > ene.x + 2:
            if dist < closestBehind:
                playerBehind = play
                beefX, beefY = play.x, play.y
                closestBehind = dist
   
    if playerBehind:
        targX, targY = beefX, beefY

    bestDist = wth
    bestXY = [0, 0]
    for i in range(-ene.maxDist, ene.maxDist + 1):
        for j in range(-ene.maxDist, ene.maxDist + 1):
            nX, nY = ene.x + i, ene.y + j
            dist = math.sqrt((targX - nX)**2 + (targY - nY)**2)
            if (dist < bestDist or (dist ==  bestDist and random.random() > .45)) and nX in range(0, wth) and nY in range(0, hth) and not wObj[nX][nY]:
                if not (  (abs(i) > 1 or abs(j) > 1) and wObj[ene.x+i//2 if abs(i)>1 else ene.x+i][ene.y+j//2 if abs(j)>1 else ene.y+j]):
                    bestDist = dist
                    bestXY = [i, j] # the combo


    MMM(ene, bestXY[0], bestXY[1])
    

    
def MMM(ene, nX, nY):
    eX = ene.x
    eY = ene.y
    wObj[eX][eY] = None
    ene.x += nX
    ene.y += nY
    ene.rect.topleft = (ene.x, ene.y)
    wObj[ene.x][ene.y] = ene

# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------

def updateBoard():
    
    global nPG, nEG
    worldScore[0], worldScore[1] = 0, 0
    nPG, nEG = 0, 0

    fstThird = int(wth * Fraction(1, 5))
    sndThird = int((wth - fstThird))

    for i in range(wth):
        for j in range(hth):
            world[i][j] = 0 

    for player in Players:
        if player.curHP <= 0: 
            Players.remove(player)
            wObj[player.rect.x][player.rect.y] = None
        else:
            wObj[player.rect.x][player.rect.y] = player
            if player.rect.x > sndThird:
                nPG += 1

    for enemy in Enemies:
        if enemy.curHP <= 0: 
            Enemies.remove(enemy)
            wObj[enemy.rect.x][enemy.rect.y] = None
        else:
            wObj[enemy.rect.x][enemy.rect.y] = enemy
            if enemy.rect.x > sndThird:
                nPG += 1

    for i in range(0, wth):
        for j in range(0, hth):
            if i == fstThird or i == sndThird:
                world[i][j] = 1
            else:
                world[i][j] = 0   

# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------

sideMenu = [False, None]
sideMenu2 = False
LUB = 0
LUB2 = 0


def displayBoard():

    screen.blit(background, background_rect)

    # World Grid display
    for i in range(0, wth):
        for j in range(0, hth):
            color = (10, 50, 255) if world[i][j] == 0 else (0, 240, 255) if world[i][j] == 1 else "Green" if world[i][j] == 2 else "Magenta"
            pygame.draw.rect(screen, color, pygame.Rect(i * wrdDiv, j * wrdDiv, tileSize, tileSize))


    # Player Display
    for player in Players:
        player.rect.topleft = (player.x * wrdDiv, player.y * wrdDiv)
        screen.blit(player.surface, player.rect)
        player.rect.topleft = (player.x, player.y)

        if not player.hasMoved:
            nm_surf = pygame.Surface((5, 5))
            nm_surf.fill("White")
            screen.blit(nm_surf, (player.x * wrdDiv, player.y * wrdDiv))

    for enemy in Enemies:
        enemy.rect.topleft = (enemy.x * wrdDiv, enemy.y * wrdDiv)
        screen.blit(enemy.surface, enemy.rect)
        enemy.rect.topleft = (enemy.x, enemy.y)

    for fence in fences:
        fence.rect.topleft = (fence.x * wrdDiv, fence.y * wrdDiv)
        screen.blit(fence.surface, fence.rect)
        fence.rect.topleft = (fence.x, fence.y)

    textArea = pygame.Surface((width, height // 5), pygame.SRCALPHA)
    textArea.fill("Black")  
    screen.blit(textArea, (0, height - (height // 5)))

    textArea = pygame.Surface((width // 2.5, height // 5), pygame.SRCALPHA)
    textArea.fill("Grey")  
    screen.blit(textArea, (width - (width // 2.5), height - (height // 5) + 10))

    textArea = pygame.Surface((width // 2.5, height // 5), pygame.SRCALPHA)
    textArea.fill("Grey")  
    screen.blit(textArea, (0, height - (height // 5) + 10))

    scoreText = str(toDisplayText)
    score_surf = font.render(scoreText, False, (254, 254, 254))
    screen.blit(score_surf, (width - (width // 2.5) + 5, height - (height // 6) + 35))

    score_surf = font.render("Turn  " + str(curTurn), False, (254, 254, 254))
    screen.blit(score_surf, (width // 2 - 50, height - (height // 6) + 35))


    score_surf = font.render("Resources  " + str(curTurn), False, (254, 254, 254))
    screen.blit(score_surf, (10, height - (height // 6)))

    score_surf = font.render("Population  " + str(curTurn), False, (254, 254, 254))
    screen.blit(score_surf, (10, height - (height // 6) + 40))

    score_surf = font.render("Active  " + str(curTurn), False, (254, 254, 254))
    screen.blit(score_surf, (10, height - (height // 6) + 80))

    

    if sideMenu[0]:
        LB = LUB
        BL = buttons
        
        if sideMenu2:
            LB = LUB2
            BL = buttons2
        
        b1 = LB - 1 if LB - 1 >= 0 else len(BL) - 1
        b2 = BL[LB]
        b3 = LB + 1 if LB + 1 <= len(BL) - 1 else 0
        btns = [BL[b1], b2, BL[b3]]

        for i, button in enumerate(btns):
            button.rect.x = ((sideMenu[1].rect.x * wrdDiv) + 10) + 100 * i 
            button.rect.y = (sideMenu[1].rect.y * wrdDiv) + 10 if i == 1 else (sideMenu[1].rect.y * wrdDiv) + 25
            button_font, sizeT = font, 10
            color = (120, 120, 120) if i != 1 else "Grey"
            if i == 1:
                button.rect.width = 100
                button.rect.height = 30
            else:
                button.rect.width = 80
                button.rect.height = 20
                button_font = pygame.font.Font('font/Pixeltype.ttf', 25)
                sizeT = 5
            pygame.draw.rect(screen, color, button.rect)
            score_surf = button_font.render(button.name, False, (0, 0, 0))
            screen.blit(score_surf, (button.rect.x + sizeT, button.rect.y + sizeT))

def closeSideMenu():
    global sideMenu2
    sideMenu[0], sideMenu[1] = False, None
    sideMenu2 = False

def reset():
    global Players, Enemies, fences, world, curTurn, toDisplayText, gameDone, showAttackScreen, endWho
    endWho = 0
    gameDone, showAttackScreen = False, False
    world = [[0 for _ in range(hth)] for _ in range(wth)]
    curTurn = 1
    toDisplayText = "The Game Has Begun"
    Players = []
    Enemies = []
    fences = []

    for i in range(-2, 3):
        Players.append(playObj(int(wth * Fraction(1, 5)) + 3,hth // 2 + (i * 3), "norm"))
        Enemies.append(enemObj(wth // 2 + 1,hth // 2 + (i * 3), "norm"))
    updateBoard()

def availableSpaces(x, y, player, targetPeople, full):
    q = deque()
    visit = set()
    dir = [(0, 1), (1, 0), (0, -1), (-1,0), (-1, -1), (-1, 1), (1, -1), (1,1)]
    q = deque([(x, y)])
    visit = set([(x, y)])
    count = 0
    distance = player.maxDist if full else 1
    while q and count < distance:
        count += 1
        for _ in range(len(q)):
            x, y = q.popleft()

            for dx, dy in dir:
                nx, ny = x + dx, y + dy
                if 0 <= nx < wth and 0 <= ny < hth and (nx, ny) not in visit:
                    if targetPeople:
                        if wObj[nx][ny]:
                            obj = wObj[nx][ny]
                            if obj in Enemies:
                                q.append((nx, ny))
                                visit.add((nx, ny))
                                world[nx][ny] = 2
                    else:
                        if not wObj[nx][ny]:
                            q.append((nx, ny))
                            visit.add((nx, ny))
                            world[nx][ny] = 3

# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------

BigMetalCage = False
playerAttacking = None 
draPla = None
dOX = 0
dOY= 0
oriX = 0
oriY = 0
lastCommand = ""

reset()
updateBoard()

def Battle(player, enemy):
    result = battle.main(player.curHP, enemy.curHP)
    pygame.time.wait(500)
    newHP = result.split(",")  # example "100,43"
    player.curHP = int(newHP[0])
    enemy.curHP = int(newHP[1])
    updateBoard()    

# want to add multiple buildings
def Build(x, y, forPlayer):
    new_fence = Fences(x, y, forPlayer) 
    fences.append(new_fence)
    wObj[x][y] = new_fence

while True:

    # Display only where player can do thing
    if playerAttacking:
        pA = playerAttacking
        if lastCommand == "Attack":
            availableSpaces(pA.x, pA.y, pA, True, False)
        elif lastCommand == "Build":
            availableSpaces(pA.x, pA.y, pA, False, False)

    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                sideMenu[0], sideMenu[1] = False, None

                for enemy in Enemies:
                    moveMid(enemy)

                for player in Players:
                    player.hasMoved = False
                    player.doneAttack = False
                    player.isAttacking = False
                    player.inRange = False  # Reset the range flag

                playerAttacking = None
                curTurn += 1
                updateBoard()

        if event.type == pygame.MOUSEBUTTONDOWN:
            
            if event.button == 1:
                if playerAttacking and lastCommand == "Attack":
                    mouse_x, mouse_y = event.pos
                    mouse_x = mouse_x // wrdDiv
                    mouse_y = mouse_y // wrdDiv
                    if wObj[mouse_x][mouse_y]:
                        obj = wObj[mouse_x][mouse_y]
                        if obj in Enemies:
                            playerAttacking.hasMoved, playerAttacking.doneAttack = True, True
                            BigMetalCage = True
                            Battle(playerAttacking, obj)
                    playerAttacking.isAttacking = False
                    playerAttacking = None
                    lastCommand = ""
                    updateBoard()

                elif playerAttacking and lastCommand == "Build":
                    mouse_x, mouse_y = event.pos
                    mouse_x = mouse_x // wrdDiv
                    mouse_y = mouse_y // wrdDiv
                    if not wObj[mouse_x][mouse_y] and world[mouse_x][mouse_y] == 3:
                        playerAttacking.hasMoved, playerAttacking.doneAttack = True, True
                        BigMetalCage = True
                        Build(mouse_x, mouse_y, True)

                    playerAttacking.isAttacking = False
                    playerAttacking = None
                    lastCommand = ""
                    updateBoard()
                

                elif sideMenu[0]:
                    LB = LUB
                    BL = buttons
                    if sideMenu2:
                        LB = LUB2
                        BL = buttons2

                    b1 = LB - 1 if LB - 1 >= 0 else len(BL) - 1
                    b3 = LB + 1 if LB + 1 <= len(BL) - 1 else 0

                    button = BL[LB]

                    if button.rect.collidepoint(event.pos):
                        closeTheMenu = True
                        if button.name == "Attack":
                            toDisplayText = "Attack clicked!"
                            playerAttacking = sideMenu[1]
                            lastCommand = "Attack"
                        elif button.name == "Defend":
                            
                            toDisplayText = "Build clicked!"
                            playerAttacking = sideMenu[1]
                            lastCommand = "Build"

                        elif button.name == "Push / Pull":
                            toDisplayText = "Push pressed!"
                        elif button.name == "Build / Fix":
                            toDisplayText = "Build / Fix pressed!"
                            sideMenu2, closeTheMenu = True, False
                        elif button.name == "Reset":
                            reset()
                        if closeTheMenu: closeSideMenu()
                    elif BL[b1].rect.collidepoint(event.pos):
                        LB -= 1
                        if LB < 0: LB = len(BL) - 1
                        if not sideMenu2:
                            LUB = LB
                        else:
                            LUB2 = LB
                    elif BL[b3].rect.collidepoint(event.pos):
                        LB += 1
                        if LB > len(BL) - 1: LB = 0
                        if not sideMenu2:
                            LUB = LB
                        else: 
                            LUB2 = LB

                    else: closeSideMenu() 
                        
                for player in Players:
                    if pygame.Rect(player.x * wrdDiv, player.y * wrdDiv, tileSize, tileSize).collidepoint(event.pos) and not player.hasMoved and player != draPla:
                        draPla = player
                        oriX, oriY = player.x, player.y
                        dOX = player.rect.x - event.pos[0] // wrdDiv
                        dOY= player.rect.y - event.pos[1] // wrdDiv
                        break
            elif event.button == 3 and not draPla:  
                for player in Players:
                    if pygame.Rect(player.x * wrdDiv, player.y * wrdDiv, tileSize, tileSize).collidepoint(event.pos) and not player.doneAttack:
                        sideMenu[0], sideMenu[1] = True, player
                    else:
                        player.isAttacking = False

        if event.type == pygame.MOUSEMOTION and not playerAttacking and not BigMetalCage: 
            if draPla:
                mouse_x, mouse_y = event.pos

                mouse_x = mouse_x // wrdDiv
                mouse_y = mouse_y // wrdDiv
                
                new_x = mouse_x + dOX
                new_y = mouse_y + dOY
                new_x = new_x
                new_y = new_y
                max_dist = draPla.maxDist
                if abs(new_x - oriX) > max_dist:
                    new_x = oriX + max_dist if new_x > oriX else oriX - max_dist
                if abs(new_y - oriY) > max_dist:
                    new_y = oriY + max_dist if new_y > oriY else oriY - max_dist
                if new_x in range(0, wth) and new_y in range(0, hth):
                    draPla.x, draPla.y = new_x, new_y
                
                availableSpaces(oriX, oriY, draPla, False, True)

        if event.type == pygame.MOUSEBUTTONUP and not BigMetalCage:
            if event.button == 1 and draPla:
                if draPla:
                    mouse_x, mouse_y = event.pos
                    new_x = mouse_x // wrdDiv
                    new_y = mouse_y // wrdDiv

                    goodSpot = True

                    if new_x in range(0, wth) and new_y in range(0, hth) and world[new_x][new_y] == 3 and not wObj[new_x][new_y]:
                        wObj[oriX][oriY] = None
                        wObj[new_x][new_y] = draPla
                        draPla.hasMoved = True
                        draPla.x = new_x
                        draPla.y = new_y
                        draPla.isAttacking = False
                        draPla.inRange = False
                    else:
                        draPla.x = oriX
                        draPla.y = oriY
                        draPla.rect.x = oriX
                        draPla.rect.y = oriY
                    updateBoard()
                    draPla = None
    displayBoard()
    BigMetalCage = False # I just don't know so I have this boolean so the transition is eh

    pygame.display.update()
    clock.tick(60)