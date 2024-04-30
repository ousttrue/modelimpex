import bpy
from .copy_humanoid_pose import CopyHumanoidPose
from .guess_human_bones import GuessHumanBones
from .add_humanoid_rig import AddHumanoidRig


class SelectPoseBone(bpy.types.Operator):
    bl_idname = "humanoid.select_posebone"
    bl_label = "select_pose_bone"
    bl_options = {"REGISTER", "UNDO"}

    bone: bpy.props.StringProperty(name="bone_name")

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return isinstance(context.active_object.data, bpy.types.Armature)

    def execute(self, context):
        bone = context.active_object.pose.bones[self.bone].bone
        context.active_object.data.bones.active.select = False
        bone.select = True
        context.active_object.data.bones.active = bone
        self.report({"INFO"}, f"select: {self.bone}")
        return {"FINISHED"}


class ArmatureHumanoidPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_humanoid"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Humanoid"
    bl_label = "Humanoid"

    @classmethod
    def poll(cls, context):
        if context.active_object:
            return isinstance(context.active_object.data, bpy.types.Armature)

    def draw_bone(self, armature: bpy.types.Armature, bone: str):
        self.layout.prop_search(armature.humanoid, bone, armature, "bones")

    def draw_bone_lr(self, armature: bpy.types.Armature, bone: str):
        split = self.layout.split(factor=0.24)
        split.label(text=f"{bone}:")
        split.column().prop_search(
            armature.humanoid, f"left_{bone}", armature, "bones", text=""
        )
        split.column().prop_search(
            armature.humanoid, f"right_{bone}", armature, "bones", text=""
        )

    def draw(self, context):
        armature = context.active_object.data
        self.draw_bone(armature, "hips")
        self.draw_bone(armature, "spine")
        self.draw_bone(armature, "chest")
        self.draw_bone(armature, "neck")
        self.draw_bone(armature, "head")
        self.draw_bone_lr(armature, "shoulder")
        self.draw_bone_lr(armature, "upper_arm")
        self.draw_bone_lr(armature, "lower_arm")
        self.draw_bone_lr(armature, "hand")
        self.draw_bone_lr(armature, "upper_leg")
        self.draw_bone_lr(armature, "lower_leg")
        self.draw_bone_lr(armature, "foot")
        self.draw_bone_lr(armature, "toes")

        # guess
        btn = self.layout.operator(GuessHumanBones.bl_idname)
        btn.clear = False
        # clear
        btn = self.layout.operator(GuessHumanBones.bl_idname, text="clear")
        btn.clear = True
        # add rig
        self.layout.operator(AddHumanoidRig.bl_idname)
        # copy pose
        self.layout.operator(CopyHumanoidPose.bl_idname)

        self.draw_bone_lr(armature, "thumb_metacarpal")
        self.draw_bone_lr(armature, "thumb_proximal")
        self.draw_bone_lr(armature, "thumb_distal")
        self.draw_bone_lr(armature, "index_proximal")
        self.draw_bone_lr(armature, "index_intermediate")
        self.draw_bone_lr(armature, "index_distal")
        self.draw_bone_lr(armature, "middle_proximal")
        self.draw_bone_lr(armature, "middle_intermediate")
        self.draw_bone_lr(armature, "middle_distal")
        self.draw_bone_lr(armature, "ring_proximal")
        self.draw_bone_lr(armature, "ring_intermediate")
        self.draw_bone_lr(armature, "ring_distal")
        self.draw_bone_lr(armature, "little_proximal")
        self.draw_bone_lr(armature, "little_intermediate")
        self.draw_bone_lr(armature, "little_distal")

        # constraint debug
        if context.mode == "POSE":
            self.layout.label(text=f"for debug. search constraint ref:")
            if context.active_pose_bone:
                # armature = context.active_object.data
                current = context.active_pose_bone.name
                self.layout.label(text=f"active bone: {current}")
                self.layout.label(text="referenced from ...")
                for b in context.active_object.pose.bones:
                    for c in b.constraints:
                        for k in dir(c):
                            t = getattr(c, k)
                            if t == current:
                                # self.layout.label(text=f"{b.name}.{k} => {t}")
                                btn = self.layout.operator(
                                    SelectPoseBone.bl_idname,
                                    text=f"{b.name}.{c.name}.{k} =>",
                                )
                                btn.bone = b.name
