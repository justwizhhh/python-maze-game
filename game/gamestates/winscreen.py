import numpy as np
import pyasge

import game
import game.gamestates.gamestate
from game.gamedata import GameData
from game.gamestates.gamestate import GameState
from game.gamestates.gamestate import GameStateID

class WinScreen(GameState):
    """ The game's win condition menu"""

    def __init__(self, data: GameData) -> None:
        super().__init__(data)

        self.id = GameStateID.START_MENU
        self.data.renderer.setClearColour(pyasge.COLOURS.BLACK)
        self.init_ui()

        # sets up the camera and points it at the player
        map_mid = [0, 0]

        self.camera = pyasge.Camera(map_mid, self.data.game_res[0], self.data.game_res[1])
        self.camera.zoom = 1

        # ui objects
        self.win_label = pyasge.Text(self.data.fonts[0], "You win!", 275, 300)
        self.win_label.z_order = 120

        settings = pyasge.GameSettings()
        print(str(settings.window_width) + " - " + str(settings.window_height))

    def init_ui(self):
        """Initialises the UI elements"""
        pass

    def start(self) -> None:
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
        pass

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        """ Simulates deterministic time steps for the game objects"""
        pass

    def update(self, game_time: pyasge.GameTime) -> GameStateID:
        return GameStateID.WINNER

    def render(self, game_time: pyasge.GameTime) -> None:
        """ Renders the game world and the UI """
        self.data.renderer.setViewport(pyasge.Viewport(0, 0, self.data.game_res[0], self.data.game_res[1]))
        self.data.renderer.setProjectionMatrix(self.camera.view)

        #self.data.shaders["example"].uniform("rgb").set([1.0, 1.0, 0])
        #self.data.renderer.shader = self.data.shaders["example"]

        self.render_ui()

    def render_ui(self) -> None:
        """ Render the UI elements and map to the whole window """
        # set a new view that covers the width and height of game
        camera_view = pyasge.CameraView(self.data.renderer.resolution_info.view)
        vp = self.data.renderer.resolution_info.viewport
        self.data.renderer.setProjectionMatrix(0, 0, vp.w, vp.h)
        self.data.renderer.render(self.win_label)

        # this restores the original camera view
        self.data.renderer.setProjectionMatrix(camera_view)