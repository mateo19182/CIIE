import random
import time
import pygame, sys, pickle
from os import listdir
from os.path import isfile, join
from button import Button

pygame.init()

SCREEN = pygame.display.set_mode((1000, 800))
pygame.display.set_caption("Platformer")

BG = pygame.image.load("assets/Background.png")
YL = pygame.image.load("assets/Background/Yellow.png")
BG_COLOR = (255,255,255)
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5
VOLUME =  0.5
LEVEL = 1
BAR_WIDTH = 300
BAR_HEIGHT = 20

def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

window = pygame.display.set_mode((WIDTH,HEIGHT))

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

def load_new_sprite_sheets(dir1,width,height,direction = False):
    path = join("assets",dir1)
    images = [f for f in listdir(path) if isfile(join(path,f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path,image)).convert_alpha()

        sprites = []

        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width,height),pygame.SRCALPHA,32)
            rect = pygame.Rect(i * width,0,width,height)
            surface.blit(sprite_sheet,(0,0),rect)
            sprites.append((surface))

        if direction:
            all_sprites[image.replace(".png","" + "_right")] = sprites
            all_sprites[image.replace(".png","" + "_left")] = flip(sprites)
        else:
            all_sprites[image.replace(".png","")] = sprites
        
    return all_sprites

def get_block(size):
    path = join("assets","Terrain","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(96,0,size,size)
    surface.blit(image,(0,0),rect)

    return pygame.transform.scale2x(surface)


def get_platform(size):
    path = join("assets","Terrain","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(270,0,size,10)
    surface.blit(image,(0,0),rect)

    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 1
    #SPRITES = load_sprite_sheets("MainCharacters","MaskDude",32,32,True)
    SPRITES = load_sprite_sheets("main", "",32,32,True)

    ANIMATION_DELAY = 3
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

        self.last_melee_time = 0
        self.melee_active = False
        self.melee_start_time = 0


    def jump(self):
        self.y_vel = -self.GRAVITY * 8
            
        self.animation_count = 0
        self.jump_count +=1

        if self.jump_count == 1:
            self.fall_count = 0

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

    def hit_head(self):
        current_time = time.time()
        if current_time - self._last_called < 3:
            return
        self._last_called = current_time
        self.lives.lives -= 1
    def collect_coin(self):
        self.coins += 1  # Increment the coin counter


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
        melee_hitbox_size = (32, 32)
        offset_x = self.rect.width if self.direction == "right" else -melee_hitbox_size[0]
        melee_hitbox = pygame.Rect(self.rect.x + offset_x, self.rect.y, *melee_hitbox_size)
        #melee_hitbox.x -= self.x_vel

        return melee_hitbox



    def update_sprite(self):
        sprite_sheet = "idle"

        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel !=0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count +=1
        self.update_melee_attack()

        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)
        if self.lives.lives <= 0:
            self.die()

    def draw(self,window,offset_x):
        if self.melee_active:
            melee_hitbox = self.get_melee_hitbox()
            pygame.draw.rect(window, (0, 255, 0), melee_hitbox, 2)
        pygame.draw.rect(window, (0, 255, 0), self.rect, 2)
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
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        
class Platform(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size)
        block = get_platform(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)


def get_background(name):
    image = pygame.image.load(join("assets","Background",name))
    _,_,width,height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width+1):
        for j in range(HEIGHT // height+1):
            pos = (i*width,j*height)
            tiles.append(pos)

    return tiles,image

def draw(window,background,bg_image,heart_image, coin_image, player,objects,coins, offset_x):
    for tile in background:
        window.blit(bg_image,tile)
        
    for obj in objects:
        obj.draw(window,offset_x)

    player.draw(window,offset_x)
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
    
    
def handle_move(player,objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0

    collide_left = collide(player,objects,-PLAYER_VEL * 2)
    collide_right = collide(player,objects,PLAYER_VEL * 2)
    if keys[pygame.K_p]:
        player.melee_attack()
    if keys[pygame.K_a] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_d] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_colission(player,objects,player.y_vel)
    to_check = [*vertical_collide]
        
def draw_bar(lives, coins, heart_image, coin_image):
    for i in range(lives):
        SCREEN.blit(heart_image, (50 + i * 35, 45))
    SCREEN.blit(coin_image, (50, 90)) 

    coins_text = get_font(20).render(str(coins), True, (0, 0, 0))
    SCREEN.blit(coins_text, (86, 93)) 



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

        VOLUME_TEXT = get_font(75).render("VOLUME", True, "#b68f40")
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
                            text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

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

                    # Update the thumb position
                    thumb_height = int(volume * scroll_bar_height)
                    thumb = pygame.Surface((scroll_bar_width, thumb_height))
                    thumb.fill((100,  100,  100))
                    scroll_bar.fill((200,  200,  200))  # Reset the scroll bar background
                    scroll_bar.blit(thumb, (0, scroll_bar_height - thumb_height))        

        pygame.display.update()




def play(window):
    clock = pygame.time.Clock()
    background,bg_image = get_background("Blue.png")
    heart_image, coin_image = pygame.image.load("assets/Collectibles/heart.png"), pygame.image.load("assets/Collectibles/coin_0.png")

    lives = Lives()

    player = Player(400,400,50,50, lives)
    
    block_size = 96
    plat_size = 100

    offset_x = 0
    scroll_area_width = 200

    run = True
    
    floor = [Block(i*block_size,HEIGHT - block_size ,block_size)for i in range(-WIDTH // block_size,WIDTH*2 // block_size)]
    floor2 = [Block(i*block_size,HEIGHT - block_size ,block_size)for i in range(5 + WIDTH*2 // block_size,WIDTH*4 // block_size)]
    plat1 = [Platform(i*block_size + 800,HEIGHT - block_size - 125, plat_size)for i in range(0,4)]
    plat2 = [Platform(i*block_size + 1300,HEIGHT - block_size - 300, plat_size)for i in range(0,2)]
    plat3 = [Platform(4*i*block_size + 1600,HEIGHT - block_size - 500, plat_size)for i in range(0,2)]
    plat4 = [Platform(2*i*block_size + 700,HEIGHT - block_size - 450, plat_size)for i in range(0,3)]
    plat5 = [Platform(i*block_size + 400,HEIGHT - block_size - 625, plat_size)for i in range(0,1)]
    plat6 = [Platform(i*block_size + 2050,HEIGHT - block_size - 150, plat_size)for i in range(0,2)]

    coin_size = 40
    num_coins = 10
    coins = [
        Coin(random.randint(0, WIDTH - coin_size), random.randint(100, 650), coin_size)
        for _ in range(num_coins)
    ]
    coins = pygame.sprite.Group(coins)

    objects = [*floor,*floor2,*plat1,*plat2,*plat3,*plat4,*plat5,*plat6]

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()  

        player.loop(FPS)
        handle_move(player,objects)
        draw(window,background,bg_image,heart_image, coin_image, player,objects,coins,offset_x)

        if pygame.sprite.spritecollideany(player, coins): 
            for _ in pygame.sprite.spritecollide(player, coins, True):
                player.collect_coin()  # Increment the player's coin counter 

        if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
                offset_x += player.x_vel 
    
    pygame.quit()
    quit()


def main_menu(window):
    while True:
        #SCREEN.blit(BG, (0, 0))
        SCREEN.fill("black")

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(75).render("DRAGON KILL?", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(515, 120))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(515, 300), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(515, 475), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(515, 650), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

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