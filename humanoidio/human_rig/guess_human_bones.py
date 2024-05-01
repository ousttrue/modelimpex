from typing import Literal
import bpy
from .humanoid_properties import PROP_NAMES, HumanoidProperties


VRM_MAP = {
    "hips": "hips",
    "spine": "spine",
    "chest": "chest",
    "upper_chest": "upperChest",
    "neck": "neck",
    "head": "head",
    "left_shoulder": "leftShoulder",
    "left_upper_arm": "leftUpperArm",
    "left_lower_arm": "leftLowerArm",
    "left_hand": "leftHand",
    "right_shoulder": "rightShoulder",
    "right_upper_arm": "rightUpperArm",
    "right_lower_arm": "rightLowerArm",
    "right_hand": "rightHand",
    #
    "left_upper_leg": "leftUpperLeg",
    "left_lower_leg": "leftLowerLeg",
    "left_foot": "leftFoot",
    "left_toes": "leftToes",
    "right_upper_leg": "rightUpperLeg",
    "right_lower_leg": "rightLowerLeg",
    "right_foot": "rightFoot",
    "right_toes": "rightToes",
    #
    "left_thumb_metacarpal": "leftThumbProximal",
    "left_thumb_proximal": "leftThumbIntermediate",
    "left_thumb_distal": "leftThumbDistal",
    "left_index_proximal": "leftIndexProximal",
    "left_index_intermediate": "leftIndexIntermediate",
    "left_index_distal": "leftIndexDistal",
    "left_middle_proximal": "leftMiddleProximal",
    "left_middle_intermediate": "leftMiddleIntermediate",
    "left_middle_distal": "leftMiddleDistal",
    "left_ring_proximal": "leftRingProximal",
    "left_ring_intermediate": "leftRingIntermediate",
    "left_ring_distal": "leftRingDistal",
    "left_little_proximal": "leftLittleProximal",
    "left_little_intermediate": "leftLittleIntermediate",
    "left_little_distal": "leftLittleDistal",
    #
    "right_thumb_metacarpal": "rightThumbProximal",
    "right_thumb_proximal": "rightThumbIntermediate",
    "right_thumb_distal": "rightThumbDistal",
    "right_index_proximal": "rightIndexProximal",
    "right_index_intermediate": "rightIndexIntermediate",
    "right_index_distal": "rightIndexDistal",
    "right_middle_proximal": "rightMiddleProximal",
    "right_middle_intermediate": "rightMiddleIntermediate",
    "right_middle_distal": "rightMiddleDistal",
    "right_ring_proximal": "rightRingProximal",
    "right_ring_intermediate": "rightRingIntermediate",
    "right_ring_distal": "rightRingDistal",
    "right_little_proximal": "rightLittleProximal",
    "right_little_intermediate": "rightLittleIntermediate",
    "right_little_distal": "rightLittleDistal",
}

RIGIFY_MAP = {
    "hips": "torso",
    "spine": "MCH-spine.002",
    "chest": "MCH-spine.003",
    # "upper_chest": "ORG-spine.003",
    "neck": "ORG-spine.004",
    "head": "ORG-spine.006",
    "left_shoulder": "ORG-shoulder.L",
    "left_upper_arm": "DEF-upper_arm.L",
    "left_lower_arm": "DEF-forearm.L",
    "left_hand": "DEF-hand.L",
    "right_shoulder": "ORG-shoulder.R",
    "right_upper_arm": "DEF-upper_arm.R",
    "right_lower_arm": "DEF-forearm.R",
    "right_hand": "DEF-hand.R",
    #
    "left_upper_leg": "ORG-thigh.L",
    "left_lower_leg": "ORG-shin.L",
    "left_foot": "ORG-foot.L",
    "left_toes": "ORG-toe.L",
    "right_upper_leg": "ORG-thigh.R",
    "right_lower_leg": "ORG-shin.R",
    "right_foot": "ORG-foot.R",
    "right_toes": "ORG-toe.R",
    #
    "left_thumb_metacarpal": "ORG-thumb.01.L",
    "left_thumb_proximal": "ORG-thumb.02.L",
    "left_thumb_distal": "ORG-thumb.03.L",
    "left_index_proximal": "ORG-f_index.01.L",
    "left_index_intermediate": "ORG-f_index.02.L",
    "left_index_distal": "ORG-f_index.03.L",
    "left_middle_proximal": "ORG-f_middle.01.L",
    "left_middle_intermediate": "ORG-f_middle.02.L",
    "left_middle_distal": "ORG-f_middle.03.L",
    "left_ring_proximal": "ORG-f_ring.01.L",
    "left_ring_intermediate": "ORG-f_ring.02.L",
    "left_ring_distal": "ORG-f_ring.03.L",
    "left_little_proximal": "ORG-f_pinky.01.L",
    "left_little_intermediate": "ORG-f_pinky.02.L",
    "left_little_distal": "ORG-f_pinky.03.L",
    #
    "right_thumb_metacarpal": "ORG-thumb.01.R",
    "right_thumb_proximal": "ORG-thumb.02.R",
    "right_thumb_distal": "ORG-thumb.03.R",
    "right_index_proximal": "ORG-f_index.01.R",
    "right_index_intermediate": "ORG-f_index.02.R",
    "right_index_distal": "ORG-f_index.03.R",
    "right_middle_proximal": "ORG-f_middle.01.R",
    "right_middle_intermediate": "ORG-f_middle.02.R",
    "right_middle_distal": "ORG-f_middle.03.R",
    "right_ring_proximal": "ORG-f_ring.01.R",
    "right_ring_intermediate": "ORG-f_ring.02.R",
    "right_ring_distal": "ORG-f_ring.03.R",
    "right_little_proximal": "ORG-f_pinky.01.R",
    "right_little_intermediate": "ORG-f_pinky.02.R",
    "right_little_distal": "ORG-f_pinky.03.R",
}

MMD_MAP = {
    "hips": "センター",
    "spine": "上半身",
    "neck": "首",
    "head": "頭",
    #
    "left_shoulder": "左肩",
    "left_upper_arm": "左腕",
    "left_lower_arm": "左ひじ",
    "left_hand": "左手首",
    #
    "left_upper_leg": "左足",
    "left_lower_leg": "左ひざ",
    "left_foot": "左足首",
    "left_toes": "左つま先",
    #
    "right_shoulder": "右肩",
    "right_upper_arm": "右腕",
    "right_lower_arm": "右ひじ",
    "right_hand": "右手首",
    #
    "right_upper_leg": "右足",
    "right_lower_leg": "右ひざ",
    "right_foot": "右足首",
    "right_toes": "右つま先",
    #
    "left_thumb_metacarpal": "左親指０",
    "left_thumb_proximal": "左親指１",
    "left_thumb_distal": "左親指２",
    "left_index_proximal": "左人指１",
    "left_index_intermediate": "左人指２",
    "left_index_distal": "左人指３",
    "left_middle_proximal": "左中指１",
    "left_middle_intermediate": "左中指２",
    "left_middle_distal": "左中指３",
    "left_ring_proximal": "左薬指１",
    "left_ring_intermediate": "左薬指２",
    "left_ring_distal": "左薬指３",
    "left_little_proximal": "左小指１",
    "left_little_intermediate": "左小指２",
    "left_little_distal": "左小指３",
    #
    "right_thumb_metacarpal": "右親指０",
    "right_thumb_proximal": "右親指１",
    "right_thumb_distal": "右親指２",
    "right_index_proximal": "右人指１",
    "right_index_intermediate": "右人指２",
    "right_index_distal": "右人指３",
    "right_middle_proximal": "右中指１",
    "right_middle_intermediate": "右中指２",
    "right_middle_distal": "右中指３",
    "right_ring_proximal": "右薬指１",
    "right_ring_intermediate": "右薬指２",
    "right_ring_distal": "右薬指３",
    "right_little_proximal": "右小指１",
    "right_little_intermediate": "右小指２",
    "right_little_distal": "右小指３",
}


def guess_bone(armature: bpy.types.Armature, prop: str) -> str | None:
    if hasattr(armature, "vrm_addon_extension"):
        vrm = armature.vrm_addon_extension
        if hasattr(vrm, "vrm1"):
            vrm1 = vrm.vrm1
            if hasattr(vrm1, "humanoid"):
                human_bones = vrm1.humanoid.human_bones
                if hasattr(human_bones, prop):
                    return getattr(human_bones, prop).node.get_bone_name()
        elif hasattr(vrm, "vrm0"):
            vrm0 = vrm.vrm0
            if hasattr(vrm0, "humanoid"):
                humanoid = vrm0.humanoid
                vrm0_bone_name = VRM_MAP.get(prop)
                for b in humanoid.human_bones:
                    name = b.node.get_bone_name()
                    # print(prop, name, b.bone)
                    if b.bone == vrm0_bone_name:
                        return name
        raise Exception(f"{prop} not found")

    bone_name = RIGIFY_MAP.get(prop)
    if bone_name and bone_name in armature.bones:
        return bone_name

    # fall back. name based search
    tokens = prop.split("_")
    search = tokens[-1].lower()

    found = [bone.name for bone in armature.bones if search in bone.name.lower()]
    if len(found) == 1:
        return found[0]
    if len(found) > 1:
        if tokens[0] == "left":
            for f in found:
                if "left" in f.lower():
                    return f
        elif tokens[0] == "right":
            for f in found:
                if "right" in f.lower():
                    return f

    return MMD_MAP.get(prop)


class GuessHumanBones(bpy.types.Operator):
    bl_idname = "humanoid.guess_bones"
    bl_label = "Guess Humanoid Bones"
    bl_options = {"REGISTER", "UNDO"}

    clear: bpy.props.BoolProperty(name="clear")  # type: ignore

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:  # type: ignore
        if context.active_object:  # type: ignore
            return isinstance(context.active_object.data, bpy.types.Armature)  # type: ignore
        return False

    def execute(
        self, context: bpy.types.Context | None = None
    ) -> set[
        Literal["RUNNING_MODAL", "CANCELLED", "FINISHED", "PASS_THROUGH", "INTERFACE"]
    ]:
        armature = context.active_object.data
        assert isinstance(armature, bpy.types.Armature)
        humanoid = HumanoidProperties.from_armature(armature)
        if self.clear:
            for prop in PROP_NAMES:
                setattr(humanoid, prop, "")
        else:
            for prop in PROP_NAMES:
                bone = getattr(humanoid, prop)
                if not bone:
                    bone = guess_bone(armature, prop)
                    if bone:
                        setattr(humanoid, prop, bone)

        return {"FINISHED"}
