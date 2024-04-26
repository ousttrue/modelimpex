import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty
import bl_ui.space_topbar


class ExportYUP(bpy.types.Operator, ExportHelper):
    """Export selection to YUP"""

    bl_idname = "export_scene.yup"
    bl_label = "Export YUP GLTF"

    filepath = StringProperty(subtype="FILE_PATH")

    # Export options

    selectedonly = BoolProperty(
        name="Export Selected Objects Only",
        description="Export only selected objects",
        default=True,
    )

    # ExportHelper mixin class uses this
    filename_ext = ".glb"

    filter_glob = StringProperty(default="*.glb;*.gltf", options={"HIDDEN"})

    def execute(self, context: bpy.types.Context):
        import pathlib

        ext = pathlib.Path(self.filepath).suffix.lower()
        if ext != ".gltf" and ext != ".glb":
            self.filepath = bpy.path.ensure_ext(self.filepath, ".gltf")
        path = pathlib.Path(self.filepath).absolute()

        from .. import yup

        yup.export(path, self.selectedonly)

        return {"FINISHED"}


def menu_func(
    self: bl_ui.space_topbar.TOPBAR_MT_file_export, context: bpy.types.Context
):
    self.layout.operator(ExportYUP.bl_idname, text="YUP GLTF (.gltf)")
