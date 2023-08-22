import abc

import pygame

from system.systems import Screen


class SceneBase(abc.ABC):

    def __init__(self):
        self.background = pygame.Surface(Screen.instance().area.size)
        self.sprites = pygame.sprite.LayeredDirty()

    @abc.abstractmethod
    def update(self):
        pass
