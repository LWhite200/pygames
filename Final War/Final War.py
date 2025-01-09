import pygame  # type: ignore
import math
import random

pygame.init()

width, height = 1000, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Circle Game")

ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
SHADOW_COLOR = (50, 50, 50, 100)

class PlayObj:
    def __init__(self, x, y, isPlay):
        self.x = x
        self.y = y
        self.isPlay = isPlay
        self.inY = y
        self.speed = 5 if self.isPlay else 3
        self.inRadius = 30
        self.radius = 30
        self.velocity_y = 0  
        self.is_jumping = False  
        self.gravity = 0.7  
        self.jump_strength = -8 
        self.max_jump_height = 10
        self.rot = 0 if self.isPlay else 180
        self.endRot = -120
        self.startRot = 90
        self.sword_rot = 90
        self.block = False
        self.swinging = False 
        self.swing_speed = 5 
        self.swing_cooldown = False
        self.cooldown = 0
        self.swordSize = 80
        self.jab= False
        self.rotation_speed = 5
        self.kbv_x = 0  # Horizontal knockback velocity
        self.kbv_y = 0
        self.beenHit = False

        # sword coordinates
        self.tX = 0
        self.tY = 0
        self.bX = 0
        self.bY = 0

    def update(self, keys, enemy, right_click, left_click):

        move_x, move_y = 0, 0

        if self.beenHit:
            self.x += self.kbv_x
            self.y += self.kbv_y

            # Gradual decay of knockback velocity (slower than 0.9 for a more noticeable knockback)
            self.kbv_x *= 0.95  # Reduce the decay rate for smoother knockback
            self.kbv_y *= 0.95

            # Stop knockback once velocities are small enough
            if abs(self.kbv_x) < 0.1 and abs(self.kbv_y) < 0.1:
                self.kbv_x = 0
                self.kbv_y = 0
                self.beenHit = False


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
        if enemy and not self.is_jumping:
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

        self.block = False
        # Handle sword swinging
        if left_click and not right_click and not self.swinging and not self.swing_cooldown and not self.jab:
            self.swinging = True
            self.sword_rot = self.startRot  # Start swing from right to left (90 degrees left)
            self.swordSize = 80
        elif left_click and right_click and self.swinging and not self.jab:
            self.block = True
        elif right_click and not self.swinging and not self.swing_cooldown and not self.jab:
            self.sword_rot = 0
            self.swordSize = 60
            if left_click and not self.jab:
                self.jab = True
        elif not self.swinging and not self.jab:
            self.sword_rot = self.startRot
            self.swordSize = 80
            self.block = False

        self.doMove()

    def updateEnemy(self):
        if player and not player.is_jumping:
            # Calculate angle to player
            angle_to_enemy = math.atan2(player.y - self.y, player.x - self.x)
            
            # Smooth rotation: Interpolate between current rotation and target rotation
            target_rot = math.degrees(angle_to_enemy)
            delta_rot = (target_rot - self.rot) % 360  # Ensure delta is between 0-360
            if delta_rot > 180:
                delta_rot -= 360  # Make rotation wrap around (-180 to 180 range)
            
            # Apply a small smooth rotation adjustment
            self.rot += max(-self.rotation_speed, min(self.rotation_speed, delta_rot))

        # Calculate distance to player
        dist_to_player = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        
        # Adjust speed based on distance to the player (slow down when close)
        if dist_to_player > 75:
            move_x = self.speed * math.cos(math.radians(self.rot))
            move_y = self.speed * math.sin(math.radians(self.rot))

            # Apply movement
            self.x += move_x
            self.y += move_y

        # Check for sword swing initiation based on distance
        if dist_to_player <= self.swordSize * 2 and not self.swinging and not self.swing_cooldown and not self.jab and not self.block:
            if random.random() > .5:
                self.block = True
                self.cooldown = 120 
            elif random.random() > .25:
                self.jab = True
            elif random.random() > 0.0:
                self.swinging = True

        self.doMove()

    # Moves that they can do
    def doMove(self):
        " combo attacks "
        
        if self.jab:
            self.sword_rot = 0
            if not self.swing_cooldown:
                self.swordSize += self.swing_speed * 3 
                if self.swordSize >= 130:
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
                if self.sword_rot <= self.endRot:
                    if not left_click:
                        self.sword_rot = self.sword_rot
                        self.swing_cooldown = True
                    else:
                        self.sword_rot = self.endRot
            elif self.swing_cooldown:
                self.sword_rot += self.swing_speed * 1.5
                self.swordSize = 60
                if self.sword_rot >= self.startRot:
                    self.sword_rot = self.startRot
                    self.swing_cooldown = False
                    self.swinging = False
                    self.swordSize = 80
        elif self.block:
            self.cooldown -= 1
            if self.cooldown <= 0:
                self.block = False


    def checkHit(self):
        other = None
        if self.isPlay:
            other = enemy
        else:
            other = player

        dist = math.sqrt((self.x - other.tX)**2 + (self.y - other.tY)**2)



        if dist < self.radius and not self.block and not self.beenHit:
            print("Someone Was Hit")
            self.beenHit = True

            knockback_angle = math.atan2(self.y - other.y, self.x - other.x)
            knockback_magnitude = 15  # You can adjust this for stronger/weaker knockbacks

            self.kbv_x = knockback_magnitude * math.cos(knockback_angle)
            self.kbv_y = knockback_magnitude * math.sin(knockback_angle)



    def draw(self, screen):

        colPLa = "Orange" if self.isPlay else "Purple"

        colPLa = "Green" if self.block else colPLa

        if self.beenHit:
            colPLa = "Red"

        # sword
        if not self.block:
            sword_length = self.swordSize
            sword_x = self.x + sword_length * math.cos(math.radians(self.sword_rot + self.rot))
            sword_y = self.y + sword_length * math.sin(math.radians(self.sword_rot + self.rot))  
            pygame.draw.line(screen, "Black", (self.x, self.y), (sword_x, sword_y), 5)

            self.bX = self.x
            self.bY = self.y
            self.tX = sword_x
            self.tY = sword_y
        else:
            sLen = self.swordSize
            centerX = self.x
            centerY = self.y
            tX = self.x + self.radius
            tY = self.y + (sLen // 2)
            bX = self.x + self.radius
            bY = self.y - (sLen // 2)

            rotation_radians = math.radians(self.rot)
            rotated_tX = centerX + (tX - centerX) * math.cos(rotation_radians) - (tY - centerY) * math.sin(rotation_radians)
            rotated_tY = centerY + (tX - centerX) * math.sin(rotation_radians) + (tY - centerY) * math.cos(rotation_radians)
            rotated_bX = centerX + (bX - centerX) * math.cos(rotation_radians) - (bY - centerY) * math.sin(rotation_radians)
            rotated_bY = centerY + (bX - centerX) * math.sin(rotation_radians) + (bY - centerY) * math.cos(rotation_radians)
            self.bX = rotated_tX
            self.bY = rotated_tY
            self.tX = rotated_bX
            self.tY = rotated_bY

            pygame.draw.line(screen, "Black", (rotated_tX, rotated_tY), (rotated_bX, rotated_bY), 5)

        self.checkHit()

        # body + shadow ----- shadow is broken IDK
        shadow_surface = pygame.Surface((self.inRadius * 2, self.inRadius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, SHADOW_COLOR, (self.x, self.y), self.inRadius)
        screen.blit(shadow_surface, (self.x + 5 - self.inRadius, self.inY + 5 - self.inRadius))
        pygame.draw.circle(screen, colPLa, (self.x, self.y), self.radius)

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
        pygame.draw.circle(screen, colPLa , (int(eye_x), int(eye_y)), self.radius // 3)

        # left 
        eye_offset = self.radius
        adjusted_rot = self.rot - 80
        eye_x = self.x + eye_offset * math.cos(math.radians(adjusted_rot))
        eye_y = self.y + eye_offset * math.sin(math.radians(adjusted_rot))
        pygame.draw.circle(screen, colPLa , (int(eye_x), int(eye_y)), self.radius // 3)


# Initialize player and enemy
player = PlayObj(width // 2, height // 2, True)
enemy = PlayObj(width - 100, height // 2, False)
running = True
clock = pygame.time.Clock()
left_click = False
right_click = False  

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                left_click = True
            elif event.button == 3:
                right_click = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: 
                left_click = False
            elif event.button == 3:
                right_click = False
    keys = pygame.key.get_pressed()
    player.update(keys, enemy, right_click, left_click)
    enemy.updateEnemy()
    screen.fill((200, 200, 200))
    player.draw(screen)
    enemy.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()