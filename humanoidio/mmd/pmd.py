from typing import Iterator
import logging
import io
from .pymeshio.pmd import pmd_format as pmd_model
from .pymeshio.pmd import pmd_reader as pmd_reader
from .. import gltf


LOGGER = logging.getLogger(__name__)


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
    mesh_node.mesh.vertices = gltf.VertexBuffer()

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

    mesh_node.mesh.vertices.POSITION = pos_gen
    mesh_node.mesh.vertices.NORMAL = normal_gen
    mesh_node.mesh.vertices.JOINTS_0 = joint_gen
    mesh_node.mesh.vertices.WEIGHTS_0 = weight_gen

    it = iter(src.indices)
    offset = 0
    for submesh in src.materials:
        gltf_submesh = gltf.Submesh(offset, submesh.vertex_count)

        def indices_gen():
            while True:
                try:
                    i0 = next(it)
                    i1 = next(it)
                    i2 = next(it)
                    yield i2
                    yield i1
                    yield i0
                except StopIteration:
                    break

        gltf_submesh.indices = indices_gen
        mesh_node.mesh.submeshes.append(gltf_submesh)
        offset += submesh.vertex_count
    mesh_node.skin = gltf.Skin()
    mesh_node.skin.joints = [node for node in loader.nodes]
    loader.nodes.append(mesh_node)
    loader.roots.append(mesh_node)

    def relative(parent: gltf.Node, parent_pos: tuple[float, float, float]):
        # print(parent.name, parent.translation)
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


def load_pmd(data: bytes) -> gltf.Loader | None:
    src = pmd_reader.read(io.BytesIO(data))  # type: ignore
    if src:
        LOGGER.debug(src)
        return pmd_to_gltf(src)
