from typing import NamedTuple, Iterator
import dataclasses
from .mesh import Mesh, ExportMesh
from ..human_bones import HumanoidBones


class RotationConstraint(NamedTuple):
    target: "Node"
    weight: float


@dataclasses.dataclass
class Skin:
    joints: list["Node"] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Node:
    name: str
    children: list["Node"] = dataclasses.field(default_factory=list)
    parent: "Node|None" = None
    translation: tuple[float, float, float] = (0, 0, 0)
    rotation: tuple[float, float, float, float] = (0, 0, 0, 1)
    scale: tuple[float, float, float] = (1, 1, 1)
    mesh: Mesh | ExportMesh | None = None
    skin: Skin | None = None
    humanoid_bone: HumanoidBones | None = None
    constraint: RotationConstraint | None = None
    vertex_count: int = 0

    def add_child(self, child: "Node"):
        child.parent = self
        self.children.append(child)

    def traverse(self) -> Iterator["Node"]:
        yield self
        for child in self.children:
            for x in child.traverse():
                yield x
