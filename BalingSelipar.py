import os
import pygame
import time
import States
import GameObjects
import random

G = 100
SCREENSIZE = [1200, 800]

def initialize_enemies(enemy_list, stage):
    move_speed = 1
    #Create x-axis enemies
    for i in range(stage):
        enemy_list.append(GameObjects.Obstacle([random.randrange(SCREENSIZE[0]/2, SCREENSIZE[0], 200), random.randrange(SCREENSIZE[1]/2, SCREENSIZE[1], 200)], stage*move_speed, 90))
    #Create y-axis enemies
    for i in range(stage):
        enemy_list.append(GameObjects.Obstacle([random.randrange(SCREENSIZE[0]/2, SCREENSIZE[0], 200), random.randrange(SCREENSIZE[1]/2, SCREENSIZE[1], 200)], stage*move_speed, 0))

def main():
    pygame.init()
    
    #Setup bgm for game
    bgm_file = GameObjects.resource_path(os.path.join("mark","assets", "Baling_Selipar_bgm.mp3"))
    pygame.mixer.init()
    pygame.mixer.music.load(bgm_file)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

    screen = pygame.display.set_mode(SCREENSIZE)
    background_image = pygame.transform.scale(GameObjects.load_image("balingselipar_background.gif").convert(), SCREENSIZE)

    retry = 0
    stage = 1
    initTime = time.time()
    shoot_timer = 0

    objects_dict = dict()
    player_dict = dict()
    enemy_list = []

    state = States.GameState.StartMenu
    keyState = States.KeyState.SpaceKeyReleased    

    menu = GameObjects.Menu(SCREENSIZE)
    dialog = GameObjects.Dialog(SCREENSIZE)
    help_dialog = GameObjects.Dialog(SCREENSIZE)

    timer = GameObjects.Timer()
    clock = pygame.time.Clock()
    
    done = False

    while not done:
        screen.blit(background_image, (0,0))
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): 
                done = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                state = States.GameState.Start
                menu.setVisibility(False)
                dialog.setVisibility(True)

        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_SPACE] == False and keyState == States.KeyState.SpaceKeyPressed:
            keyState = States.KeyState.SpaceKeyReleased

        if state == States.GameState.Start:
            if keystate[pygame.K_SPACE] and keyState == States.KeyState.SpaceKeyReleased:
                state = States.GameState.AngleSelection
                dialog.setVisibility(False)
                if 'AngleLine' not in objects_dict.keys():
                        objects_dict['AngleLine'] = GameObjects.AngleLine(SCREENSIZE)
                objects_dict.get('AngleLine').setVisibility(True)
                print(objects_dict.keys())
                if 'Tower' not in objects_dict.keys():
                    objects_dict['Tower'] = GameObjects.Tower([random.randrange(SCREENSIZE[0]/2, SCREENSIZE[0], 200), random.randrange(SCREENSIZE[1]/2, SCREENSIZE[1], 200)])
                objects_dict.get('Tower').setVisibility(True)
                help_text = ['Move line of attack using up-down directional key.', 'Press ''SPACEBAR'' to lock line of attack.']
                help_dialog = GameObjects.HelpDialog(SCREENSIZE, 'Angle Selection', help_text)
                help_dialog.setVisibility(True)
                keyState = States.KeyState.SpaceKeyPressed

        if state == States.GameState.AngleSelection:
            if keystate[pygame.K_SPACE] and keyState == States.KeyState.SpaceKeyReleased:
                keyState = States.KeyState.SpaceKeyPressed
                state = States.GameState.PowerSelection
                if 'PowerBar' not in objects_dict.keys():
                    objects_dict['PowerBar'] = GameObjects.PowerBar(SCREENSIZE)
                objects_dict.get('PowerBar').setVisibility(True)
                help_text = ['Long press ''SPACEBAR'' to control power gauge.', 'Release ''SPACEBAR'' to release flip flop.']
                help_dialog = GameObjects.HelpDialog(SCREENSIZE, 'Power Selection', help_text)
                help_dialog.setVisibility(True)
            angle = keystate[pygame.K_UP] - keystate[pygame.K_DOWN]
            objects_dict.get('AngleLine').calculateAngle(angle)
            objects_dict.get('AngleLine').updateData()

        if state == States.GameState.PowerSelection:
            if keystate[pygame.K_SPACE] and keyState == States.KeyState.SpaceKeyReleased:
                keyState = States.KeyState.SpaceKeyLongPressed
            if keystate[pygame.K_SPACE] and keyState == States.KeyState.SpaceKeyLongPressed:
                objects_dict.get('PowerBar').updateData()
            if keystate[pygame.K_SPACE] == False and keyState == States.KeyState.SpaceKeyLongPressed:
                state = States.GameState.SlipperReleased
                objects_dict.get('AngleLine').setVisibility(False)
                objects_dict.get('PowerBar').setVisibility(False)
                help_dialog.setVisibility(False)
                if 'Slipper' not in objects_dict.keys():
                    objects_dict['Slipper'] = GameObjects.Selipar()
                objects_dict.get('Slipper').setVisibility(True)
                initTime = time.time()

        if state == States.GameState.SlipperReleased:
            objects_dict.get('Slipper').updateData(objects_dict.get('PowerBar').getLength(), objects_dict.get('AngleLine').getAngle(), time.time()-initTime, G, SCREENSIZE)
            if objects_dict.get('Slipper').get_cord()[0] > SCREENSIZE[0] or objects_dict.get('Slipper').get_cord()[0] < 0 or objects_dict.get('Slipper').get_cord()[1] > SCREENSIZE[1] or objects_dict.get('Slipper').get_cord()[1] < 0:
                state = States.GameState.Start
                objects_dict.get('AngleLine').reset()
                objects_dict.get('PowerBar').reset()
                objects_dict.get('Slipper').reset()
                objects_dict.get('Tower').setVisibility(False)
                retry += 1
                dialog = GameObjects.Dialog(SCREENSIZE, 10, 'Retry: ', retry)
                dialog.setVisibility(True)
                keyState = States.KeyState.SpaceKeyReleased
            if objects_dict.get('Tower').collision_check(objects_dict.get('Slipper'), screen):
                state = States.GameState.TowerDown
                initialize_enemies(enemy_list, stage)
                for item in enemy_list:
                    item.setVisibility(True)
                player_dict['player'] = GameObjects.Player()
                player_dict['bullet'] = GameObjects.Bullet(player_dict.get('player'))
                player_dict.get('player').setVisibility(True)
                help_text = ['Control your character with ''WASD'' keys', 'Control your angle of attack with directional keys.', 'Press ''SPACEBAR'' to ''shoot'' flipflops.', 'Defeat enemies within 10s']
                help_dialog = GameObjects.HelpDialog(SCREENSIZE, 'Stop The Defenders', help_text)
                help_dialog.setVisibility(True)
                timer.setVisibility(True)
                objects_dict.clear()
                shoot_timer = time.time()
                keyState = States.KeyState.SpaceKeyReleased
        
        if state == States.GameState.TowerDown:
            timer.updateData(time.time()-shoot_timer)
            if keystate[pygame.K_SPACE] and keyState == States.KeyState.SpaceKeyReleased and player_dict.get('bullet').is_shot() == False:
                keyState = States.KeyState.SpaceKeyPressed
                player_dict.get('bullet').__init__(player_dict.get('player'))
                player_dict.get('bullet').set_dy_dx()
                player_dict.get('bullet').setVisibility(True)
            angle1 = keystate[pygame.K_UP] - keystate[pygame.K_DOWN]
            angle2 = keystate[pygame.K_LEFT] - keystate[pygame.K_RIGHT]
            move_x = keystate[pygame.K_d] - keystate[pygame.K_a]
            move_y = keystate[pygame.K_s] - keystate[pygame.K_w]
            player_dict.get('player').calculateAngle(angle1, angle2)
            player_dict.get('player').move([move_x, move_y], SCREENSIZE)
            player_dict.get('player').updateData()
            visibility_count = 0
            for enemy in enemy_list:
                if enemy.collision_check(player_dict.get('bullet'), screen):
                    enemy.setVisibility(False)
                    player_dict.get('bullet').setVisibility(False)
                    player_dict.get('bullet').set_shot_state(False)
                if enemy.isVisible() == False:
                    visibility_count += 1
                if visibility_count == len(enemy_list):
                    timer.setVisibility(False)
                    state = States.GameState.Start
                    stage += 1
                    retry = 0
                    dialog = GameObjects.Dialog(SCREENSIZE, 10, 'Nice! Stage: ', stage)
                    dialog.setVisibility(True)
                    help_dialog.setVisibility(False)
                    enemy_list.clear()
                    player_dict.clear()
            if (time.time()-shoot_timer) > 10:
                state = States.GameState.Start
                dialog = GameObjects.Dialog(SCREENSIZE, 10, 'GAME OVER at Stage ', stage)
                stage = 1
                dialog.setVisibility(True)
                enemy_list.clear()
                player_dict.clear()

        menu.update(screen)
        dialog.update(screen)
        help_dialog.update(screen)
        if 'Slipper' in objects_dict:
            objects_dict.get('Slipper').update(screen)    
        if 'Tower' in objects_dict:
            objects_dict.get('Tower').update(screen)
        if 'AngleLine' in objects_dict:
            objects_dict.get('AngleLine').update(screen)
        if 'PowerBar' in objects_dict:
            objects_dict.get('PowerBar').update(screen)
        for enemy in enemy_list:
            enemy.update(screen, SCREENSIZE)
        if len(player_dict) != 0:
            player_dict.get('player').update(screen)
            player_dict.get('bullet').update(player_dict.get('player'), screen, SCREENSIZE)
        timer.update(screen)
        
        pygame.display.update()
        clock.tick(120)
    pygame.quit()

if __name__ == "__main__":
    main()
    pygame.quit()

