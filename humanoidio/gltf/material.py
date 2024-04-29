import pathlib


class Material:
    def __init__(self, name: str):
        self.name = name
        self.color_texture: pathlib.Path | None = None
