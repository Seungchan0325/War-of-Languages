from dataclasses import dataclass

import pygame
from pygame import Surface

from game_config import GameConfig
from scenes.common import Button, ButtonList, RatioRect, render_text
from scenes.play_scene import PlayScene
from system.network import Network
from system.scenes import BaseScene, Scenes, State, STATE_QUERY


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
        super().__init__(rect)

        self.nickname = nickname
        self.ip = ip
        self.port = port
        self.addr = (ip, port)
        self.state: State = State.UNKNOWN

        network = Network.instance()
        network.conn(self.addr)
        self._is_sent = False

        self.image = self._create_surface()

    def _create_surface(self) -> Surface:
        # Make Surface
        surface = Surface(self.rect.size)
        if self.is_on_mouse():
            surface.fill("red")
        else:
            surface.fill("purple")

        # Make state
        state_size = (self.rect.height * 0.8, self.rect.height * 0.8)
        state = Surface(state_size)
        if self.state == State.ONLINE:
            state.fill("green")
        elif self.state == State.PLAYING:
            state.fill("orange")
        else:
            state.fill("red")

        dest = state.get_rect(
            right=surface.get_rect().right,
            centery=surface.get_rect().centery
        )

        dest.right -= surface.get_rect().height * 0.2 / 2

        surface.blit(state, dest)

        # Make nickname
        rendered_nickname = render_text(self.nickname, self.rect.height)
        dest = rendered_nickname.get_rect(
            left=surface.get_rect().left,
            centery=surface.get_rect().centery
        )

        dest.left += surface.get_rect().width * 0.03

        surface.blit(rendered_nickname, dest)

        return surface

    def _check_state(self) -> State:
        network = Network.instance()

        # Check if is connected
        if not network.is_conn(self.addr):
            if self.addr in network.refused:
                network.refused.remove(self.addr)
                return State.OFFLINE
            return State.UNKNOWN

        # Send query
        if not self._is_sent:
            network.send_by_addr(self.addr, STATE_QUERY)
            self._is_sent = True
            return State.UNKNOWN

        data = network.recv_by_addr(self.addr)

        if not data:
            return State.UNKNOWN

        if State.ONLINE.state in data:
            data.remove(State.ONLINE.state)
            return State.ONLINE

        if State.PLAYING.state in data:
            data.remove(State.PLAYING.state)
            return State.PLAYING

        assert False, "Wrong recv"

    def update(self):
        if self.state == State.UNKNOWN:
            state = self._check_state()
            if state != State.UNKNOWN:
                self.state = state
                self.dirty = 1
                self.image = self._create_surface()

        if self.mouse_enter() or self.mouse_exit():
            self.dirty = 1
            self.image = self._create_surface()

        super().update()


class FriendList(ButtonList):

    def __init__(self, button_size: RatioRect):
        super().__init__(RatioRect(0.05, 0.1, 0.4, 0.9), button_size)
        self.selected_idx = 0

    def update(self):
        self.selected_idx = -self._scroll_cnt
        for i, button in enumerate(self.buttons):
            is_in_area = button.rect.colliderect(self.rect)
            if is_in_area and button.is_up_clicked(pygame.BUTTON_LEFT):
                self.selected_idx = i
                self._scroll_cnt = -i
                self._draw = True

        super().update()


class MapButton(Button):

    def __init__(self,
                 map_name: str,
                 rect: RatioRect):
        super().__init__(rect)

        self.map_name = map_name

        self.image = self._create_surface()


    def _create_surface(self) -> Surface:
        surface = Surface(self.rect.size)
        if self.is_on_mouse():
            surface.fill("gray")
        else:
            surface.fill("yellow")

        text = render_text(self.map_name, self.rect.height // 2)

        normal_rect = self.rect.copy()
        normal_rect.topleft = (0, 0)
        dest = text.get_rect(
            centerx=normal_rect.centerx,
            bottom=normal_rect.bottom,
        )

        surface.blit(text, dest)

        return surface

    def update(self):
        if self.mouse_enter() or self.mouse_exit():
            self.dirty = 1
            self.image = self._create_surface()

        super().update()


class MapList(ButtonList):

    def __init__(self, button_size: RatioRect):
        super().__init__(RatioRect(0.55, 0.1, 0.4, 0.9), button_size)
        self.selected_idx = 0

    def update(self):
        self.selected_idx = -self._scroll_cnt
        for i, button in enumerate(self.buttons):
            is_in_area = button.rect.colliderect(self.rect)
            if is_in_area and button.is_up_clicked(pygame.BUTTON_LEFT):
                self.selected_idx = i
                self._scroll_cnt = -i
                self._draw = True

        super().update()


class PlayButton(Button):

    def __init__(self, rect: RatioRect,
                 friend_list: FriendList,
                 map_list: MapList):
        super().__init__(rect)

        self._friend_list = friend_list
        self._map_list = map_list

        self.image = self._create_surface()

    def _create_surface(self):
        surface = Surface(self.rect.size)
        if self.is_on_mouse():
            surface.fill("red")
        else:
            surface.fill("purple")

        text = render_text("Play", self.rect.height // 2)

        normal_rect = self.rect.copy()
        normal_rect.topleft = (0, 0)
        dest = text.get_rect(
            center=normal_rect.center
        )

        surface.blit(text, dest)
        return surface

    def update(self):
        if self.mouse_enter() or self.mouse_exit():
            self.image = self._create_surface()
            self.dirty = 1

        if self.is_up_clicked(pygame.BUTTON_LEFT):
            selected_idx = self._friend_list.selected_idx
            selected = self._friend_list.buttons[selected_idx]
            if selected.state == State.ONLINE:
                scenes = Scenes.instance()
                scenes.change_scene(PlayScene())
        super().update()


class SelectionScene(BaseScene):

    def __init__(self):
        super().__init__()

        friend_button_size = RatioRect(0, 0, 0.4, 0.05)
        self.friend_list = FriendList(friend_button_size)
        self.sprites.add(self.friend_list)

        config = GameConfig.instance()
        friends = read_csv(config.friends_file_path)

        # friend[0] is field name
        for nickname, ip, port in friends[1:]:
            button = FriendButton(nickname, ip, int(port), friend_button_size)
            self.friend_list.add_button(button)

        map_button_size = RatioRect(0.55, 0.1, 0.4, 0.4)
        self.map_list = MapList(map_button_size)
        self.sprites.add(self.map_list)
        self.map_list.add_button(MapButton("1", map_button_size))
        self.map_list.add_button(MapButton("2", map_button_size))
        self.map_list.add_button(MapButton("3", map_button_size))
        self.map_list.add_button(MapButton("4", map_button_size))
        self.map_list.add_button(MapButton("5", map_button_size))

        play_button_size = RatioRect(0, 0.1, 0.1, 0.1)
        play_button_size.centerx = 0.5
        self.sprites.add(PlayButton(play_button_size,
                                    self.friend_list,
                                    self.map_list))

    def update(self):
        super().update()

        self.sprites.update()
