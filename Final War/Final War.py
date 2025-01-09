import pygame  # type: ignore
import math

pygame.init()

width, height = 1000, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Circle Game")

ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
SHADOW_COLOR = (50, 50, 50, 100)

class EnemObj:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 30

    def draw(self, screen):
        shadow_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, SHADOW_COLOR, (self.radius, self.radius), self.radius)
        screen.blit(shadow_surface, (self.x + 5 - self.radius, self.y + 5 - self.radius))
        pygame.draw.circle(screen, PURPLE, (self.x, self.y), self.radius)

class PlayObj:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.inY = y
        self.speed = 5
        self.inRadius = 30
        self.radius = 30
        self.velocity_y = 0  
        self.is_jumping = False  
        self.gravity = 0.7  
        self.jump_strength = -8 
        self.max_jump_height = 10
        self.rot = 0

        self.sword_rot = 90
        self.swinging = False 
        self.swing_speed = 5 
        self.swing_cooldown = False
        self.swordSize = 80
        self.jab= False

    def update(self, keys, enemy, right_click, left_click):
        move_x, move_y = 0, 0
        if not self.is_jumping and not keys[pygame.K_SPACE]:
            if keys[pygame.K_w]:
                move_y -= 1
            if keys[pygame.K_s]:
                move_y += 1
            if keys[pygame.K_a]:
                move_x -= 1
            if keys[pygame.K_d]:
                move_x += 1


        if move_x != 0 and move_y != 0:
            magnitude = math.sqrt(move_x ** 2 + move_y ** 2)
            move_x /= magnitude
            move_y /= magnitude

        if enemy:
            angle_to_enemy = math.atan2(enemy.y - self.y, enemy.x - self.x)
            self.rot = math.degrees(angle_to_enemy)
        else:
            if move_x != 0 or move_y != 0:
                self.rot = math.degrees(math.atan2(move_y, move_x))

        self.x += move_x * self.speed
        self.y += move_y * self.speed

        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.inY = self.y
            self.is_jumping = True
            self.velocity_y = self.jump_strength

        if not self.is_jumping:
            self.inY = self.y
        elif self.is_jumping:
            self.y += self.velocity_y
            self.velocity_y += self.gravity

            if self.y >= self.inY:
                self.y = self.inY 
                self.is_jumping = False
                self.velocity_y = 0 

            if self.is_jumping:
                self.radius = self.inRadius + abs(self.y - self.inY) // 3
            else:
                self.radius = 30

        self.x = max(self.radius, min(self.x, width - self.radius))
        self.y = max(self.radius, min(self.y, height - self.radius))

        " self.sword_rot = 90 "

        endRot = -120
        startRot = 90

        # Handle sword swinging
        if left_click and not right_click and not self.swinging and not self.swing_cooldown and not self.jab:
            self.swinging = True
            self.sword_rot = startRot  # Start swing from right to left (90 degrees left)
            self.swordSize = 80
        elif right_click and not self.swinging and not self.swing_cooldown and not self.jab:
            self.sword_rot = 0
            self.swordSize = 60
            if left_click and not self.jab:
                self.jab = True
        elif not self.swinging and not self.jab:
            self.sword_rot = startRot
            self.swordSize = 80


        
        if self.jab:
            self.sword_rot = 0
            if not self.swing_cooldown:
                self.swordSize += self.swing_speed * 3 
                if self.swordSize >= 160:
                    self.swing_cooldown = True 
            else:
                self.swordSize -= self.swing_speed * 2
                if self.swordSize <= 80:
                    self.swing_cooldown = False 
                    self.swordSize = 80
                    self.jab = False
                
        elif self.swinging:
            if not self.swing_cooldown:
                self.sword_rot -= self.swing_speed * 3
                if self.sword_rot <= endRot:
                    self.sword_rot = self.sword_rot
                    self.swing_cooldown = True
            elif self.swing_cooldown:
                self.sword_rot += self.swing_speed * 1.5
                self.swordSize = 60
                if self.sword_rot >= startRot:
                    self.sword_rot = startRot
                    self.swing_cooldown = False
                    self.swinging = False
                    self.swordSize = 80

    def draw(self, screen):

        # sword
        sword_length = self.swordSize
        sword_x = self.x + sword_length * math.cos(math.radians(self.sword_rot + self.rot))
        sword_y = self.y + sword_length * math.sin(math.radians(self.sword_rot + self.rot))  
        pygame.draw.line(screen, "Black", (self.x, self.y), (sword_x, sword_y), 5)

        # body
        shadow_surface = pygame.Surface((self.inRadius * 2, self.inRadius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, SHADOW_COLOR, (self.inRadius, self.inRadius), self.inRadius)
        screen.blit(shadow_surface, (self.x + 5 - self.inRadius, self.inY + 5 - self.inRadius))
        pygame.draw.circle(screen, ORANGE, (self.x, self.y), self.radius)

        

        # Draw eyes
        oS = self.radius // 2  # Eye offset distance from center (can be adjusted)
        eye_x = self.x + oS * math.cos(math.radians(self.rot))
        eye_y = self.y + oS * math.sin(math.radians(self.rot))
        pygame.draw.circle(screen, "White", (int(eye_x), int(eye_y)), self.radius // 3)

        # right
        eye_offset = self.radius
        adjusted_rot = self.rot + 80
        eye_x = self.x + eye_offset * math.cos(math.radians(adjusted_rot))
        eye_y = self.y + eye_offset * math.sin(math.radians(adjusted_rot))
        pygame.draw.circle(screen, "Orange", (int(eye_x), int(eye_y)), self.radius // 3)

        

        # left 
        eye_offset = self.radius
        adjusted_rot = self.rot - 80
        eye_x = self.x + eye_offset * math.cos(math.radians(adjusted_rot))
        eye_y = self.y + eye_offset * math.sin(math.radians(adjusted_rot))
        pygame.draw.circle(screen, "Orange", (int(eye_x), int(eye_y)), self.radius // 3)


# Initialize player and enemy
player = PlayObj(width // 2, height // 2)
enemy = EnemObj(width - 100, height // 2)  # Place enemy on the right side

running = True
clock = pygame.time.Clock()

left_click = False  # Variable to track if left-click is held down
right_click = False  # Variable to track if right-click is held down

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button (button 1)
                left_click = True
            elif event.button == 3:  # Right mouse button (button 3)
                right_click = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button (button 1)
                left_click = False
            elif event.button == 3:  # Right mouse button (button 3)
                right_click = False

    keys = pygame.key.get_pressed()

    player.update(keys, enemy, right_click, left_click)

    screen.fill((200, 200, 200))

    player.draw(screen)
    enemy.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
