
import pyasge

from game.gamedata import GameData
from game.gamestates.gamestate import GameState
from game.gamestates.gamestate import GameStateID

class StartMenu(GameState):
    """ The main menu state of the game"""

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
        self.screen_mid = [
            int(self.data.renderer.resolution_info.viewport.w / 2),
            int(self.data.renderer.resolution_info.viewport.h / 2)]

        self.title_label = pyasge.Text(self.data.fonts[0], "The Incredible Ice Boy", self.screen_mid[0], self.screen_mid[1] - 200)
        self.title_label.scale = 0.75
        self.title_label.position = pyasge.Point2D(
            self.title_label.x - (self.title_label.width / 2),
            self.title_label.y - (self.title_label.height / 2))

        self.description_labels = [
            pyasge.Text(self.data.fonts[0], "Create ice blasts around the map to push and send flying across the map.", self.screen_mid[0], self.screen_mid[1] + 40),
            pyasge.Text(self.data.fonts[0], "Stun the fire enemies with a punch, and then defeat them with your ice blasts!", self.screen_mid[0], self.screen_mid[1] + 80),
            pyasge.Text(self.data.fonts[0], "Hit multiple enemies with your blasts to perform combos, to get more score points.", self.screen_mid[0], self.screen_mid[1] + 120),
        ]
        for text in self.description_labels:
            text.scale = 0.25
            text.position = pyasge.Point2D(
                text.x - (text.width / 2),
                text.y - (text.height / 2))

        self.level_select_label = pyasge.Text(self.data.fonts[0], "Select a level using the Left and Right arrow keys.",
                                              self.screen_mid[0], self.screen_mid[1] + 230)
        self.level_select_label.scale = 0.25
        self.level_select_label.position = pyasge.Point2D(
            self.level_select_label.x - (self.level_select_label.width / 2),
            self.level_select_label.y - (self.level_select_label.height / 2))

        self.level_name_label = pyasge.Text(self.data.fonts[0], "Normal Maze",
                                            self.screen_mid[0], self.screen_mid[1] + 280)
        self.level_name_label.scale = 0.45
        self.level_name_label.position = pyasge.Point2D(
            self.level_name_label.x - (self.level_name_label.width / 2),
            self.level_name_label.y - (self.level_name_label.height / 2))

        # gameplay variables
        self.start_game = False

        settings = pyasge.GameSettings()
        print(str(settings.window_width) + " - " + str(settings.window_height))

    def init_ui(self):
        """Initialises the UI elements"""
        pass

    def start(self) -> None:
        self.start_game = False
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

        # Menu interactions
        if event.action == pyasge.KEYS.KEY_PRESSED:
            # Select menu
            if event.key == pyasge.KEYS.KEY_LEFT:
                if self.data.current_level > 0:
                    self.data.current_level -= 1
            if event.key == pyasge.KEYS.KEY_RIGHT:
                if self.data.current_level < 2:
                    self.data.current_level += 1

            self.update_ui()

            # Start gameplay
            if event.key == pyasge.KEYS.KEY_ENTER:
                self.start_game = True

            pass

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        """ Simulates deterministic time steps for the game objects"""
        pass

    def update(self, game_time: pyasge.GameTime) -> GameStateID:
        if self.start_game:
            #game.gamestates.gameplay.GamePlay.start_game(game.gamestates.gameplay.GamePlay)
            self.data.score = 0
            return GameStateID.GAMEPLAY
        else:
            return GameStateID.START_MENU

    def update_ui(self):
        match self.data.current_level:
            case 0:
                self.level_name_label.string = "Normal Maze"
            case 1:
                self.level_name_label.string = "Tricky Maze"
            case 2:
                self.level_name_label.string = "Boring Maze"

        # Realign the text to the centre of the screen
        self.level_name_label.position.x = self.screen_mid[0] - (self.level_name_label.width / 2)

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

        self.data.renderer.render(self.title_label)
        for text in self.description_labels:
            self.data.renderer.render(text)
        self.data.renderer.render(self.level_select_label)
        self.data.renderer.render(self.level_name_label)

        # this restores the original camera view
        self.data.renderer.setProjectionMatrix(camera_view)