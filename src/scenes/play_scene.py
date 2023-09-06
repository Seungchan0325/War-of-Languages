from pygame.sprite import LayeredDirty

from scenes.common import FPS, RatioRect
from scenes.maps import WindowsMap
from system.scenes import BaseScene, State


class PlayScene(BaseScene):

    def __init__(self):
        super().__init__()

        self.state = State.PLAYING

        self.map = WindowsMap()

        self.ui_sprites = LayeredDirty()
        self.ui_sprites.add(FPS(RatioRect(0, 0, 0.04, 0.03)))

        self.sprites.add(self.map.sprites)
        self.sprites.add(self.ui_sprites)

    def update(self):
        super().update()

        self.ui_sprites.update()
        self.map.update()
