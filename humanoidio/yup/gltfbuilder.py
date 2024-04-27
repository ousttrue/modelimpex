from typing import Iterator, Any

import bpy
import mathutils  # type: ignore

from .meshstore import MeshStore, Vector3_from_meshVertex, Vector3
from . import gltf


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


class GLTFBuilder:
    def __init__(self):
        self.gltf = gltf.GLTF()
        self.indent = " " * 2
        self.mesh_stores: list[MeshStore] = []
        self.nodes: list[Node] = []
        self.root_nodes: list[Node] = []
        self.skins: list[Skin] = []

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

            # copy
            new_obj = o.copy()
            new_obj.data = o.data.copy()
            bpy.data.scenes[0].collection.objects.link(new_obj)

            mesh = new_obj.data

            # apply modifiers
            for m in new_obj.modifiers:
                if m.type == "ARMATURE":
                    # skin
                    node.skin = self._get_or_create_skin(node, m.object)

            # export
            bone_names = (
                [b.name for b in node.skin.object.data.bones] if node.skin else []
            )
            node.mesh = self._export_mesh(mesh, o.vertex_groups, bone_names)

        elif o.type == "ARMATURE":
            _skin = self._get_or_create_skin(node, o)

        for child in o.children:
            child_node = self._export_object(node, child, indent + self.indent)
            node.children.append(child_node)

        return node

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
        vertex_groups: list[bpy.types.VertexGroup],
        bone_names: list[str],
    ) -> MeshStore:

        mesh.calc_loop_triangles()
        uv_layer = mesh.uv_layers and mesh.uv_layers[0]

        store = MeshStore(
            mesh.name, mesh.vertices, mesh.materials, vertex_groups, bone_names
        )
        for tri in mesh.loop_triangles:
            submesh = store.get_or_create_submesh(tri.material_index)
            store.add_face(tri, uv_layer)
            for loop_index in tri.loops:
                submesh.indices.append(loop_index)

        self.mesh_stores.append(store)
        return store

    def get_skin_for_store(self, store: MeshStore) -> Skin | None:
        for node in self.nodes:
            if node.mesh == store:
                return node.skin
        return None
