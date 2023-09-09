from pygame import Surface, draw
from pygame.sprite import DirtySprite

from scenes.common import FPS, RatioRect, render_text
from scenes.maps import WindowsMap, Character
from system.scenes import Scenes, BaseScene, State
from system.screen import Screen


class HPBar(DirtySprite):

    # dir is "left" or "right"
    def __init__(self, rect: RatioRect, player: Character, dir: str):
        super().__init__()
        self.rect = rect.to_pyrect()
        self.dir = dir
        self.player = player
        self.image = self._create_surface()
        self.dirty = 2

    def _create_surface(self) -> Surface:
        surface = Surface(self.rect.size)

        surface.fill("purple")

        hp = self.player.hp / self.player.full_hp

        if hp > 0:
            width = int(hp * self.rect.width)

            rect = self.rect.copy()
            rect.width = width

            if self.dir == "left":
                rect.left = surface.get_rect().left
            elif self.dir == "right":
                rect.right = surface.get_rect().right
            else:
                assert False, "Invalid, dir"

            draw.rect(surface, "red", rect)

            text = render_text(
                f"{int(self.player.hp)} / {int(self.player.full_hp)}".rjust(9),
                self.rect.height // 2
            )
            dest = text.get_rect(center=surface.get_rect().center)
            surface.blit(text, dest)

        return surface

    def update(self):
        self.image = self._create_surface()


class PlayScene(BaseScene):

    def __init__(self):
        super().__init__()

        self.state = State.PLAYING

        self.map = WindowsMap(self.sprites)

        hp1rect = RatioRect(0, 0, 0.4, 0.05)
        hp1rect.right = 0.5
        hp1rect.top = 0
        self.sprites.add(HPBar(hp1rect, self.map.player1, "left"))

        hp2rect = RatioRect(0, 0, 0.4, 0.05)
        hp2rect.left = 0.5
        hp2rect.top = 0
        self.sprites.add(HPBar(hp2rect, self.map.player2, "right"))

        self.sprites.add(FPS(RatioRect(0, 0, 0.04, 0.03)))

    def update(self):
        super().update()

        if (self.map.player1.hp <= 0
            or self.map.player2.hp <= 0):
            scenes = Scenes.instance()

            winner = ""
            if self.map.player1.hp <= 0:
                winner = "Player 2"
            elif self.map.player2.hp <= 0:
                winner = "Player 1"
            else:
                assert False
            
            from scenes.game_over_scene import GameOverScene
            scenes.change_scene(GameOverScene(winner))

        self.map.update()
        self.sprites.update()

    def render(self):

        screen = Screen.instance()
        screen.render(self.background, self.sprites)
