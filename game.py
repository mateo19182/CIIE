import random
import time
import math
import pygame, sys, pickle

import resource_manager

from os import listdir
from os.path import isfile, join
from button import Button
from partida import Partida, Volume
from pygame import mixer


pygame.init()

SCREEN = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5 * FPS
TIMER = 0
LEVEL = 1
BAR_WIDTH = 300
BAR_HEIGHT = 20


window = pygame.display.set_mode((WIDTH,HEIGHT))

class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 2000
    SPRITES = resource_manager.load_sprite_sheets("main", "",32,32,True)

    ANIMATION_DELAY = 8
    MELEE_COOLDOWN = 1.0
    MELEE_DURATION = 0.2
    RANGED_DURATION = 0.4

    def __init__(self,x,y,width,height, lives,projectiles,coins,gems):
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 1
        self.coins = coins
        self.gems = gems
        self.lives = lives
        self._last_called = 0
        self.hit = False
        self.last_melee_time = 0
        self.melee_active = False
        self.melee_start_time = 0
        self.projectiles = projectiles
        self.ranged_active = False
        self.last_ranged_time = 0
        self.frame_count = 0
        self.dead = False

    def jump(self,volume):
        self.y_vel = -self.GRAVITY / 3
            
        self.animation_count = 0
        self.jump_count +=1

        if self.jump_count == 1:
            self.fall_count = 0

        jump_sound = mixer.Sound(resource_manager.get_sound("jump"))
        jump_sound.play() 
        jump_sound.set_volume(volume)   

    def move(self,dx,dy, delta, window, partida, volume):
        self.rect.x += dx  * delta
        self.rect.y += dy * delta
        if self.rect.y > HEIGHT + 100 :
            self.die(window, partida, volume)

    def move_left(self,vel):
        self.x_vel = -vel

        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self,vel):
        self.x_vel = vel

        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
            
    def loop(self,delta, enemies, window, partida, volume):
        self.y_vel += min(30, (self.fall_count * delta * self.GRAVITY))
        self.move(self.x_vel,self.y_vel, delta, window, partida, volume)
        self.fall_count += 1
        
        for projectile in self.projectiles:
            projectile.update()
        
        self.update_sprite()
        self.check_attack(enemies)

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def get_hit(self, volume):
        current_time = time.time()
        if current_time - self._last_called < 1:
            return
        self._last_called = current_time
        self.hit=True
        self.update_sprite()
        self.lives.lives -= 1
        self.animation_count = 0
        hit_sound = mixer.Sound(resource_manager.get_sound("hit"))
        hit_sound.play()
        hit_sound.set_volume(volume)

    def hit_head(self):
        self.y_vel = 0
        
    def collect_coin(self,volume):
        self.coins += 1 
        coin_sound = mixer.Sound(resource_manager.get_sound("coin"))
        coin_sound.play()
        coin_sound.set_volume(volume)

    def collect_gem(self,volume):
        self.gems += 1 
        gem_sound = mixer.Sound(resource_manager.get_sound("coin"))
        gem_sound.play() 
        gem_sound.set_volume(volume)   

    def melee_attack(self):
        current_time = time.time()
        if current_time - self.last_melee_time < self.MELEE_COOLDOWN:
            return
        self.melee_active = True
        self.melee_start_time = current_time
        self.last_melee_time = current_time
        self.animation_count = 0
        self.update_sprite()

    def get_melee_hitbox(self):
        melee_hitbox_size = (12, 12)
        offset_x = self.rect.width if self.direction == "right" else -melee_hitbox_size[0]
        melee_hitbox = pygame.Rect(self.rect.x + offset_x, self.rect.y, *melee_hitbox_size)
        #melee_hitbox.x -= self.x_vel
        return melee_hitbox
    
    def ranged_attack(self):
        current_time = time.time()
        if current_time - self.last_ranged_time >= self.MELEE_COOLDOWN:
            self.last_ranged_time = current_time
            self.animation_count = 0
            self.ranged_active = True
            self.update_sprite()
            
        if self.frame_count == 21:
            projectile = Fireball(self.rect, self.direction)
            self.projectiles.add(projectile)

    def die(self, window, partida, volume):
        if not self.dead : 
            self.update_sprite()
            self.x_vel = 0
            self.y_vel = 0
            self.jump_count = 3
            death_sound = mixer.Sound(resource_manager.get_sound("death"))
            mixer.music.stop()
            death_sound.play()
            death_sound.set_volume(volume.sounds_volume)
            partida.coins = self.coins
            partida.gems = self.gems
            death_menu(window, partida, volume)
        
    def check_attack(self, enemies):
        if self.melee_active:
            hitbox = self.get_melee_hitbox()
            for enemy in enemies:
                if hitbox.colliderect(enemy.rect):
                    enemy.take_damage()  
                    break 

    def update_sprite(self):
        sprite_sheet = "idle"

        if self.lives.lives <= 0:
            sprite_sheet = "die"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.hit:
            sprite_sheet = "hit"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel !=0:
            sprite_sheet = "run"
        elif self.melee_active:
            sprite_sheet = "melee"
        elif self.ranged_active:
            sprite_sheet = "ranged"
            
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        
        if sprite_sheet == "die": 
            sprite_index = len(sprites) - 1        
        self.sprite = sprites[sprite_index]
        self.animation_count +=1
        if sprite_sheet == "hit" and self.animation_count == 3:
            self.hit = False
            
        if(sprite_index == 0):
            self.frame_count = 0
            
        self.frame_count += 1

        self.update()

    def update(self):
        if self.melee_active and (time.time() - self.melee_start_time > self.MELEE_DURATION):
            self.melee_active = False       
        if self.ranged_active and (time.time() - self.last_ranged_time > self.RANGED_DURATION):
            self.ranged_active = False      
        self.rect = self.sprite.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self,window,offset_x):
        window.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))
        
class Object(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,name=None):
        super().__init__()
        self.rect = pygame.Rect(int(x),int(y),int(width),int(height))
        self.image = pygame.Surface((width,height),pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self,window,offset_x):
        window.blit(self.image,(self.rect.x - offset_x,self.rect.y))

class Lives:
    def __init__(self,num):
        self.observers = []
        self._lives = num

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def notify(self):
        for observer in self.observers:
            observer.update(self)

    @property
    def lives(self):
        return self._lives

    @lives.setter
    def lives(self, value):
        self._lives = value
        self.notify()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.images = [pygame.transform.scale(pygame.image.load(f'assets/Collectibles/coin_{i}.png'), (size, size)) for i in range(6)]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.frame_count = 0 

    def update(self):
        self.frame_count += 1 
        if self.frame_count >= 5:
            self.frame_count = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

    def draw(self,window,offset_x):
        window.blit(self.image,(self.rect.x - offset_x,self.rect.y))


class Gem(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.images = [pygame.transform.scale(pygame.image.load(f'assets/Collectibles/gem{i}.png'), (size, size)) for i in range(8)]
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.frame_count = 0 

    def update(self):
        self.frame_count += 1 
        if self.frame_count >= 5:
            self.frame_count = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

    def draw(self,window,offset_x):
        window.blit(self.image,(self.rect.x - offset_x,self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = resource_manager.get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block2(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = resource_manager.get_block2(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Block3(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = resource_manager.get_block3(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)   

class Block4(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = resource_manager.get_block4(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image) 
        
class Platform(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size)
        block = resource_manager.get_platform(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)


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

                for arrow in self.arrows:
                    arrow.update()

            self.update_sprite(player)
        
    def should_shoot(self, player):
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        return distance < self.SHOOT_DISTANCE and abs(dy) <= self.SHOOT_HEIGHT_THRESHOLD
    
    def take_damage(self):
        self.kill()
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

    def take_damage(self):
        self.kill()
        self.update_sprite(self)

    def update_sprite(self,player):
        sprite_sheet = "idle"
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
        
    def move_left(self, vel):
        self.x_vel = -vel

    def move_right(self, vel):
        self.x_vel = vel

    def update(self):
        self.rect.x += self.x_vel
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
        
    def take_damage(self):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_damage_time > self.DAMAGE_COOLDOWN:
            self.vida -= 1
            self.last_damage_time = current_time
            if self.vida <= 0:
                self.is_alive = False
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
    ANIMATION_DELAY = 20
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
        self.vida = 3
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
            if self.state == "Idle" and self.frame_count >= 100: 
                self.state = "Attack"
                self.frame_count = 0 
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
        if self.state == "Attack" and self.frame_count == 140:
            print("PUM!")
            self.create_explosion(player)
            self.state = "Idle" 

    def create_explosion(self, player):
        explosion_x = player.rect.x + random.randint(-50, 50)
        explosion_y = player.rect.y + random.randint(-50, 50)
        explosion = Explosion(explosion_x, explosion_y)
        self.explosions.add(explosion) 

    def take_damage(self):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_damage_time > self.DAMAGE_COOLDOWN:
            self.vida -= 1
            self.last_damage_time = current_time
            if self.vida <= 0:
                self.is_alive = False
                self.kill()
                self.update_sprite()
        
    def update(self):
        self.rect.x += self.x_vel
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        super().update()
        self.explosions.update()
                
    def die(self):
        if self.vida == 0:
            self.is_alive = False
        
    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
        
        bar_width = 300
        bar_height = 10 
        bar_x = self.rect.x - offset_x 
        bar_y = self.rect.y - 20
        pygame.draw.rect(window, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(window, (0, 255, 0), (bar_x, bar_y, bar_width * (self.vida / 3), bar_height))
        self.explosions.draw(window) 


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

        if dx < 0:
            self.orientation = "left"
            self.sprite = pygame.transform.flip(self.sprite,True,False)
        elif dx > 0:
            self.orientation = "right"
            self.sprite = pygame.transform.flip(self.sprite,False,False)

        if dx > -100:
            if dx < 100:
                self.close = True
            else:
                self.close = False
                self.negociating = False
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


class Arrow(pygame.sprite.Sprite):
    def __init__(self, enemy_rect,orientation):
        super().__init__()
        self.image = pygame.image.load("assets/Items/Arrow/Arrow.png")
        self.image = pygame.transform.scale(self.image, (16 * 5, 16 * 5))  # Ajusta el tamaño aquí

        if(orientation == "right"):
            self.rect = self.image.get_rect(midleft=(enemy_rect.midright[0] - 70, enemy_rect.centery + 10))  # Posiciona la flecha al lado derecho y un poco más abajo del centro del enemigo
            self.velocity = (3, 0)  # Ajusta la velocidad de la flecha
        else:
            self.image = pygame.transform.flip(self.image,True,False)
            self.rect = self.image.get_rect(midleft=(enemy_rect.midright[0] - 90, enemy_rect.centery + 10))  # Posiciona la flecha al lado derecho y un poco más abajo del centro del enemigo
            self.velocity = (-3, 0)  # Ajusta la velocidad de la flecha
            
    def is_offscreen(self,offset_x):
        return self.rect.right - offset_x < 0 or self.rect.left - offset_x > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT
    
    def update(self):
        self.rect.move_ip(self.velocity)

    def draw(self, screen,offset_x):
        screen.blit(self.image, (self.rect.x - offset_x, self.rect.y))      

class Wrench(pygame.sprite.Sprite):
    def __init__(self, enemy_rect, orientation):
        super().__init__()
        self.original_image = pygame.image.load("assets/Items/Wrench/wrench.png")
        self.original_image = pygame.transform.scale(self.original_image, (16 * 5, 16 * 5))
        self.angle = 0 
        self.image = self.original_image.copy()

        if orientation == "right":
            self.rect = self.image.get_rect(midleft=(enemy_rect.midright[0] - 70, enemy_rect.centery + 10))
            self.velocity = (3, 0)
        else:
            self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect(midleft=(enemy_rect.midright[0] - 90, enemy_rect.centery + 10))
            self.velocity = (-3, 0)
            
    def is_offscreen(self, offset_x):
        return self.rect.right - offset_x < 0 or self.rect.left - offset_x > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT
    
    def update(self):
        self.rect.move_ip(self.velocity)
        self.angle += 3
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, screen, offset_x):
        screen.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Fireball(pygame.sprite.Sprite):
    def __init__(self, initial_rect, direction):
        super().__init__()
        self.image = pygame.image.load("assets/Items/Fireball/fireball.png")
        self.image = pygame.transform.scale(self.image, (32 * 2, 32 * 2))
        self.rect = self.image.get_rect(center=initial_rect.center)

        self.speed = 10
        self.direction = direction
                
        if self.direction == "right":
            self.velocity = self.speed
        else: 
            self.image = pygame.transform.flip(self.image, True, False)
            self.velocity = -self.speed

    def update(self):
        self.rect.x += self.velocity
        
    def draw(self, screen, offset_x):
        screen.blit(self.image, (self.rect.x - offset_x, self.rect.y))
        

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('assets/Enemies/SecondBoss/Explosion.png').convert_alpha()
        self.images = self.load_explosion_images()
        self.current_frame = 0
        self.image = self.images[self.current_frame] 
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 0.2 

    def load_explosion_images(self):
        images = []
        for i in range(0, self.sprite_sheet.get_width(), 32): 
            image = self.sprite_sheet.subsurface(pygame.Rect(i, 0, 32, 32))
            scaled_image = pygame.transform.scale(image, (128, 128))
            images.append(scaled_image)
        return images

    def update(self):
        print(self.rect)
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.images):
            self.kill()
        else:
            self.image = self.images[int(self.current_frame)]
class Checkpoint(pygame.sprite.Sprite):
    ANIMATION_DELAY = 3
    
    def __init__(self,x,y,width,height,active):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_count = 0
        self.frame_count = 0
        self.rect = pygame.Rect(x,y,width,height)
        self.sprite = None
        self.activated = active
        self.activate_idle = active

    def activate(self):
        self.activated = True
        
    def loop(self):
        self.frame_count += 1
        self.update_sprite()
        
    def update_sprite(self):
        
        if self.activated:
            sprite_sheet = "flag_out"
        elif not self.activated: 
            sprite_sheet = "no_flag"
            
        if self.activate_idle:
            sprite_sheet = "idle"

        sprites = resource_manager.load_sprite_sheets("Items","Checkpoint",64,64,False)
        sprites = sprites[sprite_sheet]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        
        if sprite_index == 25:
            self.activate_idle = True
            self.deactivate()

        if(sprite_index == 0):
            self.frame_count = 0
            
        self.update()
        
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
            
    def deactivate(self):
        self.activated = False
        
    def draw(self,window,offset_x):
        window.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))


def draw(window,background,bg_image,heart_image, coin_image,gem_image,arrow_group,fireball_group, player,objects,checkpoint,checkpoint_end,
        coins,gems,all_enemies_group,mercader,opt1,opt2,opt3,offset_x):
    for tile in background:
        window.blit(bg_image,tile)
        
    for obj in objects:
        obj.draw(window,offset_x)

    player.draw(window,offset_x)
    
    for enemy in all_enemies_group:
        enemy.draw(window,offset_x)
        
    for arrow in arrow_group:
        arrow.draw(window,offset_x)
        
    for fireball in fireball_group:
        fireball.draw(window,offset_x)
        
        
    
        
    mercader.draw(window,offset_x,opt1,opt2,opt3)
    
    checkpoint.draw(window,offset_x)

    checkpoint_end.draw(window,offset_x)

    draw_bar(player.lives.lives, player.coins, player.gems, heart_image, coin_image, gem_image)
    for coin in coins:
        coin.update()
        coin.draw(window, offset_x)

    for gem in gems:
        gem.update()
        gem.draw(window, offset_x)    
        
    pygame.display.update()
    
def handle_vertical_colission(player,objects,dy):
    collided_objects = []
    
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player,objects,dx,delta, window, partida, volume):
    player.move(dx,0, delta, window, partida, volume)
    player.update()

    collided_object = None

    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            collided_object = obj
            if player.y_vel > 0.5:
                player.wall_jump = True
                player.y_vel *= 0.5
                #player.jump_count=0
            if isinstance(obj, Block3) or isinstance(obj, Block4):
                player.get_hit(volume.sounds_volume) 
            break

    player.move(-dx,0, delta, window, partida, volume)
    player.update()

    
    return collided_object

def collide_boss(player,boss,dx, delta, window, partida, volume):
    if(pygame.sprite.collide_mask(player,boss)):
        if boss.is_alive:
            player.get_hit(volume.sounds_volume)
            player.move(-dx,0, delta, window, partida, volume)
    player.update()

def collide_arrow(player,arrows,objects,volume):
    for arrow in arrows:
        if pygame.sprite.collide_mask(player,arrow):
            arrow.kill()
            player.get_hit(volume.sounds_volume)
            
        for obj in objects:
            if pygame.sprite.collide_mask(arrow,obj):
                arrow.kill()
                arrow.update()
    player.update()
    
def collide_checkpoint(player,checkpoint,partida):
    if(pygame.sprite.collide_mask(player,checkpoint)):
        if not checkpoint.activate_idle:
            checkpoint.activated = True
        partida.checkpoint = 1     

def collide_end(player,checkpoint,partida,volume):
    if(pygame.sprite.collide_mask(player,checkpoint)):
        partida.lives = 3
        partida.coins = player.coins
        partida.gems = player.gems
        if partida.level != 2:
            partida.level += 1
            partida.checkpoint = 0
            show_loading_screen()
            play(window, partida, volume)    

def collide_explosion(explosions, player, volume):
    for expl in explosions:
        if  pygame.sprite.collide_mask(expl,player):
            player.get_hit(volume.sounds_volume)

def collide_fireball(fireball_group,enemies_group,objects):
    for fireball in fireball_group:
        for enemy in enemies_group:
            if pygame.sprite.collide_mask(fireball,enemy):
                enemy.take_damage()
                enemy.is_alive = False        
                
        for obj in objects:
            if pygame.sprite.collide_mask(fireball,obj):
                fireball.kill()
                fireball.update()
    
def handle_move(partida,volume,player,enemies_group,boss,checkpoint,checkpoint_end,objects,arrow_group,fireball_group,delta):
    vertical_collide = handle_vertical_colission(player,objects,player.y_vel)
    if player.lives.lives <= 0:
        player.die(window,partida,volume)
        return 
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    collide_left = collide(player,objects,-PLAYER_VEL * 2, delta, window, partida, volume)
    collide_right = collide(player,objects,PLAYER_VEL * 2, delta, window, partida, volume)
    
    collide_arrow(player,arrow_group,objects, volume)
    collide_boss(player,boss,PLAYER_VEL * 2, delta, window, partida, volume)
    collide_checkpoint(player,checkpoint, partida)
    collide_end(player,checkpoint_end, partida, volume)
    collide_fireball(fireball_group,enemies_group,objects)
    collide_explosion(boss.explosions, player, volume)
        
    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
        player.melee_active = False
        player.ranged_active = False

    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)
        player.melee_active = False
        player.ranged_active = False
    elif keys[pygame.K_p]:
        if player.x_vel == 0 and player.y_vel == 0:
            player.melee_attack()
            player.ranged_active = False

    elif keys[pygame.K_o]:
        if player.x_vel == 0 and player.y_vel == 0:
            player.ranged_attack()
            player.melee_active = False


    #to_check = [*vertical_collide]
def draw_bar(lives, coins, gems, heart_image, coin_image, gem_image):
    for i in range(lives):
        SCREEN.blit(heart_image, (50 + i * 35, 45))

    SCREEN.blit(coin_image, (50, 90)) 
    coins_text = resource_manager.get_font(20).render(str(coins), True, (0, 0, 0))
    SCREEN.blit(coins_text, (86, 93)) 

    SCREEN.blit(gem_image, (130, 90)) 
    gem_text = resource_manager.get_font(20).render(str(gems), True, (0, 0, 0))
    SCREEN.blit(gem_text, (166, 93)) 

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

def negociation3(player):
    text = "En proceso"    
    
def outOfWindow(group,offset_x):
    for element in group:
        if element.rect.right - offset_x < 0 or element.rect.left - offset_x > WIDTH:
                element.kill()


def show_loading_screen():
    window.fill("white")
    Load1 = pygame.image.load('assets/Progress_Bar/1.jpg')
    Load2 = pygame.image.load('assets/Progress_Bar/2.jpg')
    Load3 = pygame.image.load('assets/Progress_Bar/3.jpg')
    Load4 = pygame.image.load('assets/Progress_Bar/4.jpg')

    LOADING_TEXT = resource_manager.get_font(75).render("LOADING", True, "#b68f40")
    LOADING_RECT = LOADING_TEXT.get_rect(center=(515, 180))
    SCREEN.blit(LOADING_TEXT, LOADING_RECT)

    where = (120, 360)
    progress = 0
    while progress < 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        progress += 0.01
        if progress < 0.33:
            window.blit(Load1, where)
        elif progress < 0.66:
            window.blit(Load2, where)
        elif progress <= 0.99:
            window.blit(Load3, where)
        pygame.display.update()
        pygame.time.wait(40)
    window.blit(Load4, where)
    pygame.display.update()                
        


def death_menu(window, partida, volume):

    
    if not pygame.mixer.music.get_busy():
        mixer.music.load(resource_manager.get_sound("menu"))
        mixer.music.play(-1)
        
    while True:
        #SCREEN.blit(BG, (0, 0))
        SCREEN.fill("black")

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = resource_manager.get_font(75).render("GAME OVER", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(515, 120))

        REPLAY_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(515, 300), 
                            text_input="REPLAY", font=resource_manager.get_font(75), base_color="#d7fcd4", hovering_color="White")
        MENU_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(515, 475), 
                            text_input="MENU", font=resource_manager.get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [REPLAY_BUTTON, MENU_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if REPLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    show_loading_screen()
                    play(window, partida, volume)
                if MENU_BUTTON.checkForInput(MENU_MOUSE_POS):
                    main_menu(window, volume)

        pygame.display.update()


def options(window,volumen):
    dragging_thumb = False
    dragging_thumb2 = False
    while True:
        volume = volumen.music_volume
        sound = volumen.sounds_volume
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        VOLUME_TEXT = resource_manager.get_font(75).render("MUSIC", True, "#b68f40")
        VOLUME_RECT = VOLUME_TEXT.get_rect(center=(400, 200))
        SCREEN.blit(VOLUME_TEXT, VOLUME_RECT)

        scroll_bar_width =  20
        scroll_bar_height =  200
        scroll_bar = pygame.Surface((scroll_bar_width, scroll_bar_height))
        scroll_bar.fill((200,  200,  200))

        # Draw the thumb (the part you drag)
        thumb_height = int(volume * scroll_bar_height)
        thumb = pygame.Surface((scroll_bar_width, thumb_height))
        thumb.fill((100,  100,  100))  # Set a different color for the thumb
        scroll_bar.blit(thumb, (0, scroll_bar_height - thumb_height))

        scroll_bar_rect = scroll_bar.get_rect(center=(700,  200))
        window.blit(scroll_bar, scroll_bar_rect.topleft)


        SOUND_TEXT = resource_manager.get_font(75).render("SOUND", True, "#b68f40")
        SOUND_RECT = SOUND_TEXT.get_rect(center=(400, 450))
        SCREEN.blit(SOUND_TEXT, SOUND_RECT)

        scroll_bar_width2 =  20
        scroll_bar_height2 =  200
        scroll_bar2 = pygame.Surface((scroll_bar_width2, scroll_bar_height2))
        scroll_bar2.fill((200,  200,  200))

        # Draw the thumb (the part you drag)
        thumb_height2 = int(sound * scroll_bar_height2)
        thumb2 = pygame.Surface((scroll_bar_width2, thumb_height2))
        thumb2.fill((100,  100,  100))  # Set a different color for the thumb
        scroll_bar2.blit(thumb2, (0, scroll_bar_height2 - thumb_height2))

        scroll_bar_rect2 = scroll_bar2.get_rect(center=(700,  450))
        window.blit(scroll_bar2, scroll_bar_rect2.topleft)

        OPTIONS_BACK = Button(image=None, pos=(515, 700), 
                            text_input="BACK", font=resource_manager.get_font(75), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu(window, volumen)
                if scroll_bar_rect.collidepoint(event.pos):
                    # Start dragging the scroll bar thumb
                    dragging_thumb = True
                    last_mouse_y = event.pos[1]  
                if scroll_bar_rect2.collidepoint(event.pos):
                    # Start dragging the scroll bar thumb
                    dragging_thumb2 = True
                    last_mouse_y = event.pos[1]         
            elif event.type ==pygame.MOUSEBUTTONUP:
                dragging_thumb = False
                dragging_thumb2 = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging_thumb:
                    delta_y = event.pos[1] - last_mouse_y
                    volume += delta_y / scroll_bar_height
                    volume = max(min(volume,  1),  0)
                    volumen.music_volume = volume
                    last_mouse_y = event.pos[1]

                    mixer.music.set_volume(volume)

                    # Update the thumb position
                    thumb_height = int(volume * scroll_bar_height)
                    thumb = pygame.Surface((scroll_bar_width, thumb_height))
                    thumb.fill((100,  100,  100))
                    scroll_bar.fill((200,  200,  200))  # Reset the scroll bar background
                    scroll_bar.blit(thumb, (0, scroll_bar_height - thumb_height))    


                if dragging_thumb2:
                    delta_y = event.pos[1] - last_mouse_y
                    sound += delta_y / scroll_bar_height2
                    sound = max(min(sound,  1),  0)
                    volumen.sounds_volume = sound
                    last_mouse_y = event.pos[1]

                    # Update the thumb position
                    thumb_height2 = int(sound * scroll_bar_height2)
                    thumb2 = pygame.Surface((scroll_bar_width2, thumb_height2))
                    thumb2.fill((100,  100,  100))
                    scroll_bar2.fill((200,  200,  200))  # Reset the scroll bar background
                    scroll_bar2.blit(thumb2, (0, scroll_bar_height2 - thumb_height2))       


        pygame.display.update()


def play(window, partida, volume):


    mixer.music.load(resource_manager.get_sound("forest"))
    mixer.music.play(-1)

    clock = pygame.time.Clock()

    lives = Lives(partida.lives)
    
    all_enemies_group = pygame.sprite.Group()
    arrow_group = pygame.sprite.Group()
    fireball_group = pygame.sprite.Group()

    distance = 0
    checkpoint_activated = False 

    if partida.level == 1:
        background,bg_image, heart_image, coin_image, gem_image = resource_manager.get_background("Night.png")
        if partida.checkpoint == 1:
            distance = 7300
            checkpoint_activated = True
        
        player = Player(400,400,50,50, lives,fireball_group,partida.coins,partida.gems)
        rangedenemie1 = RangedEnemies(900-distance,500,100,100,4,arrow_group,"HalflingRanger")
        rangedenemie2 = RangedEnemies(6135-distance,230,100,100,4,arrow_group,"HalflingRanger")
        meleeEnemie1 = MeleeEnemie(800-distance,625,100,100,"HalflingRogue")
        meleeEnemie2 = MeleeEnemie(4375-distance,525,100,100,"HalflingRogue")
        meleeEnemie3 = MeleeEnemie(8320-distance,500,100,100,"HalflingRogue")
        mercader = Mercader(2700-distance, 625, 100, 100) 
        firstBoss = Boss(8500-distance,450,100,100)
        checkpoint = Checkpoint(7700-distance,375,50,50, checkpoint_activated)
        checkpoint_end = Checkpoint(8700-distance,575,50,50,True)

        all_enemies_group.add(meleeEnemie1)
        all_enemies_group.add(meleeEnemie2)
        all_enemies_group.add(meleeEnemie3)
        all_enemies_group.add(rangedenemie1)
        all_enemies_group.add(rangedenemie2)
        all_enemies_group.add(firstBoss)

    elif partida.level == 2:
        background,bg_image, heart_image, coin_image, gem_image = resource_manager.get_background("Cave2.png")

        ########## CONSTRUIR ENEMIGOS PARA NIVEL 2 (AHORA MISMO ESTA COMO NIVEL 1)#############

        if partida.checkpoint == 1:
            distance = 7300
            checkpoint_activated = True
        
        player = Player(400,400,50,50, lives,fireball_group,partida.coins,partida.gems)
        rangedenemie1 = RangedEnemies(900-distance,500,100,100,4,arrow_group,"HalflingRanger")
        rangedenemie2 = RangedEnemies(6135-distance,230,100,100,4,arrow_group,"HalflingRanger")
        meleeEnemie1 = MeleeEnemie(800-distance,625,100,100,"HalflingRogue")
        meleeEnemie2 = MeleeEnemie(4375-distance,525,100,100,"HalflingRogue")
        meleeEnemie3 = MeleeEnemie(8320-distance,500,100,100,"HalflingRogue")
        mercader = Mercader(2700-distance, 625, 100, 100) 
        firstBoss = Boss(8500-distance,450,100,100)
        checkpoint = Checkpoint(7700-distance,375,50,50, checkpoint_activated)
        checkpoint_end = Checkpoint(8700-distance,575,50,50,True)

        all_enemies_group.add(meleeEnemie1)
        all_enemies_group.add(meleeEnemie2)
        all_enemies_group.add(meleeEnemie3)
        all_enemies_group.add(rangedenemie1)
        all_enemies_group.add(rangedenemie2)
        all_enemies_group.add(firstBoss)

    
<<<<<<< HEAD
    player = Player(400,400,50,50, lives,fireball_group,partida.coins,partida.gems)
    rangedenemie1 = RangedEnemies(900-distance,500,100,100,4,arrow_group,"HalflingRanger")
    rangedenemie2 = RangedEnemies(6135-distance,230,100,100,4,arrow_group,"HalflingRanger")
    meleeEnemie1 = MeleeEnemie(800-distance,625,100,100,"HalflingRogue")
    meleeEnemie2 = MeleeEnemie(4375-distance,500,100,100,"HalflingRogue")
    meleeEnemie3 = MeleeEnemie(8320-distance,500,100,100,"HalflingRogue")
    mercader = Mercader(2700-distance, 625, 100, 100) 
    firstBoss = Boss(8500-distance,450,100,100)
    firstBoss = SecondBoss(8500-distance,450,100,100)
    checkpoint = Checkpoint(7700-distance,375,50,50, checkpoint_activated)
    checkpoint_end = Checkpoint(8700-distance,575,50,50,True)

    all_enemies_group.add(meleeEnemie1)
    all_enemies_group.add(meleeEnemie2)
    all_enemies_group.add(meleeEnemie3)
    all_enemies_group.add(rangedenemie1)
    all_enemies_group.add(rangedenemie2)
    all_enemies_group.add(firstBoss)
=======
>>>>>>> main

    block_size = 96
    block2_size = 64 
    block3_size = 64 
    block4_size = 32 

    plat_size = 100

    offset_x = 0
    scroll_area_width = 400
    
    run = True
    if partida.level == 1:
   ############################################# NIVEL 1 - BOSQUE ############################################################### 
        floor = [Block(i*block_size-distance,HEIGHT - block_size ,block_size)for i in range(-WIDTH // block_size,WIDTH*2 // block_size)]
        floor2 = [Block(i*block_size-distance,HEIGHT - block_size ,block_size)for i in range(5 + WIDTH*2 // block_size,WIDTH*4 // block_size)]
        floor3 = [Block(i*block_size + 7200-distance,HEIGHT - block_size ,block_size)for i in range(0,30)]

        column = [Block(block_size + 3000-distance,HEIGHT - block_size - (100*i),block_size)for i in range(1,7)]
        column2 = [Block(block_size + 7100-distance,HEIGHT - block_size - (100*i),block_size)for i in range(1,5)]
        column3 = [Block(block_size + 7200-distance,HEIGHT - block_size - (100*i),block_size)for i in range(1,5)]
        column4 = [Block(block_size + 7300-distance,HEIGHT - block_size - (100*i),block_size)for i in range(1,4)]
        column5 = [Block(block_size + 7400-distance,HEIGHT - block_size - (100*i),block_size)for i in range(1,4)]
        column6 = [Block(block_size + 7500-distance,HEIGHT - block_size - (100*i),block_size)for i in range(1,3)]
        column7 = [Block(block_size + 7600-distance,HEIGHT - block_size - (100*i),block_size)for i in range(1,3)]
        column8 = [Block(block_size + 7700-distance,HEIGHT - block_size - (100*i),block_size)for i in range(1,2)]
        column9 = [Block(block_size + 7800-distance,HEIGHT - block_size - (100*i),block_size)for i in range(1,2)]
        column10 = [Block(block_size + 9000-distance,HEIGHT - block_size - (100*i),block_size)for i in range(1,7)]
            

        plat1 = [Platform(i*block_size + 800-distance,HEIGHT - block_size - 125, plat_size)for i in range(0,4)]
        plat2 = [Platform(i*block_size + 1300-distance,HEIGHT - block_size - 300, plat_size)for i in range(0,2)]
        plat3 = [Platform(4*i*block_size + 1600-distance,HEIGHT - block_size - 500, plat_size)for i in range(0,2)]
        plat4 = [Platform(2*i*block_size + 700-distance,HEIGHT - block_size - 450, plat_size)for i in range(0,3)]
        plat5 = [Platform(i*block_size + 400-distance,HEIGHT - block_size - 625, plat_size)for i in range(0,1)]
        plat6 = [Platform(i*block_size + 2050-distance,HEIGHT - block_size - 150, plat_size)for i in range(0,2)]

        plat7 = [Platform(i*block_size + 2500-distance,HEIGHT - block_size - 150 - (300*i), plat_size)for i in range(0,2)]
        plat8 = [Platform(i*block_size + 2825-distance,HEIGHT - block_size - 250 - (300*i), plat_size)for i in range(0,2)]

        plat9 = [Platform(3*i*block_size + 3400-distance,HEIGHT - block_size - 300 - (200*i), plat_size)for i in range(0,2)]

        plat10 = [Platform(i*block_size + 4000-distance,HEIGHT - block_size - 600, plat_size)for i in range(0,1)]

        plat11 = [Platform(i*block_size + 4100-distance,HEIGHT - block_size - 100, plat_size)for i in range(0,4)]

        plat12 = [Platform(i*block_size + 4200-distance,HEIGHT - block_size - 400, plat_size)for i in range(0,2)]

        plat13 = [Platform(i*block_size + 4700-distance,HEIGHT - block_size - 250, plat_size)for i in range(0,2)]

        plat14 = [Platform(3*i*block_size + 5050-distance,HEIGHT - block_size - (400 * i) - 100, plat_size)for i in range(0,3)]

        plat15 = [Platform(4*i*block_size + 5300-distance,HEIGHT - block_size - (200 * i), plat_size)for i in range(0,5)]
        plat16 = [Platform(4*i*block_size + 5400-distance,HEIGHT - block_size - (200 * i), plat_size)for i in range(0,5)]

        plat17 = [Platform(i*block_size + 6800-distance,HEIGHT - block_size - 400, plat_size)for i in range(0,2)]

        plat18 = [Platform(i*block_size + 6150-distance,HEIGHT - block_size, plat_size)for i in range(0,1)]
        plat19 = [Platform(i*block_size + 6600-distance,HEIGHT - block_size ,plat_size)for i in range(0,1)]


        plat20 = [Platform(3*i*block_size + 5500-distance,HEIGHT - block_size - 800 + (300 * i), plat_size)for i in range(0,2)]

        plat21 = [Platform(i*block_size + 5050-distance,HEIGHT - block_size - 425, plat_size)for i in range(0,1)]

        objects = [*floor,*floor2,*floor3,*column,*column2,*column3,*column4,*column5,*column6,*column7,*column8,*column9,*column10 ,*plat1,*plat2,*plat3,*plat4,*plat5,*plat6,*plat7,*plat8,*plat9,*plat10,*plat11,*plat12,*plat13,*plat14,*plat15,*plat16,*plat17,*plat18,*plat19,*plat20,*plat21]

########################################### FIN NIVEL 1 #############################################################################################

    elif partida.level == 2:
 ############################################# NIVEL 2 - CUEVA ###############################################################   
        floor = [Block2(i*block2_size-distance,HEIGHT - block2_size ,block2_size)for i in range(-WIDTH // block_size,WIDTH*14 // block_size)]

        column = [Block2(block2_size + 600-distance,HEIGHT - block2_size - (64*i),block2_size)for i in range(3,13)]
        column2 = [Block2(block2_size + 1600-distance,HEIGHT - block2_size - (64*i),block2_size)for i in range(1,10)]
        column3 = [Block2(block2_size + 2240-distance,HEIGHT - block2_size -  576 - (64*i),block2_size)for i in range(1,6)]
        column4 = [Block2(block2_size + 1856-distance,HEIGHT - block2_size -  384 +  (64*i),block2_size)for i in range(1,4)]
        column5 = [Block2(block2_size + 3840-distance,HEIGHT - block2_size -  832 +  (64*i),block2_size)for i in range(0,11)]
        column6 = [Block2(block2_size + 4800-distance,HEIGHT - block2_size -  832 +  (64*i),block2_size)for i in range(3,15)]
        column7 = [Block2(block2_size + 7804-distance,HEIGHT - block2_size -  832 +  (64*i),block2_size)for i in range(0,12)]
        
        spike1 = [Block3(i*block3_size-distance,HEIGHT - block3_size - 128, block3_size)for i in range(1,10)]

        mini_spike1 = [Block4(i*block4_size-distance,HEIGHT - block4_size - 192, block4_size)for i in range(1,10)]

        plat1 = [Block2(i*block2_size + 664-distance,HEIGHT - block2_size - 320, block2_size)for i in range(1,10)]
        plat2 = [Block2(i*block2_size + 960-distance,HEIGHT - block2_size - 576, block2_size)for i in range(1,15)]
        plat5 = [Block2(i*block2_size + 960-distance,HEIGHT - block2_size - 576, block2_size)for i in range(17,30)]
        plat3 = [Block2(i*block2_size + 1344-distance,HEIGHT - block2_size - 196, block2_size)for i in range(1,7)]
        plat4 = [Block2(i*block2_size + 832-distance,HEIGHT - block2_size - 512, block2_size)for i in range(1,17)]

        plat6 = [Block2(i*block2_size + 1920-distance,HEIGHT - block2_size - 384 + (64*i), block2_size)for i in range(1,7)]
        plat7 = [Block2(i*block2_size + 1856-distance,HEIGHT - block2_size - 384 + (64*i), block2_size)for i in range(1,7)]
        plat8 = [Block2(i*block2_size + 1856-distance,HEIGHT - block2_size - 128, block2_size)for i in range(1,5)]
        
        plat9 = [Block2(i*block2_size + 2880-distance,HEIGHT - block2_size - 320, block2_size)for i in range(1,14)]
        plat10 = [Block2(i*block2_size + 2944-distance,HEIGHT - block2_size - 320 - (64*i), block2_size)for i in range(0,7)]
        plat11 = [Block2(i*block2_size + 3008-distance,HEIGHT - block2_size - 128, block2_size)for i in range(0,7)]
        plat12 = [Block2(i*block2_size + 3008-distance,HEIGHT - block2_size - 192, block2_size)for i in range(0,7)]
        plat13 = [Block2(i*block2_size + 3008-distance,HEIGHT - block2_size - 256, block2_size)for i in range(0,7)]

        plat14 = [Block2(block2_size + 3328-distance,HEIGHT - block2_size - 256 + (64*i), block2_size)for i in range(0,2)]
        plat14 = [Block2(block2_size + 3392-distance,HEIGHT - block2_size - 256 + (64*i), block2_size)for i in range(0,2)]
        plat15 = [Block2(block2_size + 3584-distance,HEIGHT - block2_size - 64 - (64*i), block2_size)for i in range(0,2)]
        plat16 = [Block2(block2_size + 3648-distance,HEIGHT - block2_size - 64 - (64*i), block2_size)for i in range(0,2)]

        plat17 = [Block2(i*block2_size + 3904-distance,HEIGHT - block2_size - 192 , block2_size)for i in range(1,6)]
        plat18 = [Block2(i*block2_size + 3904-distance,HEIGHT - block2_size - 192 , block2_size)for i in range(10,15)]

        plat19 = [Block2(i*block2_size + 3904-distance,HEIGHT - block2_size - 448 , block2_size)for i in range(1,5)]
        plat20 = [Block2(i*block2_size + 3904-distance,HEIGHT - block2_size - 448 , block2_size)for i in range(11,15)]
        plat25 = [Block2(i*block2_size + 3904-distance,HEIGHT - block2_size - 512 , block2_size)for i in range(11,15)]
        plat26 = [Block2(i*block2_size + 3904-distance,HEIGHT - block2_size - 576 , block2_size)for i in range(11,15)]

        plat21 = [Block2(i*block2_size + 3904-distance,HEIGHT - block2_size - 640 , block2_size)for i in range(1,4)]
        plat22 = [Block2(i*block2_size + 3904-distance,HEIGHT - block2_size - 640 , block2_size)for i in range(11,15)]

        plat23 = [Block2(i*block2_size + 3904-distance,HEIGHT - block2_size - 320 , block2_size)for i in range(7,9)]
        plat24 = [Block2(i*block2_size + 3904-distance,HEIGHT - block2_size - 576 , block2_size)for i in range(7,9)]

        plat27 = [Block2(i*block2_size + 4992-distance,HEIGHT - block2_size - 384 + (64*i) , block2_size)for i in range(1,4)]
        plat31 = [Block2(i*block2_size + 5312-distance,HEIGHT - block2_size - 256 + (64*i) , block2_size)for i in range(1,4)]
        plat32 = [Block2(i*block2_size + 5632-distance,HEIGHT - block2_size - 384 + (64*i) , block2_size)for i in range(1,4)]
        
        plat28 = [Block2(i*block2_size + 4992-distance,HEIGHT - block2_size - 512 - (64*i) , block2_size)for i in range(1,4)]
        plat29 = [Block2(i*block2_size + 5312-distance,HEIGHT - block2_size - 384 - (64*i) , block2_size)for i in range(1,4)]
        plat30 = [Block2(i*block2_size + 5694-distance,HEIGHT - block2_size - 512 - (64*i) , block2_size)for i in range(1,4)]

        plat33 = [Block2(i*block2_size + 6016-distance,HEIGHT - block2_size - 832 + (64*i) , block2_size)for i in range(1,6)]
        plat34 = [Block2(i*block2_size + 6016-distance,HEIGHT - block2_size -  (64*i) , block2_size)for i in range(1,6)]

        plat35 = [Block2(i*block2_size + 6400-distance,HEIGHT - block2_size -  320 , block2_size)for i in range(0,21)]
        plat36 = [Block2(i*block2_size + 6400-distance,HEIGHT - block2_size -  512 , block2_size)for i in range(0,23)]

        plat39 = [Block2(i*block2_size + 6400-distance,HEIGHT - block2_size -  128 , block2_size)for i in range(0,23)]
        

        plat37 = [Block2(i*block2_size + 6400-distance,HEIGHT - block2_size -  384 , block2_size)for i in range(5,7)]
        plat38 = [Block2(i*block2_size + 6400-distance,HEIGHT - block2_size -  448 , block2_size)for i in range(14,16)]

        
        
        
        objects = [*mini_spike1,*spike1,*floor,*column,*column2,*column3,*column4,*column5,*column6,*column7,*plat1,*plat2,*plat3,*plat4,*plat5,*plat6,*plat7,*plat8,*plat9,*plat10,*plat11,*plat12,*plat13,*plat14,*plat15,*plat16,*plat17,*plat18,*plat19,*plat20,*plat21,*plat22,*plat23,*plat24,*plat25,*plat26,*plat27,*plat28,*plat29,*plat30,*plat31,*plat32,*plat33,*plat34,*plat35,*plat36,*plat37,*plat38,*plat39]

    


    coin_size = 40  
    num_coins = 10
    coins = [
        Coin(random.randint(0, WIDTH - coin_size)-distance, random.randint(100, 650), coin_size)
        for _ in range(num_coins)
    ]
    coins = pygame.sprite.Group(coins)  

    gem_size = 40  
    num_gems = 2
    gems = [
        Gem(random.randint(0, WIDTH - gem_size)-distance, random.randint(100, 650), gem_size)
        for _ in range(num_gems)
    ]
    gems = pygame.sprite.Group(gems)  



    while run: 

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        option1_mercader = Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-50), 
                        text_input="10 Coins -> 1 Life", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")
        option2_mercader = Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-30), 
                            text_input="15 Coins -> 2 Lifes", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")
        option3_mercader = Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-10), 
                            text_input="1 Gem -> New aspect", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")
        
        delta_time = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump(volume.sounds_volume)  
                if event.key == pygame.K_n and mercader.close:
                    mercader.negociating = True 
                    negociate_sound = mixer.Sound(resource_manager.get_sound("negociate"))
                    negociate_sound.play()
                    negociate_sound.set_volume(volume.sounds_volume)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if option1_mercader.checkForInput(MENU_MOUSE_POS):
                    negociation1(player, volume.sounds_volume)
                if option2_mercader.checkForInput(MENU_MOUSE_POS):
                    negociation2(player, volume.sounds_volume)
                if option3_mercader.checkForInput(MENU_MOUSE_POS):
                    negociation3(player, volume.sounds_volume)  
                    
        player.loop(delta_time, all_enemies_group, window, partida, volume)
        
        for enemy in all_enemies_group:
            enemy.loop(player,volume)
            
        mercader.loop(player,offset_x)
        checkpoint.loop()
        checkpoint_end.loop()
        
        handle_move(partida,volume,player,all_enemies_group,firstBoss,checkpoint,checkpoint_end,objects,arrow_group,fireball_group,delta_time)
        draw(window,background,bg_image,heart_image, coin_image, gem_image,arrow_group,fireball_group,player,objects,checkpoint,checkpoint_end,
             coins,gems,all_enemies_group,mercader,option1_mercader,option2_mercader,option3_mercader,offset_x)

            
        if pygame.sprite.spritecollideany(player, coins): 
            for _ in pygame.sprite.spritecollide(player, coins, True):
                player.collect_coin(volume.sounds_volume) 

        if pygame.sprite.spritecollideany(player, gems): 
            for _ in pygame.sprite.spritecollide(player, gems, True):
                player.collect_gem(volume.sounds_volume)
                
        outOfWindow(fireball_group,offset_x)
        outOfWindow(arrow_group,offset_x)

        if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
                offset_x += player.x_vel / FPS 
    
    pygame.quit()
    quit()


def main_menu(window, volume):

    if not pygame.mixer.music.get_busy():
        mixer.music.set_volume(volume.music_volume)
        mixer.music.load(resource_manager.get_sound("menu"))
        mixer.music.play(-1)
        
    while True:
        #SCREEN.blit(BG, (0, 0))
        SCREEN.fill("black")

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = resource_manager.get_font(75).render("DRAGON KILL", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(515, 120))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(515, 300), 
                            text_input="PLAY", font=resource_manager.get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(515, 475), 
                            text_input="OPTIONS", font=resource_manager.get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(515, 650), 
                            text_input="QUIT", font=resource_manager.get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    show_loading_screen()
                    partida = Partida()
                    play(window,partida,volume)
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options(window,volume)
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()    

if __name__ == "__main__":
    main_menu(window, Volume())