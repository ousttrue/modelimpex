'''
custom RNA property definitions
'''

import bpy
from bpy import types

from pyimpex import CLASSES
from .. import formats

presets = (
    ('unknown', 'unknown', ''),
    ('neutral', 'neutral', ''),
    ('a', 'a', ''),
    ('i', 'i', ''),
    ('u', 'u', ''),
    ('e', 'e', ''),
    ('o', 'o', ''),
    ('blink', 'blink', ''),
    ('joy', 'joy', ''),
    ('angry', 'angry', ''),
    ('sorrow', 'sorrow', ''),
    ('fun', 'fun', ''),
    ('lookup', 'lookup', ''),
    ('lookdown', 'lookdown', ''),
    ('lookleft', 'lookleft', ''),
    ('lookright', 'lookright', ''),
    ('blink_l', 'blink_l', ''),
    ('blink_r', 'blink_r', ''),
)


class PYIMPEX_Expression(bpy.types.PropertyGroup):
    preset: bpy.props.EnumProperty(name="Expression preset",
                                   description="VRM Expression preset",
                                   items=presets)
    name: bpy.props.StringProperty(name="Preset", default="Unknown")
    weight: bpy.props.FloatProperty(name="Weight", default=0, min=0, max=1)


class PYIMPEX_UL_ExpressionTemplate(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "preset", text="", emboss=False, icon_value=icon)
            layout.prop(item, "name", text="", emboss=False)
            layout.prop(item, "weight", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)


class PYIMPEX_ExpressionPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_pyimex_expression"
    bl_label = "VRM Expressions"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        if not isinstance(context.object.data, bpy.types.Armature):
            return False

        return True

    def draw_header(self, context):
        layout: bpy.types.UILayout = self.layout
        layout.label(text="pyimpex Expressions")

    def draw(self, context):
        layout = self.layout
        obj = context.object

        row = layout.row()
        row.template_list(
            "PYIMPEX_UL_ExpressionTemplate",
            "Expresssions",
            # list
            obj,
            "pyimpex_expressions",
            # index
            obj,
            "pyimpex_expressions_active")

        row = layout.row()


class PYIMPEX_HumanoidBonePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_pyimex_humanoidbone"
    bl_label = "VRM HumanoidBone"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        if not isinstance(context.object.data, bpy.types.Armature):
            return False

        return True

    def draw_header(self, context):
        layout: bpy.types.UILayout = self.layout
        layout.label(text="pyimpex Humanoid")

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        row = layout.row()
        if context.active_pose_bone:
            row.prop(context.active_pose_bone, 'pyimpex_humanoid_bone', text = 'humanoid bone')

        row = layout.row()


CLASSES = [
    PYIMPEX_Expression, PYIMPEX_UL_ExpressionTemplate, PYIMPEX_ExpressionPanel,
    PYIMPEX_HumanoidBonePanel
]


def register():
    for c in CLASSES:
        bpy.utils.register_class(c)

    bpy.types.Object.pyimpex_expressions = bpy.props.CollectionProperty(  # type: ignore
        type=PYIMPEX_Expression)
    bpy.types.Object.pyimpex_expressions_active = bpy.props.IntProperty(  # type: ignore
    )

    items = (
        (bone.name, bone.name, bone.name)  # (識別子, UI表示名, 説明文)
        for bone in formats.HumanoidBones)

    bpy.types.PoseBone.pyimpex_humanoid_bone = bpy.props.EnumProperty(
        items=items)


def unregister():
    for c in CLASSES:
        bpy.utils.unregister_class(c)
