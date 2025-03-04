import pygame # type: ignore
import random
import copy
from objs import deity # the object classes 

# Initialize PyGame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WordBound")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 255)

playX, playY = 520, 432
enemX, enemY = 40, 30
buttonY = 50

# Fonts
font = pygame.font.Font(None, 38)
bigfont = pygame.font.Font(None, 48)


# This will store the state of the radio buttons: False (not clicked), True (clicked)
SSC = [False, False, False, False]

player1, player2 = None, None
enemy, enemy2 = None, None
playerTeam, enemyTeam = [], []

switchSelected = -1
ppXX, ppYY = WIDTH // 2 - 100, HEIGHT // 2 + 70

curDialog = []

checkGameDone = False

def color_mapping(color_name):
    color_dict = {

        "red":    (255, 0, 0),    
        "blue":   (0, 0, 255), 
        "green":  (0, 240, 0), 
        "brown":  (150, 75, 0),  # Brown
        "lime":   (0, 250, 110),   
        "yellow": (210, 210, 0), 

        # Magical/Special Types
        "black":  (10, 10, 10), 
        "white":  (220, 220, 220), 
        "grey":   (128, 128, 128), 
        "cyan":   (0, 255, 255), 
        "magenta":(255, 0, 255), 
        "orange": (255, 165, 0), 
        "purple": (128, 0, 128), 
        "maroon": (128, 0, 0), 
    }
    return color_dict.get(color_name, (0, 0, 0))  # Default to black if color not found

# type weakness and resistances
weaknesses = {
    # Nature Types
    "red":   ["blue",  "brown"],    
    "blue":  ["green", "yellow"], 
    "green": ["red",   "cyan", "lime"], 

    "brown":  ["blue",  "green"],
    "lime":   ["brown", "maroon", "orange"],  # bug type, offensive

    "black": ["white", "magenta", "red"], 
    "white": ["black", "maroon", "cyan"],
    "grey":  [],  

    "cyan":   ["yellow",  "maroon", "red"],  # ice, cold
    "magenta":["cyan",    "purple"], 
    "yellow": ["magenta", "brown", "orange"], 
          
    "orange": ["brown", "purple"],   # like organic, oranges
    "purple": ["white", "orange"],   # thanos, bulky, sheer determination
    "maroon": ["magenta", "lime"],
}


resistances = {
    # Nature Types
    "red":    ["green", "yellow", "orange"],    
    "blue":   ["purple", "green", "cyan"], 
    "green":  ["blue", "orange", "lime"], 

    "brown":  ["red", "yellow", "maroon"], 
    "lime":   ["green", "cyan", "magenta"], 

    # Magical/Special Types
    "black":  ["grey", "purple", "maroon"], 
    "white":  ["grey", "cyan", "magenta"], 
    "grey":   [],

    "cyan":   ["blue", "green", "white"], 
    "magenta":["black", "purple", "maroon"], 
    "yellow": ["red", "brown", "orange"], 

    "orange": ["yellow", "brown", "grey"], 
    "purple": ["magenta", "white", "black"], 
    "maroon": ["brown", "lime", "cyan"], 
}

def drawLetter(letter, x, y, selected=False, hovered=False, isPlayer1=True, playerTurn=True):
        global curDialog
        boxX, boxY = x, y
        curFont = font
        if hovered and not selected and isPlayer1 and not playerTurn and not curDialog:
            x -= 4
            y -= 4
            curFont = bigfont
            rect_size = 50  # Slightly bigger
            boxX -= 5
            boxY -= 5
            color = tuple(max(0, c - 75) for c in letter.color1)  # Darker color
        else:
            rect_size = 40
            color = letter.color1
        pygame.draw.rect(screen, color, (boxX, boxY, rect_size, rect_size))
        border_color = (0, 155, 255) if selected and isPlayer1 else (255, 255, 255)
        pygame.draw.rect(screen, border_color, (boxX, boxY, rect_size, rect_size), 3)
        text = curFont.render(letter.char, True, border_color)
        screen.blit(text, (x + 10, y + 10))



    
def drawDeity(deity, x, y, isPlayer1, playerTurn):
        global player2
        text = font.render(f"{deity.name} (HP: {deity.curHP})", True, deity.battleColor)

        second = player2 if player2 and isPlayer1 else None
        if not second:
            second = enemy2 if enemy2 and not isPlayer1 else None

        if second:
            text = font.render(f"{deity.name} ({deity.curHP}) | ({second.curHP})", True, deity.battleColor)
        screen.blit(text, (x - 10, y + 10))

        spaceBetweenGroups = 10  # The space between the two groups of letters

        # Draw letters in the first group (deity.letters), offset a bit to the left
        for i, letter in enumerate(deity.letters):
            newX = x + i * 50 - 10  if second else x + i * 50 - 10
            newY = y + 50

            mouse_pos = pygame.mouse.get_pos()
            hovered = newX <= mouse_pos[0] <= newX + 40 and newY <= mouse_pos[1] <= newY + 40
            drawLetter(letter, newX, newY, letter in deity.lets, hovered, isPlayer1, playerTurn)

        # Display combo stamina (for player1)
        if isPlayer1 and player1:
            stamina_cost = player1.calculate_combo_stamina_cost()
            color = GREEN if stamina_cost <= deity.comboStamina else RED
            stamina_text = font.render(f"Combo Cost: {stamina_cost} / {deity.comboStamina}", True, color)
            screen.blit(stamina_text, (x - 10, y + 110))
        else:
            color = GREEN if 0 < deity.comboStamina else RED
            stamina_text = font.render(f"Enemy Stamina: {deity.comboStamina}", True, color)
            screen.blit(stamina_text, (x - 10, y + 110))




def drawDeity2(deity, x, y, isPlayer1, playerTurn):
        for i, letter in enumerate(deity.letters):
            newX = x + i * 50 - 10
            newY = y + 50

            mouse_pos = pygame.mouse.get_pos()
            hovered = newX <= mouse_pos[0] <= newX + 40 and newY <= mouse_pos[1] <= newY + 40
            drawLetter(letter, newX, newY, letter in deity.lets, hovered, isPlayer1, playerTurn)


def get_random_letters():
    letter_options = ['A', 'G', 'H', 'I']
    # letter_options = ['A', 'A', 'B', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    return [deity.Letter(random.choice(letter_options)) for _ in range(5)]


def enemy_choose_letters(enemy):
    # Enemy randomly selects 1-3 letters to form a word
    maxSize = len(enemy.letters)
    num_letters = random.randint(1, maxSize)
    chosen_letters = random.sample(enemy.letters, num_letters)
    return chosen_letters






# word = word Attacking   
def calculate_damage(attacking, receiving):
    global curDialog

    aboveOrBelow = sum(letter.power for letter in attacking.lets)
    base_damage = 0 # sum(letter.power for letter in word)
    
    for letter in attacking.lets:
        curType = letter.battleType
        curDmg = letter.power
        oppType = receiving.battleType
        
        # Checks each type and adds or subracts accordingly
        if curType in weaknesses[oppType]:
            base_damage += curDmg + 10
        elif curType in resistances[oppType]:
            base_damage += (curDmg // 2)
        else:
            base_damage += curDmg

    if base_damage > aboveOrBelow:
        curDialog.append("Super Effective!!!")
        curDialog.append(f"")
    elif base_damage < aboveOrBelow:
        curDialog.append("Not That Effective")
        curDialog.append(f"")

    return base_damage





def doCurTurn(person, target, isTargPlayer, SecondTarg):
    global player1, player2, enemy, enemy2, curDialog, playerTeam, enemyTeam

    targTeam = playerTeam if isTargPlayer else enemyTeam

    # If the current side is either null or knocked out
    if person.curHP <= 0 or target.curHP <= 0:
        return

    dmg = calculate_damage(person, target)

    # Determine which HP to update (left or right)
    peekHP = 0

    target.take_damage(dmg)  # Apply damage to the left side
    peekHP = target.curHP

    targTeam[0].curHP -= dmg
    if targTeam[0].curHP < 0:
        targTeam[0].curHP = 0

    # Update dialog based on the result
    curDialog.append(f"{person.name} used '{' '.join([letter.char for letter in person.lets])}'")
    curDialog.append(f"It did {dmg} dmg to '{' '.join([letter.char for letter in target.letters])}'")


    if peekHP < 1:
        if target:
            curDialog.append(f"{target.name}'s fainted!")
            curDialog.append(f"")

        if isTargPlayer:
            if SecondTarg:
                print("is, second")
                player2 = None  # Remove player2
            else:
                print("is, first")
                player1 = copy.deepcopy(player2)  # Move player2 to player1's position
                player2 = None
                
        else:
            if SecondTarg:
                print("not, second")
                enemy2 = None  # Remove enemy2
            else:
                print("not, first")
                enemy = copy.deepcopy(enemy2)  # Move enemy2 to enemy's position
                enemy2 = None

    # Reset things
    # ---blank for now as how is the stamina undated, does each deity have unique???---    person.update_stamina(person.calculate_combo_stamina_cost())
    person.lets = []





# Where messages shown
def draw_dialog():
    global curDialog

    # Get the current dialog lines
    text1 = curDialog[0] if len(curDialog) > 0 else ""
    text2 = curDialog[1] if len(curDialog) > 1 else ""

    offset = 20   # the thickness of the border
    yMoveUp = 20  # distance from the bottom of the screen
    yScale = 150
    xScale = WIDTH - 2 * offset

    yCord = HEIGHT - (yScale + yMoveUp)
    xCord = 0 + offset

    backColor = (125, 125, 125)
    pygame.draw.rect(screen, backColor, (xCord - offset, yCord - offset, xScale + 2 * offset, yScale + 2 * offset))
    frontColor = (50, 50, 50)
    pygame.draw.rect(screen, frontColor, (xCord, yCord, xScale, yScale))

    if text1 != "":
        col3 = (5, 5, 5)
        pygame.draw.rect(screen, col3, (xCord + offset, yCord + offset, xScale * 0.6, yScale - 2 * offset))


    # Draw the text with proper vertical spacing
    for i, line in enumerate([text1, text2]):
        text_surface = font.render(line, True, (255, 255, 255))
        text_rect = (xCord + 25, (yCord + 30) + (i * offset * 2.5))  # Adjusting the vertical spacing for the lines
        screen.blit(text_surface, text_rect)



# if enemy has multiple targets, let player choose left or right
def drawSideSelect():
    offset = 20  
    yMoveUp = 20 
    yScale = 150
    xScale = WIDTH - 2 * offset
    yCord = HEIGHT - (yScale + yMoveUp)
    xCord = 0 + offset
    col3 = (5, 5, 5)
    pygame.draw.rect(screen, col3, (xCord + offset, yCord + offset, xScale * 0.6, yScale - 2 * offset))

    ipX, ipY = 75, playY + buttonY
    backColor = (125, 125, 125)
    selectedColor = (0, 155, 255)
    if player1.lets:
        pygame.draw.rect(screen, backColor if not SSC[0] else selectedColor, (ipX, ipY + 45, 20, 20))
        pygame.draw.rect(screen, backColor if not SSC[1] else selectedColor, (ipX + 40, ipY + 45, 20, 20))

    # if you have multiple words
    if player2 and player2.lets:
        secondStart = ipX + (26 * len(player2.letters))   + 80
        pygame.draw.rect(screen, backColor if not SSC[2] else selectedColor, (secondStart, ipY + 45, 20, 20))
        pygame.draw.rect(screen, backColor if not SSC[3] else selectedColor, (secondStart + 40, ipY + 45, 20, 20))



def loadTeams():
    global player1, player2, enemy, enemy2, playerTeam, enemyTeam

    pD1 = deity.Deity("Gunther", get_random_letters())
    pD3 = deity.Deity("Gpla2", get_random_letters())
    playerTeam = [pD1, pD3]
    player1 = copy.deepcopy(playerTeam[0]) # must make deep copy

    en1= deity.Deity("Hugh Janus", get_random_letters())
    en2 = deity.Deity("en2", get_random_letters())
    enemyTeam = [en1, en2]
    enemy = copy.deepcopy(enemyTeam[0])
    # split afterwards, may start split, but not right now
    enemy2 = copy.deepcopy(enemy)
    enemy.letters = enemy.letters[:3]
    enemy2.letters = enemy2.letters[3:]


def separateDeity():
    global player1, player2
    
    p2Lets = []
    for let in player1.letters[:]:
        if let not in player1.lets:
            p2Lets.append(let)  
            player1.letters.remove(let)

    
    # player1.update_stamina(1) # costs 1 stamina
    player1.lets = []

    # Update stats in the split
    calcHP = len(player1.letters) / (len(player1.letters)+len(p2Lets))
    temp = player1.curHP
    player1.curHP = int(player1.curHP * calcHP)
    curHP2 = int(temp - player1.curHP)

    temp = player1.speed
    player1.speed += player1.speed - int(player1.speed * calcHP)
    speed2 = temp + int(temp * calcHP)

    # make it an entirely new deity
    player2 = copy.deepcopy(player1)
    player2.letters = p2Lets
    player2.curHP = curHP2
    player2.speed = speed2



def switch(isPlayer, newIdx):
    global player1, player2, enemy, enemy2, playerTeam, enemyTeam

    team = playerTeam if isPlayer else enemyTeam
    person = player1 if isPlayer else enemy
    person2 = player2 if isPlayer else enemy2

    totalHP = 0
    totalStam = 0

    # if not dead
    if person:
        # Get hp, stamina, ect. that changes
        totalHP += person.curHP
        totalStam += person.comboStamina
        if person2:
            totalHP += person2.curHP
            totalStam += person2.comboStamina
        team[0].curHP = totalHP
        team[0].comboStamina = totalStam

    # flip flop them
    team[0], team[newIdx] = team[newIdx], team[0]

    # Update global references
    if isPlayer:
        player1 = copy.deepcopy(team[0])
        player2 = None 
    else:
        enemy = copy.deepcopy(team[0])
        enemy2 = None


# when splitting or switching
def doEnemyTurnOnly():
    listBySpeed = [] # let enemy attack first

    if enemy:
        enemy.lets = enemy_choose_letters(enemy)
        listBySpeed.append((enemy, player1, True, False))
    if enemy2:
        enemy2.lets = enemy_choose_letters(enemy2)
        listBySpeed.append((enemy2, player1, True, True))
    for person, target, isTargPlayer, SecondTarg in listBySpeed:
        doCurTurn(person, target, isTargPlayer, SecondTarg)



def DeitySelect():
    global switchSelected
    
    screen.fill((204, 85, 0))
    
    x, y = 200, 50  # Adjust y to avoid overlap
    xSpace, ySpace = 10, 10  # for text spacing
    button_height = 80  # Adjust button height for visibility
    button_width = 400  # Adjust button width
    
    mouse_x, mouse_y = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]
    
    for i, deity in enumerate(playerTeam):
        button_rect = pygame.Rect(x, y, button_width, button_height)
        button_hover = button_rect.collidepoint(mouse_x, mouse_y)
        
        # Check if the mouse is hovering over the button and left click
        if button_hover and click and deity.curHP > 0:
            switchSelected = i
        
        # Background color logic
        backColor = (0, 125, 50) if button_hover and switchSelected == -1 else (0, 0, 125)
        backColor = (0, 0, 0) if i == switchSelected else backColor
        backColor = (255,0,0) if deity.curHP <= 0 else backColor

        pygame.draw.rect(screen, backColor, button_rect)
        pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)  # Black outline
        
        # Display the button name and HP
        input_word = f"{deity.name} HP: {deity.curHP}/{deity.maxHP}"
        input_surface = font.render(input_word, True, WHITE)
        screen.blit(input_surface, (x + xSpace, y + ySpace))
        
        y += button_height + 10  # Move y for the next button
    
    if switchSelected == 0:
        # placement if 1 or greater, -1 means nothing, -2 means turn this menu off a
        switchSelected = -3
    elif switchSelected > 0:
        # Confirmation box
        confirm_rect = pygame.Rect(100, 75, 600, 450)
        pygame.draw.rect(screen, (255, 155, 0), confirm_rect)
        pygame.draw.rect(screen, (0, 0, 0), confirm_rect, 2)  # Black outline
        
        # Display message
        message = "Do You Want To Switch?"
        message_surface = font.render(message, True, WHITE)
        screen.blit(message_surface, (WIDTH // 2 - 100, HEIGHT // 2 - 100))

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Yes, No, and Yes Separate buttons below
        yes_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 80, 40)
        no_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2, 80, 40)
        
        # Change color if hovered
        yes_color = (0, 100, 0) if yes_rect.collidepoint(mouse_x, mouse_y) else (0, 200, 0)
        no_color = (100, 0, 0) if no_rect.collidepoint(mouse_x, mouse_y) else (200, 0, 0)
        
        pygame.draw.rect(screen, yes_color, yes_rect)
        pygame.draw.rect(screen, no_color, no_rect)
        
        pygame.draw.rect(screen, (0, 0, 0), yes_rect, 2)  # Black outline
        pygame.draw.rect(screen, (0, 0, 0), no_rect, 2)  # Black outline
        
        yes_surface = font.render("Yes", True, WHITE)
        no_surface = font.render("No", True, WHITE)
        
        screen.blit(yes_surface, (WIDTH // 2 - 80, HEIGHT // 2 + 10))
        screen.blit(no_surface, (WIDTH // 2 + 40, HEIGHT // 2 + 10))

        # Draw the lettes the user can separate 
        if playerTeam[switchSelected]:
            drawDeity(playerTeam[switchSelected], ppXX, ppYY, True, False)

        if yes_rect.collidepoint(mouse_x, mouse_y) and click:
            # Perform the switch logic (implement switching logic here)
            
            p2Lets = []
            for let in playerTeam[switchSelected].lets[:]:
                    p2Lets.append(let)  

            swapBoolEvenText = False

            # if the player lost their last deity or swap in turn
            if  player1:
                switch(True, switchSelected)   # swap
                curDialog.append("Player Swapped Deities")
                curDialog.append(f"{player1.name} is vunerable!")
                doEnemyTurnOnly()              # let enemy attack - before splitting
            else:
                switch(True, switchSelected)   # swap
                curDialog.append(f"Player sent out {player1.name}")
                swapBoolEvenText = True

            # if player did not get killed
            if player1:

                if player1:
                    for let in p2Lets:
                        player1.lets.append(let)

                if player1 and player1.lets:
                    separateDeity()

                if player2 and swapBoolEvenText:
                    curDialog.append("Split in 2!")
                elif swapBoolEvenText:
                    curDialog.append("")

            switchSelected = -2  # Reset selection after switching
        
        if no_rect.collidepoint(mouse_x, mouse_y) and click:
            for let in playerTeam[switchSelected].lets[:]: 
                playerTeam[switchSelected].lets.remove(let)
            switchSelected = -1  # Cancel selection






def needAim(player):
    return all(letter.char != 'G' for letter in player.lets)

def targetNotSelf(player):
    """Returns True if any letter in the player's lets is between 'A' and 'F'."""
    return any('A' <= letter.char <= 'F' for letter in player.lets)


def turnMoves():
    global player1, player2, enemy, enemy2, playerTeam, enemyTeam, SSC

    # Randomize enemy attack
    enemy.lets = enemy_choose_letters(enemy)
    if enemy2:
        enemy2.lets = enemy_choose_letters(enemy2)

    # False = left, True = Right (rare one)
    playTarg1 = enemy2 if SSC[1] else enemy 
    playTarg2 = enemy2 if SSC[3] else enemy  
    p1t2 = True if playTarg1 == enemy2 else False
    p2t2 = True if playTarg2 == enemy2 else False

    enemTarg1 = player1 if not player2 else random.choice([player1, player2])  
    enemTarg2 = player1 if not player2 else random.choice([player1, player2]) 
    e1t2 = True if enemTarg1 == player2 else False
    e2t2 = True if enemTarg2 == player2 else False

    listBySpeed = []

    if player1 and player1.lets and targetNotSelf(player1):
        listBySpeed.append((player1, playTarg1, False, p1t2))
    if player2 and player2.lets and targetNotSelf(player2):
        listBySpeed.append((player2, playTarg2, False, p2t2))

    if enemy and enemy.lets and targetNotSelf(enemy):
        listBySpeed.append((enemy, enemTarg1, True, e1t2))
    if enemy2 and enemy2.lets and targetNotSelf(enemy2):
        listBySpeed.append((enemy2, enemTarg2, True, e2t2))

    if not listBySpeed:
        curDialog.append("Everyone Didn't Damage")
        curDialog.append("No Damage Done")

    # Process each move
    for person, target, isTargPlayer, SecondTarg in listBySpeed:

        # meaning the opponite is not protecting
        if needAim(target):
            doCurTurn(person, target, isTargPlayer, SecondTarg)
        else:
            curDialog.append(f"{target.name} Protected")
            curDialog.append(f"{person.name}'s attack failed")
    SSC = [None, None, None, None]
    




# make buttons for splitting, switching, retreat?
# screen to see your team

def main():
    global curDialog, SSC, player1, player2, enemy, enemy2, switchSelected
    loadTeams()

    running = True
    playerTurn = True
    sideSelect = False
    haveWinner = False

    showSwitchMenu = False
    while running:
        screen.fill(BLACK)

        # exit from switching
        if showSwitchMenu and switchSelected < -1:
            if not (player1 or player2):
                switchSelected = -1
            elif switchSelected == -2:
                showSwitchMenu = False
                switchSelected = -1
                # playerTurn = False
            else: # meaning they did not switch
                showSwitchMenu = False
                switchSelected = -1
            
        # Handle player input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    if curDialog:
                        curDialog.pop(0) 
                        if curDialog:
                            curDialog.pop(0)

                    # ----------------------------------------------------------
                    # When Multiple Enemies, select which side to attack [button on click ]
                    elif sideSelect:
                        ipX, ipY = 75, playY + buttonY
                        secondStart = None if not (player2 and player2.lets) else ipX + (26 * len(player2.letters)) + 80

                        if player1 and player1.lets and needAim(player1):
                            if ipX <= event.pos[0] <= ipX + 20 and ipY + 45 <= event.pos[1] <= ipY + 65:
                                SSC[0] = not SSC[0]
                                SSC[1] = False
                            elif ipX + 40 <= event.pos[0] <= ipX + 60 and ipY + 45 <= event.pos[1] <= ipY + 65:
                                SSC[1] = not SSC[1]  
                                SSC[0] = False

                        if player2 and player2.lets and needAim(player2):
                            if secondStart <= event.pos[0] <= secondStart + 20 and ipY + 45 <= event.pos[1] <= ipY + 65:
                                SSC[2] = not SSC[2]  
                                SSC[3] = False
                            elif secondStart + 40 <= event.pos[0] <= secondStart + 60 and ipY + 45 <= event.pos[1] <= ipY + 65:
                                SSC[3] = not SSC[3]  
                                SSC[2] = False


                    elif playerTurn and not sideSelect:

                        if showSwitchMenu and (switchSelected > -1):
                            for i, letter in enumerate(playerTeam[switchSelected].letters):
                                x = ppXX + i * 50 - 10
                                y = ppYY + buttonY
                                if x <= event.pos[0] <= x + 40 and y <= event.pos[1] <= y + 40:
                                    if letter not in playerTeam[switchSelected].lets:
                                        playerTeam[switchSelected].lets.append(letter)
                                    else:
                                        playerTeam[switchSelected].lets.remove(letter)



                        elif not showSwitchMenu:
                            for i, letter in enumerate(player1.letters):

                                    x = playX + i * 50 - 10  if not player2 else playX + i * 50 - 10
                                    y = playY + buttonY

                                    if x <= event.pos[0] <= x + 40 and y <= event.pos[1] <= y + 40:
                                        if letter not in player1.lets and letter and (not player2 or letter not in player2.lets):
                                            player1.lets.append(letter)
                                        else:
                                            player1.lets.remove(letter)

                            # check the second group of letters
                            if player2:
                                for i, letter in enumerate(player2.letters):
                                    x = playX + (len(player1.letters) * 50) + 10 + i * 50
                                    y = playY + buttonY

                                    if x <= event.pos[0] <= x + 40 and y <= event.pos[1] <= y + 40:
                                        if letter not in player2.lets and letter not in player2.lets:
                                            player2.lets.append(letter)
                                        else:
                                            player2.lets.remove(letter)

        #-=-=-=-=-=-=-=-=-=-==-==-=-=-=-=-=-=-=-=-=
        #-=-=-=-=-=-=-=-=-=-==-==-=-=-=-=-=-=-=-=-=
        #-=-=-=-=-=-=-=-=-=-==-==-=-=-=-=-=-=-=-=-=

        # pop the current dialog

        # The move the player is choosing to make
        if playerTurn and not curDialog:

            mouse_x, mouse_y = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()[0]

            buttonNames = ['Battle', 'Back'] if sideSelect else ['Battle', 'Split', 'Swap', 'Leave']
            button_width = 90
            button_height = 30
            button_spacing = 10
            border_radius = 1  # roundness

            for i, btn in enumerate(buttonNames):
                rect_x = playX - 120 + i * (button_width + button_spacing) if not sideSelect else  60 + i * (button_width + button_spacing)
                rect_y = playY - 60 
                rect = pygame.Rect(rect_x, rect_y, button_width, button_height)
                color = (25, 25, 25) if rect.collidepoint(mouse_x, mouse_y) else (125, 125, 124)
                color2 = (25, 25, 25) if rect.collidepoint(mouse_x, mouse_y) else (50, 50, 50)
                pygame.draw.rect(screen, color2, rect.inflate(8, 8), border_radius=border_radius)
                pygame.draw.rect(screen, color, rect, border_radius=border_radius)
                text_surface = font.render(btn, True, WHITE)
                text_rect = text_surface.get_rect(center=(rect_x + button_width // 2, rect_y + button_height // 2))
                screen.blit(text_surface, text_rect)


                if click and rect.collidepoint(mouse_x, mouse_y) and not showSwitchMenu:

                    if btn == "Battle" and (player1.lets or (player2 and player2.lets)): #----------------------------------------------------------
                        
                        # needAim(player)

                        if sideSelect:# the aiming for side select, which letter's need which side----------
                            LTarg = (SSC[0] or SSC[1])
                            RTarg = (SSC[2] or SSC[3])

                            if (not player1.lets) or LTarg or (not needAim(player1)):
                                if (not player2) or (not player2.lets) or RTarg or (not needAim(player2)):
                                    playerTurn = False
                                    sideSelect = False


                        else:
                            stamina_cost = player1.calculate_combo_stamina_cost()
                            if stamina_cost <= player1.comboStamina:
                                if (player1.lets or (player2 and player2.lets)) and enemy2:
                                    SSC = [None, None, None, None]
                                    if needAim(player1) or (player2 and needAim(player2)):
                                        sideSelect = True
                                    else:
                                        playerTurn = False
                                        sideSelect = False
                                elif (player1.lets or (player2 and player2.lets)) and not enemy2:
                                    SSC = [None, None, None, None]
                                    playerTurn = False
                                    
                    elif btn == "Battle":
                        curDialog.append("No letters selected!")
                        curDialog.append("Try Again")

                    elif btn == "Split" and (player1.lets and not player2): #----------------------------------------------------------
                        
                        curDialog.append(f"{player1.name} is Splitting ")
                        curDialog.append("Vulnerable to Attack")

                        doEnemyTurnOnly()

                        if player1.curHP > 1:
                            playerTurn = False # player chose to split (power of letter H)
                            separateDeity()
                            
                            curDialog.append(f"{player1.name}'s Split successful")
                            curDialog.append("")
                        else:
                            curDialog.append("Split failed")
                            curDialog.append(f"{player1.name}'s hp too low")
                        
                    elif btn == "Split":
                        if player2:
                            curDialog.append("Cannot Split Again")
                            curDialog.append("")
                        else:
                            curDialog.append("Please select letters")
                            curDialog.append("to become team.")
                    
                    elif btn == 'Swap' and not sideSelect:
                        showSwitchMenu = True # very simple

                    elif btn == 'Back' and sideSelect:
                        SSC = [None, None, None, None]
                        sideSelect = False
                        playerTurn = True


                    elif btn == 'Leave' and not sideSelect:
                        curDialog.append("Player Forfeited The Match")
                        curDialog.append("Enemy Wins")

                    pygame.time.delay(100)  # Wait for 1000 milliseconds (1 second)

        #-=-=-=-=-=-=-=-=-=-==-==-=-=-=-=-=-=-=-=-=
        #-=-=-=-=-=-=-=-=-=-==-==-=-=-=-=-=-=-=-=-=
        #-=-=-=-=-=-=-=-=-=-==-==-=-=-=-=-=-=-=-=-=

        draw_dialog()

        # Combate move decided ---END TURN---
        if not playerTurn and not sideSelect and not curDialog and not showSwitchMenu:

            turnMoves()

            

            playerTurn = True  # Reset for the next turn


        # display things
        if (not showSwitchMenu) or curDialog:
            if player1:
                drawDeity(player1, playX - 5, playY, True, sideSelect)
            if player2:
                drawDeity2(player2, playX + 12 + (len(player1.letters) * 50)   , playY, True, sideSelect)

            if enemy:
                drawDeity(enemy, enemX, enemY, False, playerTurn)
            if enemy2:
                drawDeity2(enemy2, enemX + 17 + (len(enemy.letters) * 50), enemY, False, playerTurn)

            # Draw input wordbox, current word being formed
            # font size is 36, 26
            if sideSelect:
                drawSideSelect()

            if not curDialog and not haveWinner:
                ipX, ipY = 75, playY + buttonY
                input_box = pygame.Rect(ipX, ipY, 26 * len(player1.letters), 40)
                pygame.draw.rect(screen, WHITE, input_box, 2)
                input_word = "".join([letter.char for letter in player1.lets])
                input_surface = font.render(input_word, True, WHITE)
                screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))

                # if there was a split, display the letters
                if player2:
                    secondStart = ipX + (26 * len(player2.letters))   + 80
                    input_box = pygame.Rect(secondStart, ipY, 26 * len(player2.letters), 40)
                    pygame.draw.rect(screen, WHITE, input_box, 2)
                    ipw2 = "".join([letter.char for letter in player2.lets])
                    input_surface = font.render(ipw2, True, WHITE)
                    screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))
        else:
            DeitySelect()

        
            
        

        # Check for game over amd/or force switch
        if not (player1 or player2) and not haveWinner and not showSwitchMenu:
            haveWinner = True
            if any(deity.curHP > 0 for deity in playerTeam): 
                haveWinner = False
                curDialog.append("Please Choose")
                curDialog.append("New Deity")
                showSwitchMenu = True
            else:  
                winner_name = enemy.name if enemy else "The Enemy"
                curDialog.append(f"{winner_name} WINS!!!!")

            

        if not (enemy or enemy2) and not haveWinner:  
            haveWinner = True
            if any(deity.curHP > 0 for deity in enemyTeam):
                haveWinner = False
                
                for i in range(1, len(enemyTeam)):
                    if enemyTeam[i].curHP > 0:
                        
                        switch(False, i)
                        curDialog.append(f"{enemyTeam[0].name} sent out")
                        curDialog.append("")
                        break
            else:  
                winner_name = player1.name if player1 else "Player"
                curDialog.append(f"{winner_name} WINS!!!!")
            

        if haveWinner and not curDialog:
            running = False

        # Update display
        pygame.display.flip()

    pygame.time.delay(100)  # Wait for 1000 milliseconds (1 second)

    # Quit PyGame
    pygame.quit()

# Run the game
if __name__ == "__main__":
    main()