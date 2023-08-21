import abc

import pygame


class SceneBase(abc.ABC):

    def __init__(self):
        self.sprites = pygame.sprite.LayeredDirty()

    @abc.abstractmethod
    def update(self):
        pass
