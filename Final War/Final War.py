import pygame # type: ignore
import math

pygame.init()

width, height = 1000, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Circle Game")

ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
SHADOW_COLOR = (50, 50, 50, 100)
SWORD_COLOR = (192, 192, 192)

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

    def update(self, keys):
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
            length = math.sqrt(move_x**2 + move_y**2)
            move_x /= length
            move_y /= length

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

    def draw(self, screen):
        shadow_surface = pygame.Surface((self.inRadius * 2, self.inRadius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, SHADOW_COLOR, (self.inRadius, self.inRadius), self.inRadius)
        screen.blit(shadow_surface, (self.x + 5 - self.inRadius, self.inY + 5 - self.inRadius))
        pygame.draw.circle(screen, ORANGE, (self.x, self.y), self.radius)

class Sword:
    def __init__(self, max_distance):
        self.length = 50  
        self.width = 10  
        self.sword_surface = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
        self.sword_surface.fill(SWORD_COLOR)
        self.max_distance = max_distance 

    def update(self, player_x, player_y, mouse_x, mouse_y):
        dx = mouse_x - player_x
        dy = mouse_y - player_y
        angle = math.atan2(dy, dx)

        distance = math.sqrt(dx**2 + dy**2)

        if distance > self.max_distance:
            dx = dx / distance * self.max_distance
            dy = dy / distance * self.max_distance

        sword_x = player_x + dx
        sword_y = player_y + dy
        self.sword_x = sword_x
        self.sword_y = sword_y
        self.angle = angle

        return self.sword_x, self.sword_y, self.angle

    def draw(self, screen):
        rotated_sword = pygame.transform.rotate(self.sword_surface, -math.degrees(self.angle))
        sword_rect = rotated_sword.get_rect(center=(self.sword_x, self.sword_y))

        screen.blit(rotated_sword, sword_rect.topleft)

player = PlayObj(width // 2, height // 2)
sword = Sword(max_distance=100)

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    player.update(keys)
    
    mouse_x, mouse_y = pygame.mouse.get_pos()

    sword_x, sword_y, sword_angle = sword.update(player.x, player.y, mouse_x, mouse_y)

    screen.fill((0, 0, 0))

    player.draw(screen)
    sword.draw(screen)
    
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
