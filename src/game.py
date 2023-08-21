import platform

import pygame

from common import get_monitor_size, SingletonInstane
from game_config import GameConfig
from system.systems import (
    EventHandler,
    SceneHandler,
)
from scenes.scene_title import SceneTitle


class Game(SingletonInstane):

    def __init__(self):
        self._config = None
        self._screen_size = None

        self._screen = None
        self._clock = None

        self._event_manager = None
        self._scene_manager = None

        self._running = None

    # return False if failed to init
    def init(self) -> bool:
        self._config = GameConfig.instance()

        self._screen_size = get_monitor_size()

        pygame.init()
        pygame.display.set_caption(self._config.name)
        self._screen = pygame.display.set_mode(self._screen_size, pygame.FULLSCREEN)
        self._clock = pygame.time.Clock()

        self._event_manager = EventHandler.instance()
        self._scene_manager = SceneHandler.instance()
        self._scene_manager.change_scene(SceneTitle())

        return True

    def loop(self):
        self._running = True

        while self._running:
            self._event_manager.update()
            self._running = not self._event_manager.is_quit

            self._scene_manager.update()
            self._scene_manager.render(self._screen)

            pygame.display.flip()

            self._clock.tick(self._config.fps)

    def release(self):
        pygame.quit()
