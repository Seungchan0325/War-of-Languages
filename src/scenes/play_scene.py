import pygame

from system.screen import Screen
from system.scenes import SceneBase
from system.event_handler import EventHandler
from system.clock import Clock
from scenes.common import FPS, Text


G = 9.80665


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
    def __init__(self, pos: tuple[float, float], size: tuple[float, float], game_sprites: pygame.sprite.Group):
        super().__init__()

        self.game_sprites = game_sprites

        # Pysical Variable
        self.is_fixed: bool = False
        self.use_gravity: bool = False

        self.is_colliding: bool = False

        self.mass: float = 1.0

        self.force: pygame.Vector2 = pygame.Vector2()

        self._acc: pygame.Vector2 = pygame.Vector2()
        self.last_acc: pygame.Vector2 = pygame.Vector2()

        self._vel: pygame.Vector2 = pygame.Vector2()
        self.last_vel: pygame.Vector2 = pygame.Vector2()

        self.static_friction: float = 0
        self.dynamic_friction: float = 0

        self.elasticity: float = 1

        self.pos: pygame.Vector2 = pygame.Vector2(pos)

        self.rect = pygame.Rect((0, 0), (meter2pixel(size[0]), meter2pixel(size[1])))
        self.rect.bottomleft = coord2pixel((self.pos.x, self.pos.y))
    
    def apply_acc(self, acc: pygame.Vector2):
        pass

    def apply_force(self, force: pygame.Vector2):
        pass

    def apply_impulse(self, impulse: pygame.Vector2):
        pass

    def change_vel(self, vel: pygame.Vector2):
        self._vel = vel

    def physical_update(self):
        if self.is_fixed:
            return

        if self.use_gravity:
            self._acc -= pygame.Vector2(0, G)

        collided = pygame.sprite.spritecollide(self, self.game_sprites, False)
        for other in collided:
            if other is self:
                continue

            e = (self.elasticity + other.elasticity) / 2

            m1 = self.mass
            v1 = self.last_vel
            m2 = other.mass
            v2 = other.last_vel

            vel_x = ((e + 1) * m2 * v2.x + v1.x * (m1 - e * m2)) / (m1 + m2)
            vel_y = ((e + 1) * m2 * v2.y + v1.y * (m1 - e * m2)) / (m1 + m2)

            vel = pygame.Vector2(vel_x, vel_y)

            self.change_vel(vel)

    def object_update(self):
        if self.is_fixed:
            return

        self.dirty = 1

        clock = Clock.instance()
        delta_time = clock.delta_sec()

        self.last_vel = self._vel
        self.last_acc = self._acc

        self._vel += self._acc * delta_time

        self.pos += self._vel * delta_time

        self.rect.bottomleft = coord2pixel((self.pos.x, self.pos.y))


class Border(Entity):

    def __init__(self):
        self.mass = 987654321
        self.is_fixed = True
        self.use_gravity = True


class Block(Entity):

    def __init__(self, game_sprites: pygame.sprite.Group, pos: tuple[int, int], vel: pygame.Vector2, mass: float, color: str):
        super().__init__(pos, (1, 1), game_sprites)

        self._vel = pygame.Vector2(vel[0], vel[1])

        self.mass = mass

        surface = pygame.Surface(self.rect.size)
        surface.fill(color)

        self.image = surface

        self.dirty = 2

    def update(self):
        super().physical_update()

        # logic


class PlayScene(SceneBase):

    def __init__(self):
        super().__init__()

        self.play_sprites = pygame.sprite.Group()

        self.play_sprites.add(Block(self.play_sprites, (3, 4), (0, 0), 10, "red"))
        self.play_sprites.add(Block(self.play_sprites, (15, 4), (-1, 0), 1, "white"))

        self.sprites.add(self.play_sprites)

        self.sprites.add(FPS())

    def update(self):
        for sprite in self.play_sprites:
            sprite.object_update()

        self.sprites.update()
