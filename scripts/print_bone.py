from typing import TypedDict
import pathlib
import argparse
import humanoidio.mmd
from humanoidio.mmd.pmd import pmd_format
import json


class Bone(TypedDict):
    name: str
    type: int
    position: tuple[float, float, float]
    children: list["Bone"]


def main(file: pathlib.Path) -> None:
    print(file)
    model = humanoidio.mmd.load_pmd(file)
    assert model

    def make_bone(b: pmd_format.Bone) -> Bone:
        return Bone(
            name=b.name,
            type=b.type,
            position=(b.pos.x, b.pos.y, b.pos.z),
            children=[],
        )

    bones: list[Bone] = [make_bone(b) for b in model.bones]
    roots: list[Bone] = []
    for i, b in enumerate(model.bones):
        if b.parent_index >= 0 and b.parent_index < len(bones):
            bones[b.parent_index]["children"].append(bones[i])
        else:
            roots.append(bones[i])
    print(json.dumps(roots, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=pathlib.Path)
    args = parser.parse_args()
    main(args.src)
