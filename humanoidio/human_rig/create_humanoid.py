from typing import NamedTuple, Tuple, List
import bpy
import math
from .humanoid_utils import get_or_create_editbone

ROLL_MAP = {
    "Shoulder.L": 90,
    "UpperArm.L": 90,
    "LowerArm.L": 90,
    "Shoulder.R": -90,
    "UpperArm.R": -90,
    "LowerArm.R": -90,
    "Toes.L": 180,
    "Toes.R": 180,
    "ThumbMetacarpal.L": -90,
    "ThumbProximal.L": -90,
    "ThumbDistal.L": -90,
    "ThumbMetacarpal.R": 90,
    "ThumbProximal.R": 90,
    "ThumbDistal.R": 90,
    "IndexProximal.L": 180,
    "IndexIntermediate.L": 180,
    "IndexDistal.L": 180,
    "MiddleProximal.L": 180,
    "MiddleIntermediate.L": 180,
    "MiddleDistal.L": 180,
    "RingProximal.L": 180,
    "RingIntermediate.L": 180,
    "RingDistal.L": 180,
    "LittleProximal.L": 180,
    "LittleIntermediate.L": 180,
    "LittleDistal.L": 180,
    "IndexProximal.R": 180,
    "IndexIntermediate.R": 180,
    "IndexDistal.R": 180,
    "MiddleProximal.R": 180,
    "MiddleIntermediate.R": 180,
    "MiddleDistal.R": 180,
    "RingProximal.R": 180,
    "RingIntermediate.R": 180,
    "RingDistal.R": 180,
    "LittleProximal.R": 180,
    "LittleIntermediate.R": 180,
    "LittleDistal.R": 180,
}


class Bone(NamedTuple):
    human_bone: str
    head: Tuple[float, float, float]
    children: List["Bone"] = []

    def create(self, armature: bpy.types.Armature, parent: bpy.types.EditBone):
        name = self.human_bone
        if parent and self.human_bone == "tip":
            name = parent.name + ".tip"

        bone = get_or_create_editbone(armature, name)
        bone.head = self.head
        if parent:
            bone.parent = parent
            bone.head += parent.head
        if bone.head.x > 0:
            bone.name += ".L"
        elif bone.head.x < 0:
            bone.name += ".R"
        bone.tail = bone.head
        for i, child in enumerate(self.children):
            child_bone = child.create(armature, bone)
            if i == 0:
                bone.tail = child_bone.head
                child_bone.use_connect = True
        return bone


def get_finger(name: str, lr: float, y: float) -> Bone:
    """
    手首から指: 10
    指: 5-3-2
    親指: 5-4-3
    """
    base = lr / 10
    return Bone(
        f"{name}Proximal",
        (base * 10, y, 0),
        [
            Bone(
                f"{name}Intermediate",
                (base * 5, 0, 0),
                [
                    Bone(
                        f"{name}Distal",
                        (base * 3, 0, 0),
                        [Bone("tip", (base * 2, 0, 0))],
                    )
                ],
            )
        ],
    )


def get_thumb(x, y, z) -> Bone:
    return Bone(
        f"ThumbMetacarpal",
        (0, 0, -0.02),
        [
            Bone(
                f"ThumbProximal",
                (x * 5, y * 5, z * 5),
                [
                    Bone(
                        f"ThumbDistal",
                        (x * 3, y * 3, z * 3),
                        [Bone("tip", (x * 2, y * 2, z * 2))],
                    )
                ],
            )
        ],
    )


def get_arm(lr: float) -> Bone:
    f = lr * 0.6
    return Bone(
        "Shoulder",
        (lr * 0.1, 0, math.fabs(lr) * 2),
        [
            Bone(
                "UpperArm",
                (lr, 0, 0),
                [
                    Bone(
                        "LowerArm",
                        (lr * 2, 0, 0),
                        [
                            Bone(
                                "Hand",
                                (lr * 2, 0, 0),
                                [
                                    get_finger("Middle", f, 0),
                                    get_finger("Index", f, -0.015),
                                    get_finger("Ring", f, 0.015),
                                    get_finger("Little", f, 0.03),
                                    get_thumb(f / 10, -abs(f / 10), 0),
                                ],
                            )
                        ],
                    )
                ],
            )
        ],
    )


def get_leg(tall: float, lr: float):
    # upper 1
    # lower 1
    # foot 0.2
    base = tall / 11
    return Bone(
        "UpperLeg",
        (lr * base, 0, 0),
        [
            Bone(
                "LowerLeg",
                (0, 0, -base * 5),
                [
                    Bone(
                        "Foot",
                        (0, 0, -base * 5),
                        [
                            Bone(
                                "Toes",
                                (0, -base, -base),
                                [Bone("tip", (0, -base, 0))],
                            )
                        ],
                    )
                ],
            ),
        ],
    )


def get_humanoid(tall: float):
    head = tall / 6
    # head=1
    #
    # neck  1
    # chest 4
    # spine 2
    # hips  2
    base = head * 2 / 9
    return Bone(
        "Hips",
        (0, 0, tall / 2),
        [
            Bone(
                "Spine",
                (0, 0, base * 2),
                [
                    Bone(
                        "Chest",
                        (0, 0, base * 2),
                        [
                            Bone(
                                "Neck",
                                (0, 0, base * 4),
                                [
                                    Bone(
                                        "Head",
                                        (0, 0, base),
                                        [Bone("tip", (0, 0, head))],
                                    )
                                ],
                            ),
                            get_arm(base * 2),
                            get_arm(-base * 2),
                        ],
                    )
                ],
            ),
            get_leg(tall / 2, 1),
            get_leg(tall / 2, -1),
        ],
    )


def activate(context, obj):
    context.view_layer.objects.active = obj
    obj.select_set(True)


def create(context):
    armature: bpy.types.Armature = bpy.data.armatures.new("Humanoid")
    obj = bpy.data.objects.new("Humanoid", armature)
    context.scene.collection.objects.link(obj)

    activate(context, obj)

    # to edit mode
    mode = context.object.mode
    if mode != "EDIT":
        print(f"enter EDIT mode from {mode} mode")
        bpy.ops.object.mode_set(mode="EDIT")

    # armature.show_names = True
    armature.show_axes = True
    armature.use_mirror_x = True
    armature.display_type = "OCTAHEDRAL"

    humanoid = get_humanoid(1.6)

    # root
    root = get_or_create_editbone(armature, "Root")
    root.tail = (0, 1, 0)
    humanoid.create(armature, root)

    # fix roll
    def to_rad(degree: float) -> float:
        return math.pi * degree / 180

    for k, roll in ROLL_MAP.items():
        armature.edit_bones[k].roll = to_rad(roll)

    # to object mode
    mode = context.object.mode
    if mode != "OBJECT":
        print(f"enter EDIT mode from {mode} mode")
        bpy.ops.object.mode_set(mode="OBJECT")

    # custom property
    armature.humanoid.hips = "Hips"
    armature.humanoid.spine = "Spine"
    armature.humanoid.chest = "Chest"
    armature.humanoid.neck = "Neck"
    armature.humanoid.head = "Head"

    armature.humanoid.left_shoulder = "Shoulder.L"
    armature.humanoid.left_upper_arm = "UpperArm.L"
    armature.humanoid.left_lower_arm = "LowerArm.L"
    armature.humanoid.left_hand = "Hand.L"
    armature.humanoid.right_shoulder = "Shoulder.R"
    armature.humanoid.right_upper_arm = "UpperArm.R"
    armature.humanoid.right_lower_arm = "LowerArm.R"
    armature.humanoid.right_hand = "Hand.R"

    armature.humanoid.left_upper_leg = "UpperLeg.L"
    armature.humanoid.left_lower_leg = "LowerLeg.L"
    armature.humanoid.left_foot = "Foot.L"
    armature.humanoid.left_toes = "Toes.L"
    armature.humanoid.right_upper_leg = "UpperLeg.R"
    armature.humanoid.right_lower_leg = "LowerLeg.R"
    armature.humanoid.right_foot = "Foot.R"
    armature.humanoid.right_toes = "Toes.R"

    armature.humanoid.left_thumb_metacarpal = "ThumbMetacarpal.L"
    armature.humanoid.left_thumb_proximal = "ThumbProximal.L"
    armature.humanoid.left_thumb_distal = "ThumbDistal.L"
    armature.humanoid.left_index_proximal = "IndexProximal.L"
    armature.humanoid.left_index_intermediate = "IndexIntermediate.L"
    armature.humanoid.left_index_distal = "IndexDistal.L"
    armature.humanoid.left_middle_proximal = "MiddleProximal.L"
    armature.humanoid.left_middle_intermediate = "MiddleIntermediate.L"
    armature.humanoid.left_middle_distal = "MiddleDistal.L"
    armature.humanoid.left_ring_proximal = "RingProximal.L"
    armature.humanoid.left_ring_intermediate = "RingIntermediate.L"
    armature.humanoid.left_ring_distal = "RingDistal.L"
    armature.humanoid.left_little_proximal = "LittleProximal.L"
    armature.humanoid.left_little_intermediate = "LittleIntermediate.L"
    armature.humanoid.left_little_distal = "LittleDistal.L"

    armature.humanoid.right_thumb_metacarpal = "ThumbMetacarpal.R"
    armature.humanoid.right_thumb_proximal = "ThumbProximal.R"
    armature.humanoid.right_thumb_distal = "ThumbDistal.R"
    armature.humanoid.right_index_proximal = "IndexProximal.R"
    armature.humanoid.right_index_intermediate = "IndexIntermediate.R"
    armature.humanoid.right_index_distal = "IndexDistal.R"
    armature.humanoid.right_middle_proximal = "MiddleProximal.R"
    armature.humanoid.right_middle_intermediate = "MiddleIntermediate.R"
    armature.humanoid.right_middle_distal = "MiddleDistal.R"
    armature.humanoid.right_ring_proximal = "RingProximal.R"
    armature.humanoid.right_ring_intermediate = "RingIntermediate.R"
    armature.humanoid.right_ring_distal = "RingDistal.R"
    armature.humanoid.right_little_proximal = "LittleProximal.R"
    armature.humanoid.right_little_intermediate = "LittleIntermediate.R"
    armature.humanoid.right_little_distal = "LittleDistal.R"

    # to object mode
    mode = context.object.mode
    if mode != "OBJECT":
        print(f"enter EDIT mode from {mode} mode")
        bpy.ops.object.mode_set(mode="OBJECT")


class CreateHumanoid(bpy.types.Operator):
    """CreateHumanoidArmature"""

    bl_idname = "humanoid.create"
    bl_label = "Humanoid(VRM-1.0)"
    bl_options = {"REGISTER", "UNDO"}
    bl_icon = "OUTLINER_OB_ARMATURE"
    bl_menu = "VIEW3D_MT_armature_add"

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT"

    def execute(self, context):
        create(context)
        return {"FINISHED"}
