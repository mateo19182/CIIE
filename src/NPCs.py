import pygame
import math
import random

import resource_manager
from items import Arrow, Wrench, Explosion
from pygame import mixer

class RangedEnemies(pygame.sprite.Sprite):
    ANIMATION_DELAY = 4
    ARROW_FRAME = 25
    SHOOT_DISTANCE = 300
    SHOOT_HEIGHT_THRESHOLD = 20

    def __init__(self,x,y,width,height,delay,arrows,sprite_sheet_name):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_count = 0
        self.frame_count = 0
        self.rect = pygame.Rect(x,y,width,height)
        self.mask = None
        self.sprite = None
        self.arrows = arrows
        self.orientation = "left"
        self.shoot = False
        self.sprite_sheet_name = sprite_sheet_name
        self.is_alive = True
        self.delay = delay

    def loop(self,player,volume):
            self.frame_count += 1
            if self.is_alive:
                if self.should_shoot(player):
                    self.shoot = True
                    if self.frame_count == self.ARROW_FRAME:
                        self.shoot_arrow(volume.sounds_volume)

            self.update_sprite(player)
        
    def should_shoot(self, player):
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        return distance < self.SHOOT_DISTANCE and abs(dy) <= self.SHOOT_HEIGHT_THRESHOLD
    
    def take_damage(self,volume):
        self.kill()
        death_sound = mixer.Sound(resource_manager.get_sound("arrow_girl_death"))
        death_sound.play()
        death_sound.set_volume(volume.sounds_volume)
        self.update_sprite(self)

    def shoot_arrow(self,volume):
        if self.sprite_sheet_name == "GnomeTinkerer":
            arrow = Wrench(self.rect,self.orientation)
        else:
            arrow = Arrow(self.rect,self.orientation)
        self.arrows.add(arrow)
        arrow_sound = mixer.Sound(resource_manager.get_sound("arrow"))
        arrow_sound.play()
        arrow_sound.set_volume(volume)

    def update_sprite(self,player):
        
        if self.shoot:
            sprite_sheet = "shoot"
            self.shoot = False
            self.ANIMATION_DELAY = self.delay
        else: 
            sprite_sheet = "idle"
            self.ANIMATION_DELAY = 9
        
        sprites = resource_manager.load_sprite_sheets("Enemies",self.sprite_sheet_name,16,16,False)
        sprites = sprites[sprite_sheet]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.sprite = pygame.transform.scale(self.sprite,(16 * 5, 16 * 5))
        self.animation_count += 1

        if(sprite_index == 0):
            self.frame_count = 0

        dx = player.rect.x - self.x

        if dx < 0:
            self.orientation = "left"
            self.sprite = pygame.transform.flip(self.sprite,True,False)
        elif dx > 0:
            self.orientation = "right"
            self.sprite = pygame.transform.flip(self.sprite,False,False)

        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self,window,offset_x):
        window.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))

class MeleeEnemie(pygame.sprite.Sprite):
    ANIMATION_DELAY = 20
    GRAVITY = 8
    
    def __init__(self,x,y,width,height,sprite_sheet_name):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_count = 0
        self.frame_count = 0
        self.rect = pygame.Rect(x,y,width,height)
        self.mask = None
        self.sprite = None
        self.orientation = "left"
        self.x_vel = 0
        self.fall = False
        self.is_alive = True
        self.sprite_sheet_name = sprite_sheet_name
        
    def loop(self,player,volume):
        self.frame_count += 1
        
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        distance = math.sqrt(dx**2 + dy**2)
        
        max_velocity = 2
    
        if distance < 300:
            ratio = min(1, distance / 150)
            self.x_vel = ratio * max_velocity * (dx / distance)
        else:
            self.x_vel = 0

        if not self.fall:
            self.rect.x += self.x_vel
            
        self.update_sprite(player)

    def take_damage(self,volume):
        self.kill()
        death_sound = mixer.Sound(resource_manager.get_sound("melee_enemie_death"))
        death_sound.play()
        death_sound.set_volume(volume.sounds_volume)
        self.update_sprite(self)

    def update_sprite(self,player):
        sprite_sheet = "idle"
        if self.sprite_sheet_name=="Skeleton":
            sprites = resource_manager.load_sprite_sheets("Enemies",self.sprite_sheet_name,32,32,False)
        else:
            sprites = resource_manager.load_sprite_sheets("Enemies",self.sprite_sheet_name,16,16,False)
        sprites = sprites[sprite_sheet]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.sprite = pygame.transform.scale(self.sprite,(16 * 5, 16 * 5))
        self.animation_count += 1

        if(sprite_index == 0):
            self.frame_count = 0

        dx = player.rect.x - self.rect.x

        if dx < 0:
            self.orientation = "left"
            self.sprite = pygame.transform.flip(self.sprite,True,False)
        elif dx > 0:
            self.orientation = "right"
            self.sprite = pygame.transform.flip(self.sprite,False,False)

        self.update()

    def update(self):
        self.rect.x += self.x_vel
        self.rect = self.sprite.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        
    def draw(self,window,offset_x):
        window.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))

class Skull(pygame.sprite.Sprite):
    ANIMATION_DELAY = 10
    GRAVITY = 1

    def __init__(self,x,y,width,height,sprite_sheet_name):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_count = 0
        self.frame_count = 0
        self.rect = pygame.Rect(x,y,width,height)
        self.mask = None
        self.sprite = None
        self.orientation = "left"
        self.x_vel = 0
        self.y_vel = 0
        self.is_alive = True
        self.sprite_sheet_name = sprite_sheet_name
        
    def loop(self,player,volume):
        self.frame_count += 1
        
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        distance = math.sqrt(dx**2 + dy**2)
        
        max_velocity = 2
    
        if distance < 500:
            ratio = min(1, distance / 150)
            self.x_vel = ratio * max_velocity * (dx / distance)
            self.y_vel = ratio * max_velocity * (dy / distance) 
        else:
            self.x_vel = 0
            self.y_vel = 0 
            
        self.update_sprite(player)

    def take_damage(self,volume):
        self.kill()
        death_sound = mixer.Sound(resource_manager.get_sound("skeleton_death"))
        death_sound.play()
        death_sound.set_volume(volume.sounds_volume)
        self.update_sprite(self)

    def update_sprite(self,player):
        sprite_sheet = "idle"
        sprites = resource_manager.load_sprite_sheets("Enemies",self.sprite_sheet_name,64,64,False)
        sprites = sprites[sprite_sheet]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.sprite = pygame.transform.scale(self.sprite,(16 * 5, 16 * 5))
        self.animation_count += 1

        if(sprite_index == 0):
            self.frame_count = 0

        dx = player.rect.x - self.rect.x

        if dx < 0:
            self.orientation = "left"
            self.sprite = pygame.transform.flip(self.sprite,True,False)
        elif dx > 0:
            self.orientation = "right"
            self.sprite = pygame.transform.flip(self.sprite,False,False)

        self.update()
        
    def update(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.rect = self.sprite.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        
    def draw(self,window,offset_x):
        window.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))

class Boss(pygame.sprite.Sprite):
    SPRITES = resource_manager.load_sprite_sheets("Enemies","Boss",32,32,False)
    ANIMATION_DELAY = 20
    GRAVITY = 5
    DAMAGE_COOLDOWN = 500
    
    def __init__(self,x,y,width,height):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_count = 0
        self.frame_count = 0
        self.rect = pygame.Rect(x,y,width,height)
        self.mask = None
        self.sprite = None
        self.orientation = "left"
        self.x_vel = 0
        self.fall = False
        self.vida = 3
        self.is_alive = True
        self.last_damage_time = 0
        
    def loop(self,player,volume):
        self.frame_count += 1
        
        self.die()
            
        self.update_sprite()
        
    def take_damage(self,volume):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_damage_time > self.DAMAGE_COOLDOWN:
            self.vida -= 1
            self.last_damage_time = current_time
            if self.vida <= 0:
                self.is_alive = False
                death_sound = mixer.Sound(resource_manager.get_sound("boss_death"))
                death_sound.play()
                death_sound.set_volume(volume.sounds_volume)
                self.kill()
                self.update_sprite()
        
    def update_sprite(self):
        sprites = self.SPRITES["Attack"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.sprite = pygame.transform.scale(self.sprite,(32 * 8, 32 * 8))
        self.sprite = pygame.transform.flip(self.sprite,True,False)
        self.animation_count += 1

        if(sprite_index == 0):
            self.frame_count = 0

        self.update()

    def update(self):
        self.rect.x += self.x_vel
        self.rect = self.sprite.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
            
    def die(self):
        if self.vida == 0:
            self.is_alive = False
        
    def draw(self,window,offset_x):
        window.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))
        
        bar_width = 300
        bar_height = 10 
        bar_x = self.rect.x - offset_x 
        bar_y = self.rect.y - 20
        pygame.draw.rect(window, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(window, (0, 255, 0), (bar_x, bar_y, bar_width * (self.vida / 3), bar_height))

class SecondBoss(pygame.sprite.Sprite):
    SPRITES = resource_manager.load_sprite_sheets("Enemies", "SecondBoss", 32, 32, False)
    ANIMATION_DELAY = 15
    GRAVITY = 5
    DAMAGE_COOLDOWN = 500
    
    def __init__(self, x, y, width, height):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_count = 0
        self.frame_count = 0
        self.rect = pygame.Rect(x, y, width, height)
        self.mask = None
        self.sprite = None
        self.orientation = "left"
        self.x_vel = 0
        self.fall = False
        self.vida = 7
        self.is_alive = True
        self.last_damage_time = 0
        self.explosions = pygame.sprite.Group()  
        self.state = "Idle"
        self.player_proximity_threshold = 1000 

    def loop(self, player, volume):
        self.frame_count += 1
        self.check_proximity(player)
        self.die()
        self.update_sprite()
        self.attack(player)

    def check_proximity(self, player):
        distance_to_player = math.hypot(player.rect.x - self.rect.x, player.rect.y - self.rect.y)
        if distance_to_player < self.player_proximity_threshold:
            self.state = "Attack"
        else:
            self.state = "Idle"

    def update_sprite(self):
        if self.state == "Attack":
            sprites = self.SPRITES["Attack"]
        else:
            sprites = self.SPRITES["Idle"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.sprite = pygame.transform.scale(self.sprite, (32 * 8, 32 * 8))
        self.sprite = pygame.transform.flip(self.sprite, True, False)
        self.animation_count += 1
    
        if sprite_index == 0 and self.state == "Attack":
            self.frame_count = 0
        self.update()

    def attack(self, player):
        if self.state == "Attack" and self.frame_count == 100:
            self.create_explosion(player)
            self.frame_count = 0
            self.state = "Idle" 

    def create_explosion(self, player):
        explosion_x = player.rect.x + random.randint(-50, 50)
        explosion_y = player.rect.y + random.randint(-50, 50)
        explosion = Explosion(explosion_x, explosion_y)
        self.explosions.add(explosion) 

    def take_damage(self,volume):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_damage_time > self.DAMAGE_COOLDOWN:
            self.vida -= 1
            self.last_damage_time = current_time
            if self.vida <= 0:
                self.is_alive = False
                death_sound = mixer.Sound(resource_manager.get_sound("boss_death"))
                death_sound.play()
                death_sound.set_volume(volume.sounds_volume)
                self.kill()
                self.update_sprite()
        
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        super().update()
        self.explosions.update()
                
    def die(self):
        if self.vida == 0:
            self.is_alive = False
        
    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
        for explosion in self.explosions:
            explosion.draw(window, offset_x)
        bar_width = 300
        bar_height = 10 
        bar_x = self.rect.x - offset_x 
        bar_y = self.rect.y - 20
        pygame.draw.rect(window, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(window, (0, 255, 0), (bar_x, bar_y, bar_width * (self.vida / 3), bar_height))
        

class ThirdBoss(pygame.sprite.Sprite):
    SPRITES = resource_manager.load_sprite_sheets("Enemies", "ThirdBoss", 140, 140, False)
    ANIMATION_DELAY = 20
    GRAVITY = 5
    DAMAGE_COOLDOWN = 500
    MOVE_SPEED = 2
    DETECTION_RANGE = 500  
    def __init__(self, x, y, width, height):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_count = 0
        self.frame_count = 0
        self.rect = pygame.Rect(x, y, width, height)
        self.mask = None
        self.sprite = None
        self.orientation = "left"
        self.x_vel = 0
        self.fall = False
        self.vida = 3
        self.is_alive = True
        self.last_damage_time = 0
        self.state = "IDLE"  # Initial state
        
    def loop(self, player, volume):
        self.frame_count += 1
        if self.detect_player2(player):
            self.state = "WALK"
            if self.detect_player(player):
                self.state = "ATTACK"
            else:
                self.approach_player(player)

        self.die()
        self.update_sprite()
        
    def take_damage(self, volume):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_damage_time > self.DAMAGE_COOLDOWN:
            self.vida -= 1
            self.last_damage_time = current_time
            self.state = "HURT" if self.vida > 0 else "DEATH"
            mixer.Sound(resource_manager.get_sound("hit")).play()
            self.update_sprite()
            if self.vida <= 0:
                #self.is_alive = False
                mixer.Sound(resource_manager.get_sound("boss_death")).play()
                self.state = "DEATH"
    
    def detect_player(self, player):
        distance_x = abs(self.rect.centerx - player.rect.centerx)
        attack_distance_x = 100
        if distance_x <= attack_distance_x:
            return True
        else:
            return False
    def detect_player2(self, player):
        distance_x = abs(self.rect.centerx - player.rect.centerx)
        attack_distance_x = self.DETECTION_RANGE
        if distance_x <= attack_distance_x:
            return True
        else:
            return False

    def approach_player(self, player):
        player_x = player.rect.centerx 
        boss_x = self.rect.centerx
        if boss_x < player_x:
            self.x_vel = self.MOVE_SPEED 
            self.orientation = "left"
        elif boss_x > player_x:
            self.x_vel = -self.MOVE_SPEED 
            self.orientation = "right"
        else:
            self.x_vel = 0 
        self.x += self.x_vel
        if(self.sprite!=None):
            self.sprite = pygame.transform.flip(self.sprite, self.orientation == "left", False)
        self.rect.x = self.x


    def update_sprite(self):
        if self.state == "DEATH":
            sprites = self.SPRITES["DEATH"]
        elif self.state == "HURT":
            sprites = self.SPRITES["HURT"]
        elif self.state == "ATTACK":
            sprites = self.SPRITES["ATTACK"]
        elif self.state == "WALK":
            sprites = self.SPRITES["WALK"]
        else:  
            sprites = self.SPRITES.get(self.state, self.SPRITES["IDLE"])
            
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.sprite = pygame.transform.scale(self.sprite, (64 * 8, 64 * 8))
        if self.orientation == "left":
            self.sprite = pygame.transform.flip(self.sprite, True, False)
        self.animation_count += 1
        
        if sprite_index == 0 and self.state == "HURT":
            self.state = "IDLE" 
        if sprite_index == 3 and self.state == "DEATH":
            self.is_alive = False
            if (not self.is_alive):
                self.kill()


        self.update()
    
    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y 
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        
    def die(self):
        if self.vida == 0:
            self.state = "DEATH"
        
    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
        
        bar_width = 300
        bar_height = 10
        bar_x = self.rect.x - offset_x
        bar_y = self.rect.y - 20
        pygame.draw.rect(window, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(window, (0, 255, 0), (bar_x, bar_y, bar_width * (self.vida / 3), bar_height))

class Mercader(pygame.sprite.Sprite):
    SPRITES = resource_manager.load_sprite_sheets("Mercader","Mercader",16,16,False)
    ANIMATION_DELAY = 10

    def __init__(self,x,y,width,height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_count = 0
        self.frame_count = 0
        self.rect = pygame.Rect(x,y,width,height)
        self.mask = None
        self.sprite = None
        self.orientation = "left"
        self.close = False
        self.negociating = False

    def loop(self,player,offset_x):
        self.frame_count += 1

        self.update_sprite(player)


    def update_sprite(self,player):
        sprites = self.SPRITES["OverworkedVillagerIdleSide"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.sprite = pygame.transform.scale(self.sprite,(16 * 5, 16 * 5))
        self.animation_count += 1

        if(sprite_index == 0):
            self.frame_count = 0

        dx = player.rect.x - self.x
        dy = player.rect.y - self.y

        if dx < 0:
            self.orientation = "left"
            self.sprite = pygame.transform.flip(self.sprite,True,False)
        elif dx > 0:
            self.orientation = "right"
            self.sprite = pygame.transform.flip(self.sprite,False,False)

        if dx > -100 and dx < 100 and dy > -100 and dy < 100:
            self.close = True
        else:
            self.close = False
            self.negociating = False

        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def show_dialog(self,window,offset_x):
        dialog_surface = pygame.Surface((320, 20))
        dialog_surface.set_alpha(128)
        window.blit(dialog_surface, (self.rect.x - offset_x-90,self.rect.y-15))
        text = pygame.font.Font("assets/font.ttf", 15).render("Press N to negociate", True, "#b68f40")
        window.blit(text, (self.rect.x - offset_x-80,self.rect.y-10))

    def show_dialog_negociating(self,window,offset_x,opt1,opt2,opt3):
        dialog_surface = pygame.Surface((320, 20))
        dialog_surface.set_alpha(128)
        for button in [opt1, opt2, opt3]:
            button.changeColor(pygame.mouse.get_pos())
            button.update(window)

    def draw(self,window,offset_x,opt1,opt2,opt3):
        window.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))
        if self.close:
            if self.negociating:
                self.show_dialog_negociating(window,offset_x,opt1,opt2,opt3)
            else:
                self.show_dialog(window,offset_x)


def negociation1(player,volume):
    if player.coins >= 10 and player.lives.lives < 3 :
        player.coins -= 10
        player.lives.lives += 1
        deal_sound = mixer.Sound(resource_manager.get_sound("done_deal"))
        deal_sound.play()
        deal_sound.set_volume(volume)

def negociation2(player,volume):
    if player.coins >= 15 and player.lives.lives < 2 :
        player.coins -= 15
        player.lives.lives += 2
        deal_sound = mixer.Sound(resource_manager.get_sound("done_deal"))
        deal_sound.play()
        deal_sound.set_volume(volume)

def negociation3(player,volume):
    if player.gems >= 1 :
        player.coins += 10
        player.gems -= 1
        deal_sound = mixer.Sound(resource_manager.get_sound("done_deal"))
        deal_sound.play()
        deal_sound.set_volume(volume)   
