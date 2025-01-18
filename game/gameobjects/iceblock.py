from game.gameobjects.baseobject import BaseObject
from game.gamedata import GameData
from game.gameobjects.gamemap import GameMap

import random
import numpy
import numpy as np
import pyasge


class IceBlock(BaseObject):

    def __init__(self):
        super().__init__()

        self.is_active = False
        self.is_sliding = False
        self.enemies_killed = 0

        self.foreground_layer = 0

        self.move_speed = 15
        self.current_move_speed_x = 0
        self.current_move_speed_y = 0

    def init_sprite(self) -> None:
        self.sprite.loadTexture("/data/textures/iceBall.png")
        self.sprite.z_order = 5

        self.sprite.scale = 2

    def move(self) -> None:
        self.current_move_speed_x = self.move_direction[0] * self.move_speed
        self.current_move_speed_y = self.move_direction[1] * self.move_speed

        self.sprite.x += self.current_move_speed_x
        self.sprite.y += self.current_move_speed_y

        pass

    def begin_slide(self, new_direction: tuple[int, int]) -> None:
        self.move_direction = new_direction
        self.is_sliding = True

    def tile_collision(self, map: GameMap) -> bool:
        tile_check_pos = [
            self.sprite.midpoint.x + (self.move_direction[0] * self.sprite.width),
            self.sprite.midpoint.y + (self.move_direction[1] * self.sprite.height)]
        tile_check = map.tile(pyasge.Point2D(tile_check_pos[0], tile_check_pos[1]))

        return map.is_valid_tile(self.foreground_layer, tile_check)
