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

def drawLetter(letter, x, y, selected=False, hovered=False, isPlayer1=True, playerChoose=True):
        global curDialog
        boxX, boxY = x, y
        curFont = font
        if hovered and not selected and isPlayer1 and not playerChoose and not curDialog:
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



    
def drawDeity(deity, x, y, isPlayer1, playerChoose):
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
            drawLetter(letter, newX, newY, letter in deity.lets, hovered, isPlayer1, playerChoose)

        # Display combo stamina (for player1)
        if isPlayer1:
            stamina_cost = player1.calculate_combo_stamina_cost()
            color = GREEN if stamina_cost <= deity.comboStamina else RED
            stamina_text = font.render(f"Combo Cost: {stamina_cost} / {deity.comboStamina}", True, color)
            screen.blit(stamina_text, (x + 20, y + 110))
        else:
            color = GREEN if 0 < deity.comboStamina else RED
            stamina_text = font.render(f"Enemy Stamina: {deity.comboStamina}", True, color)
            screen.blit(stamina_text, (x + 20, y + 110))




def drawDeity2(deity, x, y, isPlayer1, playerChoose):

        # Since this only draws the second set of letters, do not need to have much

        spaceBetweenGroups = 10

        for i, letter in enumerate(deity.letters):
            newX = x + i * 50 - 10
            newY = y + 50

            mouse_pos = pygame.mouse.get_pos()
            hovered = newX <= mouse_pos[0] <= newX + 40 and newY <= mouse_pos[1] <= newY + 40
            drawLetter(letter, newX, newY, letter in deity.lets, hovered, isPlayer1, playerChoose)


def get_random_letters():
    letter_options = ['A', 'A', 'B', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
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





def doCurTurn(person, target, isTargPlayer, TargRightSide):
    global player1, player2, enemy, enemy2, curDialog

    # If the current side is either null or knocked out
    if person.curHP <= 0 or target.curHP <= 0:
        return

    dmg = calculate_damage(person, target)

    # Determine which HP to update (left or right)
    peekHP = 0

    target.take_damage(dmg)  # Apply damage to the left side
    peekHP = target.curHP

    # Update dialog based on the result
    curDialog.append(f"{person.name} used '{' '.join([letter.char for letter in person.lets])}'")
    curDialog.append(f"It did {dmg} dmg!")

    if peekHP < 1:
        if target:
            curDialog.append(f"{target.name}'s fainted!")
            curDialog.append(f"")

        if isTargPlayer:
            if TargRightSide:
                player2 = None  # Remove player2
            else:
                player1 = player2  # Move player2 to player1's position
                player2 = None
        else:
            if TargRightSide:
                enemy2 = None  # Remove enemy2
            else:
                enemy = enemy2  # Move enemy2 to enemy's position
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
        if button_hover and click:
            switchSelected = i
        
        # Background color logic
        backColor = (0, 125, 50) if button_hover and switchSelected == -1 else (0, 0, 125)
        backColor = (0, 0, 0) if i == switchSelected else backColor
        pygame.draw.rect(screen, backColor, button_rect)
        pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)  # Black outline
        
        # Display the button name and HP
        input_word = f"{deity.name} HP: {deity.curHP}/{deity.maxHP}"
        input_surface = font.render(input_word, True, WHITE)
        screen.blit(input_surface, (x + xSpace, y + ySpace))
        
        y += button_height + 10  # Move y for the next button
    
    if switchSelected != -1:
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
        
        drawDeity(playerTeam[switchSelected], ppXX, ppYY, True, False)

        if yes_rect.collidepoint(mouse_x, mouse_y) and click:
            # Perform the switch logic (implement switching logic here)
            print(f"Switched to {playerTeam[switchSelected].name}")
            p2Lets = []
            for let in playerTeam[switchSelected].lets[:]:
                    p2Lets.append(let)  

            switch(True, switchSelected)

            for let in p2Lets:
                player1.lets.append(let)

            if player1.lets:
                separateDeity()

            switchSelected = -2  # Reset selection after switching
        
        if no_rect.collidepoint(mouse_x, mouse_y) and click:
            for let in playerTeam[switchSelected].lets[:]: 
                playerTeam[switchSelected].lets.remove(let)
            switchSelected = -1  # Cancel selection


# Draws --- Battle, Separate, Switch, Retreat
def battleOptionButtons():
    global playX, playY

    mouse_x, mouse_y = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()[0]

    buttonNames = ['Battle', 'Split', 'Swap', 'Leave']
    button_width = 90
    button_height = 30
    button_spacing = 10
    border_radius = 1  # Adjust for roundness

    for i, btn in enumerate(buttonNames):
        rect_x = playX - 120 + i * (button_width + button_spacing)
        rect_y = playY - 60
        rect = pygame.Rect(rect_x, rect_y, button_width, button_height)

        # Button color changes on hover
        color = (25, 25, 25) if rect.collidepoint(mouse_x, mouse_y) else (125, 125, 124)
        color2 = (25, 25, 25) if rect.collidepoint(mouse_x, mouse_y) else (50, 50, 50)

        # Draw outline first
        pygame.draw.rect(screen, color2, rect.inflate(8, 8), border_radius=border_radius)

        # Draw button inside the outline
        pygame.draw.rect(screen, color, rect, border_radius=border_radius)

        # Render and center the text
        text_surface = font.render(btn, True, WHITE)
        text_rect = text_surface.get_rect(center=(rect_x + button_width // 2, rect_y + button_height // 2))
        screen.blit(text_surface, text_rect)

        # Handle Click Event (if needed)
        if click and rect.collidepoint(mouse_x, mouse_y):
            print(f"{btn} button clicked!")  # Replace with actual functionality

# make buttons for splitting, switching, retreat?
# screen to see your team

def main():
    global curDialog, SSC, player1, player2, enemy, enemy2, switchSelected
    loadTeams()

    running = True
    playerChoose = True
    playerSplit = False
    sideSelect = False
    haveWinner = False

    showSwitchMenu = False
    while running:
        screen.fill(BLACK)

        # exit from switching
        if showSwitchMenu and switchSelected == -2:
            showSwitchMenu = False
            switchSelected = -1
            curDialog.append("Player Switched Deities!")
            if player2:
                curDialog.append("They also split in 2!")
            else:
                curDialog.append("")

        # Handle player input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    if curDialog and not sideSelect:
                        curDialog.pop(0) 
                        if curDialog:
                            curDialog.pop(0)

                    # ----------------------------------------------------------
                    # When Multiple Enemies, select which side to attack [button on click ]
                    elif sideSelect:
                        ipX, ipY = 75, playY + buttonY
                        secondStart = None if not (player2 and player2.lets) else ipX + (26 * len(player2.letters)) + 80

                        if player1 and player1.lets:
                            if ipX <= event.pos[0] <= ipX + 20 and ipY + 45 <= event.pos[1] <= ipY + 65:
                                SSC[0] = not SSC[0]
                                SSC[1] = False
                            elif ipX + 40 <= event.pos[0] <= ipX + 60 and ipY + 45 <= event.pos[1] <= ipY + 65:
                                SSC[1] = not SSC[1]  
                                SSC[0] = False

                        if player2 and player2.lets:
                            if secondStart <= event.pos[0] <= secondStart + 20 and ipY + 45 <= event.pos[1] <= ipY + 65:
                                SSC[2] = not SSC[2]  
                                SSC[3] = False
                            elif secondStart + 40 <= event.pos[0] <= secondStart + 60 and ipY + 45 <= event.pos[1] <= ipY + 65:
                                SSC[3] = not SSC[3]  
                                SSC[2] = False


                    elif playerChoose:

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


                if event.button == 3:
                    if sideSelect:
                        sideSelect = False
                        playerChoose = True


            elif event.type == pygame.KEYDOWN:

                # ---SPLIT-----------------------------------------------------------------------------------------------------
                 # ---SPLIT-----------------------------------------------------------------------------------------------------
                if event.key == pygame.K_TAB and len(player1.lets) > 0 and not player2 and not sideSelect and not showSwitchMenu:  # player1.lists[-1].name == "H" and 

                    # let enemy attack first
                    listBySpeed = []

                    if enemy:
                        enemy.lets = enemy_choose_letters(enemy)
                        listBySpeed.append((enemy, player1, True, False))
                    if enemy2:
                        enemy2.lets = enemy_choose_letters(enemy2)
                        listBySpeed.append((enemy2, player1, True, True))
                    for person, target, isTargPlayer, TargRightSide in listBySpeed:
                        doCurTurn(person, target, isTargPlayer, TargRightSide)

                    playerChoose = False # player chose to split (power of letter H)
                    playerSplit = True
                    separateDeity()


                    

                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT :
                    # player1.lets.remove(letter)--------------the player stores the currently selected letters
                    showSwitchMenu = not showSwitchMenu

                # [SPACE]
                if (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE) and not showSwitchMenu: 

                    if curDialog:
                        curDialog.pop(0) 
                        if curDialog:
                            curDialog.pop(0)

                    # the aiming for side select, which letter's need which side----------
                    elif sideSelect:
                        # probably not the best way

                        # check not None/null
                        # perhaps check if .lets not null and contains 'a' or 'b'?????????
                        if ((not player1.lets or (SSC[0] or SSC[1])) and (not (player2 and player2.lets) or (SSC[2] or SSC[3]))):
                            if not (player2 and player2.lets) or (SSC[2] or SSC[3]):
                                sideSelect = False
                                playerChoose = False
                            

                    else:
                        # Calculate stamina cost for the selected letters
                        stamina_cost = player1.calculate_combo_stamina_cost()

                        if stamina_cost <= player1.comboStamina:
                            # If more than 1 letter is selected and enough stamina
                            playerChoose = False

                            if (player1.lets or (player2 and player2.lets)) and enemy2:
                                sideSelect = True

        draw_dialog()

        # Combate move decided ---END TURN---
        if not playerChoose and not curDialog and not sideSelect and not showSwitchMenu:
            if playerSplit:
                
                # Let enemy attack the player???
            
                player1.lets = []
                player2.lets = []
                playerSplit = False


            # Player has their words and also which target to hit ----------------- 
            elif player1.lets or (player2 and player2.lets):

                # Randomize enemy attack
                enemy.lets = enemy_choose_letters(enemy)
                if enemy2:
                    enemy2.lets = enemy_choose_letters(enemy2)

                # False = left, True = Right (rare one)
                playTarg1 = enemy2 if SSC[1] else enemy 
                playTarg2 = enemy2 if SSC[3] else enemy  

                enemTarg1 = player1 if not player2 else random.choice([player1, player2])  
                enemTarg2 = player1 if not player2 else random.choice([player1, player2])  

                listBySpeed = []

                if player1 and player1.lets:
                    listBySpeed.append((player1, playTarg1, False, False))
                if player2 and player2.lets:
                    listBySpeed.append((player2, playTarg2, False, True))

                if enemy and enemy.lets:
                    listBySpeed.append((enemy, enemTarg1, True, False))
                if enemy2 and enemy2.lets:
                    listBySpeed.append((enemy2, enemTarg2, True, True))

                #   --organize by speed later, idk what crahs bug---     listBySpeed.sort(key=lambda x: x[], reverse=True)

                # Process each move
                for person, target, isTargPlayer, TargRightSide in listBySpeed:
                    doCurTurn(person, target, isTargPlayer, TargRightSide)
                    
                
                SSC = [None, None, None, None]

            else:
                curDialog.append("No letters selected!")
                curDialog.append("Try Again")

            playerChoose = True  # Reset for the next turn


        # display things
        if not showSwitchMenu:
            drawDeity(player1, playX, playY, True, sideSelect)
            if player2:
                drawDeity2(player2, playX + 10 + (len(player1.letters) * 50)   , playY, True, sideSelect)

            drawDeity(enemy, enemX, enemY, False, playerChoose)
            if enemy2:
                drawDeity2(enemy2, enemX + 10 + (len(enemy.letters) * 50), enemY, False, playerChoose)

            # Draw input wordbox, current word being formed
            # font size is 36, 26
            if sideSelect:
                drawSideSelect()

            battleOptionButtons()

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
        
            
        

        # Check for game over
        if not player1 and not player2 and not haveWinner:
            curDialog.append(f"{enemy.name}   WINS!!!!")
            haveWinner = True
        elif not enemy and not enemy2 and not haveWinner:
            curDialog.append(f"{player1.name}   WINS!!!!")
            haveWinner = True

        if haveWinner and not curDialog:
            running = False



        # Update display
        pygame.display.flip()

    pygame.time.delay(10)  # Wait for 1000 milliseconds (1 second)

    # Quit PyGame
    pygame.quit()

# Run the game
if __name__ == "__main__":
    main()