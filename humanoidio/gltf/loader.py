from typing import Any
import pathlib
import json
from .mesh import Submesh, VertexBuffer, Mesh
from .glb import get_glb_chunks
from .accessor_util import GltfAccessor
from .coordinate import Coordinate, Conversion
from .node import Node, Skin
from .humanoid import HumanoidBones
from . import gltf_json_type
from .material import Material, Texture


class Vrm0:
    def __init__(self, src: dict[str, Any]):
        self.data = src


class Vrm1:
    def __init__(self, src: dict[str, Any]):
        self.data = src


class Loader:
    def __init__(self):
        self.meshes: list[Mesh] = []
        self.nodes: list[Node] = []
        self.roots: list[Node] = []
        self.vrm: Vrm0 | Vrm1 | None = None
        self.textures: list[pathlib.Path | Texture] = []
        self.materials: list[Material] = []

    def load(self, gltf: gltf_json_type.glTF, bin: bytes):

        data = GltfAccessor(gltf, bin)

        #
        # textures
        #
        if "textures" in gltf:
            for i, t in enumerate(gltf["textures"]):
                match t:
                    case {"source": source}:
                        mime, image_bytes = data.image_mime_bytes(source)
                        self.textures.append(
                            Texture(t.get("name", f"texture.{i}"), mime, image_bytes)
                        )
                    case _:
                        raise RuntimeError()

        #
        # material
        #
        if "materials" in gltf:
            for i, m in enumerate(gltf["materials"]):
                material = Material(m.get("name", f"material.{i}"))
                self.materials.append(material)
                match m:
                    case {
                        "pbrMetallicRoughness": {"baseColorTexture": {"index": index}}
                    }:
                        material.color_texture = index
                    case _:
                        pass

        print(self.materials)

        #
        # mesh
        #
        if "meshes" in gltf:
            for i, m in enumerate(gltf["meshes"]):
                mesh = self._load_mesh(data, i, m)
                self.meshes.append(mesh)

        #
        # node
        #
        if "nodes" in gltf:
            for i, n in enumerate(gltf["nodes"]):
                node = self._load_node(i, n)
                self.nodes.append(node)

            for i, n in enumerate(gltf["nodes"]):
                node = self.nodes[i]
                for child_index in n.get("children", []):
                    node.add_child(self.nodes[child_index])

                if "skins" in gltf and "skin" in n:
                    s = gltf["skins"][n["skin"]]
                    node.skin = Skin()
                    for j in s["joints"]:
                        node.skin.joints.append(self.nodes[j])

        for node in self.nodes:
            if not node.parent:
                self.roots.append(node)

        #
        # extensions
        #
        if "extensions" in gltf:
            if "VRM" in gltf["extensions"]:
                self.vrm = Vrm0(gltf["extensions"]["VRM"])
                for bone in self.vrm.data["humanoid"]["humanBones"]:
                    node = self.nodes[bone["node"]]
                    node.humanoid_bone = HumanoidBones.from_name(bone["bone"])
            elif "VRMC_vrm" in gltf["extensions"]:
                self.vrm = Vrm1(gltf["extensions"]["VRMC_vrm"])
                for k, bone in self.vrm.data["humanoid"]["humanBones"].items():
                    node = self.nodes[bone["node"]]
                    try:
                        node.humanoid_bone = HumanoidBones.from_name(k)
                    except Exception:
                        pass

    def _load_mesh(self, data: GltfAccessor, i: int, m: gltf_json_type.Mesh):
        mesh = Mesh(m.get("name", f"mesh{i}"))

        index_offset = 0
        vertex_offset = 0
        for prim in m["primitives"]:
            match prim:
                case {"indices": int(indices), "material": material}:
                    count = data.accessors[indices]["count"]
                    sm = Submesh(VertexBuffer(), index_offset, count, material)
                    sm.vertex_offset = vertex_offset
                    vertex_offset += data.accessors[prim["attributes"]["POSITION"]][
                        "count"
                    ]
                    index_offset += count

                    mesh.submeshes.append(sm)
                    for k, v in prim["attributes"].items():
                        sm.vertices.set_attribute(k, data.accessor_generator(v))
                    sm.indices = data.accessor_generator(prim["indices"])
                case _:
                    raise RuntimeError("no primitive.indices or material")

        return mesh

    def _load_node(self, i: int, n: gltf_json_type.Node):
        name = n.get("name", f"node_{i}")
        node = Node(name)

        match n:
            case {"matrix": _matrix}:
                raise NotImplementedError("node.matrix")
            case _:
                match n:
                    case {"translation": (x, y, z)}:
                        node.translation = (x, y, z)
                    case _:
                        node.translation = (0, 0, 0)
                match n:
                    case {"rotation": (x, y, z, w)}:
                        node.rotation = (x, y, z, w)
                    case _:
                        node.rotation = (0, 0, 0, 1)
                match n:
                    case {"scale": (x, y, z)}:
                        node.scale = (x, y, z)
                    case _:
                        node.scale = (1, 1, 1)

        if "mesh" in n:
            node.mesh = self.meshes[n["mesh"]]

        return node


def load_glb(
    path: pathlib.Path, data: bytes, dst: Coordinate
) -> tuple[Loader, Conversion]:
    json_chunk, bin_chunk = get_glb_chunks(data)
    gltf = json.loads(json_chunk)

    loader = Loader()
    loader.load(gltf, bin_chunk)
    src = Coordinate.GLTF
    if isinstance(loader.vrm, Vrm0):
        src = Coordinate.VRM0
    return loader, Conversion(src, dst)


def load_gltf(
    path: pathlib.Path, json_src: str, conv: Coordinate
) -> tuple[Loader, Conversion]:
    raise NotImplementedError()


def load(src: pathlib.Path, data: bytes, conv: Coordinate) -> tuple[Loader, Conversion]:
    if src.suffix == ".gltf":
        return load_gltf(src, data.decode("utf-8)"), conv)
    else:
        return load_glb(src, data, conv)
