"""
generate pyi from rna_info
"""

from typing import List, Any
import io
import bpy
import rna_info
import logging
import argparse
import pathlib

LOGGER = logging.getLogger(__name__)


def print_struct(name: str, s):
    print(name, type(s))
    for k in dir(s):
        print(k, getattr(s, k))


def type_str(v: Any):
    match v.type:
        case "boolean":
            return "bool"

        case "string":
            return "str"

        case "enum":
            return (
                "Literal["
                + ",".join([f"'{name}'" for name, value, desc in v.enum_items])
                + "]"
            )

        case "pointer":
            return "Any"
            # raise NotImplemented()

        case "collection":
            return "List[Any]"

        case _:
            return v.type


def create(f: io.TextIOBase, s: Any):
    f.write(
        f"""# generated
            
from typing import Any, List, Literal

class {s.identifier}:
    ...
"""
    )
    for i, v in enumerate(s.properties):
        if i == 0:
            for d in dir(v):
                print(d)
        f.write(f"    {v.identifier}: {type_str(v)}\n")


def generate(output: pathlib.Path):
    bpy = output / "bpy"
    bpy_init = bpy / "__init__.pyi"
    bpy_init.parent.mkdir(parents=True, exist_ok=True)
    with bpy_init.open("w", encoding="utf-8") as f:
        f.write(
            """
from . import types
"""
        )

    structs, funcs, ops, props = rna_info.BuildRNAInfo()

    bpy_types_init = bpy / "types.pyi"
    # bpy_types_init.parent.mkdir(parents=True, exist_ok=True)
    with bpy_types_init.open("w", encoding="utf-8") as f:
        create(f, structs[("", "Object")])  # type: ignore

    # for k, v in structs.items():
    #     if v.module_name == "bpy.types":
    #         print(f"{k[1]}")

    # for d in dir(structs[("", "Object")]):
    #     print(d)


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(
        prog="rnastubgen",
        description="generate pyi from blender rna_info",
    )
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()
    generate(args.output)


if __name__ == "__main__":
    main()
