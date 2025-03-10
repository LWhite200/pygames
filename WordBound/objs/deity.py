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

        self.power = 50 if self.char in ["A", "B"] else 25 if self.char in ["C", "D"] else 0
        self.statChange = self.getStatChange(self.char)

        self.Accuracy = 100

    def getStatChange(self, letter):
        
        # notNeedAim --- ('C', 'D', 'G', 'H', 'F', 'I', 'K')

        # multi hit ---- ('C', 'D') or contains 'M'

        # ---- Must Be Alone ---- ("G", U, V, J)

        # must be paired with attacking (M, I, S)

        # ("C", "D", "F", "G", "I", "K")

        if letter == "A":
            return "curHP,decrease,opp"
        
        elif letter == "B":
            return "curHP,decrease,opp"
        
        elif letter == "C":
            return "curHP,decrease,opp"
        
        elif letter == "D":
            return "curHP,decrease,opp"
        
        elif letter == "E":
            return "attack,decrease,opp"

        elif letter == "F":
            return "attack,increase,user"

        elif letter == "G":
            return "PROTECT,increase,user"
        
        elif letter == "H":
            return "defense,decrease,opp"

        elif letter == "I":
            return "defense,increase,user"
        
        elif letter == "J":
            return "accuracy,decrease,opp"

        elif letter == "K":
            return "accuracy,increase,user"
        

        




        
        elif letter == "L":
            return "Perish Song"
        
        elif letter == "M":
            return "weather"
        
        elif letter == "N":
            return "MEAN LOOK"
        
        # ---- Must be paired with attacking ----
        elif letter == "O":
            return "MULTI-ATTACK"
        
        elif letter == "P":
            return "Multi-stat"
        
        elif letter == "Q":
            return "FakeOut"
        






        elif letter == "R":
            return "BURN"
        
        elif letter == "S":
            return "SHOCK"
        
        elif letter == "T":
            return "FREEZE"

        # -- Stat changing below ---

        # ---- ATTACK CHANGE ----
        
        
        # ---- DEFENSE CHANGE ----
       

        else:
            return ""

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

        self.baseAttack = 100
        self.baseDefense = 100
        self.baseSpecial = 100
        self.baseAccuracy = 100

        # -- stats below are stages, out of 6. 1/4 for all stat increase so maximum of *2.5

        self.protect = 0 # 0 = not, 1 = not first, 2 = 2/3, 3 = total protect

        # may remain entire game
        self.attack = 0
        self.defense = 0
        self.special = 0
        self.accuracy = 0

        # for the specific turn
        self.tempattack = 0
        self.tempdefense = 0
        self.tempspecial = 0
        self.tempaccuracy = 0
        
        self.comboStamina = 5
        self.battleType = self.randType()
        self.battleColor = color_mapping(self.battleType)

    def removeTemporary(self):
        self.tempattack = 0
        self.tempdefense = 0
        self.tempspecial = 0
        self.tempaccuracy = 0

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