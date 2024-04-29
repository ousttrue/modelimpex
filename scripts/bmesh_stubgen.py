import bpy  # type: ignore
import bmesh  # type: ignore

import logging
import argparse
import pathlib
import inspect
import re
import io

LOGGER = logging.getLogger(__name__)


def to_type(src: str) -> str:
    match src:
        case "Undefined" | "any":
            return "Any"
        case ":function: returning a number":
            return "Callable[[],float]"
        case "int":
            return "int"
        case "string":
            return "str"
        case "list":
            return "list[Any]"
        case "set":
            return "set[Any]"
        case "list of strings":
            return "list[str]"
        case "float":
            return "float"
        case "float triplet":
            return "tuple[float, float, float]"
        case "boolean" | "bool" | ":boolean:":
            return "bool"
        case "list of tuples":
            return "list[tuple[float,...]]"
        case "list of ints":
            return "list[int]"
        case "list of floats":
            return "list[float]"
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
        case ":class:`BMLoop`":
            return "BMLoop"
        case ":class:`BMVert`":
            return "BMVert"
        case ":class:`BMVert` or None":
            return "BMVert|None"
        case ":class:`bmesh.types.BMesh`":
            return "BMesh"
        case ":class:`BMEdge`":
            return "BMEdge"
        case ":class:`BMFace`":
            return "BMFace"
        case ":class:`BMLayerAccessEdge`":
            return "BMLayerAccessEdge"
        case ":class:`BMFace` or None":
            return "BMFace|None"
        case ":class:`BMElemSeq` of :class:`BMFace`":
            return "Iterator[BMFace]"
        case ":class:`BMElemSeq` of :class:`BMLoop`":
            return "Iterator[BMLoop]"
        case ":class:`BMElemSeq` of :class:`BMVert`":
            return "Iterator[BMVert]"
        case ":class:`BMElemSeq` of :class:`BMEdge`":
            return "Iterator[BMEdge]"
        case "pair of :class:`BMVert`":
            return "tuple[BMVert, BMVert]"
        case ":class:`BMVert`, :class:`BMEdge` or :class:`BMFace`":
            return "BMVert|BMEdge|BMFace"
        case ":class:`BMLayerAccessFace`":
            return "BMLayerAccessFace"
        case "sequence of :class:`BMVert`":
            return "Iterator[BMVert]"
        case ":class:`BMLayerCollection`":
            return "BMLayerCollection"
        case ":class:`BMLayerItem`":
            return "BMLayerItem"
        case ":class:`BMLayerAccessLoop`":
            return "BMLayerAccessLoop"
        case ":class:`BMLayerAccessVert`":
            return "BMLayerAccessVert"
        case ":class:`BMEdgeSeq`":
            return "BMEdgeSeq"
        case ":class:`BMFaceSeq`":
            return "BMFaceSeq"
        case ":class:`BMLoopSeq`":
            return "BMLoopSeq"
        case ":class:`BMEditSelSeq`":
            return "BMEditSelSeq"
        case ":class:`BMVertSeq`":
            return "BMVertSeq"
        case "list of :class:`BMLoop` tuples":
            return "list[tuple[BMLoop, ...]]"
        case ":class:`BMesh`":
            return "BMesh"
        #
        case "4x4 :class:`mathutils.Matrix`":
            return "mathutils.Matrix"
        case ":class:`mathutils.Vector`":
            return "mathutils.Vector"
        #
        case ":class:`bpy.types.Mesh`" | ":class:`Mesh`":
            return "bpy.types.Mesh"
        case ":class:`Object`":
            return "bpy.types.Object"
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
        if l.startswith("type:"):
            t.append(to_type(l[5:].strip()))
    if t:
        return ", ".join(t)

    pass


def parse_func(use_self: bool, src: str | None) -> tuple[str, str] | None:
    if not src:
        return

    args: list[str] = []
    if use_self:
        args.append("self")
    type_map: dict[str, str] = {}

    lines = src.splitlines()
    sig = lines.pop(0)

    def param_str(arg: str) -> str:
        if arg == "self":
            return "self"

        param_default = get_default(sig, arg)

        type_str = "Any"
        t = type_map.get(arg)
        if t:
            type_str = to_type(t)

        ret = f"{arg}: {type_str}"
        if param_default:
            ret += "=" + param_default
        return ret

    ret = "None"

    for l in lines:
        l = l.lstrip()

        if l.startswith(":rtype:"):
            ret = to_type(l[7:].strip())
        elif l.startswith(":arg "):
            arg, _desc = l[5:].split(":", 1)
            args.append(arg)
        elif l.startswith(":type "):
            arg, type_name = l[6:].split(":", 1)
            type_map[arg] = type_name.strip()
        else:
            pass

    return ",".join((param_str(arg) for arg in args)), ret


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

    m = re.search(param_name + r"=(\w+)", src)
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
        bmesh_dir = self.output / "bmesh"
        bmesh_dir.mkdir(parents=True, exist_ok=True)

        types_pyi = bmesh_dir / "types.pyi"
        with types_pyi.open("w", encoding="utf-8") as f:
            f.write(
                f"""
from typing import Iterator, Any, Callable
import mathutils                
import bpy
"""
            )

            for k, v in inspect.getmembers(bmesh.types, inspect.isclass):  # type: ignore
                self._write_class(f, k, v)

        init_pyi = bmesh_dir / "__init__.pyi"
        with init_pyi.open("w", encoding="utf-8") as f:
            f.write(
                f"""
import bpy
from .types import BMesh
"""
            )

            for k, v in inspect.getmembers(bmesh, inspect.isbuiltin):
                args, ret = parse_func(False, v.__doc__)  # type: ignore
                if ret:
                    f.write(f"def {k}({args})->{ret}:\n")
                    f.write(f"    ...\n")

    def _write_class(self, f: io.TextIOBase, name: str, klass: type):
        f.write(
            f"""
class {name}:
    ...
"""
        )

        # attribute
        for k, v in inspect.getmembers(klass, inspect.isgetsetdescriptor):
            type_str = parse_attribute(v.__doc__)
            if type_str:
                f.write(f"    {k}: {type_str}\n")

            else:
                pass

        #         args = parse_constructor(klass.__doc__)
        #         f.write(
        #             f"""
        #     def __init__({args})->None:
        #         ...
        # """
        #         )

        # functions
        for k, v in inspect.getmembers(klass, inspect.ismethoddescriptor):
            if not v.__doc__:
                continue
            if k.startswith("__"):
                continue
                pass
            args, ret = parse_func(True, v.__doc__)  # type: ignore
            if ret:
                f.write(f"    def {k}({args})->{ret}:\n")
                f.write(f"        ...\n")


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        prog="bmesh_stubgen",
        description="generate pyi from blender rna_info",
    )
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()

    g = StubGenerator(args.output)
    g.generate()


if __name__ == "__main__":
    main()
