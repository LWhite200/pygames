import pygame  # type: ignore
import math
import random
from fractions import Fraction



width, height = 1200, 655



ORANGE = (230, 150, 0)
PURPLE = (128, 0, 128)
SHADOW_COLOR = (50, 50, 50, 100)

class PlayObj:
    def __init__(self, x, y, isPlay, isLong, startHP):
        self.x = x
        self.y = y
        self.maxHP = startHP
        self.curHP = self.maxHP
        self.power = 25 if isLong else 22
        self.isPlay = isPlay
        self.inY = y
        self.speed = 3 if self.isPlay else 2
        if not isLong: self.speed *= 2
        self.inRadius = 30
        self.radius = 30
        self.velocity_y = 0  
        self.is_jumping = False  
        self.gravity = 0.7  
        self.jump_strength = -8 
        self.max_jump_height = 10
        self.rot = 0 if self.isPlay else 180
        self.endRot = -130
        self.startRot = 90
        self.sword_rot = self.startRot
        self.block = False
        self.swinging = False 
        self.swing_speed = 1.5 if isLong else 5
        self.swing_cooldown = False
        self.cooldown = 0
        self.swordNorm = 180 if isLong else 80
        self.swordSize = self.swordNorm # 80
        self.jab= False
        self.rotation_speed = 5
        self.kbv_x = 0
        self.kbv_y = 0
        self.beenHit = False
        self.stunned = 0
        self.stunStart = 0
        self.tX = 0
        self.tY = 0
        self.bX = 0
        self.bY = 0
    
    def knockBack(self):
        if self.beenHit:
            self.x += self.kbv_x
            self.y += self.kbv_y
            self.kbv_x *= 0.95
            self.kbv_y *= 0.95

            if abs(self.kbv_x) < 0.1 and abs(self.kbv_y) < 0.1:
                self.kbv_x = 0
                self.kbv_y = 0
                self.beenHit = False

    def update(self, keys, enemy, right_click, left_click):

        move_x, move_y = 0, 0
        self.knockBack()

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

        # The button presses to do things when nothing going on
        if self.block and not (left_click and right_click):
            self.block = False
        if not self.block and not self.swinging and not self.swing_cooldown and not self.jab:
            if left_click:
                self.swinging = True
                self.sword_rot = self.startRot
                self.swordSize = self.swordNorm
            elif right_click:
                self.jab = True
            else:
                self.block = False
                self.jab = False
                self.sword_rot = self.startRot
                self.swordSize = self.swordNorm
        elif left_click and right_click:
            self.block = True
            self.jab = False
            self.sword_rot = self.startRot
            self.swordSize = self.swordNorm
        elif not right_click and not (self.swinging or self.swing_cooldown):
            self.block = False
            self.sword_rot = self.startRot
            self.swordSize = self.swordNorm
        

        self.doMove()

    def updateEnemy(self):
        self.knockBack()
        distPla = 75
        if self.curHP < (self.maxHP // 2):
            distPla *= 2
        distPla = max(distPla, player.swordSize)
        if player and not player.is_jumping:
            angle_to_enemy = math.atan2(player.y - self.y, player.x - self.x)
            target_rot = math.degrees(angle_to_enemy)
            delta_rot = (target_rot - self.rot) % 360
            if delta_rot > 180:
                delta_rot -= 360
            self.rot += max(-self.rotation_speed, min(self.rotation_speed, delta_rot))
        dist_to_player = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        if dist_to_player > distPla:
            move_x = self.speed * math.cos(math.radians(self.rot))
            move_y = self.speed * math.sin(math.radians(self.rot))
            self.x += move_x
            self.y += move_y
        self.x = max(self.radius, min(self.x, width - self.radius))
        self.y = max(self.radius, min(self.y, height - self.radius))

            
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

        if self.block or self.jab:
            self.cooldown -= 1
            if self.cooldown <= 0:
                self.block = False
                self.jab = False
                self.cooldown = 0

        # Check for sword swing initiation based on distance
        if dist_to_player <= distPla * 2 and not self.swinging and not self.swing_cooldown and not self.is_jumping and self.cooldown <= 0:
            if player.stunned:
                if random.random() > 0.40:
                    self.swinging = True
                else:
                    self.jab = True
                    self.cooldown = 80 if random.random() > .5 else 30
            elif player.block:
                if 0.7 > random.random() > .45:
                    self.inY = self.y
                    self.is_jumping = True
                    self.velocity_y = self.jump_strength
                elif random.random() > 0.25:
                    self.swinging = True
                elif random.random() > 0:
                    self.block = True
                    self.cooldown = 100 if random.random() > .5 else 60
                else:
                    self.jab = True
                    self.cooldown = 80 if random.random() > .5 else 30
            elif player.jab or player.swinging:
                if random.random() > 0.70:
                    self.block = True
                    self.cooldown = 120 if random.random() > .5 else 60
                elif random.random() > .60:
                    self.swinging = True
                elif random.random() > .45:
                    self.inY = self.y
                    self.is_jumping = True
                    self.velocity_y = self.jump_strength
                elif random.random() > 30:
                    self.jab = True
                    self.cooldown = 80 if random.random() > .5 else 30
            else:
                if random.random() > 0.80:
                    self.block = True
                    self.cooldown = 120 if random.random() > .5 else 60
                elif random.random() > .50:
                    self.jab = True
                    self.cooldown = 80 if random.random() > .5 else 30
                elif random.random() > .20:
                    self.swinging = True

        self.doMove()

    # Moves that they can do
    def doMove(self):
        " combo attacks "
        
        if self.jab:
            if self.sword_rot != 0:
                if self.sword_rot > 0:
                    self.sword_rot -= 2 * self.swing_speed
                elif self.sword_rot < 0:
                    self.sword_rot += 2 * self.swing_speed

                if abs(self.sword_rot) < 10:
                    self.sword_rot = 0

            self.swordSize = self.swordNorm
            if player == self and not right_click:
                self.jab = False


        elif self.swinging:
            if not self.swing_cooldown:
                self.sword_rot -= self.swing_speed * 3
                if self.sword_rot <= self.endRot:
                    self.sword_rot = self.sword_rot
                    self.swing_cooldown = True
            elif self.swing_cooldown:
                self.sword_rot += self.swing_speed * 1.75
                self.swordSize = int(self.swordNorm * Fraction(3, 4))
                if self.sword_rot >= self.startRot:
                    self.sword_rot = self.startRot
                    self.swing_cooldown = False
                    self.swinging = False
                    self.swordSize = self.swordNorm

    # check if you've been hit
    def checkHit(self):
        other = None
        if self.isPlay:
            other = enemy
        else:
            other = player

        dist1 = math.sqrt((self.x - other.tX)**2 + (self.y - other.tY)**2)
        dist2 = math.sqrt((self.x - ((other.tX + other.bX) //2))**2 + (self.y - ((other.tY + other.bY) //2))**2)
        dist3 = math.sqrt((self.x - other.bX)**2 + (self.y - other.bY)**2)
        dist4 = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2) # body collision

        if (dist1 < self.radius or dist2 < self.radius * 2 or dist3 < self.radius) and not self.block and not self.beenHit and not self.is_jumping and not other.block:
            self.beenHit = True
            knockback_magnitude = 15
            self.curHP -= other.power
            if not other.jab:
                knockback_magnitude *= 2
                
            if self.curHP <= 0:
                self.curHP = 0
            knockback_angle = math.atan2(self.y - other.y, self.x - other.x)
              # You can adjust this for stronger/weaker knockbacks
            self.kbv_x = knockback_magnitude * math.cos(knockback_angle)
            self.kbv_y = knockback_magnitude * math.sin(knockback_angle)

        elif (dist1 < self.radius * 2 or dist2 < self.radius * 2 or dist3 < self.radius) and self.block and other.jab and not self.beenHit:
            other.stunned = 900  # mili second
            other.stunStart = pygame.time.get_ticks()

        elif (dist4 < self.radius * 2.5) and other.is_jumping and self.block and not self.beenHit:
            self.beenHit = True
            self.curHP -= other.power // 4
            if self.curHP <= 0:
                self.curHP = 0
            knockback_angle = math.atan2(self.y - other.y, self.x - other.x)
            knockback_magnitude = 15 
            self.kbv_x = knockback_magnitude * math.cos(knockback_angle)
            self.kbv_y = knockback_magnitude * math.sin(knockback_angle)



    def draw(self, screen):
        colPLa = "Orange" if self.isPlay else "Purple"
        colPLa2 = ORANGE if self.isPlay else PURPLE
        colPLa = "Green" if self.block else colPLa
        if self.beenHit:
            colPLa = "Red"
        if self.stunned != 0:
            colPLa = "Blue"

        # sword
        if not self.block:
            sword_length = self.swordSize
            sword_x = self.x + sword_length * math.cos(math.radians(self.sword_rot + self.rot))
            sword_y = self.y + sword_length * math.sin(math.radians(self.sword_rot + self.rot))  
            pygame.draw.line(screen, (200,200,200), (self.x, self.y), (sword_x, sword_y), 5)

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

            pygame.draw.line(screen, (200,200,200), (rotated_tX, rotated_tY), (rotated_bX, rotated_bY), 5)

        self.checkHit()

        # body + shadow ----- shadow is broken IDK
        shadow_surface = pygame.Surface((self.inRadius * 2, self.inRadius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, SHADOW_COLOR, (self.x, self.y), self.inRadius)
        screen.blit(shadow_surface, (self.x + 5 - self.inRadius, self.inY + 5 - self.inRadius))
        pygame.draw.circle(screen, colPLa, (self.x, self.y), self.radius)
        oS = self.radius // 2 # Draw eyes
        eye_x = self.x + oS * math.cos(math.radians(self.rot))
        eye_y = self.y + oS * math.sin(math.radians(self.rot))
        pygame.draw.circle(screen, "White", (int(eye_x), int(eye_y)), self.radius // 3)
        eye_offset = self.radius # right
        adjusted_rot = self.rot + 80
        eye_x = self.x + eye_offset * math.cos(math.radians(adjusted_rot))
        eye_y = self.y + eye_offset * math.sin(math.radians(adjusted_rot))
        pygame.draw.circle(screen, colPLa2 , (int(eye_x), int(eye_y)), self.radius // 3)
        eye_offset = self.radius # left 
        adjusted_rot = self.rot - 80
        eye_x = self.x + eye_offset * math.cos(math.radians(adjusted_rot))
        eye_y = self.y + eye_offset * math.sin(math.radians(adjusted_rot))
        pygame.draw.circle(screen, colPLa2 , (int(eye_x), int(eye_y)), self.radius // 3)

def reset():
    global player, enemy, start_time, timer_duration

    # Reset player and enemy positions, health, and other stats
    player = PlayObj(width * .25, height // 2, True, True if random.random() > 0.5 else False, 100)
    enemy = PlayObj(width * .75, height // 2, False, True if random.random() > 0.5 else False, 100)

    # Reset game timer
    start_time = pygame.time.get_ticks()
    timer_duration = 11000  # Set back to the initial duration

def show_game_over_screen():
    global running
    font = pygame.font.SysFont(None, 48)
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    player_hp_text = font.render(f"Player HP: {player.curHP} / {player.maxHP}", True, (255, 255, 255))
    enemy_hp_text = font.render(f"Enemy HP: {enemy.curHP} / {enemy.maxHP}", True, (255, 255, 255))

    screen.fill((0, 0, 0))  # Black background for game over screen
    screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 4))
    screen.blit(player_hp_text, (width // 2 - player_hp_text.get_width() // 2, height // 2 - 50))
    screen.blit(enemy_hp_text, (width // 2 - enemy_hp_text.get_width() // 2, height // 2))

    pygame.display.flip()
    running = False

player = None
enemy = None
running = True
clock = pygame.time.Clock()
left_click = False
right_click = False  

start_time = pygame.time.get_ticks()
timer_duration = 11000  

def main(playHP, enemHP):
    global player, enemy, left_click, right_click, start_time, timer_duration, running, clock, screen, width, height

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Circle Game")

    running = True
    start_time = pygame.time.get_ticks()

    player = PlayObj(width * .25, height // 2, True, True if random.random() > 0.5 else False, playHP)
    enemy = PlayObj(width * .75, height // 2, False, True if random.random() > 0.5 else False, enemHP)

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

        elapsed_time = pygame.time.get_ticks() - start_time
        remaining_time = max(0, timer_duration - elapsed_time)

        if player.curHP <= 0 or enemy.curHP <= 0 or remaining_time <= 0:
            show_game_over_screen()
            pygame.time.wait(2000)
        else:
            keys = pygame.key.get_pressed()
            if player.stunned == 0: 
                player.update(keys, enemy, right_click, left_click)
            else:
                player.sword_rot = player.startRot
                player.jab = False
                player.swing_cooldown = False
                player.swinging = False
                if (pygame.time.get_ticks() - player.stunStart) > player.stunned:
                    player.stunned = 0
                    player.stunStart = 0

            if enemy.stunned == 0:
                enemy.updateEnemy()
            else:
                enemy.sword_rot = enemy.startRot
                enemy.jab = False
                enemy.swing_cooldown = False
                enemy.swinging = False
                enemy.cooldown = 0
                if (pygame.time.get_ticks() - enemy.stunStart) > enemy.stunned:
                    enemy.stunned = 0
                    enemy.stunStart = 0

            screen.fill((0, 0, 40))
            font = pygame.font.SysFont(None, 200)
            timer_text = font.render(f"{remaining_time // 1000}", True, (255, 255, 255))

            font = pygame.font.SysFont(None, 34)
            player_hp_text = font.render(f"{player.curHP}", True, (255, 255, 255))
            enemy_hp_text = font.render(f"{enemy.curHP}", True, (255, 255, 255))
            screen.blit(player_hp_text, (width // 2 - 250, int(height * Fraction(4,5))))
            screen.blit(enemy_hp_text, (width // 2 + 100, int(height * Fraction(4,5))))

            screen.blit(timer_text, (width // 2 - 50, height // 2 - 50))
            if enemy.is_jumping:
                player.draw(screen)
                enemy.draw(screen)
            else:
                enemy.draw(screen)
                player.draw(screen)


            pygame.display.flip()
        
        
        clock.tick(60)

    return str(str(player.curHP) + "," + str(enemy.curHP))