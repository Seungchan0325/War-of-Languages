from scenes.common import Title
from scenes.title_scene import TitleScene
from system.event_handler import EventHandler
from system.scenes import BaseScene, Scenes
from system.screen import Screen


class LoadingScene(BaseScene):

    def __init__(self):
        super().__init__()
        self.sprites.add(Title())

    def update(self):
        super().update()

        self.sprites.update()

        event_handler = EventHandler.instance()
        if event_handler.is_key_updated or event_handler.is_mouse_updated:
            scenes = Scenes.instance()
            scenes.change_scene(TitleScene())

    def render(self):
        screen = Screen.instance()
        screen.render(self.background, self.sprites)
