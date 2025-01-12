from collections import deque
from fractions import Fraction
import pygame  # type: ignore
import random
pygame.init()

width, height = 1200, 700
wth, hth = int((width // 100) * 4), int((height // 100) * 4)
wrdDiv = 20 # translate phyiscal location to world grid
tileSize = wrdDiv - 2
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Final War')
clock = pygame.time.Clock()

world = [[0 for _ in range(hth)] for _ in range(wth)]  # 0: red enemy, 1: blue player, 2: white being dragged, 3: Magenta can be placed
wObj = [[None for _ in range(hth)] for _ in range(wth)]
worldScore = [0, 0]
curTurn = 0
toDisplayText = "The Game Has Begun"

font = pygame.font.Font('font/Pixeltype.ttf', 40)

background = pygame.Surface((width, height))
background.fill((0, 50, 210))
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
# buttonObjs.append(Buttons(0, 0, "Pull", False))
buttonObjs.append(Buttons(0, 0, "Build", False))
buttonObjs.append(Buttons(0, 0, "Fix Wall", False))
buttonObjs.append(Buttons(900, 550, "Reset", True)) # always appear

PlayerObjs = []
class playObj:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.surface = pygame.Surface((tileSize, tileSize))
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
            self.moveDistance = 3
        elif type == "God":
            self.maxHP = 1500
            self.curHP = 1500
            self.power = 1000
            self.moveDistance = 20

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

    for player in PlayerObjs:
        playX = player.rect.x
        playY = player.rect.y
        if playX > sndThird:
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
buttonMoveUp = False


def displayBoard():

    screen.blit(background, background_rect)

    # World Grid display
    for i in range(0, wth):
        for j in range(0, hth):
            color = (10, 50, 255) if world[i][j] == 0 else (255, 240, 0) if world[i][j] == 1 else "Green" if world[i][j] == 2 else "Magenta"
            pygame.draw.rect(screen, color, pygame.Rect(i * wrdDiv, j * wrdDiv, tileSize, tileSize))

    # Player Display
    for player in PlayerObjs:
        player.canAttack = False

        screen.blit((player.x * wrdDiv, player.y * wrdDiv), player.rect)

    # Button and button of screen

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
                    button.rect.y -= 150


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
    global PlayerObjs, world, curTurn, toDisplayText, gameDone, showAttackScreen, endWho
    endWho = 0
    gameDone, showAttackScreen = False, False
    world = [[0 for _ in range(hth)] for _ in range(wth)]
    curTurn = 0
    toDisplayText = "The Game Has Begun"
    PlayerObjs = []

    for i in range(-2, 3):
        PlayerObjs.append(playObj( int(width * Fraction(1, 4)) + i, (height // 2) + (i * 2), "norm"))

    updateBoard()

# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------

playerAttacking = None 
draPla = None
dOX = 0
dOY= 0
oriX = 0
oriY = 0

reset()
updateBoard()


while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            sideMenu[0], sideMenu[1] = False, None

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
                    if playerAttacking:
                        playerAttacking.isAttacking = False
                        playerAttacking = None
                for button in buttonObjs:
                    if button.rect.collidepoint(event.pos) and button.isOn:
                        if button.name == "Attack":
                            toDisplayText = "Attack clicked!"
                        elif button.name == "Build":
                            toDisplayText = "Build clicked!"
                        elif button.name == "Defend":
                            toDisplayText = "Player Defending!"
                        elif button.name == "Push":
                            toDisplayText = "Push pressed!"
                        elif button.name == "Pull":
                            toDisplayText = "Pull pressed!"
                        elif button.name == "Fix Wall":
                            toDisplayText = "Fix Wall pressed!"
                        elif button.name == "Reset":
                            reset()
                        closeSideMenu()
                for player in PlayerObjs:
                    if player.rect.collidepoint(event.pos) and not player.hasMoved and player != draPla:
                        draPla = player
                        oriX, oriY = player.x, player.y
                        dOX = player.rect.x - event.pos[0]
                        dOY= player.rect.y - event.pos[1]
                        break
                closeSideMenu()
            elif event.button == 3:  
                for player in PlayerObjs:
                    if player.rect.collidepoint(event.pos) and not player.doneAttack:
                        sideMenu[0], sideMenu[1] = True, player
                    else:
                        player.isAttacking = False


        # -------------------------------------------------------------------------
        # Dragging all done here

        # a true fence is able to be stepped on
        

        # -----------------------------------------------

        if event.type == pygame.MOUSEMOTION: 
            if draPla:
                mouse_x, mouse_y = event.pos
                new_x = mouse_x + dOX
                new_y = mouse_y + dOY
                new_x = new_x
                new_y = new_y
                max_dist = draPla.moveDistance  # Movement distance limit
                if abs(new_x - oriX) > max_dist:
                    new_x = oriX + max_dist if new_x > oriX else oriX - max_dist
                if abs(new_y - oriY) > max_dist:
                    new_y = oriY + max_dist if new_y > oriY else oriY - max_dist
                draPla.rect.topleft = (new_x, new_y)

                q = deque()
                visit = set()
                dir = [(0, 1), (1, 0), (0, -1), (-1,0), (-1, -1), (-1, 1), (1, -1), (1,1)]
                dirTwo = [(-1, -1), (-1, 1), (1, -1), (1,1)] # ignore for now
                q = deque([(oriX, oriY)])
                visit = set([(oriX, oriY)])
                count = 0
                while q and count < max_dist:
                    count += 1

                    for _ in range(len(q)):
                        x, y = q.popleft()

                        for dx, dy in dir:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < wth and 0 <= ny < hth and (nx, ny) not in visit:
                                q.append((nx, ny))
                                visit.add((nx, ny))
                                world[nx][ny] = 3


        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and draPla:
                if draPla:
                    new_x = draPla.rect.x
                    new_y = draPla.rect.y

                    goodSpot = True

                    if (draPla.x != new_x or draPla.y != new_y) and goodSpot and world[new_x][new_y] == 3:
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

    pygame.display.update()
    clock.tick(60)