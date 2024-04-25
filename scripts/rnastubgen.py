"""
generate pyi from rna_info
"""

import bpy  # type: ignore
import rna_info  #  type: ignore

from typing import Any, Iterator, List
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


class StructStubGenerator:
    def __init__(
        self,
        output: pathlib.Path,
        structs: dict[tuple[str, str], Any],
    ) -> None:
        self.output = output
        self.dependencies = []
        self.structs = structs
        self.resolved: set[str] = set()

    def generate(self):
        names: List[str] = []
        for _, name in self.structs.keys():
            for d in self._resolve_dependency(name):
                names.append(d)

        mod_map: dict[str, List[str]] = {}
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
        self.resolved.add(name)

        s = self.structs.get(("", name))  # type: ignore
        if s:
            if s.base:
                for child in self._resolve_dependency(s.base.identifier):
                    yield child
            for p in s.properties:
                match p.type:
                    case "pointer":
                        for child in self._resolve_dependency(p.fixed_type.identifier):
                            yield child
                    case "collection":
                        for child in self._resolve_dependency(p.fixed_type.identifier):
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
                return f"List[{v.fixed_type.identifier}]"

            case _:
                match v.array_length:
                    case 0:
                        return v.type
                    case _:
                        return "tuple[" + ",".join([v.type] * v.array_length) + "]"

    def _create_struct(self, f: io.TextIOBase, name: str):
        s = self.structs[("", name)]
        f.write(
            f"""
                
class {s.identifier}({s.base.identifier if s.base else ""}):
    ...
"""
        )
        for _, v in enumerate(s.properties):
            # if i == 0:
            #     for d in dir(v):
            #         print(d)
            f.write(f"    {v.identifier}: {self._type_str(v)}\n")

    def _create_module(self, k: str, v: List[str]):
        pyi = self.output / (k.replace(".", "/") + ".pyi")
        # bpy_types_init = bpy / "types.pyi"
        pyi.parent.mkdir(parents=True, exist_ok=True)
        with pyi.open("w", encoding="utf-8") as f:
            f.write(
                """
from typing import List, Literal

"""
            )
            for d in v:
                self._create_struct(f, d)


class OperatorStubGenerator:
    def __init__(
        self,
        output: pathlib.Path,
        ops: dict[tuple[str, str], Any],
    ) -> None:
        self.output = output
        self.ops = ops

    def generate(self):
        mod_map: dict[str, List[str]] = {}
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

        def quote(src: str) -> str:
            return '"' + src + '"'

        with (ops_dir / "__init__.py").open("w", encoding="utf-8") as f:
            f.write(
                f"""
__all__ = [{','.join(quote(x) for x in mod_map.keys())}]
"""
            )
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
from . import data
from . import context
from . import types
from . import props
from . import ops # py
"""
        )

    sg = StructStubGenerator(args.output, structs)  # type: ignore
    sg.generate()

    og = OperatorStubGenerator(args.output, ops)  # type: ignore
    og.generate()

    # for parent, name in props:
    #     print(parent, name)
    # bpy/data.py => bpy.types.BlendData
    # print(type(bpy.data), bpy.data)
    for d in dir(bpy):
        a = getattr(bpy, d)
        print(d, type(a), a)
    # print(bpy.props)


if __name__ == "__main__":
    main()
