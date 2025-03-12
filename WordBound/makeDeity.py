import pygame # type: ignore
import random

# Initialize PyGame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 875
SCREEN_HEIGHT = 650

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Deity Creator")

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Text input class
class TextInput:
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False

    def draw(self, screen):
        color = BLUE if self.active else GRAY
        pygame.draw.rect(screen, color, self.rect, 2)
        text_surface = font.render(self.text if self.text else self.placeholder, True, BLACK)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

# Scrollbar class
class Scrollbar:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, statName):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.statName = statName

        self.height = height

        self.x = x
        self.y = y

        self.maxWidth = width
        self.curWidth = int(self.maxWidth * (self.value - self.min_val) / (self.max_val - self.min_val))


        self.handle_height = 20  # Fixed handle height
        self.handle_rect = pygame.Rect(x, y, width, self.handle_height)
        self.dragging = False

    def draw(self, screen):

        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.maxWidth, self.height))
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.curWidth, self.height))

        stuff = f"{self.value}   {self.statName}" 
        value_text = small_font.render(stuff, True, BLACK)
        screen.blit(value_text, (self.rect.x + self.rect.width + 10, self.rect.y))


    def handle_event(self, event):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]


        if click and self.rect.collidepoint(mouse_x, mouse_y):
            self.dragging = True
        else:
            self.dragging = False
            
        
        if event.type == pygame.MOUSEMOTION and self.dragging:
            value = self.min_val + ((mouse_x - self.x) * (self.max_val - self.min_val)) / self.maxWidth
            value = max(self.min_val, min(value, self.max_val))
            self.curWidth = int(self.maxWidth * (value - self.min_val) / (self.max_val - self.min_val))
            if value % 2 != 0:
                value += 1
            self.value = int(value)
            



class Dropdown:
    def __init__(self, x, y, width, height, options, visible_items=4):
        self.rect = pygame.Rect(x, y, width, height)  # Main dropdown rectangle
        self.options = options  # List of options
        self.selected = options[0]  # Currently selected option
        self.active = False  # Whether the dropdown is active
        self.visible_items = visible_items  # Number of visible items
        self.scroll_offset = 0  # Current scroll position
        self.scrollbar_width = 10  # Width of the scrollbar
        self.scrollbar_rect = pygame.Rect(x + width + 5, y, self.scrollbar_width, height * visible_items)  # Scrollbar rectangle
        self.scrollbar_dragging = False  # Whether the scrollbar is being dragged
        self.item_spacing = 5  # Spacing between dropdown items

    def draw(self, screen):
        # Draw the main dropdown box
        color = BLUE if self.active else GRAY
        pygame.draw.rect(screen, color, self.rect, 2)
        text_surface = small_font.render(self.selected, True, BLACK)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

        if self.active:
            # Draw the dropdown options
            for i in range(self.scroll_offset, min(self.scroll_offset + self.visible_items, len(self.options))):
                # Calculate the position of each option
                y = self.rect.y + self.rect.height + (i - self.scroll_offset) * (self.rect.height + self.item_spacing)
                option_rect = pygame.Rect(self.rect.x, y, self.rect.width, self.rect.height)
                pygame.draw.rect(screen, GRAY, option_rect)  # Draw option background
                pygame.draw.rect(screen, BLACK, option_rect, 1)  # Draw option border
                text_surface = small_font.render(self.options[i], True, BLACK)
                screen.blit(text_surface, (option_rect.x + 10, option_rect.y + 10))  # Draw option text

            # Draw the scrollbar
            pygame.draw.rect(screen, GRAY, self.scrollbar_rect)  # Scrollbar background
            scrollbar_handle_height = self.scrollbar_rect.height * (self.visible_items / len(self.options))
            scrollbar_handle_y = self.scrollbar_rect.y + (self.scroll_offset / len(self.options)) * self.scrollbar_rect.height
            scrollbar_handle_rect = pygame.Rect(self.scrollbar_rect.x, scrollbar_handle_y, self.scrollbar_rect.width, scrollbar_handle_height)
            pygame.draw.rect(screen, BLUE, scrollbar_handle_rect)  # Scrollbar handle

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active  # Toggle dropdown visibility
            elif self.active:
                # Check if an option is clicked
                for i in range(self.scroll_offset, min(self.scroll_offset + self.visible_items, len(self.options))):
                    y = self.rect.y + self.rect.height + (i - self.scroll_offset) * (self.rect.height + self.item_spacing)
                    option_rect = pygame.Rect(self.rect.x, y, self.rect.width, self.rect.height)
                    if option_rect.collidepoint(event.pos):
                        self.selected = self.options[i]  # Update selected option
                        self.active = False  # Close dropdown

                # Check if the scrollbar is clicked
                if self.scrollbar_rect.collidepoint(event.pos):
                    self.scrollbar_dragging = True  # Start dragging the scrollbar

        if event.type == pygame.MOUSEBUTTONUP:
            self.scrollbar_dragging = False  # Stop dragging the scrollbar

        if event.type == pygame.MOUSEMOTION and self.scrollbar_dragging:
            # Update scroll offset based on scrollbar position
            mouse_y = event.pos[1]
            scrollbar_y = mouse_y - self.scrollbar_rect.y
            self.scroll_offset = int((scrollbar_y / self.scrollbar_rect.height) * len(self.options))
            self.scroll_offset = max(0, min(self.scroll_offset, len(self.options) - self.visible_items))


            

# Letter data
LetterData = {
    'A': [25, 'physical', 'curHP', -1, 'opponent', 100],
    'B': [25, 'special', 'curHP', -1, 'opponent', 100],
    'C': [15, 'physical', 'curHP', -1, 'opponent', 100],
    'D': [15, 'special', 'curHP', -1, 'opponent', 100],
    'E': [0, None, 'attack', -1, 'opponent', 100],
    'F': [0, None, 'attack', 1, 'user', 100],
    'G': [0, None, 'protect', 1, 'user', 100],
    'H': [0, None, 'defense', -1, 'opponent', 100],
    'I': [0, None, 'defense', 1, 'user', 100],
    'J': [0, None, 'accuracy', -1, 'opponent', 100],
    'K': [0, None, 'accuracy', 1, 'user', 100],
    'L': [0, None, 'perish', 1, 'all', 100],
    'M': [0, None, 'weather', 1, 'all', 100],
    'N': [0, None, 'trap', 1, 'opponent', 100],
    'O': [0, None, 'multi-attack', 1, 'user', 100],
    'P': [0, None, 'multi-stat', 1, 'user', 100],
    'Q': [0, None, 'multi-attack', -1, 'opponent', 100],
    'R': [0, None, 'multi-stat', -1, 'opponent', 100],
    'S': [10, 'physical', 'Fake-out', -1, 'opponent', 100],
    'T': [0, None, 'burn', 1, 'opponent', 100],
    'U': [0, None, 'shock', 1, 'opponent', 100],
    'V': [0, None, 'freeze', 1, 'opponent', 100],
    'W': [0, None, 'speed', -1, 'opponent', 100],
    'X': [0, None, 'speed', 1, 'user', 100],
}

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
        parts = [part.strip() for part in letter_string.split(",")]
        if len(parts) != 3:
            raise ValueError("Invalid letter string format.")
        char = parts[0]
        battleType = parts[1]
        tier = int(parts[2])
        return cls(char, battleType, tier)

# Deity class
class Deity:
    def __init__(self, name=None):
        self.name = name if name is not None else str(random.randint(0, 101))
        self.maxHP = 250
        self.letters = self.get_random_letters()
        self.attack = random.randint(50, 250)
        self.defense = random.randint(50, 250)
        self.special = random.randint(50, 250)
        self.accuracy = 100
        self.speed = random.randint(50, 250)
        self.comboStamina = 5
        self.battleType, self.battleType2 = self.assign_battle_types()
        self.lets = []
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
        letter_options = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        return [Letter(random.choice(letter_options)) for _ in range(5)]

    def assign_battle_types(self):
        colors = ["red", "blue", "green", "brown", "lime", "yellow", "black", "white", "grey", "cyan", "magenta", "orange", "purple", "maroon"]
        primary = random.choice(colors)
        if random.random() < 1/3:
            secondary = None
        else:
            secondary = random.choice([c for c in colors if c != primary])
        return primary, secondary

    def save_to_file(self):
        with open("deity_list.txt", "a") as file:
            letters_str = ",".join([letter.toString() for letter in self.letters])
            file.write(f"{self.name}|{letters_str}|{self.battleType}|{self.battleType2}|{self.attack}|{self.defense}|{self.special}|{self.accuracy}|{self.speed}\n")

    @classmethod
    def load_from_file(cls, filename):
        deities = []
        with open(filename, "r") as file:
            for line in file:
                parts = line.strip().split("|")
                if len(parts) != 9:
                    continue
                deity = cls(parts[0])
                deity.letters = [Letter.fromString(letter_str) for letter_str in parts[1].split(",")]
                deity.battleType = parts[2]
                deity.battleType2 = parts[3]
                deity.attack = int(parts[4])
                deity.defense = int(parts[5])
                deity.special = int(parts[6])
                deity.accuracy = int(parts[7])
                deity.speed = int(parts[8])
                deities.append(deity)
        return deities

# Main application
# Main application
# Main application
# Main application
# Main application
def main():
    clock = pygame.time.Clock()
    running = True

    # UI elements
    create_button = Button(50, 50, 150, 50, "Create Deity", GRAY)
    view_button = Button(250, 50, 150, 50, "View Deities", GRAY)
    name_input = TextInput(50, 120, 200, 50, "Enter name...")
    output_text = ""

    # Scrollbars for stats
    hp_scrollbar = Scrollbar(50, 200, 200, 20, 50, 250, 150, "HP")
    attack_scrollbar = Scrollbar(50, 250, 200, 20, 50, 250, 150, "Attack")
    special_scrollbar = Scrollbar(50, 300, 200, 20, 50, 250, 150, "Special")
    defense_scrollbar = Scrollbar(50, 350, 200, 20, 50, 250, 150, "Defense")
    speed_scrollbar = Scrollbar(50, 400, 200, 20, 50, 250, 150, "Speed")

    # Dropdowns for types
    type_options = ["red", "blue", "green", "brown", "lime", "yellow", "black", "white", "grey", "cyan", "magenta", "orange", "purple", "maroon"]
    primary_type_dropdown = Dropdown(50, 450, 200, 30, type_options)  # Smaller dropdown
    secondary_type_dropdown = Dropdown(300, 450, 200, 30, type_options + ["None"])  # Smaller dropdown

    # Add 5 TextInputs for letters
    letter_inputs = [TextInput(550, 50 + i * 60, 40, 40, "") for i in range(5)]

    # Add 5 Dropdowns for tiers
    tier_options = ["1", "2", "3", "4", "5"]
    tier_dropdowns = [Dropdown(625, 50 + i * 60, 40, 30, tier_options) for i in range(5)]

    # Add 5 Dropdowns for battle types
    battleType_dropdowns = [Dropdown(700, 50 + i * 60, 85, 30, type_options) for i in range(5)]

    # List to store the selected letters/moves
    selected_letters = []

    # Modify the main loop to handle the new UI elements
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle text input
            name_input.handle_event(event)
            for letter_input in letter_inputs:
                letter_input.handle_event(event)

            # Handle scrollbars
            hp_scrollbar.handle_event(event)
            attack_scrollbar.handle_event(event)
            defense_scrollbar.handle_event(event)
            special_scrollbar.handle_event(event)
            speed_scrollbar.handle_event(event)

            # Handle dropdowns
            primary_type_dropdown.handle_event(event)
            secondary_type_dropdown.handle_event(event)
            for tier_dropdown in tier_dropdowns:
                tier_dropdown.handle_event(event)
            for battleType_dropdown in battleType_dropdowns:
                battleType_dropdown.handle_event(event)

            # Handle button clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if create_button.is_clicked(event.pos):
                    name = name_input.text
                    if name:
                        # Validate and collect the selected letters
                        selected_letters = []
                        for i in range(5):
                            letter = letter_inputs[i].text.upper()
                            tier = tier_dropdowns[i].selected
                            battleType = battleType_dropdowns[i].selected

                            # Validate the letter
                            if len(letter) == 1 and (letter.isalpha() or letter.isdigit()):
                                # Validate the tier
                                if tier in tier_options:
                                    # Format the letter string correctly
                                    selected_letters.append(f"{letter},{battleType},{tier}")
                                else:
                                    output_text = f"Please select a tier between 1 and 5."
                                    break
                            else:
                                output_text = f"Please enter a single capital letter or number."
                                break
                        else:
                            # If all letters are valid, create the deity
                            try:
                                print("Selected Letters:", selected_letters)  # Debugging
                                deity = Deity(name)
                                deity.maxHP = hp_scrollbar.value
                                deity.attack = attack_scrollbar.value
                                deity.defense = defense_scrollbar.value
                                deity.special = special_scrollbar.value
                                deity.speed = speed_scrollbar.value
                                deity.battleType = primary_type_dropdown.selected
                                deity.battleType2 = secondary_type_dropdown.selected if secondary_type_dropdown.selected != "None" else None
                                deity.letters = [Letter.fromString(letter) for letter in selected_letters]
                                deity.save_to_file()
                                output_text = f"Created deity: {deity.name}"
                            except ValueError as e:
                                output_text = f"Error creating deity: {e}"
                    else:
                        output_text = "Please enter a name for the deity."
                elif view_button.is_clicked(event.pos):
                    try:
                        deities = Deity.load_from_file("deity_list.txt")
                        output_text = "\n".join([f"Deity: {deity.name}, Letters: {[letter.toString() for letter in deity.letters]}" for deity in deities])
                    except Exception as e:
                        output_text = f"Error loading deities: {e}"

        # Draw UI elements
        create_button.draw(screen)
        view_button.draw(screen)
        name_input.draw(screen)
        hp_scrollbar.draw(screen)
        attack_scrollbar.draw(screen)
        special_scrollbar.draw(screen)
        defense_scrollbar.draw(screen)
        speed_scrollbar.draw(screen)
        primary_type_dropdown.draw(screen)
        secondary_type_dropdown.draw(screen)

        # Draw letter inputs, tier dropdowns, and battle type dropdowns
        for i in range(5):
            letter_inputs[i].draw(screen)
            tier_dropdowns[i].draw(screen)
            battleType_dropdowns[i].draw(screen)

        # Draw selected letters
        y_offset = 590
        for letter in selected_letters:
            text_surface = small_font.render(letter, True, BLACK)
            screen.blit(text_surface, (50, y_offset))
            y_offset += 30

        # Draw output text
        text_surface = font.render(output_text, True, BLACK)
        screen.blit(text_surface, (50, 500))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()