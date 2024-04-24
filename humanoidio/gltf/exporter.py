from typing import NamedTuple, Iterator, MutableSequence
from enum import Enum, auto
import ctypes
from . import gltf_json_type
from . import glb
from . import accessor_util
from .node import Node
from .mesh import ExportMesh
from .types import Float3, Float4


GltfJson = dict[str, "GltfJson"] | list["GltfJson"] | bool | int | float | str


def enum_extensions_unique(
    gltf: GltfJson, used: set[str] | None = None
) -> Iterator[str]:
    if not used:
        used = set()

    match gltf:
        case dict():
            for k, v in gltf.items():
                if k == "extensions":
                    for kk, vv in v.items():  # type: ignore
                        if kk not in used:
                            yield kk
                            used.add(kk)  # type: ignore
                            break
                else:
                    for x in enum_extensions_unique(v, used):
                        yield x
        case list():
            for v in gltf:
                for x in enum_extensions_unique(v, used):
                    yield x

        case _:
            pass


class AnimationChannelTargetPath(Enum):
    translation = auto()
    rotation = auto()
    scale = auto()
    weights = auto()


class Animation(NamedTuple):
    action_name: str
    node: int
    target_path: AnimationChannelTargetPath
    times: MutableSequence[float]
    values: ctypes.Array[Float4]


class PostionMinMax:
    def __init__(self):
        self.min = [float("inf"), float("inf"), float("inf")]
        self.max = [-float("inf"), -float("inf"), -float("inf")]

    def push(self, v: Float3):
        # min
        if v.x < self.min[0]:
            self.min[0] = v.x
        if v.y < self.min[1]:
            self.min[1] = v.y
        if v.z < self.min[2]:
            self.min[2] = v.z
        # max
        if v.x > self.max[0]:
            self.max[0] = v.x
        if v.y > self.max[1]:
            self.max[1] = v.y
        if v.z > self.max[2]:
            self.max[2] = v.z


class FloatMinMax:
    def __init__(self):
        self.min = [float("inf")]
        self.max = [-float("inf")]

    def push(self, v: float):
        if v < self.min[0]:
            self.min[0] = v
        if v > self.max[0]:
            self.max[0] = v


class GltfWriter:
    def __init__(self):
        self.gltf: gltf_json_type.glTF = {
            "asset": {
                "version": "2.0",
            },
            "buffers": [],
            "bufferViews": [],
            "accessors": [],
            "meshes": [],
            "nodes": [],
            "scenes": [],
        }
        self.accessor = accessor_util.GltfAccessor(self.gltf, bytearray())

    def push_mesh(self, mesh: ExportMesh):
        if mesh.normal_splitted:
            mesh = mesh.split()

        gltf_mesh: gltf_json_type.Mesh = {"primitives": []}
        primitive: gltf_json_type.MeshPrimitive = {"attributes": {}}
        primitive["attributes"]["POSITION"] = self.accessor.push_array(
            mesh.POSITION, PostionMinMax
        )
        primitive["attributes"]["NORMAL"] = self.accessor.push_array(mesh.NORMAL)
        primitive["indices"] = self.accessor.push_array(mesh.indices)
        gltf_mesh["primitives"].append(primitive)

        meshes = self.gltf.get("meshes", [])
        self.gltf["meshes"] = meshes
        mesh_index = len(meshes)
        meshes.append(gltf_mesh)

        return mesh_index

    def _export_node(self, node: Node):
        gltf_node: gltf_json_type.Node = {"name": node.name}
        nodes = self.gltf.get("nodes", [])
        self.gltf["nodes"] = nodes
        node_index = len(nodes)
        nodes.append(gltf_node)

        # TODO: TRS
        if node.translation != (0, 0, 0):
            gltf_node["translation"] = node.translation  # type: ignore

        # mesh
        if isinstance(node.mesh, ExportMesh):
            mesh_index = self.push_mesh(node.mesh)
            gltf_node["mesh"] = mesh_index

        # children
        for child in node.children:
            child_node_index = self._export_node(child)
            if "children" not in gltf_node:
                gltf_node["children"] = []
            gltf_node["children"].append(child_node_index)

        # constraint
        if node.constraint:
            src = self.nodes.index(node.constraint.target)
            gltf_node["extensions"] = {
                "VRMC_node_constraint": {
                    "constraint": {
                        "rotation": {"source": src, "weight": node.constraint.weight}
                    }
                }
            }

        return node_index

    def push_scene(self, nodes: list[Node]):
        self.nodes = nodes
        scene: gltf_json_type.Scene = {"nodes": []}
        for node in nodes:
            node_index = self._export_node(node)
            scene["nodes"].append(node_index)

        scenes = self.gltf.get("scenes", [])
        self.gltf["scenes"] = scenes
        scenes.append(scene)

    def push_animation(self, animation: Animation, fps: float):
        if "animations" not in self.gltf:
            self.gltf["animations"] = []

        inv = 1 / fps
        for i, _ in enumerate(animation.times):
            animation.times[i] = animation.times[i] * inv

        time_accessor = self.accessor.push_array(animation.times, FloatMinMax)
        values_accessor = self.accessor.push_array(animation.values)

        gltf_animation: gltf_json_type.Animation = {  # type: ignore
            "name": animation.action_name,
            "samplers": [
                {
                    "input": time_accessor,
                    "interpolation": "LINEAR",
                    "output": values_accessor,
                }
            ],
            "channels": [
                {
                    "sampler": 0,
                    "target": {
                        "node": animation.node,
                        "path": animation.target_path.name,
                    },
                }
            ],
        }
        self.gltf["animations"].append(gltf_animation)

    def to_gltf(self) -> tuple[gltf_json_type.glTF, bytes]:
        self.gltf["buffers"] = [{"byteLength": len(self.accessor.bin)}]

        # update extensions used
        self.gltf["extensionsUsed"] = [x for x in enum_extensions_unique(self.gltf)]  # type: ignore

        return self.gltf, bytes(self.accessor.bin)

    def to_glb(self) -> bytes:
        gltf, bin = self.to_gltf()
        return glb.to_glb(gltf, bin)
