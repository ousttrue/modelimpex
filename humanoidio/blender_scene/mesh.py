import bpy
import ctypes
import mathutils  # type: ignore
import bmesh  # type: ignore
from .. import gltf


UV_LAYER_NAME = "texcoord0"
DEFORM_LAYER_NAME = "deform0"


def create_vertices(bm: bmesh.types.BMesh, vertices: ctypes.Array[gltf.Vertex]):

    for v in vertices:
        # position
        vert = bm.verts.new((v.position.x, v.position.y, v.position.z))
        # normal
        vert.normal = mathutils.Vector((v.normal.x, v.normal.y, v.normal.z))


def create_face(
    bm: bmesh.types.BMesh, indices: ctypes.Array[ctypes.c_uint16], submesh: gltf.Submesh
):
    for i in range(submesh.index_offset, submesh.index_offset + submesh.index_count, 3):
        i0 = indices[i]
        i1 = indices[i + 1]
        i2 = indices[i + 2]
        v0 = bm.verts[i0]
        v1 = bm.verts[i1]
        v2 = bm.verts[i2]
        face = bm.faces.new((v0, v1, v2))
        face.smooth = True  # use vertex normal
        face.material_index = submesh.material_index


def get_or_create_uv_layer(bm: bmesh.types.BMesh) -> bmesh.types.BMLayerItem:
    if UV_LAYER_NAME in bm.loops.layers.uv:
        return bm.loops.layers.uv[UV_LAYER_NAME]
    return bm.loops.layers.uv.new(UV_LAYER_NAME)


def set_uv(bm: bmesh.types.BMesh, vertices: ctypes.Array[gltf.Vertex]):
    uv_layer = get_or_create_uv_layer(bm)
    for face in bm.faces:
        for loop in face.loops:
            uv = vertices[loop.vert.index].uv
            loop[uv_layer].uv = (uv.x, uv.y)

    # # Set morph target positions (no normals/tangents)
    # for target in mesh.morphtargets:

    #     layer = bm.verts.layers.shape.new(target.name)

    #     for i, vert in enumerate(bm.verts):
    #         p = target.attributes.position[i]
    #         vert[layer] = mathutils.Vector(yup2zup(p)) + vert.co


def create_mesh(bl_mesh: bpy.types.Mesh, mesh: gltf.Mesh):
    # create an empty BMesh
    bm = bmesh.new()

    # vertices
    create_vertices(bm, mesh.vertices)

    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    # triangles
    for sm in mesh.submeshes:
        create_face(bm, mesh.indices, sm)

    # loop layer
    set_uv(bm, mesh.vertices)

    bm.to_mesh(bl_mesh)
    bm.free()
