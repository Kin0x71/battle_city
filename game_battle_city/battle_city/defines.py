
import threading

DIST_COLLIDE=32
BLOCK_SIZE=8
SCALE_FACTOR=1

player_lvl_states=[
    {"speed":0.5,"shot_time_interval":0.5,"bullet_speed":1.0},
    {"speed":0.8,"shot_time_interval":0.4,"bullet_speed":1.5},
    {"speed":1.1,"shot_time_interval":0.3,"bullet_speed":2.0},
    {"speed":1.4,"shot_time_interval":0.2,"bullet_speed":2.5}
]

class GameContext:
    context=None
    event_list=None
    event_list_locker=None
    
    @classmethod
    def set(cls,game_context):
        cls.context=game_context

        cls.event_list = []
        cls.event_list_locker = threading.Lock()

        print("define source_player_lvl_list")
        cls.source_player_lvl_list=None
        print("source_player_lvl_list:",id(cls),id(cls.source_player_lvl_list))

    @classmethod
    def get(cls):
        return cls.context