from enum import Enum

from pygame import Surface
from pygame.sprite import LayeredDirty

from common import SingletonInstane
from system.screen import Screen


class BaseScene:

    def __init__(self):
        self.background = Surface(Screen.instance().area.size)
        self.sprites = LayeredDirty()

    def update(self):
        pass

    def render(self):
        pass


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
        self._scene.render()
