import pygame
import time
import math
import random
import os
import json
import io
pygame.init()

import map_templates

from engine.sources import *
from engine.units import *
from engine.navigation import *
from engine.transforms import *

import engine.nicholas_swift_astar

from datetime import datetime

game_timers_list=[]

def CreateGame(screen_resolution=(640, 480), content_directory=".", debuging_screen=False, debuging_map=False, debuging_gamemx=False):

    gc=GameContext.get()
    print("CreateGame:")
    print("gc:",gc)

    GameContext.set(cGame(screen_resolution,content_directory))
    gc=GameContext.get()

    gc.DEBUG_SCREEN = debuging_screen
    gc.DEBUG_MAP = debuging_map
    gc.DEBUG_SHOW_GAME_MATRIX = debuging_gamemx

    gc.init_values()
    
    return gc

class cGame():

    map_navigation=None
    transforms=None

    def __init__(self, screen_resolution=(640, 480), content_directory="."):
        self.DEBUG_SCREEN = False
        self.DEBUG_MAP = False
        self.DEBUG_SHOW_GAME_MATRIX = False

        self.pause=False

        self.content_directory=content_directory

        self.screen_resolution = screen_resolution

        self.font_default = pygame.font.Font(self.content_directory+"/Terminus.ttf", 12)
        self.font_8 = pygame.font.Font(self.content_directory+"/Terminus.ttf", 8)

        random.seed(1)

    def init_values(self):
        self.map_navigation = map_navigation()
        self.transforms = transforms(self.map_navigation)
        self.screen_surf = pygame.Surface(self.screen_resolution)

        SourcesLoader(self.content_directory,"sprites_sheet.png")
        SourcesLoader.load_game_objects("game_objects.json")
        SourcesLoader.load_blocks("blocks.json")

        print("init source_player_lvl_list")

        GameContext.source_player_lvl_list=[
            SourcesLoader.game_sources.player00,
            SourcesLoader.game_sources.player01,
            SourcesLoader.game_sources.player02,
            SourcesLoader.game_sources.player03
        ]
        print("source_player_lvl_list:",id(GameContext),id(GameContext.source_player_lvl_list))

        if self.DEBUG_SCREEN:
            self.debug_screen_surf = pygame.Surface((512,480))

        if self.DEBUG_MAP:
            self.debug_map_surf = pygame.Surface(self.screen_resolution,flags=pygame.SRCALPHA)

        if self.DEBUG_SHOW_GAME_MATRIX:
            self.debug_gamemx_surf = pygame.Surface((512,480))

    def reset_stats(self):
        self.world_object_list = []
        self.bullet_object_list = []
        self.map_object_list = []
        self.effect_object_list = []
        self.units = []
        self.players = []

        self.spawn_points = []
        self.spawn_list = []

        self.total_enemy_count=0

    def load_savegame(self, fname):
        json_file = io.open(fname, "rb")
        json_str = json_file.read()
        json_data = json.loads(json_str)
        json_file.close()
        return json_data

    def reset_map(self):
        save_obj=None

        if os.path.exists("save.json"):
            save_obj=self.load_savegame("save.json")
        else:
            save_obj=map_templates.map00

        self.map_navigation.fill(save_obj["map"].copy())

        return save_obj

    def reset_units(self):

        save_obj=self.reset_map()

        world_map=self.map_navigation.map_src

        for unit_obj in save_obj["units"]:
            if unit_obj["type"]=="player" or unit_obj["type"]=="player" or unit_obj["type"]=="player":
                player=cPlayerUnit(unit_obj["type"], unit_obj["lvl"], (unit_obj["pos"][0]*BLOCK_SIZE)+BLOCK_SIZE, (unit_obj["pos"][1]*BLOCK_SIZE)+BLOCK_SIZE)
                player.direction=unit_obj["dir"]
                player.action_move("stop")
                player.update_animation()
                self.players.append(player)
                self.world_object_list.append(player)
            elif unit_obj["type"]=="tank00":
                unit = cUnit("tank00_"+str(self.total_enemy_count+1), SourcesLoader.game_sources.tank00, (unit_obj["pos"][0]*BLOCK_SIZE)+BLOCK_SIZE, (unit_obj["pos"][1]*BLOCK_SIZE)+BLOCK_SIZE)
                unit.direction=unit_obj["dir"]
                unit.action_move("stop")
                unit.update_animation()
                self.units.append(unit)
                self.total_enemy_count+=1

                self.world_object_list.append(unit)

        self.spawn_list = []
        for wi in save_obj["spawn_list"]:
            wi["start_time"]=time.time()
            self.spawn_list.append(wi)

        for imr in range(0, len(world_map)):
            for imc in range(0, len(world_map[0])):
                px = imc*BLOCK_SIZE
                py = imr*BLOCK_SIZE

                cell_flag=world_map[imr][imc]

                if cell_flag == 1:
                    self.map_object_list.append(sprites.cMapSprite(px, py, SourcesLoader.map_sources.blocks.bricks.surf, SourcesLoader.map_sources.blocks.bricks.hp))
                elif cell_flag == 2:
                    self.map_object_list.append(sprites.cMapSprite(px, py, SourcesLoader.map_sources.blocks.steel.surf, SourcesLoader.map_sources.blocks.steel.hp))
                elif cell_flag == 100:
                    self.map_object_list.append(sprites.cMapSprite(px, py, SourcesLoader.map_sources.blocks.base.surf, SourcesLoader.map_sources.blocks.base.hp))
                elif cell_flag == -7:
                    self.spawn_points.append((imc, imr))
                    
        if len(self.players):
            self.players[0].speed = 1.5
            self.players[0].hp = 1000

        self.frame_counter = 0
        self.fps = 0
        self.frame_checker_start_time = time.time()

        for obj in self.world_object_list:
            obj.self_point_cell_value=self.map_navigation.astar_map[obj.self_point[1]][obj.self_point[0]]
            self.map_navigation.astar_map[obj.self_point[1]][obj.self_point[0]]=-9

    def spawn_unit(self,spawn_pos):
        unit = cUnit("tank00_"+str(self.total_enemy_count+1), SourcesLoader.game_sources.tank00, spawn_pos[0], spawn_pos[1])

        unit.wait_time=0.5
        unit.start_wait_time=time.time()

        self.units.append(unit)
        self.total_enemy_count+=1
        self.world_object_list.append(unit)

        self.effect_object_list.append(
            sprites.cAnimationSprite(
                SourcesLoader.game_sources.tank_spawn.drawn,
                spawn_pos[0], spawn_pos[1]
            )
        )

    def game_timer_update(self):
        ct=time.time()

        rm_list=[]
        for timer_item in game_timers_list:
            if ct-timer_item.start>=timer_item.interval:
                if timer_item.callback!=None:
                    timer_item.callback()
                    if timer_item.once:
                        rm_list.append(timer_item)

        for ri in rm_list:
            game_timers_list.remove(ri)

    def game_event(self, event):
        if event["type"] == "destroyed":
            if event["object_type"] == "map_item":
                if event["object"] in self.map_object_list:
                    map_object = event["object"]
                    self.map_object_list.remove(event["object"])

                    self.map_navigation.remove_cell_by_position(map_object.pos.x, map_object.pos.y)

            elif event["object_type"] == "unit":
                if event["object"] in self.world_object_list:
                    map_object = event["object"]
                    self.world_object_list.remove(event["object"])

                    if isinstance(event["object"], cUnit):
                        if event["object"] in self.units:

                            if event["object"].self_point_cell_value!=None:
                                self.map_navigation.astar_map[event["object"].self_point[1]][event["object"].self_point[0]]=event["object"].self_point_cell_value

                            self.units.remove(event["object"])

                            self.spawn_list.append({"start_time":time.time(),"wait":1.0,"name":"tank00","pos":None})

                    elif isinstance(event["object"], cPlayerUnit):
                        if event["object"] in self.players:
                            self.players.remove(event["object"])

                    self.effect_object_list.append(
                        sprites.cAnimationSprite(
                            SourcesLoader.game_sources.tank_explosion.drawn,
                            event["object"].pos.x,event["object"].pos.y
                        )
                    )

            elif event["object_type"] == "bullet":
                if event["object"] in self.bullet_object_list:
                    self.bullet_object_list.remove(event["object"])

                    self.effect_object_list.append(
                        sprites.cAnimationSprite(
                            SourcesLoader.game_sources.bullet_explosion.drawn,
                            event["object"].pos.x,event["object"].pos.y
                        )
                    )

            elif event["object_type"] == "effect":
                if event["object"] in self.effect_object_list:
                    self.effect_object_list.remove(event["object"])

            del event["object"]

        elif event["type"] == "unit_event":

            if event["object_type"] == "unit_path":
                event["object"]["sender"].capturred_player(event["object"]["success"],event["object"]["path"],event["object"]["action_args"])
            elif event["object_type"] == "unit_spawn":
                spawn_pos=None
                if event["spawn_info"]["pos"]!=None:
                    sp=event["spawn_info"]["pos"]
                    spawn_pos=((sp[0]*BLOCK_SIZE)+BLOCK_SIZE,(sp[1]*BLOCK_SIZE)+BLOCK_SIZE)
                    
                else:
                    spawn_points=self.spawn_points.copy()
                    for ui in range(0,len(self.units)):
                        u=self.units[ui]
                        for si in range(0,len(spawn_points)):
                            if u.self_point==spawn_points[si]:
                                spawn_points.pop(si)
                                break
                    
                    if len(spawn_points)!=0:
                        sp=spawn_points[random.randint(0, len(spawn_points)-1)]
                        spawn_pos=((sp[0]*BLOCK_SIZE)+BLOCK_SIZE,(sp[1]*BLOCK_SIZE)+BLOCK_SIZE)

                if spawn_pos:
                    self.spawn_unit(spawn_pos)
                    self.spawn_list.remove(event["spawn_info"])
                else:
                    event["spawn_info"]["start_time"]=time.time()

            elif event["object_type"] == "hit":
                
                event["object"].hp -= 1

                if event["object"].type == "player":
                    event["object"].hits_count+=1
                    
                if event["object"].hp <= 0:
                    GameContext.event_list.append({"type": "destroyed", "object_type": "unit", "object": event["object"], "killer":event["shooter"]})
                    GameContext.event_list.append({"type": "timer", "object_type": "unit", "object": event["object"], "killer":event["shooter"]})

    def shot(self, shooter, x, y, direction):

        ds = {
            "up": Vector2(0.0, -1.0),
            "right": Vector2(1.0, 0.0),
            "down": Vector2(0.0, 1.0),
            "left": Vector2(-1.0, 0.0)
        }

        bs = sprites.cBulletSprite(shooter.pos.x, shooter.pos.y, SourcesLoader.game_sources.bullet.drawn[direction], shooter)

        bs.velocity = ds[direction]

        bs.start_pos = bs.pos
        bs.target_pos = bs.pos+bs.velocity*shooter.bullet_speed

        self.bullet_object_list.append(bs)

    def draw_objects(self, objects_list):

        for obj in objects_list:

            if isinstance(obj, sprites.cUnitSprite) and not obj.is_stay:
                obj.update_animation()

            self.screen_surf.blit(obj.surf, ((obj.pos.x-(obj.w/2.0))+obj.offs.x, (obj.pos.y-(obj.h/2.0))+obj.offs.y))

            if self.DEBUG_MAP:
                pygame.draw.line(self.debug_map_surf, (255, 0, 0, 100), [obj.pos.x-(obj.w/2), obj.pos.y], [obj.pos.x+(obj.w/2), obj.pos.y], 1)
                pygame.draw.line(self.debug_map_surf, (255, 0, 0, 100), [obj.pos.x, obj.pos.y-(obj.h/2)], [obj.pos.x, obj.pos.y+(obj.h/2)], 1)

                radius = 1
                if hasattr(obj, "radius") and obj.radius:
                    radius = int(obj.radius)

                pygame.draw.circle(
                    self.debug_map_surf,
                    (0, 0, 127, 255),
                    (int(obj.pos.x), int(obj.pos.y)), radius, 1
                )

    def player_action(self):
        pass

    def update(self):

        if time.time()-self.frame_checker_start_time >= 1.0:
            self.frame_checker_start_time = time.time()
            self.fps = self.frame_counter
            self.frame_counter = -1
        self.frame_counter += 1

        if self.pause:return self.screen_surf

        self.screen_surf.fill((0, 0, 0))

        if len(self.spawn_list)>0:
            for si in self.spawn_list:
                if si["start_time"]!=None and time.time()-si["start_time"]>=si["wait"]:
                    si["start_time"]=None
                    GameContext.event_list.append({"type": "unit_event", "object_type": "unit_spawn", "spawn_info":si})

        for player in self.players:
            for action in player.actions:

                if action=="right":
                    player.action_move("right")
                elif action=="right_step":
                    player.action_move("left")
                elif action=="left":
                    player.action_move("left")
                elif action=="up":
                    player.action_move("up")
                elif action=="down":
                    player.action_move("down")
                elif action=="stop":
                    player.action_move("stop")

                if action=="shot" and time.time()-player.shot_time > player.shot_time_interval:
                    player.shot_time = time.time()
                    self.shot(player, player.pos.x+(player.w/2)-1, player.pos.y+(player.h/2)-1, player.direction)

            player.actions=[]
            player.collide_status=False

        self.transforms.update_transforms_collide(self.world_object_list)

        for bullet in self.bullet_object_list:
            self.transforms.update_transform(bullet)
        
        self.transforms.update_bullet_collides(self.bullet_object_list,self.world_object_list)
        self.transforms.update_bullet_collides(self.bullet_object_list,self.map_object_list)
        self.transforms.update_bullet_collides(self.bullet_object_list,self.bullet_object_list)

        self.game_timer_update()

        GameContext.event_list_locker.acquire()
        while len(GameContext.event_list) > 0:
            self.game_event(GameContext.event_list.pop())
        GameContext.event_list_locker.release()

        for unit_obj in self.units:
            unit_obj.update_behavior()

        for i in self.map_object_list:
            self.screen_surf.blit(i.surf, (i.pos.x, i.pos.y))

        self.draw_objects(self.bullet_object_list)
        self.draw_objects(self.world_object_list)

        for obj in self.effect_object_list:
            if isinstance(obj, sprites.cAnimationSprite):
                obj.update()

            self.screen_surf.blit(obj.surf, ((obj.pos.x-(obj.w/2.0))+obj.offs.x, (obj.pos.y-(obj.h/2.0))+obj.offs.y))

        if self.DEBUG_SCREEN:
            dbg_screen_x = 1

            self.debug_screen_surf.fill((0, 0, 127, 255))

            self.debug_screen_surf.blit(self.font_default.render(str(self.fps)+" fps", 1, (0, 255, 0)), (dbg_screen_x, 10))

            yl = 24
            for unit in self.world_object_list:
                #if isinstance(unit,cUnitSprite):
                #   self.self.debug_screen_surf.blit(self.font_default.render(str(unit.self_point[0])+" "+str(unit.self_point[1])+" "+str(Vector2Length(unit.velocity)), 1, (0, 255, 0)), (self.screen_resolution[0]-145, yl))
                #   yl+=10

                if isinstance(unit, sprites.cUnitSprite):
                    self.debug_screen_surf.blit(self.font_default.render(unit.name, 1, (0, 255, 0)), (dbg_screen_x, yl))
                    self.debug_screen_surf.blit(self.font_default.render(str(unit.self_point[0])+"x"+str(unit.self_point[1]), 1, (0, 255, 0)), (dbg_screen_x+60, yl))
                    self.debug_screen_surf.blit(self.font_default.render(unit.direction, 1, (0, 255, 0)), (dbg_screen_x+100, yl))
                    #
                    yl += 10

                    if hasattr(unit, "behavior_action"):
                        self.debug_screen_surf.blit(self.font_default.render(str(unit.is_astar_stay), 1, (0, 255, 0)), (dbg_screen_x, yl))
                        self.debug_screen_surf.blit(self.font_default.render(unit.behavior_action, 1, (0, 255, 0)), (dbg_screen_x+36, yl))
                        print(unit.is_astar_stay,unit.behavior_action)

                        if unit.behavior_action=="wait_capture":
                            st=None
                            if unit.start_waiting_capture_time!=None:
                                st=time.time()-unit.start_waiting_capture_time
                            self.debug_screen_surf.blit(self.font_default.render(str(st), 1, (0, 255, 0)), (dbg_screen_x+165, yl))
                            self.debug_screen_surf.blit(self.font_default.render(str(unit.thread_locked), 1, (0, 255, 0)), (dbg_screen_x+300, yl))
                        else:
                            self.debug_screen_surf.blit(self.font_default.render(unit.behavior_subaction, 1, (0, 255, 0)), (dbg_screen_x+250, yl))
                        #self.debug_screen_surf.blit(self.font_default.render(str(unit.is_player_in_view()), 1, (0, 255, 0)), (dbg_screen_x+300, yl))
                        
                        if unit.move_to_point:
                            yl += 10
                            self.debug_screen_surf.blit(self.font_default.render(str(unit.self_point)+"x"+str(unit.move_to_point), 1, (0, 255, 0)), (dbg_screen_x, yl))                            

                    yl += 16
                    pygame.draw.line(self.debug_screen_surf, (0, 255, 0, 255), (dbg_screen_x, yl), (dbg_screen_x+640, yl), 1)

                    yl += 4

        if self.DEBUG_MAP:
            for unit_obj in self.units:
                unit_obj.draw_path(self.debug_map_surf)

            #print("open",engine.astar.Debug.open)
            #print("close",engine.astar.Debug.close)
            '''for p in engine.astar.Debug.open:
                pygame.draw.circle(
                    self.debug_map_surf,
                    (0,0,255,255),
                    ((p.position[0]*BLOCK_SIZE)+int(BLOCK_SIZE), (p.position[1]*BLOCK_SIZE)+int(BLOCK_SIZE)), 2,
                    1
                )
            for p in engine.astar.Debug.close:
                pygame.draw.circle(
                    self.debug_map_surf,
                    (0,255,0,255),
                    ((p.position[0]*BLOCK_SIZE)+int(BLOCK_SIZE), (p.position[1]*BLOCK_SIZE)+int(BLOCK_SIZE)), 2,
                    1
                )'''

            for ir in range(0, self.map_navigation.astar_rows+1):
                pygame.draw.line(
                    self.debug_map_surf,
                    (255, 255, 255, 255),
                    (0,(ir*BLOCK_SIZE)+int(BLOCK_SIZE/2)),
                    (self.map_navigation.astar_cells*BLOCK_SIZE+BLOCK_SIZE,(ir*BLOCK_SIZE)+int(BLOCK_SIZE/2)),
                    1
                )

                for ic in range(0, self.map_navigation.astar_cells+1):
                    pygame.draw.line(
                        self.debug_map_surf,
                        (255, 255, 255, 255),
                        ((ic*BLOCK_SIZE)+int(BLOCK_SIZE/2),0),
                        ((ic*BLOCK_SIZE)+int(BLOCK_SIZE/2),self.map_navigation.astar_rows*BLOCK_SIZE+BLOCK_SIZE),
                        1
                    )

                    if ir<self.map_navigation.astar_rows and ic<self.map_navigation.astar_cells and self.map_navigation.astar_map[ir][ic]!=0:
                        pygame.draw.circle(
                            self.debug_map_surf,
                            (255, 0, 0, 255),
                            ((ic*BLOCK_SIZE)+int(BLOCK_SIZE), (ir*BLOCK_SIZE)+int(BLOCK_SIZE)), 2,
                            1
                        )

            pygame.draw.line(
                self.debug_map_surf,
                (255, 0, 0, 255),
                (0,0),
                (0,self.map_navigation.astar_rows*BLOCK_SIZE+BLOCK_SIZE),
                1
            )

            pygame.draw.line(
                self.debug_map_surf,
                (255, 0, 0, 255),
                (self.map_navigation.astar_cells*BLOCK_SIZE+BLOCK_SIZE,0),
                (self.map_navigation.astar_cells*BLOCK_SIZE+BLOCK_SIZE,self.map_navigation.astar_rows*BLOCK_SIZE+int(BLOCK_SIZE/2)),
                1
            )

            def _dbg_draw_point(p,color = (255, 255, 255, 255),offset_x=0,offset_y=0):
                pygame.draw.circle(
                        self.debug_map_surf,
                        color,
                        [(p[0]*BLOCK_SIZE)+BLOCK_SIZE+offset_x, (p[1]*BLOCK_SIZE)+BLOCK_SIZE+offset_y], 2,
                        1
                )
                #self.debug_map_surf.blit(self.font_default.render(str(p[0])+":"+str(p[1]), 1, (0, 255, 0)), ((p[0]*BLOCK_SIZE)+BLOCK_SIZE+offset_x, (p[1]*BLOCK_SIZE)+BLOCK_SIZE+offset_y))

            def _dbg_draw_line(pa,pb,color = (255, 255, 255, 255)):
                pygame.draw.line(
                        self.debug_map_surf,
                        color,
                        [(pa[0]*BLOCK_SIZE)+BLOCK_SIZE,(pa[1]*BLOCK_SIZE)+BLOCK_SIZE],
                        [(pb[0]*BLOCK_SIZE)+BLOCK_SIZE,(pb[1]*BLOCK_SIZE)+BLOCK_SIZE],
                        1
                    )

            def _dbg_draw_lines_array(la,color = (255, 255, 255, 255)):
                for line in la:
                    pygame.draw.line(
                        self.debug_map_surf,
                        color,
                        [(line[0][0]*BLOCK_SIZE)+BLOCK_SIZE,(line[0][1]*BLOCK_SIZE)+BLOCK_SIZE],
                        [(line[1][0]*BLOCK_SIZE)+BLOCK_SIZE,(line[1][1]*BLOCK_SIZE)+BLOCK_SIZE],
                        1
                    )

                    #_dbg_draw_point(line[0])
                    #_dbg_draw_point(line[1])

            for line in self.map_navigation.collide_list:
                #_dbg_draw_line(line[0],line[1])
                #_dbg_draw_point(line[0])
                #_dbg_draw_point(line[1])
                color = (255, 255, 255, 255)
                pygame.draw.line(
                        self.debug_map_surf,
                        color,
                        [line[0][0],line[0][1]],
                        [line[1][0],line[1][1]],
                        1
                    )

        return self.screen_surf

    def debug_draw_game_matrix(self):
        
        self.debug_gamemx_surf.fill((0, 0, 127, 255))

        scale=6
        rows_num=self.map_navigation.astar_rows
        cells_num=self.map_navigation.astar_cells

        for ir in range(0, rows_num):
            for ic in range(0, cells_num):

                color=(255,255,255)

                if self.map_navigation.astar_map[ir][ic]>0:
                    color=(255,0,0)
                elif self.map_navigation.astar_map[ir][ic]<0:
                    color=(0,0,255)

                pygame.draw.rect(self.debug_gamemx_surf,color,(ic*scale,ir*scale,scale,scale))

    def debug_action(self, action):

        if action == 5:

            save_obj={}

            save_obj["units"]=[]
            for unit_obj in self.units:
                print(unit_obj.name,unit_obj.self_point)
                save_obj["units"].append({"type":unit_obj.type,"pos":unit_obj.self_point,"dir":unit_obj.direction})

            for unit_obj in self.players:
                print(unit_obj.name,unit_obj.self_point)
                save_obj["units"].append({"type":unit_obj.type,"lvl":unit_obj.lvl,"pos":unit_obj.self_point,"dir":unit_obj.direction})

            save_obj["spawn_list"]=self.spawn_list

            save_obj["map"]=[]

            for ri in range(0, self.map_navigation.map_rows):
                row=[]
                for ci in range(0, self.map_navigation.map_cells):
                    row.append(int(self.map_navigation.map_src[ri][ci]))
                save_obj["map"].append(row)

            pf=io.open("save.json", "wb")
            pf.write(json.dumps(save_obj).encode())
            pf.close()

        return