from logging import getLogger
from typing import Tuple

logger = getLogger(__name__)

import bpy
from bpy_extras.io_utils import ImportHelper
import pathlib
from .. import gltf
from .. import blender_scene
from .. import mmd


class Importer(bpy.types.Operator, ImportHelper):
    bl_idname = "humanoidio.importer"
    bl_label = "humanoidio Importer"

    def execute(self, context: bpy.types.Context):
        logger.debug("#### start ####")
        # read file
        path = pathlib.Path(self.filepath).absolute()
        ext = path.suffix.lower()
        if ext == ".pmx" or ext == ".pmd":
            loader = mmd.load(path.read_bytes())
            conversion = gltf.Conversion(
                gltf.Coordinate.VRM1, gltf.Coordinate.BLENDER_ROTATE
            )

        else:
            loader, conversion = gltf.load(path, gltf.Coordinate.BLENDER_ROTATE)

        # build mesh
        collection = bpy.data.collections.new(name=path.name)
        context.scene.collection.children.link(collection)
        bl_importer = blender_scene.Importer(collection, conversion)
        bl_importer.load(loader)

        logger.debug("#### end ####")
        return {"FINISHED"}


def menu(self, context: bpy.types.Context):
    self.layout.operator(Importer.bl_idname, text=f"humanoidio (.gltf;.glb;.vrm;.pmx)")
