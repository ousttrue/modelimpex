# This is dummy for development. Main is `../__init__.py`
bl_info = {
    "name": "humanoidio",
    "blender": (4, 1, 0),
    "category": "Import-Export",
}

import bpy
from .ops.importer import Importer, menu as import_menu
from .ops.exporter import Exporter, menu as export_menu
from .ops.exporter_yup import ExportYUP, menu_func as export_yup_menu
from . import human_rig

CLASSES = [Importer, Exporter, ExportYUP] + human_rig.CLASSES


def register():
    for c in CLASSES:
        bpy.utils.register_class(c)  # type: ignore

        if hasattr(c, "bl_menu"):
            human_rig.add_to_menu(c.bl_menu, c)

    bpy.types.TOPBAR_MT_file_import.append(import_menu)  # type: ignore
    bpy.types.TOPBAR_MT_file_export.append(export_menu)  # type: ignore
    bpy.types.TOPBAR_MT_file_export.append(export_yup_menu)  # type: ignore

    bpy.types.Armature.humanoid = bpy.props.PointerProperty(
        type=human_rig.HumanoidProperties
    )


def unregister():
    for c in reversed(CLASSES):
        bpy.utils.unregister_class(c)  # type: ignore

        # if hasattr(c, "bl_menu"):
        #     human_rig.remove_from_menu(c.bl_menu, c)

    bpy.types.TOPBAR_MT_file_import.remove(import_menu)  # type: ignore
    bpy.types.TOPBAR_MT_file_export.remove(export_menu)  # type: ignore
    bpy.types.TOPBAR_MT_file_export.remove(export_yup_menu)  # type: ignore
