import pyasge

class GameData:
    """
    GameData stores the data that needs to be shared

    When using multiple states in a game, you will find that
    some game data needs to be shared. GameData can be used to
    share access to data that the game and any running states may
    need.
    """

    def __init__(self) -> None:
        self.cursor = None
        self.fonts = {}
        self.game_map = None
        self.game_map_empty = []
        self.game_res = [1920, 1080]
        self.inputs = None
        self.gamepad = None
        self.prev_gamepad = None
        self.renderer = None
        self.shaders: dict[str, pyasge.Shader] = {}

        # global variables
        self.current_level = 0
        self.score = 0
        self.time_elapsed = ""

        # global customisables
        self.game_map_layer = 0

        self.highscores = [[100, 600, 250, 400, 200],
                           [300, 200, 400, 100],
                           [800, 400, 250]]
        self.highscore_limit = 6
