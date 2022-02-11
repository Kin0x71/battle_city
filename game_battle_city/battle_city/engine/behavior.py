import time
import threading
import random
import engine.nicholas_swift_astar as astar
print("astar",astar)

import engine.sprites as sprites
from defines import *
from engine.collisions_math import *

class cUnitBehavior:
    wait_time=None
    start_wait_time=None
    wait_stay_player_st=None
    dbg_last_close_list=None
    is_astar_stay=True

    find_failed_checker=0
    taran_moving=False

    def __init__(self):
        self.wait_time=None
        self.start_wait_time=None
        self.start_waiting_capture_time=None
        self.thread_locked=False

        self.taran_moving=False

    def capturred_player(self, sucess, path, action_args):

        self.start_waiting_capture_time=None

        def _reset_action():
            self.behavior_action = None
            self.behavior_subaction = None
            self.move_to_point = None
            self.path = None
            self.action_move("stop")

        def _wait_action():
            self.wait_time=1.0
            self.start_wait_time=time.time()

        def _try_move(path):
            self.find_failed_checker=0

            self.path=path

            self.move_to_point = self.path.pop(0)
            cd = sprites._check_direction(self.self_point, self.move_to_point)

            if cd != "stop":                
                self.action_move(cd)
            else:
                self.action_move(self.direction)

            self.behavior_action = "move_to_point"
            self.target_point=self.path[len(self.path)-1]

        if action_args == None:

            _reset_action()
        
            if not sucess:
                self.taran_moving=True

                return
            
            if path and len(path)>2:_try_move(path)

        elif action_args["flag"]=="ignore_destructible_blocks":

            _reset_action()

            if not sucess:
                self.find_failed_checker+=1
                _wait_action()
                return

            if path and len(path)>2:_try_move(path)

        elif action_args["flag"]=="test_correct_path":

            if not sucess:
                return

            self.taran_moving=False
            self.find_failed_checker=0

            if len(path)>2:_try_move(path)

    def collect_exclude_points(self):
        exclude_points=[]
        for unit in GameContext.context.units:
            if unit!=self and unit.is_astar_stay:
                exclude_points.append((unit.self_point[0],unit.self_point[1]))

                exclude_points.append((unit.self_point[0]+1,unit.self_point[1]))
                exclude_points.append((unit.self_point[0],unit.self_point[1]+1))
                exclude_points.append((unit.self_point[0]+1,unit.self_point[1]+1))

                exclude_points.append((unit.self_point[0]-1,unit.self_point[1]))
                exclude_points.append((unit.self_point[0],unit.self_point[1]-1))
                exclude_points.append((unit.self_point[0]-1,unit.self_point[1]-1))

                exclude_points.append((unit.self_point[0]+1,unit.self_point[1]-1))
                exclude_points.append((unit.self_point[0]-1,unit.self_point[1]+1))
        return exclude_points

    def capturing_player(self, player_index=0):

        gc=GameContext.context

        if len(gc.players) == 0 or player_index > len(gc.players):
            return False

        player = gc.players[player_index]

        def _find_path(astar_map,exclude_points,ignore_flags,action_args):
            self.thread_locked=True
            ret = astar.astar(astar_map, self.self_point, player.self_point, exclude_points, ignore_flags)
            self.thread_locked=False

            print(ret)
            
            GameContext.event_list_locker.acquire()

            GameContext.event_list.append({"type": "unit_event", "object_type": "unit_path", "object":{"sender":self,"success":ret != None,"path":ret,"action_args":action_args}})

            GameContext.event_list_locker.release()
            
        exclude_points=self.collect_exclude_points()

        self.start_waiting_capture_time=time.time()
        if self.taran_moving:
            threading.Thread(target=_find_path,args=(gc.map_navigation.astar_map.copy(),exclude_points,[1],{"flag":"ignore_destructible_blocks"})).start()
        else:
            threading.Thread(target=_find_path,args=(gc.map_navigation.astar_map.copy(),exclude_points,[],None)).start()

        return True

    def is_target_at_viewline(self):
        gc=GameContext.context
        asmap=gc.map_navigation.astar_map

        target_point=gc.players[self.target_plyer_index].self_point

        exclude_points=self.collect_exclude_points()

        if self.direction == "left":

            if self.self_point[1] != target_point[1] or target_point[0] >= self.self_point[0]:return False
            for xi in range(target_point[0], self.self_point[0]):
                v=asmap[self.self_point[1]][xi]
                if (v != 1 and v > 0) or (xi,self.self_point[1]) in exclude_points:return False

        elif self.direction == "right":

            if self.self_point[1] != target_point[1] or target_point[0] <= self.self_point[0]:return False

            for xi in range(self.self_point[0],target_point[0]):
                v=asmap[self.self_point[1]][xi]
                if (v != 1 and v > 0) or (xi,self.self_point[1]) in exclude_points:return False
        
        elif self.direction == "up":

            if self.self_point[0] != target_point[0] or target_point[1] >= self.self_point[1]:return False
            for yi in range(target_point[1],self.self_point[1]):
                v=asmap[yi][self.self_point[0]]
                if (v != 1 and v > 0) or (self.self_point[0],yi) in exclude_points:return False

        elif self.direction == "down":

            if self.self_point[0] != target_point[0] or target_point[1] <= self.self_point[1]:return False

            for yi in range(self.self_point[1],target_point[1]):
                v=asmap[yi][self.self_point[0]]
                if  (v != 1 and v > 0) or (self.self_point[0],yi) in exclude_points:return False

        return True

    def try_shot(self):
        gc=GameContext.context
        if time.time()-self.shot_time > self.shot_time_interval:
            self.shot_time = time.time()
            gc.shot(self, (self.self_point[0]*BLOCK_SIZE)+10, (self.self_point[1]*BLOCK_SIZE)+10, self.direction)

    def checking_straight_path(self):
        gc=GameContext.context
        if len(gc.players) == 0 or self.target_plyer_index >= len(gc.players):
            return False

        player = gc.players[self.target_plyer_index]

        unit_pos = Vector2(self.self_point[0], self.self_point[1])
        player_pos = Vector2(player.self_point[0], player.self_point[1])
        astar_map = gc.map_navigation.astar_map

        exclude_points=self.collect_exclude_points()

        def _h_check_line(xa, xb, y):
            if xb-xa < 1:
                return False

            for c in range(xa, xb):
                p = astar_map[y][c]
                if p > 0 or p == -9 or (c,y) in exclude_points:
                    return False
            return True

        def _v_check_line(ya, yb, x):
            if yb-ya < 1:
                return False

            for r in range(ya, yb):
                p = astar_map[r][x]
                if p > 0 or p == -9  or (x,r) in exclude_points:
                    return False
            return True

        if player_pos.x > unit_pos.x and player_pos.y < unit_pos.y:
            if _h_check_line(unit_pos.x, player_pos.x, unit_pos.y) and _v_check_line(player_pos.y+1, unit_pos.y, player_pos.x):
                new_path = []

                for x in range(unit_pos.x+1, player_pos.x+1):
                    new_path.append((x, unit_pos.y))

                for y in reversed(range(player_pos.y+1, unit_pos.y)):
                    new_path.append((player_pos.x, y))

                return new_path
            elif _v_check_line(player_pos.y+1, unit_pos.y, unit_pos.x) and _h_check_line(unit_pos.x, player_pos.x, player_pos.y):
                new_path = []

                for y in reversed(range(player_pos.y, unit_pos.y)):
                    new_path.append((unit_pos.x, y))

                for x in range(unit_pos.x, player_pos.x-1):
                    new_path.append((x, player_pos.y))

                return new_path
                
        elif player_pos.x > unit_pos.x and player_pos.y > unit_pos.y:
            if _h_check_line(unit_pos.x+1, player_pos.x+1, unit_pos.y) and _v_check_line(unit_pos.y+1, player_pos.y, player_pos.x):
                new_path = []

                for x in range(unit_pos.x+1, player_pos.x+1):
                    new_path.append((x, unit_pos.y))

                for y in range(unit_pos.y+1, player_pos.y-1):
                    new_path.append((player_pos.x, y))
                
                return new_path
            elif _v_check_line(unit_pos.y+1, player_pos.y, unit_pos.x) and _h_check_line(unit_pos.x, player_pos.x-1, player_pos.y):
                new_path = []

                for y in range(unit_pos.y+1, player_pos.y):
                    new_path.append((unit_pos.x, y))

                for x in range(unit_pos.x, player_pos.x-1):
                    new_path.append((x, player_pos.y))

                return new_path

        elif player_pos.x < unit_pos.x and player_pos.y < unit_pos.y:
            if _h_check_line(player_pos.x, unit_pos.x-1, unit_pos.y) and _v_check_line(player_pos.y+1, unit_pos.y-1, player_pos.x):
                new_path = []

                for x in reversed(range(player_pos.x, unit_pos.x)):
                    new_path.append((x, unit_pos.y))

                for y in reversed(range(player_pos.y+1, unit_pos.y)):
                    new_path.append((player_pos.x, y))

                return new_path
            elif _v_check_line(player_pos.y, unit_pos.y-1, unit_pos.x) and _h_check_line(player_pos.x, unit_pos.x-1, player_pos.y):
                new_path = []

                for y in reversed(range(player_pos.y, unit_pos.y)):
                    new_path.append((unit_pos.x, y))

                for x in reversed(range(player_pos.x+1, unit_pos.x)):
                    new_path.append((x, player_pos.y))

                return new_path
                
        elif player_pos.x < unit_pos.x and player_pos.y > unit_pos.y:
            if _h_check_line(player_pos.x, unit_pos.x-1, unit_pos.y) and _v_check_line(unit_pos.y+1, player_pos.y-1, player_pos.x):
                new_path = []

                for x in reversed(range(player_pos.x, unit_pos.x)):
                    new_path.append((x, unit_pos.y))

                for y in range(unit_pos.y+1, player_pos.y):
                    new_path.append((player_pos.x, y))

                return new_path
            elif _v_check_line(unit_pos.y+1, player_pos.y-1, unit_pos.x) and _h_check_line(player_pos.x+1, unit_pos.x-1, player_pos.y):
                new_path = []

                for y in range(unit_pos.y+1, player_pos.y+1):
                    new_path.append((unit_pos.x, y))

                for x in reversed(range(player_pos.x+1, unit_pos.x-1)):
                    new_path.append((x, player_pos.y))

                return new_path

        return False

    def update_behavior(self):

        if self.behavior_action=="wait_capture":
            return

        if self.wait_time!=None and time.time()-self.start_wait_time<self.wait_time:
            return

        self.wait_time=None
        self.start_wait_time=None

        gc=GameContext.context

        if len(gc.players) <= self.target_plyer_index:
            return

        player_pos = gc.players[self.target_plyer_index].pos
        player_point = (int(player_pos.x/BLOCK_SIZE)-1, int(player_pos.y/BLOCK_SIZE)-1)

        def _random_action():

            del self.path
            self.path = None

            self.behavior_timeout = 1.0

            rnd = random.randint(0, 4)
            if rnd == 0:
                print("try_shot>> rnd",self.name)
                self.try_shot()
                return
            elif rnd == 1:
                self.action_move("up")
            elif rnd == 2:
                self.action_move("down")
            elif rnd == 3:
                self.action_move("left")
            elif rnd == 4:
                self.action_move("right")

            self.behavior_action = "random_action"

        def _get_straight_path():
            new_path = self.checking_straight_path()
            if new_path:

                if len(new_path)<1:
                    print("ERROR!! new_path:",new_path,self.name)

                self.move_to_point = new_path.pop(0)

                if self.self_point[0]!=self.move_to_point[0] and self.self_point[1]!=self.move_to_point[1]:
                    self.action_move("stop")
                    self.behavior_action = None
                    self.behavior_subaction = None
                    print("set None action:a",self.name)
                    return

                del self.path
                self.path = new_path

                cd = sprites._check_direction(self.self_point, self.move_to_point)

                if cd == "stop":
                    self.action_move("stop")
                    self.behavior_action = "stay_and_attacked_player"
                    self.behavior_subaction = "A"
                    return True

                self.action_move(cd)

                self.last_step_dist = PointDistance((self.pos.x-BLOCK_SIZE, self.pos.y-BLOCK_SIZE), (self.move_to_point[0]*BLOCK_SIZE, self.move_to_point[1]*BLOCK_SIZE))

                self.target_point=gc.players[self.target_plyer_index].self_point

                self.behavior_subaction = "move_straight_path"

                return True

        if self.behavior_action == "move_to_point" or self.behavior_action == "stay_and_attacked_player":
            if self.behavior_subaction=="wait_stay_player":
                if time.time()-self.wait_stay_player_st>1.0:
                    self.behavior_action = "find_player"
                    self.behavior_subaction = None
                    self.move_to_point = None
                    self.action_move("stop")

            if gc.players[self.target_plyer_index].self_point != self.target_point:
                self.behavior_subaction="wait_stay_player"
                self.wait_stay_player_st=time.time()

        if self.behavior_action == None:
            self.behavior_action = "find_player"
            self.behavior_subaction = None
            self.move_to_point = None
            self.action_move("stop")
            return

        elif self.behavior_action == "find_player":
            if self.behavior_subaction != "move_straight_path" and _get_straight_path():
                return
            
            if self.capturing_player(self.target_plyer_index):
                self.behavior_action = "wait_capture"
                self.behavior_subaction = None
                self.move_to_point = None
                self.path = None
                self.action_move("stop")
                return

        elif self.behavior_action == "stay_and_attacked_player":
            if self.is_target_at_viewline():
                self.try_shot()
                return
            self.behavior_action = None
            self.behavior_subaction = None

        elif self.behavior_action == "move_to_point":

            if self.taran_moving:
                self.try_shot()
            if self.self_point == self.move_to_point:
                d = PointDistance((self.pos.x-BLOCK_SIZE, self.pos.y-BLOCK_SIZE),(self.move_to_point[0]*BLOCK_SIZE, self.move_to_point[1]*BLOCK_SIZE))

                if self.last_step_dist != None and d >= self.last_step_dist:
                    
                    self.last_step_dist = None

                    if len(self.path) == 0:
                        self.action_move("stop")
                        self.behavior_action = None
                        self.behavior_subaction = None
                        return

                    self.move_to_point = (self.path.pop(0))

                    cd = sprites._check_direction(self.self_point, self.move_to_point)

                    self.action_move(cd)
                self.last_step_dist = d
            else:
                if PointDistance((self.pos.x-BLOCK_SIZE, self.pos.y-BLOCK_SIZE),(self.move_to_point[0]*BLOCK_SIZE, self.move_to_point[1]*BLOCK_SIZE))>BLOCK_SIZE*2:
                    self.action_move("stop")
                    self.behavior_action = None
                    self.behavior_subaction = None
                    return

                if self.is_stay:

                    try_points=[]
                    dirs={"left":(-1,0),"right":(1,0),"up":(0,-1),"down":(0,1)}
                    for d in dirs:
                        tpx=self.self_point[0]+dirs[d][0]
                        tpy=self.self_point[1]+dirs[d][1]

                        if tpx<0:tpx=0
                        elif tpx>=GameContext.context.map_navigation.astar_cells:tpx=GameContext.context.map_navigation.astar_cells-1

                        if tpy<0:tpy=0
                        elif tpy>=GameContext.context.map_navigation.astar_rows:tpy=GameContext.context.map_navigation.astar_rows-1

                        try_point=(tpx,tpy)

                        if GameContext.context.map_navigation.astar_map[try_point[1]][try_point[0]]<1:
                            try_points.append({"dir":d,"point":try_point})

                    if len(try_points)>0:
                        tpo=try_points[random.randint(0, len(try_points)-1)]
                        self.move_to_point=tpo["point"]
                        self.path=[]
                        self.action_move(tpo["dir"])
                    else:
                        self.action_move("stop")
                        self.behavior_action = None
                        self.behavior_subaction = None

                        self.wait_time=1.0
                        self.start_wait_time=time.time()

                    return

            if self.is_target_at_viewline():
                self.try_shot()

                self.behavior_action = "stay_and_attacked_player"
                self.behavior_subaction = "B"
                self.action_move("stop")

            if self.behavior_subaction != "move_straight_path":
                _get_straight_path()
                return

        elif self.behavior_action == "random_action":
            self.behavior_action = None
            print("set None action:g",self.name)

            return