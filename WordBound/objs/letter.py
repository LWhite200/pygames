# letter.py

import random
import pygame # type: ignore

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

# Letter class
class Letter:
    def __init__(self, char):
        self.char = char.upper()
        self.battleType = self.ranColor()
        self.color1 = color_mapping(self.battleType)
        self.tier = random.randint(0, 2)

        self.power = 50 if self.char in ["A", "B"] else 5
        self.statChange = "" if self.char in ["A", "B"] else self.getStatChange(self.char)

        self.accuracy = 100

    def getStatChange(self, letter):
        
        #stat change
        if letter == "C":
            return "accuracy, increase, user"

        elif letter == "D":
            return "accuracy, decrease, opp"

        # status 
        elif letter == "E":
            return "accuracy, increase, user"

        # Heal
        elif letter == "F":
            return "accuracy, decrease, opp"

        # Protect if first, else defense buff current turn
        elif letter == "G":
            return "accuracy, decrease, opp"

        # Current Move Accuracy increase, no miss?
        elif letter == "H":
            return "accuracy, decrease, opp"

        # Changes weather if out front, else temporary current turn weather change
        elif letter == "I":
            return "accuracy, decrease, opp"

        # User cannot switch out [j, idk abouit k and L]
        else:
            return "accuracy, decrease, opp"

    def getRandomStat(self, isStatus):
        if not isStatus:
            return random.choice(["speed", "physical", "special", "accuracy"])

    def ranColor(self):
        colors = ["red", "blue", "green", "brown", "lime", "yellow", "black", "white", "grey", "cyan", "magenta", "orange", "purple", "maroon"]
        ccc = random.choice(colors)
        return ccc

    def draw(self, x, y, selected=False, hovered=False, isPlayer1=True, playerChoose=True):
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