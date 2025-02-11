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

# Letter class
class Letter:
    def __init__(self, char):
        self.char = char.upper()
        self.type = random.randint(0, 11)  # Random type for variety - do later
        self.power = 50 if self.char in ["A", "B"] else 0
        self.tier = random.randint(0, 5)
        self.accuracy = 100

    def draw(self, x, y, selected=False):
        color = BLUE if selected else WHITE
        pygame.draw.rect(screen, color, (x, y, 40, 40), 2)
        text = font.render(self.char, True, WHITE)
        screen.blit(text, (x + 10, y + 10))

# Deity class
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

    def take_damage(self, damage):
        self.curHP -= damage
        if self.curHP < 0:
            self.curHP = 0

    def draw(self, x, y):
        text = font.render(f"{self.name} (HP: {self.curHP})", True, WHITE)
        screen.blit(text, (x, y))
        for i, letter in enumerate(self.letters):
            letter.draw(x + i * 50, y + 40, letter in self.selected_letters)

def get_random_letters():
    letter_options = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    return [Letter(random.choice(letter_options)) for _ in range(5)]


def enemy_choose_letters(enemy):
    # Enemy randomly selects 1-3 letters to form a word
    num_letters = random.randint(1, 3)
    chosen_letters = random.sample(enemy.letters, num_letters)
    return chosen_letters

player1 = Deity("AERIS", get_random_letters())
player2 = Deity("ZORAN", get_random_letters())

cur_word = []
message = ""

playX = 520
enemX = 20

playY = 500
enemY = 30

def calculate_damage(word):
    # Simple damage calculation: sum of the power of the letters
    return sum(letter.power for letter in word)

def main():
    global cur_word, message

    running = True
    playerChoose = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # What moves the player chooses - button clicking
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, letter in enumerate(player1.letters):
                        x = playX + i * 50
                        y = playY + 50

                        if x <= event.pos[0] <= x + 40 and y <= event.pos[1] <= y + 40:
                            if letter not in cur_word:
                                cur_word.append(letter)
                                player1.selected_letters.append(letter)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    playerChoose = False

                elif event.key == pygame.K_BACKSPACE:
                    if cur_word:
                        removed_letter = cur_word.pop()
                        player1.selected_letters.remove(removed_letter)

        # When the player has made their choice, see who to attack first
        if not playerChoose:
            if cur_word:

                enem_choice = enemy_choose_letters(player2)

                firstGroup = cur_word
                secondGroup = enem_choice

                firstPlayer, secondPlayer = (player1, player2) if player1.speed >= player2.speed else (player2, player1)
                firstGroup, secondGroup = (cur_word, enem_choice) if player1.speed >= player2.speed else (enem_choice, cur_word)

                dmg1 = calculate_damage(firstGroup)
                secondPlayer.take_damage(dmg1)

                dmg2 = calculate_damage(secondGroup)
                firstPlayer.take_damage(dmg2)

                cur_word = []
                player1.selected_letters = []
                message = f"{firstPlayer.name} attacks first! Damage dealt: {dmg1}"
            else:
                message = "No letters selected!"

            playerChoose = True  # Reset for the next turn

        # Draw players
        player1.draw(playX, playY)
        player2.draw(enemX, enemY)

        # Draw input word
        input_box = pygame.Rect(50, 500, 200, 40)
        pygame.draw.rect(screen, WHITE, input_box, 2)
        input_word = "".join([letter.char for letter in cur_word])
        input_surface = font.render(input_word, True, WHITE)
        screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))

        # Draw message
        message_surface = font.render(message, True, RED)
        screen.blit(message_surface, (50, 550))

        # Check for game over
        if player1.curHP <= 0:
            message = f"{player2.name} wins!"
            running = False
        elif player2.curHP <= 0:
            message = f"{player1.name} wins!"
            running = False

        # Update display
        pygame.display.flip()

    # Quit PyGame
    pygame.quit()

# Run the game
if __name__ == "__main__":
    main()