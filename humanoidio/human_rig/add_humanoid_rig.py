from typing import cast, Optional
import bpy
from .humanoid_utils import (
    enter_pose,
    get_or_create_editbone,
    set_bone_collection,
    get_or_create_constraint,
    get_human_bone,
    get_human_editbone,
    get_human_posebone,
)
import math


def make_inverted_pelvis(obj: bpy.types.Object):
    mode = bpy.context.object.mode
    if mode != "EDIT":
        print(f"enter EDIT mode from {mode} mode")
        bpy.ops.object.mode_set(mode="EDIT")

    armature = cast(bpy.types.Armature, obj.data)

    root = get_or_create_editbone(armature, "Root")
    root.parent = None
    root.use_connect = False
    root.head = (0, 0, 0)
    root.tail = (0, 1, 0)

    cog = get_or_create_editbone(armature, "COG")
    cog.parent = root
    cog.head = get_human_editbone(armature, "spine").head
    cog.tail = (cog.head.x, cog.head.y + 0.4, cog.head.z)

    pelvis = get_or_create_editbone(armature, "Pelvis")
    pelvis.parent = cog
    pelvis.use_connect = False
    pelvis.head = cog.head

    hips = get_human_editbone(armature, "hips")
    pelvis.tail = hips.head

    hips.parent = pelvis
    with enter_pose(obj):
        set_bone_collection(obj, "Root", "Rig", "THEME05")
        set_bone_collection(obj, "COG", "Rig", "THEME05")
        set_bone_collection(obj, "Pelvis", "Rig", "THEME05")
        set_bone_collection(obj, "spine", "Rig", "THEME05")
        set_bone_collection(obj, "chest", "Rig", "THEME05")
        set_bone_collection(obj, "neck", "Rig", "THEME05")
        set_bone_collection(obj, "head", "Rig", "THEME05")
        set_bone_collection(obj, "left_toes", "Rig", "THEME05")
        set_bone_collection(obj, "right_toes", "Rig", "THEME05")

        hips = get_human_posebone(obj, "hips")
        hips.lock_rotation = (True, True, True)
        hips.lock_scale = (True, True, True)
        get_human_bone(armature, "hips").hide = True

    get_human_bone(armature, "spine").use_inherit_rotation = False


def make_leg_ik(obj: bpy.types.Object, suffix: str):
    mode = bpy.context.object.mode
    if mode != "EDIT":
        print(f"enter EDIT mode from {mode} mode")
        bpy.ops.object.mode_set(mode="EDIT")

    armature = cast(bpy.types.Armature, obj.data)

    prefix = ""
    if suffix == ".L":
        prefix = "left_"
    elif suffix == ".R":
        prefix = "right_"

    foot_name = f"{prefix}foot"
    foot_offset_name = f"FootOffset{suffix}"
    ik_name = f"LegIK{suffix}"
    upper_name = f"{prefix}upper_leg"
    lower_name = f"{prefix}lower_leg"
    pole_name = f"LegPole{suffix}"

    ik_head = get_human_editbone(armature, foot_name).head
    ik = get_or_create_editbone(armature, ik_name)
    ik.parent = armature.edit_bones["Root"]
    ik.use_connect = False
    ik.head = ik_head
    ik.tail = (ik_head.x, ik_head.y + 0.2, ik_head.z)

    pole_head = get_human_editbone(armature, lower_name).head
    pole = get_or_create_editbone(armature, pole_name)
    pole.parent = ik
    pole.use_connect = False
    pole.head = (pole_head.x, pole_head.y - 0.4, pole_head.z)
    pole.tail = (pole_head.x, pole_head.y - 0.6, pole_head.z)

    upper = get_human_editbone(armature, upper_name)
    lower = get_human_editbone(armature, lower_name)
    if upper.vector == lower.vector:
        # ちょっと曲げる
        lower.head.y -= 0.01

    foot_offset = get_or_create_editbone(armature, foot_offset_name)
    foot_offset.parent = ik
    foot_offset.use_connect = False
    foot_offset.head = get_human_editbone(armature, foot_name).head
    foot_offset.tail = get_human_editbone(armature, foot_name).tail

    with enter_pose(obj):
        # IK
        c = get_or_create_constraint(obj, lower_name, "IK")
        c.target = obj
        c.subtarget = ik_name
        c.pole_target = obj
        c.pole_subtarget = pole_name
        c.pole_angle = math.pi * (-90) / 180
        c.chain_count = 2
        set_bone_collection(obj, ik_name, "Rig", "THEME05")
        set_bone_collection(obj, pole_name, "Rig", "THEME05")

        # FootCopy
        c = get_or_create_constraint(obj, foot_name, "COPY_ROTATION", "Copy Rotation")
        c.target = obj
        c.subtarget = foot_offset_name


def make_arm_ik(obj: bpy.types.Object, suffix: str):
    mode = bpy.context.object.mode
    if mode != "EDIT":
        print(f"enter EDIT mode from {mode} mode")
        bpy.ops.object.mode_set(mode="EDIT")

    armature = cast(bpy.types.Armature, obj.data)

    prefix = ""
    if suffix == ".L":
        prefix = "left_"
    elif suffix == ".R":
        prefix = "right_"

    hand_name = f"{prefix}hand"
    ik_name = f"ArmIK{suffix}"
    upper_name = f"{prefix}upper_arm"
    lower_name = f"{prefix}lower_arm"
    pole_name = f"ArmPole{suffix}"

    hand = get_human_editbone(armature, hand_name)
    ik = get_or_create_editbone(armature, ik_name)
    ik.parent = armature.edit_bones["COG"]
    ik.use_connect = False
    ik.head = hand.head
    ik.tail = hand.tail

    pole_head = get_human_editbone(armature, lower_name).head
    pole = get_or_create_editbone(armature, pole_name)
    pole.parent = armature.edit_bones["COG"]
    pole.use_connect = False
    pole.head = (pole_head.x, pole_head.y + 0.4, pole_head.z)
    pole.tail = (pole_head.x, pole_head.y + 0.6, pole_head.z)

    upper = get_human_editbone(armature, upper_name)
    lower = get_human_editbone(armature, lower_name)
    if upper.vector == lower.vector:
        # ちょっと曲げる
        lower.head.y += 0.01

    with enter_pose(obj):
        # IK
        c = get_or_create_constraint(obj, lower_name, "IK")
        c.target = obj
        c.subtarget = ik_name
        c.pole_target = obj
        c.pole_subtarget = pole_name
        c.pole_angle = math.pi * (-90) / 180
        c.chain_count = 2
        set_bone_collection(obj, ik_name, "Rig", "THEME05")
        set_bone_collection(obj, pole_name, "Rig", "THEME05")

        # HandCopy
        c = get_or_create_constraint(obj, hand_name, "COPY_ROTATION", "Copy Rotation")
        c.target = obj
        c.subtarget = ik_name


def is_limb(bone: str) -> bool:
    if bone.startswith("LowerArm"):
        return True
    if bone.startswith("LowerLeg"):
        return True
    if "Metacarpal" in bone:
        return True
    if "Proximal" in bone:
        return True
    if "Intermediate" in bone:
        return True
    if "Distal" in bone:
        return True
    return False


def make_finger_bend(obj: bpy.types.Object, finger_name: str, suffix: str):
    mode = bpy.context.object.mode
    if mode != "EDIT":
        print(f"enter EDIT mode from {mode} mode")
        bpy.ops.object.mode_set(mode="EDIT")

    armature = cast(bpy.types.Armature, obj.data)

    prefix = ""
    if suffix == ".L":
        prefix = "left_"
    elif suffix == ".R":
        prefix = "right_"

    hand_name = f"{prefix}hand"
    if finger_name == "Thumb":
        proximal_name = f"{prefix}{finger_name.lower()}_metacarpal"
        intermediate_name = f"{prefix}{finger_name.lower()}_proximal"
    else:
        proximal_name = f"{prefix}{finger_name.lower()}_proximal"
        intermediate_name = f"{prefix}{finger_name.lower()}_intermediate"
    distal_name = f"{prefix}{finger_name.lower()}_distal"
    bend_name = f"Bend{finger_name}{suffix}"

    hand = get_human_editbone(armature, hand_name)
    proximal = get_human_editbone(armature, proximal_name)
    distal = get_human_editbone(armature, distal_name)

    bend = get_or_create_editbone(armature, bend_name)
    bend.parent = hand
    bend.use_connect = False
    delta = 0.01 if proximal.head.x > 0 else -0.01
    bend.head = proximal.head
    bend.tail = distal.tail
    bend.roll = proximal.roll
    if finger_name == "Thumb":
        bend.head.y -= 0.02
        bend.tail.y -= 0.02
    else:
        bend.head.z += 0.02
        bend.tail.z += 0.02

    def copy_rot(
        src_name: str,
        dst_name: str,
        scale_min: Optional[float] = None,
        *,
        scale_range: float = 0.3,
    ):
        c = get_or_create_constraint(obj, dst_name, "COPY_ROTATION", "Copy Rotation")
        c.target = obj
        c.subtarget = src_name
        c.target_space = "LOCAL"
        c.owner_space = "LOCAL"
        set_bone_collection(obj, src_name, "Rig", "THEME05")

        if scale_min:
            # for Intermediate & Distal
            c.use_y = False
            c.use_z = False
            # scale influence
            factor = 1 / scale_range
            scale_max = scale_min + scale_range
            driver = c.driver_add("influence")
            driver.driver.type = "SCRIPTED"
            var = driver.driver.variables.new()
            var.name = "var"
            var.type = "SINGLE_PROP"
            var.targets[0].id = obj
            var.targets[0].data_path = f'pose.bones["{src_name}"].scale[1]'
            driver.driver.expression = (
                f"({scale_max} - min(max(var, {scale_min}), {scale_max})) * {factor}"
            )

    def copy_rot_3(
        src_name: str,
        dst_name: str,
        scale_min: Optional[float] = None,
        *,
        scale_range: float = 0.3,
    ):
        c = get_or_create_constraint(obj, dst_name, "TRANSFORM", "Transformation")
        c.target = obj
        c.subtarget = src_name
        c.target_space = "LOCAL"
        c.owner_space = "LOCAL"

        c.map_from = "ROTATION"
        c.from_min_x_rot = -1
        c.from_max_x_rot = 1

        c.map_to = "ROTATION"
        c.to_min_x_rot = -3
        c.to_max_x_rot = 3
        c.mix_mode_rot = "BEFORE"

        set_bone_collection(obj, src_name, "Rig", "THEME05")

        if scale_min:
            # scale influence
            factor = 1 / scale_range
            scale_max = scale_min + scale_range
            driver = c.driver_add("influence")
            driver.driver.type = "SCRIPTED"
            var = driver.driver.variables.new()
            var.name = "var"
            var.type = "SINGLE_PROP"
            var.targets[0].id = obj
            var.targets[0].data_path = f'pose.bones["{src_name}"].scale[1]'
            driver.driver.expression = (
                f"({scale_max} - min(max(var, {scale_min}), {scale_max})) * {factor}"
            )

    with enter_pose(obj):
        bend_pose = obj.pose.bones[bend_name]
        bend_pose.rotation_mode = "ZYX"
        bend_pose.lock_location[0] = True
        bend_pose.lock_location[1] = True
        bend_pose.lock_location[2] = True
        if finger_name == "Thumb":
            bend_pose.lock_rotation[1] = True
        else:
            bend_pose.lock_rotation[1] = True
            bend_pose.lock_rotation[2] = True
        bend_pose.lock_scale[0] = True
        bend_pose.lock_scale[2] = True

        copy_rot(bend_name, proximal_name)
        if finger_name == "Thumb":
            copy_rot_3(bend_name, intermediate_name, 0.7, scale_range=0.3)
            copy_rot_3(bend_name, distal_name, 0.4, scale_range=0.3)
        else:
            copy_rot(bend_name, intermediate_name, 0.7, scale_range=0.3)
            copy_rot(bend_name, distal_name, 0.4, scale_range=0.3)


def make_hand_rig(obj, suffix: str):
    make_finger_bend(obj, "Index", suffix)
    make_finger_bend(obj, "Middle", suffix)
    make_finger_bend(obj, "Ring", suffix)
    make_finger_bend(obj, "Little", suffix)
    make_finger_bend(obj, "Thumb", suffix)

    mode = bpy.context.object.mode
    if mode != "EDIT":
        print(f"enter EDIT mode from {mode} mode")
        bpy.ops.object.mode_set(mode="EDIT")
    armature = cast(bpy.types.Armature, obj.data)

    prefix = ""
    if suffix == ".L":
        prefix = "left_"
    elif suffix == ".R":
        prefix = "right_"

    hand_name = f"{prefix}hand"
    spread_name = f"Spread{suffix}"
    little_proximal_name = f"{prefix}little_proximal"
    little_distal_name = f"{prefix}little_distal"

    hand = get_human_editbone(armature, hand_name)
    ring_proximal = get_human_editbone(armature, little_proximal_name)
    ring_distal = get_human_editbone(armature, little_distal_name)
    spread = get_or_create_editbone(armature, spread_name)
    spread.parent = hand
    spread.use_connect = False
    spread.head = ring_proximal.head
    spread.head.y += 0.02
    spread.head.z += 0.02
    spread.tail = ring_distal.tail
    spread.tail.y += 0.02
    spread.tail.z += 0.02
    spread.roll = ring_proximal.roll

    def copy_rot2bend(src_name: str, dst_name: str, influence: float):
        c = get_or_create_constraint(obj, dst_name, "TRANSFORM", "Transformation")
        c.target = obj
        c.subtarget = src_name
        c.target_space = "LOCAL"
        c.owner_space = "LOCAL"

        c.map_from = "ROTATION"
        c.from_min_z_rot = -1.5  # about pi/2
        c.from_max_z_rot = 1.5

        c.map_to = "ROTATION"
        c.to_min_z_rot = -1.5 * influence
        c.to_max_z_rot = 1.5 * influence
        c.mix_mode_rot = "BEFORE"

        set_bone_collection(obj, src_name, "Rig", "THEME05")

    with enter_pose(obj):
        spread_pose = obj.pose.bones[spread_name]
        spread_pose.rotation_mode = "ZYX"
        spread_pose.lock_rotation = [True, True, False]
        copy_rot2bend(spread_name, f"BendIndex{suffix}", -0.65)
        # copy_rot2bend(spread_name, f'BendMiddle{suffix}')
        copy_rot2bend(spread_name, f"BendRing{suffix}", 0.65)
        copy_rot2bend(spread_name, f"BendLittle{suffix}", 1)


class AddHumanoidRig(bpy.types.Operator):
    """AddRig to HumanoidArmature"""

    bl_idname = "humanoid.add_rig"
    bl_label = "Add Rig to Humanoid"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return isinstance(context.active_object.data, bpy.types.Armature)

    def execute(self, context):
        obj = context.active_object
        with enter_pose(obj):
            for b in obj.pose.bones:
                b.rotation_mode = "ZYX"
                b.lock_scale = [True, True, True]
                if is_limb(b.name):
                    b.lock_rotation[1] = True
                    b.lock_rotation[2] = True

        make_inverted_pelvis(obj)
        make_leg_ik(obj, ".L")
        make_leg_ik(obj, ".R")
        make_arm_ik(obj, ".L")
        make_arm_ik(obj, ".R")
        make_hand_rig(obj, ".L")
        make_hand_rig(obj, ".R")
        return {"FINISHED"}
