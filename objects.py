import pygame
import resource_manager
from partida import WIDTH, HEIGHT
from os.path import isfile, join

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

class Block5(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = resource_manager.get_block5(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image) 

class Block6(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = resource_manager.get_block6(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image) 

class Spikeball(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = resource_manager.get_spikeball(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)  
        
class Platform(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size)
        block = resource_manager.get_platform(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)


