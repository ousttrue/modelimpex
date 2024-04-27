from typing import Any, NamedTuple, Self, Iterator, Iterable
import array
import mathutils  # type: ignore
import ctypes
import bpy


class Vector2(ctypes.LittleEndianStructure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
    ]


def Vector2_from_faceUV(uv: mathutils.Vector) -> Vector2:
    return Vector2(uv.x, -uv.y)


class Vector3(ctypes.LittleEndianStructure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float), ("z", ctypes.c_float)]

    def __sub__(self, rhs: Self):
        return Vector3(self.x - rhs.x, self.y - rhs.y, self.z - rhs.z)


def Vector3_from_meshVertex(v: mathutils.Vector) -> Vector3:
    return Vector3(v.x, v.z, -v.y)


def get_min_max2(values: Iterator[Vector2]) -> tuple[list[float], list[float]]:
    min: list[float] = [float("inf")] * 2
    max: list[float] = [float("-inf")] * 2
    for v in values:
        if v.x < min[0]:
            min[0] = v.x
        if v.x > max[0]:
            max[0] = v.x
        if v.y < min[1]:
            min[1] = v.y
        if v.y > max[1]:
            max[1] = v.y
    return min, max


def get_min_max3(values: Iterable[Vector3]):
    min: list[float] = [float("inf")] * 3
    max: list[float] = [float("-inf")] * 3
    for v in values:
        if v.x < min[0]:
            min[0] = v.x
        if v.x > max[0]:
            max[0] = v.x
        if v.y < min[1]:
            min[1] = v.y
        if v.y > max[1]:
            max[1] = v.y
        if v.z < min[2]:
            min[2] = v.z
        if v.z > max[2]:
            max[2] = v.z
    return min, max


class Submesh:
    def __init__(self, material_index: int) -> None:
        self.indices: Any = array.array("I")
        self.material_index = material_index


class Values(NamedTuple):
    values: memoryview
    min: list[float] | None = None
    max: list[float] | None = None


class Vector4(ctypes.LittleEndianStructure):
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float),
    ]


class IVector4(ctypes.LittleEndianStructure):
    _fields_ = [
        ("x", ctypes.c_ushort),
        ("y", ctypes.c_ushort),
        ("z", ctypes.c_ushort),
        ("w", ctypes.c_ushort),
    ]


class BoneWeight(ctypes.LittleEndianStructure):
    _fields_ = [
        ("i0", ctypes.c_int),
        ("i1", ctypes.c_int),
        ("i2", ctypes.c_int),
        ("i3", ctypes.c_int),
        ("weights", Vector4),
    ]


def PushBoneWeight(self: BoneWeight, i: int, w: float):
    if self.weights.x == 0:
        self.i0 = i
        self.weights.x = w
    elif self.weights.y == 0:
        self.i1 = i
        self.weights.y = w
    elif self.weights.z == 0:
        self.i2 = i
        self.weights.z = w
    elif self.weights.w == 0:
        self.i3 = i
        self.weights.w = w
    else:
        # raise NotImplementedError()
        print("over 4")


def GetBoneJoints(self: BoneWeight, group_index_to_joint_index: dict[int, int]):
    return IVector4(
        (
            group_index_to_joint_index[self.i0]
            if self.i0 in group_index_to_joint_index
            else 0
        ),
        (
            group_index_to_joint_index[self.i1]
            if self.i1 in group_index_to_joint_index
            else 0
        ),
        (
            group_index_to_joint_index[self.i2]
            if self.i2 in group_index_to_joint_index
            else 0
        ),
        (
            group_index_to_joint_index[self.i3]
            if self.i3 in group_index_to_joint_index
            else 0
        ),
    )


class Mesh(NamedTuple):
    name: str
    positions: Values
    normals: Values
    uvs: Values | None
    materials: list[bpy.types.Material]
    submeshes: list[Submesh]
    joints: memoryview | None
    weights: memoryview | None


class MeshStore:
    # TODO: https://docs.blender.org/manual/ja/latest/modeling/meshes/editing/mesh/sort_elements.html
    def __init__(
        self,
        mesh: bpy.types.Mesh,
        vertex_groups: bpy.types.VertexGroups,
        bone_names: list[str],
    ) -> None:
        self.name = mesh.name
        mesh.calc_loop_triangles()
        self.positions: ctypes.Array[Vector3] = (Vector3 * len(mesh.loops))()
        self.normals: ctypes.Array[Vector3] = (Vector3 * len(mesh.loops))()
        self.materials: list[bpy.types.Material] = [m for m in mesh.materials]
        self.submeshes: list[Submesh] = []

        submesh = Submesh(0)
        self.submeshes.append(submesh)

        uv_layer = mesh.uv_layers and mesh.uv_layers[0]
        self.uv: ctypes.Array[Vector2] | None = None
        if isinstance(uv_layer, bpy.types.MeshUVLoopLayer) and uv_layer:
            self.uv = (Vector2 * len(mesh.loops))()

        for tri in mesh.loop_triangles:
            for loop_index in tri.loops:
                # dst = vertices[loop_index]
                v = mesh.vertices[mesh.loops[loop_index].vertex_index]
                self.positions[loop_index] = Vector3_from_meshVertex(v.co)
                if tri.normal:
                    self.normals[loop_index] = Vector3_from_meshVertex(tri.normal)
                else:
                    self.normals[loop_index] = Vector3_from_meshVertex(v.normal)
                if self.uv:
                    self.uv[loop_index] = Vector2(*uv_layer.data[loop_index].uv) # type: ignore

                submesh.indices.append(loop_index)

        self.vertex_group_names = [g.name for g in vertex_groups]
        self.bone_names = bone_names
        self.bone_weights = (BoneWeight * len(mesh.loops))()
        for i, v in enumerate(mesh.loops):
            ve = mesh.vertices[v.vertex_index]
            for g in ve.groups:
                vg_name = self.vertex_group_names[g.group]
                if vg_name in self.bone_names:
                    PushBoneWeight(self.bone_weights[i], g.group, g.weight)

    def freeze(self, skin_bone_names: list[str]) -> Mesh:
        position_min, position_max = get_min_max3(self.positions)
        joints = None
        weights = None
        if skin_bone_names and len(skin_bone_names) > 0:
            group_index_to_joint_index = {
                i: skin_bone_names.index(vertex_group)
                for i, vertex_group in enumerate(self.vertex_group_names)
                if vertex_group in skin_bone_names
            }
            joints = (IVector4 * len(self.positions))()
            weights = (Vector4 * len(self.positions))()
            for i in range(len(self.positions)):
                joints[i] = GetBoneJoints(
                    self.bone_weights[i], group_index_to_joint_index
                )
                weights[i] = self.bone_weights[i].weights

        return Mesh(
            name=self.name,
            positions=Values(
                memoryview(self.positions), position_min, position_max  # type: ignore
            ),
            normals=Values(memoryview(self.normals)),  # type: ignore
            uvs=Values(memoryview(self.uv)) if self.uv else None,
            materials=self.materials,
            submeshes=self.submeshes,
            joints=memoryview(joints) if joints else None,  # type: ignore
            weights=memoryview(weights) if weights else None,  # type: ignore
        )
