import numpy as np
import pyasge

import game
import game.gamestates.gamestate
from game.gamedata import GameData
from game.gamestates.gamestate import GameState
from game.gamestates.gamestate import GameStateID

class GameOver(GameState):
    """ The game's lose screen menu"""

    def __init__(self, data: GameData) -> None:
        super().__init__(data)

        self.id = GameStateID.GAME_OVER
        self.data.renderer.setClearColour(pyasge.COLOURS.BLACK)
        self.init_ui()

        self.restart_game = False

        # sets up the camera and points it at the player
        map_mid = [0, 0]

        self.camera = pyasge.Camera(map_mid, self.data.game_res[0], self.data.game_res[1])
        self.camera.zoom = 1

        # ui objects
        self.screen_mid = [
            int(self.data.renderer.resolution_info.window_resolution[0] / 2),
            int(self.data.renderer.resolution_info.window_resolution[1] / 2)]

        self.game_over_label = pyasge.Text(self.data.fonts[0], "Game Over", self.screen_mid[0], self.screen_mid[1] - 250)
        self.game_over_label.position = pyasge.Point2D(
            self.game_over_label.x - (self.game_over_label.width / 2),
            self.game_over_label.y - (self.game_over_label.height / 2))

        self.highscore_label = pyasge.Text(self.data.fonts[0], "High Scores", self.screen_mid[0], self.screen_mid[1] - 140)
        self.highscore_label.scale = 0.5
        self.highscore_label.position = pyasge.Point2D(
            self.highscore_label.x - (self.highscore_label.width / 2),
            self.highscore_label.y - (self.highscore_label.height / 2))

        self.is_there_new_score = False
        self.new_score_label = pyasge.Text(self.data.fonts[0], "- NEW -        - NEW -", self.screen_mid[0],self.screen_mid[1] - 140)
        self.new_score_label.scale = 0.55
        self.new_score_label.position = pyasge.Point2D(
            self.new_score_label.x - (self.new_score_label.width / 2),
            self.new_score_label.y - (self.new_score_label.height / 2))

        self.time_elapsed_label = pyasge.Text(self.data.fonts[0], "Elapsed Time", self.screen_mid[0], self.screen_mid[1] + 300)
        self.time_elapsed_label.scale = 0.5
        self.time_elapsed_label.position = pyasge.Point2D(
            self.time_elapsed_label.x - (self.time_elapsed_label.width / 2),
            self.time_elapsed_label.y - (self.time_elapsed_label.height / 2))

        self.time_elapsed_display = pyasge.Text(self.data.fonts[0], "", self.screen_mid[0], self.screen_mid[1] + 330)
        self.time_elapsed_display.scale = 0.5
        self.time_elapsed_display.position = pyasge.Point2D(
            self.time_elapsed_display.x - (self.time_elapsed_display.width / 2),
            self.time_elapsed_display.y - (self.time_elapsed_display.height / 2))

        self.highscore_text = [[], [], []]
        for i in range(3):
            for index in range(self.data.highscore_limit):
                self.highscore_text[i].append(pyasge.Text(self.data.fonts[0], "0",
                                                   self.screen_mid[0],
                                                   self.screen_mid[1] - 50 + (50 * index)))
                current_text = self.highscore_text[i][index]
                current_text.scale = 0.55
                current_text.x -= current_text.width / 2
                current_text.y -= current_text.height / 2

    def start(self) -> None:
        self.restart_game = False

        # Sorting and clamping the highscore list
        if self.data.score != 0 and self.data.score > min(self.data.highscores[self.data.current_level]):
            self.data.highscores[self.data.current_level].append(self.data.score)
        print(self.data.highscores)

        for score in range(len(self.data.highscores[self.data.current_level])):
            if score >= self.data.highscore_limit:
                self.data.highscores[self.data.current_level].pop(score - 1)
        self.merge_sort(self.data.highscores[self.data.current_level])

        # Displaying the newly-sorted scores
        for i in range(3):
            for index in range(len(self.highscore_text[i])):
                if index < len(self.data.highscores[self.data.current_level]):
                    self.highscore_text[i][index].string = self.data.highscores[self.data.current_level][index].__str__()

                    # Realigning the text to the centre of the screen
                    self.highscore_text[i][index].x = self.screen_mid[0] - self.highscore_text[i][index].width / 2

        # Re-alignined text poistions
        match self.data.current_level:
            case 0:
                self.highscore_label.string = "Normal Maze - High Scores"
            case 1:
                self.highscore_label.string = "Tricky Maze - High Scores"
            case 2:
                self.highscore_label.string = "Boring Maze - High Scores"

        try:
            new_score_label_id = self.data.highscores[self.data.current_level].index(self.data.score)
            self.new_score_label.position.y = self.highscore_text[self.data.current_level][new_score_label_id].y
            self.is_there_new_score = True
        except ValueError:
            self.is_there_new_score = False

        self.highscore_label.position.x = self.screen_mid[0] - (self.highscore_label.width / 2)

        self.time_elapsed_display.string = self.data.time_elapsed
        self.time_elapsed_display.position.x = self.screen_mid[0] - (self.time_elapsed_display.width / 2)

        pass

    def init_ui(self):
        """Initialises the UI elements"""
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
            if event.key == pyasge.KEYS.KEY_ENTER:
                self.restart_game = True

            pass
        pass

    def merge_sort(self, arr):
        # Code inspired by W3Schools and Educative
        # https://www.w3schools.com/dsa/dsa_algo_mergesort.php
        # https://www.educative.io/answers/merge-sort-in-python

        if len(arr) <= 1:
            return

        # Divide the array into two, and try to merge-sort those sub-arrays as well until they only end up with one element
        mid = len(arr) // 2
        left_side = arr[:mid]
        right_side = arr[mid:]

        self.merge_sort(left_side)
        self.merge_sort(right_side)

        left_index = right_index = index = 0

        # The temporary arrays are used to compare which numbers are bigger/smaller
        while left_index < len(left_side) and right_index < len(right_side):
            if left_side[left_index] >= right_side[right_index]:
                arr[index] = left_side[left_index]
                left_index += 1
            else:
                arr[index] = right_side[right_index]
                right_index += 1
            index += 1

        # Add the remaining numbers that were discarded in the first while-loop
        while left_index < len(left_side):
            arr[index] = left_side[left_index]
            left_index += 1
            index += 1

        while right_index < len(right_side):
            arr[index] = right_side[right_index]
            right_index += 1
            index += 1

        # Array is already updated by the end of the function

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        """ Simulates deterministic time steps for the game objects"""
        pass

    def update(self, game_time: pyasge.GameTime) -> GameStateID:
        if self.restart_game:
            return GameStateID.START_MENU
        else:
            return GameStateID.GAME_OVER

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

        self.data.renderer.render(self.game_over_label)
        self.data.renderer.render(self.highscore_label)
        if self.is_there_new_score:
            self.data.renderer.render(self.new_score_label)

        for i in range(3):
            for score_text in self.highscore_text[i]:
                self.data.renderer.render(score_text)

        self.data.renderer.render(self.time_elapsed_label)
        self.data.renderer.render(self.time_elapsed_display)

        # this restores the original camera view
        self.data.renderer.setProjectionMatrix(camera_view)