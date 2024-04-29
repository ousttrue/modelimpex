# coding: utf-8
"""
========================
MikuMikuDance PMD format
========================

file format
~~~~~~~~~~~
* http://blog.goo.ne.jp/torisu_tetosuki/e/209ad341d3ece2b1b4df24abf619d6e4 

specs
~~~~~
* textencoding: bytes(cp932)
* coordinate: left handed y-up(DirectX)
* uv origin: 
* face: only triangle
* backculling: 

"""
from typing import Self, Iterable
import pathlib
from .. import common


class Vertex(common.Diff):
    """
    ==========
    pmd vertex
    ==========
    two bone weighted vertex with normal and uv.

    format
    ~~~~~~
    * http://blog.goo.ne.jp/torisu_tetosuki/e/5a1b16e2f61067838dfc66d010389707

    :IVariables:
        pos
            Vector3
        normal
            Vector3
        uv
            Vector2
        bone0
            bone index
        bone1
            bone index
        weight0
            bone0 influence.  min: 0, max: 100
        edge_flag
            int flag.  0: edge on, 1: edge off
    """

    __slots__ = ["pos", "normal", "uv", "bone0", "bone1", "weight0", "edge_flag"]

    def __init__(
        self,
        pos: common.Vector3,
        normal: common.Vector3,
        uv: common.Vector2,
        bone0: int,
        bone1: int,
        weight0: int,
        edge_flag: int,
    ):
        self.pos = pos
        self.normal = normal
        self.uv = uv
        self.bone0 = bone0
        self.bone1 = bone1
        self.weight0 = weight0
        self.edge_flag = edge_flag

    def __str__(self) -> str:
        return "<%s %s %s, (%d, %d, %d)>" % (
            str(self.pos),
            str(self.normal),
            str(self.uv),
            self.bone0,
            self.bone1,
            self.weight0,
        )

    def __eq__(self, rhs: object) -> bool:
        match rhs:
            case Vertex():
                return (
                    self.pos == rhs.pos
                    and self.normal == rhs.normal
                    and self.uv == rhs.uv
                    and self.bone0 == rhs.bone0
                    and self.bone1 == rhs.bone1
                    and self.weight0 == rhs.weight0
                    and self.edge_flag == rhs.edge_flag
                )
            case _:
                return False

    def __getitem__(self, key: int) -> float:
        if key == 0:
            return self.pos.x
        elif key == 1:
            return self.pos.y
        elif key == 2:
            return self.pos.z
        else:
            assert False


class Material(common.Diff):
    """
    ============
    pmd material
    ============

    format
    ~~~~~~
    * http://blog.goo.ne.jp/torisu_tetosuki/e/ea0bb1b1d4c6ad98a93edbfe359dac32

    :IVariables:
        diffuse_color
            RGB
        alpha
            float
        specular_factor
            float
        specular_color
            RGB
        ambient_color
            RGB
        toon_index
            int
        edge_flag
            int
        vertex_count
            indices length
        texture_file
            texture file path
    """

    __slots__ = [
        "diffuse_color",
        "alpha",
        "specular_factor",
        "specular_color",
        "ambient_color",
        "toon_index",
        "edge_flag",
        "vertex_count",
        "texture_file",
    ]

    def __init__(
        self,
        diffuse_color: common.RGB,
        alpha: float,
        specular_factor: float,
        specular_color: common.RGB,
        ambient_color: common.RGB,
        toon_index: int,
        edge_flag: int,
        vertex_count: int,
        texture_file: str,
    ):
        self.diffuse_color = diffuse_color
        self.alpha = alpha
        self.specular_factor = specular_factor
        self.specular_color = specular_color
        self.ambient_color = ambient_color
        self.toon_index = toon_index
        self.edge_flag = edge_flag
        self.vertex_count = vertex_count
        self.texture_file = texture_file

    def __str__(self) -> str:
        return "<Material [%s, %f] [%s %f] [%s] %d %d '%s' %d>" % (
            str(self.diffuse_color),
            self.alpha,
            str(self.specular_color),
            self.specular_factor,
            str(self.ambient_color),
            self.toon_index,
            self.edge_flag,
            self.texture_file,
            self.vertex_count,
        )

    def __eq__(self, rhs: object) -> bool:
        match rhs:
            case Material():
                return (
                    self.diffuse_color == rhs.diffuse_color
                    and self.alpha == rhs.alpha
                    and self.specular_factor == rhs.specular_factor
                    and self.specular_color == rhs.specular_color
                    and self.ambient_color == rhs.ambient_color
                    and self.toon_index == rhs.toon_index
                    and self.edge_flag == rhs.edge_flag
                    and self.vertex_count == rhs.vertex_count
                    and self.texture_file == rhs.texture_file
                )
            case _:
                return False

    def diff(self, rhs: Self):
        self._diff(rhs, "diffuse_color")
        self._diff(rhs, "alpha")
        self._diff(rhs, "specular_color")
        self._diff(rhs, "specular_factor")
        self._diff(rhs, "ambient_color")
        self._diff(rhs, "edge_flag")
        # todo
        # self._diff(rhs, "toon_index")
        self._diff(rhs, "texture_file")
        self._diff(rhs, "vertex_count")


class Bone(common.Diff):
    """
    ==========
    pmd bone
    ==========

    format
    ~~~~~~
    * http://blog.goo.ne.jp/torisu_tetosuki/e/638463f52d0ad6ca1c46fd315a9b17d0

    :IVariables:
        name
            bone name
        english_name
            bone english_name
        index
            boen index(append for internal use)
        type
            bone type
        ik
            ik(append for internal use)
        pos
            bone head position
        ik_index
            ik target bone index
        parent_index
            parent bone index
        tail_index
            tail bone index
        parent
            parent bone(append for internal use)
        tail
            tail bone(append for internal use)
        children
            children bone(append for internal use)
    """

    # kinds
    ROTATE = 0
    ROTATE_MOVE = 1
    IK = 2
    IK_ROTATE_INFL = 4
    ROTATE_INFL = 5
    IK_TARGET = 6
    # typo
    UNVISIBLE = 7
    INVISIBLE = 7
    # since v4.0
    ROLLING = 8  # ?
    TWEAK = 9
    __slots__ = [
        "name",
        "index",
        "type",
        "parent",
        "ik",
        "pos",
        "children",
        "english_name",
        "ik_index",
        "parent_index",
        "tail_index",
        "tail",
    ]

    def __init__(self, name: str = "bone", type: int = 0):
        self.name = name
        self.index = 0
        self.type = type
        self.parent_index = 0xFFFF
        self.tail_index = 0
        self.tail = common.Vector3(0, 0, 0)
        self.parent: Bone | None = None
        self.ik_index = 0xFFFF
        self.pos = common.Vector3(0, 0, 0)
        self.children: list[Bone] = []
        self.english_name = ""

    def __str__(self) -> str:
        return "<Bone:%s %d %d>" % (self.name, self.type, self.ik_index)

    def __eq__(self, rhs: object) -> bool:
        match rhs:
            case Bone():
                return (
                    self.name == rhs.name
                    and self.index == rhs.index
                    and self.type == rhs.type
                    and self.parent_index == rhs.parent_index
                    and self.tail_index == rhs.tail_index
                    and self.tail == rhs.tail
                    and self.ik_index == rhs.ik_index
                    and self.pos == rhs.pos
                    and self.children == rhs.children
                    and self.english_name == rhs.english_name
                )
            case _:
                return False

    def diff(self, rhs: Self) -> None:
        self._diff(rhs, "name")
        if self.english_name.endswith("_t") or rhs.english_name.endswith("_t"):
            pass
        elif self.english_name.startswith("arm twist") or rhs.english_name.startswith(
            "arm twist"
        ):
            pass
        else:
            self._diff(rhs, "english_name")
        self._diff(rhs, "index")
        self._diff(rhs, "type")
        self._diff(rhs, "parent_index")
        self._diff(rhs, "tail_index")
        self._diff(rhs, "ik_index")
        self._diff(rhs, "pos")

    def hasParent(self) -> bool:
        return self.parent_index != 0xFFFF

    def hasChild(self) -> bool:
        return self.tail_index != 0 and self.tail_index != 0xFFFF

    def display(self, indent: list[bool] | None = None) -> None:
        indent = indent or []
        if len(indent) > 0:
            prefix = ""
            for i, is_end in enumerate(indent):
                if i == len(indent) - 1:
                    break
                else:
                    prefix += "  " if is_end else " |"
            uni = "%s +%s(%s)" % (prefix, self, self.english_name)
            print(uni)
        else:
            uni = "%s(%s)" % (self, self.english_name)
            print(uni)

        child_count = len(self.children)
        for i in range(child_count):
            child = self.children[i]
            if i < child_count - 1:
                child.display(indent + [False])
            else:
                # last
                child.display(indent + [True])


# 0
class Bone_Rotate(Bone):
    __slots__ = []

    def __init__(self, name: str):
        super(Bone_Rotate, self).__init__(name, 0)

    def __str__(self):
        return "<ROTATE %s>" % (self.name)


# 1
class Bone_RotateMove(Bone):
    __slots__ = []

    def __init__(self, name: str):
        super(Bone_RotateMove, self).__init__(name, 1)

    def __str__(self):
        return "<ROTATE_MOVE %s>" % (self.name)


# 2
class Bone_IK(Bone):
    __slots__ = []

    def __init__(self, name: str):
        super(Bone_IK, self).__init__(name, 2)

    def __str__(self):
        return "<IK %s>" % (self.name)


# 4
class Bone_IKRotateInfl(Bone):
    __slots__ = []

    def __init__(self, name: str):
        super(Bone_IKRotateInfl, self).__init__(name, 4)

    def __str__(self):
        return "<IK_ROTATE_INFL %s>" % (self.name)


# 5
class Bone_RotateInfl(Bone):
    __slots__ = []

    def __init__(self, name: str):
        super(Bone_RotateInfl, self).__init__(name, 5)

    def __str__(self):
        return "<ROTATE_INFL %s>" % (self.name)


# 6
class Bone_IKTarget(Bone):
    __slots__ = []

    def __init__(self, name: str):
        super(Bone_IKTarget, self).__init__(name, 6)

    def __str__(self):
        return "<IK_TARGET %s>" % (self.name)


# 7
class Bone_Unvisible(Bone):
    __slots__ = []

    def __init__(self, name: str):
        super(Bone_Unvisible, self).__init__(name, 7)

    def __str__(self):
        return "<UNVISIBLE %s>" % (self.name)


# 8
class Bone_Rolling(Bone):
    __slots__ = []

    def __init__(self, name: str):
        super(Bone_Rolling, self).__init__(name, 8)

    def __str__(self):
        return "<ROLLING %s>" % (self.name)


# 9
class Bone_Tweak(Bone):
    __slots__ = []

    def __init__(self, name: str):
        super(Bone_Tweak, self).__init__(name, 9)

    def __str__(self):
        return "<TWEAK %s>" % (self.name)


def createBone(name: str, type: int) -> Bone:
    if type == 0:
        return Bone_Rotate(name)
    elif type == 1:
        return Bone_RotateMove(name)
    elif type == 2:
        return Bone_IK(name)
    elif type == 3:
        raise Exception("no used bone type: 3(%s)" % name)
    elif type == 4:
        return Bone_IKRotateInfl(name)
    elif type == 5:
        return Bone_RotateInfl(name)
    elif type == 6:
        return Bone_IKTarget(name)
    elif type == 7:
        return Bone_Unvisible(name)
    elif type == 8:
        return Bone_Rolling(name)
    elif type == 9:
        return Bone_Tweak(name)
    else:
        raise Exception("unknown bone type: %d(%s)" % (type, name))


class IK(common.Diff):
    __slots__ = ["index", "target", "iterations", "weight", "length", "children"]

    def __init__(self, index: int = 0, target: int = 0):
        self.index = index
        self.target = target
        self.iterations = 0
        self.weight = 0.0
        self.children: list[int] = []

    def __str__(self):
        return (
            "<IK index: %d, target: %d, iterations: %d, weight: %f, children: %s(%d)>"
            % (
                self.index,
                self.target,
                self.iterations,
                self.weight,
                "-".join([str(i) for i in self.children]),
                len(self.children),
            )
        )

    def __eq__(self, rhs: object) -> bool:
        match rhs:
            case IK():
                return (
                    self.index == rhs.index
                    and self.target == rhs.target
                    and self.iterations == rhs.iterations
                    and self.weight == rhs.weight
                    and self.children == rhs.children
                )
            case _:
                return False


class Morph(common.Diff):
    __slots__ = ["name", "type", "indices", "pos_list", "english_name", "vertex_count"]

    def __init__(self, name: str):
        self.name = name
        self.type = -1
        self.indices: list[int] = []
        self.pos_list: list[common.Vector3] = []
        self.english_name = ""
        self.vertex_count = 0

    def append(self, index: int, x: float, y: float, z: float) -> None:
        self.indices.append(index)
        self.pos_list.append(common.Vector3(x, y, z))

    def __str__(self) -> str:
        return '<Skin name: "%s", type: %d, vertex: %d>' % (
            self.name,
            self.type,
            len(self.indices),
        )

    def __eq__(self, rhs: object) -> bool:
        match rhs:
            case Morph():
                return (
                    self.name == rhs.name
                    and self.type == rhs.type
                    and self.indices == rhs.indices
                    and self.pos_list == rhs.pos_list
                    and self.english_name == rhs.english_name
                    and self.vertex_count == rhs.vertex_count
                )
            case _:
                return False

    def diff(self, rhs: Self) -> None:
        self._diff(rhs, "name")
        self._diff(rhs, "english_name")
        self._diff(rhs, "type")
        # self._diff_array(rhs, "indices")
        # self._diff_array(rhs, "pos_list")


class BoneGroup(common.Diff):
    __slots__ = ["name", "english_name"]

    def __init__(self, name: str = "group", english_name: str = "center"):
        self.name = name
        self.english_name = english_name

    def __eq__(self, rhs: object) -> bool:
        match rhs:
            case BoneGroup():
                return self.name == rhs.name and self.english_name == rhs.english_name
            case _:
                return False

    def diff(self, rhs: Self) -> None:
        self._diff(rhs, "name")
        self._diff(rhs, "english_name")


SHAPE_SPHERE = 0
SHAPE_BOX = 1
SHAPE_CAPSULE = 2

RIGIDBODY_KINEMATICS = 0
RIGIDBODY_PHYSICS = 1
RIGIDBODY_PHYSICS_WITH_BONE = 2


class RigidBody(common.Diff):
    __slots__ = [
        "name",
        "bone_index",
        "collision_group",
        "no_collision_group",
        "shape_type",
        "shape_size",
        "shape_position",
        "shape_rotation",
        "mass",
        "linear_damping",
        "angular_damping",
        "restitution",
        "friction",
        "mode",
    ]

    def __init__(
        self,
        name: str,
        bone_index: int,
        collision_group: int,
        no_collision_group: int,
        shape_type: int,
        shape_size: common.Vector3,
        shape_position: common.Vector3,
        shape_rotation: common.Vector3,
        mass: float,
        linear_damping: float,
        angular_damping: float,
        restitution: float,
        friction: float,
        mode: int,
    ):
        self.name = name
        self.bone_index = bone_index
        self.collision_group = collision_group
        self.no_collision_group = no_collision_group
        self.shape_type = shape_type
        self.shape_size = shape_size
        self.shape_position = shape_position
        self.shape_rotation = shape_rotation
        self.mass = mass
        self.linear_damping = linear_damping
        self.angular_damping = angular_damping
        self.restitution = restitution
        self.friction = friction
        self.mode = mode

    def __eq__(self, rhs: object) -> bool:
        match rhs:
            case RigidBody():
                return (
                    self.name == rhs.name
                    and self.bone_index == rhs.bone_index
                    and self.collision_group == rhs.collision_group
                    and self.no_collision_group == rhs.no_collision_group
                    and self.shape_type == rhs.shape_type
                    and self.shape_size == rhs.shape_size
                    and self.shape_position == rhs.shape_position
                    and self.shape_rotation == rhs.shape_rotation
                    and self.mass == rhs.mass
                    and self.linear_damping == rhs.linear_damping
                    and self.angular_damping == rhs.angular_damping
                    and self.restitution == rhs.restitution
                    and self.friction == rhs.friction
                    and self.mode == rhs.mode
                )
            case _:
                return False

    def diff(self, rhs: Self) -> None:
        self._diff(rhs, "name")
        self._diff(rhs, "bone_index")
        self._diff(rhs, "collision_group")
        self._diff(rhs, "no_collision_group")
        self._diff(rhs, "shape_type")
        if self.shape_type == SHAPE_SPHERE:
            pass
        elif self.shape_type == SHAPE_CAPSULE:
            pass
        elif self.shape_type == SHAPE_BOX:
            self._diff(rhs, "shape_size")
        self._diff(rhs, "shape_position")
        self._diff(rhs, "shape_rotation")
        self._diff(rhs, "mass")
        self._diff(rhs, "linear_damping")
        self._diff(rhs, "angular_damping")
        self._diff(rhs, "restitution")
        self._diff(rhs, "friction")
        self._diff(rhs, "mode")


class Joint(common.Diff):
    __slots__ = [
        "name",
        "rigidbody_index_a",
        "rigidbody_index_b",
        "position",
        "rotation",
        "translation_limit_max",
        "translation_limit_min",
        "rotation_limit_max",
        "rotation_limit_min",
        "spring_constant_translation",
        "spring_constant_rotation",
    ]

    def __init__(
        self,
        name: str,
        rigidbody_index_a: int,
        rigidbody_index_b: int,
        position: common.Vector3,
        rotation: common.Vector3,
        translation_limit_max: common.Vector3,
        translation_limit_min: common.Vector3,
        rotation_limit_max: common.Vector3,
        rotation_limit_min: common.Vector3,
        spring_constant_translation: common.Vector3,
        spring_constant_rotation: common.Vector3,
    ):
        self.name = name
        self.rigidbody_index_a = rigidbody_index_a
        self.rigidbody_index_b = rigidbody_index_b
        self.position = position
        self.rotation = rotation
        self.translation_limit_max = translation_limit_max
        self.translation_limit_min = translation_limit_min
        self.rotation_limit_max = rotation_limit_max
        self.rotation_limit_min = rotation_limit_min
        self.spring_constant_translation = spring_constant_translation
        self.spring_constant_rotation = spring_constant_rotation

    def __eq__(self, rhs: object) -> bool:
        match rhs:
            case Joint():
                return (
                    self.name == rhs.name
                    and self.rigidbody_index_a == rhs.rigidbody_index_a
                    and self.rigidbody_index_b == rhs.rigidbody_index_b
                    and self.position == rhs.position
                    and self.rotation == rhs.rotation
                    and self.translation_limit_max == rhs.translation_limit_max
                    and self.translation_limit_min == rhs.translation_limit_min
                    and self.rotation_limit_max == rhs.rotation_limit_max
                    and self.rotation_limit_min == rhs.rotation_limit_min
                    and self.spring_constant_translation
                    == rhs.spring_constant_translation
                    and self.spring_constant_rotation == rhs.spring_constant_rotation
                )
            case _:
                return False

    def diff(self, rhs: Self) -> None:
        self._diff(rhs, "name")
        self._diff(rhs, "rigidbody_index_a")
        self._diff(rhs, "rigidbody_index_b")
        self._diff(rhs, "position")
        self._diff(rhs, "rotation")
        self._diff(rhs, "translation_limit_min")
        self._diff(rhs, "translation_limit_max")
        self._diff(rhs, "rotation_limit_min")
        self._diff(rhs, "rotation_limit_max")
        self._diff(rhs, "spring_constant_translation")
        self._diff(rhs, "spring_constant_rotation")


class Pmd(common.Diff):
    """pmd loader class.

    Attributes:
        io: internal use.
        end: internal use.
        pos: internal user.

        version: pmd version number
        _name: internal
    """

    __slots__ = [
        "path",
        "version",
        "name",
        "comment",
        "english_name",
        "english_comment",
        "vertices",
        "indices",
        "materials",
        "bones",
        "ik_list",
        "morphs",
        "morph_indices",
        "bone_group_list",
        "bone_display_list",
        "toon_textures",
        "rigidbodies",
        "joints",
        "no_parent_bones",
    ]

    def __init__(self, version: float = 1.0):
        self.path: pathlib.Path | None = None
        self.version = version
        self.name = ""
        self.comment = ""
        self.english_name = ""
        self.english_comment = ""
        self.vertices: list[Vertex] = []
        self.indices: list[int] = []
        self.materials: list[Material] = []
        self.bones: list[Bone] = []
        self.ik_list: list[IK] = []
        self.morphs: list[Morph] = []
        self.morph_indices: list[int] = []
        self.bone_group_list: list[BoneGroup] = []
        self.bone_display_list: list[tuple[int, int]] = []
        # extend
        self.toon_textures: list[str] = [""] * 10
        self.rigidbodies: list[RigidBody] = []
        self.joints: list[Joint] = []
        # innner use
        self.no_parent_bones: list[Bone] = []

    def each_vertex(self) -> Iterable[Vertex]:
        return self.vertices

    def getUV(self, i: int) -> common.Vector2:
        return self.vertices[i].uv

    def __str__(self) -> str:
        return (
            '<pmd-%g, "%s" vertex: %d, face: %d, material: %d, bone: %d ik: %d, skin: %d>'
            % (
                self.version,
                self.name,
                len(self.vertices),
                len(self.indices),
                len(self.materials),
                len(self.bones),
                len(self.ik_list),
                len(self.morphs),
            )
        )

    def __eq__(self, rhs: object) -> bool:
        match rhs:
            case Pmd():
                return (
                    self.name == rhs.name
                    and self.comment == rhs.comment
                    and self.english_name == rhs.english_name
                    and self.english_comment == rhs.english_comment
                    and self.vertices == rhs.vertices
                    and self.indices == rhs.indices
                    and self.materials == rhs.materials
                    and self.bones == rhs.bones
                    and self.ik_list == rhs.ik_list
                    and self.morphs == rhs.morphs
                    and self.morph_indices == rhs.morph_indices
                    and self.bone_group_list == rhs.bone_group_list
                    and self.bone_display_list == rhs.bone_display_list
                    and self.toon_textures == rhs.toon_textures
                    and self.rigidbodies == rhs.rigidbodies
                    and self.joints == rhs.joints
                )
            case _:
                return False

    def diff(self, rhs: Self) -> None:
        self._diff(rhs, "name")
        self._diff(rhs, "english_name")
        # self._diff(rhs, "comment")
        # self._diff(rhs, "english_comment")
        # self._diff_array(rhs, "vertices")
        # self._diff_array(rhs, "indices")
        self._diff_array(rhs, "materials")
        self._diff_array(rhs, "bones")
        self._diff_array(rhs, "morphs")
        self._diff_array(rhs, "morph_indices")
        self._diff_array(rhs, "bone_group_list")
        for i, (l, r) in enumerate(
            zip(
                sorted(self.bone_display_list, key=lambda e: e[0]),
                sorted(rhs.bone_display_list, key=lambda e: e[0]),
            )
        ):
            if l != r:
                raise common.DifferenceException("{0}: {1}-{2}".format(i, l, r))
        self._diff_array(rhs, "toon_textures")
        self._diff_array(rhs, "rigidbodies")
        self._diff_array(rhs, "joints")
