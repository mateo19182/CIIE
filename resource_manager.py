
import pygame, sys, pickle
from os import listdir
from os.path import isfile, join

WIDTH, HEIGHT = 1000, 800


def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

def get_background(name):
    image = pygame.image.load(join("assets","Background",name))
    _,_,width,height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width+1):
        for j in range(HEIGHT // height+1):
            pos = (i*width,j*height)
            tiles.append(pos)
    coin = pygame.image.load("assets/Collectibles/heart.png")
    heart = pygame.image.load("assets/Collectibles/coin_0.png")

    return tiles,image, coin, heart

def flip(sprites):
    return[pygame.transform.flip(sprite,True,False) for sprite in sprites]

def load_sprite_sheets(dir1,dir2,width,height,direction = False):
    path = join("assets",dir1,dir2)
    images = [f for f in listdir(path) if isfile(join(path,f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path,image)).convert_alpha()

        sprites = []

        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width,height),pygame.SRCALPHA,32)
            rect = pygame.Rect(i * width,0,width,height)
            surface.blit(sprite_sheet,(0,0),rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png","" + "_right")] = sprites
            all_sprites[image.replace(".png","" + "_left")] = flip(sprites)
        else:
            all_sprites[image.replace(".png","")] = sprites
        
    return all_sprites

def get_block(size):
    #path = join("assets","Terrain","Terrain.png")
    path = join("assets","LV1_Build.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(96,205,size,size)
    surface.blit(image,(0,0),rect)

    return pygame.transform.scale2x(surface)

def get_block2(size):
    #path = join("assets","Terrain","Terrain.png")
    path = join("assets","Cave_build.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(336,367,size,size)
    surface.blit(image,(0,0),rect)

    return pygame.transform.scale2x(surface)

def get_block3(size):
    #path = join("assets","Terrain","Terrain.png")
    path = join("assets","Spike.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(0,0,size,size)
    surface.blit(image,(0,0),rect)
    scaled = pygame.transform.scale2x(surface)
    return pygame.transform.scale2x(scaled)

def get_block4(size):
    #path = join("assets","Terrain","Terrain.png")
    path = join("assets","Spike.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(0,0,size,size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)

    



def get_platform(size):
    #path = join("assets","Terrain","Terrain.png")
    path = join("assets","LV1_Build.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(96,125,size,20)
    surface.blit(image,(0,0),rect)

    return pygame.transform.scale2x(surface)

def get_death():
    sprite_sheet = pygame.image.load('assets/Desappearing (96x96).png').convert_alpha()
    frame_width, frame_height = 96, 96 
    frames = []
    for i in range(7):
        frame_x = i * frame_width
        frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA).convert_alpha()
        frame_surface.blit(sprite_sheet, (0, 0), (frame_x, 0, frame_width, frame_height))
        frames.append(frame_surface)
    return frames

def get_sound(path):
    return join("assets", "Sounds", path + ".mp3")