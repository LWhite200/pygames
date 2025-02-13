import pygame
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
    "red": ["blue", "green"],     # Red is weak to Blue and Green
    "orange": ["purple", "blue"], # Orange is weak to Purple and Blue
    "yellow": ["orange", "green"], # Yellow is weak to Orange and Green
    "green": ["red", "purple"],   # Green is weak to Red and Purple
    "blue": ["yellow", "purple"], # Blue is weak to Yellow and Purple
    "purple": ["green", "yellow"], # Purple is weak to Green and Yellow
    "grey": ["red", "blue"],      # Grey is weak to Red and Blue
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

    def draw(self, x, y, selected=False):
        color = (0,155,255) if selected else (255,255,255)
        pygame.draw.rect(screen, self.color1, (x, y, 40, 40))
        pygame.draw.rect(screen, color, (x, y, 40, 40), 3)
        text = font.render(self.char, True, (255,255,255))
        screen.blit(text, (x + 10, y + 10))

class Deity:
    def __init__(self, name, letters):
        self.name = name
        self.letters = letters  # List of Letter objects
        self.maxHP = 100
        self.curHP = self.maxHP
        self.speed = random.randint(50, 101)
        self.comboStamina = 5
        self.physical = 100
        self.special = 100
        self.selected_letters = []  # Initialize selected_letters
        self.battleType = self.randType()

    def take_damage(self, damage):
        self.curHP -= damage
        if self.curHP < 0:
            self.curHP = 0

    def draw(self, x, y, isPlayer1):
        text = font.render(f"{self.name} (HP: {self.curHP})", True, color_mapping(self.battleType))
        screen.blit(text, (x + 20, y + 10))

        # Draw letters
        for i, letter in enumerate(self.letters):
            letter.draw(x + i * 50, y + 50, letter in self.selected_letters)

        # Display combo stamina
        if isPlayer1:
            stamina_cost = player1.calculate_combo_stamina_cost()
            color = GREEN if stamina_cost <= self.comboStamina else RED
            stamina_text = font.render(f"Combo Cost: {stamina_cost} / {self.comboStamina}", True, color)
            screen.blit(stamina_text, (x + 20, y + 110))

    def calculate_combo_stamina_cost(self):
        # Only calculate stamina cost if more than one letter is selected
        if len(self.selected_letters) > 1:
            return sum(letter.tier for letter in self.selected_letters[1:])  # Skip the first letter
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
    num_letters = random.randint(1, 3)
    chosen_letters = random.sample(enemy.letters, num_letters)
    return chosen_letters

player1 = Deity("Gunther", get_random_letters())
player2 = Deity("Hugh Janus", get_random_letters())

cur_word = []
message1 = ""
message2 = ""

playX = 520
enemX = 20

playY = 400
enemY = 30

buttonY = 50

def calculate_damage(word, opponent_deity):

    base_damage = 0 # sum(letter.power for letter in word)
    
    for letter in word:
        curType = letter.battleType
        curDmg = letter.power
        oppType = opponent_deity.battleType
        
        # Checks each type and adds or subracts accordingly
        if curType in weaknesses[oppType]:
            base_damage += curDmg + 10
            print("weakness hit")
        elif curType in resistances[oppType]:
            base_damage += (curDmg // 2)
            print("resistance yes")
        else:
            base_damage += curDmg

    return base_damage


def main():
    global cur_word, message1, message2

    running = True
    playerChoose = True
    while running:
        screen.fill(BLACK)

        # Handle player input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, letter in enumerate(player1.letters):
                        x = playX + i * 50
                        y = playY + buttonY

                        if x <= event.pos[0] <= x + 40 and y <= event.pos[1] <= y + 40:
                            if letter not in cur_word:
                                cur_word.append(letter)
                                player1.selected_letters.append(letter)

                if event.button == 3:
                    if cur_word:
                        removed_letter = cur_word.pop()
                        player1.selected_letters.remove(removed_letter)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Calculate stamina cost for the selected letters
                    stamina_cost = player1.calculate_combo_stamina_cost()

                    if stamina_cost <= player1.comboStamina:
                        # If more than 1 letter is selected and enough stamina
                        playerChoose = False
                        player1.update_stamina(stamina_cost)

        # When the player has made their choice, see who to attack first
        if not playerChoose:
            if cur_word:


                p1, p2 = player1, player2
                move1, move2 = cur_word, enemy_choose_letters(player2)

                # flip if opposing player fastter
                if player2.speed > player1.speed:
                    p1, p2 = player2, player1
                    move1, move2 = move2, move1

                dmg1 = calculate_damage(move1, p2)
                p2.take_damage(dmg1)

                dmg2 = calculate_damage(move2, p1)
                p1.take_damage(dmg2)
            
                cur_word = []
                player1.selected_letters = []
                message1 = f"{p2.name} hit by '{' '.join([letter.char for letter in move1])}' for {dmg1} dmg!"
                message2 = f"{p1.name} hit by '{' '.join([letter.char for letter in move2])}' for {dmg2} dmg!"

            else:
                message1 = "No letters selected!"
                message2 = "     Try Again"

            playerChoose = True  # Reset for the next turn

        # Draw players
        player1.draw(playX, playY, True)
        player2.draw(enemX, enemY, False)

        # Draw input word
        input_box = pygame.Rect(50, playY + buttonY, 200, 40)
        pygame.draw.rect(screen, WHITE, input_box, 2)
        input_word = "".join([letter.char for letter in cur_word])
        input_surface = font.render(input_word, True, WHITE)
        screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))

        # Draw messages ------------
        def drawMessage():
            message_surface = font.render(message1, True, (200,200,200))
            screen.blit(message_surface, (100, HEIGHT // 2))
            message_surface = font.render(message2, True, WHITE)
            screen.blit(message_surface, (100, HEIGHT // 2 + 50))

        # Check for game over
        if player1.curHP <= 0:
            message1 = f"{player2.name}   WINS!!!!"
            message2 = ""
            running = False
        elif player2.curHP <= 0:
            message2 = f"{player1.name}   WINS!!!!"
            message2 = ""
            running = False

        drawMessage()

        # Update display
        pygame.display.flip()

    pygame.time.delay(3000)  # Wait for 1000 milliseconds (1 second)

    # Quit PyGame
    pygame.quit()

# Run the game
if __name__ == "__main__":
    main()
