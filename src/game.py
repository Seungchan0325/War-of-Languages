import pygame

from common import SingletonInstane
from game_config import GameConfig
from scenes.loading_scene import LoadingScene
from system.clock import Clock
from system.event_handler import EventHandler
from system.scenes import Scenes
from system.screen import Screen


class Game(SingletonInstane):
    # return False if failed to init
    def init(self) -> bool:

        pygame.init()

        # Get singleton classes
        config = GameConfig.instance()
        clock = Clock.instance()
        event_handler = EventHandler.instance()
        scenes = Scenes.instance()
        screen = Screen.instance()

        # Initialize system classes
        clock.init()
        event_handler.init()
        screen.init()
        scenes.init(LoadingScene())

        return True

    # Main loop
    def loop(self):

        # Get singleton classes
        clock = Clock.instance()
        event_handler = EventHandler.instance()
        scenes = Scenes.instance()

        # Loop
        while not event_handler.is_quit:
            event_handler.update()

            scenes.update()
            scenes.render()

            clock.tick()

    def release(self):

        pygame.quit()
