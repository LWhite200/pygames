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
        "black":  (25, 25, 25), 
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
        self.tier = random.randint(1, 3)

        self.power = 50 if self.char in ["A", "B"] else 0
        self.statChange = "" if self.char in ["A", "B"] else self.getStatChange(self.char)

        self.Accuracy = 100

    def getStatChange(self, letter):
        
        # letters not present: A, B, C, D

        # status 
        if letter == "E":
            return "Accuracy,increase,user"

        # Heal
        elif letter == "F":
            return "Accuracy,decrease,opp"
        
        # Protect, must be alone for full protect, else it is 'wide guard' with slight defense boost
        elif letter == "G":
            return "Defense,increase,user"

        # Current Move Accuracy increase, no miss?
        elif letter == "H":
            return "Defense,Increase,user"

        # Changes weather if out front, else temporary current turn weather change
        elif letter == "I":
            return "Accuracy,decrease,opp"

        # User cannot switch out [j, idk abouit k and L]
        else:
            return ""

    def getRandomStat(self, isStatus):
        if not isStatus:
            return random.choice(["speed", "physical", "special", "Accuracy"])

    def ranColor(self):
        colors = ["red", "blue", "green", "brown", "lime", "yellow", "black", "white", "grey", "cyan", "magenta", "orange", "purple", "maroon"]
        ccc = random.choice(colors)
        return ccc

    

class Deity:
    def __init__(self, name, letters):
        self.name = name
        self.maxHP = 250
        self.curHP = self.maxHP
        self.speed = random.randint(50, 101)

        self.letters = letters # What the deity can use
        self.lets = []         # current move the player is choosing to do

        self.physical = 100
        self.defense = 100
        self.special = 100
        self.Accuracy = 100

        # -- stats below are stages, out of 6. 1/4 for all stat increase so maximum of *2.5

        self.protect = 0 # 0 = not, 1 = not first, 2 = 2/3, 3 = total protect

        # may remain entire game
        self.statPhysical = 0
        self.statDefense = 0
        self.statSpecial = 0
        self.statAccuracy = 0

        # for the specific turn
        self.tempPhysical = 0
        self.tempDefense = 0
        self.tempSpecial = 0
        self.tempAccuracy = 0
        
        self.comboStamina = 5
        self.battleType = self.randType()
        self.battleColor = color_mapping(self.battleType)

    def removeTemporary(self):
        self.tempPhysical = 0
        self.tempDefense = 0
        self.tempSpecial = 0
        self.tempAccuracy = 0

    def take_damage(self, damage):
        self.curHP -= damage
        if self.curHP < 0:
            self.curHP = 0

    def calculate_combo_stamina_cost(self):
        if len(self.lets) > 1:
            return sum(letter.tier for letter in self.lets[1:])  
        return 0  # No cost for a single letter

    def update_stamina(self, cost):
        self.comboStamina -= cost
        if self.comboStamina < 0:
            self.comboStamina = 0

    def randType(self):
        colors = ["red", "blue", "green", "brown", "lime", "yellow", "black", "white", "grey", "cyan", "magenta", "orange", "purple", "maroon"]
        return random.choice(colors)