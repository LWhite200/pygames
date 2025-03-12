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

# hashmap of the letter/moves
# char --- base power, physical/special, what does, increase/decrease, whom
LetterData = {
    'A': [25, 'physical', 'curHP', -1, 'opponent',100],
    'B': [25, 'special', 'curHP', -1, 'opponent',100],
    'C': [15, 'physical', 'curHP', -1, 'opponent',100],
    'D': [15, 'special', 'curHP', -1, 'opponent',100],

    'E': [0, None, 'attack', -1, 'opponent',100],
    'F': [0, None, 'attack', 1, 'user',100],
    'G': [0, None, 'protect', 1, 'user',100],
    'H': [0, None, 'defense', -1, 'opponent',100],
    'I': [0, None, 'defense', 1, 'user',100],

    'J': [0, None, 'accuracy', -1, 'opponent',100],
    'K': [0, None, 'accuracy', 1, 'user',100],

    # not set up yet
    'L': [0, None, 'perish', 1, 'all',100],
    'M': [0, None, 'weather', 1, 'all',100],
    'N': [0, None, 'trap', 1, 'opponent',100],

    'O': [0, None, 'multi-attack', 1, 'user',100],
    'P': [0, None, 'multi-stat', 1, 'user',100],
    'Q': [0, None, 'multi-attack', -1, 'opponent',100],
    'R': [0, None, 'multi-stat', -1, 'opponent',100],

    'S': [10, 'physical', 'Fake-out', -1, 'opponent',100],
    'T': [0, None, 'burn', 1, 'opponent',100],
    'U': [0, None, 'shock', 1, 'opponent',100],
    'V': [0, None, 'freeze', 1, 'opponent',100],

    'W': [0, None, 'speed', -1, 'opponent',100],
    'X': [0, None, 'speed', 1, 'user',100],

    'Y': [0, None, 'counter'],
    'Z': [0, None, 'mirror']
}
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------



# Letter class
class Letter:
    def __init__(self, char, battleType=None, tier=None):
        self.char = char.upper()
        self.battleType = battleType if battleType is not None else self.ranColor()
        self.tier = tier if tier is not None else random.randint(1, 3)

    def ranColor(self):
        colors = ["red", "blue", "green", "brown", "lime", "yellow", "black", "white", "grey", "cyan", "magenta", "orange", "purple", "maroon"]
        return random.choice(colors)

    def toString(self):
        return f"[{self.char},{self.battleType},{self.tier}]"

    @classmethod
    def fromString(cls, letter_string):
        parts = [part.strip() for part in letter_string.split(",")]  # Strip any extra spaces
        if len(parts) != 3:
            raise ValueError("Invalid letter string format.")
        
        char = parts[0]
        battleType = parts[1]
        tier = int(parts[2])

        return cls(char, battleType, tier)



    


class Deity:
    def __init__(self):

        self.name = str(random.randint(0, 101))
        self.maxHP = 250
        
        self.letters = self.get_random_letters() # What the deity can use

        self.attack = random.randint(25, 250)
        self.defense = random.randint(25, 250)
        self.special = random.randint(25, 250)
        self.accuracy = random.randint(25, 250)
        self.speed = random.randint(25, 250)

        self.comboStamina = 5
        self.battleType, self.battleType2 = self.assign_battle_types()
        

        # -- below are things that change mid-game
        self.lets = []         # current move the player is choosing to do
        self.protect = 0 
        self.turnStart = 0
        self.curHP = self.maxHP

        self.curattack = self.attack
        self.curdefense = self.defense
        self.curspecial = self.special
        self.curaccuracy = self.accuracy
        self.curspeed = self.speed

        self.tempattack = 0
        self.tempdefense = 0
        self.tempspecial = 0
        self.tempaccuracy = 0

        

    def get_random_letters(self):
        letter_options = ['A', 'B', 'C', 'D', 'E' , 'F', 'G', 'H', 'I']
        # letter_options = ['A', 'A', 'B', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        return [Letter(random.choice(letter_options)) for _ in range(5)]

    def assign_battle_types(self):
        colors = ["red", "blue", "green", "brown", "lime", "yellow", "black", "white", "grey", "cyan", "magenta", "orange", "purple", "maroon"]
        primary = random.choice(colors)  
        if random.random() < 1/3:  
            secondary = None
        else:
            secondary = random.choice([c for c in colors if c != primary])  # Ensure secondary is different
        return primary, secondary
    

    def save_to_file(self):
        with open("deity_list.txt", "a") as file:
            letters_str = ",".join([letter.toString() for letter in self.letters])  # Save only letter characters
            file.write(f"{self.name}|{letters_str}|{self.battleType}|{self.battleType2}|{self.attack}|{self.defense}|{self.special}|{self.accuracy}|{self.speed}\n")
        
        

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
    
    def randType2(self):
        colors = [None, "red", "blue", "green", "brown", "lime", "yellow", "black", "white", "grey", "cyan", "magenta", "orange", "purple", "maroon"]
        return random.choice(colors)
    