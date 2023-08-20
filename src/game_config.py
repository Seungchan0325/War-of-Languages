import dataclasses


@dataclasses.dataclass
class GameConfig:
    def __init__(
            self,
            caption: str,
            fps: int,
            screen_size: tuple[int, int]
    ):
        self.caption = caption
        self.fps = fps
        self.screen_size = screen_size
