import pygame

from common import SingletonInstane
from scenes.loading_scene import LoadingScene
from system.clock import Clock
from system.event_handler import EventHandler
from system.scenes import Scenes
from system.screen import Screen


class Game(SingletonInstane):

    def __init__(self):
        self._running: bool

    # return False if failed to init
    def init(self) -> bool:
        self._running = True

        pygame.init()

        clock = Clock.instance()
        event_handler = EventHandler.instance()
        scenes = Scenes.instance()
        screen = Screen.instance()

        clock.init()
        event_handler.init()
        screen.init()
        scenes.init(LoadingScene())

        return True

    def loop(self):
        clock = Clock.instance()
        event_handler = EventHandler.instance()
        scenes = Scenes.instance()

        while self._running:
            event_handler.update()
            self._running = not event_handler.is_quit

            scenes.update()
            scenes.render()

            clock.tick()

    def release(self):
        pygame.quit()
