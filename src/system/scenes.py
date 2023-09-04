import pygame

from common import SingletonInstane
from system.network import Network
from system.screen import Screen


class BaseScene:

    def __init__(self):
        self.background = pygame.Surface(Screen.instance().area.size)
        self.sprites = pygame.sprite.LayeredDirty()
        self.state = "state_online"

    def network_handling(self):
        network = Network.instance()

        for sock in network.connection:
            data = network.pick(sock)
            if data is None:
                continue
            msg = data.decode()
            if msg.startswith("get_state"):
                network.recv(sock)
                network.send(sock, self.state.encode())
                network.close(sock)

    def update(self):
        self.network_handling()


class Scenes(SingletonInstane):

    def __init__(self):
        self._is_changed: bool
        self._next_scene: BaseScene
        self._scene: BaseScene

    def init(self, scene: BaseScene):

        self._is_changed = False
        self._next_scene = None
        self._scene = scene

    def change_scene(self, scene: BaseScene):
        self._is_changed = True
        self._next_scene = scene

    def update(self):
        if self._is_changed:
            self._scene = self._next_scene
            self._next_scene = None
            self._is_changed = False

        self._scene.update()

    def render(self):
        screen = Screen.instance()
        screen.render(self._scene.background, self._scene.sprites)
