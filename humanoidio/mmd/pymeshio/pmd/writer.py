# coding: utf-8
"""
pmd writer
"""
import io
import struct
from .. import common
from . import model


class Writer(common.BinaryWriter):
    def write_veritices(self, vertices: list[model.Vertex]) -> None:
        self.write_uint(len(vertices), 4)
        for v in vertices:
            self.write_vector3(v.pos)
            self.write_vector3(v.normal)
            self.write_vector2(v.uv)
            self.write_uint(v.bone0, 2)
            self.write_uint(v.bone1, 2)
            self.write_uint(v.weight0, 1)
            self.write_uint(v.edge_flag, 1)

    def write_indices(self, indices: list[int]) -> None:
        self.write_uint(len(indices), 4)
        self.ios.write(struct.pack("=%dH" % len(indices), *indices))

    def write_materials(self, materials: list[model.Material]) -> None:
        self.write_uint(len(materials), 4)
        for m in materials:
            self.write_rgb(m.diffuse_color)
            self.write_float(m.alpha)
            self.write_float(m.specular_factor)
            self.write_rgb(m.specular_color)
            self.write_rgb(m.ambient_color)
            self.write_uint(m.toon_index, 1)
            self.write_uint(m.edge_flag, 1)
            self.write_uint(m.vertex_count, 4)
            self.write_bytes(m.texture_file.encode("cp932"), 20)

    def write_bones(self, bones: list[model.Bone]) -> None:
        self.write_uint(len(bones), 2)
        sBone = struct.Struct("=20sHHBH3f")
        assert sBone.size == 39
        for b in bones:
            self.write_bytes(b.name.encode("cp932"), 20)
            self.write_uint(b.parent_index, 2)
            self.write_uint(b.tail_index, 2)
            self.write_uint(b.type, 1)
            self.write_uint(b.ik_index, 2)
            self.write_vector3(b.pos)

    def write_ik_list(self, ik_list: list[model.IK]) -> None:
        self.write_uint(len(ik_list), 2)
        for ik in ik_list:
            self.write_uint(ik.index, 2)
            self.write_uint(ik.target, 2)
            self.write_uint(len(ik.children), 1)
            self.write_uint(ik.iterations, 2)
            self.write_float(ik.weight)
            self.ios.write(struct.pack("=%dH" % len(ik.children), *ik.children))

    def write_morphs(self, morphs: list[model.Morph]) -> None:
        self.write_uint(len(morphs), 2)
        for morph in morphs:
            self.write_bytes(morph.name.encode("cp932"), 20)
            self.write_uint(len(morph.indices), 4)
            self.write_uint(morph.type, 1)
            for i, v in zip(morph.indices, morph.pos_list):
                self.write_uint(i, 4)
                self.write_vector3(v)

    def write_morph_indices(self, morph_indices: list[int]) -> None:
        self.write_uint(len(morph_indices), 1)
        self.ios.write(struct.pack("=%dH" % len(morph_indices), *morph_indices))

    def write_bone_group_list(self, bone_group_list: list[model.BoneGroup]) -> None:
        self.write_uint(len(bone_group_list), 1)
        for g in bone_group_list:
            self.write_bytes(g.name.encode("cp932"), 50)

    def write_bone_display_list(self, bone_display_list: list[tuple[int, int]]) -> None:
        self.write_uint(len(bone_display_list), 4)
        for l in bone_display_list:
            self.write_uint(l[0], 2)
            self.write_uint(l[1], 1)

    def write_rigidbodies(self, rigidbodies: list[model.RigidBody]) -> None:
        self.write_uint(len(rigidbodies), 4)
        for r in rigidbodies:
            self.write_bytes(r.name.encode("cp932"), 20)
            self.write_int(r.bone_index, 2)
            self.write_uint(r.collision_group, 1)
            self.write_int(r.no_collision_group, 2)
            self.write_uint(r.shape_type, 1)
            self.write_vector3(r.shape_size)
            self.write_vector3(r.shape_position)
            self.write_vector3(r.shape_rotation)
            self.write_float(r.mass)
            self.write_float(r.linear_damping)
            self.write_float(r.angular_damping)
            self.write_float(r.restitution)
            self.write_float(r.friction)
            self.write_uint(r.mode, 1)

    def write_joints(self, joints: list[model.Joint]) -> None:
        self.write_uint(len(joints), 4)
        for j in joints:
            self.write_bytes(j.name.encode("cp932"), 20)
            self.write_uint(j.rigidbody_index_a, 4)
            self.write_uint(j.rigidbody_index_b, 4)
            self.write_vector3(j.position)
            self.write_vector3(j.rotation)
            self.write_vector3(j.translation_limit_min)
            self.write_vector3(j.translation_limit_max)
            self.write_vector3(j.rotation_limit_min)
            self.write_vector3(j.rotation_limit_max)
            self.write_vector3(j.spring_constant_translation)
            self.write_vector3(j.spring_constant_rotation)


def write(ios: io.IOBase, src: model.Model) -> None:
    """
    write model to ios.

    :Parameters:
        ios
            output stream (in io.IOBase)
        model
            pmd model

    >>> import pymeshio.pmd.writer
    >>> pymeshio.pmd.writer.write(io.open('out.pmd', 'wb'), pmd_model)

    """
    assert isinstance(ios, io.IOBase)
    assert isinstance(src, model.Model)
    writer = Writer(ios)
    writer.write_bytes(b"Pmd")
    writer.write_float(src.version)
    writer.write_bytes(src.name.encode("cp932"), 20)
    writer.write_bytes(src.comment.encode("cp932"), 256)
    writer.write_veritices(src.vertices)
    writer.write_indices(src.indices)
    writer.write_materials(src.materials)
    writer.write_bones(src.bones)
    writer.write_ik_list(src.ik_list)
    writer.write_morphs(src.morphs)
    writer.write_morph_indices(src.morph_indices)
    writer.write_bone_group_list(src.bone_group_list)
    writer.write_bone_display_list(src.bone_display_list)
    # extend data
    writer.write_uint(1, 1)
    writer.write_bytes(src.english_name.encode("cp932"), 20)
    writer.write_bytes(src.english_comment.encode("cp932"), 256)
    for bone in src.bones:
        writer.write_bytes(bone.english_name.encode("cp932"), 20)
    for skin in src.morphs:
        if skin.name == "base":
            continue
        writer.write_bytes(skin.english_name.encode("cp932"), 20)
    for g in src.bone_group_list:
        writer.write_bytes(g.english_name.encode("cp932"), 50)
    for toon_texture in src.toon_textures:
        writer.write_bytes(toon_texture.encode("cp932"), 100)
    writer.write_rigidbodies(src.rigidbodies)
    writer.write_joints(src.joints)
