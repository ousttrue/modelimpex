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
        case ":class:`Color`":
            return "Color"
        case ":class:`Euler`":
            return "Euler"
        case ":class:`Vector` of size 3":
            return "tuple[float, float, float]"
        case ":class:`Quaternion`":
            return "Quaternion"
        case ":class:`Matrix`":
            return "Matrix"
        case "(:class:`Vector`, :class:`Quaternion`, :class:`Vector`)":
            return "tuple[Vector, Quaternion, Vector]"
        case "(:class:`Vector`, float) pair":
            return "tuple[Vector, float]"
        case "(:class:`Quaternion`, float) pair":
            return "tuple[Quaternion, float]"
        case ":class:`Vector` or float when 2D vectors are used":
            return "Vector | float"
        case "tuple":
            # ?
            return "tuple"
        case _:
            m = re.match(r"string in (\[[^]]*\])", src)
            if m:
                return "Literal" + m.group(1)
            raise NotImplemented()


def parse_attribute(src: str | None) -> str | None:
    if not src:
        return
    t: list[str] = []
    for l in src.splitlines():
        if l.startswith(":type:"):
            t.append(to_type(l[6:].strip()))
    return ", ".join(t)


def parse_func(src: str | None) -> tuple[str, str] | None:
    if not src:
        return

    ret = "None"
    for l in src.splitlines():
        l = l.lstrip()
        if l.startswith(":rtype:"):
            ret = to_type(l[7:].strip())

    match src:
        case "Return self+value.":
            return "self", "Self"
        case "Implement delattr(self, name)":
            return "self, name: str", "None"
        case _:
            return "self", ret


def to_param(src: str) -> tuple[str, str]:
    match src:
        case ":type rgb: 3d vector":
            return "rgb", "tuple[float, float, float]"
        case ":type angles: 3d vector":
            return "angles", "tuple[float, float, float]"
        case ":type order: str":
            return "order", "str"
        case ":type rows: 2d number sequence":
            return "rows", "list[float]"
        case ":type seq: :class:`Vector`":
            return "seq", "list[Vector]"
        case ":type angle: float":
            return "angle", "float"
        case ":type seq: sequence of numbers":
            return "seq", "list[float]"
        case _:
            raise RuntimeError()


def get_default(src: str, param_name: str) -> str | None:
    m = re.search(param_name + r"=('[^']*')", src)
    if m:
        return m.group(1)


def parse_constructor(src: str) -> str:
    lines: list[str] = []
    for l in src.splitlines():
        l = l.lstrip()
        if l.startswith(":arg "):
            lines.append(l)
        if l.startswith(":type "):
            assert lines[-1].startswith(":arg ")
            lines.append(l)

    args = ["self"]
    for i in range(0, len(lines), 2):
        param_name, param_type = to_param(lines[i + 1])
        param_default = get_default(src, param_name)
        if param_default:
            args.append(f"{param_name}:{param_type}={param_default}")
        else:
            args.append(f"{param_name}:{param_type}")
    return ",".join(args)


class StubGenerator:
    def __init__(self, output: pathlib.Path) -> None:
        self.output = output

    def generate(self):
        pyi = self.output / "mathutils.pyi"
        with pyi.open("w", encoding="utf-8") as f:
            f.write(
                f"""
from typing import Literal, Self
"""
            )
            for k, v in inspect.getmembers(mathutils, inspect.isclass):
                self._write_class(f, k, v)

    def _write_class(self, f: io.TextIOBase, name: str, klass: type):
        f.write(
            f"""
class {name}:
"""
        )

        # attribute
        for k, v in inspect.getmembers(klass, inspect.isgetsetdescriptor):
            type_str = parse_attribute(v.__doc__)
            if type_str:
                f.write(f"    {k}: {type_str}\n")

        args = parse_constructor(klass.__doc__)
        f.write(
            f"""
    def __init__({args})->None:
        ...
"""
        )

        # functions
        for k, v in inspect.getmembers(klass, inspect.ismethoddescriptor):
            if not v.__doc__:
                continue
            if k == "__init__":
                continue
                pass
            args, ret = parse_func(v.__doc__)
            if ret:
                f.write(f"    def {k}({args})->{ret}:\n")
                f.write(f"        ...\n")


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
