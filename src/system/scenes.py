from system import scene_base
from system.systems import Screen
from common import SingletonInstane


class Scenes(SingletonInstane):

    def __init__(self):
        self._scene = None

    def init(self):
        pass

    def change_scene(self, scene: scene_base.SceneBase):
        self._scene = scene

    def update(self):
        self._scene.update()

    def render(self):
        screen = Screen.instance()
        screen.render(self._scene.sprites)
