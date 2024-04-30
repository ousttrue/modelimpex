from typing import Iterator, Callable
import io
import pathlib
from .pymeshio.pmd import pmd_format as pmd_model
from .pymeshio.pmd import pmd_reader as pmd_reader
from .. import gltf


def z_reverse(x: float, y: float, z: float) -> tuple[float, float, float]:
    return (x, y, -z)


def pmd_to_gltf(src: pmd_model.Pmd, scale: float = 1.59 / 20) -> gltf.Loader:
    loader = gltf.Loader()

    # create bones
    for b in src.bones:
        node = gltf.Node(b.name)
        # world pos
        node.translation = z_reverse(b.pos.x * scale, b.pos.y * scale, b.pos.z * scale)
        loader.nodes.append(node)

    # build tree
    for i, b in enumerate(src.bones):
        if b.parent_index == -1 or b.parent_index == 65535:
            # root
            loader.roots.append(loader.nodes[i])
        else:
            parent = loader.nodes[b.parent_index]
            parent.add_child(loader.nodes[i])

    mesh_node = gltf.Node("__mesh__")
    mesh_node.mesh = gltf.Mesh("mesh")

    def pos_gen() -> Iterator[tuple[float, float, float]]:
        it = iter(src.vertices)
        while True:
            try:
                v = next(it)
                yield z_reverse(v.pos.x * scale, v.pos.y * scale, v.pos.z * scale)
            except StopIteration:
                break

    def normal_gen() -> Iterator[tuple[float, float, float]]:
        it = iter(src.vertices)
        while True:
            try:
                v = next(it)
                yield z_reverse(v.normal.x, v.normal.y, v.normal.z)
            except StopIteration:
                break

    def tex_gen() -> Iterator[tuple[float, float]]:
        it = iter(src.vertices)
        while True:
            try:
                v = next(it)
                yield v.uv.x, 1 - v.uv.y
            except StopIteration:
                break

    def joint_gen() -> Iterator[tuple[int, int, int, int]]:
        it = iter(src.vertices)
        while True:
            try:
                v = next(it)
                yield (v.bone0, v.bone1, 0, 0)
            except StopIteration:
                break

    def weight_gen() -> Iterator[tuple[float, float, float, float]]:
        it = iter(src.vertices)
        while True:
            try:
                v = next(it)
                yield (v.weight0, 1 - v.weight0, 0, 0)
            except StopIteration:
                break

    vertices = gltf.VertexBuffer()
    vertices.POSITION = pos_gen
    vertices.NORMAL = normal_gen
    vertices.TEXCOORD_0 = tex_gen
    vertices.JOINTS_0 = joint_gen
    vertices.WEIGHTS_0 = weight_gen

    offset = 0

    def flip(
        indices: list[int], offset: int, vertex_count: int
    ) -> Callable[[], Iterator[int]]:
        def gen() -> Iterator[int]:
            for i in range(offset, offset + vertex_count, 3):
                yield indices[i + 2]
                yield indices[i + 1]
                yield indices[i]

        return gen

    for i, submesh in enumerate(src.materials):
        material = gltf.Material(f"{src.name}.{i}")
        if src.path and submesh.texture_file:
            texutre_index = len(loader.textures)
            loader.textures.append(src.path.parent / submesh.texture_file)
            material.color_texture = texutre_index
        loader.materials.append(material)
        gltf_submesh = gltf.Submesh(vertices, offset, submesh.vertex_count, i)
        gltf_submesh.indices = flip(src.indices, offset, submesh.vertex_count)
        mesh_node.mesh.submeshes.append(gltf_submesh)
        offset += submesh.vertex_count
    mesh_node.skin = gltf.Skin()
    mesh_node.skin.joints = [node for node in loader.nodes]
    loader.nodes.append(mesh_node)
    loader.roots.append(mesh_node)

    def relative(parent: gltf.Node, parent_pos: tuple[float, float, float]):
        for child in parent.children:
            child_pos = child.translation

            child.translation = (
                child_pos[0] - parent_pos[0],
                child_pos[1] - parent_pos[1],
                child_pos[2] - parent_pos[2],
            )

            relative(child, child_pos)

    for root in loader.roots:
        relative(root, root.translation)

    return loader


def load_pmd(path: pathlib.Path, data: bytes) -> gltf.Loader | None:
    src = pmd_reader.read(io.BytesIO(data))  # type: ignore
    if src:
        print(src)
        src.path = path
        return pmd_to_gltf(src)
