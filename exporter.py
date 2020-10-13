import bpy


def mesh_triangulate(me: bpy.types.Mesh):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()


def export_mesh(mesh: bpy.types.Mesh):

    mesh_triangulate(mesh)
    print(mesh)

    # positions
    vertices = [v.co for v in mesh.vertices]

    # normals
    # uv
    # skins
    # materials

    # indices
    triangles = []
    for face in mesh.polygons:
        v = face.vertices
        if len(v) == 3:
            triangles.append([i for i in v])
        else:
            raise NotImplementedError()

    print(f'{len(vertices)} vertices, {len(triangles)} triangles')

    if len(mesh.uv_layers) > 0:
        uv_layer = mesh.uv_layers.active.data[:]
    else:
        faceuv = False


def export_object(o: bpy.types.Object):
    '''
    addons/io_scene_obj/export_obj.py
    '''
    try:
        me = o.to_mesh()
        if not me:
            return

        # me.transform(EXPORT_GLOBAL_MATRIX @ ob_mat)
        # # If negative scaling, we have to invert the normals...
        # if ob_mat.determinant() < 0.0:
        #     me.flip_normals()

        export_mesh(me)

        # clean up
        o.to_mesh_clear()

    except RuntimeError:
        me = None


def run(context: bpy.types.Context):
    print('excute')

    # apply modifier
    # depsgraph = context.evaluated_depsgraph_get()
    # ob.evaluated_get(depsgraph)

    # Exit edit mode before exporting, so current object states are exported properly.
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    for o in context.scene.objects:
        export_object(o)