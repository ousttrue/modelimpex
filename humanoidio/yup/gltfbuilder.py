from typing import Iterator, Any, cast, Literal, TypedDict
from contextlib import contextmanager

import bpy
import mathutils  # type: ignore

from .meshstore import MeshStore, Vector3_from_meshVertex, Vector3
from . import gltf
from ..human_rig import HumanoidProperties


class HumanBone(TypedDict):
    node: int


class Node:
    def __init__(self, name: str, position: mathutils.Vector, parent: Any) -> None:
        self.name = name
        self.position = Vector3_from_meshVertex(position)
        self.children: list[Node] = []
        self.mesh: MeshStore | None = None
        self.skin: Skin | None = None
        self.parent = parent

    def get_local_position(self) -> Vector3:
        if not self.parent:
            return self.position
        return self.position - self.parent.position

    def __str__(self) -> str:
        return f"<{self.name}>"

    def traverse(self) -> Iterator["Node"]:
        yield self

        for child in self.children:
            for x in child.traverse():
                yield x


class Skin:
    def __init__(self, root: Node, o: bpy.types.Object) -> None:
        self.root = root
        self.object = o


@contextmanager
def tmp_active(obj: bpy.types.Object | None = None):
    active = bpy.context.active_object
    bpy.context.view_layer.objects.active = obj
    try:
        yield
    finally:
        bpy.context.view_layer.objects.active = active


MODE_MAP: dict[str, str] = {
    "EDIT_MESH": "EDIT",
    "EDIT_CURVE": "EDIT",
    "EDIT_CURVES": "EDIT",
    "EDIT_SURFACE": "EDIT",
    "EDIT_TEXT": "EDIT",
    "EDIT_ARMATURE": "EDIT",
    "EDIT_METABALL": "EDIT",
    "EDIT_LATTICE": "EDIT",
    "EDIT_GREASE_PENCIL": "EDIT",
    "EDIT_POINT_CLOUD": "EDIT",
    "PAINT_WEIGHT": "WEIGHT_PAINT",
    "PAINT_VERTEX": "VERTEX_PAINT",
    "PAINT_TEXTURE": "TEXTURE_PAINT",
    "PARTICLE": "PARTICLE_EDIT",
}


@contextmanager
def tmp_mode(
    mode: Literal[
        "OBJECT",
        "EDIT",
        "POSE",
        "SCULPT",
        "VERTEX_PAINT",
        "WEIGHT_PAINT",
        "TEXTURE_PAINT",
        "PARTICLE_EDIT",
        "EDIT_GPENCIL",
        "SCULPT_GPENCIL",
        "PAINT_GPENCIL",
        "WEIGHT_GPENCIL",
        "VERTEX_GPENCIL",
        "SCULPT_CURVES",
        "PAINT_GREASE_PENCIL",
    ],
    obj: bpy.types.Object | None = None,
):
    with tmp_active(obj):
        last_mode = cast(str, bpy.context.mode)
        bpy.ops.object.mode_set(mode=mode)
        try:
            yield
        finally:
            bpy.ops.object.mode_set(mode=MODE_MAP.get(last_mode, last_mode))  # type: ignore


class GLTFBuilder:
    def __init__(self):
        self.gltf = gltf.GLTF()
        self.indent = " " * 2
        self.mesh_stores: list[MeshStore] = []
        self.nodes: list[Node] = []
        self.root_nodes: list[Node] = []
        self.skins: list[Skin] = []

        self.tmp_objects: list[bpy.types.Object] = []

        self.extensions: dict[str, Any] = {}

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):  # type: ignore
        for x in self.tmp_objects:
            mesh = x.data
            bpy.context.scene.collection.objects.unlink(x)
            bpy.data.objects.remove(x)
            if isinstance(mesh, bpy.types.Mesh):
                bpy.data.meshes.remove(mesh)

    def export_objects(self, objects: list[bpy.types.Object]):
        for o in objects:
            root_node = self._export_object(None, o)
            self.root_nodes.append(root_node)

    def _export_object(
        self, parent: Node | None, o: bpy.types.Object, indent: str = ""
    ) -> Node:
        node = Node(o.name, o.matrix_world.to_translation(), parent)
        self.nodes.append(node)

        # only mesh
        if o.type == "MESH":
            new_obj, mesh = self._create_copy(o)

            # apply modifiers
            for m in new_obj.modifiers:
                if m.type == "ARMATURE":
                    # skin
                    node.skin = self._get_or_create_skin(node, m.object)

            # export
            bone_names = cast(
                list[str],
                [b.name for b in node.skin.object.data.bones] if node.skin else [],
            )
            node.mesh = self._export_mesh(mesh, o.vertex_groups, bone_names)

        elif o.type == "ARMATURE":
            self._get_or_create_skin(node, o)

            self._export_humanoid(HumanoidProperties.from_obj(o))

        for child in o.children:
            child_node = self._export_object(node, child, indent + self.indent)
            node.children.append(child_node)

        return node

    def _create_copy(
        self, o: bpy.types.Object
    ) -> tuple[bpy.types.Object, bpy.types.Mesh]:
        new_obj = cast(bpy.types.Object, o.copy())
        mesh = cast(bpy.types.Mesh, o.data.copy())
        new_obj.data = mesh
        bpy.data.scenes[0].collection.objects.link(new_obj)

        self.tmp_objects.append(new_obj)

        with tmp_mode("EDIT", new_obj):
            bpy.ops.mesh.sort_elements(type="MATERIAL", elements={"FACE"})

        return new_obj, mesh

    def _export_humanoid(self, humanoid: HumanoidProperties):

        vrm_bones: dict[str, HumanBone] = {}
        for _, bone_name in humanoid:
            if bone_name:
                vrm_name = humanoid.vrm_from_name(bone_name)
                found = False
                if vrm_name:
                    for i, node in enumerate(self.nodes):
                        if node.name == bone_name:
                            vrm_bones[vrm_name] = {"node": i}
                            found = True
                            break
                print(vrm_name, bone_name, found)

        # print(vrm_bones)
        self.extensions["VRMC_vrm"] = {"humanoid": {"humanBones": vrm_bones}}

    def _export_bone(
        self, parent: Node, matrix_world: mathutils.Matrix, bone: bpy.types.Bone
    ) -> Node:
        node = Node(bone.name, bone.head_local, parent)
        self.nodes.append(node)

        for child in bone.children:
            child_node = self._export_bone(node, matrix_world, child)
            node.children.append(child_node)

        return node

    def _get_or_create_skin(
        self, node: Node, armature_object: bpy.types.Object
    ) -> Skin:
        for skin in self.skins:
            if skin.object == armature_object:
                return skin

        skin = Skin(node, armature_object)
        self.skins.append(skin)

        armature = armature_object.data
        assert isinstance(armature, bpy.types.Armature)
        for b in armature.bones:
            if not b.parent:
                root_bone = self._export_bone(node, armature_object.matrix_world, b)
                node.children.append(root_bone)

        return skin

    def _export_mesh(
        self,
        mesh: bpy.types.Mesh,
        vertex_groups: bpy.types.VertexGroups,
        bone_names: list[str],
    ) -> MeshStore:

        store = MeshStore(mesh, vertex_groups, bone_names)
        self.mesh_stores.append(store)
        return store

    def get_skin_for_store(self, store: MeshStore) -> Skin | None:
        for node in self.nodes:
            if node.mesh == store:
                return node.skin
        return None
