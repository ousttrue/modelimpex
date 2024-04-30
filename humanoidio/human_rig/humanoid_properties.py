import bpy
from typing import NamedTuple, List, Iterable, Optional

PROP_NAMES = [
    "hips",
    "spine",
    "chest",
    "neck",
    "head",
    "left_shoulder",
    "left_upper_arm",
    "left_lower_arm",
    "left_hand",
    "right_shoulder",
    "right_upper_arm",
    "right_lower_arm",
    "right_hand",
    "left_upper_leg",
    "left_lower_leg",
    "left_foot",
    "left_toes",
    "right_upper_leg",
    "right_lower_leg",
    "right_foot",
    "right_toes",
    "left_thumb_metacarpal",
    "left_thumb_proximal",
    "left_thumb_distal",
    "left_index_proximal",
    "left_index_intermediate",
    "left_index_distal",
    "left_middle_proximal",
    "left_middle_intermediate",
    "left_middle_distal",
    "left_ring_proximal",
    "left_ring_intermediate",
    "left_ring_distal",
    "left_little_proximal",
    "left_little_intermediate",
    "left_little_distal",
    "right_thumb_metacarpal",
    "right_thumb_proximal",
    "right_thumb_distal",
    "right_index_proximal",
    "right_index_intermediate",
    "right_index_distal",
    "right_middle_proximal",
    "right_middle_intermediate",
    "right_middle_distal",
    "right_ring_proximal",
    "right_ring_intermediate",
    "right_ring_distal",
    "right_little_proximal",
    "right_little_intermediate",
    "right_little_distal",
]

# for VRM
PROP_TO_HUMANBONE = {
    "left_shoulder": "leftShoulder",
    "left_upper_arm": "leftUpperArm",
    "left_lower_arm": "leftLowerArm",
    "left_hand": "leftHand",
    "right_shoulder": "rightShoulder",
    "right_upper_arm": "rightUpperArm",
    "right_lower_arm": "rightLowerArm",
    "right_hand": "rightHand",
    "left_upper_leg": "leftUpperLeg",
    "left_lower_leg": "leftLowerLeg",
    "left_foot": "leftFoot",
    "left_toes": "leftToes",
    "right_upper_leg": "rightUpperLeg",
    "right_lower_leg": "rightLowerLeg",
    "right_foot": "rightFoot",
    "right_toes": "rightToes",
    "left_thumb_metacarpal": "leftThumbMetacarpal",
    "left_thumb_proximal": "leftThumbProximal",
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
    "right_thumb_metacarpal": "rightThumbMetacarpal",
    "right_thumb_proximal": "rightThumbProximal",
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


class Node(NamedTuple):
    prop: str
    children: List["Node"]


def make_hand(prefix: str) -> Node:
    return Node(
        f"{prefix}hand",
        [
            Node(
                f"{prefix}thumb_metacarpal",
                [Node(f"{prefix}thumb_proximal", [Node(f"{prefix}thumb_distal", [])])],
            ),
            Node(
                f"{prefix}index_proximal",
                [
                    Node(
                        f"{prefix}index_intermediate",
                        [Node(f"{prefix}index_distal", [])],
                    )
                ],
            ),
            Node(
                f"{prefix}middle_proximal",
                [
                    Node(
                        f"{prefix}middle_intermediate",
                        [Node(f"{prefix}middle_distal", [])],
                    )
                ],
            ),
            Node(
                f"{prefix}ring_proximal",
                [
                    Node(
                        f"{prefix}ring_intermediate",
                        [Node(f"{prefix}ring_distal", [])],
                    )
                ],
            ),
            Node(
                f"{prefix}little_proximal",
                [
                    Node(
                        f"{prefix}little_intermediate",
                        [Node(f"{prefix}little_distal", [])],
                    )
                ],
            ),
        ],
    )


TREE = Node(
    "hips",
    [
        Node(
            "spine",
            [
                Node(
                    "chest",
                    [
                        Node("neck", [Node("head", [])]),
                        Node(
                            "left_shoulder",
                            [
                                Node(
                                    "left_upper_arm",
                                    [Node("left_lower_arm", [make_hand("left_")])],
                                )
                            ],
                        ),
                        Node(
                            "right_shoulder",
                            [
                                Node(
                                    "right_upper_arm",
                                    [Node("right_lower_arm", [make_hand("right_")])],
                                )
                            ],
                        ),
                    ],
                )
            ],
        ),
        Node(
            "left_upper_leg",
            [Node("left_lower_leg", [Node("left_foot", [Node("left_toes", [])])])],
        ),
        Node(
            "right_upper_leg",
            [Node("right_lower_leg", [Node("right_foot", [Node("right_toes", [])])])],
        ),
    ],
)


def get_node(prop: str) -> Optional[Node]:
    def find(node):
        if node.prop == prop:
            return node
        for child in node.children:
            found = find(child)
            if found:
                return found

    found = find(TREE)
    return found


def enum_children(prop: str) -> Iterable[str]:
    found = get_node(prop)
    if found:
        for child in found.children:
            yield child.prop


def get_parent(prop: str) -> Optional[str]:
    def find_parent(node) -> Optional[Node]:
        for child in node.children:
            if child.prop == prop:
                return node
            found = find_parent(child)
            if found:
                return found

    found = find_parent(TREE)
    if found:
        return found.prop


class HumanTree:
    def __init__(self, armature: bpy.types.Armature) -> None:
        # custom property
        self.humanoid_map = armature.humanoid
        assert self.humanoid_map

    def vrm_from_name(self, bone_name: str) -> Optional[str]:
        for prop in PROP_NAMES:
            if getattr(self.humanoid_map, prop) == bone_name:
                human_bone = PROP_TO_HUMANBONE.get(prop)
                if human_bone:
                    return human_bone
                else:
                    return prop

    def prop_from_name(self, bone_name: str) -> Optional[str]:
        for prop in PROP_NAMES:
            if getattr(self.humanoid_map, prop) == bone_name:
                return prop

    def child_bone_names_from_name(self, name: str) -> Iterable[str]:
        prop = self.prop_from_name(name)
        if prop:
            for child_prop in enum_children(prop):
                bone_name = getattr(self.humanoid_map, child_prop)
                if bone_name:
                    yield bone_name

    def get_parentname(self, name: str) -> Optional[str]:
        prop = self.prop_from_name(name)
        if prop:
            parent_prop = get_parent(prop)
            if parent_prop:
                name = getattr(self.humanoid_map, parent_prop)

    def bonename_from_prop(self, prop: str) -> Optional[str]:
        return getattr(self.humanoid_map, prop)


class HumanoidProperties(bpy.types.PropertyGroup):
    hips: bpy.props.StringProperty(name="hips")
    spine: bpy.props.StringProperty(name="spine")
    chest: bpy.props.StringProperty(name="chest")
    neck: bpy.props.StringProperty(name="neck")
    head: bpy.props.StringProperty(name="head")
    # arm(8)
    left_shoulder: bpy.props.StringProperty(name="left_shoulder")
    left_upper_arm: bpy.props.StringProperty(name="left_upper_arm")
    left_lower_arm: bpy.props.StringProperty(name="left_lower_arm")
    left_hand: bpy.props.StringProperty(name="left_hand")
    right_shoulder: bpy.props.StringProperty(name="right_shoulder")
    right_upper_arm: bpy.props.StringProperty(name="right_upper_arm")
    right_lower_arm: bpy.props.StringProperty(name="right_lower_arm")
    right_hand: bpy.props.StringProperty(name="right_hand")
    # leg(8)
    left_upper_leg: bpy.props.StringProperty(name="left_upper_leg")
    left_lower_leg: bpy.props.StringProperty(name="left_lower_leg")
    left_foot: bpy.props.StringProperty(name="left_foot")
    left_toes: bpy.props.StringProperty(name="left_toes")
    right_upper_leg: bpy.props.StringProperty(name="right_upper_leg")
    right_lower_leg: bpy.props.StringProperty(name="right_lower_leg")
    right_foot: bpy.props.StringProperty(name="right_foot")
    right_toes: bpy.props.StringProperty(name="right_toes")
    # fingers(30)
    left_thumb_metacarpal: bpy.props.StringProperty(name="left_thumb_metacarpal")
    left_thumb_proximal: bpy.props.StringProperty(name="left_thumb_proximal")
    left_thumb_distal: bpy.props.StringProperty(name="left_thumb_distal")
    left_index_proximal: bpy.props.StringProperty(name="left_index_proximal")
    left_index_intermediate: bpy.props.StringProperty(name="left_index_intermediate")
    left_index_distal: bpy.props.StringProperty(name="left_index_distal")
    left_middle_proximal: bpy.props.StringProperty(name="left_middle_proximal")
    left_middle_intermediate: bpy.props.StringProperty(name="left_middle_intermediate")
    left_middle_distal: bpy.props.StringProperty(name="left_middle_distal")
    left_ring_proximal: bpy.props.StringProperty(name="left_ring_proximal")
    left_ring_intermediate: bpy.props.StringProperty(name="left_ring_intermediate")
    left_ring_distal: bpy.props.StringProperty(name="left_ring_distal")
    left_little_proximal: bpy.props.StringProperty(name="left_little_proximal")
    left_little_intermediate: bpy.props.StringProperty(name="left_little_intermediate")
    left_little_distal: bpy.props.StringProperty(name="left_little_distal")

    right_thumb_metacarpal: bpy.props.StringProperty(name="right_thumb_metacarpal")
    right_thumb_proximal: bpy.props.StringProperty(name="right_thumb_proximal")
    right_thumb_distal: bpy.props.StringProperty(name="right_thumb_distal")
    right_index_proximal: bpy.props.StringProperty(name="right_index_proximal")
    right_index_intermediate: bpy.props.StringProperty(name="right_index_intermediate")
    right_index_distal: bpy.props.StringProperty(name="right_index_distal")
    right_middle_proximal: bpy.props.StringProperty(name="right_middle_proximal")
    right_middle_intermediate: bpy.props.StringProperty(
        name="right_middle_intermediate"
    )
    right_middle_distal: bpy.props.StringProperty(name="right_middle_distal")
    right_ring_proximal: bpy.props.StringProperty(name="right_ring_proximal")
    right_ring_intermediate: bpy.props.StringProperty(name="right_ring_intermediate")
    right_ring_distal: bpy.props.StringProperty(name="right_ring_distal")
    right_little_proximal: bpy.props.StringProperty(name="right_little_proximal")
    right_little_intermediate: bpy.props.StringProperty(
        name="right_little_intermediate"
    )
    right_little_distal: bpy.props.StringProperty(name="right_little_distal")
