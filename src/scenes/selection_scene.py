import pygame
from pygame.sprite import DirtySprite, LayeredDirty

from game_config import GameConfig
from system.event_handler import EventHandler
from system.scenes import BaseScene, Scenes
from system.control.button import Button, ButtonList
from system.screen import Screen, RatioRect
from scenes.play_scene import PlayScene


def read_csv(file_path: str) -> list[list]:
    ret = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # remove newline
            line = line.strip()
            ret.append(line.split(", "))

    return ret


def append_csv(file_path: str, data: list):
    with open(file_path, "a", encoding="utf-8") as file:
        data_str = ", ".join(data)
        file.write(data_str)
        file.write("\n")


class FriendButton(Button):

    def __init__(self,
                 nickname: str,
                 ip: str,
                 port: str,
                 rect: RatioRect):
        super().__init__(rect.to_pyrect())

        self._prev_is_on = self.is_on_mouse()

        self.nickname = nickname
        self.ip = ip
        self.port = port

        self._surface_on_mouse = pygame.Surface(self.rect.size)
        self._surface_not_on_mouse = pygame.Surface(self.rect.size)

        self._surface_on_mouse.fill("red")
        self._surface_not_on_mouse.fill("purple")

        text_color = (255, 255, 255)
        text_font = pygame.font.SysFont("arial", int(self.rect.height * 0.5))

        rendered_nickname = text_font.render(self.nickname, True, text_color)
        dest = rendered_nickname.get_rect(
            left=self._surface_on_mouse.get_rect().left,
            centery=self._surface_on_mouse.get_rect().centery
        )

        dest.left += Screen.instance().width * 0.01

        self._surface_on_mouse.blit(rendered_nickname, dest)
        self._surface_not_on_mouse.blit(rendered_nickname, dest)

        if self._prev_is_on:
            self.image = self._surface_on_mouse
        else:
            self.image = self._surface_not_on_mouse

    def update(self):
        if self._prev_is_on and not self.is_on_mouse():
            self.dirty = 1
            self.image = self._surface_not_on_mouse

        if not self._prev_is_on and self.is_on_mouse():
            self.dirty = 1
            self.image = self._surface_on_mouse

        self._prev_is_on = self.is_on_mouse()

        # if self.is_up_clicked(pygame.BUTTON_LEFT):
        #     scenes = Scenes.instance()
        #     scenes.change_scene(PlayScene())


class FriendList(ButtonList):

    def __init__(self, button_size: RatioRect):
        super().__init__(RatioRect(0.05, 0.1, 0.4, 0.9), button_size)
        self._selected_idx = 0

    def update(self):
        self._selected_idx = -self._scroll_cnt
        for i, button in enumerate(self.buttons):
            if button.is_up_clicked(pygame.BUTTON_LEFT):
                self._is_scrolled = True
                self._selected_idx = i
                self._scroll_cnt = -i

        super().update()


class SelectionScene(BaseScene):

    def __init__(self):
        super().__init__()

        button_size = RatioRect(0, 0, 0.4, 0.05)

        self.friend_list = FriendList(button_size)
        self.sprites.add(self.friend_list)

        config = GameConfig.instance()
        friends = read_csv(config.friends_file_path)

        # friend[0] is field name
        for nickname, ip, port in friends[1:]:
            button = FriendButton(nickname, ip, port, button_size)
            self.friend_list.add_button(button)

    def update(self):
        self.sprites.update()
