import pygame # type: ignore
import random

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
font = pygame.font.Font(None, 36)
bigfont = pygame.font.Font(None, 48)

def color_mapping(color_name):
    color_dict = {
        "red": (255, 0, 0),
        "orange": (255, 165, 0),
        "yellow": (225, 225, 0),
        "green": (0, 215, 0),
        "blue": (0, 0, 255),
        "purple": (128, 0, 128),
        "black": (50, 50, 50),
        "white": (255, 255, 255),
        "grey": (169, 169, 169),
        None: (20, 20, 20), 
    }
    return color_dict.get(color_name, (0, 0, 0))

# type weakness and resistances
weaknesses = {
    "red": ["blue", "green"],    
    "orange": ["purple", "blue"], 
    "yellow": ["orange", "green"], 
    "green": ["red", "purple"],   
    "blue": ["yellow", "purple"], 
    "purple": ["green", "yellow"],
    "grey": ["red", "blue"],    
}

resistances = {
    "red": ["green", "yellow"],    # Red resists Green and Yellow
    "orange": ["yellow", "purple"], # Orange resists Yellow and Purple
    "yellow": ["red", "blue"],     # Yellow resists Red and Blue
    "green": ["blue", "orange"],   # Green resists Blue and Orange
    "blue": ["purple", "green"],   # Blue resists Purple and Green
    "purple": ["orange", "red"],   # Purple resists Orange and Red
    "grey": ["green", "purple"],   # Grey resists Green and Purple
}


# Letter class
class Letter:
    def __init__(self, char):
        self.char = char.upper()
        self.battleType = self.ranColor()
        self.color1 = color_mapping(self.battleType)
        self.power = 50 if self.char in ["A", "B"] else 10
        self.tier = random.randint(0, 2) # the stamina it takes to use in a combo
        print(str(self.tier))
        self.accuracy = 100

    def ranColor(self):
        colors = ["red", "orange", "yellow", "green", "blue", "purple", "grey"]
        ccc = random.choice(colors)
        print(str(ccc))
        return ccc

    def draw(self, x, y, selected=False, hovered=False, isPlayer1=True, playerChoose=True):
        # Adjust size and color if hovered and not selected
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
            color = tuple(max(0, c - 75) for c in self.color1)  # Darker color
        else:
            rect_size = 40
            color = self.color1

        pygame.draw.rect(screen, color, (boxX, boxY, rect_size, rect_size))
        border_color = (0, 155, 255) if selected else (255, 255, 255)
        pygame.draw.rect(screen, border_color, (boxX, boxY, rect_size, rect_size), 3)
        text = curFont.render(self.char, True, border_color)
        screen.blit(text, (x + 10, y + 10))

class Deity:
    def __init__(self, name, letters, startMultipleDebug):
        self.name = name
        self.maxHP = 100
        self.maxSpeed = random.randint(50, 101)

        if startMultipleDebug:
            self.letters = letters[:3]  # List of Letter objects
            self.letters2 = letters[3:]  # empty

            calcHP = len(self.letters) / (len(self.letters)+len(self.letters2))
            self.curHP = int(self.maxHP * calcHP)
            self.curHP2 = int(self.maxHP - self.curHP)

            self.speed = int(self.maxSpeed * calcHP)
            self.speed2 = int(self.maxSpeed - self.maxSpeed)
        else:
            self.letters = letters  # List of Letter objects
            self.letters2 = []  # empty
            self.curHP = self.maxHP
            self.curHP2 = 0
            self.speed = self.maxSpeed
            self.speed2 = 0

        self.comboStamina = 5
        self.physical = 100
        self.special = 100
        self.lets = []  # Initialize lets
        self.lets2 = []  # Initialize lets
        self.battleType = self.randType()

    def take_damage(self, damage):
        self.curHP -= damage
        if self.curHP < 0:
            self.curHP = 0

    def take_damage2(self, damage):
        self.curHP2 -= damage
        if self.curHP2 < 0:
            self.curHP2 = 0

    def draw(self, x, y, isPlayer1, playerChoose):
        text = font.render(f"{self.name} (HP: {self.curHP})", True, color_mapping(self.battleType))
        if self.letters2:
            text = font.render(f"{self.name} ({self.curHP}) | ({self.curHP2})", True, color_mapping(self.battleType))
        screen.blit(text, (x - 10, y + 10))

        spaceBetweenGroups = 5  # The space between the two groups of letters

        # Draw letters in the first group (self.letters), offset a bit to the left
        for i, letter in enumerate(self.letters):
            newX = x + i * 50 - 10  if not self.letters2 else x + i * 50 - 10
            newY = y + 50

            mouse_pos = pygame.mouse.get_pos()
            hovered = newX <= mouse_pos[0] <= newX + 40 and newY <= mouse_pos[1] <= newY + 40
            letter.draw(newX, newY, letter in self.lets or letter in self.lets2, hovered, isPlayer1, playerChoose)

        # Draw letters in the second group (self.letters2), to the right of the first group
        for i, letter in enumerate(self.letters2):
            newX = x + (len(self.letters) * 50) + spaceBetweenGroups + i * 50  # Positioning to the right of the first group
            newY = y + 50

            mouse_pos = pygame.mouse.get_pos()
            hovered = newX <= mouse_pos[0] <= newX + 40 and newY <= mouse_pos[1] <= newY + 40
            letter.draw(newX, newY, letter in self.lets or letter in self.lets2, hovered, isPlayer1, playerChoose)

        # Display combo stamina (for player1)
        if isPlayer1:
            stamina_cost = player1.calculate_combo_stamina_cost()
            color = GREEN if stamina_cost <= self.comboStamina else RED
            stamina_text = font.render(f"Combo Cost: {stamina_cost} / {self.comboStamina}", True, color)
            screen.blit(stamina_text, (x + 20, y + 110))


    def calculate_combo_stamina_cost(self):
        # Only calculate stamina cost if more than one letter is selected (from both lets and lets2)
        if len(self.lets) + len(self.lets2) > 1:
            # Combine both lets and lets2, and calculate the sum of tiers, skipping the first letter
            combined_letters = self.lets + self.lets2
            return sum(letter.tier for letter in combined_letters[1:])  # Skip the first letter
        return 0  # No cost for a single letter


    
    def update_stamina(self, cost):
        self.comboStamina -= cost
        if self.comboStamina < 0:
            self.comboStamina = 0

    def randType(self):
        colors = ["red", "orange", "yellow", "green", "blue", "purple", "grey"]
        return random.choice(colors)


def get_random_letters():
    letter_options = ['A', 'A', 'B', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    return [Letter(random.choice(letter_options)) for _ in range(5)]


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

# word = word Attacking   |   opp = deity being attacked (left and right side have same type/defense)
def calculate_damage(word, opp):
    global curDialog

    aboveOrBelow = sum(letter.power for letter in word)
    base_damage = 0 # sum(letter.power for letter in word)
    
    for letter in word:
        curType = letter.battleType
        curDmg = letter.power
        oppType = opp.battleType
        
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






player1 = Deity("Gunther", get_random_letters(), False)
player2 = Deity("Hugh Janus", get_random_letters(), True)

def main():
    global curDialog, SSC

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
                        secondStart = ipX + (26 * len(player1.letters2)) + 80 if player1.lets2 else None
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
                            x = playX + i * 50 - 10  if not player1.letters2 else playX + i * 50 - 10
                            y = playY + buttonY

                            if x <= event.pos[0] <= x + 40 and y <= event.pos[1] <= y + 40:
                                if letter not in player1.lets and letter not in player1.lets2:
                                    player1.lets.append(letter)
                                else:
                                    player1.lets.remove(letter)

                        # check the second group of letters
                        if player1.letters2:
                            for i, letter in enumerate(player1.letters2):
                                x = playX + (len(player1.letters) * 50) + 5 + i * 50
                                y = playY + buttonY

                                if x <= event.pos[0] <= x + 40 and y <= event.pos[1] <= y + 40:
                                    if letter not in player1.lets2 and letter not in player1.lets:
                                        player1.lets2.append(letter)
                                    else:
                                        player1.lets2.remove(letter)


                if event.button == 3:
                    if sideSelect:
                        sideSelect = False
                        playerChoose = True


            elif event.type == pygame.KEYDOWN:

                # ---SPLIT--- This splits the letters into 2, ones not selected go to the other
                if event.key == pygame.K_TAB and len(player1.lets) > 0 and not player1.letters2 and not sideSelect:  # player1.lists[-1].name == "H" and 
                    for let in player1.letters[:]:
                        if let not in player1.lets:
                            player1.letters2.append(let)  
                            player1.letters.remove(let)
                    playerChoose = False # player chose to split (power of letter H)
                    playerSplit = True
                    player1.update_stamina(1) # costs 1 stamina
                    player1.lets = player1.lets2 = []

                    # Update stats in the split
                    calcHP = len(player1.letters) / (len(player1.letters)+len(player1.letters2))
                    player1.curHP = int(player1.maxHP * calcHP)
                    player1.curHP2 = int(player1.maxHP - player1.curHP)
                    player1.speed = int(player1.maxSpeed * calcHP)
                    player1.speed2 = int(player1.maxSpeed - player1.maxSpeed)

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

                            if player1.lets and player2.letters2:
                                sideSelect = True

        draw_dialog()

        # Combate move decided ---END TURN---
        if not playerChoose and not curDialog and not sideSelect:
            if playerSplit:
                p1, p2 = player1, player2
                move1, move2 = player1.lets, enemy_choose_letters(player2)

                dmg2 = calculate_damage(move2, p1)
                p1.take_damage(dmg2)
                curDialog.append(f"{p2.name} used '{' '.join([letter.char for letter in move2])}' ")
                curDialog.append(f"It did {dmg2} dmg!")
            
                player1.lets = []
                player1.lets2 = []
                playerSplit = False


            # Player has their words and also which target to hit ----------------- {{{HERE HELP}}}
            # This is what you need to fix chat gpt or deepseek
            elif player1.lets:
                # False = left, True = Right (rare one)
                defaultTarg = True if (not player2.lets and player2.lets2) else False

                playTarg1 = True if SSC[1] else False  # player1.speed | player1.curHP
                playTarg2 = True if SSC[3] else False  # player1.speed2 | player1.curHP2
                play1 = player1.lets
                play2 = player1.lets2 if player1.lets2 else None

                enemTarg1 = False if not player2.letters2 else random.choice([False, True])  # player2.speed | player2.curHP
                enemTarg2 = False if not player2.letters2 else random.choice([False, True])  # player2.speed2 | player2.curHP2
                enem1 = player2.letters
                enem2 = player2.letters2 if player2.letters2 else None

                listBySpeed = []

                # Add player moves to the list
                if play1:
                    listBySpeed.append((player1, play1, playTarg1, player1.speed, player2))
                if play2:
                    listBySpeed.append((player1, play2, playTarg2, player1.speed2, player2))

                # Add enemy moves to the list
                if enem1:
                    listBySpeed.append((player2, enem1, enemTarg1, player2.speed, player1))
                if enem2:
                    listBySpeed.append((player2, enem2, enemTarg2, player2.speed2, player1))

                # Sort by speed (higher speed first)
                listBySpeed.sort(key=lambda x: x[3], reverse=True)

                # Process each move
                for person, move, target, speed, targDeity in listBySpeed:
                    dmg = calculate_damage(move, targDeity)

                    # Determine which HP to update (left or right)
                    if target:  # Target is right
                        targDeity.take_damage2(dmg)  # Apply damage to the right side
                        peekHP = targDeity.curHP2
                    else:  # Target is left
                        targDeity.take_damage(dmg)  # Apply damage to the left side
                        peekHP = targDeity.curHP

                    # Update dialog based on the result
                    if peekHP > 0:
                        curDialog.append(f"{person.name} used '{' '.join([letter.char for letter in move])}'")
                        curDialog.append(f"It did {dmg} dmg!")
                    else:
                        curDialog.append(f"{targDeity.name}'s {'right' if target else 'left'} side fainted!")

                # Reset things
                stamina_cost = player1.calculate_combo_stamina_cost()
                player1.update_stamina(stamina_cost)
                player1.lets = []
                player1.lets2 = []
                SSC = [False, False, False, False]

            else:
                curDialog.append("No letters selected!")
                curDialog.append("Try Again")

            playerChoose = True  # Reset for the next turn

        # Draw players
        player1.draw(playX, playY, True, sideSelect)
        player2.draw(enemX, enemY, False, playerChoose)

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
            if player1.letters2:
                secondStart = ipX + (26 * len(player1.letters2))   + 80
                input_box = pygame.Rect(secondStart, ipY, 26 * len(player1.letters2), 40)
                pygame.draw.rect(screen, WHITE, input_box, 2)
                ipw2 = "".join([letter.char for letter in player1.lets2])
                input_surface = font.render(ipw2, True, WHITE)
                screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))
        
            
        

        # Check for game over
        if player1.curHP <= 0 and player1.curHP2 <= 0 and not haveWinner:
            curDialog.append(f"{player2.name}   WINS!!!!")
            haveWinner = True
        elif player2.curHP <= 0 and player2.curHP2 <= 0 and not haveWinner:
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
