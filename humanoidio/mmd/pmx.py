import ctypes
import io
import pathlib
import logging
from .pymeshio.pmx import pmx_format as pmx_model
from .pymeshio.pmx import pmx_reader as pmx_reader
from .. import gltf


LOGGER = logging.getLogger(__name__)


# z:up -y:forward
def z_reverse(x: float, y: float, z: float) -> tuple[float, float, float]:
    return (x, y, -z)


def pmx_to_gltf(
    dir: pathlib.Path, src: pmx_model.Pmx, scale: float = 1.59 / 20
) -> gltf.Loader:
    loader = gltf.Loader(src.name)

    # create bones
    for b in src.bones:
        node = gltf.Node(b.name)
        # world pos
        node.translation = z_reverse(
            b.position.x * scale, b.position.y * scale, b.position.z * scale
        )
        loader.nodes.append(node)

    # build tree
    for i, b in enumerate(src.bones):
        if b.parent_index == -1:
            # root
            loader.roots.append(loader.nodes[i])
        else:
            parent = loader.nodes[b.parent_index]
            parent.add_child(loader.nodes[i])

    vertices = (gltf.Vertex * len(src.vertices))()
    boneweights = (gltf.Bdef4 * len(src.vertices))()
    for i, v in enumerate(src.vertices):
        dst = vertices[i]
        dst.position.x = v.position.x * scale
        dst.position.y = v.position.y * scale
        dst.position.z = -v.position.z * scale
        dst.normal.x = v.normal.x
        dst.normal.y = v.normal.y
        dst.normal.z = -v.normal.z
        dst.uv.x = v.uv.x
        dst.uv.y = v.uv.y
        bdst = boneweights[i]
        match v.deform:
            case pmx_model.Bdef1() as d:
                bdst.joints = gltf.Float4(d.index0, 0, 0, 0)
                bdst.weights = gltf.Float4(1, 0, 0, 0)
            case pmx_model.Bdef2() as d:
                if d.weight0 == 1:
                    bdst.joints = gltf.Float4(d.index0, 0, 0, 0)
                    bdst.weights = gltf.Float4(1, 0, 0, 0)
                elif d.weight0 == 0:
                    bdst.joints = gltf.Float4(0, d.index1, 0, 0)
                    bdst.weights = gltf.Float4(0, 1, 0, 0)
                else:
                    bdst.joints = gltf.Float4(d.index0, d.index1, 0, 0)
                    bdst.weights = gltf.Float4(d.weight0, 1 - d.weight0, 0, 0)
            case pmx_model.Bdef4() as d:
                bdst.weights = gltf.Float4(d.weight0, d.weight1, d.weight2, d.weight3)
                bdst.joints = gltf.Float4(
                    d.index0 if d.weight0 > 0 else 0,
                    d.index1 if d.weight1 > 0 else 0,
                    d.index2 if d.weight2 > 0 else 0,
                    d.index3 if d.weight3 > 0 else 0,
                )
            case pmx_model.Sdef() as d:
                if d.weight0 == 1:
                    bdst.joints = gltf.Float4(d.index0, 0, 0, 0)
                    bdst.weights = gltf.Float4(1, 0, 0, 0)
                elif d.weight0 == 0:
                    bdst.joints = gltf.Float4(0, d.index1, 0, 0)
                    bdst.weights = gltf.Float4(0, 1, 0, 0)
                else:
                    bdst.joints = gltf.Float4(d.index0, d.index1, 0, 0)
                    bdst.weights = gltf.Float4(d.weight0, 1 - d.weight0, 0, 0)

        if bdst.weights.x > 0:
            loader.nodes[int(bdst.joints.x)].vertex_count += 1
        if bdst.weights.y > 0:
            loader.nodes[int(bdst.joints.y)].vertex_count += 1
        if bdst.weights.z > 0:
            loader.nodes[int(bdst.joints.z)].vertex_count += 1
        if bdst.weights.w > 0:
            loader.nodes[int(bdst.joints.w)].vertex_count += 1

    indices = (ctypes.c_uint16 * len(src.indices))()
    for i in range(0, len(src.indices), 3):
        indices[i] = src.indices[i + 2]
        indices[i + 1] = src.indices[i + 1]
        indices[i + 2] = src.indices[i]

    mesh_node = gltf.Node("__mesh__")
    mesh_node.mesh = gltf.Mesh("mesh", vertices, boneweights, indices, [])
    loader.meshes.append(mesh_node.mesh)

    # texture
    for t in src.textures:
        loader.textures.append(gltf.Texture(dir / t))

    # material
    offset = 0
    for i, submesh in enumerate(src.materials):
        material = gltf.Material(f"{submesh.name}")
        if submesh.texture_index >= 0 and submesh.texture_index < len(src.textures):
            material.color_texture = submesh.texture_index
        loader.materials.append(material)

        gltf_submesh = gltf.Submesh(offset, submesh.vertex_count, i)
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

    loader.guess_human_bones()

    return loader


def load_pmx(path: pathlib.Path, data: bytes) -> gltf.Loader | None:
    src = pmx_reader.read(io.BytesIO(data))  # type: ignore
    if src:
        print(src)
        return pmx_to_gltf(path.parent, src)
