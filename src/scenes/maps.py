import abc
from random import randrange
from enum import Enum, auto

import pygame
from pygame import Rect, Surface
from pygame.sprite import DirtySprite, Group
import pymunk
from pymunk import Body, Poly, Space

from system.clock import Clock, Timer
from system.event_handler import EventHandler
from system.screen import Screen

G = 980.665


"""
Map ratio = 16 : 9
1m = 100coord
1coord = screen width / 16 / 100

width: 16m
height: 9m

 ---------------
|        (16, 9)|
|               |
|(0, 0)         |
 ---------------

"""


class Lenght:

    def __init__(self, x: float):
        self.x: float = x

    def to_px(self) -> int:
        screen = Screen.instance()
        pixel_per_coord = screen.width / 16 / 100
        return round(self.x * pixel_per_coord)


class Size:

    def __init__(self, width: float, height: float):
        self.width = Lenght(width)
        self.height = Lenght(height)

    def to_tuple(self) -> tuple[float, float]:
        return (self.width.x, self.height.x)

    def to_px(self) -> tuple[int, int]:
        return (self.width.to_px(), self.height.to_px())


class Coord:

    def __init__(self, x: float, y: float):
        self.x = Lenght(x)
        self.y = Lenght(y)

    def to_tuple(self) -> tuple[float, float]:
        return (self.x.x, self.y.x)

    def to_px(self) -> tuple[int, int]:
        screen = Screen.instance()
        return (self.x.to_px(), screen.height - self.y.to_px())


class CollisionTypes(Enum):
    GROUND = auto()
    PLAYER = auto()
    BULLET = auto()


class Entity(DirtySprite):

    def __init__(self, sprites: Group, space: Space, pos: Coord, size: Size):
        super().__init__()

        self.sprites = sprites
        self.space = space

        self.sprites.add(self)

        self.pos: Coord = pos
        self.size: Size = size

        self.body: Body = Body(2, float("inf"))
        self.body.position = self.pos.to_tuple()

        width = self.size.width.x
        height = self.size.height.x

        vs = [
            (0, 0),
            (width, 0),
            (width, height),
            (0, height),
        ]

        self.shape = Poly(self.body, vs)
        self.shape.friction = 0.8
        self.shape.elasticity = 0.5

        space.add(self.body, self.shape)

        self.rect = Rect(self.pos.to_px(), self.size.to_px())

        surface = Surface(self.rect.size)
        surface.fill("purple")

        self.image = surface

    def apply_force(self, force: tuple[int, int]):
        self.body.apply_force_at_local_point(force, self.body.center_of_gravity)

    def apply_impulse(self, impulse: tuple[int, int]):
        self.body.apply_impulse_at_local_point(impulse, self.body.center_of_gravity)

    def collision_begin(self,
                        arbiter: pymunk.Arbiter,
                        space: pymunk.Space,
                        other: "Entity") -> bool:
        return True

    def collision_end(self,
                        arbiter: pymunk.Arbiter,
                        space: pymunk.Space,
                        other: "Entity"):
        pass

    def update(self):
        self.dirty = 1
        self.pos = Coord(self.body.position[0], self.body.position[1])
        self.rect.bottomleft = self.pos.to_px()


class BaseMap:

    def __init__(self, sprites: Group):
        self.sprites: Group = sprites
        self.space = Space()
        self.space.gravity = (0, -G)

        self.background = Surface(Screen.instance().size)

        width = 1600
        height = 900
        thickness = 100

        borders = [
            Entity(self.sprites, self.space, Coord(0, -thickness), Size(width, thickness)),
            Entity(self.sprites, self.space, Coord(0, height), Size(width, thickness)),
            Entity(self.sprites, self.space, Coord(-thickness, 0), Size(thickness, height)),
            Entity(self.sprites, self.space, Coord(width, 0), Size(thickness, height)),
        ]

        borders[0].shape.collision_type = CollisionTypes.GROUND.value
        for border in borders:
            border.body.body_type = Body.STATIC
            border.shape.elasticity = 1
            border.shape.friction = 0

        def find_entities(shapes: tuple[pymunk.Shape, pymunk.Shape]) -> list[Entity]:
            ret = []
            for i in self.sprites:
                if (hasattr(i, "shape")
                    and (i.shape is shapes[0]
                    or i.shape is shapes[1])):
                    ret.append(i)

            return ret

        def default_begin_handler(arbiter: pymunk.Arbiter, space: Space, data) -> bool:
            entities = find_entities(arbiter.shapes)
            if len(entities) != 2:
                return True

            ok = True
            ok = ok and entities[0].collision_begin(arbiter, space, entities[1])
            ok = ok and entities[1].collision_begin(arbiter, space, entities[0])
            return ok

        def default_end_handler(arbiter: pymunk.Arbiter, space: Space, data):
            entities = find_entities(arbiter.shapes)
            if len(entities) != 2:
                return

            entities[0].collision_end(arbiter, space, entities[1])
            entities[1].collision_end(arbiter, space, entities[0])

        handler = self.space.add_default_collision_handler()
        handler.begin = default_begin_handler
        handler.separate = default_end_handler

        self.player1: Character
        self.player2: Character

    def update(self):
        clock = Clock.instance()
        self.space.step(clock.delta_sec())


class BaseInput(abc.ABC):

    @abc.abstractmethod
    def jump(self) -> bool:
        pass

    @abc.abstractmethod
    def left(self) -> bool:
        pass

    @abc.abstractmethod
    def right(self) -> bool:
        pass

    @abc.abstractmethod
    def basic_attack(self) -> bool:
        pass


class Bullet(Entity):

    def __init__(self, sprites: Group, space: Space, owner: Entity, pos: Coord, damage: float, img: Surface):
        super().__init__(sprites, space, pos, Size(10, 10))
        self.owner = owner
        self.damage = damage

        self.body.mass = 1
        self.shape.collision_type = CollisionTypes.BULLET.value

        self.image = img

        def zero_gravity(body, gravity, damping, dt):
            Body.update_velocity(body, (0, 0), damping, dt)
        self.body.velocity_func = zero_gravity

    def collision_begin(self, arbiter: pymunk.Arbiter, space: Space, other: Entity) -> bool:
        if other.shape.collision_type != CollisionTypes.BULLET.value and other is not self.owner:
            self.space.remove(self.shape, self.body)
            self.sprites.remove(self)

        if other.shape.collision_type == CollisionTypes.PLAYER.value:
            return True

        return False


class Character(Entity):

    def __init__(self, sprites: Group, space: Space, pos: Coord, my_input: BaseInput):
        super().__init__(sprites, space, pos, Size(60, 60))
        self.shape.collision_type = CollisionTypes.PLAYER.value
        self.input = my_input

        self.full_hp: float = 100.0
        self.hp: float = 100.0

        self.speed = 3000
        self.jump = 1400
        self.limit_speed = 300

        self.rpm = 400
        self.bullet_damage = 10
        self.bullet_impulse = 1500

        self.bullet_interval = Timer(1 / (self.rpm / 60) * 1000)
        self.bullet_interval.start()

        self.bullet_img = Surface(self.rect.size)

        self._grounded_cnt = 0
        self._dir = 1


    def collision_begin(self, arbiter: pymunk.Arbiter, space: Space, other: Entity) -> True:
        if other.shape.collision_type == CollisionTypes.GROUND.value:
            self._grounded_cnt += 1

        if other.shape.collision_type == CollisionTypes.BULLET.value:
            self.hp -= other.damage

        return True

    def collision_end(self, arbiter: pymunk.Arbiter, space: Space, other: Entity):
        if other.shape.collision_type == CollisionTypes.GROUND.value:
            self._grounded_cnt -= 1

    def update(self):
        super().update()

        if self._grounded_cnt > 0 and self.input.jump():
            self.apply_impulse((0, self.jump))

        if -self.limit_speed < self.body.velocity.x and self.input.left():
            self.apply_force((-self.speed, 0))
            self._dir = -1

        if self.body.velocity.x < self.limit_speed and self.input.right():
            self.apply_force((self.speed, 0))
            self._dir = 1

        if self.bullet_interval.over() and self.input.basic_attack():
            pos = self.pos
            if self._dir < 0:
                pos.x.x -= 10
            elif self._dir > 0:
                pos.x.x += 50
            pos.y.x += self.size.height.x / 2 - 10
            bullet = Bullet(self.sprites, self.space, self, pos, self.bullet_damage, self.bullet_img)
            bullet.apply_impulse((self.bullet_impulse * self._dir, 0))

            self.bullet_interval.start()


class CppCharacter(Character):

    def __init__(self, sprites: Group, space: Space, pos: Coord, my_input: BaseInput):
        super().__init__(sprites, space, pos, my_input)
        self.body.mass = 2.5

        self.full_hp = 150.0
        self.hp = 150.0

        self.rpm = 80

        self.bullet_impulse = 2000
        self.bullet_damage = 7.5

        self.bullet_interval = Timer(1 / (self.rpm / 60) * 1000)
        self.bullet_interval.start()

        self.bullet_img = pygame.image.load("resources/c_bullet.png")
        self.bullet_img = pygame.transform.scale(self.bullet_img, Size(10, 10).to_px())

        self._hitted_timer = Timer(100)

        self._img = pygame.image.load("resources/c.png").convert_alpha()
        self._img = pygame.transform.scale(self._img, (self.rect.width, self.rect.height))

        self._img_hitted = pygame.image.load("resources/c_hitted.png").convert_alpha()
        self._img_hitted = pygame.transform.scale(self._img_hitted, (self.rect.width, self.rect.height))
        self.image = self._img

    def collision_begin(self, arbiter: pymunk.Arbiter, space: Space, other: Entity) -> True:
        if other.shape.collision_type == CollisionTypes.BULLET.value:
            self._hitted_timer.start()
            self.image = self._img_hitted

        return super().collision_begin(arbiter, space, other)

    def update(self):
        if self._hitted_timer.over():
            self._hitted_timer.stop()
            self.image = self._img
        super().update()


class PythonCharacter(Character):

    def __init__(self, sprites: Group, space: Space, pos: Coord, my_input: BaseInput):
        super().__init__(sprites, space, pos, my_input)
        self.body.mass = 1.5

        self.full_hp = 75
        self.hp = 75

        self.rpm = 800

        self.bullet_impulse = 1000
        self.bullet_damage = 1.5
        self.bullet_interval = Timer(1 / (self.rpm / 60) * 1000)
        self.bullet_interval.start()

        self.bullet_img = pygame.image.load("resources/python_bullet.png")
        self.bullet_img = pygame.transform.scale(self.bullet_img, Size(10, 10).to_px())

        self._hitted_timer = Timer(100)

        self._img = pygame.image.load("resources/python.png").convert_alpha()
        self._img = pygame.transform.scale(self._img, (self.rect.width, self.rect.height))

        self._img_hitted = pygame.image.load("resources/python_hitted.png").convert_alpha()
        self._img_hitted = pygame.transform.scale(self._img_hitted, (self.rect.width, self.rect.height))

        self.image = self._img

    def collision_begin(self, arbiter: pymunk.Arbiter, space: Space, other: Entity) -> True:
        if other.shape.collision_type == CollisionTypes.BULLET.value:
            self._hitted_timer.start()
            self.image = self._img_hitted

        return super().collision_begin(arbiter, space, other)

    def update(self):
        if self._hitted_timer.over():
            self._hitted_timer.stop()
            self.image = self._img
        super().update()


class P1Input(BaseInput):

    def __init__(self):
        self.event_handler = EventHandler.instance()

    def jump(self) -> bool:
        return self.event_handler.is_key_down[pygame.K_w]

    def left(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_a]

    def right(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_d]

    def basic_attack(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_s]


class P2Input(BaseInput):

    def __init__(self):
        self.event_handler = EventHandler.instance()

    def jump(self) -> bool:
        return self.event_handler.is_key_down[pygame.K_UP]

    def left(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_LEFT]

    def right(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_RIGHT]

    def basic_attack(self) -> bool:
        return self.event_handler.is_key_pressing[pygame.K_DOWN]


class StartMenu(Entity):

    def __init__(self, sprites: Group, space: Space):
        super().__init__(sprites, space, Coord(0, -1000), Size(500, 1000))

        self.shape.collision_type = CollisionTypes.GROUND.value
        self.body.body_type = Body.KINEMATIC

        img = pygame.image.load("resources/startmenu.png").convert_alpha()
        img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
        self.image = img

        t = randrange(3_000, 10_000)
        self.timer = Timer(t)
        self.timer.start()

        self.up_timer = Timer(500)
        self.stop_timer = Timer(1000)
        self.down_timer = Timer(500)

        self.states = {
            "stop": 1,
            "up": 2,
            "down": 3
        }

        self.state = self.states["stop"]

        def move(body, gravity, damping, dt):
            if self.state == self.states["stop"]:
                body.velocity = (0, 0)
            elif self.state == self.states["up"]:
                body.velocity = (0, 1200)
            elif self.state == self.states["down"]:
                body.velocity = (0, -1200)
        self.body.velocity_func = move

    def update(self):
        super().update()

        if self.timer.over():
            self.timer.start()
            self.state = self.states["up"]
            self.up_timer.start()

        if self.up_timer.over():
            self.up_timer.stop()
            self.state = self.states["stop"]
            self.stop_timer.start()

        if self.stop_timer.over():
            self.stop_timer.stop()
            self.state = self.states["down"]
            self.down_timer.start()

        if self.down_timer.over():
            self.down_timer.stop()
            self.state = self.states["stop"]
            self.body.position = (0, -1000)


class Calendar(Entity):

    def __init__(self, sprites: Group, space: Space):
        super().__init__(sprites, space, Coord(1600, 75), Size(300, 400))

        self.shape.collision_type = CollisionTypes.GROUND.value
        self.body.body_type = Body.KINEMATIC

        img = pygame.image.load("resources/calender.png").convert_alpha()
        img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
        self.image = img

        t = randrange(3_000, 10_000)
        self.timer = Timer(t)
        self.timer.start()

        self.push_timer = Timer(300)
        self.stop_timer = Timer(1_000)
        self.pull_timer = Timer(300)

        self.states = {
            "stop": 1,
            "push": 2,
            "pull": 3
        }

        self.state = self.states["stop"]

        def move(body, gravity, damping, dt):
            if self.state == self.states["stop"]:
                body.velocity = (0, 0)
            elif self.state == self.states["push"]:
                body.velocity = (-1000, 0)
            elif self.state == self.states["pull"]:
                body.velocity = (1000, 0)
        self.body.velocity_func = move

    def update(self):
        super().update()

        if self.timer.over():
            self.timer.start()
            self.state = self.states["push"]
            self.push_timer.start()

        if self.push_timer.over():
            self.push_timer.stop()
            self.state = self.states["stop"]
            self.stop_timer.start()

        if self.stop_timer.over():
            self.stop_timer.stop()
            self.state = self.states["pull"]
            self.pull_timer.start()

        if self.pull_timer.over():
            self.pull_timer.stop()
            self.state = self.states["stop"]
            self.body.position = (1600, 75)


class Taskbar(Entity):

    def __init__(self, sprites: Group, space: Space):
        super().__init__(sprites, space, Coord(0, 0), Size(1600, 50))

        self.shape.collision_type = CollisionTypes.GROUND.value
        self.body.body_type = Body.STATIC

        img = pygame.image.load("resources/taskbar.png").convert_alpha()
        img = pygame.transform.scale(img, (self.rect.width, self.rect.height))
        self.image = img


class Icon(Entity):

    def __init__(self, sprites: Group, space: Space, pos: Coord, img: Surface):
        super().__init__(sprites, space, pos, Size(40, 40))

        self.shape.collision_type = CollisionTypes.GROUND.value
        self.body.body_type = Body.STATIC

        self.image = img


class WindowsMap(BaseMap):

    def __init__(self, sprites: Group):
        super().__init__(sprites)

        background = pygame.image.load("resources/background.png").convert_alpha()
        background = pygame.transform.scale(background, Screen.instance().size)
        self.background = background

        StartMenu(self.sprites, self.space)
        Calendar(self.sprites, self.space)
        Taskbar(self.sprites, self.space)

        icons = []
        for i in range(1, 12):
            icon = pygame.image.load(f"resources/icon{i:02d}.png").convert_alpha()
            icons.append(pygame.transform.scale(icon, Size(40, 40).to_px()))

        for i in range(3):
            for j in range(10):
                icon = randrange(0, 11)
                Icon(self.sprites, self.space, Coord(j * 120 + 250, i * 230 + 120), icons[icon])

        self.player1 = CppCharacter(self.sprites, self.space, Coord(0, 100), P1Input())
        self.player2 = PythonCharacter(self.sprites, self.space, Coord(1550, 100), P2Input())
