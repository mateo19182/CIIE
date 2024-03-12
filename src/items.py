import pygame
import resource_manager
from partida import WIDTH, HEIGHT
from os.path import isfile, join

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

class Arrow(pygame.sprite.Sprite):
    def __init__(self, enemy_rect,orientation):
        super().__init__()
        self.image = pygame.image.load("assets/Items/Arrow/Arrow.png")
        self.image = pygame.transform.scale(self.image, (5 * 5, 1 * 5))  # Ajusta el tamaño aquí

        if(orientation == "right"):
            self.rect = self.image.get_rect(midleft=(enemy_rect.midright[0] - 70, enemy_rect.centery + 10))  # Posiciona la flecha al lado derecho y un poco más abajo del centro del enemigo
            self.velocity = (3, 0)  # Ajusta la velocidad de la flecha
        else:
            self.image = pygame.transform.flip(self.image,True,False)
            self.rect = self.image.get_rect(midleft=(enemy_rect.midright[0] - 90, enemy_rect.centery + 10))  # Posiciona la flecha al lado derecho y un poco más abajo del centro del enemigo
            self.velocity = (-3, 0)  # Ajusta la velocidad de la flecha
            
    def is_offscreen(self,offset_x):
        return self.rect.right - offset_x < 0 or self.rect.left - offset_x > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT
    
    def loop(self):
        self.update()
    
    def update(self):
        self.rect.move_ip(self.velocity)

    def draw(self, screen,offset_x):
        screen.blit(self.image, (self.rect.x - offset_x, self.rect.y))      

class Wrench(pygame.sprite.Sprite):
    def __init__(self, enemy_rect, orientation):
        super().__init__()
        self.original_image = pygame.image.load("assets/Items/Wrench/wrench.png")
        self.original_image = pygame.transform.scale(self.original_image, (5 * 5, 9 * 5))
        self.angle = 0 
        self.image = self.original_image.copy()

        if orientation == "right":
            self.rect = self.image.get_rect(midleft=(enemy_rect.midright[0] - 70, enemy_rect.centery + 10))
            self.velocity = (3, 0)
        else:
            self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect(midleft=(enemy_rect.midright[0] - 90, enemy_rect.centery + 10))
            self.velocity = (-3, 0)
            
    def loop(self):
        self.update()
                    
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
        self.image = pygame.transform.scale(self.image, (20 * 2, 13 * 2))
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

class CheckpointEnd(pygame.sprite.Sprite):
    ANIMATION_DELAY = 3
    
    def __init__(self,x,y,width,height):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_count = 0
        self.frame_count = 0
        self.rect = pygame.Rect(x,y,width,height)
        self.sprite = None
        
    def loop(self):
        self.frame_count += 1
        self.update_sprite()
        
    def update_sprite(self):

        sprites = resource_manager.load_sprite_sheets("Items","End",64,64,False)
        sprites = sprites["end"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

        if(sprite_index == 0):
            self.frame_count = 0
            
        self.update()
        
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        
    def draw(self,window,offset_x):
        window.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))

class Sign(pygame.sprite.Sprite):
    
    def __init__(self,x,y,width,height):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x,y,width,height)
        self.sprite = pygame.transform.scale(pygame.image.load(join("assets","Other","Sign.png")), (170,100))
        close = False

    def loop(self,player):
        dx = player.rect.x - self.x
        dy = player.rect.y - self.y

        if dx > -100 and dx < 200 and dy > -150 and dy < 100:
            self.close = True
        else:
            self.close = False

    def show_dialog(self,window,offset_x):
        dialog_surface = pygame.Surface((240, 20))
        dialog_surface.set_alpha(128)
        window.blit(dialog_surface, (self.rect.x - offset_x-30,self.rect.y-15))
        text = pygame.font.Font("assets/font.ttf", 15).render("Press R to read", True, "#b68f40")
        window.blit(text, (self.rect.x - offset_x-20,self.rect.y-10))        
        
    def draw(self,window,offset_x):
        window.blit(self.sprite,(self.rect.x - offset_x,self.rect.y))  
        if self.close:
            self.show_dialog(window,offset_x)        


def putCoins(x,y,num_coins,coins):
    for i in range(num_coins):
        coins.append(Coin(x + i * 50,y,40))

def putGems(x,y,num_gems,gems):
    for i in range(num_gems):
        gems.append(Gem(x + i * 50,y,40))
