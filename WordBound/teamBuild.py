import pygame  # type: ignore
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
SELECTED_COLOR = (100, 200, 100)  # Color for the selected button

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
        self.selected = False  # Track if the button is selected
        self.char = ""  # Additional attribute for char
        self.type = ""  # Additional attribute for type
        self.stamina = ""  # Additional attribute for stamina

    def draw(self, screen):
        # Change color if selected
        button_color = SELECTED_COLOR if self.selected else self.color
        pygame.draw.rect(screen, button_color, self.rect)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Dropdown:
    def __init__(self, x, y, width, height, options, visible_items=4):
        self.rect = pygame.Rect(x, y, width, height)  # Main dropdown rectangle
        self.options = options  # List of options
        self.selected = options[0] if options else ""  # Currently selected option
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

# Read deity data from file
def read_deity_data(filename):
    deities = []
    with open(filename, "r") as file:
        for line in file:
            data = line.strip().split("|")
            name = data[0]
            letters = data[1].split(",")
            types = data[2:6]  # Types are at indices 2, 3, 4, 5
            deities.append({"name": name, "letters": letters, "types": types})
    return deities

def main():
    clock = pygame.time.Clock()
    running = True

    # Read deity data
    deities = read_deity_data("deity_db.txt")

    # Deity buttons
    deity_buttons = [
        Button(50, 50, 125, 50, deities[0]["name"], GRAY),  # Default to first deity name
        Button(200, 50, 125, 50, deities[0]["name"], GRAY),
        Button(350, 50, 125, 50, deities[0]["name"], GRAY),
        Button(500, 50, 125, 50, deities[0]["name"], GRAY),
        Button(650, 50, 125, 50, deities[0]["name"], GRAY)
    ]

    # Save Team and Randomize buttons
    save_team_button = Button(475, 120, 150, 50, "Save Team", GRAY)
    randomize_button = Button(650, 120, 150, 50, "Randomize", GRAY)

    # Current Deity dropdown
    deity_options = [deity["name"] for deity in deities]
    current_deity_dropdown = Dropdown(50, 120, 200, 40, deity_options)

    # Letter buttons
    letter_buttons = [
        Button(50, 380, 50, 50, "_", GRAY),
        Button(110, 380, 50, 50, "_", GRAY),
        Button(170, 380, 50, 50, "_", GRAY),
        Button(230, 380, 50, 50, "_", GRAY),
        Button(290, 380, 50, 50, "_", GRAY)
    ]

    # Dropdowns for the currently selected letter button
    letter_dropdown = Dropdown(50, 440, 100, 40, [])  # Empty initially, populated when a deity is selected
    type_dropdown = Dropdown(160, 440, 100, 40, [])  # Empty initially, populated when a deity is selected
    stamina_dropdown = Dropdown(270, 440, 100, 40, ["1", "2", "3", "4"])

    # Track the currently selected deity button
    selected_deity_button = deity_buttons[0]  # Default to the first button
    selected_deity_button.selected = True  # Mark it as selected
    current_deity_dropdown.selected = selected_deity_button.text  # Default dropdown to selected button's name

    # Track the currently selected letter button
    selected_letter_button = letter_buttons[0]  # Default to the first letter button
    selected_letter_button.selected = True  # Mark it as selected

    # Function to reset all letter buttons to default values
    def reset_letter_buttons(deity):
        for i, button in enumerate(letter_buttons):
            if i < len(deity["letters"]):
                button.char = deity["letters"][i]  # First character
                button.type = deity["types"][0]  # First type
                button.stamina = "1"  # Default stamina
                button.text = button.char  # Update button text
            else:
                button.char = "_"
                button.type = ""
                button.stamina = ""
                button.text = "_"

    # Initialize letter buttons with default values for the first deity
    selected_deity = next(deity for deity in deities if deity["name"] == selected_deity_button.text)
    reset_letter_buttons(selected_deity)

    # Populate dropdowns with the letters and types of the first deity
    letter_dropdown.options = selected_deity["letters"]
    letter_dropdown.selected = selected_deity["letters"][0] if selected_deity["letters"] else ""
    type_dropdown.options = selected_deity["types"]
    type_dropdown.selected = selected_deity["types"][0] if selected_deity["types"] else ""

    while running:
        screen.fill((50, 175, 80))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            for button in deity_buttons:
                if event.type == pygame.MOUSEBUTTONDOWN and button.is_clicked(event.pos):
                    # Deselect all other buttons
                    for b in deity_buttons:
                        b.selected = False
                    button.selected = True
                    selected_deity_button = button
                    current_deity_dropdown.selected = button.text

                    # Find the deity data corresponding to the selected button
                    selected_deity = next((deity for deity in deities if deity["name"] == selected_deity_button.text), None)
                    
                    if selected_deity:
                        # Reset all letter buttons to default values for the new deity
                        reset_letter_buttons(selected_deity)

                        # Update dropdown options
                        letter_dropdown.options = selected_deity["letters"]
                        letter_dropdown.selected = selected_deity["letters"][0] if selected_deity["letters"] else ""

                        type_dropdown.options = selected_deity["types"]
                        type_dropdown.selected = selected_deity["types"][0] if selected_deity["types"] else ""

                    # Ensure selected letter button updates its text
                    selected_letter_button.text = letter_dropdown.selected

            # Handle save team and randomize buttons
            if event.type == pygame.MOUSEBUTTONDOWN and save_team_button.is_clicked(event.pos):
                print("Save Team clicked")
            if event.type == pygame.MOUSEBUTTONDOWN and randomize_button.is_clicked(event.pos):
                print("Randomize clicked")

            # Handle current deity dropdown
            current_deity_dropdown.handle_event(event)

            # Update the selected deity button's text when a deity is selected from the dropdown
            if selected_deity_button and current_deity_dropdown.selected:
                selected_deity_button.text = current_deity_dropdown.selected

                # Find the deity data corresponding to the selected deity
                selected_deity = next((deity for deity in deities if deity["name"] == selected_deity_button.text), None)
                if selected_deity:
                    # Reset all letter buttons to default values for the new deity
                    reset_letter_buttons(selected_deity)

                    # Update dropdown options
                    letter_dropdown.options = selected_deity["letters"]
                    letter_dropdown.selected = selected_deity["letters"][0] if selected_deity["letters"] else ""

                    type_dropdown.options = selected_deity["types"]
                    type_dropdown.selected = selected_deity["types"][0] if selected_deity["types"] else ""

            # Handle letter buttons
            for button in letter_buttons:
                if event.type == pygame.MOUSEBUTTONDOWN and button.is_clicked(event.pos):
                    # Deselect all other letter buttons
                    for b in letter_buttons:
                        b.selected = False
                    # Select the clicked letter button
                    button.selected = True
                    selected_letter_button = button

                    # Update dropdowns to reflect the selected letter button's attributes
                    letter_dropdown.selected = button.char
                    type_dropdown.selected = button.type
                    stamina_dropdown.selected = button.stamina

            # Handle dropdowns for the selected letter button
            letter_dropdown.handle_event(event)
            type_dropdown.handle_event(event)
            stamina_dropdown.handle_event(event)

            # Update the selected letter button's attributes based on dropdown selections
            selected_letter_button.char = letter_dropdown.selected
            selected_letter_button.type = type_dropdown.selected
            selected_letter_button.stamina = stamina_dropdown.selected
            selected_letter_button.text = selected_letter_button.char  # Update button text to show the selected char

        # Draw deity buttons
        for button in deity_buttons:
            button.draw(screen)

        # Draw save team and randomize buttons
        save_team_button.draw(screen)
        randomize_button.draw(screen)

        # Draw current deity dropdown
        current_deity_dropdown.draw(screen)

        # Draw letter buttons
        for button in letter_buttons:
            button.draw(screen)

        # Draw dropdowns for the selected letter button
        if selected_letter_button:
            letter_dropdown.draw(screen)
            type_dropdown.draw(screen)
            stamina_dropdown.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()