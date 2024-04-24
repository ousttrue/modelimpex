import bpy  # type: ignore
import mathutils  # type: ignore

import logging
import argparse
import pathlib
import inspect
import re
import io

LOGGER = logging.getLogger(__name__)


def to_type(src: str) -> str:
    match src:
        case "float":
            return "float"
        case "float triplet":
            return "tuple[float, float, float]"
        case "boolean" | "bool":
            return "bool"
        case "Matrix Access":
            return "tuple[float,float,float,float,float,float,float,float,float,float,float,float,float,float,float,float]"
        case "Vector" | ":class:`Vector`":
            return "Vector"
        case _:
            m = re.match(r"string in (\[[^]]*\])", src)
            if m:
                return "Literal" + m.group(1)
            raise NotImplemented()


def parse_doc(src: str | None) -> str | None:
    if not src:
        return
    t: list[str] = []
    for l in src.splitlines():
        if l.startswith(":type:"):
            t.append(to_type(l[6:].strip()))
    return ", ".join(t)


class StubGenerator:
    def __init__(self, output: pathlib.Path) -> None:
        self.output = output

    def generate(self):
        pyi = self.output / "mathutils.pyi"
        with pyi.open("w", encoding="utf-8") as f:
            f.write(
                f"""
from typing import Literal
"""
            )
            for k, v in inspect.getmembers(mathutils, inspect.isclass):
                self._write_class(f, k, v)

    def _write_class(self, f: io.TextIOBase, name: str, klass: type):
        f.write(
            f"""
class {name}:
    ...
"""
        )

        # attribute
        for k, v in inspect.getmembers(klass, inspect.isgetsetdescriptor):
            type_str = parse_doc(v.__doc__)
            if type_str:
                f.write(f"    {k}: {type_str}\n")


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        prog="rnastubgen",
        description="generate pyi from blender rna_info",
    )
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()

    g = StubGenerator(args.output)
    g.generate()


if __name__ == "__main__":
    main()
