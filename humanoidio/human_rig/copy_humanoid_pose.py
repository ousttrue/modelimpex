from typing import Optional
import bpy
import json
from . import humanoid_properties
from .humanoid_utils import enter_pose

VRM_ANIMATION = "VRMC_vrm_animation"
VRM_POSE = "UNIVRM_pose"


class Builder:
    def __init__(self, obj: bpy.types.Object, to_meter: float) -> None:
        self.obj = obj
        self.tree = humanoid_properties.HumanTree(obj.data)
        self.to_meter = to_meter

        self.gltf = {
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [
                {
                    "name": "__zup__",
                    "rotation": [-0.7071, 0, 0, 0.7071],
                }
            ],
            "asset": {"version": "2.0"},
            "extensionsUsed": [VRM_ANIMATION, VRM_POSE],
            "extensions": {
                VRM_ANIMATION: {
                    "humanoid": {
                        "humanBones": {},
                    },
                    "specVersion": "1.0",
                    "extras": {
                        VRM_POSE: {
                            "humanoid": {
                                "translation": [0, 0, 0],
                                "rotations": {},
                            },
                            "expressions": {
                                "preset": {
                                    "happy": 1,
                                    "Aa": 1,
                                }
                            },
                            "lookAt": {
                                "position": [4, 5, 6],
                            },
                        },
                    },
                },
            },
        }

    def add_gltf_node(self, gltf_parent: Optional[dict], gltf_node: dict) -> int:
        index = len(self.gltf["nodes"])
        if not gltf_parent:
            # root
            gltf_parent = self.gltf["nodes"][0]
        if "children" not in gltf_parent:
            gltf_parent["children"] = []
        gltf_parent["children"].append(index)
        self.gltf["nodes"].append(gltf_node)
        return index

    def _traverse_tpose(
        self,
        b: bpy.types.Bone,
        parent: Optional[bpy.types.Bone],
        gltf_parent,
        *,
        indent: str,
    ):
        m = b.matrix_local
        if parent:
            m = parent.matrix_local.inverted() @ m
        t, r, s = m.decompose()
        print(f"{indent}{b}: {t} {r}")
        gltf_node = {
            "name": b.name,
            "translation": [
                t.x * self.to_meter,
                t.y * self.to_meter,
                t.z * self.to_meter,
            ],
            "rotation": [r.x, r.y, r.z, r.w],
        }
        index = self.add_gltf_node(gltf_parent, gltf_node)
        bone_name = self.tree.vrm_from_name(b.name)
        if bone_name:
            # bone node mapping
            self.gltf["extensions"][VRM_ANIMATION]["humanoid"]["humanBones"][
                bone_name
            ] = {"node": index}

        for child_name in self.tree.child_bone_names_from_name(b.name):
            child = self.obj.data.bones[child_name]
            self._traverse_tpose(child, b, gltf_node, indent=indent + "  ")

        return gltf_node

    def get_tpose(self):
        hips_name = self.tree.bonename_from_prop("hips")
        hips = self.obj.data.bones[hips_name]
        self._traverse_tpose(hips, None, None, indent="")

    def _traverse_current_pose(
        self, b: bpy.types.PoseBone, parent: Optional[bpy.types.PoseBone]
    ):
        human_bone = self.tree.vrm_from_name(b.name)
        assert human_bone

        m = b.matrix
        if parent:
            m = parent.matrix.inverted() @ m
        else:
            pass
        t, r, s = m.decompose()

        vrm_pose = self.gltf["extensions"][VRM_ANIMATION]["extras"][VRM_POSE][
            "humanoid"
        ]
        vrm_pose["rotations"][human_bone] = [r.x, r.y, r.z, r.w]
        if human_bone == "hips":
            vrm_pose["translation"] = [
                t.x * self.to_meter,
                t.y * self.to_meter,
                t.z * self.to_meter,
            ]

        for child_name in self.tree.child_bone_names_from_name(b.name):
            child = self.obj.pose.bones[child_name]
            self._traverse_current_pose(child, b)

    def get_current_pose(self):
        with enter_pose(self.obj):
            hips_name = self.tree.bonename_from_prop("hips")
            hips = self.obj.pose.bones[hips_name]
            self._traverse_current_pose(hips, None)

    def to_json(self) -> str:
        return json.dumps(self.gltf, indent=2)


class CopyHumanoidPose(bpy.types.Operator):
    bl_idname = "humanoid.copy_pose"
    bl_label = "Copy Pose To Clipboard"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.active_object:
            return isinstance(context.active_object.data, bpy.types.Armature)
        return False

    def execute(self, context: bpy.types.Context):
        o = bpy.context.active_object  # type: ignore
        builder = Builder(o, 1)

        builder.get_tpose()
        builder.get_current_pose()

        # to clip board
        text = builder.to_json()
        # print(text)
        self.report({"INFO"}, "copy pose to clipboard")
        context.window_manager.clipboard = text
        return {"FINISHED"}
