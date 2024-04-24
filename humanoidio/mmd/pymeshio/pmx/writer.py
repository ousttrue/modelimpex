# coding: utf-8
"""
pmx writer
"""
from typing import Callable
import io
from .. import common
from . import model


class Writer(common.BinaryWriter):
    """pmx writer"""

    def __init__(
        self,
        ios: io.IOBase,
        text_encoding: int,
        extended_uv: int,
        vertex_index_size: int,
        texture_index_size: int,
        material_index_size: int,
        bone_index_size: int,
        morph_index_size: int,
        rigidbody_index_size: int,
    ):
        super(Writer, self).__init__(ios)
        if text_encoding == 0:

            def write_text_utf16(unicode: str):
                if not unicode:
                    self.write_int(0, 4)
                else:
                    utf16 = unicode.encode("utf-16-le")
                    self.write_int(len(utf16), 4)
                    self.write_bytes(utf16)

            self.write_text = write_text_utf16
        elif text_encoding == 1:

            def write_text_utf8(unicode: str):
                utf8 = unicode.encode("utf8")
                self.write_int(len(utf8), 4)
                self.write_bytes(utf8)

            self.write_text = write_text_utf8
        else:
            raise common.WriteException(
                "invalid text_encoding: {0}".format(text_encoding)
            )

        self.write_vertex_index: Callable[[int], None] = lambda index: self.write_int(
            index, vertex_index_size
        )
        self.write_texture_index: Callable[[int], None] = lambda index: self.write_int(
            index, texture_index_size
        )
        self.write_material_index: Callable[[int], None] = lambda index: self.write_int(
            index, material_index_size
        )
        self.write_bone_index: Callable[[int], None] = lambda index: self.write_int(
            index, bone_index_size
        )
        self.write_morph_index: Callable[[int], None] = lambda index: self.write_int(
            index, morph_index_size
        )
        self.write_rigidbody_index: Callable[[int], None] = (
            lambda index: self.write_int(index, rigidbody_index_size)
        )

    def write_vertices(self, vertices: list[model.Vertex]) -> None:
        self.write_int(len(vertices), 4)
        for v in vertices:
            self.write_vector3(v.position)
            self.write_vector3(v.normal)
            self.write_vector2(v.uv)
            self.write_deform(v.deform)
            self.write_float(v.edge_factor)

    def write_deform(
        self, deform: model.Bdef1 | model.Bdef2 | model.Bdef4 | model.Sdef
    ) -> None:
        if isinstance(deform, model.Bdef1):
            self.write_int(0, 1)
            self.write_bone_index(deform.index0)
        elif isinstance(deform, model.Bdef2):
            self.write_int(1, 1)
            self.write_bone_index(deform.index0)
            self.write_bone_index(deform.index1)
            self.write_float(deform.weight0)
        elif isinstance(deform, model.Bdef4):
            self.write_int(2, 1)
            self.write_bone_index(deform.index0)
            self.write_bone_index(deform.index1)
            self.write_bone_index(deform.index2)
            self.write_bone_index(deform.index3)
            self.write_float(deform.weight0)
            self.write_float(deform.weight1)
            self.write_float(deform.weight2)
            self.write_float(deform.weight3)
        else:
            raise common.WriteException(f"unknown deform type: {deform}")

    def write_indices(self, indices: list[int]) -> None:
        self.write_int(len(indices), 4)
        for i in indices:
            self.write_vertex_index(i)

    def write_textures(self, textures: list[str]) -> None:
        self.write_int(len(textures), 4)
        for t in textures:
            self.write_text(t)

    def write_materials(self, materials: list[model.Material]) -> None:
        self.write_int(len(materials), 4)
        for m in materials:
            self.write_text(m.name)
            self.write_text(m.english_name)
            self.write_rgb(m.diffuse_color)
            self.write_float(m.alpha)
            self.write_rgb(m.specular_color)
            self.write_float(m.specular_factor)
            self.write_rgb(m.ambient_color)
            self.write_int(m.flag, 1)
            self.write_rgba(m.edge_color)
            self.write_float(m.edge_size)
            self.write_texture_index(m.texture_index)
            self.write_texture_index(m.sphere_texture_index)
            self.write_int(m.sphere_mode, 1)
            self.write_int(m.toon_sharing_flag, 1)
            if m.toon_sharing_flag == 0:
                self.write_texture_index(m.toon_texture_index)
            elif m.toon_sharing_flag == 1:
                self.write_int(m.toon_texture_index, 1)
            else:
                raise common.WriteException(
                    "unknown toon_sharing_flag {0}".format(m.toon_sharing_flag)
                )
            self.write_text(m.comment)
            self.write_int(m.vertex_count, 4)

    def write_bones(self, bones: list[model.Bone]) -> None:
        self.write_int(len(bones), 4)
        for bone in bones:
            self.write_text(bone.name)
            self.write_text(bone.english_name)
            self.write_vector3(bone.position)
            self.write_bone_index(bone.parent_index)
            self.write_int(bone.layer, 4)
            self.write_int(bone.flag, 2)
            if not bone.getConnectionFlag():
                self.write_vector3(bone.tail_position)
            elif bone.getConnectionFlag():
                self.write_bone_index(bone.tail_index)
            else:
                raise common.WriteException(
                    "unknown bone conenction flag: {0}".format(bone.getConnectionFlag())
                )

            if bone.getExternalRotationFlag() or bone.getExternalTranslationFlag():
                self.write_bone_index(bone.effect_index)
                self.write_float(bone.effect_factor)

            if bone.getFixedAxisFlag():
                self.write_vector3(bone.fixed_axis)

            if bone.getLocalCoordinateFlag():
                self.write_vector3(bone.local_x_vector)
                self.write_vector3(bone.local_z_vector)

            if bone.getExternalParentDeformFlag():
                self.write_int(bone.external_key, 4)

            if bone.getIkFlag():
                assert bone.ik
                self.write_ik(bone.ik)

    def write_ik(self, ik: model.Ik) -> None:
        self.write_bone_index(ik.target_index)
        self.write_int(ik.loop, 4)
        self.write_float(ik.limit_radian)
        self.write_int(len(ik.link), 4)
        for l in ik.link:
            self.write_ik_link(l)

    def write_ik_link(self, link: model.IkLink) -> None:
        self.write_bone_index(link.bone_index)
        self.write_int(link.limit_angle, 1)
        if link.limit_angle == 0:
            pass
        elif link.limit_angle == 1:
            self.write_vector3(link.limit_min)
            self.write_vector3(link.limit_max)
        else:
            raise common.WriteException(
                "invalid ik link limit_angle: {0}".format(link.limit_angle)
            )

    def write_morph(self, morphs: list[model.Morph]) -> None:
        self.write_int(len(morphs), 4)
        for m in morphs:
            self.write_text(m.name)
            self.write_text(m.english_name)
            self.write_int(m.panel, 1)
            self.write_int(m.morph_type, 1)

            match (m):
                case model.GroupMorph():
                    assert m.morph_type == 0
                    # todo
                    raise common.WriteException("not implemented GroupMorph")
                case model.VertexMorph():
                    assert m.morph_type == 1
                    self.write_int(len(m.offsets), 4)
                    for o in m.offsets:
                        self.write_vertex_index(o.vertex_index)
                        self.write_vector3(o.position_offset)
                case model.BoneMorph():
                    assert m.morph_type == 2
                    # todo
                    raise common.WriteException("not implemented BoneMorph")
                case model.UVMorph():
                    assert (
                        m.morph_type == 3
                        or m.morph_type == 4
                        or m.morph_type == 5
                        or m.morph_type == 6
                        or m.morph_type == 7
                        or m.morph_type == 8
                    )
                    # todo
                    raise common.WriteException("not implemented UvMorph")
                case _:
                    raise common.WriteException(
                        "unknown morph type: {0}".format(m.morph_type)
                    )

    def write_display_slots(self, display_slots: list[model.DisplaySlot]) -> None:
        self.write_int(len(display_slots), 4)
        for s in display_slots:
            self.write_text(s.name)
            self.write_text(s.english_name)
            self.write_int(s.special_flag, 1)
            self.write_int(len(s.references), 4)
            for r in s.references:
                self.write_int(r[0], 1)
                if r[0] == 0:
                    self.write_bone_index(r[1])
                elif r[0] == 1:
                    self.write_morph_index(r[1])
                else:
                    raise common.WriteException(
                        "unknown display_type: {0}".format(r[0])
                    )

    def write_rigidbodies(self, rigidbodies: list[model.RigidBody]) -> None:
        self.write_int(len(rigidbodies), 4)
        for rb in rigidbodies:
            self.write_text(rb.name)
            self.write_text(rb.english_name)
            self.write_bone_index(rb.bone_index)
            self.write_int(rb.collision_group, 1)
            self.write_int(rb.no_collision_group, 2)
            self.write_int(rb.shape_type, 1)
            self.write_vector3(rb.shape_size)
            self.write_vector3(rb.shape_position)
            self.write_vector3(rb.shape_rotation)
            self.write_float(rb.param.mass)
            self.write_float(rb.param.linear_damping)
            self.write_float(rb.param.angular_damping)
            self.write_float(rb.param.restitution)
            self.write_float(rb.param.friction)
            self.write_int(rb.mode, 1)

    def write_joints(self, joints: list[model.Joint]) -> None:
        self.write_int(len(joints), 4)
        for j in joints:
            self.write_text(j.name)
            self.write_text(j.english_name)
            self.write_int(j.joint_type, 1)
            self.write_rigidbody_index(j.rigidbody_index_a)
            self.write_rigidbody_index(j.rigidbody_index_b)
            self.write_vector3(j.position)
            self.write_vector3(j.rotation)
            self.write_vector3(j.translation_limit_min)
            self.write_vector3(j.translation_limit_max)
            self.write_vector3(j.rotation_limit_min)
            self.write_vector3(j.rotation_limit_max)
            self.write_vector3(j.spring_constant_translation)
            self.write_vector3(j.spring_constant_rotation)


def write(ios: io.IOBase, pmx: model.Model, text_encoding: int = 0) -> None:
    """
    write model to ios.

    :Parameters:
        ios
            output stream (in io.IOBase)
        model
            pmx model
        text_encoding
            text field encoding (0: UTF16, 1:UTF-8).

    >>> import pymeshio.pmx.writer
    >>> pymeshio.pmx.writer.write(io.open('out.pmx', 'wb'), pmx_model)

    """
    assert isinstance(ios, io.IOBase)
    assert isinstance(model, model.Model)
    writer = common.BinaryWriter(ios)
    # header
    writer.write_bytes(b"PMX ")
    writer.write_float(model.version)

    # flags
    writer.write_int(8, 1)
    # textencoding
    writer.write_int(text_encoding, 1)
    # extend uv
    writer.write_int(0, 1)

    def get_array_size(size: int):
        if size < 128:
            return 1
        elif size < 32768:
            return 2
        elif size < 2147483647:
            return 4
        else:
            raise common.WriteException("invalid array_size: {0}".format(size))

    # vertex_index_size
    vertex_index_size = get_array_size(len(model.vertices))
    writer.write_int(vertex_index_size, 1)
    # texture_index_size
    texture_index_size = get_array_size(len(model.textures))
    writer.write_int(texture_index_size, 1)
    # material_index_size
    material_index_size = get_array_size(len(model.materials))
    writer.write_int(material_index_size, 1)
    # bone_index_size
    bone_index_size = get_array_size(len(model.bones))
    writer.write_int(bone_index_size, 1)
    # morph_index_size
    morph_index_size = get_array_size(len(model.morphs))
    writer.write_int(morph_index_size, 1)
    # rigidbody_index_size
    rigidbody_index_size = get_array_size(len(model.rigidbodies))
    writer.write_int(rigidbody_index_size, 1)

    writer = Writer(
        writer.ios,
        text_encoding,
        0,
        vertex_index_size,
        texture_index_size,
        material_index_size,
        bone_index_size,
        morph_index_size,
        rigidbody_index_size,
    )

    # model info
    writer.write_text(model.name)
    writer.write_text(model.english_name)
    writer.write_text(model.comment)
    writer.write_text(model.english_comment)

    # model data
    writer.write_vertices(model.vertices)
    writer.write_indices(model.indices)
    writer.write_textures(model.textures)
    writer.write_materials(model.materials)
    writer.write_bones(model.bones)
    writer.write_morph(model.morphs)
    writer.write_display_slots(model.display_slots)
    writer.write_rigidbodies(model.rigidbodies)
    writer.write_joints(model.joints)


def write_to_file(pmx_model: model.Model, path: str):
    with io.open(path, "wb") as f:
        return write(f, pmx_model)
