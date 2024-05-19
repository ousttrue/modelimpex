from typing import NamedTuple
import pathlib


class TextureData(NamedTuple):
    name: str
    data: bytes
    mime: str


class Texture(NamedTuple):
    data: TextureData | pathlib.Path

    @property
    def name(self) -> str:
        return self.data.name


class Material:
    def __init__(self, name: str):
        self.name = name
        self.color_texture: int | None = None
