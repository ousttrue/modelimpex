from typing import Literal, TypeAlias, Callable
import re

LegBones: TypeAlias = (
    Literal["leftUpperLeg"]
    | Literal["rightUpperLeg"]
    | Literal["leftLowerLeg"]
    | Literal["rightLowerLeg"]
    | Literal["leftFoot"]
    | Literal["rightFoot"]
    | Literal["leftToes"]
    | Literal["rightToes"]
)
BodyBones: TypeAlias = (
    Literal["spine"]
    | Literal["chest"]
    | Literal["neck"]
    | Literal["head"]
    | Literal["leftEye"]
    | Literal["rightEye"]
    | Literal["jaw"]
    | Literal["upperChest"]
)
ArmBones: TypeAlias = (
    Literal["leftShoulder"]
    | Literal["rightShoulder"]
    | Literal["leftUpperArm"]
    | Literal["rightUpperArm"]
    | Literal["leftLowerArm"]
    | Literal["rightLowerArm"]
    | Literal["leftHand"]
    | Literal["rightHand"]
)
FingerBones: TypeAlias = (
    Literal["leftThumbProximal"]
    | Literal["leftThumbIntermediate"]
    | Literal["leftThumbDistal"]
    | Literal["leftIndexProximal"]
    | Literal["leftIndexIntermediate"]
    | Literal["leftIndexDistal"]
    | Literal["leftMiddleProximal"]
    | Literal["leftMiddleIntermediate"]
    | Literal["leftMiddleDistal"]
    | Literal["leftRingProximal"]
    | Literal["leftRingIntermediate"]
    | Literal["leftRingDistal"]
    | Literal["leftLittleProximal"]
    | Literal["leftLittleIntermediate"]
    | Literal["leftLittleDistal"]
    | Literal["rightThumbProximal"]
    | Literal["rightThumbIntermediate"]
    | Literal["rightThumbDistal"]
    | Literal["rightIndexProximal"]
    | Literal["rightIndexIntermediate"]
    | Literal["rightIndexDistal"]
    | Literal["rightMiddleProximal"]
    | Literal["rightMiddleIntermediate"]
    | Literal["rightMiddleDistal"]
    | Literal["rightRingProximal"]
    | Literal["rightRingIntermediate"]
    | Literal["rightRingDistal"]
    | Literal["rightLittleProximal"]
    | Literal["rightLittleIntermediate"]
    | Literal["rightLittleDistal"]
)
HumanoidBones: TypeAlias = (
    Literal["hips"] | LegBones | BodyBones | ArmBones | FingerBones
)

EXCLUDE_NAMES: list[Callable[[str], bool]] = [
    lambda x: re.search(r"[iIＩ][kKＫ]", x) != None,
    lambda x: "親" in x,
    lambda x: "ﾈｸﾀｲ" in x,
    lambda x: ("先" in x) and ("つま先" not in x),
    lambda x: "髪" in x,
    lambda x: "アホ毛" in x,
    lambda x: "捩" in x,
    lambda x: "もみあげ" in x,
    lambda x: "キャンセル" in x,
    lambda x: "スカート" in x,
    lambda x: "オフセ" in x,
    lambda x: "袖" in x,
    lambda x: "Point" in x,
    lambda x: "リボン" in x,
    lambda x: "自動" in x,
    lambda x: "ｽｶｰﾄ" in x,
]


def prefix(src: str, left: HumanoidBones, right: HumanoidBones) -> HumanoidBones:
    if src.startswith("右"):
        return left
    elif src.startswith("左"):
        return right
    else:
        raise RuntimeError()


def guess_humanbone(name: str) -> HumanoidBones | None:
    for ex in EXCLUDE_NAMES:
        if ex(name):
            return
    match name:
        case (
            "操作中心"
            | "エッジ倍率"
            | "全ての親"
            | "センター"
            | "グルーブ"
            | "右胸１"
            | "左胸１"
            | "右胸２"
            | "左胸２"
            | "右肩P"
            | "左肩P"
            | "右肩C"
            | "左肩C"
            | "右ひじ補助"
            | "左ひじ補助"
            | "右ダミー"
            | "左ダミー"
            | "メガネ"
            | "舌１"
            | "舌２"
            | "舌３"
            | "両目"
            | "右目戻"
            | "左目戻"
            | "右足D"
            | "左足D"
            | "右ひざD"
            | "左ひざD"
            | "右足首D"
            | "左足首D"
            | "腰"
            | "__mesh__"
        ):
            return
        case "下半身":
            return "hips"
        case "上半身":
            return "spine"
        case "上半身2":
            return "chest"
        case "首":
            return "neck"
        case "頭":
            return "head"
        case "右目" | "左目":
            return prefix(name, "leftEye", "rightEye")
        case "右足" | "左足":
            return prefix(name, "leftUpperLeg", "rightUpperLeg")
        case "右ひざ" | "左ひざ":
            return prefix(name, "leftLowerLeg", "rightLowerLeg")
        case "右足首" | "左足首":
            return prefix(name, "leftFoot", "rightFoot")
        case "右つま先" | "左つま先":
            return prefix(name, "leftToes", "rightToes")
        case "右肩" | "左肩":
            return prefix(name, "leftShoulder", "rightShoulder")
        case "右腕" | "左腕":
            return prefix(name, "leftUpperArm", "rightUpperArm")
        case "右ひじ" | "左ひじ":
            return prefix(name, "leftLowerArm", "rightLowerArm")
        case "右手首" | "左手首":
            return prefix(name, "leftHand", "rightHand")
        case "右人指１" | "左人指１":
            return prefix(name, "leftIndexProximal", "rightIndexProximal")
        case "右人指２" | "左人指２":
            return prefix(name, "leftIndexIntermediate", "rightIndexIntermediate")
        case "右人指３" | "左人指３":
            return prefix(name, "leftIndexDistal", "rightIndexDistal")
        case "右中指１" | "左中指１":
            return prefix(name, "leftMiddleProximal", "rightMiddleProximal")
        case "右中指２" | "左中指２":
            return prefix(name, "leftMiddleIntermediate", "rightMiddleIntermediate")
        case "右中指３" | "左中指３":
            return prefix(name, "leftMiddleDistal", "rightMiddleDistal")
        case "右薬指１" | "左薬指１":
            return prefix(name, "leftRingProximal", "rightRingProximal")
        case "右薬指２" | "左薬指２":
            return prefix(name, "leftRingIntermediate", "rightRingIntermediate")
        case "右薬指３" | "左薬指３":
            return prefix(name, "leftRingDistal", "rightRingDistal")
        case "右小指１" | "左小指１":
            return prefix(name, "leftLittleProximal", "rightLittleProximal")
        case "右小指２" | "左小指２":
            return prefix(name, "leftLittleIntermediate", "rightLittleIntermediate")
        case "右小指３" | "左小指３":
            return prefix(name, "leftLittleDistal", "rightLittleDistal")
        case _:
            # raise NotImplementedError(name)
            print(f"unknown: {name}")


# SPINE = [
#     HumanoidBones.hips,
#     HumanoidBones.spine,
#     HumanoidBones.chest,
#     HumanoidBones.upperChest,
#     HumanoidBones.neck,
# ]

# HEAD = [
#     HumanoidBones.head,
#     HumanoidBones.leftEye,
#     HumanoidBones.rightEye,
#     HumanoidBones.jaw,
# ]

# LEGS = [
#     HumanoidBones.leftUpperLeg,
#     HumanoidBones.leftLowerArm,
#     HumanoidBones.leftFoot,
#     HumanoidBones.leftToes,
#     HumanoidBones.rightUpperLeg,
#     HumanoidBones.rightLowerArm,
#     HumanoidBones.rightFoot,
#     HumanoidBones.rightToes,
# ]

# ARMS = [
#     HumanoidBones.leftUpperArm,
#     HumanoidBones.leftLowerArm,
#     HumanoidBones.leftHand,
#     HumanoidBones.rightUpperArm,
#     HumanoidBones.rightLowerArm,
#     HumanoidBones.rightHand,
# ]

# LEFT_FINGERS = [
#     HumanoidBones.leftThumbProximal,
#     HumanoidBones.leftThumbIntermediate,
#     HumanoidBones.leftThumbDistal,
#     HumanoidBones.leftIndexProximal,
#     HumanoidBones.leftIndexIntermediate,
#     HumanoidBones.leftIndexDistal,
#     HumanoidBones.leftMiddleProximal,
#     HumanoidBones.leftMiddleIntermediate,
#     HumanoidBones.leftMiddleDistal,
#     HumanoidBones.leftRingProximal,
#     HumanoidBones.leftRingIntermediate,
#     HumanoidBones.leftRingDistal,
#     HumanoidBones.leftLittleProximal,
#     HumanoidBones.leftLittleIntermediate,
#     HumanoidBones.leftLittleDistal,
# ]

# RIGHT_FINGERS = [
#     HumanoidBones.rightThumbProximal,
#     HumanoidBones.rightThumbIntermediate,
#     HumanoidBones.rightThumbDistal,
#     HumanoidBones.rightIndexProximal,
#     HumanoidBones.rightIndexIntermediate,
#     HumanoidBones.rightIndexDistal,
#     HumanoidBones.rightMiddleProximal,
#     HumanoidBones.rightMiddleIntermediate,
#     HumanoidBones.rightMiddleDistal,
#     HumanoidBones.rightRingProximal,
#     HumanoidBones.rightRingIntermediate,
#     HumanoidBones.rightRingDistal,
#     HumanoidBones.rightLittleProximal,
#     HumanoidBones.rightLittleIntermediate,
#     HumanoidBones.rightLittleDistal,
# ]
