import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import FloatVectorProperty, StringProperty
import bl_ui.space_topbar

from .. import blender_scene
from .. import gltf
import pathlib


class Exporter(bpy.types.Operator, ExportHelper):
    bl_idname = "humanoidio.exporter"
    bl_label = "humanoidio Exporter"
    bl_options = {"PRESET"}

    # ExportHelper mixin class uses this
    filename_ext = ".vrm"

    filter_glob: StringProperty(default="*.glb;*.gltf;*.vrm", options={"HIDDEN"})

    def execute(self, context: bpy.types.Context):
        print("#### start ####")

        # scan scene
        bl_obj_list = bpy.context.selected_objects
        if not bl_obj_list:
            # export all
            bl_obj_list = bpy.context.collection.objects
        obj_node = blender_scene.object_scanner.scan(bl_obj_list)
        animations = blender_scene.animation_scanner.scan(obj_node)
        constraints = blender_scene.constraint_scanner.scan(obj_node)

        # serialize
        writer = gltf.exporter.GltfWriter()
        writer.push_scene([node for _, node in obj_node if not node.parent])
        for a in animations:
            writer.push_animation(a, bpy.context.scene.render.fps)
        glb = writer.to_glb()
        path = pathlib.Path(self.filepath)

        print(f"write {len(glb)} bytes to {path}")
        path.write_bytes(glb)

        return {"FINISHED"}


def menu(
    self: bl_ui.space_topbar.TOPBAR_MT_file_export, context: bpy.types.Context
) -> None:
    print(type(self), self)
    self.layout.operator(Exporter.bl_idname, text=f"humanoidio (.glb;.vrm)")
