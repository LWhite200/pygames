" Destroying Fences "

" buttons not moving up "

from collections import deque
from fractions import Fraction
import pygame  # type: ignore
import random
pygame.init()

width, height = 1000, 800
wth, hth = (width // 100) * 2, (height // 100) * 2
wrdDiv = 50 # translate phyiscal location to world grid
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
buttonObjs.append(Buttons(0, 0, "Fix Wall", False))
buttonObjs.append(Buttons(900, 550, "Reset", True)) # always appear

fenceObjs = []
class Fences:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.HP = 151
        self.surface = pygame.Surface((35, 35))
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
        elif type == "God":
            self.maxHP = 1500
            self.curHP = 1500
            self.power = 1000
            self.moveDistance = 20

# ---------------------------------------------------------------------------------------

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
        self.strat = "OFF"

teamStrat = "MID"
eNum = 5

wLoc = wth // 2
yLoc = hth // 2

def enemyAI():
    global teamStrat, curTurn, wLoc
    allStrats = ["OFF", "MID","DEF", "WALL", "RUN"] 

    # choose strat
    pcx, pcy = 0, 0
    plaLocations = []
    for player in PlayerObjs:
        pX = player.x // wrdDiv
        pY = player.y // wrdDiv
        plaLocations.append((pX, pY))
        pcx += pX
        pcy += pY
    pcx = pcx // len(PlayerObjs)
    pcy = pcy // len(PlayerObjs)

    fstThird = wth * Fraction(1, 5)
    sndThird = (wth - fstThird) - 1

    # Find The team's strategy
    if curTurn == 0:
        wLoc = wth // 2
        teamStrat = random.choice(allStrats)
    elif curTurn > 3:
        if teamStrat == "RUN" or (curTurn >= 5 and random.random() < 0.025):
            teamStrat = "RUN"
            wLoc = 1
        elif pcx > fstThird or pcx < sndThird:
            wLoc = 1
        elif teamStrat == "OFF" and pcx < wth // 2:
            wLoc = pcx
        elif teamStrat == "DEF" and pcx < wth // 2:
            wLoc = sndThird - 2
        elif pcx < wth // 2:
            wLoc = wth // 2
        elif pcx > wth // 2:
            wLoc = pcx + 1
        

    for enemy in EnemyObjs:
        enemy.canBeAttacked = False
        enemy.strat = teamStrat
        
        objsNear = []
        objsNear = ObjectsNear(enemy)
        plaNear = []
        plaNear = PlayerNear(objsNear)

        # If they should diverge from the normal strategy
        if teamStrat == "RUN":
            enemy.strat = "RUN"
        elif plaNear:
            enemy.strat = random.choice(["OFF", "DEF", "OFF", teamStrat])

        es = enemy.strat
        if es == "OFF":
            print("OFF")
            if plaNear:
                if random.random() < .50:
                    eneAttack(enemy, plaNear)
                else:
                    if teamStrat == "MID":
                        moveMid(enemy)
                    else:
                        eneMove(enemy)
                    objsNear = ObjectsNear(enemy)
                    plaNear = PlayerNear(objsNear)
                    if plaNear: eneAttack(enemy, plaNear)
            else:
                eneMove(enemy)
        elif es == "DEF":
            print("DEF")
        elif es == "MID":
            print("MID")
            moveMid(enemy)
            if random.random() < .60:
                objsNear = ObjectsNear(enemy)
                plaNear = PlayerNear(objsNear)
                if plaNear: eneAttack(enemy, plaNear)
        elif es == "WALL":
            print("Wall")
            if wLoc-1 == (enemy.x // wrdDiv - 1) and wObj[wLoc-1][enemy.y // wrdDiv]:
                enY = enemy.y // wrdDiv
                DY = [-1, 1, -2, 2]
                hasMoved = False
                for dy in DY:
                    if (enY + dy) in range(0, hth) and not wObj[wLoc-1][enY + dy] and not wObj[wLoc][enY + dy]:
                        MMM(enemy, 0, dy)
                        eneWall(wLoc-1, enemy.y // wrdDiv)
                        hasMoved = True
                        break        
                    if not hasMoved:
                        moveMid(enemy)
            elif wLoc-1 == (enemy.x // wrdDiv - 1) and not wObj[wLoc-1][enemy.y // wrdDiv]:
                eneWall(wLoc-1, enemy.y // wrdDiv)
            else:
                moveMid(enemy)
                if wLoc-1 == (enemy.x // wrdDiv - 1) and not wObj[wLoc-1][enemy.y // wrdDiv]:
                    eneWall(wLoc-1, enemy.y // wrdDiv)
        elif es == "RUN":
            print("RUN")
            eneRun(enemy)
            
        else:
            print("Errorororor")

def eneRun(ene):
    eX = ene.x // wrdDiv
    eY = ene.y // wrdDiv
    dir = [(-2, 0), (-2, 1), (-2, -1), (-2, 2), (-2, -2), 
            (-1, 0), (-1, 1), (-1, -1), (-1, 2), (-1, -2),
            (-0, 0), (-0, 1), (-0, -1), (-0, 2), (-0, -2),
            (1, 0), (1, 1), (1, -1), (1, 2), (1, -2)]

    for dx, dy in dir:
        if (eX + dx) in range(0, wth) and (eY + dy) in range(0, hth) and not wObj[eX + dx][eY + dy]:
            if abs(dx) > 1 and wObj[eX + (dx // 2)][eY + dy]:
                continue
            elif abs(dy) > 1 and wObj[eX][eY + (dy // 2)]:
                continue
            else:
                MMM(ene, dx, dy)
                break

def eneWall(x, y):
    print("Wall placed")
    new_fence = Fences(x * wrdDiv, y * wrdDiv, False) 
    fenceObjs.append(new_fence)

def ObjectsNear(ene):
    directions = [
            (-wrdDiv, 0), (wrdDiv, 0), (0, -wrdDiv), (0, wrdDiv), 
            (-wrdDiv, -wrdDiv), (wrdDiv, -wrdDiv), (-wrdDiv, wrdDiv), (wrdDiv, wrdDiv) ]
    objs = []
    for dx, dy in directions:
        nX = (ene.x + dx) // wrdDiv
        nY = (ene.y + dy) // wrdDiv
        if 0 <= nX < wth and 0 <= nY < hth and wObj[nX][nY]:
            objs.append((nX, nY))
    if objs:
        return objs
    else:
        return []
    
def PlayerNear(objsNear):
    plaNear = []
    for ob in objsNear:
        nX, nY = ob
        player = wObj[nX][nY]
        if isinstance(player, playObj):
            plaNear.append((nX, nY))

    return plaNear

def closestPlayer(ene):
    q = deque()
    visit = set()
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1), (2, 0), (-2, 0)]
    start_x, start_y = ene.x // wrdDiv, ene.y // wrdDiv  
    q.append((start_x, start_y))
    visit.add((start_x, start_y))
    count = 0

    while q and len(PlayerObjs) > 0:
        count += 1

        for _ in range(len(q)): 
            x, y = q.popleft()

            for dx, dy in directions: 
                nx, ny = x + dx, y + dy

                if 0 <= nx < wth and 0 <= ny < hth and (nx, ny) not in visit:
                    visit.add((nx, ny))

                    if wObj[nx][ny]: 
                        player = wObj[nx][ny]
                        if isinstance(player, playObj): 
                            return player
                    
                    if not wObj[nx][ny]:  
                        q.append((nx, ny))
    return None

def eneMove(ene):
    xx, yy = ene.x // wrdDiv, ene.y // wrdDiv
    decrease = False
    dir = [(-1, 0), (0, 1), (0, -1), (1, 0), (-1, -1), (-1, 1), (1, 1), (1, -1),
            (2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (2, -2), (-2, 2), (-2, -2),
            (2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
    attempts = 0
    while attempts < 10:
        attempts += 1
        ranStep = random.randint(1, 4) if not ene.canBeAttacked else random.randint(1, 5)
        
        # If the enemy can be attacked and the random chance is high, break
        if ene.canBeAttacked and random.random() < 0.95:
            decrease = True
            ranStep = 5
        
        if ranStep == 5:
            if decrease:
                break
            decrease = True
        else:
            # Prioritize leftward movement (more likely to move left if canBeAttacked is False)
            if random.random() < 0.75:
                dx, dy = dir[0]  # Always move 2 steps left (high priority)
            else:
                dx, dy = random.choice(dir[1:])  # Randomly pick from other directions

            new_x, new_y = xx + dx, yy + dy

            # Ensure the new position is within bounds
            if 0 <= new_x < width // wrdDiv and 0 <= new_y < height // wrdDiv:
                if wObj[new_x][new_y]:
                    continue
                if xx != new_x or yy != new_y:
                    ene.isDefending = False
                wObj[xx][yy] = None
                wObj[new_x][new_y] = ene
                ene.x, ene.y = new_x * wrdDiv, new_y * wrdDiv
                break
    
    ene.rect.topleft = (ene.x, ene.y)

# Follow player's behind the enemy barrior
def moveMid(ene):
    targX = wLoc
    eX = ene.x // wrdDiv
    eY = ene.y // wrdDiv
    need = (targX - eX)

    behind_player = None
    for player in PlayerObjs:
        pX = player.x // wrdDiv
        pY = player.y // wrdDiv
        if pX >= eX:
            behind_player = player
            break

    if behind_player:
        pX = behind_player.x // wrdDiv
        pY = behind_player.y // wrdDiv

        dx = pX - eX
        dy = pY - eY

        if abs(dx) > 2:
            dx = 2
        elif abs(dx) == 2:
            dx = 1
        elif abs(dx) < 2:
            dx = 0

        if abs(dy) > 2:
            dy = 2
        elif abs(dy) == 2:
            dy = 1
        elif abs(dy) < 2:
            dy = 0   
        
        if pX < eX:
            dx *= -1
        if pY < eY:
            dy *= -1

        if 0 <= (eX + dx) < wth and 0 <= (eY + dy) < hth and not wObj[eX + dx][eY + dy]:
            MMM(ene, dx, dy)

    else:
        pY = 0
        ppN = closestPlayer(ene)
        if ppN:
            pY = ppN.y // wrdDiv
        pY = pY - eY

        if need == -1 and 0 <= targX < wth and 0 <= eY < hth and not wObj[eX - 1][eY]:
            MMM(ene, -1, 0)
        elif need == -1 and 0 <= targX < wth and 0 <= eY < hth:
            dir = [(-1, 0), (-1, 1), (-1, -1), (-1, 2), (-1, -2)]
            for dx, dy in dir:
                if 0 <= (eX + dx) < wth and 0 <= (eY + dy) < hth and not wObj[eX + dx][eY + dy]:
                    MMM(ene, dx, dy)
                    break


        elif need <= -2:
            if not wObj[eX - 2][eY] and not wObj[eX - 1][eY]:
                MMM(ene, -2, 0)
            else:
                dir = [(-2, 0), (-2, 1), (-2, -1), (-1, 0), (-1, 1), (-1, -1), (-1, 2), (-1, -2)]
                for dx, dy in dir:
                    tx, ty = dx, dy
                    if abs(dx) > 1: tx = tx // 2
                    if abs(dy) > 1: ty = ty // 2

                    if 0 <= (eX + dx) < wth and 0 <= (eY + dy) < hth and not wObj[eX + dx][eY + dy] and not wObj[eX + tx][eY + ty]:
                        MMM(ene, dx, dy)
                        break
        else:
            if ppN and 0 <= eX < wth and 0 <= eY + pY < hth and not wObj[eX][eY + pY]:
                MMM(ene, 0, pY)

# To move enemies
def MMM(ene, nX, nY):
    eX = ene.x // wrdDiv
    eY = ene.y // wrdDiv
    wObj[eX][eY] = None
    ene.x += nX * wrdDiv
    ene.y += nY * wrdDiv
    ene.rect.topleft = (ene.x, ene.y)
    wObj[ene.x // wrdDiv][ene.y // wrdDiv] = ene

def eneAttack(ene, plaNear):
    global wObj, playObj
    pX, pY = random.choice(plaNear)

    player = wObj[pX][pY]
    if isinstance(player, playObj):
        attackFunct(player, ene, False, False)

def updateBoard():
    
    global nPG, nEG

    worldScore[0], worldScore[1] = 0, 0
    nPG, nEG = 0, 0

    fstThird = int(wth * Fraction(1, 5))
    sndThird = int((wth - fstThird) - 1)

    for i in range(wth):
        for j in range(hth):
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
        if playX > sndThird:
            nPG += 1

    for enemy in EnemyObjs:
        enemX = enemy.rect.x // wrdDiv
        enemY = enemy.rect.y // wrdDiv
        worldScore[world[enemX][enemY]] += 1
        wObj[enemX][enemY] = enemy
        if enemX < fstThird:
            nEG += 1

    

    for i in range(0, wth):
        for j in range(0, hth):
            if i == fstThird or i == sndThird:
                world[i][j] = 1
            else:
                world[i][j] = 0
    



battleText = ["Battle 0", "Battle 1", 0]
showAttackScreen = False

def attackFunct(pla, ene, who, pWD):
    global showAttackScreen, battleText
    pAta, eAta = pla.power, ene.power
    if not who: # enemy attacked
        if pla.isDefending and not pWD:
            eAta = eAta // 4
            pAta = pAta // 3
            pla.isDefending = False
        elif pla.isDefending and pWD:
            eAta = 0
            pAta = pAta // 2
            pla.isDefending = False
        else:
            pAta = pAta // 4
    else: # player attacked
        if ene.isDefending and not pWD:
            pAta = pAta // 4
            eAta = eAta // 3
            ene.isDefending = False
        elif ene.isDefending and pWD:
            pAta = pAta // 2
            eAta = 0
            ene.isDefending = False
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
    elif pWD:
        battleText[2] = 4
    updateBoard()
    ene.canBeAttacked = False


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
        else:
            deathNotice = "!!!PWD HYPE!!!"

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
    for i in range(0, wth):
        for j in range(0, hth):
            color = (0, 110, 255) if world[i][j] == 0 else "Cyan" if world[i][j] == 1 else "Green" if world[i][j] == 2 else "Magenta"
            pygame.draw.rect(screen, color, pygame.Rect(i * wrdDiv, j * wrdDiv, 45, 45))

    for fence in fenceObjs:
        if fence.team:
            pygame.draw.rect(screen, "Yellow", fence.rect)
        else:
            pygame.draw.rect(screen, "Purple", fence.rect)



    # Enemy Display
    for enemy in EnemyObjs:
        screen.blit(enemy.surface, enemy.rect)
        if enemy.canBeAttacked:
            color = "White"
            nm_surf = pygame.Surface((12, 12))
            nm_surf.fill(color)
            nm_rect = nm_surf.get_rect(center=enemy.rect.center)
            screen.blit(nm_surf, nm_rect)

        

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

            if 0 <= adjacent_x < wth and 0 <= adjacent_y < hth:
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

    textArea = pygame.Surface((width // 2.5, height // 6), pygame.SRCALPHA)
    textArea.fill((169, 169, 169, 80))  
    screen.blit(textArea, (width - (width // 2.5), height - (height // 6)))

    scoreText = str("Turn  " + str(curTurn) + " / " + str(numTurns))
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

def gameOverScreen():
    global endWho
    screen.blit(background, background_rect)
    if endWho == 3:
        eA_surf = font.render("Ended In A Tie", False, (254, 254, 254))
        eA_rect = eA_surf.get_rect(center=(width // 2, height // 2))
        screen.blit(eA_surf, eA_rect)

    elif endWho == 1:
        p = pygame.Surface((100, 200))
        p.fill('Orange')
        p_rect = p.get_rect(center=(width // 2, height // 2))
        screen.blit(p, p_rect)

        eA_surf = font.render("You Win", False, (254, 254, 254))
        eA_rect = eA_surf.get_rect(center=(width // 2, height * Fraction(4, 5)))
        screen.blit(eA_surf, eA_rect)
    elif endWho == 2:
        e = pygame.Surface((100, 200))
        e.fill('Purple')
        e_rect = e.get_rect(center=(width // 2, height // 2))
        screen.blit(e, e_rect)

        eA_surf = font.render("You Lost", False, (254, 254, 254))
        eA_rect = eA_surf.get_rect(center=(width // 2, height * Fraction(4, 5)))
        screen.blit(eA_surf, eA_rect)



def reset():
    global PlayerObjs, EnemyObjs, fenceObjs, world, wObj, worldScore, curTurn, toDisplayText, gameDone, showAttackScreen, numTurns, endWho
    endWho = 0
    gameDone, showAttackScreen = False, False
    world = [[0 for _ in range(hth)] for _ in range(wth)]
    wObj = [[None for _ in range(hth)] for _ in range(wth)]
    worldScore = [0, 0]
    curTurn = 0
    toDisplayText = "The Game Has Begun"
    PlayerObjs = []
    EnemyObjs = []
    fenceObjs = []

    for i in range(-2, 3):
        PlayerObjs.append(playObj(int(width * Fraction(1, 4)), (height // 2) + (wrdDiv * i * 2), "norm"))
        EnemyObjs.append(enemObj(int(width * Fraction(3, 4) - wrdDiv), (height // 2) + (wrdDiv * i * 2)))

    numTurns = (len(PlayerObjs) + len(EnemyObjs)) * 2
    updateBoard()

# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------

playerAttacking = None 
buildMode = False
pushMode = False
pullMode = False
gameDone = False
FixWall = False
endWho = 0 # [1 = player, 2 = enemy, 3 = tie]

numTurns = (len(PlayerObjs) + len(EnemyObjs)) * 2

nPG = 0
nEG = 0

draPla = None
dOX = 0
dOY= 0
oriX = 0
oriY = 0

reset()
updateBoard()


while True:
    if (not PlayerObjs or not EnemyObjs or nPG >= len(EnemyObjs) or nEG >= len(PlayerObjs) or curTurn > numTurns) and not showAttackScreen:
        if curTurn > numTurns:
            endWho = 3
        elif not PlayerObjs:
            endWho = 2
        elif nEG >= len(PlayerObjs):
            endWho = 2
        elif not EnemyObjs: # or 
            endWho = 1
        elif nPG >= len(EnemyObjs):
            endWho = 1

        toDisplayText = "Game Over"
        gameDone = True

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:  # 
                reset()
            if event.type == pygame.QUIT:
                pygame.quit()


    if FixWall and pullMode and not showAttackScreen:
        dir = [(wrdDiv, 0), (-wrdDiv, 0), (0, wrdDiv), (0, -wrdDiv)]
        newDir = []
        px, py = playerAttacking.rect.x, playerAttacking.rect.y 

        for dx, dy in dir:
            newX, newY = (px + dx) // wrdDiv, (py + dy) // wrdDiv
            if newX in range(0, wth) and newY in range(0, hth) and wObj[newX][newY]:

                if wObj[newX][newY]:
                    obj = wObj[newX][newY]
                    if isinstance(obj, Fences):
                        newDir.append((newX, newY))
                        world[newX][newY] = 3                    
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = (mouse_x // wrdDiv) * wrdDiv
        grid_y = (mouse_y // wrdDiv) * wrdDiv
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                playerAttacking = None
                pullMode = False
                FixWall = False 
                closeSideMenu()
                updateBoard()
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    ngX, ngY = grid_x // wrdDiv, grid_y // wrdDiv
                    if wObj[ngX][ngY] and world[ngX][ngY] == 3 and (ngX, ngY) in newDir:
                        obj = wObj[ngX][ngY]
                        if isinstance(obj, Fences):
                            
                            if obj.team: # false means it is a enemy
                                fenceObjs.remove(obj)
                            else:
                                obj.HP -= playerAttacking.power
                                if obj.HP <= 0:
                                    fenceObjs.remove(obj)

                    playerAttacking.hasMoved, playerAttacking.doneAttack = True, True
                    updateBoard()

                pullMode = False
                FixWall = False
                playerAttacking = None
                closeSideMenu()
                updateBoard()  


    elif pullMode and not showAttackScreen and not gameDone:
        dir = [(wrdDiv, 0), (-wrdDiv, 0), (0, wrdDiv), (0, -wrdDiv)]
        newDir = []
        px, py = playerAttacking.rect.x, playerAttacking.rect.y 

        for dx, dy in dir:
            newX, newY = (px + dx) // wrdDiv, (py + dy) // wrdDiv
            if newX in range(0, wth - 1) and newY in range(0, hth - 1) and wObj[newX][newY]:
                pla = wObj[newX][newY]
                if isinstance(pla, playObj):
                    newDir.append((newX, newY))
                    world[newX][newY] = 3

        mouse_x, mouse_y = pygame.mouse.get_pos()
        grid_x = (mouse_x // wrdDiv) * wrdDiv
        grid_y = (mouse_y // wrdDiv) * wrdDiv

        if not newDir:
            toDisplayText = "Nobody can be pushes"
            pullMode = False
            playerAttacking = None
            closeSideMenu()
            updateBoard()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                playerAttacking = None
                pullMode = False 
                closeSideMenu()
                updateBoard()
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if wObj[grid_x // wrdDiv][grid_y // wrdDiv] and (grid_x // wrdDiv, grid_y // wrdDiv) in newDir:
                        
                        for enemy in PlayerObjs:
                            if enemy.x == grid_x and enemy.y == grid_y:
                                nX = (grid_x - px) // wrdDiv # 0 or -1 or 1 for directions
                                nY = (grid_y - py) // wrdDiv
                                pushDist = random.choice([wrdDiv * 2, wrdDiv * 3]) # the pixel representation of 1 or 2 tiles
                                new_x = grid_x - (nX * pushDist) # original plus the new position
                                new_y = grid_y - (nY * pushDist)
                                if 0 <= new_x < width and 0 <= new_y < height and not wObj[new_x // wrdDiv][new_y // wrdDiv]:
                                    enemy.x = new_x
                                    enemy.y = new_y
                                    enemy.rect.topleft = (enemy.x, enemy.y)
                                    playerAttacking.hasMoved, playerAttacking.doneAttack = True, True
                                    updateBoard()
                                else:
                                    toDisplayText = ("Couldn't push " + str(pushDist // wrdDiv))
                                break
                    pullMode = False
                    playerAttacking = None
                    closeSideMenu()
                    updateBoard()
    elif pushMode and not showAttackScreen and not gameDone:
        dir = [(wrdDiv, 0), (-wrdDiv, 0), (0, wrdDiv), (0, -wrdDiv)]
        newDir = []
        px, py = playerAttacking.rect.x, playerAttacking.rect.y 

        for dx, dy in dir:
            newX, newY = (px + dx) // wrdDiv, (py + dy) // wrdDiv
            if newX in range(0, wth - 1) and newY in range(0, hth - 1) and wObj[newX][newY]:
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
                            if enemy.x == grid_x and enemy.y == grid_y:

                                nX = (grid_x - px) // wrdDiv # 0 or -1 or 1 for directions
                                nY = (grid_y - py) // wrdDiv

                                pushDist = random.choice([wrdDiv, wrdDiv * 2]) # the pixel representation of 1 or 2 tiles

                                new_x = grid_x + (nX * pushDist) # original plus the new position
                                new_y = grid_y + (nY * pushDist)

                                if 0 <= new_x < width and 0 <= new_y < height and not wObj[new_x // wrdDiv][new_y // wrdDiv]:
                                    enemy.x = new_x
                                    enemy.y = new_y
                                    enemy.rect.topleft = (enemy.x, enemy.y)
                                    playerAttacking.hasMoved, playerAttacking.doneAttack = True, True
                                    if enemy.isDefending:
                                        attackFunct(playerAttacking, enemy, True, True)
                                    updateBoard()
                                else:
                                    toDisplayText = ("Couldn't push " + str(pushDist // wrdDiv))

                                break

                    pushMode = False
                    playerAttacking = None
                    closeSideMenu()
                    updateBoard()
    elif buildMode and not showAttackScreen and not pushMode and not gameDone:
        dir = [(wrdDiv, 0), (-wrdDiv, 0), (0, wrdDiv), (0, -wrdDiv)]
        newDir = []
        px, py = playerAttacking.rect.x, playerAttacking.rect.y 

        for dx, dy in dir:
            newX, newY = (px + dx) // wrdDiv, (py + dy) // wrdDiv
            if newX in range(0, wth) and newY in range(0, hth) and not wObj[newX][newY]:
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
                        updateBoard()
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

    " --- Normal Game Loop Here ---"
    if not buildMode and not showAttackScreen and not pushMode and not gameDone: #-------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                sideMenu[0], sideMenu[1] = False, None

                enemyAI() # The new enemy A.I.

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
                                    attackFunct(playerAttacking, enemy, True, False)
                                    playerAttacking.doneAttack = True 
                                    playerAttacking.hasMoved = True
                                    playerAttacking.isAttacking = False
                                    playerAttacking.curHP -= enemy.power // 4
                                    playerAttacking = None
                                break 
                        if playerAttacking:
                            playerAttacking.isAttacking = False
                            playerAttacking = None
                    for button in buttonObjs:
                        if button.rect.collidepoint(event.pos) and button.isOn:
                            if sideMenu[1]: sideMenu[1].isDefending = False
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
                            elif button.name == "Pull":
                                toDisplayText = "Pull pressed!"
                                playerAttacking = sideMenu[1]
                                pullMode = True
                            elif button.name == "Fix Wall":
                                toDisplayText = "Fix Wall pressed!"
                                playerAttacking = sideMenu[1]
                                FixWall = True
                                pullMode = True
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
                    new_x = (new_x // wrdDiv) * wrdDiv
                    new_y = (new_y // wrdDiv) * wrdDiv
                    max_dist = draPla.moveDistance  # Movement distance limit
                    if abs(new_x - oriX) > max_dist * wrdDiv:
                        new_x = oriX + max_dist * wrdDiv if new_x > oriX else oriX - max_dist * wrdDiv
                    if abs(new_y - oriY) > max_dist * wrdDiv:
                        new_y = oriY + max_dist * wrdDiv if new_y > oriY else oriY - max_dist * wrdDiv
                    draPla.rect.topleft = (new_x, new_y)

                    q = deque()
                    visit = set()
                    dir = [(0, 1), (1, 0), (0, -1), (-1,0), (-1, -1), (-1, 1), (1, -1), (1,1)]
                    dirTwo = [(-1, -1), (-1, 1), (1, -1), (1,1)] # ignore for now
                    q = deque([(oriX // wrdDiv, oriY // wrdDiv)])
                    visit = set([(oriX // wrdDiv, oriY // wrdDiv)])
                    count = 0
                    while q and count < max_dist:
                        count += 1

                        for _ in range(len(q)):
                            x, y = q.popleft()

                            for dx, dy in dir:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < wth and 0 <= ny < hth and not wObj[nx][ny] and (nx, ny) not in visit:
                                    q.append((nx, ny))
                                    visit.add((nx, ny))
                                    world[nx][ny] = 3


            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and draPla:
                    if draPla:
                        new_x = draPla.rect.x // wrdDiv
                        new_y = draPla.rect.y // wrdDiv

                        goodSpot = True
                        if wObj[new_x][new_y]:
                            goodSpot = False

                        if (draPla.x != new_x * wrdDiv or draPla.y != new_y * wrdDiv) and goodSpot and world[new_x][new_y] == 3:
                            draPla.hasMoved = True
                            draPla.x = new_x * wrdDiv
                            draPla.y = new_y * wrdDiv
                            draPla.isAttacking = False
                            draPla.inRange = False
                        else:
                            draPla.x = oriX
                            draPla.y = oriY
                            draPla.rect.x = oriX
                            draPla.rect.y = oriY
                        updateBoard()
                        draPla = None
    if not showAttackScreen and not gameDone:
        displayBoard()
    elif showAttackScreen:
        battleScreen()
    else:
        gameOverScreen()
    pygame.display.update()
    clock.tick(60)