import pygame
import random
import sys
from pygame.locals import *

from sprites import (MasterSprite, 
                     Player, FriendShip, Monster, Beam, Explosion,
                     BombPower, ShieldPower, DoublebeamPower, FriendPower, LifePower, TriplecupcakePower,
                     BroccoliBeamfast,
                     Green, Yellow, Grey, Blue, Pink, Boss)
from database import Database
from load import load_image, load_sound, load_music,Var
from menu import *

if not pygame.mixer:
    print('Warning, sound disablead')
if not pygame.font:
    print('Warning, fonts disabled')

BACK = 0
SINGLE = 0

BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

direction = {None: (0, 0), pygame.K_UP: (0, -2), pygame.K_DOWN: (0, 2),
             pygame.K_LEFT: (-2, 0), pygame.K_RIGHT: (2, 0)}

class Single():

    def playGame(screen_size):
        load_music('music_loop.ogg')
    # Initialize everything
        pygame.mixer.pre_init(11025, -16, 2, 512)
        pygame.init()
        ratio = (screen_size / 400)
        screen = pygame.display.set_mode((screen_size, screen_size), HWSURFACE|DOUBLEBUF|RESIZABLE)
        pygame.display.set_caption("Let's Play!")
        pygame.mouse.set_visible(0)

    # Prepare background image
        # Game field
        field1, field1Rect = load_image("field.png") # skin
        field2, field2Rect = load_image("field.png") #skin
        field1Rect.midtop = screen.get_rect().midtop
        field2Rect.midbottom = field1Rect.midtop



        # pause
        pause,pauseRect = load_image('pause.png')
        pause = pygame.transform.scale(pause, (600, 600))
        pauseRect.midtop = screen.get_rect().midtop
        pauseMenu = False


    # Prepare game contents
        # life
        life1, life1Rect = load_image('heart1.png')
        life2, life2Rect = load_image('heart2.png')
        life3, life3Rect = load_image('heart3.png')

        # boss life       
        Bosslife0, Bosslife0Rect = load_image('bossheart0.png')
        Bosslife1, Bosslife1Rect = load_image('bossheart2.png')
        Bosslife2, Bosslife2Rect = load_image('bossheart4.png')
        Bosslife3, Bosslife3Rect = load_image('bossheart6.png')
        Bosslife4, Bosslife4Rect = load_image('bossheart8.png')
        Bosslife5, Bosslife5Rect = load_image('bossheart10.png')

        # Sounds
        missile_sound = load_sound('missile.ogg')
        bomb_sound = load_sound('bomb.ogg')
        alien_explode_sound = load_sound('alien_explode.ogg')
        ship_explode_sound = load_sound('ship_explode.ogg')
        load_music('music_loop.ogg')
        soundFX = Database().getSound()
        music = Database().getSound()
        if music and pygame.mixer: 
           pygame.mixer.music.play(loops=-1)

        # font
        font = pygame.font.Font("LeeSeoyun.ttf", round(15*ratio))
        font2 = pygame.font.Font("LeeSeoyun.ttf", round(21*ratio))
        # clock - 60 FPS game
        clockTime = 60  # maximum FPS
        clock = pygame.time.Clock()
        
        # speed
        speed = 1.5
        MasterSprite.speed = speed
        
        # object
        player = Player(screen_size)
        miniplayer = FriendShip(screen_size)
        boss = Boss(screen_size)
        
        initialMonsterTypes = (Green, Yellow)
        powerTypes = (BombPower, ShieldPower, DoublebeamPower, TriplecupcakePower, BroccoliBeamfast,
                        FriendPower, LifePower)
        bombs = pygame.sprite.Group()
        powers = pygame.sprite.Group()

        ship_selection = Ship_selection_check() 
        
     # Score Function
        def kill_monster(monster, monstersLeftThisWave, score) :
            if wave == 5:
                if monster.pType == 'green' or monster.pType == 'yellow' or monster.pType == 'blue' or monster.pType == 'pink':
                    score += 0
                elif monster.pType == 'boss':
                    monstersLeftThisWave -= 160
                    score += 20
            else:
                monstersLeftThisWave -= 1
                if monster.pType == 'green':
                    score += 1
                elif monster.pType == 'yellow':
                    score += 2
                elif monster.pType == 'blue':
                    score += 4
                elif monster.pType == 'pink':
                    score += 8
                elif monster.pType == 'boss':
                    monstersLeftThisWave -= 159
                    score += 20
            return monstersLeftThisWave, score
        
    # High Score
        hiScores=Database().getScores()
        highScoreTexts = [font.render("NAME", 1, RED),
                        font.render("SCORE", 1, RED)]
        highScorePos = [highScoreTexts[0].get_rect(
                        topleft=screen.get_rect().inflate(-100, -100).topleft),
                        highScoreTexts[1].get_rect(
                        midtop=screen.get_rect().inflate(-100, -100).midtop)]
        for hs in hiScores:
            highScoreTexts.extend([font.render(str(hs[x]), 1, 'WHITE')
                                for x in range(2)])
            highScorePos.extend([highScoreTexts[x].get_rect(
                topleft=highScorePos[x].bottomleft) for x in range(-2, 0)])
    
    # pause menu text  
        
        blankText=font.render('            ',1,'white')
        blankPos=blankText.get_rect(topright=screen.get_rect().center)
        continueText = font2.render('CONTINUE', 1, 'white')
        continuePos = continueText.get_rect(topleft=blankPos.bottomleft)   
        gotoMenuText = font2.render('GO TO MAIN', 1, 'white')
        gotoMenuPos = gotoMenuText.get_rect(topleft=continuePos.bottomleft)
        selectText = font2.render('*', 1, 'white')
        pauseMenuDict = {1: continuePos, 2: gotoMenuPos}
        selection = 1
        selectPos = selectText.get_rect(topright=pauseMenuDict[selection].topleft)
        


    #########################
    #    Start Time Mode    #
    #########################

        restart = True
        while restart == True:

        # Prepare game objects : reset
            # Reset Sprite groups
            alldrawings = pygame.sprite.Group()
            allsprites = pygame.sprite.RenderPlain((player,))
            MasterSprite.allsprites = allsprites
            Monster.pool = pygame.sprite.Group(
                [monster(screen_size) for monster in initialMonsterTypes for _ in range(5)])
            Monster.active = pygame.sprite.Group()
            Beam.pool = pygame.sprite.Group([Beam(screen_size) for _ in range(10)]) 
            Beam.active = pygame.sprite.Group()
            Explosion.pool = pygame.sprite.Group([Explosion(screen_size) for _ in range(10)])
            Explosion.active = pygame.sprite.Group()

            # Reset game contents
            monstersThisWave, monstersLeftThisWave, Monster.numOffScreen = 10, 10, 10
            friendship = False
            doublebeam = False
            triplecupcake = False
            broccoli = False
            pepper_chili = False 
            bombsHeld = 3
            score = 0
            beamFired = 0
            wave = 1
            health = 3

            # speed
            speed = 1.5 * ratio
            newspeed = 2.5 * ratio
            org_speed = 1.5 * ratio
            player.speed = speed
        
            # Reset all time
            bearPeriod = clockTime // speed
            curTime = 0
            powerTime = 8 * clockTime
            powerTimeLeft = powerTime
            betweenWaveTime = 3 * clockTime
            betweenWaveCount = betweenWaveTime
            
            betweenDoubleTime = 8 * clockTime
            betweenDoubleCount = betweenDoubleTime
            betweenTripleTime = 8 * clockTime
            betweenTripleCount = betweenTripleTime
            friendshipTime = 8 * clockTime
            friendshipCount = friendshipTime
            friendshipBeamTime = 0.2 * clockTime
            friendshipBeamCount = friendshipBeamTime
            broccoliTime  = 8 * clockTime
            broccoliCount = broccoliTime
            
            player.alive = True
            player.life = 3
            player.initializeKeys()
            
            boss.health = 10
            
            player.showChange_ship = False
        # Start Game
            while player.alive:
                clock.tick(clockTime)
                
            # Drop Items
                powerTimeLeft -= 1
                if powerTimeLeft <= 0:
                    powerTimeLeft = powerTime
                    random.choice(powerTypes)(screen_size).add(powers, allsprites)
            # Event Handling
                for event in pygame.event.get():
                    if (event.type == pygame.QUIT
                        or event.type == pygame.KEYDOWN
                            and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                    # Resize windowSize
                    elif (event.type == pygame.VIDEORESIZE):
                        screen_size = min(event.w, event.h)
                        if screen_size <= 400:
                            screen_size = 400
                        if screen_size >= 900:
                            screen_size = 900
                        screen = pygame.display.set_mode((screen_size, screen_size), HWSURFACE|DOUBLEBUF|RESIZABLE)
                        ratio = (screen_size / 600)
                        font = pygame.font.Font(None, round(36*ratio))
                    # Player Moving
                    elif (event.type == pygame.KEYDOWN
                        and event.key in direction.keys()):
                        player.horiz += direction[event.key][0] * player.speed
                        player.vert += direction[event.key][1] * player.speed
                    elif (event.type == pygame.KEYUP
                        and event.key in direction.keys()):
                        player.horiz -= direction[event.key][0] * player.speed
                        player.vert -= direction[event.key][1] * player.speed
                    # Beam
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_SPACE):
                        if doublebeam :
                            Beam.position(player.rect.topleft)
                            Beam.position(player.rect.topright)
                            beamFired += 2
                        elif triplecupcake :
                            Beam.position2(player.rect.left - 5)
                            Beam.position2(player.rect.top)
                            Beam.position2(player.rect.right + 5)
                            beamFired += 3
                        elif broccoli :
                            Beam.position(player.rect.midtop)
                            beam.speed = 1.5
                            beamFired += 1
                        else : 
                            Beam.position(player.rect.midtop)
                            beamFired += 1
                        if soundFX:
                            missile_sound.play()
                    # Bomb
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_b):
                        if bombsHeld > 0:
                            bombsHeld -= 1
                            newBomb = player.bomb()
                            newBomb.add(bombs, alldrawings)
                            if soundFX:
                                bomb_sound.play()
                    # Pause Menu
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_p):
                        pauseMenu = True
                        cnt=0
                        pauseMenuDict={1:continuePos,2:gotoMenuPos}
                        selection=1
                        while pauseMenu:
                            #clock.tick(clockTime)
                            clock.tick(clockTime)
                            pause_size = (round(pause.get_width() * ratio), round(pause.get_height() * ratio))
                            screen.blit(pygame.transform.scale(pause, pause_size), (0,0))
                            pause = pygame.transform.scale(pause, (600, 600))
                            pauseRect.midtop = screen.get_rect().midtop
                            
                            for event in pygame.event.get():
                                if (event.type == pygame.QUIT
                                    or event.type == pygame.KEYDOWN
                                        and event.key == pygame.K_ESCAPE):
                                    pygame.quit()
                                    sys.exit()
                                # Resize windowSize
                                elif (event.type == pygame.VIDEORESIZE):
                                    screen_size = min(event.w, event.h)
                                    if screen_size <= 400:
                                        screen_size = 400
                                    if screen_size >= 900:
                                        screen_size = 900
                                    screen = pygame.display.set_mode((screen_size, screen_size), HWSURFACE|DOUBLEBUF|RESIZABLE)
                                    ratio = (screen_size / 600)
                                    font = pygame.font.Font(None, round(36*ratio))
                                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) :  #pause menu (continue, go)
                                    if selection == 1:
                                        pauseMenu = False
                                    elif selection == 2:
                                        inMenu =True
                                        return inMenu, screen_size
                                elif (event.type == pygame.KEYDOWN
                                        and event.key == pygame.K_DOWN
                                        and selection < len(pauseMenuDict)):
                                        selection += 1
                                elif (event.type == pygame.KEYDOWN
                                        and event.key == pygame.K_UP
                                        and selection > 1):
                                        selection -= 1
                                
                                
                            blankText=font.render('            ',1,BLACK)
                            blankPos=blankText.get_rect(topright=screen.get_rect().center)
                            continueText = font2.render('CONTINUE', 1, 'white')
                            continuePos = continueText.get_rect(topleft=blankPos.bottomleft)   
                            gotoMenuText = font2.render('GO TO MAIN', 1, 'white')
                            gotoMenuPos = gotoMenuText.get_rect(topleft=continuePos.bottomleft)
                            selectText = font2.render('*', 1, 'white')
                            pauseMenuDict={1:continuePos,2:gotoMenuPos}

                            
                            selectPos = selectText.get_rect(topright=pauseMenuDict[selection].topleft)

                            textOverlays = zip([blankText,continueText, gotoMenuText, selectText],
                                                    [blankPos,continuePos, gotoMenuPos, selectPos])
                            for txt, pos in textOverlays:
                                screen.blit(txt, pos)

                            alldrawings.update()
                            pygame.display.flip()
                    

            # Collision Detection
                # monster
                for monster in Monster.active:
                    for bomb in bombs:
                        if pygame.sprite.collide_circle(
                                bomb, monster) and monster in Monster.active:
                            if monster.pType != 'grey' :
                                if monster.pType == 'boss':
                                    if boss.health >= 1 :
                                        boss.health -= 1
                                    else :
                                        monster.table() 
                                        Explosion.position(monster.rect.center)
                                        monstersLeftThisWave, score = kill_monster(monster, monstersLeftThisWave, score)
                                else:
                                    monster.table()
                                    Explosion.position(monster.rect.center)
                                    monstersLeftThisWave, score = kill_monster(monster, monstersLeftThisWave, score)
                            beamFired += 1
                            
                    for beam in Beam.active:
                        if pygame.sprite.collide_rect(
                                beam, monster) and monster in Monster.active:
                            beam.table()
                            if monster.pType != 'grey' :
                                beam.table()
                                if monster.pType == 'boss':
                                    if boss.health >= 1 :
                                        boss.health -= 1                        
                                    else :         
                                        monster.table()                  
                                        Explosion.position(monster.rect.center)
                                        monstersLeftThisWave, score = kill_monster(monster, monstersLeftThisWave, score)
                                else:
                                    monster.table()
                                    Explosion.position(monster.rect.center)
                                    monstersLeftThisWave, score = kill_monster(monster, monstersLeftThisWave, score)
                            
                    if pygame.sprite.collide_rect(monster, player) :
                        if player.shieldUp:
                            monster.table()
                            Explosion.position(monster.rect.center)
                            monstersLeftThisWave, score = kill_monster(monster, monstersLeftThisWave, score)
                            beamFired += 1
                            player.shieldUp = False
                        elif player.life > 1:   # life
                            monster.table()
                            Explosion.position(monster.rect.center)
                            monstersLeftThisWave -= 1
                            score += 1
                            if monster.pType == 'boss':
                                player.life = 0
                            else:
                                player.life -= 1
                        else:
                            restart = False
                            player.alive = False
                            player.remove(allsprites)
                            Explosion.position(player.rect.center)
                            if soundFX:
                                alien_explode_sound.play() #
                
                # PowerUps
                for power in powers:
                    if pygame.sprite.collide_circle(power, player):
                        if power.pType == 'bomb':
                            bombsHeld += 1
                        elif power.pType == 'shield':
                            player.shieldUp = True
                        elif power.pType == 'doublebeam' :
                            doublebeam = True
                        elif power.pType == 'triplecupcake' :
                            triplecupcake = True
                        elif power.pType == 'broccoli' :
                            broccoli = True
                        elif power.pType == 'life':
                            if player.life < 3:
                                player.life += 1 
                        elif power.pType == 'friendShip' :
                            friendship = True
                            MasterSprite.allsprites.add(miniplayer) 
                            allsprites.update(screen_size)
                            allsprites.draw(screen)
                        power.kill()
                    elif power.rect.top > power.area.bottom:
                        power.kill()

            # Update Monsters
                if curTime <= 0 and monstersLeftThisWave > 0 :
                    Monster.position()
                    curTime = bearPeriod
                elif curTime > 0:
                    curTime -= 1

            # Update text overlays
                waveText = font.render("Wave: " + str(wave), 1, 'WHITE')
                leftText = font.render("Monsters Left: " + str(monstersLeftThisWave), 1, 'WHITE')
                scoreText = font.render("Score: " + str(score), 1, 'WHITE')
                bHealthText = font.render("Boss Health: ", 1, 'WHITE')
                beamText = font.render("Fart Beams: " + str(bombsHeld), 1, 'WHITE')

                wavePos = waveText.get_rect(topleft=screen.get_rect().topleft)
                leftPos = leftText.get_rect(midtop=screen.get_rect().midtop)
                scorePos = scoreText.get_rect(topright=screen.get_rect().topright)
                bHealthPos = bHealthText.get_rect(bottomleft=screen.get_rect().bottomleft)
                bombPos = beamText.get_rect(bottomright=screen.get_rect().bottomright)

                text = [waveText, leftText, scoreText, bHealthText, beamText]
                textposition = [wavePos, leftPos, scorePos, bHealthPos, bombPos]

            # Update using items
                # item - doublebeam, triplecupcake, broccoli
                if doublebeam:
                    if betweenDoubleCount > 0:
                        betweenDoubleCount -= 1
                    elif betweenDoubleCount == 0:
                        doublebeam = False
                        betweenDoubleCount = betweenDoubleTime
                if triplecupcake:
                    if betweenTripleCount > 0:
                        betweenTripleCount -= 1
                    elif betweenTripleCount == 0:
                        triplecupcake = False
                        betweenTripleCount = betweenTripleTime
                if broccoli:
                    if broccoliCount > 0:
                        broccoliCount -= 1
                    elif broccoliCount == 0:
                        beam.speed = 1
                        broccoli = False
                        broccoliCount = broccoliTime
                # item - friendship
                miniplayer.rect.bottomright = player.rect.bottomleft
                if friendship:
                    # friendship
                    if friendshipCount > 0:
                        friendshipCount -= 1
                    elif friendshipCount == 0:
                        friendship = False
                        miniplayer.remove()
                        friendshipCount = friendshipTime
                    # friendship's beam
                    if friendshipBeamCount > 0:
                        friendshipBeamCount -= 1
                    elif friendshipBeamCount == 0:
                        friendshipBeamCount = friendshipBeamTime
                        Beam.position(miniplayer.rect.midtop)

            # betweenWaveCount - Detertmine when to move to next wave
                if monstersLeftThisWave <= 0 :
                    if betweenWaveCount > 0:
                        betweenWaveCount -= 1
                        nextWaveText = font.render(
                            'Wave ' + str(wave + 1) + ' in', 1, 'WHITE')
                        nextWaveNum = font.render(
                            str((betweenWaveCount // clockTime) + 1), 1, 'WHITE')
                        text.extend([nextWaveText, nextWaveNum])
                        nextWavePos = nextWaveText.get_rect(
                            center=screen.get_rect().center)
                        nextWaveNumPos = nextWaveNum.get_rect(
                            midtop=nextWavePos.midbottom)
                        textposition.extend([nextWavePos, nextWaveNumPos])
                        if wave % 5 == 0:
                            speedUpText = font.render('SPEED UP!', 1, RED)
                            speedUpPos = speedUpText.get_rect(
                                midtop=nextWaveNumPos.midbottom)
                            text.append(speedUpText)
                            textposition.append(speedUpPos)
                    elif betweenWaveCount == 0:
                        if wave % 5 == 0:
                            speed += 0.5
                            monstersThisWave = 10
                            monstersLeftThisWave = Monster.numOffScreen = monstersThisWave 
                        else:
                            monstersThisWave *= 2
                            monstersLeftThisWave = Monster.numOffScreen = monstersThisWave 
                        if wave == 1:            
                            Monster.pool.add([Grey(screen_size) for _ in range(5)])
                        if wave == 2:
                            Monster.pool.add([Blue(screen_size) for _ in range(5)])
                        if wave == 3:
                            Monster.pool.add([Pink(screen_size) for _ in range(5)])
                        if wave == 4:
                            Monster.pool.add(boss)                 
                        if wave >= 5:
                            monstersThisWave = 10
                            Monster.pool.remove(boss)
                        wave += 1
                        betweenWaveCount = betweenWaveTime

                textOverlays = zip(text, textposition)

            # moving field - Resize windowSize
                field1Rect.y += int(2 * ratio)
                field2Rect.y += int(2 * ratio)
                if field1Rect.y >= screen_size:
                    field1Rect.midbottom = field2Rect.midtop
                if field2Rect.y >= screen_size:
                    field2Rect.midbottom = field1Rect.midtop
                
                field_size = (round(field1.get_width() * ratio), round(field1.get_height() * ratio))
                screen.blit(pygame.transform.scale(field1, field_size), (0,field1Rect.y))
                screen.blit(pygame.transform.scale(field2, field_size), (0,field2Rect.y))

            # Update and draw all sprites and text                                   
                allsprites.update(screen_size)
                allsprites.draw(screen)
                alldrawings.update()
                for txt, pos in textOverlays:
                    screen.blit(txt, pos)

            # Update life
                life1Rect.topleft = wavePos.bottomleft
                life2Rect.topleft = wavePos.bottomleft
                life3Rect.topleft = wavePos.bottomleft

                life_size = (round(life1.get_width() * ratio), round(life1.get_height() * ratio))
                if player.life == 3:
                    screen.blit(pygame.transform.scale(life3, life_size), life3Rect)
                elif player.life == 2:
                    screen.blit(pygame.transform.scale(life2, life_size), life2Rect)
                elif player.life == 1:
                    screen.blit(pygame.transform.scale(life1, life_size), life1Rect)
                        
            # Update Boss life 
                Bosslife0Rect.topleft = bHealthPos.topright
                Bosslife1Rect.topleft = bHealthPos.topright
                Bosslife2Rect.topleft = bHealthPos.topright
                Bosslife3Rect.topleft = bHealthPos.topright
                Bosslife4Rect.topleft = bHealthPos.topright
                Bosslife5Rect.topleft = bHealthPos.topright               
                
                boss_life_size = (round(Bosslife0.get_width() * ratio * 0.3), round(Bosslife0.get_height() * ratio * 0.5))  
                
                if boss.health <= 10 and boss.health > 8:
                    screen.blit(pygame.transform.scale(Bosslife5, boss_life_size), Bosslife5Rect)
                elif boss.health <= 8 and boss.health > 6:
                    screen.blit(pygame.transform.scale(Bosslife4, boss_life_size), Bosslife4Rect)
                elif boss.health <= 6 and boss.health > 4:
                    screen.blit(pygame.transform.scale(Bosslife3, boss_life_size), Bosslife3Rect)
                elif boss.health <= 4 and boss.health > 2:
                    screen.blit(pygame.transform.scale(Bosslife2, boss_life_size), Bosslife2Rect)
                elif boss.health <= 2 and boss.health > 0:
                    screen.blit(pygame.transform.scale(Bosslife1, boss_life_size), Bosslife1Rect)
                elif boss.health == 0:
                    screen.blit(pygame.transform.scale(Bosslife0, boss_life_size), Bosslife0Rect)     
   

                pygame.display.flip()

            name = ''
            nameBuffer = []


    #########################
    #    After Game Loop    #
    #########################

        while True:
            # 바로 점수 저장되게
            clock.tick(clockTime)
        # name 입력받는 부분 지우기
        # Event Handling
            for event in pygame.event.get():
                if (event.type == pygame.QUIT and event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE): # 게임 창 끔
                        return False
                # Resize windowSize
                elif (event.type == pygame.VIDEORESIZE):
                        screen_size = min(event.w, event.h)
                        if screen_size <= 400:
                            screen_size = 400
                        if screen_size >= 900:
                            screen_size = 900
                        screen = pygame.display.set_mode((screen_size, screen_size), HWSURFACE|DOUBLEBUF|RESIZABLE)
                        ratio = (screen_size / 600)
                        font = pygame.font.Font(None, round(36*ratio))
                elif (event.type == pygame.KEYDOWN # 키보드를 눌렀다 떼고
                    and event.key == pygame.K_RETURN # 엔터키
                    ): # 
                    Database().setScore(Var.user_id,score)
                    Database().setCoins(Var.user_id,score)
                    return True

            
        # moving field         
            field1Rect.y += int(2 * ratio)
            field2Rect.y += int(2 * ratio)

            if field1Rect.y >= screen_size:
                field1Rect.midbottom = field2Rect.midtop
            if field2Rect.y >= screen_size:
                field2Rect.midbottom = field1Rect.midtop
                
            field_size = (round(field1.get_width() * ratio), round(field1.get_height() * ratio))
            screen.blit(pygame.transform.scale(field1, field_size), (0,field1Rect.y))
            screen.blit(pygame.transform.scale(field2, field_size), (0,field2Rect.y))

            # Update and draw all sprites
            allsprites.update(screen_size)
            allsprites.draw(screen)
            alldrawings.update()
            for txt, pos in textOverlays:
                screen.blit(txt, pos)

            pygame.display.flip()