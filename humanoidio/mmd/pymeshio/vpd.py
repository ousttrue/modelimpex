from typing import NamedTuple
import re
from . import common


RE_OPEN = re.compile(r"^(\w+){(.*)")
RE_OSM = re.compile(r"^\w+\.osm;")
RE_COUNT = re.compile(r"^(\d+);")


class Transform(NamedTuple):
    name: str
    pos: common.Vector3
    q: common.Quaternion


def parseTransform(name: str, lines: list[str]) -> Transform:
    pos = common.Vector3(
        *[float(token) for token in lines.pop(0).split(";")[0].split(",")]
    )
    q = common.Quaternion(
        *[float(token) for token in lines.pop(0).split(";")[0].split(",")]
    )
    assert lines.pop(0) == "}"
    return Transform(name, pos, q)


def parse(src: str) -> list[Transform]:
    lines = [x.strip() for x in src.splitlines()]
    if lines.pop(0) != "Vocaloid Pose Data file":
        raise RuntimeError()

    pose: list[Transform] = []
    bone_count = -1
    while len(lines) > 0:
        line = lines.pop(0)
        if line == "":
            continue
        m = RE_OPEN.match(line)
        if m:
            transform = parseTransform(m.group(2), lines)
            pose.append(transform)
            if not transform:
                raise Exception("invalid bone")
            continue

        m = RE_OSM.match(line)
        if m:
            continue

        m = RE_COUNT.match(line)
        if m:
            bone_count = int(m.group(1))
            continue

    assert len(pose) == bone_count
    return pose
