import pygame

import game_config
import utils
from system import (
    event_manager,
    scene_manager,
)
from scenes import scene_title


class Game:

    def __init__(self):
        self.config = None

        self._screen = None
        self._clock = None

        self._event_manager = None
        self._scene_manager = None

        self._running = None

    # return False if failed to init
    def init(self) -> bool:
        self.config = game_config.GameConfig(
            "War of Languages",
            30,
            utils.get_screen_size(),
        )

        pygame.init()
        pygame.display.set_caption(self.config.caption)
        self._screen = pygame.display.set_mode(self.config.screen_size, pygame.FULLSCREEN)
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

            self._clock.tick(self.config.fps)

    def release(self):
        pygame.quit()
