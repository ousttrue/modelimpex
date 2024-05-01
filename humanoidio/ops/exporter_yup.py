from typing import Literal
import pathlib
import bpy
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty  # type: ignore
import bl_ui.space_topbar


class ExportYUP(bpy.types.Operator, ExportHelper):
    """Export selection to YUP"""

    bl_idname = "humanoidio.export_yup"
    bl_label = "Export YUP GLTF"

    # Export options
    selectedonly: BoolProperty(
        name="Export Selected Objects Only",
        description="Export only selected objects",
        default=True,
    )  # type: ignore

    # ExportHelper mixin class uses this
    filename_ext = ".vrm"

    filter_glob: StringProperty(default="*.vrm;*.glb;*.gltf", options={"HIDDEN"})  # type: ignore

    def execute(
        self, context: bpy.types.Context | None = None
    ) -> set[
        Literal["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH", "INTERFACE"]
    ]:
        # ext = pathlib.Path(self.filepath).suffix.lower()
        # if ext != ".gltf" and ext != ".glb":
        #     self.filepath = bpy.path.ensure_ext(self.filepath, ".glb")
        path = pathlib.Path(self.filepath).absolute()

        from .. import yup

        yup.export(path, self.selectedonly)  # type ignore

        return {"FINISHED"}


def menu_func(
    self: bl_ui.space_topbar.TOPBAR_MT_file_export, context: bpy.types.Context
):
    self.layout.operator(ExportYUP.bl_idname, text="YUP GLTF (.gltf)")
