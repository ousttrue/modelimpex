from typing import Literal
import bpy
from bpy_extras.io_utils import ImportHelper
import bl_ui.space_topbar
import pathlib
from .. import gltf
from .. import blender_scene
from .. import mmd


class Importer(bpy.types.Operator, ImportHelper):
    bl_idname = "humanoidio.importer"
    bl_label = "humanoidio Importer"

    def execute(
        self, context: bpy.types.Context | None = None
    ) -> set[
        Literal["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH", "INTERFACE"]
    ]:
        # read file
        path = pathlib.Path(self.filepath).absolute()  # type: ignore
        data = path.read_bytes()
        ext = path.suffix.lower()
        match ext:
            case ".pmx":
                # TODO: rig のシンプル化
                # skinning に使われない joint の削除
                # humanoid 部分の再構成
                loader = mmd.load_pmx(path, data)
                conversion = gltf.Conversion(
                    gltf.Coordinate.VRM1, gltf.Coordinate.BLENDER_ROTATE
                )

            case ".pmd":
                # TODO: rig のシンプル化
                # skinning に使われない joint の削除
                # humanoid 部分の再構成
                loader = mmd.load_pmd(path, data)
                conversion = gltf.Conversion(
                    gltf.Coordinate.VRM1, gltf.Coordinate.BLENDER_ROTATE
                )

            case _:
                loader, conversion = gltf.load(
                    path, data, gltf.Coordinate.BLENDER_ROTATE
                )

        # build mesh
        if not loader:
            return {"CANCELLED"}

        collection = bpy.data.collections.new(name=path.name)
        context.scene.collection.children.link(collection)  # type: ignore
        bl_importer = blender_scene.Importer(collection, conversion)
        bl_importer.load(loader)

        return {"FINISHED"}


def menu(self: bl_ui.space_topbar.TOPBAR_MT_file_export, context: bpy.types.Context):
    self.layout.operator(Importer.bl_idname, text=f"humanoidio (.gltf;.glb;.vrm;.pmx)")
