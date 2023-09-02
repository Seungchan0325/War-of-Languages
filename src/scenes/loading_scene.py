from system.scenes import BaseScene, Scenes
from system.event_handler import EventHandler
from system.network import Network
from scenes.common import (
    Title,
)
from scenes.title_scene import TitleScene


class LoadingScene(BaseScene):

    def __init__(self):
        super().__init__()
        self.sprites.add(Title())

    def update(self):
        network = Network.instance()
        for sock in network.connection:
            data = network.recv(sock)
            if data is None:
                continue
            msg = data.decode()
            if msg.startswith("get_state"):
                network.send(sock, "state_online".encode())
                network.close(sock)

        event_handler = EventHandler.instance()
        if event_handler.is_key_updated or event_handler.is_mouse_updated:
            scenes = Scenes.instance()
            scenes.change_scene(TitleScene())
