import platform

import pygame

from game_config import GameConfig
from system.event_manager import EventManager
from system.scene_manager import SceneManager
from scenes.scene_title import SceneTitle
from window import Window


class Game:

    def __init__(self):
        self._config = None
        self._window = None

        self._screen = None
        self._clock = None

        self._event_manager = EventManager.instance()
        self._scene_manager = SceneManager.instance()

        self._running = None

    # return False if failed to init
    def init(self) -> bool:
        self._config = GameConfig.instance()

        self._window = Window.instance()
        if platform.system() == "Windows":
            self._window.size = self._window.get_screen_size()
        else:
            self._window.size = (1920, 1080)

        pygame.init()
        pygame.display.set_caption(self._config.name)
        self._screen = pygame.display.set_mode(self._window.size, pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()

        self._scene_manager.change_scene(SceneTitle())

        return True

    def loop(self):
        self._running = True

        while self._running:
            self._event_manager.update()
            self._running = not self._event_manager.is_quit()

            self._scene_manager.update()
            self._scene_manager.render(self._screen)

            pygame.display.flip()

            self._clock.tick(self._config.fps)

    def release(self):
        pygame.quit()
