import pygame
import json
import io
import os

from defines import *
import engine.sprites as sprites

class map_block_info:
    def __init__(self,surf,hp):
        self.surf=surf
        self.hp=hp

class map_blocks_list:
    def __init__(self):
        pass

class game_objects_list:
    def __init__(self):
        pass

class map_sources:
    def __init__(self):
        self.blocks=map_blocks_list()

class game_sources:
    def __init__(self):
        self.objects=game_objects_list()

class cGameObject:
    def __init__(self, drawn, size, radius=None):
        self.drawn=drawn
        self.size=size
        self.radius=radius

class SourcesLoader:

    @classmethod
    def __init__(cls,content_directory,sprites_sheet):
        cls.content_directory=content_directory
        cls.map_sources=map_sources()
        cls.game_sources=game_sources()

        cls.source_surf=cls.surf_from_file(cls.get_content_path(sprites_sheet))

    @classmethod
    def surf_from_file(cls,fname):
        pf = io.open(fname, "rb")
        f = io.BytesIO(pf.read())
        
        surf = pygame.image.load(f)

        pf.close()
        return surf

    @classmethod
    def read_json(cls,file_name):
        json_file = io.open(file_name, "rb")
        json_str = json_file.read()
        json_data = json.loads(json_str)
        json_file.close()
        return json_data

    @classmethod
    def get_content_path(cls,file_name):
        return (cls.content_directory+"/"+file_name).replace("\\", "/")

    @classmethod
    def get_source_path(cls,source_file):
        return source_file[0:source_file.rindex("/")]+"/"

    @classmethod
    def load_blocks(cls, file_name):
        info_file = cls.get_content_path(file_name)

        json_data = cls.read_json(info_file)

        for block_name in json_data["blocks"]:
            block_info=json_data["blocks"][block_name]

            scale = max(block_info["scale"],SCALE_FACTOR) if "scale" in block_info else SCALE_FACTOR

            surf=pygame.Surface((block_info["w"], block_info["h"]),flags=pygame.SRCALPHA)

            surf.blit(cls.source_surf,pygame.Rect(0, 0, block_info["w"], block_info["h"]), pygame.Rect(block_info["x"], block_info["y"], block_info["w"], block_info["h"]))
            surf=pygame.transform.scale(surf, (block_info["w"]*scale, block_info["h"]*scale))

            setattr(cls.map_sources.blocks,block_name,map_block_info(surf,block_info["hp"]))

    @classmethod
    def load_game_objects(cls, file_name):
        info_file = cls.get_content_path(file_name)
        
        json_data = cls.read_json(info_file)

        for object_name in json_data:
            print("loading:",object_name)
            object_info=json_data[object_name]

            drawn=None

            scale = max(object_info["scale"],SCALE_FACTOR) if "scale" in object_info else SCALE_FACTOR
            radius = object_info["radius"] if "radius" in object_info else None
            size = (object_info["size"][0], object_info["size"][1]) if "size" in object_info else None

            if "direction_sprites" in object_info:

                drawn={}

                for direct_name in object_info["direction_sprites"]:
                    sprites_info=object_info["direction_sprites"][direct_name]

                    if type(sprites_info)==list:
                        frames=[]
                        for fi in sprites_info:
                            surf=pygame.Surface((fi["w"], fi["h"]),flags=pygame.SRCALPHA)
                            surf.blit(cls.source_surf,(0, 0, fi["w"], fi["h"]), (fi["x"], fi["y"], fi["w"], fi["h"]))
                            surf=pygame.transform.scale(surf, (fi["w"]*scale, fi["h"]*scale))

                            offs = (fi["offs"][0]*scale,fi["offs"][1]*scale) if "offs" in fi else (0, 0)

                            frames.append(sprites.cFrame(surf=surf, w=fi["w"], h=fi["h"], offs=offs))

                        drawn[direct_name]=frames

                    elif type(sprites_info)==dict:
                        surf=pygame.Surface((sprites_info["w"], sprites_info["h"]),flags=pygame.SRCALPHA)

                        surf.blit(cls.source_surf,pygame.Rect(0, 0, sprites_info["w"], sprites_info["h"]), pygame.Rect(sprites_info["x"], sprites_info["y"], sprites_info["w"], sprites_info["h"]))
                        surf=pygame.transform.scale(surf, (sprites_info["w"]*scale, sprites_info["h"]*scale))

                        offs = (sprites_info["offs"][0]*scale,sprites_info["offs"][1]*scale) if "offs" in sprites_info else (0, 0)

                        drawn[direct_name]=sprites.cFrame(surf=surf, w=sprites_info["w"], h=sprites_info["h"], offs=offs)

            elif "sprites" in object_info:
                sprites_info=object_info["sprites"]

                if type(sprites_info)==list:
                    frames=[]
                    for fi in sprites_info:
                        surf=pygame.Surface((fi["w"], fi["h"]),flags=pygame.SRCALPHA)
                        surf.blit(cls.source_surf,(0, 0, fi["w"], fi["h"]), (fi["x"], fi["y"], fi["w"], fi["h"]))
                        surf=pygame.transform.scale(surf, (fi["w"]*scale, fi["h"]*scale))

                        offs = (fi["offs"][0]*scale,fi["offs"][1]*scale) if "offs" in fi else (0, 0)

                        frames.append(sprites.cFrame(surf=surf, w=fi["w"], h=fi["h"], offs=offs))

                    drawn=frames

            setattr(cls.game_sources, object_name, cGameObject(drawn=drawn, size=size, radius=radius))