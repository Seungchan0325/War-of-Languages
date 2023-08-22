import pygame

from common import SingletonInstane
from game_config import GameConfig
from scenes.scene_title import SceneTitle
from system.event_handler import EventHandler
from system.scenes import Scenes
from system.screen import Screen


class Game(SingletonInstane):

    def __init__(self):
        self._running: bool
        self._clock: pygame.time.Clock

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
        scenes.init(SceneTitle())

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

            delta_time = self._clock.tick(config.fps)
            print(delta_time)

    def release(self):
        pygame.quit()
