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

# Fonts
font = pygame.font.Font(None, 38)
bigfont = pygame.font.Font(None, 48)

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
        border_color = (0, 155, 255) if selected else (255, 255, 255)
        pygame.draw.rect(screen, border_color, (boxX, boxY, rect_size, rect_size), 3)
        text = curFont.render(letter.char, True, border_color)
        screen.blit(text, (x + 10, y + 10))



    
def drawDeity(deity, x, y, isPlayer1, playerChoose):
        global player2
        text = font.render(f"{deity.name} (HP: {deity.curHP})", True, deity.battleColor)

        second = player2 if player2 and isPlayer1 else None
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


playX, playY = 520, 432
enemX, enemY = 40, 30
buttonY = 50

# This will store the state of the radio buttons: False (not clicked), True (clicked)
SSC = [False, False, False, False]

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



curDialog = []

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
    pygame.draw.rect(screen, backColor if not SSC[0] else selectedColor, (ipX, ipY + 45, 20, 20))
    pygame.draw.rect(screen, backColor if not SSC[1] else selectedColor, (ipX + 40, ipY + 45, 20, 20))

    # if you have multiple words
    if player1.lets2:
        secondStart = ipX + (26 * len(player1.letters2))   + 80
        pygame.draw.rect(screen, backColor if not SSC[2] else selectedColor, (secondStart, ipY + 45, 20, 20))
        pygame.draw.rect(screen, backColor if not SSC[3] else selectedColor, (secondStart + 40, ipY + 45, 20, 20))


player1 = deity.Deity("Gunther", get_random_letters())
player2 = None # copy.deepcopy(player1)
#player1.letters = player1.letters[:3]
#player2.letters = player2.letters[3:]

enemy = deity.Deity("Hugh Janus", get_random_letters())
enemy2 = copy.deepcopy(enemy)
enemy.letters = enemy.letters[:3]
enemy2.letters = enemy2.letters[3:]

def main():
    global curDialog, SSC, player1, player2, enemy, enemy2

    running = True
    playerChoose = True
    playerSplit = False
    sideSelect = False
    haveWinner = False
    while running:
        screen.fill(BLACK)

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
                    # when multiple enemy out, which one to attack -- [BUTTONS CLICKS]
                    elif sideSelect:
                        ipX, ipY = 75, playY + buttonY
                        secondStart = ipX + (26 * len(player2.letters)) + 80 if player2.lets else None
                        if ipX <= event.pos[0] <= ipX + 20 and ipY + 45 <= event.pos[1] <= ipY + 65:
                            SSC[0] = not SSC[0]
                            SSC[1] = False
                        elif ipX + 40 <= event.pos[0] <= ipX + 60 and ipY + 45 <= event.pos[1] <= ipY + 65:
                            SSC[1] = not SSC[1]  
                            SSC[0] = False
                        if player1.lets2:
                            if secondStart <= event.pos[0] <= secondStart + 20 and ipY + 45 <= event.pos[1] <= ipY + 65:
                                SSC[2] = not SSC[2]  
                                SSC[3] = False
                            elif secondStart + 40 <= event.pos[0] <= secondStart + 60 and ipY + 45 <= event.pos[1] <= ipY + 65:
                                SSC[3] = not SSC[3]  
                                SSC[2] = False


                    elif playerChoose:

                        # Check for the first group of letters
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

                # ---SPLIT--- This splits the letters into 2, ones not selected go to the other
                if event.key == pygame.K_TAB and len(player1.lets) > 0 and not player2 and not sideSelect:  # player1.lists[-1].name == "H" and 

                    p2Lets = []

                    for let in player1.letters[:]:
                        if let not in player1.lets:
                            p2Lets.append(let)  
                            player1.letters.remove(let)


                    playerChoose = False # player chose to split (power of letter H)
                    playerSplit = True
                    # player1.update_stamina(1) # costs 1 stamina
                    player1.lets = []

                    # Update stats in the split
                    calcHP = len(player1.letters) / (len(player1.letters)+len(p2Lets))
                    player1.curHP = int(player1.maxHP * calcHP)
                    curHP2 = int(player1.maxHP - player1.curHP)
                    player1.speed = int(player1.maxSpeed * calcHP)
                    speed2 = int(player1.maxSpeed - player1.maxSpeed)

                    # make it an entirely new deity
                    player2 = copy.deepcopy(player1)
                    player2.letters = p2Lets
                    player2.curHP = curHP2
                    player2.speed = speed2

                    curDialog.append("Player Split their words")
                    curDialog.append("Now You Can make 2 words")

                # [SPACE]
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:

                    if curDialog:
                        curDialog.pop(0) 
                        if curDialog:
                            curDialog.pop(0)
                    elif sideSelect:
                        if (SSC[0] or SSC[1]):
                            if not player1.lets2 or (SSC[2] or SSC[3]):
                                sideSelect = False
                                playerChoose = False
                            

                    else:
                        # Calculate stamina cost for the selected letters
                        stamina_cost = player1.calculate_combo_stamina_cost()

                        if stamina_cost <= player1.comboStamina:
                            # If more than 1 letter is selected and enough stamina
                            playerChoose = False

                            if player1.lets and enemy.letters2:
                                sideSelect = True

        draw_dialog()

        # Combate move decided ---END TURN---
        if not playerChoose and not curDialog and not sideSelect:
            if playerSplit:
                
                # Let enemy attack the player???
            
                player1.lets = []
                player2.lets = []
                playerSplit = False


            # Player has their words and also which target to hit ----------------- 
            elif player1.lets or (player2 and player2.lets):
                # False = left, True = Right (rare one)
                playTarg1 = True if SSC[1] else False  
                playTarg2 = True if SSC[3] else False  

                enemTarg1 = False if not player2 else random.choice([False, True])  
                enemTarg2 = False if not player2 else random.choice([False, True])  

                listBySpeed = []

                if player1:
                    listBySpeed.append((player1, playTarg1, False, False))
                if player2:
                    listBySpeed.append((player2, playTarg2, False, True))

                if enemy:
                    listBySpeed.append((enemy, enemTarg1, True, False))
                if enemy:
                    listBySpeed.append((enemy2, enemTarg2, True, True))

                #   --organize by speed later, idk what crahs bug---     listBySpeed.sort(key=lambda x: x[], reverse=True)

                # Process each move
                for person, target, isTargPlayer, TargRightSide in listBySpeed:
                    
                    # If the current side is either null or knocked out
                    if person.curHP <= 0 or target.curHP <= 0:
                        continue

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

                        #if TargRightSide:
                        #    target = None
                        if not TargRightSide:
                            # If the left side died, move the left to the right
                            point2 = player2 if isTargPlayer else enemy2
                            target = copy.deepcopy(point2)
                            point2 = None

                # Reset things
                player1.update_stamina(player1.calculate_combo_stamina_cost())
                player1.lets = []
                if player2:
                    player2.lets = []
                SSC = [False, False, False, False]

            else:
                curDialog.append("No letters selected!")
                curDialog.append("Try Again")

            playerChoose = True  # Reset for the next turn

        # Draw players
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
        
            
        

        # Check for game over
        if player1.curHP <= 0 and player2.curHP <= 0 and not haveWinner:
            curDialog.append(f"{enemy.name}   WINS!!!!")
            haveWinner = True
        elif enemy.curHP <= 0 and enemy2.curHP <= 0 and not haveWinner:
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
