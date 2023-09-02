import pygame

from common import SingletonInstane
from game_config import GameConfig
from scenes.loading_scene import LoadingScene
from system.clock import Clock
from system.event_handler import EventHandler
from system.scenes import Scenes
from system.screen import Screen
from system.network import Network


class Game(SingletonInstane):

    def __init__(self):
        self._running: bool

    # return False if failed to init
    def init(self) -> bool:
        self._running = True

        pygame.init()

        config = GameConfig.instance()
        clock = Clock.instance()
        event_handler = EventHandler.instance()
        scenes = Scenes.instance()
        screen = Screen.instance()
        network = Network.instance()

        clock.init()
        event_handler.init()
        screen.init()
        scenes.init(LoadingScene())
        network.init(("", config.port))

        return True

    # Main loop
    def loop(self):
        clock = Clock.instance()
        event_handler = EventHandler.instance()
        scenes = Scenes.instance()
        network = Network.instance()

        while self._running:
            event_handler.update()
            self._running = not event_handler.is_quit

            scenes.update()
            scenes.render()

            network.update()

            clock.tick()

    def release(self):
        pygame.quit()
