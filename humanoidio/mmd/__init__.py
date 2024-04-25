from .pymeshio.pmd import pmd_format as pmd_model
from .pymeshio.pmd import pmd_reader as pmd_reader

from .pymeshio.pmx import model as pmx_model
from .pymeshio.pmx import reader as pmx_reader

from .. import gltf

import logging
import io

LOGGER = logging.getLogger(__name__)


def z_reverse(x: float, y: float, z: float) -> tuple[float, float, float]:
    return (x, y, -z)


def pmd_to_gltf(pmd: pmd_model.Pmd) -> gltf.Loader:

    loader = gltf.Loader()

    # create bones
    for b in pmd.bones:
        node = gltf.Node(b.name)
        # world pos
        node.translation = z_reverse(b.pos.x, b.pos.y, b.pos.z)
        loader.nodes.append(node)

    return loader


def pmx_to_gltf(src: pmx_model.Model) -> gltf.Loader:
    """
    model
      mesh
      root
    """

    loader = gltf.Loader()

    # create bones
    for b in src.bones:
        node = gltf.Node(b.name)
        # world pos
        node.translation = z_reverse(b.position.x, b.position.y, b.position.z)
        loader.nodes.append(node)

    # build tree
    for i, b in enumerate(src.bones):
        if b.parent_index == -1:
            # root
            loader.roots.append(loader.nodes[i])
        else:
            parent = loader.nodes[b.parent_index]
            parent.add_child(loader.nodes[i])

    mesh_node = gltf.Node("__mesh__")
    mesh_node.mesh = gltf.Mesh("mesh")
    mesh_node.mesh.vertices = gltf.VertexBuffer()

    def pos_gen():
        it = iter(src.vertices)
        while True:
            try:
                v = next(it)
                yield z_reverse(v.position.x, v.position.y, v.position.z)
            except StopIteration:
                break

    def normal_gen():
        it = iter(src.vertices)
        while True:
            try:
                v = next(it)
                yield z_reverse(v.normal.x, v.normal.y, v.normal.z)
            except StopIteration:
                break

    def joint_gen():
        it = iter(src.vertices)
        while True:
            try:
                v = next(it)
                match v.deform:
                    case pmx_model.Bdef4() as d:
                        yield (d.index0, d.index1, d.index2, d.index3)
                    case _:
                        raise NotImplemented()
            except StopIteration:
                break

    def weight_gen():
        it = iter(src.vertices)
        while True:
            try:
                v = next(it)
                match v.deform:
                    case pmx_model.Bdef4() as d:
                        yield (d.weight0, d.weight1, d.weight2, d.weight3)
                    case _:
                        raise NotImplemented()
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
                    i = next(it)
                    yield i
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


def load(data: bytes) -> gltf.Loader | None:
    try:
        src = pmx_reader.read(io.BytesIO(data))  # type: ignore
        if src:
            LOGGER.debug(src)
            return pmx_to_gltf(src)
    except Exception:
        pass

    try:
        src = pmd_reader.read(io.BytesIO(data))  # type: ignore
        if src:
            LOGGER.debug(src)
            return src
    except Exception:
        pass
