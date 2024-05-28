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
from .types import Vertex, Bdef4, Float2, Float3, Float4


LOGGER = logging.getLogger(__name__)


class HumanBone(NamedTuple):
    bone_name: human_bones.HumanoidBones
    node: int


@dataclasses.dataclass
class Vrm0:
    human_bones: list[HumanBone] = dataclasses.field(default_factory=list)

    @staticmethod
    def from_vrm0_dict(data: dict[str, Any]) -> "Vrm0":
        return Vrm0(
            [HumanBone(x["bone"], x["node"]) for x in data["humanoid"]["humanBones"]]
        )


@dataclasses.dataclass
class Vrm1:
    humanbones: list[HumanBone] = dataclasses.field(default_factory=list)

    @staticmethod
    def from_vrm1_dict(data: dict[str, Any]) -> "Vrm1":
        vrm1 = Vrm1()
        for k, v in data["humanoid"]["humanBones"].items():
            vrm1.humanbones.append(HumanBone(k, v["node"]))
        return vrm1


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

                    sub_tex = data.get_typed_accessor(
                        Float2, prim["attributes"]["TEXCOORD_0"]
                    )
                    if sub_tex:
                        for i, uv in enumerate(sub_tex):
                            vertices[vertex_offset + i].uv = uv

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

    def get_human_bone(self, bone: human_bones.HumanoidBones) -> Node | None:
        for node in self.nodes:
            if node.humanoid_bone == bone:
                return node

    def get_bone(self, name: str) -> Node | None:
        for node in self.nodes:
            if node.name == name:
                return node

    def guess_human_bones(self):
        for root in self.roots:
            root.update_world_position()

        d_bones: dict[str, Node] = {}
        center_upper_lower: dict[str, Node] = {}
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
                case "センター" | "上半身" | "下半身":
                    center_upper_lower[node.name] = node
                case _:
                    pass

        # fix D bone
        if len(d_bones) == 8:

            def remap_human_bone(
                bone: human_bones.HumanoidBones, d_bone: str, allow_skip: bool = False
            ):
                node = self.get_human_bone(bone)
                if not node and allow_skip:
                    return
                assert node
                node.humanoid_bone = None
                d_bones[d_bone].humanoid_bone = bone
                assert node.removable()

            remap_human_bone("leftUpperLeg", "左足D")
            remap_human_bone("leftLowerLeg", "左ひざD")
            remap_human_bone("leftFoot", "左足首D")
            remap_human_bone("leftToes", "左足先EX", True)
            remap_human_bone("rightUpperLeg", "右足D")
            remap_human_bone("rightLowerLeg", "右ひざD")
            remap_human_bone("rightFoot", "右足首D")
            remap_human_bone("rightToes", "右足先EX", True)

        # fix upper lower
        if len(center_upper_lower) == 3:
            #  center
            #    + upper
            #    + lower
            #      + leftUpperLeg
            #      + rightUpperLeg
            pass
            # center
            #   + lower(hips)
            #     + upper
            #     + leftUpperLeg
            #     + rightUpperLeg
            hips = center_upper_lower["下半身"]
            assert hips.humanoid_bone == "hips"

            left_upper_leg = self.get_human_bone("leftUpperLeg")
            assert left_upper_leg
            right_upper_leg = self.get_human_bone("rightUpperLeg")
            assert right_upper_leg
            hips.world_position = (
                (left_upper_leg.world_position[0] + right_upper_leg.world_position[0])
                / 2,
                (left_upper_leg.world_position[1] + right_upper_leg.world_position[1])
                / 2,
                (left_upper_leg.world_position[2] + right_upper_leg.world_position[2])
                / 2,
            )

            spine = self.get_human_bone("spine")
            assert spine
            hips.add_child(spine)

        leftUpperArm = self.get_human_bone("leftUpperArm")
        leftLowerArm = self.get_human_bone("leftLowerArm")
        rightUpperArm = self.get_human_bone("rightUpperArm")
        rightLowerArm = self.get_human_bone("rightLowerArm")
        if leftUpperArm and leftLowerArm and rightUpperArm and rightLowerArm:
            if (
                leftUpperArm.vertex_count == 0
                and leftLowerArm.vertex_count == 0
                and rightUpperArm.vertex_count == 0
                and rightLowerArm.vertex_count == 0
            ):
                # TODO: IK
                leftSode = self.get_bone("左腕袖")
                assert leftSode
                leftUpperArm.add_child(leftSode)

                leftLowerSode = self.get_bone("左ひじ袖")
                assert leftLowerSode
                leftLowerArm.add_child(leftLowerSode)

                rightSode = self.get_bone("右腕袖")
                assert rightSode
                rightUpperArm.add_child(rightSode)

                rightLowerSode = self.get_bone("右ひじ袖")
                assert rightLowerSode
                rightLowerArm.add_child(rightLowerSode)

        # recalc local position
        for root in self.roots:
            root.local_from_world()

    def remove_bones(self):
        for root in self.roots:
            root.update_world_position()

        removes = self._remove_leaf_bones()
        self._remove_not_leaf_bones(removes)

        # fix
        index_map: dict[int, int] = {}
        for i, node in enumerate([x for x in self.nodes]):
            if node.name == "__mesh__":
                continue
            if node in removes:
                self.nodes.remove(node)
            else:
                index_map[i] = len(index_map)

        for i, node in enumerate([x for x in self.nodes]):
            if node.skin:
                skin_index_map: dict[int, int] = {}
                for j, joint in enumerate([x for x in node.skin.joints]):
                    if joint in removes:
                        node.skin.joints.remove(joint)
                    else:
                        skin_index_map[j] = len(skin_index_map)
                assert skin_index_map == index_map

        for mesh in self.meshes:
            if mesh.boneweights:
                for bdef in mesh.boneweights:
                    if bdef.weights.x > 0:
                        bdef.joints.x = index_map[int(bdef.joints.x)]
                    if bdef.weights.y > 0:
                        bdef.joints.y = index_map[int(bdef.joints.y)]
                    if bdef.weights.z > 0:
                        bdef.joints.z = index_map[int(bdef.joints.z)]
                    if bdef.weights.w > 0:
                        bdef.joints.w = index_map[int(bdef.joints.w)]

        for root in self.roots:
            root.local_from_world()

    def _remove_leaf_bones(self) -> list[Node]:
        remove_list: list[int] = []
        for i, node in enumerate(self.nodes):
            if node.removable():
                remove_list.append(i)
        removes: list[Node] = []
        for i in reversed(remove_list):
            node = self.nodes[i]
            if i > 0 and len(node.children) == 0:
                if node.parent:
                    node.parent.remove_child(node)
                removes.append(node)
                assert len(node.children) == 0
                LOGGER.debug(f"remove leaf: {node.name}")
        return removes

    def _remove_not_leaf_bones(self, removes: list[Node]) -> None:
        for node in self.nodes:
            if node in removes:
                continue

            if node.removable():
                removes.append(node)
                if node.parent:
                    assert node.parent not in removes
                    LOGGER.debug(f"remove not root: {node.name}")
                    # 子ボーンの移植
                    for child in [x for x in node.children]:
                        node.parent.add_child(child)
                    node.parent.remove_child(node)
                else:
                    LOGGER.debug(f"remove root: {node.name}")
                    self.roots.remove(node)
                    for child in [x for x in node.children]:
                        node.remove_child(child)
                        self.roots.append(child)


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
