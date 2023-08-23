from system.scenes import SceneBase, Scenes
from system.clock import Timer
from scenes.common import (
    Title,
)
from scenes.title_scene import TitleScene


class LoadingScene(SceneBase):

    def __init__(self):
        super().__init__()
        self.sprites.add(Title())

        self._timer = Timer(1000)
        self._timer.start()

    def update(self):
        if self._timer.over():
            scenes = Scenes.instance()
            scenes.change_scene(TitleScene())
