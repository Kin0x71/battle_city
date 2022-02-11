import io
import time
import pygame

from defines import *
from engine.collisions_math import *

class cFrame:
    def __init__(self, surf=None, w=0, h=0, offs=(0.0,0.0)):
        self.w = w
        self.h = h
        self.offs = Vector2(offs[0], offs[1])
        self.surf = surf

class cSprite(object):
    def __init__(self, surf=None, x=0, y=0, w=0, h=0, radius=None, offs=(0.0,0.0)):
        self.pos = Vector2(float(x), float(y))
        self.offs = Vector2(offs[0], offs[1])
        self.w = w
        self.h = h
        self.radius = radius

        self.surf = surf

class cMapSprite(cSprite):
    def __init__(self, x=0, y=0, surf=None, hp=0):
        super(cMapSprite, self).__init__(surf=surf, x=x, y=y)

        self.w, self.h = self.surf.get_size()

        self.hp = hp

    def on_collide(self, collider):
        if isinstance(collider, cBulletSprite):
            self.hp -= 1
            if self.hp <= 0:
                GameContext.event_list.append({"type": "destroyed", "object_type": "map_item", "object": self})
        return self.hp


class cBulletSprite(cSprite):
    def __init__(self, x, y, drawn, shooter=None):
        super(cBulletSprite, self).__init__(x=x, y=y)

        self.name="bullet"

        self.radius = 4.0

        self.last_pos = Vector2(float(x), float(y))
        self.self_point = None
        self.update_self_point()

        self.surf = drawn.surf

        self.w, self.h = self.surf.get_size()

        self.velocity = Vector2(0.0, 0.0)
        self.direction = "up"

        self.speed = 3.5

        self.hp = 1

        self.shooter = shooter

    def update_self_point(self):
        self.self_point = (int(self.pos.x-BLOCK_SIZE/BLOCK_SIZE)-1, int(self.pos.y-1/BLOCK_SIZE)-1)
        return self.self_point

    def on_collide(self, collider):
        
        if collider==None:
            GameContext.event_list.append({"type": "destroyed", "object_type": "bullet", "object": self})
            return

        if isinstance(collider, cBulletSprite) or isinstance(collider, cMapSprite) or isinstance(collider, cUnitSprite):
            self.hp -= 1
            if self.hp <= 0:
                GameContext.event_list.append({"type": "destroyed", "object_type": "bullet", "object": self})
        return self.hp


class cAnimationSprite(cSprite):
    def __init__(self, frames, x=0, y=0, loop=False):
        super(cAnimationSprite, self).__init__(x=x, y=y)

        self.loop = loop

        self.frames = frames

        self.cur_frame = 0
        self.surf = self.frames[self.cur_frame].surf
        self.offs = self.frames[self.cur_frame].offs

        self.anim_time = time.time()

    def update(self):
        
        t = (time.time()-self.anim_time)*10.0
        
        self.cur_frame = int(t)

        if self.cur_frame>=len(self.frames):
            if not self.loop:
                GameContext.event_list.append({"type": "destroyed", "object_type": "effect", "object": self})
                return

            self.anim_time = time.time()
            self.cur_frame = 0

        self.surf = self.frames[self.cur_frame].surf
        self.offs = self.frames[self.cur_frame].offs


class cFramesList:
    def __init__(self, frames, w, h, radius=None):
        self.frames = frames
        self.w = w
        self.h = h
        self.radius = radius

class cUnitSprite(cSprite):
    def __init__(self, name, game_source, x=0, y=0):
        super(cUnitSprite, self).__init__(x=x, y=y)

        self.name=name

        self.last_pos = Vector2(float(x), float(y))
        self.self_point = (0,0)

        self.is_stay=True

        self.w = game_source.size[0]
        self.h = game_source.size[1]
        self.radius = game_source.radius

        self.anim_groups = game_source.drawn
        self.cur_frame = 0
        self.anim_time = time.time()
        self.anim_playing=False

        self.velocity = Vector2(0.0, 0.0)
        self.speed = 1.0
        self.direction = "up"

        self.surf = self.anim_groups[self.direction][0].surf
        self.offs = self.anim_groups[self.direction][0].offs

        self.action = "move_stop"

        self.update_self_point()

    def update_animation(self):

        t = (time.time()-self.anim_time)*10.0
        
        group=self.anim_groups[self.direction]

        self.cur_frame = int(t)

        if self.cur_frame>=len(group):
            self.anim_time = time.time()
            self.cur_frame = 0

        self.surf = group[self.cur_frame].surf
        self.offs = group[self.cur_frame].offs

    def update_self_point(self,max_x=None,max_y=None):

        HBS=BLOCK_SIZE/2.0

        if self.direction=="left":
            self.self_point = (int((self.pos.x-1.5)/BLOCK_SIZE), int((self.pos.y-HBS)/BLOCK_SIZE))
        elif self.direction=="right":
            self.self_point = (int((self.pos.x-BLOCK_SIZE+1.0)/BLOCK_SIZE), int((self.pos.y-HBS)/BLOCK_SIZE))
        elif self.direction=="up":
            self.self_point = (int((self.pos.x-HBS)/BLOCK_SIZE), int((self.pos.y-1.5)/BLOCK_SIZE))
        elif self.direction=="down":
            self.self_point = (int((self.pos.x-HBS)/BLOCK_SIZE), int((self.pos.y+1.0)/BLOCK_SIZE))

        if max_x!=None:
            if self.self_point[0]>max_x:
                self.self_point=(max_x,self.self_point[1])
            elif self.self_point[0]<0:
                self.self_point=(0,self.self_point[1])

        if max_y!=None:
            if self.self_point[1]>max_y:
                self.self_point=(self.self_point[0],max_y)
            elif self.self_point[1]<0:
                self.self_point=(self.self_point[0],0)

        return self.self_point

    def action_move(self, direction):

        self.anim_playing=False

        if self.action == "move_"+direction:
            return

        omd = self.direction
        if direction == "right":
            self.direction = "right"
            self.action = "move_right"
            self.velocity = Vector2(1.0, 0.0)
        elif direction == "left":
            self.direction = "left"
            self.action = "move_left"
            self.velocity = Vector2(-1.0, 0.0)
        elif direction == "up":
            self.direction = "up"
            self.action = "move_up"
            self.velocity = Vector2(0.0, -1.0)
        elif direction == "down":
            self.direction = "down"
            self.action = "move_down"
            self.velocity = Vector2(0.0, 1.0)
        elif direction == "stop":
            self.action = "move_stop"
            self.velocity = Vector2(0.0, 0.0)
        else:
            return

        self.anim_playing=True

        self.start_pos = self.pos
        self.target_pos = self.pos+self.velocity*self.speed
        self.time_start_move = time.time()
        self.time_end_move = self.time_start_move+self.speed

        if self.direction != omd:
            self.surf = self.anim_groups[self.direction][self.cur_frame].surf
            self.offs = self.anim_groups[self.direction][self.cur_frame].offs

def _check_direction(sp, tp):
    if sp[0] == tp[0] and sp[1] > tp[1]:
        return "up"
    elif sp[0] == tp[0] and sp[1] < tp[1]:
        return "down"
    elif sp[0] < tp[0] and sp[1] == tp[1]:
        return "right"
    elif sp[0] > tp[0] and sp[1] == tp[1]:
        return "left"
    elif sp[0] > tp[0] and sp[1] > tp[1]:
        return "up"
    elif sp[0] > tp[0] and sp[1] < tp[1]:
        return "down"
    elif sp[0] < tp[0] and sp[1] < tp[1]:
        return "down"
    else:
        return "stop"