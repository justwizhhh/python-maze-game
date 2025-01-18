import math

import pyasge

from game.gamestates.gameover import GameOver
from game.gameobjects.gamemap import GameMap
from game.gamedata import GameData
from game.gamestates.gamestate import GameState
from game.gamestates.gamestate import GameStateID

from game.gameobjects.player import Player
from game.misc.pathfinding import Pathfinding
from game.gameobjects.enemy import EnemyType
from game.gameobjects.enemy import Enemy
from game.gameobjects.iceblock import IceBlock


class GamePlay(GameState):
    """ The game play state is the core of the game itself.

    The role of this class is to process the game logic, update
    the players positioning and render the resultant game-world.
    The logic for deciding on victory or loss should be handled by
    this class and its update function should return GAME_OVER or
    GAME_WON when the end game state is reached.
    """

    def __init__(self, data: GameData) -> None:
        """ Creates the game world

        Use the constructor to initialise the game world in a "clean"
        state ready for the player. This includes resetting of player's
        health and the enemy positions.

        Args:
            data (GameData): The game's shared data
        """
        super().__init__(data)

        self.id = GameStateID.GAMEPLAY
        self.data.renderer.setClearColour(pyasge.COLOURS.CORAL)
        self.init_ui()
        self.init_level()

        # setting up all gameplay objects
        self.player = Player(self.data)
        self.player.init_sprite()
        self.player.sprite.z_order = 10

        self.ice_block = IceBlock()
        self.ice_block.init_sprite()

        self.enemies = [
            Enemy(EnemyType.CHASE, self.data, self.player, self.ice_block),
            Enemy(EnemyType.SMART_CHASE, self.data, self.player, self.ice_block),
            Enemy(EnemyType.WACKY_CHASE, self.data, self.player, self.ice_block),
            Enemy(EnemyType.RANDOM, self.data, self.player, self.ice_block)]
        self.level_enemy_pos = None

        for enemy in self.enemies:
            enemy.init_sprite()
            enemy.sprite.z_order = 5
            pass

        # sets up the camera and points it at the player
        self.map_mid = [
            self.data.game_map.width * self.data.game_map.tile_size[0] * 0.5,
            self.data.game_map.height * self.data.game_map.tile_size[1] * 0.5
        ]

        self.camera = pyasge.Camera(self.map_mid, self.data.game_res[0], self.data.game_res[1])
        self.camera.zoom = 1

        # ui/background objects
        self.background = pyasge.Sprite()
        self.background.loadTexture("data/textures/backgroundRocks.png")
        self.background.scale = 2
        self.background.z_order = -10

        self.score_display = pyasge.Text(self.data.fonts[0], "Score - 0000000", 75, 125)
        self.score_display.scale = 0.5
        self.score_display.z_order = 10

        self.current_timer = 0
        self.time_display = pyasge.Text(self.data.fonts[0], "", 75, 175)
        self.time_display.scale = 0.425
        self.time_display.z_order = 10

        self.max_combo_timer = 1.35
        self.min_combo_text_size = 0.65
        self.combo_text_scaler = 0.25

        self.is_combo = True
        self.combo_timer = 0
        self.last_combo_pos = pyasge.Point2D(0, 0)
        self.combo_display = pyasge.Text(self.data.fonts[0], "x1", 0, 0)
        self.combo_display.scale = self.min_combo_text_size
        self.combo_display.z_order = 10

    def init_ui(self):
        """Initialises the UI elements"""
        pass

    def init_level(self):
        # sets up the level the player will be exploring
        match self.data.current_level:
            case 0:
                self.data.game_map = GameMap(self.data.renderer, "data/map/NewLevels/Maze1.tmx")
            case 1:
                self.data.game_map = GameMap(self.data.renderer, "data/map/NewLevels/Maze2.tmx")
            case 2:
                self.data.game_map = GameMap(self.data.renderer, "data/map/NewLevels/Maze3.tmx")

        # Find all the empty areas on the map that the player/enemies can move along
        self.data.game_map_empty = self.data.game_map.get_empty_tiles()

    def start(self) -> None:
        # Load a new level (if it has changed since restarting the game
        self.init_level()

        self.current_timer = 0

        # Resets player input (stops player inputs from freezing
        self.player.move_input_dir = [0, 0]
        self.player.punch_input_dir = [0, 0]

        # Respawn/reset all objects
        self.player.collision_sprite.x = self.map_mid[0] - self.player.sprite.width
        self.player.collision_sprite.y = self.map_mid[1] - self.player.sprite.height
        self.player.sprite.x = self.player.collision_sprite.x
        self.player.sprite.y = self.player.collision_sprite.y

        self.level_enemy_pos = [
            [
                self.data.game_map.world((6, 2)),
                self.data.game_map.world((24, 2)),
                self.data.game_map.world((6, 14)),
                self.data.game_map.world((24, 14))],
            [
                self.data.game_map.world((7, 3)),
                self.data.game_map.world((23, 3)),
                self.data.game_map.world((7, 13)),
                self.data.game_map.world((23, 13))],
            [
                self.data.game_map.world((5, 4)),
                self.data.game_map.world((25, 4)),
                self.data.game_map.world((5, 12)),
                self.data.game_map.world((25, 12))]
        ]
        for i in range(4):
            self.enemies[i].sprite.x = \
                self.level_enemy_pos[self.data.current_level][i].x - (self.data.game_map.tile_size[0] / 2)
            self.enemies[i].sprite.y = \
                self.level_enemy_pos[self.data.current_level][i].y - (self.data.game_map.tile_size[1] / 2)

        for enemy in self.enemies:
            enemy.enemy_type = enemy.start_enemy_type
            enemy.reset_speed()
            enemy.current_stun_timer = 0

            enemy.step_progress = 0
            enemy.set_path()

        self.ice_block.is_active = False
        self.ice_block.is_sliding = False

        self.combo_timer = 0

        self.score_display.string = "Score - 0000000"

        pass

    def click_handler(self, event: pyasge.ClickEvent) -> None:
        if event.button is pyasge.MOUSE.MOUSE_BTN2 and \
                event.action is pyasge.MOUSE.BUTTON_PRESSED:
            pass

        if event.button is pyasge.MOUSE.MOUSE_BTN1 and \
                event.action is pyasge.MOUSE.BUTTON_PRESSED:
            pass

    def move_handler(self, event: pyasge.MoveEvent) -> None:
        """ Listens for mouse movement events from the game engine """
        pass

    def key_handler(self, event: pyasge.KeyEvent) -> None:
        """ Listens for key events from the game engine """

        # Player inputs
        if event.action == pyasge.KEYS.KEY_PRESSED:
            self.player.move_input_dir[0] += \
                1 if event.key == pyasge.KEYS.KEY_D else -1 if event.key == pyasge.KEYS.KEY_A else 0
            self.player.move_input_dir[1] += \
                1 if event.key == pyasge.KEYS.KEY_S else -1 if event.key == pyasge.KEYS.KEY_W else 0

            self.player.punch_input_dir[0] = \
                1 if event.key == pyasge.KEYS.KEY_RIGHT else -1 if event.key == pyasge.KEYS.KEY_LEFT else 0
            self.player.punch_input_dir[1] = \
                1 if event.key == pyasge.KEYS.KEY_DOWN else -1 if event.key == pyasge.KEYS.KEY_UP else 0

            if event.key == pyasge.KEYS.KEY_SPACE:
                if self.ice_block.is_active is False:
                    self.ice_block.is_active = True

                    new_pos = self.data.game_map.world(
                        self.data.game_map.tile(
                            pyasge.Point2D(self.player.sprite.midpoint.x, self.player.sprite.midpoint.y)))
                    self.ice_block.sprite.x = new_pos.x - (self.data.game_map.tile_size[0] / 2)
                    self.ice_block.sprite.y = new_pos.y - (self.data.game_map.tile_size[1] / 2)

        elif event.action == pyasge.KEYS.KEY_RELEASED:
            self.player.move_input_dir[0] -= \
                1 if event.key == pyasge.KEYS.KEY_D else -1 if event.key == pyasge.KEYS.KEY_A else 0
            self.player.move_input_dir[1] -= \
                1 if event.key == pyasge.KEYS.KEY_S else -1 if event.key == pyasge.KEYS.KEY_W else 0

            if event.key == pyasge.KEYS.KEY_LEFT or event.key == pyasge.KEYS.KEY_RIGHT:
                self.player.punch_input_dir[0] = 0
            elif event.key == pyasge.KEYS.KEY_UP or event.key == pyasge.KEYS.KEY_DOWN:
                self.player.punch_input_dir[1] = 0

        pass

    def update_combo_display(self):
        # Update combo display
        self.is_combo = True
        self.combo_display.scale = self.min_combo_text_size + \
                                   (self.combo_text_scaler * (self.ice_block.enemies_killed - 1))
        self.combo_timer = self.max_combo_timer
        self.combo_display.string = "x" + self.ice_block.enemies_killed.__str__()
        self.last_combo_pos = pyasge.Point2D(
            self.ice_block.sprite.x - (self.combo_display.width / 2),
            self.ice_block.sprite.y)

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        """ Simulates deterministic time steps for the game objects"""
        pass

    def update_score(self, new_score: int):
        self.data.score += new_score
        self.score_display.string = "Score - " + self.data.score.__str__().zfill(7)

    def update(self, game_time: pyasge.GameTime) -> GameStateID:
        """ Updates the game world

        Processes the game world logic. You should handle collisions,
        actions and AI actions here. At present cannonballs are
        updated and so are player collisions with the islands, but
        consider how the ships will react to each other

        Args:
            game_time (pyasge.GameTime): The time between ticks.
        """

        # Player movement
        if self.player.move_input_dir[1] != 0:
            self.player.move_direction = [0, self.player.move_input_dir[1]]
        elif self.player.move_input_dir[0] != 0:
            self.player.move_direction = [self.player.move_input_dir[0], 0]
        else:
            self.player.move_direction = [0, 0]

        self.player.update_speed()

        if self.player.collision_check(self.data.game_map) is False:
            self.player.move(self.data.game_map)

        # Player animations
        if self.player.punch_input_dir[1] != 0:
            self.player.punch_direction = [0, self.player.punch_input_dir[1]]
        elif self.player.punch_input_dir[0] != 0:
            self.player.punch_direction = [self.player.punch_input_dir[0], 0]
        else:
            self.player.punch_direction = [0, 0]

        self.player.update_anims()
        self.player.update_sprite()

        # Enemy movement
        for enemy in self.enemies:
            if enemy.is_active:
                enemy.move(game_time.fixed_timestep)
                enemy.update_anims()

                # Player collision check
                col_with_player = enemy.collision(self.player.sprite, 10)
                if col_with_player[0] != 0 and col_with_player[1] != 0:
                    # Stun the enemy temporarily if the player punches them
                    if self.player.is_punching:
                        enemy.current_stun_timer = enemy.stun_timer
                        enemy.enemy_type = EnemyType.STUNNED
                    else:
                        self.data.time_elapsed = self.time_display.string
                        return GameStateID.GAME_OVER

                # Ice block collisions
                col_with_ice_block = enemy.collision(self.ice_block.sprite, 5)
                if col_with_ice_block[0] != 0 and col_with_ice_block[1] != 0:
                    if self.ice_block.is_active:
                        enemy.respawn()
                        self.ice_block.enemies_killed += 1
                        self.update_score(enemy.death_score * self.ice_block.enemies_killed)

                        self.update_combo_display()

        # Ice block movement
        if self.ice_block.is_active:
            if self.ice_block.is_sliding:
                self.ice_block.move()

            ice_block_col = self.ice_block.collision(self.player.sprite, 10)
            if (self.player.punch_direction[0] == 0 and self.player.punch_direction[1] == 0) is False:
                if ice_block_col[0] != 0 and ice_block_col[1] != 0:
                    if not self.ice_block.tile_collision(self.data.game_map):
                        self.ice_block.begin_slide(self.player.punch_direction)

            if self.ice_block.tile_collision(self.data.game_map):
                self.ice_block.move_direction = (0, 0)
                self.ice_block.is_active = False
                self.ice_block.is_sliding = False
                self.ice_block.enemies_killed = 0

        # UI updates and positioning
        if self.is_combo:
            self.combo_display.x = self.last_combo_pos.x
            self.combo_display.y = self.last_combo_pos.y

            self.combo_timer -= game_time.fixed_timestep
            if self.combo_timer <= 0:
                self.is_combo = False

        self.current_timer += game_time.fixed_timestep
        self.time_display.string = \
            str(math.trunc(self.current_timer) // 60).zfill(2) + ":" + \
            str(math.trunc(self.current_timer) % 60).zfill(2) + ":" + \
            str(self.current_timer % 1)[2:4]

        self.update_camera()
        self.update_inputs()
        return GameStateID.GAMEPLAY

    def update_camera(self):
        """ Updates the camera based on gamepad input"""
        if self.data.gamepad.connected:
            self.camera.translate(
                self.data.inputs.getGamePad().AXIS_LEFT_X * 10,
                self.data.inputs.getGamePad().AXIS_LEFT_Y * 10, 0.0)

    def update_inputs(self):
        """ This is purely example code to show how gamepad events
        can be tracked """
        if self.data.gamepad.connected:
            if self.data.gamepad.A and not self.data.prev_gamepad.A:
                # A button is pressed
                pass
            elif self.data.gamepad.A and self.data.prev_gamepad.A:
                # A button is being held
                pass
            elif not self.data.gamepad.A and self.data.prev_gamepad.A:
                # A button has been released
                pass

    def render(self, game_time: pyasge.GameTime) -> None:
        """ Renders the game world and the UI """
        self.data.renderer.setViewport(pyasge.Viewport(0, 0, self.data.game_res[0], self.data.game_res[1]))
        self.data.renderer.setProjectionMatrix(self.camera.view)

        # self.data.shaders["example"].uniform("rgb").set([1.0, 1.0, 0])
        # self.data.renderer.shader = self.data.shaders["example"]

        self.data.renderer.render(self.background)

        self.data.game_map.render(self.data.renderer, game_time)

        self.data.renderer.render(self.player.sprite)
        for enemy in self.enemies:
            if enemy.is_active:
                self.data.renderer.render(enemy.sprite)

        if self.ice_block.is_active:
            self.data.renderer.render(self.ice_block.sprite)

        self.render_ui()

    def render_ui(self) -> None:
        """ Render the UI elements and map to the whole window """
        # set a new view that covers the width and height of game
        camera_view = pyasge.CameraView(self.data.renderer.resolution_info.view)
        vp = self.data.renderer.resolution_info.viewport
        self.data.renderer.setProjectionMatrix(0, 0, vp.w, vp.h)

        self.data.renderer.render(self.score_display)
        self.data.renderer.render(self.time_display)

        if self.is_combo:
            self.data.renderer.render(self.combo_display)

        # this restores the original camera view
        self.data.renderer.setProjectionMatrix(camera_view)

    def to_world(self, pos: pyasge.Point2D) -> pyasge.Point2D:
        """
        Converts from screen position to world position
        :param pos: The position on the current game window camera
        :return: Its actual/absolute position in the game world
        """
        view = self.camera.view
        x = (view.max_x - view.min_x) / self.data.game_res[0] * pos.x
        y = (view.max_y - view.min_y) / self.data.game_res[1] * pos.y
        x = view.min_x + x
        y = view.min_y + y

        return pyasge.Point2D(x, y)
