import pygame
import time
from pygame import mixer
import resource_manager
from partida import HEIGHT, WIDTH
from items import Fireball

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
        self.fallen = False
        self.death_menu = False
        self.out_of_range = False

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
            #if self.out_of_range:
                self.die(partida, volume, True)
            #else:
            #    self.out_of_range = True    

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

        if self.death_menu:
            partida.coins = self.coins
            partida.gems = self.gems
            #death_menu(window, partida, volume)

        self.y_vel += min(30, (self.fall_count * delta * self.GRAVITY))
        self.move(self.x_vel,self.y_vel, delta, window, partida, volume)
        self.fall_count += 1
        
        for projectile in self.projectiles:
            projectile.update()
        
        self.update_sprite()
        self.check_attack(enemies,volume)

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
        gem_sound = mixer.Sound(resource_manager.get_sound("gem"))
        gem_sound.play() 
        gem_sound.set_volume(volume)   

    def melee_attack(self,volume):
        current_time = time.time()
        if current_time - self.last_melee_time < self.MELEE_COOLDOWN:
            return
        self.melee_active = True
        self.melee_start_time = current_time
        self.last_melee_time = current_time
        self.animation_count = 0
        self.update_sprite()
        melee_sound = mixer.Sound(resource_manager.get_sound("melee"))
        melee_sound.play() 
        melee_sound.set_volume(volume) 

    def get_melee_hitbox(self):
        melee_hitbox_size = (12, 12)
        offset_x = self.rect.width if self.direction == "right" else -melee_hitbox_size[0]
        melee_hitbox = pygame.Rect(self.rect.x + offset_x, self.rect.y, *melee_hitbox_size)
        #melee_hitbox.x -= self.x_vel
        return melee_hitbox
    
    def ranged_attack(self,volume):
        current_time = time.time()
        if current_time - self.last_ranged_time >= self.MELEE_COOLDOWN:
            self.last_ranged_time = current_time
            self.animation_count = 0
            self.ranged_active = True
            self.update_sprite()
            
        if self.frame_count == 21:
            fire_sound = mixer.Sound(resource_manager.get_sound("fireball"))
            fire_sound.play() 
            fire_sound.set_volume(volume) 
            projectile = Fireball(self.rect, self.direction)
            self.projectiles.add(projectile)

    def die(self, partida, volume, fall):
        if not self.dead : 
            self.dead = True
            self.update_sprite()
            self.x_vel = 0
            self.y_vel = 0
            self.jump_count = 3
            death_sound = mixer.Sound(resource_manager.get_sound("death"))
            mixer.music.stop()
            death_sound.play()
            death_sound.set_volume(volume.sounds_volume)
            if fall:
                self.death_menu = True
                #death_menu(window, partida, volume)
        
    def check_attack(self, enemies,volume):
        if self.melee_active:
            hitbox = self.get_melee_hitbox()
            for enemy in enemies:
                if hitbox.colliderect(enemy.rect):
                    enemy.take_damage(volume)  
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
            if self.fallen and sprite_index == len(sprites) -1: 
                # Si ha pasado el tiempo de otra caida abrimos menu
                self.death_menu = True
            if self.fallen or sprite_index == len(sprites) -1: 
                # Si ya se cayó lo dejamos en el suelo
                sprite_index = len(sprites) - 1
                self.fallen = True
        self.sprite = sprites[sprite_index]
        self.animation_count +=1
        if sprite_sheet == "hit" and self.animation_count == 3:
            self.hit = False
            self.animation_count = 0
            
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
