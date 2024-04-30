import bpy

# from . import humanoid_utils
from .humanoid_properties import HumanoidProperties
from .create_humanoid import CreateHumanoid
from .add_humanoid_rig import AddHumanoidRig
from .copy_humanoid_pose import CopyHumanoidPose
from .guess_human_bones import GuessHumanBones
from .humanoid_panel import ArmatureHumanoidPanel, SelectPoseBone


OPERATORS = [
    CreateHumanoid,
    AddHumanoidRig,
    CopyHumanoidPose,
    GuessHumanBones,
    SelectPoseBone,
]
CLASSES = [HumanoidProperties, ArmatureHumanoidPanel] + OPERATORS


def add_to_menu(menu: str, op: bpy.types.Operator):
    def menu_func(self, _context):
        if hasattr(op, "bl_icon"):
            self.layout.operator(op.bl_idname, icon=op.bl_icon)
        else:
            self.layout.operator(op.bl_idname)

    getattr(bpy.types, menu).prepend(menu_func)
