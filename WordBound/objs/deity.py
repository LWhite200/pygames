import pygame # type: ignore
import random

# Initialize PyGame
pygame.init()

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

    



class Deity:
    def __init__(self, name, letters, startMultipleDebug):
        self.name = name
        self.maxHP = 250
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
        self.accuracy = 100
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

    



    def calculate_combo_stamina_cost(self):
        # Only calculate stamina cost if more than one letter is selected (from both lets and lets2)
        if len(self.lets) + len(self.lets2) > 1:
            # Combine both lets and lets2, and calculate the sum of tiers, skipping the first letter
            combined_letters = self.lets[1:] + self.lets2[1:]
            return sum(letter.tier for letter in combined_letters)  # Skip the first letter
        return 0  # No cost for a single letter


    
    def update_stamina(self, cost):
        self.comboStamina -= cost
        if self.comboStamina < 0:
            self.comboStamina = 0

    def randType(self):
        colors = ["red", "blue", "green", "brown", "lime", "yellow", "black", "white", "grey", "cyan", "magenta", "orange", "purple", "maroon"]
        return random.choice(colors)