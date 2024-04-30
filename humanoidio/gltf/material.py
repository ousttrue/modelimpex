from typing import NamedTuple


class Texture(NamedTuple):
    name: str
    mime: str
    data: bytes


class Material:
    def __init__(self, name: str):
        self.name = name
        self.color_texture: int | None = None
