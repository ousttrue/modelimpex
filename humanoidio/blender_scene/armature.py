import bpy
import mathutils  # type: ignore
from typing import Dict, Optional
from .. import gltf

EXCLUDE_HUMANOID_PARENT: list[gltf.human_bones.HumanoidBones] = ["head"]

EXCLUDE_HUMANOID_CHILDREN: list[gltf.human_bones.HumanoidBones] = [
    "hips",
    "leftUpperLeg",
    "rightUpperLeg",
    "leftShoulder",
    "rightShoulder",
    "leftEye",
    "rightEye",
    #
    "leftThumbProximal",
    "leftIndexProximal",
    "leftMiddleProximal",
    "leftRingProximal",
    "leftLittleProximal",
    #
    "rightThumbProximal",
    "rightIndexProximal",
    "rightMiddleProximal",
    "rightRingProximal",
    "rightLittleProximal",
]

EXCLUDE_OTHERS: list[str] = [
    "J_Adj_L_FaceEyeSet",
    "J_Adj_R_FaceEyeSet",
]


class BoneConnector:
    """
    ボーンを適当に接続したり、しない場合でも tail を設定してやる

    tail を決める

    * child が 0。親からまっすぐに伸ばす
    * child が ひとつ。それ
    * child が 2つ以上。どれか選べ(同じざひょうのときは少しずらす。head と tail が同じボーンは消滅するので)
    """

    def __init__(self, bones: Dict[gltf.Node, bpy.types.EditBone]):
        self.bones = bones

    def extend_tail(self, node: gltf.Node):
        """
        親ボーンと同じ方向にtailを延ばす
        """
        bl_bone = self.bones[node]
        if node.parent:
            try:
                bl_parent = self.bones[node.parent]
                tail_offset = bl_bone.head - bl_parent.head  # type: ignore
                bl_bone.tail = bl_bone.head + tail_offset
            except KeyError:
                print(f"{node}.parent not found")

    def connect_tail(self, node: gltf.Node, tail: gltf.Node):
        bl_bone = self.bones[node]
        bl_tail = self.bones[tail]
        bl_bone.tail = bl_tail.head
        bl_tail.parent = bl_bone
        bl_tail.use_connect = True

    def traverse(self, node: gltf.Node, parent: Optional[gltf.Node], is_connect: bool):
        # connect
        if parent:
            # print(f'connect {parent} => {node}')
            bl_parent = self.bones[parent]
            bl_bone = self.bones.get(node)
            if not bl_bone:
                # not in skin
                return

            bl_bone.parent = bl_parent
            if is_connect:
                if bl_parent.head != bl_bone.head:
                    bl_parent.tail = bl_bone.head
                else:
                    bl_parent.tail = bl_bone.head + mathutils.Vector((0, 0, 1e-4))

                if parent and (
                    parent.humanoid_bone == "leftShoulder"
                    or parent.humanoid_bone == "rightShoulder"
                ):
                    # https://blenderartists.org/t/rigify-error-generation-has-thrown-an-exception-but-theres-no-exception-message/1228840
                    pass
                else:
                    bl_bone.use_connect = True

        if node.children:
            # recursive
            connect_child_index = None
            if node.humanoid_bone in EXCLUDE_HUMANOID_PARENT:
                pass
            elif any(child.humanoid_bone for child in node.children):
                # humanioid
                for i, child in enumerate(node.children):
                    if child.humanoid_bone:
                        if child.humanoid_bone in EXCLUDE_HUMANOID_CHILDREN:
                            continue
                        connect_child_index = i
                        break
            else:
                for i, child in enumerate(node.children):
                    if child.name in EXCLUDE_OTHERS:
                        continue
                    # とりあえず
                    connect_child_index = i
                    break

            # select connect child
            for i, child in enumerate(node.children):
                self.traverse(child, node, i == connect_child_index)
        else:
            # stop recursive
            self.extend_tail(node)


def connect_bones(bones: Dict[gltf.Node, bpy.types.EditBone]):

    nodes = bones.keys()
    roots: list[gltf.Node] = []

    for node in nodes:
        if not node.parent:
            roots.append(node)
        elif node.parent not in nodes:
            roots.append(node)

    connector = BoneConnector(bones)
    for root in roots:
        connector.traverse(root, None, False)
