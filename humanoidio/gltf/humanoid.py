from typing import Literal, TypeAlias

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
