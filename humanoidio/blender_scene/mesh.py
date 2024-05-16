import bpy
import mathutils  # type: ignore
import bmesh  # type: ignore
from .. import gltf

UV_LAYER_NAME = "texcoord0"
DEFORM_LAYER_NAME = "deform0"


def create_vertices(bm: bmesh.types.BMesh, vertex_buffer: gltf.VertexBuffer):

    for pos, n, j, w in vertex_buffer.get_vertices():
        # position
        vert = bm.verts.new(pos)
        # normal
        if n:
            vert.normal = mathutils.Vector(n)


def create_face(bm: bmesh.types.BMesh, submesh: gltf.Submesh):
    for i0, i1, i2 in submesh.get_indices():
        v0 = bm.verts[i0 + submesh.vertex_offset]
        v1 = bm.verts[i1 + submesh.vertex_offset]
        v2 = bm.verts[i2 + submesh.vertex_offset]
        face = bm.faces.new((v0, v1, v2))
        face.smooth = True  # use vertex normal
        face.material_index = submesh.material_index


def get_or_create_uv_layer(bm: bmesh.types.BMesh) -> bmesh.types.BMLayerItem:
    if UV_LAYER_NAME in bm.loops.layers.uv:
        return bm.loops.layers.uv[UV_LAYER_NAME]
    return bm.loops.layers.uv.new(UV_LAYER_NAME)


def set_uv(bm: bmesh.types.BMesh, uv_list: list[tuple[float, float]]):
    uv_layer = get_or_create_uv_layer(bm)
    for face in bm.faces:
        for loop in face.loops:
            uv = uv_list[loop.vert.index]
            loop[uv_layer].uv = uv

    # # Set morph target positions (no normals/tangents)
    # for target in mesh.morphtargets:

    #     layer = bm.verts.layers.shape.new(target.name)

    #     for i, vert in enumerate(bm.verts):
    #         p = target.attributes.position[i]
    #         vert[layer] = mathutils.Vector(yup2zup(p)) + vert.co


def create_mesh(bl_mesh: bpy.types.Mesh, mesh: gltf.Mesh):
    # create an empty BMesh
    bm = bmesh.new()

    uv_list: list[tuple[float, float]] = []

    # vertices
    for sm in mesh.submeshes:
        create_vertices(bm, sm.vertices)
        tex = sm.vertices.TEXCOORD_0
        if tex:
            for uv in tex():
                uv_list.append(uv)

    bm.verts.ensure_lookup_table()
    bm.verts.index_update()

    # triangles
    for sm in mesh.submeshes:
        create_face(bm, sm)

    # loop layer
    if len(uv_list) > 0:
        set_uv(bm, uv_list)

    bm.to_mesh(bl_mesh)
    bm.free()
