import socket

import pygame

from common import SingletonInstane
from game_config import GameConfig
from scenes.loading_scene import LoadingScene
from system.clock import Clock
from system.event_handler import EventHandler
from system.network import Network
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
        network = Network.instance()

        # Initialize system classes
        clock.init()
        event_handler.init()
        screen.init()
        scenes.init(LoadingScene())

        my_local_ip = socket.gethostbyname(socket.gethostname())
        my_addr = (my_local_ip, config.port)
        network.init(my_addr)

        return True

    # Main loop
    def loop(self):

        # Get singleton classes
        clock = Clock.instance()
        event_handler = EventHandler.instance()
        scenes = Scenes.instance()
        network = Network.instance()

        while not event_handler.is_quit:
            event_handler.update()

            scenes.update()
            scenes.render()

            network.update()

            clock.tick()

    def release(self):

        pygame.quit()

        # Get singleton class
        network = Network.instance()
        network.release()
