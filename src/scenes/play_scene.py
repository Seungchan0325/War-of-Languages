import pygame

from system.screen import Screen
from system.scenes import SceneBase
from system.event_handler import EventHandler
from system.clock import Clock, Timer
from scenes.common import FPS


G = 9.80665
Gv = pygame.math.Vector2(0, -G)


"""
Map ratio = 16 : 9
1m = screen width / 16

 ---------------
|        (16, 9)|
|               |
|(0, 0)         |
 ---------------

"""


def meter2pixel(meter: float) -> int:
    screen = Screen.instance()
    return meter * screen.width / 16


def coord2pixel(meter: tuple[float, float]) -> tuple[int, int]:
    screen = Screen.instance()
    return (meter2pixel(meter[0]), screen.height - meter2pixel(meter[1]))


class Entity(pygame.sprite.DirtySprite):

    # Both pos and size are meters
    def __init__(self, pos: tuple[float, float], size: tuple[float, float]):
        super().__init__()

        self._acc = pygame.Vector2()
        self._vel = pygame.Vector2()

        self.pos = pygame.Vector2(pos)

        self.rect = pygame.Rect((0, 0), (meter2pixel(size[0]), meter2pixel(size[1])))
        self.rect.bottomleft = coord2pixel((self.pos.x, self.pos.y))

    def update(self):
        self._vel += self._acc

        self.pos += self._vel

        self.pos.x = pygame.math.clamp(self.pos.x, 0, 15)
        self.pos.y = pygame.math.clamp(self.pos.y, 0, 8)

        self.rect.bottomleft = coord2pixel((self.pos.x, self.pos.y))


class MyCharater(Entity):

    def __init__(self):
        super().__init__((0, 8), (1, 1))

        surface = pygame.Surface(self.rect.size)
        surface.fill("purple")

        self.image = surface

        self.dirty = 2

        self._timer = Timer(0)
        self._timer.start()
        self.flag = True

    def update(self):
        event_handler = EventHandler.instance()
        clock = Clock.instance()

        print(clock.delta_sec())

        self._acc = pygame.Vector2()

        if self.pos.y == 0 and self.flag:
            self.flag = False
            print(self._timer.remain())

        if event_handler.is_key_pressing[pygame.K_a]:
            self._acc += pygame.Vector2(-4, 0) * clock.delta_sec()

        if event_handler.is_key_pressing[pygame.K_d]:
            self._acc += pygame.Vector2(4, 0) * clock.delta_sec()

        if self.pos.y == 0 and event_handler.is_key_down[pygame.K_SPACE]:
            self._acc += pygame.Vector2(0, 2*G + 10) * clock.delta_sec()

        if self.pos.y > 0:
            self._acc += Gv * clock.delta_sec()

        super().update()


class PlayScene(SceneBase):

    def __init__(self):
        super().__init__()

        self.sprites.add(MyCharater())
        self.sprites.add(FPS())

    def update(self):
        self.sprites.update()
