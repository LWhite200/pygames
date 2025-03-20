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




# RadioButton class for letters A-Z
# RadioButton class for letters A-Z
class RadioButton:
    def __init__(self, x, y, size, letter):
        self.rect = pygame.Rect(x, y, size, size)
        self.letter = letter
        self.selected = False

    def draw(self, screen):
        # Draw the outline (grey by default)
        # pygame.draw.rect(screen, BLUE, self.rect)

        # If selected, fill the rectangle with blue
        if self.selected:
            pygame.draw.rect(screen, BLUE, self.rect, 2)
        else:
            pygame.draw.rect(screen, GRAY, self.rect, 2)


        # Draw the letter text
        text_surface = small_font.render(self.letter, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

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
    primary_type_dropdown =   Dropdown(50, 450, 150, 30, type_options)  # Smaller dropdown
    secondary_type_dropdown = Dropdown(250, 450, 150, 30, type_options) 
    third_type_dropdown =     Dropdown(450, 450, 150, 30, type_options)
    four_type_dropdown =      Dropdown(650, 450, 150, 30, type_options)

    # Radio buttons for letters A-Z
    radio_buttons = []
    start_x = 600
    start_y = 50
    button_size = 30
    spacing = 10
    letters = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    for i, letter in enumerate(letters):
        x = start_x + (i % 5) * (button_size + spacing)
        y = start_y + (i // 5) * (button_size + spacing)
        radio_buttons.append(RadioButton(x, y, button_size, letter))

    # Modify the main loop to handle the new UI elements
    while running:
        screen.fill((0,0,155))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle text input
            name_input.handle_event(event)

            # Handle scrollbars
            hp_scrollbar.handle_event(event)
            attack_scrollbar.handle_event(event)
            defense_scrollbar.handle_event(event)
            special_scrollbar.handle_event(event)
            speed_scrollbar.handle_event(event)

            # Handle dropdowns
            primary_type_dropdown.handle_event(event)
            secondary_type_dropdown.handle_event(event)
            third_type_dropdown.handle_event(event)
            four_type_dropdown.handle_event(event)

            # Handle radio buttons
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rb in radio_buttons:
                    if rb.is_clicked(event.pos):
                        rb.selected = not rb.selected

            # Handle button clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if create_button.is_clicked(event.pos):
                    name = name_input.text
                    if name:
                        # Collect the selected letters
                        selected_letters = [rb.letter for rb in radio_buttons if rb.selected]
                        if selected_letters:
                            # Format the deity data
                            deity_data = (
                                f"{name}|{selected_letters}|{primary_type_dropdown.selected}|"
                                f"{secondary_type_dropdown.selected}|{third_type_dropdown.selected}|"
                                f"{four_type_dropdown.selected}|{attack_scrollbar.value}|"
                                f"{defense_scrollbar.value}|{special_scrollbar.value}|"
                                f"{speed_scrollbar.value}\n"
                            )

                            # Save the deity data to the file
                            with open("DeityList.txt", "a") as file:
                                file.write(deity_data)

                            output_text = "Deity saved successfully!"
                        else:
                            output_text = "Please select at least one letter."
                    else:
                        output_text = "Please enter a name for the deity."

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
        third_type_dropdown.draw(screen)
        four_type_dropdown.draw(screen)

        # Draw radio buttons
        for rb in radio_buttons:
            rb.draw(screen)

        # Draw output text
        text_surface = font.render(output_text, True, BLACK)
        screen.blit(text_surface, (50, 500))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()