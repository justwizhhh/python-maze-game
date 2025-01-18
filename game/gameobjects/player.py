from game.gameobjects.baseobject import BaseObject
from game.gamedata import GameData
from game.gameobjects.gamemap import GameMap

import numpy
import numpy as np
import pyasge


class Player(BaseObject):

    def __init__(self, data: GameData):
        super().__init__()
        self.data = data

        self.collision_sprite = pyasge.Sprite()

        self.move_input_dir = [0, 0]
        self.punch_input_dir = [0, 0]

        self.collision_check_margin = 2
        self.move_speed = 5

        self.current_move_speed = [0, 0]
        self.is_punching = False
        self.punch_direction = [0, 0]

        # Animations
        self.anim_offset = pyasge.Point2D(0, 0)
        self.anim_idle = self.data.renderer.createNonCachedTexture("/data/textures/icy_Idle.png")
        self.anim_walk = \
            (
                self.data.renderer.createNonCachedTexture("/data/textures/icy_LookLeft.png"),
                self.data.renderer.createNonCachedTexture("/data/textures/icy_LookRight.png"),
                self.data.renderer.createNonCachedTexture("/data/textures/icy_LookUp.png"),
                self.data.renderer.createNonCachedTexture("/data/textures/icy_LookDown.png")
            )
        self.anim_punch = \
            (
                self.data.renderer.createNonCachedTexture("data/textures/icy_PunchLeft.png"),
                self.data.renderer.createNonCachedTexture("data/textures/icy_PunchRight.png"),
                self.data.renderer.createNonCachedTexture("data/textures/icy_PunchUp.png"),
                self.data.renderer.createNonCachedTexture("data/textures/icy_PunchDown.png")
            )

    def init_sprite(self) -> None:
        self.sprite.attach(self.anim_idle)
        self.collision_sprite.attach(self.anim_idle)
        self.sprite.z_order = 5

        self.sprite.scale = 2
        self.collision_sprite.scale = 2

    def collision_check(self, map: GameMap) -> bool:
        # Check if there is a tile in front of the player before moving
        tile_check_pos1 = [self.collision_sprite.midpoint.x, self.collision_sprite.midpoint.y]
        tile_check_pos2 = [self.collision_sprite.midpoint.x, self.collision_sprite.midpoint.y]

        if self.move_direction[0] != 0:
            tile_check_pos1[0] += ((self.collision_sprite.width / 2) * self.move_direction[0]) + self.current_move_speed[0]
            tile_check_pos2[0] += ((self.collision_sprite.width / 2) * self.move_direction[0]) + self.current_move_speed[0]
            tile_check_pos1[1] += (self.collision_sprite.height / 2)
            tile_check_pos2[1] -= (self.collision_sprite.height / 2)

        elif self.move_direction[1] != 0:
            tile_check_pos1[1] += ((self.collision_sprite.height / 2) * self.move_direction[1]) + self.current_move_speed[1]
            tile_check_pos2[1] += ((self.collision_sprite.height / 2) * self.move_direction[1]) + self.current_move_speed[1]
            tile_check_pos1[0] += (self.collision_sprite.width / 2)
            tile_check_pos2[0] -= (self.collision_sprite.width / 2)

        tile_check1 = map.tile(pyasge.Point2D(tile_check_pos1[0], tile_check_pos1[1]))
        tile_check2 = map.tile(pyasge.Point2D(tile_check_pos2[0], tile_check_pos2[1]))

        test1 = map.is_valid_tile(self.data.game_map_layer, (tile_check1[0], tile_check1[1]))
        test2 = map.is_valid_tile(self.data.game_map_layer, (tile_check2[0], tile_check2[1]))

        if test1 is True or test2 is True:
            return True
        else:
            return False

    def update_speed(self):
        # Update the player's speed for more accurate collision detection
        self.current_move_speed[0] = self.move_direction[0] * self.move_speed
        self.current_move_speed[1] = self.move_direction[1] * self.move_speed

    def update_anims(self):
        # Walking animations
        if (self.move_input_dir[0] == 0 and self.move_input_dir[1] == 0) is False:
            self.anim_offset = pyasge.Point2D(0, 0)
            if self.move_direction[0] != 0:
                if self.move_direction[0] < 0:
                    self.sprite.attach(self.anim_walk[0])
                else:
                    self.sprite.attach(self.anim_walk[1])
            elif self.move_direction[1] != 0:
                if self.move_direction[1] < 0:
                    self.sprite.attach(self.anim_walk[2])
                else:
                    self.sprite.attach(self.anim_walk[3])

        # Punching animations
        if (self.punch_input_dir[0] == 0 and self.punch_input_dir[1] == 0) is False:
            self.is_punching = True

            if self.punch_direction[0] != 0:
                if self.punch_direction[0] < 0:
                    self.sprite.attach(self.anim_punch[0])
                    self.anim_offset = pyasge.Point2D(-self.collision_sprite.width * 2, 0)
                else:
                    self.sprite.attach(self.anim_punch[1])
                    self.anim_offset = pyasge.Point2D(0, 0)
            elif self.punch_direction[1] != 0:
                if self.punch_direction[1] < 0:
                    self.sprite.attach(self.anim_punch[2])
                    self.anim_offset = pyasge.Point2D(0, -self.collision_sprite.height * 2)
                else:
                    self.sprite.attach(self.anim_punch[3])
                    self.anim_offset = pyasge.Point2D(0, 0)
        else:
            self.is_punching = False

            self.sprite.attach(self.anim_idle)
            self.anim_offset = pyasge.Point2D(0, 0)

    def move(self, map: GameMap):
        # Update the player's position
        self.collision_sprite.x += self.current_move_speed[0]
        self.collision_sprite.y += self.current_move_speed[1]

    def update_sprite(self):
        self.sprite.x = self.collision_sprite.x + self.anim_offset.x
        self.sprite.y = self.collision_sprite.y + self.anim_offset.y
