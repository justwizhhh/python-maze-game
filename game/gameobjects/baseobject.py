from abc import abstractmethod

import pyasge

from game.gamedata import GameData


class BaseObject:

    def __init__(self):
        self.is_active = True

        self.sprite = pyasge.Sprite()
        self.move_direction = [0, 0]

    def collision(self, other_sprite: pyasge.Sprite, margin: float) -> list[int, int]:
        # 'margin' can be used to calculate collisions between scaled-down bounding boxes
        collision_x = self.sprite.x + (self.sprite.width * self.sprite.scale) - margin >= other_sprite.x + margin \
                      and other_sprite.x + (other_sprite.width * other_sprite.scale) - margin >= self.sprite.x + margin

        collision_y = self.sprite.y + (self.sprite.height * self.sprite.scale) - margin >= other_sprite.y + margin \
                      and other_sprite.y + (other_sprite.height * other_sprite.scale) - margin >= self.sprite.y + margin

        collision_dir = [0, 0]
        if collision_x:
            collision_dir[0] = 1 if self.sprite.midpoint.x > other_sprite.midpoint.x else -1
        if collision_y:
            collision_dir[1] = 1 if self.sprite.midpoint.y > other_sprite.midpoint.y else -1

        return collision_dir

    @abstractmethod
    def init_sprite(self) -> None:
        pass
