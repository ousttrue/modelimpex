from typing import Literal
import contextlib
import bpy


def prop_to_name(armature: bpy.types.Armature, prop: str) -> str | None:
    if hasattr(armature.humanoid, prop):  # type: ignore
        return getattr(armature.humanoid, prop)  # type: ignore


def get_human_bone(armature: bpy.types.Armature, prop: str) -> bpy.types.Bone | None:
    name = prop_to_name(armature, prop)
    if name:
        return armature.bones.get(name)
    else:
        return armature.bones.get(prop)


def get_human_editbone(
    armature: bpy.types.Armature, prop: str
) -> bpy.types.EditBone | None:
    name = prop_to_name(armature, prop)
    if name:
        return armature.edit_bones.get(name)
    else:
        return armature.edit_bones.get(prop)


def get_human_posebone(obj: bpy.types.Object, prop: str) -> bpy.types.PoseBone | None:
    armature = obj.data
    assert isinstance(armature, bpy.types.Armature)
    name = prop_to_name(armature, prop)
    if name:
        return obj.pose.bones.get(name)
    else:
        return obj.pose.bones.get(prop)


def get_or_create_editbone(
    armature: bpy.types.Armature, name: str
) -> bpy.types.EditBone:
    if name in armature.edit_bones:
        return armature.edit_bones[name]
    return armature.edit_bones.new(name)


@contextlib.contextmanager
def enter_pose(obj: bpy.types.Object):
    bpy.context.view_layer.objects.active = obj
    if bpy.context.mode == "POSE":
        yield
    else:
        bpy.ops.object.posemode_toggle()
        try:
            yield
        finally:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.posemode_toggle()


def get_or_create_bone_collection(
    armature: bpy.types.Armature, name: str
) -> bpy.types.BoneCollection:
    if name not in armature.collections:
        armature.collections.new(name=name)
    return armature.collections[name]


def set_bone_collection(
    obj: bpy.types.Object,
    prop: str,
    group_name: str,
    theme: Literal[
        "DEFAULT",
        "THEME01",
        "THEME02",
        "THEME03",
        "THEME04",
        "THEME05",
        "THEME06",
        "THEME07",
        "THEME08",
        "THEME09",
        "THEME10",
        "THEME11",
        "THEME12",
        "THEME13",
        "THEME14",
        "THEME15",
        "THEME16",
        "THEME17",
        "THEME18",
        "THEME19",
        "THEME20",
        "CUSTOM",
    ],
):
    armature = obj.data
    assert isinstance(armature, bpy.types.Armature)
    collection = get_or_create_bone_collection(armature, group_name)
    bone = get_human_bone(armature, prop)
    if bone:
        bone.color.palette = theme
        collection.assign(bone)  # type: ignore


def get_or_create_constraint(
    armature_obj: bpy.types.Object,
    pose_bone_name: str,
    constraint_type: Literal[
        "CAMERA_SOLVER",
        "FOLLOW_TRACK",
        "OBJECT_SOLVER",
        "COPY_LOCATION",
        "COPY_ROTATION",
        "COPY_SCALE",
        "COPY_TRANSFORMS",
        "LIMIT_DISTANCE",
        "LIMIT_LOCATION",
        "LIMIT_ROTATION",
        "LIMIT_SCALE",
        "MAINTAIN_VOLUME",
        "TRANSFORM",
        "TRANSFORM_CACHE",
        "CLAMP_TO",
        "DAMPED_TRACK",
        "IK",
        "LOCKED_TRACK",
        "SPLINE_IK",
        "STRETCH_TO",
        "TRACK_TO",
        "ACTION",
        "ARMATURE",
        "CHILD_OF",
        "FLOOR",
        "FOLLOW_PATH",
        "PIVOT",
        "SHRINKWRAP",
    ],
    constraint_name: str = "",
):
    if not constraint_name:
        constraint_name = constraint_type
    pose_bone = get_human_posebone(armature_obj, pose_bone_name)
    if not pose_bone:
        return
    if constraint_name in pose_bone.constraints:
        return pose_bone.constraints[constraint_name]

    armature = armature_obj.data
    assert isinstance(armature, bpy.types.Armature)
    armature.bones.active = get_human_bone(armature, pose_bone_name)  # type: ignore
    bpy.ops.pose.constraint_add(type=constraint_type)
    return pose_bone.constraints[constraint_name]
