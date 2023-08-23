from abc import ABC, abstractmethod

import pygame

from common import SingletonInstane
from system.screen import Screen


class SceneBase(ABC):

    def __init__(self):
        self.background = pygame.Surface(Screen.instance().area.size)
        self.sprites = pygame.sprite.LayeredDirty()

    @abstractmethod
    def update(self):
        pass


class Scenes(SingletonInstane):

    def __init__(self):
        self._is_changed: bool
        self._next_scene: SceneBase
        self._scene: SceneBase

    def init(self, scene: SceneBase):
        self._is_changed = False
        self._next_scene = None
        self._scene = scene

    def change_scene(self, scene: SceneBase):
        self._is_changed = True
        self._next_scene = scene

    def update(self):
        if self._is_changed:
            self._is_changed = False

            self._scene = self._next_scene
            self._next_scene = None

        self._scene.update()

    def render(self):
        screen = Screen.instance()
        screen.render(self._scene.background, self._scene.sprites)
