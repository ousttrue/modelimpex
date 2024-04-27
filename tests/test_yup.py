import math
import pathlib
import unittest
from logging import basicConfig, DEBUG
import bpy
import humanoidio

humanoidio.register()

HERE = pathlib.Path(__file__).parent


def set_key(bl_obj: bpy.types.Object, frame: int, euler: tuple[float, float, float]):
    print("set_key", bl_obj, frame, euler)
    bl_obj.rotation_euler = euler
    bl_obj.keyframe_insert(data_path="rotation_euler", frame=frame)


def set_copy_rotation(src: bpy.types.Object, dst: bpy.types.Object):
    print(src, dst)
    bpy.context.view_layer.objects.active = dst
    bpy.ops.object.constraint_add(type="COPY_ROTATION")
    c = dst.constraints[-1]
    c.target = src
    print(c)
    # Target space
    # Owner space
    # Influence


class TestYup(unittest.TestCase):
    def test(self):
        # # cube
        bpy.ops.mesh.primitive_cube_add(
            size=2,
            enter_editmode=False,
            align="WORLD",
            location=(3, 0, 0),
            scale=(1, 1, 1),
        )
        bpy.context.active_object.name = "dst"

        # setup key frame
        bpy.context.scene.frame_end = 60
        bl_cube = bpy.context.collection.objects["Cube"]
        set_key(bl_cube, 1, (0, 0, 0))
        set_key(bl_cube, 20, (0, 0, math.pi / 180 * 120))
        set_key(bl_cube, 40, (0, 0, math.pi / 180 * 240))
        set_key(bl_cube, 60, (0, 0, math.pi / 180 * 360))
        bl_cube.animation_data.action.fcurves[-1].extrapolation = "LINEAR"

        set_copy_rotation(
            bpy.context.collection.objects["Cube"],
            bpy.context.collection.objects["dst"],
        )

        # deselect
        bpy.ops.object.select_all(action="DESELECT")

        # save
        bpy.ops.wm.save_as_mainfile(filepath=str(HERE.parent / "export.blend"))

        # export
        path = HERE.parent / "export.glb"
        bpy.ops.humanoidio.export_yup(filepath=str(path))  # type: ignore


if __name__ == "__main__":
    basicConfig(
        level=DEBUG,
        datefmt="%H:%M:%S",
        format="%(asctime)s[%(levelname)s][%(name)s.%(funcName)s] %(message)s",
    )

    unittest.main()
