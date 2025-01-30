" Updated version of the WordBound I made for Wii "

import pygame # type: ignore
import random
import string
import sys

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("1v1 Battle")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (169, 169, 169)
BUTTON_COLOR = (100, 100, 100) 
BUTTON_HOVER_COLOR =  (50, 50, 50)  
button_width = 110
button_height = 55

sos = 10 # scale of stuff

# Define fonts
font = pygame.font.SysFont('Arial', 35)
font2 = pygame.font.SysFont('Arial', sos *4)

# Letter class (already defined by you)
class letter:
    def __init__(self):
        self.name = self.ranName()
        self.color1, self.color2 = self.ranColor()
        self.level = self.ranLevel()
        self.maxHP = self.ranHP()
        self.hp = self.maxHP
        self.power = self.ranPower()
        self.defense = self.ranDefense()
        self.speed = self.ranSpeed()
        self.accuracy = self.ranAccuracy()
        self.evasive = self.ranEvasive()
        self.luck = self.ranLuck()
        self.isAttacking = False

    def ranName(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=4))

    def ranColor(self):
        colors = ["red", "orange", "yellow", "green", "blue", "purple", "white", "grey", None]
        color1 = random.choice(colors)
        color2 = random.choice(colors)
        while color1 == color2:
            color2 = random.choice(colors)
        return color1, color2

    def ranLevel(self):
        return random.randint(1, 100)

    def ranHP(self):
        return random.randint(50, 200)

    def ranPower(self):
        return random.randint(10, 100)

    def ranDefense(self):
        return random.randint(5, 80)

    def ranSpeed(self):
        return random.randint(5, 50)

    def ranAccuracy(self):
        return random.randint(70, 100)

    def ranEvasive(self):
        return random.randint(70, 100)

    def ranLuck(self):
        return random.randint(1, 10)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def is_alive(self):
        return self.hp > 0



def calculate_damage(attacker, defender):
    base_damage = attacker.power
    defense_factor = defender.defense / 100
    mitigated_damage = base_damage * (1 - defense_factor)
    random_factor = random.uniform(0.9, 1.1)
    final_damage = mitigated_damage * random_factor
    critical_chance = attacker.luck / 100
    if random.random() < critical_chance:
        final_damage *= 2
        print("Critical hit!")
    
    return int(final_damage)




# Create player and enemy
player = letter()
enemy = letter()



def game_loop():
    running = True
    userTurn = True

    playX = 520
    enemX = 20

    playY = 500
    enemY = 30

    clock = pygame.time.Clock()
    buttonClicked = ""
    buttonHeld = False

    while running:
        screen.fill(BLACK)



        # Turns determine
        if not userTurn:
            first, second = player, enemy
            if enemy.speed > player.speed:
                first, second = second, first
                
            damage = calculate_damage(first, second)
            second.take_damage(damage)
            print(f"{second.name} attacked for {damage} damage!")
            if second.is_alive():
                damage = calculate_damage(second, first)
                first.take_damage(damage)
                print(f"{first.name} attacked for {damage} damage!")
            userTurn = True
            buttonClicked = ""

        # letter, types, hp display
        for i in range(0, 2):
            ltr = player if i != 0 else enemy
            x = playX if i != 0 else enemX
            y = playY if i != 0 else enemY
            ltr_name = font2.render(f"{ltr.name}", True, WHITE)
            screen.blit(ltr_name, (x, y))
            pygame.draw.rect(screen, GREY, (x + 90, y + 35, 150, sos)) 
            pygame.draw.rect(screen, GREEN, (x + 90, y + 35, 150 * (ltr.hp / ltr.maxHP), sos))
            if ltr.color1:
                pygame.draw.rect(screen, color_mapping(ltr.color1), (x + 90, y + 10, 20, sos * 2)) 
            if ltr.color2:
                pygame.draw.rect(screen, color_mapping(ltr.color2), (x + 120, y + 10, 20, sos * 2)) 


        # button draw and detection
        options = ["Attack", "Color1", "Color2", "Defend"]
        for i, option in enumerate(options):

            button_rect = pygame.Rect( 20 + i * 120, playY + 5, button_width, button_height)
            mouse_pos = pygame.mouse.get_pos()

            if button_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect)
                if pygame.mouse.get_pressed()[0] and buttonHeld == False: 
                    buttonClicked = option
                    buttonHeld = True
                elif not pygame.mouse.get_pressed()[0]:
                    buttonHeld = False
            else:
                pygame.draw.rect(screen, BUTTON_COLOR, button_rect)


            option_text = font.render(option, True, WHITE)
            screen.blit(option_text, (27 + i * 120, playY + 10))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    buttonClicked = "Attack"
                elif event.key == pygame.K_2:
                    buttonClicked = "Color1"
                elif event.key == pygame.K_3:
                    buttonClicked = "Color2"
                elif event.key == pygame.K_4:
                    buttonClicked = "Defend"

                
        if buttonClicked != "":
            userTurn = False

        


        if not player.is_alive():
            game_over_text = font.render("You lost! Game Over!", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2))
            pygame.display.update()
            pygame.time.delay(2000)
            running = False
        elif not enemy.is_alive():
            win_text = font.render("You won! Victory!", True, GREEN)
            screen.blit(win_text, (WIDTH // 2 - 100, HEIGHT // 2))
            pygame.display.update()
            pygame.time.delay(2000)
            running = False

        pygame.display.update()
        clock.tick(30)

    pygame.quit()
    sys.exit()

def color_mapping(color_name):
    color_dict = {
        "red": (255, 0, 0),
        "orange": (255, 165, 0),
        "yellow": (255, 255, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "purple": (128, 0, 128),
        "black": (50, 50, 50),
        "white": (255, 255, 255),
        "grey": (169, 169, 169),
        None: (20, 20, 20), 
    }
    return color_dict.get(color_name, (0, 0, 0))

game_loop()
