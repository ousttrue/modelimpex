from typing import Iterator
from PIL import Image  # type: ignore
import io


def load(mime: str, data: bytes, yflip: bool) -> tuple[int, int, list[float]]:
    img = Image.open(io.BytesIO(data))

    if yflip:
        img = img.flip()

    w, h = img.size

    # numpy ?
    def gen() -> Iterator[float]:
        for r, g, b, a in img.getdata():
            yield r / 255
            yield g / 255
            yield b / 255
            yield a / 255

    return w, h, [x for x in gen()]
