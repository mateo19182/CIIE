import pygame
from objects import Block3, Block4, Spikeball
from pygame import mixer
import resource_manager


def handle_vertical_colission(player,objects,dy):
    collided_objects = []
    
    for obj in objects:
        if pygame.sprite.collide_rect(player,obj):
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
        if pygame.sprite.collide_rect(player,obj):
            collided_object = obj
            if player.y_vel > 0.5:
                player.wall_jump = True
                player.y_vel *= 0.7
                #player.jump_count=0
            if isinstance(obj, Block3) or isinstance(obj, Block4) or isinstance(obj, Spikeball):
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
        if pygame.sprite.collide_rect(player,arrow):
            arrow.kill()
            player.get_hit(volume.sounds_volume)
            
        for obj in objects:
            if pygame.sprite.collide_rect(arrow,obj):
                arrow.kill()
                arrow.update()
    player.update()

def collide_checkpoint(player,checkpoint,partida,volume):
    if(pygame.sprite.collide_mask(player,checkpoint)):
        if not checkpoint.activated:
            checkpoint.activated = True
            partida.coins = player.coins
            partida.gems = player.gems
            death_sound = mixer.Sound(resource_manager.get_sound("checkpoint"))
            death_sound.play()
            death_sound.set_volume(volume.sounds_volume)
            partida.checkpoint = 1     

def collide_explosion(explosions, player, volume):
    for expl in explosions:
        if pygame.sprite.collide_circle(expl,player) and expl.current_frame > 7:
            player.get_hit(volume.sounds_volume)

def collide_fireball(fireball_group,enemies_group,objects,volume):
    for fireball in fireball_group:
        for enemy in enemies_group:
            if pygame.sprite.collide_rect(fireball,enemy):
                enemy.take_damage(volume)
                #enemy.is_alive = False
                fireball.kill()    
                
        for obj in objects:
            if pygame.sprite.collide_rect(fireball,obj):
                fireball.kill()
                fireball.update()

def collide_enemie(player,enemie,objects,volume):
    
    if(pygame.sprite.collide_mask(player,enemie)):
        if enemie.is_alive:
            player.get_hit(volume.sounds_volume)
                
    for obj in objects:
        if(pygame.sprite.collide_rect(enemie,obj)):
            enemie.fall = False
            return
                
    enemie.fall = True

    if enemie.GRAVITY > 1:
        enemie.y += enemie.GRAVITY
        enemie.rect.y = enemie.y

    player.update()
