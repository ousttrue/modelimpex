import pathlib
from .pmd import load_pmd, gltf_from_pmd
from .pmx import load_pmx, gltf_from_pmx
from ..gltf.loader import Loader


__all__ = [
    "load_pmd",
    "gltf_from_pmd",
    "load_pmx",
    "gltf_from_pmx",
]


def load_as_gltf(path: pathlib.Path, data: bytes | None = None) -> Loader | None:
    match path.suffix:
        case ".pmd":
            return gltf_from_pmd(path, data)
        case ".pmx":
            return gltf_from_pmx(path, data)
        case _:
            return None
