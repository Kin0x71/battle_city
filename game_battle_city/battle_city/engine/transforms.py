from engine.collisions_math import *
import engine.sprites as sprites
from engine.behavior import *

def dist(xa, ya, xb, yb):
    return math.sqrt((xa-xb)**2.0 + (ya-yb)**2.0)

class transforms:

    map_navigation=None

    def __init__(self,map_navigation):
        self.map_navigation=map_navigation

    def update_transform(self, obj):
        obj.last_pos.x = obj.pos.x
        obj.last_pos.y = obj.pos.y

        obj.last_point = obj.self_point
        
        obj.pos += (obj.velocity*obj.speed)

        if obj.pos.x-obj.w/2 <= 0.0:
            obj.pos.x = (obj.w/2)+1
            obj.start_pos = obj.last_pos
            obj.on_collide(None)
        elif obj.pos.x+obj.w/2 >= self.map_navigation.map_w:
            obj.pos.x = (self.map_navigation.map_w-obj.w/2)-1
            obj.start_pos = obj.last_pos
            obj.on_collide(None)

        if obj.pos.y-obj.h/2 <= 0.0:
            obj.pos.y = (obj.h/2)+1
            obj.start_pos = obj.last_pos
            obj.on_collide(None)
        elif obj.pos.y+obj.h/2 >= self.map_navigation.map_h:
            obj.pos.y = (self.map_navigation.map_h-obj.h/2)-1
            obj.start_pos = obj.last_pos
            obj.on_collide(None)

    def update_transforms_collide(self, objects_list):
        
        for obj in objects_list:

            self.update_transform(obj)

            if Vector2Length(obj.velocity) > 0.0:
                for t in objects_list:
                    
                    vReaction = Vector2()
                    if t != obj and dist(obj.pos.x, obj.pos.y, t.pos.x, t.pos.y) < DIST_COLLIDE and Collide_Circle_Circle(Vector2(obj.pos.x, obj.pos.y), obj.radius, Vector2(t.pos.x, t.pos.y), t.radius, vReaction):
                        obj.pos += vReaction

                        obj.start_pos = obj.last_pos

                        obj.on_collide(t)

                for line in self.map_navigation.collide_list:

                    vReaction = Vector2()
                    if Collide_Circle_Line(obj.pos, obj.radius, line[0], line[1], vReaction) or \
                        Collide_Circle_Point(obj.pos, obj.radius, Vector2(line[0][0],line[0][1]), vReaction) or \
                        Collide_Circle_Point(obj.pos, obj.radius, Vector2(line[1][0],line[1][1]), vReaction):
                        obj.pos += vReaction

                        obj.start_pos = obj.last_pos

                        obj.on_collide(line)
                        
            if isinstance(obj, sprites.cUnitSprite):
                if obj.last_pos != obj.pos:
                    
                    obj.is_stay=False
                
                    if obj.self_point_cell_value!=None:
                        self.map_navigation.astar_map[obj.self_point[1]][obj.self_point[0]]=obj.self_point_cell_value
                    
                    last_point=obj.self_point
                    obj.update_self_point(self.map_navigation.astar_cells-1,self.map_navigation.astar_rows-1)

                    if isinstance(obj, cUnitBehavior):

                        lx=int(obj.last_pos.x * 1000) / 1000
                        ly=int(obj.last_pos.y * 1000) / 1000

                        px=int(obj.pos.x * 1000) / 1000
                        py=int(obj.pos.y * 1000) / 1000

                        if (lx,ly) != (px,py):
                            if obj.self_point!=last_point:
                                obj.is_astar_stay=False

                    obj.self_point_cell_value=self.map_navigation.astar_map[obj.self_point[1]][obj.self_point[0]]
                    self.map_navigation.astar_map[obj.self_point[1]][obj.self_point[0]]=-9

                else:
                    if isinstance(obj, cUnitBehavior):
                        obj.is_astar_stay=True

                    obj.is_stay=True

    def update_bullet_collides(self, bullet_object_list, objects_list):

        for bullet in bullet_object_list:

            for obj in objects_list:

                if obj != bullet and bullet.shooter != obj and  dist(bullet.pos.x, bullet.pos.y, obj.pos.x, obj.pos.y) <= DIST_COLLIDE:
                    
                    vReaction = Vector2()
                    collide=False
                    if isinstance(obj, sprites.cMapSprite):
                        if Collide_Circle_Rectangle(Vector2(bullet.pos.x, bullet.pos.y), bullet.radius, Rectangle(obj.pos.x, obj.pos.y, obj.w, obj.h), vReaction) or \
                            Collide_Circle_Point(Vector2(bullet.pos.x, bullet.pos.y), bullet.radius, obj.pos, vReaction) or \
                            Collide_Circle_Point(Vector2(bullet.pos.x, bullet.pos.y), bullet.radius, Vector2(obj.pos.x+obj.w, obj.pos.y), vReaction) or \
                            Collide_Circle_Point(Vector2(bullet.pos.x, bullet.pos.y), bullet.radius, Vector2(obj.pos.x, obj.pos.y+obj.h), vReaction) or \
                            Collide_Circle_Point(Vector2(bullet.pos.x, bullet.pos.y), bullet.radius, Vector2(obj.pos.x+obj.w, obj.pos.y+obj.h), vReaction):
                            collide=True
                    else:
                        if Collide_Circle_Circle(Vector2(obj.pos.x, obj.pos.y), obj.radius, Vector2(bullet.pos.x, bullet.pos.y), bullet.radius, vReaction):
                            collide=True

                    if collide:
                        bullet.pos += vReaction
                        bullet.start_pos = bullet.last_pos
                        bullet.on_collide(obj)
                        obj.on_collide(bullet)