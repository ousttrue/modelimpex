from logging import getLogger
from typing import Tuple

logger = getLogger(__name__)

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

    def execute(self, context: bpy.types.Context) -> set[str]:
        logger.debug("#### start ####")
        # read file
        path = pathlib.Path(self.filepath).absolute()  # type: ignore
        ext = path.suffix.lower()
        match ext:
            case ".pmx":
                loader = mmd.load_pmx(path.read_bytes())
                conversion = gltf.Conversion(
                    gltf.Coordinate.VRM1, gltf.Coordinate.BLENDER_ROTATE
                )

            case ".pmd":
                loader = mmd.load_pmd(path.read_bytes())
                conversion = gltf.Conversion(
                    gltf.Coordinate.VRM1, gltf.Coordinate.BLENDER_ROTATE
                )

            case _:
                loader, conversion = gltf.load(path, gltf.Coordinate.BLENDER_ROTATE)

        # build mesh
        if loader:
            collection = bpy.data.collections.new(name=path.name)
            context.scene.collection.children.link(collection)
            bl_importer = blender_scene.Importer(collection, conversion)
            bl_importer.load(loader)

            logger.debug("#### end ####")
            return {"FINISHED"}

        else:
            return {"FINISHED"}


def menu(self: bl_ui.space_topbar.TOPBAR_MT_file_export, context: bpy.types.Context):
    self.layout.operator(Importer.bl_idname, text=f"humanoidio (.gltf;.glb;.vrm;.pmx)")
