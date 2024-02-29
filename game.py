import random
import time
import math
import pygame, sys, pickle

import resource_manager

from os import listdir
from os.path import isfile, join
from button import Button
from pygame import mixer


pygame.init()

SCREEN = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5
VOLUME =  0.5
TIMER = 0
LEVEL = 1
BAR_WIDTH = 300
BAR_HEIGHT = 20


window = pygame.display.set_mode((WIDTH,HEIGHT))

class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 1
    SPRITES = resource_manager.load_sprite_sheets("main", "",32,32,True)

    ANIMATION_DELAY = 8
    MELEE_COOLDOWN = 1.0
    MELEE_DURATION = 0.5

    def __init__(self,x,y,width,height, lives):
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.coins = 0
        self.lives = lives
        self._last_called = 0
        self.hit = False
        self.last_melee_time = 0
        self.melee_active = False
        self.melee_start_time = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
            
        self.animation_count = 0
        self.jump_count +=1

        if self.jump_count == 1:
            self.fall_count = 0

        jump_sound = mixer.Sound(resource_manager.get_sound("jump"))
        jump_sound.play()    

    def move(self,dx,dy):
        self.rect.x += dx
        self.rect.y += dy

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
            
    def loop(self,fps):
        self.y_vel += min(1,(self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel,self.y_vel)
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def get_hit(self):
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

    def hit_head(self):
        self.y_vel = 0
        
    def collect_coin(self):
        self.coins += 1 
        coin_sound = mixer.Sound(resource_manager.get_sound("coin"))
        coin_sound.play()

    def melee_attack(self):
        current_time = time.time()
        if current_time - self.last_melee_time < self.MELEE_COOLDOWN:
            return
        self.melee_active = True
        self.melee_start_time = current_time
        self.last_melee_time = current_time
    def update_melee_attack(self):
        if self.melee_active and (time.time() - self.melee_start_time > self.MELEE_DURATION):
            self.melee_active = False
    def get_melee_hitbox(self):
        melee_hitbox_size = (64, 64)
        offset_x = self.rect.width if self.direction == "right" else -melee_hitbox_size[0]
        melee_hitbox = pygame.Rect(self.rect.x + offset_x, self.rect.y, *melee_hitbox_size)
        #melee_hitbox.x -= self.x_vel
        return melee_hitbox
    def die(self):
        self.update_sprite()
        self.x_vel = 0
        self.y_vel = 0
        self.jump_count = 3
        death_sound = mixer.Sound(resource_manager.get_sound("death"))
        death_sound.play()

        #pantalla de game over
    def update_sprite(self):
        sprite_sheet = "idle"

        if self.lives.lives <= 0:
            sprite_sheet = "die"
        if self.y_vel < 0:
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
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        if sprite_sheet == "die": 
            sprite_index = len(sprites) - 1        
        self.sprite = sprites[sprite_index]
        self.animation_count +=1
        if sprite_sheet == "hit" and self.animation_count == 4:
            self.hit = False
        self.update_melee_attack()            
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self,window,offset_x):
        if self.melee_active:
            melee_hitbox = self.get_melee_hitbox()
            pygame.draw.rect(window, (0, 255, 0), melee_hitbox, 2)
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
    def __init__(self):
        self.observers = []
        self._lives = 3

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

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = resource_manager.get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        
class Platform(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size)
        block = resource_manager.get_platform(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)


class RangedEnemies(pygame.sprite.Sprite):
    SPRITES = resource_manager.load_sprite_sheets("Enemies","HalflingRanger",16,16,False)
    ANIMATION_DELAY = 4
    ARROW_FRAME = 25
    SHOOT_DISTANCE = 300
    SHOOT_HEIGHT_THRESHOLD = 20

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
        self.arrows = []
        self.orientation = "left"
        self.shoot = False

    def loop(self,player,offset_x):
        self.frame_count += 1

        if self.should_shoot(player):
            self.shoot = True
            if self.frame_count == self.ARROW_FRAME:
                self.shoot_arrow(offset_x)

        for arrow in self.arrows:
            arrow.update()

        self.update_sprite(player)
        
    def should_shoot(self, player):
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        return distance < self.SHOOT_DISTANCE and abs(dy) <= self.SHOOT_HEIGHT_THRESHOLD

    def shoot_arrow(self,offset_x):
        enemy_rect = self.rect.move(-offset_x,0)
        arrow = Arrow(self.rect,self.orientation)
        self.arrows.append(arrow)
        arrow_sound = mixer.Sound(resource_manager.get_sound("arrow"))
        arrow_sound.play()

    def update_sprite(self,player):
        
        if self.shoot:
            sprite_sheet = "shoot"
            self.shoot = False
            self.ANIMATION_DELAY = 4
        else: 
            sprite_sheet = "idle"
            self.ANIMATION_DELAY = 9
        
        sprites = self.SPRITES[sprite_sheet]
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
        for arrow in self.arrows:
            arrow.draw(window,offset_x)
        window.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))
        
class MeleeEnemie(pygame.sprite.Sprite):
    SPRITES = resource_manager.load_sprite_sheets("Enemies","HalflingRogue",16,16,False)
    ANIMATION_DELAY = 20
    ENEMY_VELOCITY = 2
    GRAVITY = 5
    
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
        self.x_vel = 0
        self.fall = False
        
    def loop(self,player,fps):
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
    
        self.rect.x += self.x_vel
            
        self.update_sprite(player)
        
    def update_sprite(self,player):
        sprites = self.SPRITES["HalflingRogueIdleSide"]
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
    ENEMY_VELOCITY = 2
    GRAVITY = 5
    
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
        self.x_vel = 0
        self.fall = False
        
    def loop(self,player,fps):
        self.frame_count += 1
        
        # dx = player.rect.x - self.rect.x
        # dy = player.rect.y - self.rect.y
        # distance = math.sqrt(dx**2 + dy**2)
        
        # max_velocity = 2
    
        # if distance < 400:
        #     ratio = min(1, distance / 300)
        #     self.x_vel = ratio * max_velocity * (dx / distance)
        # else:
        #     self.x_vel = 0
    
        # self.rect.x += self.x_vel
            
        self.update_sprite(player)
        
    def update_sprite(self,player):
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
        
    def draw(self,window,offset_x):
        window.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))
    

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
    


def draw(window,background,bg_image,heart_image, coin_image, player,objects,coins,enemie,meleeEnemie,firstBoss,mercader,opt1,opt2,opt3,offset_x):
    for tile in background:
        window.blit(bg_image,tile)
        
    for obj in objects:
        obj.draw(window,offset_x)

    player.draw(window,offset_x)
    enemie.draw(window,offset_x)
    meleeEnemie.draw(window,offset_x)
    mercader.draw(window,offset_x,opt1,opt2,opt3)
    firstBoss.draw(window,offset_x)

    draw_bar(player.lives.lives, player.coins, heart_image, coin_image)
    for coin in coins:
        coin.update()
        coin.draw(window, offset_x)
        
    pygame.display.update()
    
def handle_vertical_colission(player,objects,dy):
    collided_objects = []
    
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = player.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player,objects,dx):
    player.move(dx,0)
    player.update()

    collided_object = None

    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            collided_object = obj
            if player.y_vel > 0.5:
                player.wall_jump = True
                player.y_vel *= 0.5
                player.jump_count = 1
            break

    player.move(-dx,0)
    player.update()

    
    return collided_object

def collide_boss(player,boss,dx):
    if(pygame.sprite.collide_mask(player,boss)):
        player.get_hit()
        player.move(-dx,0)
    
    player.update()

def collide_arrow(player,arrows,objects):
    for arrow in arrows:
        if pygame.sprite.collide_mask(player,arrow):
            arrows.remove(arrow)
            player.get_hit()
            
        for obj in objects:
            if pygame.sprite.collide_mask(arrow,obj):
                arrows.remove(arrow)
    player.update()
    
def collide_enemie(player,enemie,objects):
    
    if(pygame.sprite.collide_mask(player,enemie)):
        player.get_hit()
            
    for obj in objects:
        if(pygame.sprite.collide_mask(enemie,obj)):
            enemie.fall = False
            return
            
    enemie.fall = True

    enemie.y += enemie.GRAVITY
    enemie.rect.y = enemie.y

    player.update()
    
def handle_move(player,arrows,enemie,boss,objects):
    vertical_collide = handle_vertical_colission(player,objects,player.y_vel)
    if player.lives.lives <= 0:
        player.die()
        return 
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    #por timer
    collide_left = collide(player,objects,-PLAYER_VEL * 2)
    collide_right = collide(player,objects,PLAYER_VEL * 2)
    collide_arrow(player,arrows,objects)
    collide_enemie(player,enemie,objects)
    collide_boss(player,boss,PLAYER_VEL * 2)
        
    if keys[pygame.K_p]:
        player.melee_attack()
    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    #to_check = [*vertical_collide]
def draw_bar(lives, coins, heart_image, coin_image):
    for i in range(lives):
        SCREEN.blit(heart_image, (50 + i * 35, 45))
    SCREEN.blit(coin_image, (50, 90)) 

    coins_text = resource_manager.get_font(20).render(str(coins), True, (0, 0, 0))
    SCREEN.blit(coins_text, (86, 93)) 


def negociation1(player):
    if player.coins >= 10 and player.lives.lives < 3 :
        player.coins -= 10
        player.lives.lives += 1
        deal_sound = mixer.Sound(resource_manager.get_sound("done_deal"))
        deal_sound.play()

def negociation2(player):
    if player.coins >= 15 and player.lives.lives < 2 :
        player.coins -= 15
        player.lives.lives += 2
        deal_sound = mixer.Sound(resource_manager.get_sound("done_deal"))
        deal_sound.play()

def negociation3(player):
    text = "En proceso"    


def options(window):
    try:
        with open('volumen.pkl', 'rb') as f:
            volume = pickle.load(f)
    except FileNotFoundError:
        volume =  0.5

    dragging_thumb = False
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        VOLUME_TEXT = resource_manager.get_font(75).render("VOLUME", True, "#b68f40")
        VOLUME_RECT = VOLUME_TEXT.get_rect(center=(400, 300))
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

        scroll_bar_rect = scroll_bar.get_rect(center=(700,  300))
        window.blit(scroll_bar, scroll_bar_rect.topleft)

        OPTIONS_BACK = Button(image=None, pos=(515, 550), 
                            text_input="BACK", font=resource_manager.get_font(75), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu(window)
                if scroll_bar_rect.collidepoint(event.pos):
                    # Start dragging the scroll bar thumb
                    dragging_thumb = True
                    last_mouse_y = event.pos[1]    
            elif event.type ==pygame.MOUSEBUTTONUP:
                dragging_thumb = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging_thumb:
                    # Calculate the new volume based on the mouse movement
                    delta_y = event.pos[1] - last_mouse_y
                    volume += delta_y / scroll_bar_height
                    volume = max(min(volume,  1),  0)  # Clamp between  0 and  1
                    with open('volumen.pkl', 'wb') as f:
                        pickle.dump(volume, f)
                    last_mouse_y = event.pos[1]

                    mixer.music.set_volume(volume)

                    # Update the thumb position
                    thumb_height = int(volume * scroll_bar_height)
                    thumb = pygame.Surface((scroll_bar_width, thumb_height))
                    thumb.fill((100,  100,  100))
                    scroll_bar.fill((200,  200,  200))  # Reset the scroll bar background
                    scroll_bar.blit(thumb, (0, scroll_bar_height - thumb_height))        

        pygame.display.update()


def play(window):

    mixer.music.load(resource_manager.get_sound("forest"))
    mixer.music.play(-1)

    clock = pygame.time.Clock()
    background,bg_image, heart_image, coin_image = resource_manager.get_background("Night.png")

    lives = Lives()

    player = Player(400,400,50,50, lives)
    enemie = RangedEnemies(900,500,100,100)
    meleeEnemie = MeleeEnemie(0,625,100,100)
    mercader = Mercader(2700, 625, 100, 100) 
    firstBoss = Boss(500,450,100,100)

    block_size = 96
    plat_size = 100

    offset_x = 0
    scroll_area_width = 200

    run = True
    
    floor = [Block(i*block_size,HEIGHT - block_size ,block_size)for i in range(-WIDTH // block_size,WIDTH*2 // block_size)]
    floor2 = [Block(i*block_size,HEIGHT - block_size ,block_size)for i in range(5 + WIDTH*2 // block_size,WIDTH*4 // block_size)]

    column = [Block(block_size + 3000,HEIGHT - block_size - (100*i),block_size)for i in range(1,7)]

    plat1 = [Platform(i*block_size + 800,HEIGHT - block_size - 125, plat_size)for i in range(0,4)]
    plat2 = [Platform(i*block_size + 1300,HEIGHT - block_size - 300, plat_size)for i in range(0,2)]
    plat3 = [Platform(4*i*block_size + 1600,HEIGHT - block_size - 500, plat_size)for i in range(0,2)]
    plat4 = [Platform(2*i*block_size + 700,HEIGHT - block_size - 450, plat_size)for i in range(0,3)]
    plat5 = [Platform(i*block_size + 400,HEIGHT - block_size - 625, plat_size)for i in range(0,1)]
    plat6 = [Platform(i*block_size + 2050,HEIGHT - block_size - 150, plat_size)for i in range(0,2)]

    plat7 = [Platform(i*block_size + 2500,HEIGHT - block_size - 150 - (300*i), plat_size)for i in range(0,2)]
    plat8 = [Platform(i*block_size + 2825,HEIGHT - block_size - 250 - (300*i), plat_size)for i in range(0,2)]

    plat9 = [Platform(3*i*block_size + 3400,HEIGHT - block_size - 300 - (200*i), plat_size)for i in range(0,2)]
    

    coin_size = 40
    num_coins = 10
    coins = [
        Coin(random.randint(0, WIDTH - coin_size), random.randint(100, 650), coin_size)
        for _ in range(num_coins)
    ]
    coins = pygame.sprite.Group(coins)

    objects = [*floor,*floor2,*column,*plat1,*plat2,*plat3,*plat4,*plat5,*plat6,*plat7,*plat8,*plat9]

    while run:

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        option1_mercader = Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-50), 
                        text_input="10 Coins -> 1 Life", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")
        option2_mercader = Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-30), 
                            text_input="15 Coins -> 2 Lifes", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")
        option3_mercader = Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-10), 
                            text_input="1 Gem -> New aspect", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")

        clock.tick(FPS)
        #timer
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()  
                if event.key == pygame.K_n and mercader.close:
                    mercader.negociating = True 
                    negociate_sound = mixer.Sound(resource_manager.get_sound("negociate"))
                    negociate_sound.play()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if option1_mercader.checkForInput(MENU_MOUSE_POS):
                    negociation1(player)
                if option2_mercader.checkForInput(MENU_MOUSE_POS):
                    negociation2(player)
                if option3_mercader.checkForInput(MENU_MOUSE_POS):
                    negociation3(player)  


        player.loop(FPS)
        #timer
        enemie.loop(player,offset_x)
        meleeEnemie.loop(player,FPS)
        mercader.loop(player,offset_x)
        firstBoss.loop(player,FPS)
        handle_move(player,enemie.arrows,meleeEnemie,firstBoss,objects)
        draw(window,background,bg_image,heart_image, coin_image, player,objects,coins,enemie,meleeEnemie,firstBoss,mercader,option1_mercader,option2_mercader,option3_mercader,offset_x)
        
        enemie.arrows = [arrow for arrow in enemie.arrows if not arrow.is_offscreen(offset_x)]

        if pygame.sprite.spritecollideany(player, coins): 
            for _ in pygame.sprite.spritecollide(player, coins, True):
                player.collect_coin() 

        if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
                offset_x += player.x_vel 
    
    pygame.quit()
    quit()


def main_menu(window):

    if not pygame.mixer.music.get_busy():
        try:
            with open('volumen.pkl', 'rb') as f:
                volume = pickle.load(f)
        except FileNotFoundError:
            volume =  0.5
        mixer.music.set_volume(volume)
        mixer.music.load(resource_manager.get_sound("menu"))
        mixer.music.play(-1)
        
    while True:
        #SCREEN.blit(BG, (0, 0))
        SCREEN.fill("black")

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = resource_manager.get_font(75).render("DRAGON KILL?", True, "#b68f40")
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
                    play(window)
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options(window)
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()    

if __name__ == "__main__":
    main_menu(window)