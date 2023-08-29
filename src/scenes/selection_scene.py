import pygame
from pygame.sprite import DirtySprite

from game_config import GameConfig
from system.event_handler import EventHandler
from system.scenes import BaseScene, Scenes
from system.control.button import Button
from system.screen import Screen, RatioRect, create_rect
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
                 y_ratio: float):
        rect = create_rect(0.05, y_ratio, 0.4, 0.05)

        super().__init__(rect)

        self._y_ratio = y_ratio

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

    def position_update(self, y_ratio: float):
        if abs(self._y_ratio - y_ratio) < 1e-10:
            return

        screen = Screen.instance()
        self.dirty = 1
        self._y_ratio = y_ratio
        self.rect.top = int(screen.height * y_ratio)

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


# class ButtonList(DirtySprite):

#     def __init__(self,
#                  area: RatioRect,
#                  button_size: RatioRect):
#         super().__init__()

#         self.area = area

#         self.rect = self.area.to_pyrect()

#         self._scroll_cnt = 0
#         self._button_size = button_size

#         self.buttons: list[Button] = []

#     def _compute_position(self, index: int) -> RatioRect:
#         x = self.area.x
#         y = (index + self._scroll_cnt) * self._button_size.h + self.area.h
#         w = self.area.y
#         h = self._button_size.h
#         return RatioRect(x, y, w, h)

#     def add_button(self, button: Button):
#         self.buttons.append(button)

#     def update(self):
#         event_handler = EventHandler.instance()
#         if self.rect.collidepoint(event_handler.get_mouse_pos()):
#             if event_handler.mouse_scroll < 0 and self._scroll_cnt < 0:
#                 self._scroll_cnt += 1
#             elif event_handler.mouse_scroll > 0 and self._scroll_cnt > -len(self.buttons) + 1:
#                 self._scroll_cnt -= 1

#         for i, button in enumerate(self.buttons):
#             pos = self._compute_position(i)
#             button.position_update(pos)


class FriendList():

    def __init__(self):
        super().__init__()

        self._count = 0
        self.buttons: list[FriendButton] = []

        self._y_offset = 0.1
        self._scroll_cnt = 0

        self.selected_idx: int = 0

        # ratio
        self._button_height = 0.05

        self.rect = create_rect(0.05, self._y_offset, 0.4, 0.8)

    def compute_y_ratio(self, index: int):
        return (index + self._scroll_cnt) * self._button_height + self._y_offset

    def add_button(self, nickname: str, ip: str, port: str) -> FriendButton:
        y_ratio = self.compute_y_ratio(self._count)

        button = FriendButton(
            nickname,
            ip,
            port,
            y_ratio
        )

        self._count += 1

        self.buttons.append(button)
        return button

    def update(self):
        event_handler = EventHandler.instance()
        if self.rect.collidepoint(event_handler.get_mouse_pos()):
            if event_handler.mouse_scroll < 0 and self._scroll_cnt < 0:
                self._scroll_cnt += 1
            elif event_handler.mouse_scroll > 0 and self._scroll_cnt > -self._count + 1:
                self._scroll_cnt -= 1

        for i, button in enumerate(self.buttons):
            y_ratio = self.compute_y_ratio(i)
            button.position_update(y_ratio)
            if y_ratio < self._y_offset:
                button.visible = False
            else:
                button.visible = True

        self.selected_idx = -self._scroll_cnt

        for i, button in enumerate(self.buttons):
            if button.is_up_clicked(pygame.BUTTON_LEFT):
                self.selected_idx = i
                self._scroll_cnt = -i
                break


class SelectionScene(BaseScene):

    def __init__(self):
        super().__init__()

        self.friend_list = FriendList()

        config = GameConfig.instance()
        friends = read_csv(config.friends_file_path)

        # friend[0] is field name
        for nickname, ip, port in friends[1:]:
            button = self.friend_list.add_button(nickname, ip, port)
            self.sprites.add(button)

    def update(self):
        self.friend_list.update()
        self.sprites.update()
