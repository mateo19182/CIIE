import pygame, sys
pygame.init()

from partida import Partida, Volume, WIDTH, HEIGHT
window = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Platformer")
import resource_manager
import build_levels
from NPCs import negociation1, negociation2, negociation3

from collisions import collide, collide_arrow, collide_boss, collide_checkpoint, handle_vertical_colission, collide_enemie, collide_explosion, collide_fireball

from button import Button
from pygame import mixer

FPS = 60
PLAYER_VEL = 5 * FPS
TIMER = 0
LEVEL = 1
BAR_WIDTH = 300
BAR_HEIGHT = 20


def draw(window,background,bg_image,heart_image, coin_image,gem_image,arrow_group,fireball_group, player,sign,objects,checkpoint,checkpoint_end,
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

    sign.draw(window,offset_x)    
        
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

def collide_end(player,checkpoint,partida,volume,boss):
    if(pygame.sprite.collide_mask(player,checkpoint)):
        if not (partida.level==3 and boss.is_alive):
            partida.lives = 3
            partida.coins = player.coins
            partida.gems = player.gems
            if partida.level != 3:
                partida.level += 1
                partida.checkpoint = 0
                if partida.level == 2:
                    text = "Level 2: Cave"
                    message = "Our warrior is closer to revenge, keep going!"
                else:
                    text = "Level 3: Dragon island"
                    message = "Last step, be ready to fight the dragon!"   
                show_loading_screen(text, message)
                play(window, partida, volume)    
            else:
                game_completed(window, partida,volume)    

def handle_move(partida,volume,player,enemies_group,boss,meleeEnemies_group,checkpoint,checkpoint_end,objects,arrow_group,fireball_group,delta):
    vertical_collide = handle_vertical_colission(player,objects,player.y_vel)
    if player.death_menu:
        if partida.coins >= 10 and partida.checkpoint==1:
            partida.coins -= 10
        death_menu(window, partida, volume)
        return
    if player.lives.lives <= 0:
        player.die(partida, volume, False)
        #death_menu(window, partida, volume)
        return 
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    collide_left = collide(player,objects,-PLAYER_VEL * 2, delta, window, partida, volume)
    collide_right = collide(player,objects,PLAYER_VEL * 2, delta, window, partida, volume)
    
    collide_arrow(player,arrow_group,objects, volume)
    collide_boss(player,boss,PLAYER_VEL * 2, delta, window, partida, volume)
    collide_checkpoint(player,checkpoint, partida,volume)
    collide_end(player,checkpoint_end, partida, volume,boss)
    collide_fireball(fireball_group,enemies_group,objects,volume)
    
    for meleeEnemie in meleeEnemies_group:
        collide_enemie(player,meleeEnemie,objects,volume)
    
    if partida.level==2:
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
            player.melee_attack(volume.sounds_volume)
            player.ranged_active = False

    elif keys[pygame.K_o]:
        if player.x_vel == 0 and player.y_vel == 0:
            player.ranged_attack(volume.sounds_volume)
            player.melee_active = False


    #to_check = [*vertical_collide]

def draw_bar(lives, coins, gems, heart_image, coin_image, gem_image):
    for i in range(lives):
        window.blit(heart_image, (50 + i * 35, 45))

    window.blit(coin_image, (50, 90)) 
    coins_text = resource_manager.get_font(20).render(str(coins), True, (0, 0, 0))
    window.blit(coins_text, (86, 93)) 

    window.blit(gem_image, (130, 90)) 
    gem_text = resource_manager.get_font(20).render(str(gems), True, (0, 0, 0))
    window.blit(gem_text, (166, 93)) 

def outOfWindow(group,offset_x):
    for element in group:
        if element.rect.right - offset_x < 0 or element.rect.left - offset_x > WIDTH:
                element.kill()

def show_loading_screen(level_text, message):
    window.fill("white")
    Load1 = pygame.image.load('assets/Progress_Bar/1.jpg')
    Load2 = pygame.image.load('assets/Progress_Bar/2.jpg')
    Load3 = pygame.image.load('assets/Progress_Bar/3.jpg')
    Load4 = pygame.image.load('assets/Progress_Bar/4.jpg')

    LOADING_TEXT = resource_manager.get_font(75).render("LOADING", True, "#b68f40")
    LOADING_RECT = LOADING_TEXT.get_rect(center=(515, 180))
    window.blit(LOADING_TEXT, LOADING_RECT)

    LEVEL_TEXT = resource_manager.get_font(40).render(level_text, True, "#b68f40")
    LEVEL_RECT = LEVEL_TEXT.get_rect(center=(515, 290))
    window.blit(LEVEL_TEXT, LEVEL_RECT)

    MESSAGE_TEXT = resource_manager.get_font(20).render(message, True, "#b68f40")
    MESSAGE_RECT = MESSAGE_TEXT.get_rect(center=(515, 650))
    window.blit(MESSAGE_TEXT,MESSAGE_RECT)

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
        pygame.time.wait(30)
    window.blit(Load4, where)
    pygame.display.update()   

def game_completed(window, partida, volume):

    
    if not pygame.mixer.music.get_busy():
        mixer.music.load(resource_manager.get_sound("menu"))
        mixer.music.play(-1)
        
    while True:
        window.fill("#333333")

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = resource_manager.get_font(60).render("CONGRATULATIONS!", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(515, 200))

        REPLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(300, 650), 
                            text_input="REPLAY", font=resource_manager.get_font(55), base_color="#d7fcd4", hovering_color="White")
        MENU_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(715, 650), 
                            text_input="MENU", font=resource_manager.get_font(55), base_color="#d7fcd4", hovering_color="White")

        window.blit(MENU_TEXT, MENU_RECT)

        text = """        You have helped our warrior defeat the dragon,
        giving him the vengaence he seaked. Now,
        he lives in peace. Great job! Feel free to 
        return anytime."""

        lines = text.splitlines()
        y = 350 # Posición inicial en el eje Y
        for line in lines:
            text_surface = resource_manager.get_font(20).render(line, True, "#B68F40")
            window.blit(text_surface, (-100, y))
            y += resource_manager.get_font(20).get_linesize() + 10

        #pygame.display.update()        

        for button in [REPLAY_BUTTON, MENU_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(window)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if REPLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    text = "Level 1: Forest"
                    message = "The adventure begins, the dragon waits" 
                    partida_new= Partida()    
                    show_loading_screen(text,message)
                    play(window, partida_new, volume)
                if MENU_BUTTON.checkForInput(MENU_MOUSE_POS):
                    main_menu(window, volume)

        pygame.display.update()                 

def death_menu(window, partida, volume):

    
    if not pygame.mixer.music.get_busy():
        mixer.music.load(resource_manager.get_sound("menu"))
        mixer.music.play(-1)
        
    while True:
        window.fill("#1a1a1a")

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = resource_manager.get_font(75).render("GAME OVER", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(515, 170))

        REPLAY_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(515, 400), 
                            text_input="REPLAY", font=resource_manager.get_font(75), base_color="#d7fcd4", hovering_color="White")
        MENU_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(515, 600), 
                            text_input="MENU", font=resource_manager.get_font(75), base_color="#d7fcd4", hovering_color="White")

        window.blit(MENU_TEXT, MENU_RECT)

        for button in [REPLAY_BUTTON, MENU_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(window)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if REPLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    if partida.level == 1:
                        text = "Level 1: Forest"
                        message = "The adventure begins, the dragon waits"
                    elif partida.level == 2:
                        text = "Level 2: Cave"
                        message = "Our warrior is closer to revenge, keep going!"
                    else:
                        text = "Level 3: Dragon island"
                        message = "Last step, be ready to fight the dragon!"  
                    show_loading_screen(text,message)
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

        window.fill("white")

        VOLUME_TEXT = resource_manager.get_font(75).render("MUSIC", True, "#b68f40")
        VOLUME_RECT = VOLUME_TEXT.get_rect(center=(400, 200))
        window.blit(VOLUME_TEXT, VOLUME_RECT)

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
        window.blit(SOUND_TEXT, SOUND_RECT)

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
        OPTIONS_BACK.update(window)

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

    offset_x = 0
    scroll_area_width = 400
    
    run = True
    read = False
    pause = False
    controls = False
    sound_options = False

    mercader, player, sign, all_enemies_group, arrow_group, checkpoint, checkpoint_end, firstBoss, meleeEnemies_group, objects, fireball_group, background, bg_image, heart_image, coin_image, gem_image, coins, gems, option1_mercader, option2_mercader, option3_mercader, text = build_levels.build_level(partida)
    
    while run: 

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        delta_time = clock.tick(FPS) / 1000.0

        BACK_BUTTON = None
        OPTIONS_BACK = None
        scroll_bar_rect = None
        scroll_bar_rect2 = None

        if read:
            distance=0
            surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)
            surface.fill((128, 128, 128))
            surface.set_alpha(20) 
            window.blit(surface, (0, 0))
            if partida.level==2:
                FIRE_TEXT = resource_manager.get_font(25).render("New attack! Fireball -> Key O", True, (100,0,100))
                FIRE_RECT = FIRE_TEXT.get_rect(center=(500, 600))
                window.blit(FIRE_TEXT, FIRE_RECT)
                distance=30

            PAUSE_TEXT = resource_manager.get_font(35).render("The warrior and the Dragon", True, (100,0,0))
            PAUSE_RECT = PAUSE_TEXT.get_rect(center=(500, 150-distance))
            window.blit(PAUSE_TEXT, PAUSE_RECT)

            lines = text.splitlines()
            y = 270-distance # Posición inicial en el eje Y
            for line in lines:
                text_surface = resource_manager.get_font(20).render(line, True, (0,0,0)) #"#B68F40"
                window.blit(text_surface, (-100, y))
                y += resource_manager.get_font(20).get_linesize() + 10
            
            RESUME_BUTTON = Button(image=None, pos=(500, 680+distance), 
                                text_input="RESUME", font=resource_manager.get_font(50), base_color="Black", hovering_color="Green")
            RESUME_BUTTON.changeColor(MENU_MOUSE_POS)
            RESUME_BUTTON.update(window) 

            
            pygame.display.update()

        if pause:
            surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA, 32)
            surface.fill((128, 128, 128))
            surface.set_alpha(20) 
            window.blit(surface, (0, 0))   

            PAUSE_TEXT = resource_manager.get_font(75).render("PAUSE MENU", True, "#b68f40")
            PAUSE_RECT = PAUSE_TEXT.get_rect(center=(500, 100))
            window.blit(PAUSE_TEXT, PAUSE_RECT)

            if controls:
                JUMP_TEXT = resource_manager.get_font(35).render("Space -> Jump", True, (0,0,0))
                JUMP_RECT = JUMP_TEXT.get_rect(center=(500, 300))
                window.blit(JUMP_TEXT, JUMP_RECT)    

                ATTACK_TEXT = resource_manager.get_font(35).render("P -> Attack", True, (0,0,0))
                ATTACK_RECT = ATTACK_TEXT.get_rect(center=(500, 450))
                window.blit(ATTACK_TEXT, ATTACK_RECT)    

                if partida.level >= 2:
                    FIRE_TEXT = resource_manager.get_font(35).render("O -> Fireball", True, (0,0,0))
                    FIRE_RECT = FIRE_TEXT.get_rect(center=(500, 600))
                    window.blit(FIRE_TEXT, FIRE_RECT)

                BACK_BUTTON = Button(image=None, pos=(500, 700), 
                                    text_input="BACK", font=resource_manager.get_font(50), base_color="Black", hovering_color="Green")
                BACK_BUTTON.changeColor(MENU_MOUSE_POS)
                BACK_BUTTON.update(window)  
            elif sound_options:
                volumen = volume.music_volume
                sound = volume.sounds_volume

                VOLUME_TEXT = resource_manager.get_font(75).render("MUSIC", True, (0,0,0))
                VOLUME_RECT = VOLUME_TEXT.get_rect(center=(400, 340))
                window.blit(VOLUME_TEXT, VOLUME_RECT)

                scroll_bar_width =  20
                scroll_bar_height =  200
                scroll_bar = pygame.Surface((scroll_bar_width, scroll_bar_height))
                scroll_bar.fill((250,  250,  250))

                # Draw the thumb (the part you drag)
                thumb_height = int(volumen * scroll_bar_height)
                thumb = pygame.Surface((scroll_bar_width, thumb_height))
                thumb.fill((50,  50,  50))  # Set a different color for the thumb
                scroll_bar.blit(thumb, (0, scroll_bar_height - thumb_height))

                scroll_bar_rect = scroll_bar.get_rect(center=(700,  340))
                window.blit(scroll_bar, scroll_bar_rect.topleft)


                SOUND_TEXT = resource_manager.get_font(75).render("SOUND", True, (0,0,0))
                SOUND_RECT = SOUND_TEXT.get_rect(center=(400, 585))
                window.blit(SOUND_TEXT, SOUND_RECT)

                scroll_bar_width2 =  20
                scroll_bar_height2 =  200
                scroll_bar2 = pygame.Surface((scroll_bar_width2, scroll_bar_height2))
                scroll_bar2.fill((250,  250,  250))

                # Draw the thumb (the part you drag)
                thumb_height2 = int(sound * scroll_bar_height2)
                thumb2 = pygame.Surface((scroll_bar_width2, thumb_height2))
                thumb2.fill((50,  50,  50))  # Set a different color for the thumb
                scroll_bar2.blit(thumb2, (0, scroll_bar_height2 - thumb_height2))

                scroll_bar_rect2 = scroll_bar2.get_rect(center=(700,  585))
                window.blit(scroll_bar2, scroll_bar_rect2.topleft)

                OPTIONS_BACK = Button(image=None, pos=(515, 750), 
                                    text_input="BACK", font=resource_manager.get_font(50), base_color="Black", hovering_color="Green")

                OPTIONS_BACK.changeColor(MENU_MOUSE_POS)
                OPTIONS_BACK.update(window)    
            else:
                RESUME_BUTTON = Button(image=None, pos=(500, 250), 
                                    text_input="RESUME", font=resource_manager.get_font(50), base_color="Black", hovering_color="Green")
                RESUME_BUTTON.changeColor(MENU_MOUSE_POS)
                RESUME_BUTTON.update(window)

                RESTART_BUTTON = Button(image=None, pos=(500, 350), 
                                    text_input="RESTART", font=resource_manager.get_font(50), base_color="Black", hovering_color="Green")
                RESTART_BUTTON.changeColor(MENU_MOUSE_POS)
                RESTART_BUTTON.update(window)

                RESTART2_BUTTON = Button(image=None, pos=(500, 450), 
                                    text_input="LAST CHECKPOINT", font=resource_manager.get_font(50), base_color="Black", hovering_color="Green")
                RESTART2_BUTTON.changeColor(MENU_MOUSE_POS)
                RESTART2_BUTTON.update(window) 

                CONTROLS_BUTTON = Button(image=None, pos=(500, 550), 
                                    text_input="CONTROLS", font=resource_manager.get_font(50), base_color="Black", hovering_color="Green")
                CONTROLS_BUTTON.changeColor(MENU_MOUSE_POS)
                CONTROLS_BUTTON.update(window)

                OPTIONS_BUTTON = Button(image=None, pos=(500, 650), 
                                    text_input="OPTIONS", font=resource_manager.get_font(50), base_color="Black", hovering_color="Green")
                OPTIONS_BUTTON.changeColor(MENU_MOUSE_POS)
                OPTIONS_BUTTON.update(window)

                MENU_BUTTON = Button(image=None, pos=(500, 750), 
                                    text_input="MAIN MENU", font=resource_manager.get_font(50), base_color="Black", hovering_color="Green")
                MENU_BUTTON.changeColor(MENU_MOUSE_POS)
                MENU_BUTTON.update(window)
            pygame.display.update()                

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if (not read and not pause) and event.key == pygame.K_SPACE and player.jump_count < 2 and player.dead == False:
                    player.jump(volume.sounds_volume)  
                if read and (event.key == pygame.K_SPACE):
                    read = False   
                if pause and (event.key == pygame.K_SPACE):
                    pause = False 
                    sound_options = False
                    controls = False    
                if event.key == pygame.K_ESCAPE:
                    if pause:   
                        pause = False 
                        sound_options = False
                        controls = False 
                    else:
                        #partida.coins = player.coins
                        #partida.gems = player.gems
                        pause = True    
                        if read:
                            read=False
                if (not read and not pause) and event.key == pygame.K_n and mercader.close:
                    mercader.negociating = True 
                    negociate_sound = mixer.Sound(resource_manager.get_sound("negociate"))
                    negociate_sound.play()
                    negociate_sound.set_volume(volume.sounds_volume)
                    option1_mercader = Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-50), 
                            text_input="10 Coins -> 1 Life", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")
                    option2_mercader = Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-30), 
                                text_input="15 Coins -> 2 Lifes", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")
                    option3_mercader = Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-10), 
                                text_input="1 Gem -> 10 coins", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")
                if (not read and not pause) and event.key == pygame.K_r and sign.close:
                    read = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if option1_mercader.checkForInput(MENU_MOUSE_POS):
                    negociation1(player, volume.sounds_volume)
                if option2_mercader.checkForInput(MENU_MOUSE_POS):
                    negociation2(player, volume.sounds_volume)
                if option3_mercader.checkForInput(MENU_MOUSE_POS):
                    negociation3(player, volume.sounds_volume)
                if read and RESUME_BUTTON.checkForInput(MENU_MOUSE_POS):
                    read = False  
                if pause and not controls and not sound_options:    
                    if RESUME_BUTTON.checkForInput(MENU_MOUSE_POS):
                        pause = False
                    if RESTART_BUTTON.checkForInput(MENU_MOUSE_POS):
                        partida_new = Partida()
                        text = "Level 1: Forest"
                        message = "The adventure begins, the dragon waits"  
                        show_loading_screen(text,message)
                        play(window, partida_new, volume)
                    if RESTART2_BUTTON.checkForInput(MENU_MOUSE_POS):
                        partida.lives = player.lives.lives
                        if partida.coins >= 10 and partida.checkpoint==1:
                            partida.coins -= 10
                        if partida.level == 1:
                            text = "Level 1: Forest"
                            message = "The adventure begins, the dragon waits"
                        elif partida.level == 2:
                            text = "Level 2: Cave"
                            message = "Our warrior is closer to revenge, keep going!"
                        else:
                            text = "Level 3: Dragon island"
                            message = "Last step, be ready to fight the dragon!"  
                        show_loading_screen(text,message)
                        play(window, partida, volume)   
                    if CONTROLS_BUTTON.checkForInput(MENU_MOUSE_POS):
                        controls = True  
                    if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                        sound_options = True    
                    if MENU_BUTTON.checkForInput(MENU_MOUSE_POS):
                        main_menu(window, volume)         
                if pause and controls and BACK_BUTTON is not None and BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                    controls = False 

            # Manejo de la pantalla de opciones de volumen                 
            if sound_options:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if OPTIONS_BACK is not None and OPTIONS_BACK.checkForInput(MENU_MOUSE_POS):
                        sound_options = False
                    if scroll_bar_rect is not None and scroll_bar_rect.collidepoint(event.pos):
                        # Start dragging the scroll bar thumb for music
                        dragging_thumb = True
                        last_mouse_y = event.pos[1]  
                    if scroll_bar_rect2 is not None and scroll_bar_rect2.collidepoint(event.pos):
                        # Start dragging the scroll bar thumb for sound
                        dragging_thumb2 = True
                        last_mouse_y = event.pos[1]         
                elif event.type == pygame.MOUSEBUTTONUP:
                    dragging_thumb = False
                    dragging_thumb2 = False
                elif event.type == pygame.MOUSEMOTION:
                    if dragging_thumb:
                        delta_y = event.pos[1] - last_mouse_y
                        volumen += delta_y / scroll_bar_height
                        volumen = max(min(volumen,  1),  0)
                        volume.music_volume = volumen
                        last_mouse_y = event.pos[1]

                        mixer.music.set_volume(volumen)

                        # Update the thumb position
                        thumb_height = int(volumen * scroll_bar_height)
                        thumb = pygame.Surface((scroll_bar_width, thumb_height))
                        thumb.fill((100,  100,  100))
                        scroll_bar.fill((200,  200,  200))  # Reset the scroll bar background
                        scroll_bar.blit(thumb, (0, scroll_bar_height - thumb_height))    


                    if dragging_thumb2:
                        delta_y = event.pos[1] - last_mouse_y
                        sound += delta_y / scroll_bar_height2
                        sound = max(min(sound,  1),  0)
                        volume.sounds_volume = sound
                        last_mouse_y = event.pos[1]

                        # Update the thumb position
                        thumb_height2 = int(sound * scroll_bar_height2)
                        thumb2 = pygame.Surface((scroll_bar_width2, thumb_height2))
                        thumb2.fill((100,  100,  100))
                        scroll_bar2.fill((200,  200,  200))  # Reset the scroll bar background
                        scroll_bar2.blit(thumb2, (0, scroll_bar_height2 - thumb_height2))



        if not read and not pause:
            player.loop(delta_time, all_enemies_group, window, partida, volume)
            
            for arrow in arrow_group:
                arrow.loop()

            for enemy in all_enemies_group:
                enemy.loop(player,volume)
                
            mercader.loop(player,offset_x)
            checkpoint.loop()
            checkpoint_end.loop()
            sign.loop(player)

            handle_move(partida,volume,player,all_enemies_group,firstBoss,meleeEnemies_group,checkpoint,checkpoint_end,objects,arrow_group,fireball_group,delta_time)
            draw(window,background,bg_image,heart_image, coin_image, gem_image,arrow_group,fireball_group,player,sign,objects,checkpoint,checkpoint_end,
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
                    offset_x += player.x_vel  / FPS
    
    pygame.quit()
    quit()

def main_menu(window, volume):

    if not pygame.mixer.music.get_busy():
        mixer.music.set_volume(volume.music_volume)
        mixer.music.load(resource_manager.get_sound("menu"))
        mixer.music.play(-1)
        
    while True:
        window.fill("black")

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = resource_manager.get_font(75).render("DRAGON KILL", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(515, 120))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(515, 300), 
                            text_input="PLAY", font=resource_manager.get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Options Rect.png"), pos=(515, 475), 
                            text_input="OPTIONS", font=resource_manager.get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(515, 650), 
                            text_input="QUIT", font=resource_manager.get_font(75), base_color="#d7fcd4", hovering_color="White")

        window.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(window)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    text = "Level 1: Forest"
                    message = "The adventure begins, the dragon awaits"  
                    show_loading_screen(text, message)
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