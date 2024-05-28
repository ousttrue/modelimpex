import ctypes
import io
import pathlib
from .pymeshio.pmd import pmd_format as pmd_model
from .pymeshio.pmd import pmd_reader as pmd_reader
from .. import gltf
from .. import human_bones


def z_reverse(x: float, y: float, z: float) -> tuple[float, float, float]:
    return (x, y, -z)


def pmd_to_gltf(
    dir: pathlib.Path, src: pmd_model.Pmd, scale: float = 1.59 / 20
) -> gltf.Loader:
    loader = gltf.Loader(src.name)

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

    vertices = (gltf.Vertex * len(src.vertices))()
    boneweights = (gltf.Bdef4 * len(src.vertices))()
    for i, v in enumerate(src.vertices):
        dst = vertices[i]
        dst.position.x = v.pos.x * scale
        dst.position.y = v.pos.y * scale
        dst.position.z = -v.pos.z * scale
        dst.normal.x = v.normal.x
        dst.normal.y = v.normal.y
        dst.normal.z = -v.normal.z
        dst.uv.x = v.uv.x
        dst.uv.y = v.uv.y
        bdst = boneweights[i]
        bdst.joints.x = v.bone0 if v.bone0 != 65535 else 0
        bdst.joints.y = v.bone1 if v.bone1 != 65535 else 0
        bdst.weights.x = v.weight0 * 0.01
        bdst.weights.y = (100 - v.weight0) * 0.01
        if bdst.weights.x > 0:
            loader.nodes[int(bdst.joints.x)].vertex_count += 1
        if bdst.weights.y > 0:
            loader.nodes[int(bdst.joints.y)].vertex_count += 1

    indices = (ctypes.c_uint16 * len(src.indices))()
    for i in range(0, len(src.indices), 3):
        indices[i] = src.indices[i + 2]
        indices[i + 1] = src.indices[i + 1]
        indices[i + 2] = src.indices[i]

    mesh_node = gltf.Node("__mesh__")
    mesh_node.mesh = gltf.Mesh("mesh", vertices, boneweights, indices, [])
    loader.meshes.append(mesh_node.mesh)

    for i, submesh in enumerate(src.materials):
        if submesh.texture_file:
            texture_file = dir / submesh.texture_file
            if all(x.data != texture_file for x in loader.textures):
                loader.textures.append(gltf.Texture(texture_file))

    offset = 0
    for i, submesh in enumerate(src.materials):
        material = gltf.Material(f"{src.name}.{i}")
        if submesh.texture_file:
            texture_file = dir / submesh.texture_file
            for j, texture in enumerate(loader.textures):
                if texture.data == texture_file:
                    material.color_texture = j
                    break
        loader.materials.append(material)
        gltf_submesh = gltf.Submesh(offset, submesh.vertex_count, i)
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
        return pmd_to_gltf(path.parent, src)
