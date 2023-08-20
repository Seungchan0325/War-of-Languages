import platform

import pygame

from game_config import GameConfig
from system import (
    event_manager,
    scene_manager,
)
from scenes import scene_title
import window


class Game:

    def __init__(self):
        self._window = None

        self._screen = None
        self._clock = None

        self._event_manager = None
        self._scene_manager = None

        self._running = None

    # return False if failed to init
    def init(self) -> bool:
        self._window = window.Window()
        if platform.system() == "Window":
            self._window.size = self._window.get_screen_size()
        else:
            self._window.size = (1920, 1080)

        pygame.init()
        pygame.display.set_caption(GameConfig.name)
        self._screen = pygame.display.set_mode(self._window.size, pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()

        self._event_manager = event_manager.EventManager()
        self._scene_manager = scene_manager.SceneManager(scene_title.SceneTitle())

        return True

    def loop(self):
        self._running = True

        while self._running:
            self._event_manager.update()
            self._running = not self._event_manager.is_quit()

            self._scene_manager.update()
            self._scene_manager.render(self._screen)

            pygame.display.flip()

            self._clock.tick(GameConfig.fps)

    def release(self):
        pygame.quit()
