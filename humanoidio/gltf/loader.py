from typing import Any, NamedTuple
import logging
import dataclasses
import ctypes
import pathlib
import json
from .mesh import Submesh, Mesh
from .glb import get_glb_chunks
from .accessor_util import GltfAccessor
from .coordinate import Coordinate, Conversion
from .node import Node, Skin
from .. import human_bones
from . import gltf_json_type
from .material import Material, Texture, TextureData
from .types import Vertex, Bdef4, Float3


LOGGER = logging.getLogger(__name__)


class HumanBone(NamedTuple):
    bone_name: human_bones.HumanoidBones
    node: int


@dataclasses.dataclass
class Vrm0:
    human_bones: list[HumanBone]

    @staticmethod
    def from_vrm0_dict(data: dict[str, Any]) -> "Vrm0":
        return Vrm0(data["humanoid"]["humanBones"])


@dataclasses.dataclass
class Vrm1:
    humanbones: list[HumanBone]

    @staticmethod
    def from_vrm1_dict(data: dict[str, Any]) -> "Vrm1":
        raise NotImplementedError()


@dataclasses.dataclass
class Loader:
    name: str
    meshes: list[Mesh] = dataclasses.field(default_factory=list)
    nodes: list[Node] = dataclasses.field(default_factory=list)
    roots: list[Node] = dataclasses.field(default_factory=list)
    vrm: Vrm0 | Vrm1 | None = None
    textures: list[Texture] = dataclasses.field(default_factory=list)
    materials: list[Material] = dataclasses.field(default_factory=list)

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
                            Texture(
                                TextureData(
                                    t.get("name", f"texture.{i}"), image_bytes, mime
                                )
                            )
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
                self.vrm = Vrm0.from_vrm0_dict(gltf["extensions"]["VRM"])
                for bone in self.vrm.human_bones:
                    node = self.nodes[bone.node]
                    node.humanoid_bone = bone.bone_name
            elif "VRMC_vrm" in gltf["extensions"]:
                self.vrm = Vrm1.from_vrm1_dict(gltf["extensions"]["VRMC_vrm"])
                for bone in self.vrm.humanbones:
                    node = self.nodes[bone.node]
                    try:
                        node.humanoid_bone = bone.bone_name
                    except Exception:
                        pass

    # def _load_mesh(self, data: GltfAccessor, i: int, m: gltf_json_type.Mesh):
    #     mesh = Mesh(m.get("name", f"mesh{i}"))

    #     index_offset = 0
    #     vertex_offset = 0
    #     for prim in m["primitives"]:
    #         match prim:
    #             case {"indices": int(indices), "material": material}:
    #                 count = data.accessors[indices]["count"]
    #                 sm = Submesh(VertexBuffer(), index_offset, count, material)
    #                 sm.vertex_offset = vertex_offset
    #                 vertex_offset += data.accessors[prim["attributes"]["POSITION"]][
    #                     "count"
    #                 ]
    #                 index_offset += count

    #                 mesh.submeshes.append(sm)
    #                 for k, v in prim["attributes"].items():
    #                     sm.vertices.set_attribute(k, data.accessor_generator(v))
    #                 sm.indices = data.accessor_generator(prim["indices"])
    #             case _:
    #                 raise RuntimeError("no primitive.indices or material")

    #     return mesh

    def _load_mesh(self, data: GltfAccessor, i: int, m: gltf_json_type.Mesh) -> Mesh:
        index_count = 0
        vertex_count = 0
        submeshes: list[Submesh] = []
        for prim in m["primitives"]:
            match prim:
                case {"indices": int(indices_accessor), "material": int(material)}:
                    count = data.accessors[indices_accessor]["count"]
                    sm = Submesh(index_count, count, material)
                    submeshes.append(sm)
                    vertex_count += data.accessors[prim["attributes"]["POSITION"]][
                        "count"
                    ]
                    index_count += count
                    # for k, v in prim["attributes"].items():
                    #     sm.vertices.set_attribute(k, data.accessor_generator(v))
                    # sm.indices = data.accessor_generator(prim["indices"])
                case _:
                    raise RuntimeError("no primitive.indices or material")

        vertices = (Vertex * vertex_count)()
        boneweights = (Bdef4 * vertex_count)()
        indices = (ctypes.c_uint16 * index_count)()

        vertex_offset = 0
        index_offset = 0
        for prim in m["primitives"]:
            match prim:
                case {"indices": int(indices_accessor)}:
                    sub_positions = data.get_typed_accessor(
                        Float3, prim["attributes"]["POSITION"]
                    )
                    for i, position in enumerate(sub_positions):
                        vertices[vertex_offset + i].position = position

                    sub_indices = data.get_index_accessor(indices_accessor)
                    for i, index in enumerate(sub_indices):
                        indices[index_offset + i] = vertex_offset + index

                    vertex_offset += len(sub_positions)
                    index_offset += len(sub_indices)
                case _:
                    pass

        mesh = Mesh(
            m.get("name", f"mesh{i}"), vertices, boneweights, indices, submeshes
        )
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

    def get_bone(self, bone: human_bones.HumanoidBones) -> Node | None:
        for node in self.nodes:
            if node.humanoid_bone == bone:
                return node

    def guess_human_bones(self):
        d_bones: dict[str, Node] = {}
        for node in self.nodes:
            node.humanoid_bone = human_bones.guess_humanbone(node.name)
            match node.name:
                case (
                    "左足D"
                    | "左ひざD"
                    | "左足首D"
                    | "左足先EX"
                    | "右足D"
                    | "右ひざD"
                    | "右足首D"
                    | "右足先EX"
                ):
                    d_bones[node.name] = node
                case _:
                    pass
        if len(d_bones) == 8:

            def remap_human_bone(bone: human_bones.HumanoidBones, d_bone: str):
                node = self.get_bone(bone)
                assert node
                node.humanoid_bone = None
                d_bones[d_bone].humanoid_bone = bone
                assert node.removable()

            remap_human_bone("leftUpperLeg", "左足D")
            remap_human_bone("leftLowerLeg", "左ひざD")
            remap_human_bone("leftFoot", "左足首D")
            remap_human_bone("leftToes", "左足先EX")
            remap_human_bone("rightUpperLeg", "右足D")
            remap_human_bone("rightLowerLeg", "右ひざD")
            remap_human_bone("rightFoot", "右足首D")
            remap_human_bone("rightToes", "右足先EX")

    def remove_bones(self):
        remove_list: list[int] = []
        for i, node in enumerate(self.nodes):
            if node.removable():
                remove_list.append(i)

        # remove leaf nodes
        removes: list[Node] = []
        for i in reversed(remove_list):
            node = self.nodes[i]
            if i > 0 and len(node.children) == 0:
                if node.parent:
                    node.parent.remove_child(node)
                removes.append(node)
                LOGGER.debug(f"remove leaf: {node.name}")

        # fix
        index_map: dict[int, int] = {}
        for i, node in enumerate([x for x in self.nodes]):
            if node in removes:
                self.nodes.remove(node)
            else:
                index_map[i] = len(index_map)

        # TODO: 非ヒューマノイドボーンからヒューマノイドボーンへの weight 付け替え

        # # replace index
        # for i, node in enumerate(self.nodes):
        #     if i in index_map:
        #         if node.parent:
        #             parent_index = self.nodes.index(node.parent)
        #             node.parent = self.nodes[index_map[parent_index]]

        #         for j, child in enumerate([x for x in node.children]):
        #             child_index = self.nodes.index(child)
        #             node.children[j] = self.nodes[index_map[child_index]]

        #         if node.skin:
        #             for j, joint in enumerate([x for x in node.skin.joints]):
        #                 joint_index = self.nodes.index(joint)
        #                 node.skin.joints[j] = self.nodes[index_map[joint_index]]

        for mesh in self.meshes:
            if mesh.boneweights:
                for bdef in mesh.boneweights:
                    bdef.joints.x = index_map[int(bdef.joints.x)]
                    bdef.joints.y = index_map[int(bdef.joints.y)]
                    bdef.joints.z = index_map[int(bdef.joints.z)]
                    bdef.joints.w = index_map[int(bdef.joints.w)]

    def _remove_bone(
        self, node_map: dict[int, Node], i: int, keep_list: set[Node]
    ) -> None:
        node = node_map[i]
        self.nodes.remove(node)

        while node.parent:
            if node.parent in keep_list:
                break
            # skip remove parent
            assert node.parent.removable()
            if node.parent.parent:
                node.parent.parent.add_child(node)
            else:
                node.parent = None


def load_glb(
    path: pathlib.Path, data: bytes, dst: Coordinate
) -> tuple[Loader, Conversion]:
    json_chunk, bin_chunk = get_glb_chunks(data)
    gltf = json.loads(json_chunk)

    loader = Loader(path.stem)
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
