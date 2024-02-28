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

    return tiles,image