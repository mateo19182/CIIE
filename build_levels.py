import pygame
import button
from objects import Block, Block2, Block3, Block4, Block5, Block6, Platform, Spikeball
import resource_manager
from player import Player
from partida import HEIGHT, WIDTH
from NPCs import RangedEnemies, MeleeEnemie, Mercader, Boss, SecondBoss, Skull, ThirdBoss
from items import Sign, Checkpoint, CheckpointEnd, Lives, putCoins, putGems

def build_level(partida):
    lives = Lives(partida.lives)
    
    all_enemies_group = pygame.sprite.Group()
    meleeEnemies_group = pygame.sprite.Group()
    arrow_group = pygame.sprite.Group()
    fireball_group = pygame.sprite.Group()

    distance = 0
    checkpoint_activated = False 

    block_size = 96
    block2_size = 64 
    block3_size = 64 
    block4_size = 32 

    plat_size = 100

    offset_x = 0

    if partida.level == 1:
        background,bg_image, heart_image, coin_image, gem_image = resource_manager.get_background("Night.png")
        if partida.checkpoint == 1:
            distance = 7300
            checkpoint_activated = True
        
        player = Player(400,400,50,50, lives,fireball_group,partida.coins,partida.gems)
        sign = Sign(300-distance,618,100,100)
        rangedenemie1 = RangedEnemies(900-distance,500,100,100,4,arrow_group,"HalflingRanger")
        rangedenemie2 = RangedEnemies(6135-distance,230,100,100,4,arrow_group,"HalflingRanger")
        meleeEnemie1 = MeleeEnemie(800-distance,625,100,100,"HalflingRogue")
        meleeEnemie2 = MeleeEnemie(4375-distance,525,100,100,"HalflingRogue")
        meleeEnemie3 = MeleeEnemie(8320-distance,500,100,100,"HalflingRogue")
        mercader = Mercader(2700-distance, 625, 100, 100) 
        firstBoss = Boss(8500-distance,450,100,100)
        checkpoint = Checkpoint(7700-distance,375,50,50, checkpoint_activated)
        checkpoint_end = CheckpointEnd(8950-distance,575,50,50)

        all_enemies_group.add(meleeEnemie1)
        all_enemies_group.add(meleeEnemie2)
        all_enemies_group.add(meleeEnemie3)

        all_enemies_group.add(rangedenemie1)
        all_enemies_group.add(rangedenemie2)
        all_enemies_group.add(firstBoss)
        
        meleeEnemies_group.add(meleeEnemie1)
        meleeEnemies_group.add(meleeEnemie2)
        meleeEnemies_group.add(meleeEnemie3)

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
        
        gems = []
        
        putGems(-1000 - distance,650,2,gems)
        putGems(425 - distance,25,1,gems)
        putGems(6630 - distance,650,1,gems)

        gems = pygame.sprite.Group(gems)

        coins = []

        putCoins(1115 - distance,200,1,coins)
        putCoins(920 - distance,200,1,coins)
        putCoins(725 - distance,200,1,coins)
        putCoins(1325 - distance,350,3,coins)
        putCoins(2075 - distance,500,3,coins)
        putCoins(4225 - distance,250,3,coins)
        putCoins(4730 - distance,400,3,coins)
        putCoins(2525 - distance,500,1,coins)
        putCoins(2850 - distance,400,1,coins)
        putCoins(2625 - distance,200,1,coins)
        putCoins(2950 - distance,100,1,coins)
        putCoins(5335 - distance,650,3,coins)
        putCoins(5720 - distance,450,3,coins)
        putCoins(6485 - distance,50,3,coins)
        putCoins(6835 - distance,250,3,coins)

        coins = pygame.sprite.Group(coins)

    elif partida.level == 2:
        background,bg_image, heart_image, coin_image, gem_image = resource_manager.get_background("Cave2.png")

        if partida.checkpoint == 1:
            distance = 7300
            checkpoint_activated = True
        
        player = Player(400,400,50,50, lives,fireball_group,partida.coins,partida.gems)
        sign = Sign(700-distance,647,100,100)
        rangedenemie1 = RangedEnemies(945-distance,335,100,100,30,arrow_group,"GnomeTinkerer")
        rangedenemie2 = RangedEnemies(6553-distance,530,100,100,30,arrow_group,"GnomeTinkerer")
        meleeEnemie1 = MeleeEnemie(1400-distance,625,100,100,"HalflingRogue")
        meleeEnemie2 = MeleeEnemie(4375-distance,525,100,100,"HalflingRogue")
        mercader = Mercader(2700-distance, 655, 100, 100) 
        firstBoss = SecondBoss(8500-distance,480,100,100)
        checkpoint = Checkpoint(7700-distance,480,50,50, checkpoint_activated)
        checkpoint_end = CheckpointEnd(9000-distance,610,50,50)
        meleeEnemie4 = Skull(5950 - distance,350,1000,1000,"Skull")
        meleeEnemie5 = Skull(6050 - distance,350,1000,1000,"Skull")

        all_enemies_group.add(meleeEnemie1)
        all_enemies_group.add(meleeEnemie2)
        all_enemies_group.add(meleeEnemie4)
        all_enemies_group.add(meleeEnemie5)
        all_enemies_group.add(rangedenemie1)
        all_enemies_group.add(rangedenemie2)
        all_enemies_group.add(firstBoss)

        meleeEnemies_group.add(meleeEnemie1)
        meleeEnemies_group.add(meleeEnemie2)
        meleeEnemies_group.add(meleeEnemie4)
        meleeEnemies_group.add(meleeEnemie5)

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

        gems = []

        putGems(2100 - distance,682,1,gems)
        putGems(2370 - distance,106,1,gems)

        gems = pygame.sprite.Group(gems)


        coins = []

        putCoins(1450 - distance,487,4,coins)
        putCoins(2050 - distance,106,5,coins)
        putCoins(3050 - distance,683,8,coins)
        putCoins(3975 - distance,42,4,coins)
        putCoins(3975 - distance,234,5,coins)
        putCoins(3975 - distance,490,6,coins)
        putCoins(6850 - distance,363,15,coins)

        coins = pygame.sprite.Group(coins)

    elif partida.level == 3:
        background,bg_image, heart_image, coin_image, gem_image = resource_manager.get_background("Cave2.png")

        if partida.checkpoint == 1:
            distance = 8800
            checkpoint_activated = True
        player = Player(400,400,50,50, lives,fireball_group,partida.coins,partida.gems)
        sign = Sign(300-distance,647,100,100)
        rangedenemie1 = RangedEnemies(1200-distance,270,100,100,30,arrow_group,"GnomeTinkerer")
        meleeEnemie1 = Skull(2875 - distance,350,1000,1000,"Skull")
        meleeEnemie2 = Skull(3525 - distance,350,1000,1000,"Skull")
        meleeEnemie3 = MeleeEnemie(4475-distance,500,100,100,"Skeleton")
        mercader = Mercader(3915-distance, 400, 100, 100)
        firstBoss = ThirdBoss(9800-distance,390,100,100)
        checkpoint = Checkpoint(9185-distance,290,50,50, checkpoint_activated)
        checkpoint_end = CheckpointEnd(10400-distance,610,50,50)

        all_enemies_group.add(meleeEnemie1)
        all_enemies_group.add(meleeEnemie2)
        all_enemies_group.add(meleeEnemie3)


        all_enemies_group.add(rangedenemie1)

        all_enemies_group.add(firstBoss)

        meleeEnemies_group.add(meleeEnemie1)
        meleeEnemies_group.add(meleeEnemie2)
        meleeEnemies_group.add(meleeEnemie3)
        floor = [Block5(i*block2_size-distance,HEIGHT - block2_size ,block2_size)for i in range(-10,8)]
        floor5 = [Block5(i*block2_size-distance + 6000,HEIGHT - block2_size - 64 ,block2_size)for i in range(0,5)]
        floor6 = [Block5(i*block2_size-distance + 7000,HEIGHT - block2_size - 64 ,block2_size)for i in range(0,5)]
        floor7 = [Block5(i*block2_size-distance + 9200,HEIGHT - block2_size - 320 + i*block2_size,block2_size)for i in range(0,6)]
        floor8 = [Block5(i*block2_size-distance + 9584,HEIGHT - block2_size  ,block2_size)for i in range(0,15)]
        
        build0 = [Block6(i*block2_size-distance + 3700,HEIGHT - block2_size - 256 ,block2_size)for i in range(0,6)]
        build1 = [Block6(i*block2_size-distance + 3700,HEIGHT - block2_size - 256 ,block2_size)for i in range(0,7)]
        build2 = [Block6(i*block2_size-distance + 3700,HEIGHT - block2_size - 192 ,block2_size)for i in range(0,8)]
        build3 = [Block6(i*block2_size-distance + 3700,HEIGHT - block2_size - 128 ,block2_size)for i in range(0,9)]
        build4 = [Block6(i*block2_size-distance + 3700,HEIGHT - block2_size - 64 ,block2_size)for i in range(0,19)]
        build5 = [Block6(i*block2_size-distance + 3700,HEIGHT - block2_size ,block2_size)for i in range(0,19)]
        
        plat1 = [Block5(i*block4_size-distance + 1000,HEIGHT - block2_size - 384,block4_size)for i in range(0,10)]
        plat2 = [Block5(i*block4_size-distance + 1672,HEIGHT - block2_size - 384,block4_size)for i in range(0,10)]
        plat3 = [Block5(i*block4_size-distance + 300,HEIGHT - block2_size - 448,block4_size)for i in range(0,3)]
        plat4 = [Block5(i*block4_size-distance + 700,HEIGHT - block2_size - 640,block4_size)for i in range(0,4)]
        plat5 = [Block5(i*block4_size-distance,HEIGHT - block2_size - 150,block4_size)for i in range(0,3)]
        
        plat6 = [Block5(3*i*block4_size-distance + 2100 ,HEIGHT - block2_size - 100 - 4*i*block2_size,block4_size)for i in range(0,5)]
        plat7 = [Block5(3*i*block4_size-distance + 2500 ,HEIGHT - block2_size - 100 - 4*i*block2_size,block4_size)for i in range(0,5)]
        plat8 = [Block5(3*i*block4_size-distance + 2900 ,HEIGHT - block2_size - 100 - 4*i*block2_size,block4_size)for i in range(0,5)]
        
        plat9 = [Block5(3*i*block4_size-distance + 2350 ,HEIGHT - block2_size - 200 - 4*i*block2_size,block4_size)for i in range(0,3)]
        plat10 = [Block5(3*i*block4_size-distance + 2750 ,HEIGHT - block2_size - 200 - 4*i*block2_size,block4_size)for i in range(0,3)]
        plat11 = [Block5(3*i*block4_size-distance + 3150 ,HEIGHT - block2_size - 200 - 4*i*block2_size,block4_size)for i in range(0,3)]
        
        plat12 = [Block5(3*i*block4_size-distance + 3300 ,HEIGHT - block2_size - 100 - 4*i*block2_size,block4_size)for i in range(0,2)]
        plat13 = [Block5(3*i*block4_size-distance + 3550 ,HEIGHT - block2_size - 200 - 4*i*block2_size,block4_size)for i in range(0,2)]
        
        plat14 = [Block5(i*block4_size-distance + 4450,HEIGHT - block2_size - 400 ,block4_size)for i in range(0,3)]
        plat15 = [Block5(i*block4_size-distance + 4720,HEIGHT - block2_size - 550 ,block4_size)for i in range(0,3)]

        plat16 = [Block5(i*block4_size-distance + 5100,HEIGHT - block2_size - 550 + i*block4_size,block4_size)for i in range(0,3)]
        plat17 = [Block5(i*block4_size-distance + 5192,HEIGHT - block2_size - 454 ,block4_size)for i in range(0,10)]

        plat18 = [Block5(10*i*block4_size-distance + 5800,HEIGHT - block2_size - 600 - i*block4_size ,block4_size)for i in range(0,3)]
        
        plat19 = [Block5(i*block4_size-distance + 5650,HEIGHT - block2_size - 200 ,block4_size)for i in range(0,5)]

        plat20 = [Block5(i*block4_size-distance + 6500,HEIGHT - block2_size - 300 ,block4_size)for i in range(0,2)]
        plat21= [Block5(i*block4_size-distance + 6600,HEIGHT - block2_size , block4_size)for i in range(0,3)]
        plat22 = [Block5(i*block4_size-distance + 6500,HEIGHT - block2_size - 300 ,block4_size)for i in range(0,2)]
        plat23 = [Block5(i*block4_size-distance + 6700,HEIGHT - block2_size - 600 ,block4_size)for i in range(0,10)]

        plat24 = [Block5(i*block4_size-distance + 7250,HEIGHT - block2_size - 500 ,block4_size)for i in range(0,5)]

        plat25 = [Block5(5*i*block4_size-distance + 7500 ,HEIGHT - block2_size - 100 - 4*i*block2_size,block4_size)for i in range(0,5)]
        plat26 = [Block5(5*i*block4_size-distance + 8050 ,HEIGHT - block2_size - 100 - 4*i*block2_size,block4_size)for i in range(0,5)]
        plat27 = [Block5(5*i*block4_size-distance + 8600 ,HEIGHT - block2_size - 100 - 4*i*block2_size,block4_size)for i in range(0,5)]   
        plat28 = [Block5(5*i*block4_size-distance + 7800 ,HEIGHT - block2_size - 200 - 4*i*block2_size,block4_size)for i in range(0,3)]
        plat29 = [Block5(5*i*block4_size-distance + 8350 ,HEIGHT - block2_size - 200 - 4*i*block2_size,block4_size)for i in range(0,3)]
        plat30 = [Block5(5*i*block4_size-distance + 8900 ,HEIGHT - block2_size - 200 - 4*i*block2_size,block4_size)for i in range(0,2)]
        
        spike1 = [Spikeball(i*block4_size-distance + 1480 ,HEIGHT - block2_size - 600,block2_size)for i in range(0,1)]
        spike2 = [Spikeball(2*i*block4_size - distance + 4600 ,HEIGHT - block2_size - 350 - 2*i*block4_size,block2_size)for i in range(0,3)]
        spike3 = [Spikeball(40*i - distance + 5850 ,HEIGHT - block2_size - 500 - 3*i,block2_size)for i in range(0,20)]

        objects = [*build0,*build1,*build2,*build3,*build4,*build5, *floor, *floor5,*floor6,*floor7,*floor8, *plat1, *plat2, *plat3, *plat4, *plat5, *plat6, *plat7, *plat8, *plat9, *plat10, *plat11, *plat12, *plat13, *plat14, *plat15,*plat16, *plat17, *plat18,*plat19,*plat20,*plat21,*plat22,*plat23,*plat24,*plat25,*plat26,*plat27,*plat28,*plat29,*plat30, *spike1, *spike2, *spike3]

        gems = []

        putGems(2097 - distance,584,1,gems)
        putGems(6790 - distance,83,2,gems)

        gems = pygame.sprite.Group(gems)


        coins = []

        putCoins(1400 - distance,487,4,coins)
        putCoins(0 - distance,533,2,coins)
        putCoins(300 - distance,234,2,coins)
        putCoins(700 - distance,42,3,coins)
        putCoins(4449 - distance,282,2,coins)
        putCoins(4721 - distance,133,2,coins)

        coins = pygame.sprite.Group(coins)   

    option1_mercader = button.Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-50), 
                        text_input="10 Coins -> 1 Life", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")
    option2_mercader = button.Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-30), 
                            text_input="15 Coins -> 2 Lifes", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")
    option3_mercader = button.Button(image=pygame.image.load("assets/OptionsMercader.png"), pos=(mercader.rect.x - offset_x+40,mercader.rect.y-10), 
                            text_input="1 Gem -> 10 coins", font=pygame.font.Font("assets/font.ttf", 15), base_color="#d7fcd4", hovering_color="White")

    return mercader, player, sign, all_enemies_group, arrow_group, checkpoint, checkpoint_end, firstBoss, meleeEnemies_group, objects, fireball_group, background, bg_image, heart_image, coin_image, gem_image, coins, gems, option1_mercader, option2_mercader, option3_mercader