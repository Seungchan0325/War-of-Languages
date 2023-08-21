import pygame

from common import SingletonInstane
from game_config import GameConfig
from system.systems import (
    EventHandler,
    Scenes,
    Screen,
)
from scenes.scene_title import SceneTitle


class Game(SingletonInstane):

    def __init__(self):
        self._running = None
        self._clock = None

    # return False if failed to init
    def init(self) -> bool:
        config = GameConfig.instance()

        pygame.init()
        pygame.display.set_caption(config.name)
        self._clock = pygame.time.Clock()

        event_handler = EventHandler.instance()
        scenes = Scenes.instance()
        screen = Screen.instance()

        event_handler.init()
        screen.init()
        scenes.init()

        scenes.change_scene(SceneTitle())

        return True

    def loop(self):
        config = GameConfig.instance()

        event_handler = EventHandler.instance()
        scenes = Scenes.instance()

        self._running = True

        while self._running:
            event_handler.update()
            self._running = not event_handler.is_quit

            scenes.update()
            scenes.render()

            self._clock.tick(config.fps)

    def release(self):
        pygame.quit()
