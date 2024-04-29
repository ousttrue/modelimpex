from typing import Callable, Iterator, Any
from .types import Float3
import ctypes


class VertexBuffer:
    def __init__(self) -> None:
        self.POSITION: Callable[[], Iterator[tuple[float, float, float]]] | None = None
        self.NORMAL: Callable[[], Iterator[tuple[float, float, float]]] | None = None
        self.TEXCOORD_0: Callable[[], Iterator[tuple[float, float]]] | None = None
        self.JOINTS_0: Callable[[], Iterator[tuple[int, int, int, int]]] | None = None
        self.WEIGHTS_0: (
            Callable[[], Iterator[tuple[float, float, float, float]]] | None
        ) = None

    def set_attribute(self, key: str, value: Any):
        if key == "POSITION":
            self.POSITION = value  # type: ignore
        elif key == "NORMAL":
            self.NORMAL = value  # type: ignore
        elif key == "TEXCOORD_0":
            self.TEXCOORD_0 = value  # type: ignore
        elif key == "JOINTS_0":
            self.JOINTS_0 = value  # type: ignore
        elif key == "WEIGHTS_0":
            self.WEIGHTS_0 = value  # type: ignore
        else:
            raise NotImplementedError()

    def get_vertices(
        self,
    ) -> Iterator[
        tuple[
            tuple[float, float, float],
            tuple[float, float, float],
            tuple[int, int, int, int],
            tuple[float, float, float, float],
        ]
    ]:
        assert self.POSITION
        pos = self.POSITION()
        assert self.NORMAL
        nom = self.NORMAL()

        def ng_joint() -> Iterator[tuple[int, int, int, int]]:
            while True:
                yield 0, 0, 0, 0

        joints = ng_joint()
        if self.JOINTS_0:
            joints = self.JOINTS_0()

        def ng_weight() -> Iterator[tuple[float, float, float, float]]:
            while True:
                yield 1, 0, 0, 0

        weights = ng_weight()
        if self.WEIGHTS_0:
            weights = self.WEIGHTS_0()

        while True:
            try:
                p = next(pos)
                n = next(nom)
                j = next(joints)
                w = next(weights)
                yield p, n, j, w
            except StopIteration:
                break


class Submesh:
    def __init__(
        self,
        vertices: VertexBuffer,
        index_offset: int,
        index_count: int,
        material_index: int,
    ):
        self.vertices = vertices
        self.index_offset = index_offset
        self.index_count = index_count
        self.vertex_offset = 0  # VRM shared vertex buffer
        self.indices: Callable[[], Iterator[int]] | None = None
        self.material_index = material_index

    def get_indices(self) -> Iterator[tuple[int, int, int]]:
        assert self.indices
        i = self.indices()
        while True:
            try:
                i0 = next(i)
                i1 = next(i)
                i2 = next(i)
                yield (i0, i1, i2)
            except StopIteration:
                break


class Mesh:
    def __init__(self, name: str):
        self.name = name
        self.submeshes: list[Submesh] = []


class ExportMesh:
    def __init__(self, vertex_count: int, index_count: int):
        self.POSITION = (Float3 * vertex_count)()
        self.NORMAL = (Float3 * vertex_count)()
        self.indices = (ctypes.c_uint32 * index_count)()
        self.loop_normals = (Float3 * index_count)()
        self.normal_splitted = False

    def check_normal(self, i: int):
        if self.normal_splitted:
            return
        if self.NORMAL[self.indices[i]] != self.loop_normals[i]:
            l = self.NORMAL[self.indices[i]]
            l = (l.x, l.y, l.z)
            r = self.loop_normals[i]
            r = (r.x, r.y, r.z)
            self.normal_splitted = True

    def split(self) -> "ExportMesh":
        vertices: list[
            tuple[tuple[float, float, float], tuple[float, float, float]]
        ] = []
        vertex_map: dict[tuple[float, float, float, float, float, float], int] = {}
        indices: list[int] = []
        for i, n in zip(self.indices, self.loop_normals):
            p = self.POSITION[i]
            key = (p.x, p.y, p.z, n.x, n.y, n.z)
            if key in vertex_map:
                index = vertex_map[key]
            else:
                index = len(vertices)
                vertices.append((p, n))
                vertex_map[key] = index
            indices.append(index)

        splitted = ExportMesh(len(vertices), len(indices))
        for i, (v, n) in enumerate(vertices):
            splitted.POSITION[i] = v
            splitted.NORMAL[i] = n
        for i, index in enumerate(indices):
            splitted.indices[i] = index

        return splitted
