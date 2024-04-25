"""
generate pyi from rna_info
"""

import bpy  # type: ignore
import rna_info  #  type: ignore

from typing import Any, Iterator
import io
import logging
import argparse
import pathlib

LOGGER = logging.getLogger(__name__)

INCLUDE_MODULES = [
    "bpy.types",
    "cycles",
    "cycles.properties",
    "bl_operators.wm",
    "bl_operators.node",
]


def quote(src: str) -> str:
    return '"' + src + '"'


class StructStubGenerator:
    def __init__(
        self,
        output: pathlib.Path,
        structs: dict[tuple[str, str], Any],
    ) -> None:
        self.output = output
        self.dependencies = []
        self.structs = structs
        self.resolved: dict[str, set[str]] = {}

    def generate(self):
        names: list[str] = []
        for _, name in self.structs.keys():
            for d in self._resolve_dependency(name):
                names.append(d)

        mod_map: dict[str, list[str]] = {}
        for name in names:
            s = self.structs[("", name)]
            mod = mod_map.get(s.module_name)
            if not mod:
                mod = []
                mod_map[s.module_name] = mod
            mod.append(name)

        # print(mod_map)
        for k, v in mod_map.items():
            if k in INCLUDE_MODULES:
                LOGGER.info(f"create: {k}")
                self._create_module(k, v)
            else:
                LOGGER.warning(f"skip: {k}")

    def _resolve_dependency(self, name: str) -> Iterator[str]:
        if name in self.resolved:
            return
        deps: set[str] = set()
        self.resolved[name] = deps

        s = self.structs.get(("", name))  # type: ignore
        if s:
            if s.base:
                deps.add(s.base.identifier)
                for child in self._resolve_dependency(s.base.identifier):
                    yield child
            for p in s.properties:
                match p.type:
                    case "pointer":
                        deps.add(p.fixed_type.identifier)
                        for child in self._resolve_dependency(p.fixed_type.identifier):
                            yield child
                    case "collection":
                        # if p.name == 'children':
                        #     pass
                        if p.collection_type:
                            deps.add(p.collection_type.identifier)
                            for child in self._resolve_dependency(
                                p.collection_type.identifier
                            ):
                                yield child
                        else:
                            deps.add(p.fixed_type.identifier)
                            for child in self._resolve_dependency(
                                p.fixed_type.identifier
                            ):
                                yield child
                    case _:
                        pass

            yield name

    def _type_str(self, v: Any):
        match v.type:
            case "boolean":
                return "bool"

            case "string":
                return "str"

            case "enum":
                return (
                    "Literal["
                    + ",".join([f"'{name}'" for name, _, _ in v.enum_items])
                    + "]"
                )

            case "pointer":
                return v.fixed_type.identifier
                # raise NotImplemented()

            case "collection":
                # return f"bpy_prop_collection[{v.fixed_type.identifier}]"
                if v.collection_type:
                    return v.collection_type.identifier
                else:
                    return v.fixed_type.identifier

            case _:
                match v.array_length:
                    case 0:
                        return v.type
                    case _:
                        return "tuple[" + ",".join([v.type] * v.array_length) + "]"

    def _create_struct(self, f: io.TextIOBase, name: str):
        s = self.structs[("", name)]

        if name == "BlendDataObjects":
            pass

        f.write("from typiing import Literal # type: ignore\n")

        if s.base:
            base_struct = s.base.identifier
        elif s.description.startswith("Collection of "):
            item_type = name[:-1]
            f.write(f"from .{item_type} import {item_type}\n")
            base_struct = f"bpy_prop_collection[{item_type}]"
            f.write(f"from .bpy_prop_collection import bpy_prop_collection\n")
        else:
            base_struct = "bpy_struct"
            f.write(f"from .bpy_struct import bpy_struct\n")

        deps = self.resolved[name]
        for d in deps:
            if d == name:
                continue
            if d == "CyclesObjectSettings":
                continue
            f.write(f"from .{d} import {d}\n")

        f.write(
            f"""
class {s.identifier}({base_struct}):
    ...
"""
        )
        for _, v in enumerate(s.properties):
            if v.identifier == "active_object":
                pass
            f.write(f"    {v.identifier}: {self._type_str(v)}\n")

        for m in s.functions:
            if m.identifier == "new":
                pass
            f.write(f"    def {m.identifier}(self)->None: ...\n")

    def _create_module(self, k: str, v: list[str]):
        pyi_dir = self.output / (k.replace(".", "/"))
        # bpy_types_init = bpy / "types.pyi"
        pyi_dir.mkdir(parents=True, exist_ok=True)
        pyi = pyi_dir / "__init__.py"
        with pyi.open("w", encoding="utf-8") as f:
            f.write("__all__ = [")
            f.write(",".join([quote(x) for x in v]))
            f.write("]\n")
            for x in v:
                f.write(f"from .{x} import {x}\n")

        for x in v:
            with (pyi_dir / f"{x}.pyi").open("w", encoding="utf-8") as f:
                self._create_struct(f, x)


class OperatorStubGenerator:
    def __init__(
        self,
        output: pathlib.Path,
        ops: dict[tuple[str, str], Any],
    ) -> None:
        self.output = output
        self.ops = ops

    def generate(self):
        mod_map: dict[str, list[str]] = {}
        for _, name in self.ops.keys():
            op = self.ops[("", name)]
            mod = mod_map.get(op.module_name)
            if not mod:
                mod = []
                mod_map[op.module_name] = mod
            mod.append(name)

        ops_dir = self.output / f"bpy/ops"
        for k, v in mod_map.items():
            pyi = ops_dir / f"{k}.pyi"
            pyi.parent.mkdir(exist_ok=True, parents=True)
            with pyi.open("w", encoding="utf-8") as f:
                f.write(
                    """
"""
                )
                for op_name in v:
                    self._create_op(f, op_name)

        with (ops_dir / "__init__.py").open("w", encoding="utf-8") as f:
            f.write("__all__ = [")
            f.write(",".join(quote(x) for x in mod_map.keys()))
            f.write("]\n")
            for x in mod_map.keys():
                f.write(f"from . import {x}\n")

    def _create_op(self, f: io.TextIOBase, name: str):
        op = self.ops[("", name)]
        f.write(
            f"""
def {op.func_name}()->None:
    ...
"""
        )


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        prog="rnastubgen",
        description="generate pyi from blender rna_info",
    )
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()

    structs, funcs, ops, props = rna_info.BuildRNAInfo()  # type: ignore

    bpy_dir = args.output / "bpy"
    bpy_init = bpy_dir / "__init__.pyi"
    bpy_init.parent.mkdir(parents=True, exist_ok=True)
    with bpy_init.open("w", encoding="utf-8") as f:
        f.write(
            """
__all__ = [
    'types',
    'data',
    'ops',
    'context',
    'props',
]
from . import types

class View3DContext(types.Context):
    active_object: types.Object
    selected_ids: sequence[bpy.types.ID]

data: types.BlendData
context: View3DContext
from . import props
from . import ops # py
"""
        )

    bpy_struct_pyi = bpy_dir / "types/bpy_struct.pyi"
    bpy_struct_pyi.parent.mkdir(parents=True, exist_ok=True)
    with bpy_struct_pyi.open("w", encoding="utf-8") as f:
        f.write(
            """import bpy

class bpy_struct:
    def keyframe_insert(self, data_path: str, index: int=- 1, frame: int=bpy.context.scene.frame_current, group: str='', options: set[str]=set())->bool: ...
"""
        )

    bpy_prop_collection_pyi = bpy_dir / "types/bpy_prop_collection.pyi"
    bpy_prop_collection_pyi.parent.mkdir(parents=True, exist_ok=True)
    with bpy_prop_collection_pyi.open("w", encoding="utf-8") as f:
        f.write(
            """
from typing import Generic, TypeVar

T = TypeVar("T")

class bpy_prop_collection(Generic[T]):
    def __getitem__(self, key: int|str)->T:...
"""
        )

    sg = StructStubGenerator(args.output, structs)  # type: ignore
    sg.generate()

    og = OperatorStubGenerator(args.output, ops)  # type: ignore
    og.generate()

    # for parent, name in props:
    #     print(parent, name)
    # bpy/data.py => bpy.types.BlendData
    # for d in dir(bpy):
    #     a = getattr(bpy, d)
    #     print(d, type(a), a)
    print(type(bpy.context), bpy.context)
    # print(bpy.props)


if __name__ == "__main__":
    main()
