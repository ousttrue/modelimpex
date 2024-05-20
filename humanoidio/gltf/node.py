from typing import NamedTuple, Iterator
import dataclasses
from .mesh import Mesh, ExportMesh
from ..human_bones import HumanoidBones


class RotationConstraint(NamedTuple):
    target: "Node"
    weight: float


class Skin:
    def __init__(self, joints: list["Node"] | None = None):
        self.joints: list["Node"] = joints or []


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
    world_position: tuple[float, float, float] = (0, 0, 0)

    def __hash__(self) -> int:
        return hash(self.name)

    def add_child(self, child: "Node") -> None:
        if child.parent:
            child.parent.children.remove(child)
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "Node") -> None:
        assert child.parent == self
        child.parent = None
        self.children.remove(child)

    def traverse(self) -> Iterator["Node"]:
        yield self
        for child in self.children:
            for x in child.traverse():
                yield x

    def removable(self) -> bool:
        if self.mesh:
            return False
        if self.humanoid_bone:
            return False
        if self.vertex_count > 0:
            return False
        return True

    def update_world_position(
        self, parent: tuple[float, float, float] = (0, 0, 0)
    ) -> None:
        self.world_position = (
            parent[0] + self.translation[0],
            parent[1] + self.translation[1],
            parent[2] + self.translation[2],
        )
        for child in self.children:
            child.update_world_position(self.world_position)

    def local_from_world(self) -> None:
        if self.parent:
            self.translation = (
                self.world_position[0] - self.parent.world_position[0],
                self.world_position[1] - self.parent.world_position[1],
                self.world_position[2] - self.parent.world_position[2],
            )
        else:
            self.translation = (
                self.world_position[0],
                self.world_position[1],
                self.world_position[2],
            )
        for child in self.children:
            child.local_from_world()
