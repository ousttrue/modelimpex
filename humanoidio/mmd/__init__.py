import pathlib
from .pmd import load_pmd
from .pmx import load_pmx
from ..gltf.loader import Loader


__all__ = [
    "load_pmd",
    "load_pmx",
]


def from_path(path: pathlib.Path) -> Loader | None:
    match path.suffix:
        case ".pmd":
            return load_pmd(path, path.read_bytes())
        case ".pmx":
            return load_pmx(path, path.read_bytes())
        case _:
            return None
