import pygame

import engine.sprites as sprites
from engine.behavior import *
from defines import *

class cUnit(sprites.cUnitSprite,cUnitBehavior):
    def __init__(self, name, sprites_list, x=0, y=0):
        super(cUnit, self).__init__(name, sprites_list, x, y)

        self.type="tank00"
        self.hp = 1
        self.speed=0.5

        self.path = []
        self.target_point = (0, 0)
        self.move_to_point = (0, 0)

        self.shot_time = 0.0
        self.shot_time_interval = 0.5
        self.bullet_speed = 1.0

        self.debug_info = None

        self.behavior_action = None
        self.behavior_subaction = None

        self.astar_last_update = 0.0
        self.last_step_dist = None
        self.target_plyer_index = 0

        self.self_point_cell_value=None

    def on_collide(self, collider):
        if isinstance(collider, sprites.cBulletSprite):

            if isinstance(collider.shooter, cUnit):return

            GameContext.event_list.append({"type": "unit_event", "object_type": "hit", "object": self, "shooter":collider.shooter})
       
    def draw_path(self, surf):
        
        if self.path!=None and len(self.path)>0:
            color = (255, 0, 255, 255)

            if self.behavior_subaction == "move_straight_path":
                color = (0, 255, 0, 255)

            last_pos = self.path[0]
            for i in range(1, len(self.path)):
                pos = self.path[i]

                pygame.draw.line(surf, color, [(last_pos[0]*BLOCK_SIZE)+BLOCK_SIZE, (last_pos[1]*BLOCK_SIZE)+BLOCK_SIZE], [(pos[0]*BLOCK_SIZE)+BLOCK_SIZE, (pos[1]*BLOCK_SIZE)+BLOCK_SIZE], 3)

                last_pos = pos

            for p in self.path:
                pygame.draw.circle(
                    surf,
                    (255, 0, 0, 255),
                    [(p[0]*BLOCK_SIZE)+BLOCK_SIZE, (p[1]*BLOCK_SIZE)+BLOCK_SIZE], 2,
                    1
                )

        surf.blit(GameContext.context.font_default.render(self.name, 1, (255, 255, 255)), [(self.self_point[0]*BLOCK_SIZE), (self.self_point[1]*BLOCK_SIZE)])
        
        pygame.draw.circle(
            surf,
            (0, 0, 255, 255),
            [(self.self_point[0]*BLOCK_SIZE)+BLOCK_SIZE, (self.self_point[1]*BLOCK_SIZE)+BLOCK_SIZE], 2,
            1
        )

        if self.move_to_point:
            pygame.draw.line(surf, (255, 0, 0, 255), [(self.self_point[0]*BLOCK_SIZE)+BLOCK_SIZE, (self.self_point[1]*BLOCK_SIZE)+BLOCK_SIZE], [(self.move_to_point[0]*BLOCK_SIZE)+BLOCK_SIZE, (self.move_to_point[1]*BLOCK_SIZE)+BLOCK_SIZE], 1)
            pygame.draw.circle(
                surf,
                (0, 255, 255, 255),
                [(self.move_to_point[0]*BLOCK_SIZE)+BLOCK_SIZE, (self.move_to_point[1]*BLOCK_SIZE)+BLOCK_SIZE], 2,
                1
            )

class cPlayerUnit(sprites.cUnitSprite):
    lvl=0
    def __init__(self, name, lvl=0, x=0, y=0):
        super(cPlayerUnit, self).__init__(name, GameContext.source_player_lvl_list[lvl], x, y)

        self.type="player"

        self.hp = 1
        self.hits_count = 0

        self.shot_time = 0.0
        self.shot_time_interval = 0.5
        self.bullet_speed = 1.0

        self.lvl=lvl

        self.self_point_cell_value=None

        self.collide_status=False

        self.actions=[]

    def set_lvl(self,lvl):
        self.lvl = lvl
        if self.lvl < 0:
            self.lvl=0
        elif self.lvl > len(GameContext.source_player_lvl_list)-1:
            self.lvl = len(GameContext.source_player_lvl_list)-1

        self.anim_groups = GameContext.source_player_lvl_list[self.lvl].drawn
        self.update_animation()

        self.speed=player_lvl_states[self.lvl]["speed"]
        self.shot_time_interval=player_lvl_states[self.lvl]["shot_time_interval"]
        self.bullet_speed=player_lvl_states[self.lvl]["bullet_speed"]

    def action_move(self, direction):
        super(cPlayerUnit, self).action_move(direction)

    def on_collide(self, collider):
        if isinstance(collider, sprites.cBulletSprite):

            if isinstance(collider.shooter, cPlayerUnit):return

            GameContext.event_list.append({"type": "unit_event", "object_type": "hit", "object": self, "shooter":collider.shooter})
        else:
            self.collide_status=True
