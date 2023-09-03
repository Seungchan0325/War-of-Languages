from system.scenes import BaseScene, Scenes
from system.event_handler import EventHandler
from scenes.common import (
    Title,
    global_network_handling,
)
from scenes.title_scene import TitleScene


class LoadingScene(BaseScene):

    def __init__(self):
        super().__init__()
        self.sprites.add(Title())

    def update(self):
        global_network_handling("state_online")

        event_handler = EventHandler.instance()
        if event_handler.is_key_updated or event_handler.is_mouse_updated:
            scenes = Scenes.instance()
            scenes.change_scene(TitleScene())
