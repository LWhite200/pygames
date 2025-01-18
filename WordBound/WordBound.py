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

# Define fonts
font = pygame.font.SysFont('Arial', 24)

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

    def ranName(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=4))

    def ranColor(self):
        colors = ["red", "orange", "yellow", "green", "blue", "purple", "black", "white", "grey", None]
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



# Player and AI characters (Both will inherit from the letter class)
class Player(letter):
    def __init__(self):
        super().__init__()

    def attack(self, enemy):
        damage = self.power - enemy.defense
        if damage < 0:
            damage = 0
        enemy.take_damage(damage)

    def defend(self):
        self.defense += 10  # Increases defense when defending

    def use_color1(self, enemy):
        # For simplicity, using color1 as a healing move
        healing = 20
        self.hp += healing
        if self.hp > 200:
            self.hp = 200

    def use_color2(self, enemy):
        # For simplicity, use color2 as a random effect
        self.speed += 5  # Temporarily increase speed

# Enemy AI (Simple AI behavior)
class Enemy(letter):
    def __init__(self):
        super().__init__()

    def attack(self, player):
        damage = self.power - player.defense
        if damage < 10:
            damage = 10
        player.take_damage(damage)

    def defend(self):
        self.defense += 10

    def use_color1(self, player):
        healing = 20
        self.hp += healing
        if self.hp > 200:
            self.hp = 200

    def use_color2(self, player):
        self.speed += 5

# Create player and enemy
player = Player()
enemy = Enemy()





def game_loop():
    running = True
    userTurn = True

    playX = 20
    enemX = 20

    playY = 20
    enemY = 100

    clock = pygame.time.Clock()

    while running:
        screen.fill(BLACK)


        player_name_text = font.render(f"{player.name}", True, WHITE)
        screen.blit(player_name_text, (playX, playY))
        pygame.draw.rect(screen, GREY, (playX + 70, playY + 25, 50, 10)) 
        pygame.draw.rect(screen, GREEN, (playX + 70, playY + 25, 50 * (player.hp / player.maxHP), 10))
        if player.color1:
            pygame.draw.rect(screen, color_mapping(player.color1), (playX + 70, playY, 20, 20)) 
        if player.color2:
            pygame.draw.rect(screen, color_mapping(player.color2), (playX + 100, playY, 20, 20))  

        enemy_name_text = font.render(f"{enemy.name}", True, WHITE)
        screen.blit(enemy_name_text, (enemX, enemY))
        pygame.draw.rect(screen, GREY, (enemX + 70, enemY + 25, 50, 10))  
        pygame.draw.rect(screen, GREEN, (enemX + 70, enemY + 25, 50 * (enemy.hp / enemy.maxHP), 10)) 
        if enemy.color1:
            pygame.draw.rect(screen, color_mapping(enemy.color1), (enemX + 70, enemY, 20, 20))  
        if enemy.color2:
            pygame.draw.rect(screen, color_mapping(enemy.color2), (enemX + 100, enemY, 20, 20))


        options = ["Attack", "Use Color1", "Use Color2", "Defend"]
        for i, option in enumerate(options):
            option_text = font.render(option, True, WHITE)
            screen.blit(option_text, (WIDTH - 150, 100 + i * 40))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.attack(enemy)
                    userTurn = False
                elif event.key == pygame.K_2:
                    player.use_color1(enemy)
                    userTurn = False
                elif event.key == pygame.K_3:
                    player.use_color2(enemy)
                    userTurn = False
                elif event.key == pygame.K_4:
                    player.defend()
                    userTurn = False


        if enemy.is_alive() and not userTurn:
            enemy.attack(player)
            userTurn = True


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
