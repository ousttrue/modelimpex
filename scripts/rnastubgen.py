"""
generate pyi from rna_info
"""

from functools import cmp_to_key
import functools
import re
import sys
import bpy  # type: ignore
import rna_info  #  type: ignore
from _bpy import rna_enum_items_static  #  type: ignore

rna_enum_dict = rna_enum_items_static()  #  type: ignore

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


def param_str(x: Any) -> str:
    if x.default_str:
        if x.default_str == "None":
            return f"{x.identifier}: {type_str(x)}|None=None"
        else:
            return f"{x.identifier}: {type_str(x)}={x.default_str}"
    else:
        return f"{x.identifier}: {type_str(x)}"


def type_str(v: Any):
    match v.subtype:
        case "MATRIX":
            return "mathutils.Matrix"
        case _:
            pass

    match v.type:
        case "boolean":
            return "bool"

        case "string":
            return "str"

        case "enum":
            if len(v.enum_items) == 0:
                return "str"
            else:
                return (
                    "Literal["
                    + ",".join([f"'{name}'" for name, _, _ in v.enum_items])
                    + "]"
                )

        case "pointer":
            return v.fixed_type.identifier
            # raise NotImplemented()

        case "collection":
            if v.collection_type:
                return v.collection_type.identifier
            else:
                return f"bpy_prop_collection[{v.fixed_type.identifier}]"

        case _:
            match v.array_length:
                case 0:
                    return v.type
                case _:
                    return "tuple[" + ",".join([v.type] * v.array_length) + "]"


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
        self.item_type: dict[str, str] = {}
        self.properties: list[str] = []

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
                            self.item_type[p.collection_type.identifier] = (
                                p.fixed_type.identifier
                            )
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

            for m in s.functions:
                for a in m.args:
                    if a.fixed_type:
                        deps.add(a.fixed_type.identifier)
                        for child in self._resolve_dependency(a.fixed_type.identifier):
                            yield child

                for r in m.return_values:
                    if r.fixed_type:
                        deps.add(r.fixed_type.identifier)
                        for child in self._resolve_dependency(r.fixed_type.identifier):
                            yield child

            yield name

    def _create_struct(self, f: io.TextIOBase, name: str):
        s = self.structs[("", name)]

        if name == "BlendDataObjects":
            pass

        f.write("from typing import Literal # type: ignore\n")
        f.write("import mathutils # type: ignore\n")
        f.write(f"from .bpy_prop_collection import bpy_prop_collection\n")

        if s.base:
            base_struct = s.base.identifier
            if base_struct == "Property":
                self.properties.append(s.identifier)
        elif name in self.item_type:
            item_type = self.item_type[name]
            f.write(f"from .{item_type} import {item_type}\n")
            base_struct = f"bpy_prop_collection[{item_type}]"
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
        for v in s.properties:
            f.write(f"    {v.identifier}: {type_str(v)}\n")

        # def sort_arg(a: Any, b: Any) -> int:
        #     if a.default and not b.default:
        #         return 1
        #     elif not a.default and b.default:
        #         return -1
        #     else:
        #         return 0

        for m in s.functions:
            args = ["self"] + [param_str(x) for x in m.args]
            return_values = [type_str(x) for x in m.return_values]
            match len(return_values):
                case 0:
                    return_str = "None"
                case 1:
                    return_str = return_values[0]
                case _:
                    return_str = "tuple[" + ",".join(return_values) + "]"
            f.write(f"    def {m.identifier}({','.join(args)})->{return_str}: ...\n")

    def _create_module(self, k: str, v: list[str]):
        pyi_dir = self.output / (k.replace(".", "/"))
        # bpy_types_init = bpy / "types.pyi"
        pyi_dir.mkdir(parents=True, exist_ok=True)
        pyi = pyi_dir / "__init__.py"
        with pyi.open("w", encoding="utf-8") as f:
            f.write("__all__ = ['bpy_prop_collection'. ")
            f.write(",".join([quote(x) for x in v]))
            f.write("]\n")
            f.write(f"from .bpy_prop_collection import bpy_prop_collection\n")
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
from typing import Literal # type: ignore
"""
                )
                for op_name in v:
                    for d in self._op_dependency(op_name):
                        f.write(f"from bpy.types import {d}\n")

                for op_name in v:
                    self._create_op(f, op_name)

        with (ops_dir / "__init__.py").open("w", encoding="utf-8") as f:
            f.write("__all__ = [")
            f.write(",".join(quote(x) for x in mod_map.keys()))
            f.write("]\n")
            for x in mod_map.keys():
                f.write(f"from . import {x}\n")

    def _op_dependency(self, name: str) -> Iterator[str]:
        op = self.ops[("", name)]
        for arg in op.args:
            if arg.fixed_type:
                yield arg.fixed_type.identifier

    def _create_op(self, f: io.TextIOBase, name: str):
        op = self.ops[("", name)]

        args = [param_str(x) for x in op.args]
        f.write(
            f"""
def {op.func_name}({','.join(args)})->None:
    ...
"""
        )


def write_property_function(f: io.IOBase, name: str, doc: str) -> None:
    lines = doc.splitlines()

    l = lines.pop(0)
    m = re.match(r"^\.\. function:: (\w+)\((.*)\)$", l)
    assert m
    assert m.group(1) == name

    def ret_kv(*_: Any, **kv: Any) -> dict[str, Any]:
        return kv

    # sp = [x.split("=", 1) for x in .split(",")]
    # print(l, sp)
    # defaults: dict[str, str] = {k.strip(): v.strip() for k, v in sp}
    defaults = eval(
        f"ret_kv({m.group(2)})", {"items": None, "sys": sys}, {"ret_kv": ret_kv}
    )

    type_map = {
        "string": "str",
        "int": "int",
        "float": "float",
        "set": "set[str]",
        "function": "Callable[[], None]|None",
        "sequence": "list[Any]",
        "int or int sequence": "int|list[int]",
        "class": "type|None",
        "sequence of string tuples or a function": "list[tuple[str]]|Callable[[], None]|None",
        "string, integer or set": "str|int|set[str]|None",
    }

    def value_str(src: str) -> str:
        if src[0] == "(" and src[-1] == ")":
            return "[" + src[1:-1] + "]"

        return src

    # def arg_order(a: str, b: str) -> int:
    #     if "=" in a and "=" not in b:
    #         return 1
    #     elif "=" not in a and "=" in b:
    #         return -1
    #     return 0

    args: list[str] = []
    for l in lines:
        m = re.match(r":type (\w+):(.*)", l.lstrip())
        if m:
            arg_name = m.group(1)
            if arg_name == "translation_context":
                if name == "BoolProperty":
                    # ?
                    args.append("default:bool=False")
                continue
            arg_type = m.group(2).strip()
            if arg_name in defaults:
                args.append(
                    f"{arg_name}:{type_map[arg_type]}={value_str(repr(defaults[arg_name]))}"
                )
            else:
                args.append(f"{arg_name}:{type_map[arg_type]}")

    f.write(f"def {name}({','.join(args)})->types.{name}:...\n")


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
from typing import Any
from . import types

__all__ = [
    'types',
    'data',
    'ops',
    'context',
    'props',
]


class ScreenContext(types.Context):
    scene: types.Scene
    view_layer: types.ViewLayer
    visible_objects: list[types.Object]
    selectable_objects: list[types.Object]
    selected_objects: list[types.Object]
    editable_objects: list[types.Object]
    selected_editable_objects: list[types.Object]
    objects_in_mode: list[types.Object]
    objects_in_mode_unique_data: list[types.Object]
    visible_bones: list[types.EditBone]
    editable_bones: list[types.EditBone]
    selected_bones: list[types.EditBone]
    selected_editable_bones: list[types.EditBone]
    visible_pose_bones: list[types.PoseBone]
    selected_pose_bones: list[types.PoseBone]
    selected_pose_bones_from_active_object: list[types.PoseBone]
    active_bone: types.EditBone
    active_pose_bone: types.PoseBone
    active_object: types.Object
    object: types.Object
    edit_object: types.Object
    sculpt_object: types.Object
    vertex_paint_object: types.Object
    weight_paint_object: types.Object
    image_paint_object: types.Object
    particle_edit_object: types.Object
    pose_object: types.Object
    active_sequence_strip: types.Sequence
    sequences: list[types.Sequence]
    selected_sequences: list[types.Sequence]
    selected_editable_sequences: list[types.Sequence]
    active_nla_track: types.NlaTrack
    active_nla_strip: types.NlaStrip
    selected_nla_strips: list[types.NlaStrip]
    selected_movieclip_tracks: list[types.MovieTrackingTrack]
    gpencil_data: types.GreasePencil
    gpencil_data_owner: types.ID
    annotation_data: types.GreasePencil
    annotation_data_owner: types.ID
    visible_gpencil_layers: list[types.GPencilLayer]
    editable_gpencil_layers: list[types.GPencilLayer]
    editable_gpencil_strokes: list[types.GPencilStroke]
    active_gpencil_layer: list[types.GPencilLayer]
    active_gpencil_frame: list[types.GreasePencilLayer]
    active_annotation_layer: types.GPencilLayer
    active_operator: types.Operator
    active_action: types.Action
    selected_visible_actions: list[types.Action]
    selected_editable_actions: list[types.Action]
    visible_fcurves: list[types.FCurve]
    editable_fcurves: list[types.FCurve]
    selected_visible_fcurves: list[types.FCurve]
    selected_editable_fcurves: list[types.FCurve]
    active_editable_fcurve: types.FCurve
    selected_editable_keyframes: list[types.Keyframe]
    ui_list: types.UIList
    property: tuple[Any, str, int]
    asset_library_reference: types.AssetLibraryReference

    
data: types.BlendData
context: ScreenContext
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
    def remove(self, item: T)->None:...
"""
        )

    sg = StructStubGenerator(args.output, structs)  # type: ignore
    sg.generate()

    og = OperatorStubGenerator(args.output, ops)  # type: ignore
    og.generate()

    bpy_props_pyi = bpy_dir / "props.pyi"
    with bpy_props_pyi.open("w", encoding="utf-8") as f:
        f.write("from typing import Any, Callable\n")
        f.write("from . import types\n")
        for d in dir(bpy.props):
            if d == "RemoveProperty":
                continue
            if d.endswith("Property"):
                prop = getattr(bpy.props, d)
                print(prop)
                write_property_function(f, d, prop.__doc__)


if __name__ == "__main__":
    main()
