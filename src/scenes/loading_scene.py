from system.scenes import SceneBase, Scenes
from system.event_handler import EventHandler
from system.clock import Timer
from scenes.common import (
    Title,
)
from scenes.title_scene import TitleScene


class LoadingScene(SceneBase):

    def __init__(self):
        super().__init__()
        self.sprites.add(Title())

        # self._timer = Timer(1000)
        # self._timer.start()

    def update(self):
        # if self._timer.over():
        #     self._timer.stop()
        #     scenes = Scenes.instance()
        #     scenes.change_scene(TitleScene())

        event_handler = EventHandler.instance()
        if event_handler.is_key_updated or event_handler.is_mouse_updated:
            scenes = Scenes.instance()
            scenes.change_scene(TitleScene())
