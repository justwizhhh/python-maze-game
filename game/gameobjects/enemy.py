import math
import random
from enum import Enum

from game.gameobjects.baseobject import BaseObject
from game.misc.pathfinding import Pathfinding
from game.gameobjects.player import Player
from game.gameobjects.iceblock import IceBlock

from game.gamedata import GameData

import pyasge


class EnemyType(Enum):
    STUNNED = 0
    CHASE = 1
    WACKY_CHASE = 2
    SMART_CHASE = 3
    RANDOM = 4
    RUN_AWAY = 5

class Enemy(BaseObject):

    def __init__(self, type: EnemyType, gamedata: GameData, player: Player, ice_block: IceBlock):
        super().__init__()
        # Public toggles
        self.spawn_distance = 6

        self.move_speed_start = 0.05
        self.move_speed_increase = 0.005
        self.move_speed_max = 0.1

        self.pathfind_attempts = 35
        self.pathfind_randomness = 4
        self.ice_block_distance = 4

        self.stun_timer = 1
        self.death_score = 100

        # Object references
        self.data = gamedata
        self.player = player
        self.ice_block = ice_block

        self.start_enemy_type = type
        self.enemy_type = type

        self.foreground_layer = 0
        self.current_stun_timer = 0.0

        # Pathfinding variables
        self.move_path = []
        self.pathfinding = Pathfinding(self.data, 0, [self.ice_block])
        self.current_coord = self.next_coord = pyasge.Point2D((self.data.game_map.tile(self.sprite))[0],
                                                              (self.data.game_map.tile(self.sprite))[1])
        self.next_coord = None

        self.current_move_speed = self.move_speed_start
        self.move_step = pyasge.Point2D(0.00, 0.00)
        self.step_progress = 0.00

        # Animations
        self.anim_idle = self.data.renderer.createNonCachedTexture("/data/textures/fire_Idle.png")
        self.anim_runaway = self.data.renderer.createNonCachedTexture("/data/textures/fire_RunAway.png")
        self.anim_stunned = self.data.renderer.createNonCachedTexture("/data/textures/fire_Stunned.png")

    def init_sprite(self) -> None:
        self.sprite.loadTexture("/data/textures/fire_Idle.png")
        self.sprite.z_order = 5

        self.sprite.scale = 2

    @staticmethod
    def lerp(point_a: pyasge.Point2D, point_b: pyasge.Point2D, i: float):
        x = (point_b.x - point_a.x) * i
        y = (point_b.y - point_a.y) * i
        return pyasge.Point2D(x, y)

    def set_spawn(self):
        while True:
            random_pos = random.choice(self.data.game_map_empty)
            distance = math.dist(
                [self.data.game_map.world(random_pos).x, self.data.game_map.world(random_pos).y],
                [self.player.sprite.x, self.player.sprite.y]) / self.data.game_map.tile_size[0]

            if self.data.game_map.is_valid_tile(self.foreground_layer, (random_pos[0], random_pos[1])) is False:
                # Check to see the player isn't too far away from the player
                if distance > self.ice_block_distance:
                    break
                else:
                    continue
            else:
                continue

        self.sprite.x = self.data.game_map.world(random_pos).x - (
                self.data.game_map.tile_size[0] / 2)
        self.sprite.y = self.data.game_map.world(random_pos).y - (
                self.data.game_map.tile_size[1] / 2)

    def change_type(self):
        # Run away from the ice block if we get near it
        distance = math.dist([self.sprite.x, self.sprite.y],
                             [self.ice_block.sprite.x, self.ice_block.sprite.y]) / self.data.game_map.tile_size[0]

        if self.enemy_type != EnemyType.RUN_AWAY:
            if self.ice_block.is_active is True and self.ice_block.is_sliding is False:
                if distance < self.ice_block_distance:
                    self.enemy_type = EnemyType.RUN_AWAY
                    self.reset_path()
            pass
        pass

    def default_type(self):
        self.enemy_type = self.start_enemy_type
        pass

    def set_path(self):
        target_pos = pyasge.Point2D(0, 0)

        idle_pos = pyasge.Point2D((self.data.game_map.tile(self.sprite))[0], (self.data.game_map.tile(self.sprite))[1])
        default_pos = pyasge.Point2D((self.data.game_map.tile(self.player.sprite.midpoint))[0], (self.data.game_map.tile(self.player.sprite.midpoint))[1])

        match self.enemy_type:
            case EnemyType.STUNNED:
                target_pos = idle_pos

            case EnemyType.CHASE:
                # Move directly towards the player
                target_pos = default_pos

            case EnemyType.WACKY_CHASE:
                # Move towards the player, but don't always follow them exactly
                pos_check = pyasge.Point2D(
                    (self.data.game_map.tile(self.player.sprite.midpoint))[0] + random.randint(-self.pathfind_randomness, self.pathfind_randomness),
                    (self.data.game_map.tile(self.player.sprite.midpoint))[1] + random.randint(-self.pathfind_randomness, self.pathfind_randomness))
                if self.data.game_map.is_valid_tile(self.data.game_map_layer, (pos_check.x, pos_check.y)) is False:
                    target_pos = pos_check
                else:
                    target_pos = default_pos

            case EnemyType.SMART_CHASE:
                # Try to move in front of the player and get ahead of them
                pos_check = pyasge.Point2D(
                    (self.data.game_map.tile(self.player.sprite.midpoint))[0] + (self.player.move_direction[0] * self.pathfind_randomness),
                    (self.data.game_map.tile(self.player.sprite.midpoint))[1] + (self.player.move_direction[1] * self.pathfind_randomness))
                if self.data.game_map.is_valid_tile(self.data.game_map_layer, (pos_check.x, pos_check.y)) is False:
                    target_pos = pos_check
                else:
                    target_pos = default_pos

            case EnemyType.RANDOM:
                # Pick a random position to move to
                new_tile = random.choice(self.data.game_map_empty)

                target_pos = pyasge.Point2D(new_tile[0], new_tile[1])

            case EnemyType.RUN_AWAY:
                # Try to move away from the ice block (with a limited number of attempts)
                while True:
                    new_direction = pyasge.Point2D(
                        -1 if self.sprite.midpoint.x < self.ice_block.sprite.midpoint.x else 1,
                        -1 if self.sprite.midpoint.y < self.ice_block.sprite.midpoint.y else 1
                    )
                    pos_check = pyasge.Point2D(
                        (self.data.game_map.tile(self.sprite.midpoint))[0] + (
                                    new_direction.x * random.randint(0, self.pathfind_randomness)),
                        (self.data.game_map.tile(self.sprite.midpoint))[1] + (
                                    new_direction.y * random.randint(0, self.pathfind_randomness)))

                    if pos_check in self.data.game_map_empty:
                        target_pos = pos_check
                        break
                    else:
                        continue

                # If no position is found, just use default to prevent the game from lagging/freezing
                if target_pos == pyasge.Point2D(0, 0):
                    target_pos = default_pos

        start_pos = pyasge.Point2D(
            (self.data.game_map.tile(self.sprite.midpoint))[0],
            (self.data.game_map.tile(self.sprite.midpoint))[1])

        self.pathfinding.find_path(start_pos, pyasge.Point2D(target_pos))
        self.move_path = self.pathfinding.path

    def reset_path(self):
        self.step_progress = 0
        self.set_path()

    def reset_speed(self):
        self.current_move_speed = self.move_speed_start

    # Move the enemy object along the specified path
    def move(self, dt):
        if self.enemy_type == EnemyType.STUNNED:
            # Stop the enemy from moving for a short period of time
            if round(self.current_stun_timer, 2) <= 0:
                self.enemy_type = self.start_enemy_type
                pass
            else:
                self.current_stun_timer -= dt
                pass
        else:
            if self.move_path.__len__() >= 1:
                self.current_coord = self.data.game_map.world([
                    self.move_path[math.floor(self.step_progress)].x,
                    self.move_path[math.floor(self.step_progress)].y])

                if math.ceil(self.step_progress) >= self.move_path.__len__():
                    self.next_coord = self.data.game_map.world([
                        self.move_path[math.floor(self.step_progress)].x,
                        self.move_path[math.floor(self.step_progress)].y])
                else:
                    self.next_coord = self.data.game_map.world([
                        self.move_path[math.ceil(self.step_progress)].x,
                        self.move_path[math.ceil(self.step_progress)].y])

                self.move_step = self.lerp(self.current_coord, self.next_coord,
                                           self.step_progress - math.floor(self.step_progress))
                self.step_progress += self.current_move_speed

                self.sprite.x = (self.current_coord.x + self.move_step.x) - (self.data.game_map.tile_size[0] / 2)
                self.sprite.y = (self.current_coord.y + self.move_step.y) - (self.data.game_map.tile_size[1] / 2)

                # Check if any nearby obstacles should change the next path
                if self.step_progress + self.current_move_speed >= math.ceil(self.step_progress):
                    self.change_type()

                # Switch to a new path if the current path has been fully traversed
                if self.current_coord == self.next_coord:
                    if math.ceil(self.step_progress) > self.move_path.__len__() - 1:
                        self.reset_path()
                        self.default_type()
                else:
                    if math.ceil(self.step_progress) > self.move_path.__len__():
                        self.reset_path()
                        self.default_type()
            else:
                self.reset_path()
        pass

    def respawn(self):
        self.set_spawn()
        self.reset_path()

        self.current_stun_timer = 0

        # Speed up the enemy a bit every time they die
        if self.current_move_speed < self.move_speed_max:
            self.current_move_speed += self.move_speed_increase

    def update_anims(self):
        if self.enemy_type == EnemyType.RUN_AWAY:
            self.sprite.attach(self.anim_runaway)
        elif self.enemy_type == EnemyType.STUNNED:
            self.sprite.attach(self.anim_stunned)
        else:
            self.sprite.attach(self.anim_idle)

        pass
