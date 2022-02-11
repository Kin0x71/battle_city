import pygame
import time
import sys

import battle_city

from battle_city.game import *

def main():
    pygame.init()

    pygame_display=pygame.display.set_mode((1024, 480))

    game=CreateGame((640, 480),"battle_city/battle_city_content", debuging_screen=False, debuging_map=False, debuging_gamemx=False)

    game.DEBUG_MAP=False
    game.DEBUG_SCREEN=False

    game.reset_stats()
    game.reset_map()
    game.reset_units()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return

            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_r and e.mod:
                    pass
                    #print("restart")
                    #del game.GameContext.context
                    #game.GameContext.context=None
                    #game=game.CreateGame((640, 480),"battle_city_content", debuging_screen=True, debuging_map=True)
                elif e.key == pygame.K_1:
                    game.debug_action(1)
                elif e.key == pygame.K_2:
                    game.debug_action(2)
                elif e.key == pygame.K_3:
                    game.debug_action(3)
                elif e.key == pygame.K_4:
                    game.debug_action(4)
                elif e.key == pygame.K_F1:
                    game.DEBUG_SCREEN = not game.DEBUG_SCREEN
                elif e.key == pygame.K_F2:
                    game.DEBUG_MAP = not game.DEBUG_MAP
                elif e.key == pygame.K_F3:
                    game.DEBUG_SHOW_GAME_MATRIX = not game.DEBUG_SHOW_GAME_MATRIX
                elif e.key == pygame.K_F4:
                    game.reset_stats()
                    game.reset_map()
                    game.reset_units()
                elif e.key == pygame.K_F5:
                    game.pause = not game.pause

        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            game.players[0].actions.append("up")
        elif keys[pygame.K_a]:
            game.players[0].actions.append("left")
        elif keys[pygame.K_s]:
            game.players[0].actions.append("down")
        elif keys[pygame.K_d]:
            game.players[0].actions.append("right")
        else:
            game.players[0].actions.append("stop")
        
        if keys[pygame.K_SPACE]:
            game.players[0].actions.append("shot")

        game_surf=game.update()

        game_surf_size=game_surf.get_size()
        
        pygame_display.blit(pygame.transform.scale(game_surf, (game_surf_size[0]*2, game_surf_size[1]*2)), (0, 0))

        if game.DEBUG_MAP:
            debug_map_surf_size=game.debug_map_surf.get_size()
            pygame_display.blit(pygame.transform.scale(game.debug_map_surf, (debug_map_surf_size[0]*2, debug_map_surf_size[1]*2)), (0, 0))
        
        if game.DEBUG_SHOW_GAME_MATRIX:
            game.debug_draw_game_matrix()
            pygame_display.blit(game.debug_gamemx_surf, (640, 0))

        if game.DEBUG_SCREEN:
            pygame_display.blit(game.debug_screen_surf, (640, 0))
        
        pygame.display.update()

if __name__ == "__main__":
    main()
