from typing import TypedDict, cast, Iterator
from PySide6 import QtCore
from humanoidio.mmd.pymeshio import vpd


class BoneDict(TypedDict):
    name: str
    type: int
    position: tuple[float, float, float]
    children: list["BoneDict"]
    transform: vpd.Transform | None


class RigModel(QtCore.QAbstractItemModel):
    def __init__(
        self,
        roots: list[BoneDict],
    ):
        super().__init__()
        self.headers = ["name", "type", "t", "q"]
        self.roots = roots
        self.parent_map: dict[str, BoneDict] = {}

        def traverse(b: BoneDict):
            for child in [x for x in b["children"]]:
                match child:
                    case (
                        # {"type": 7}
                        {"name": "ﾈｸﾀｲＩＫ"}
                        | {"name": "左髪ＩＫ"}
                        | {"name": "右髪ＩＫ"}
                        | {"name": "ﾈｸﾀｲ１"}
                        | {"name": "左ｽｶｰﾄ前"}
                        | {"name": "左ｽｶｰﾄ後"}
                        | {"name": "左腕捩1"}
                        | {"name": "左腕捩2"}
                        | {"name": "左腕捩3"}
                        | {"name": "左袖"}
                        | {"name": "右ｽｶｰﾄ前"}
                        | {"name": "右ｽｶｰﾄ後"}
                        | {"name": "右腕捩1"}
                        | {"name": "右腕捩2"}
                        | {"name": "右腕捩3"}
                        | {"name": "右袖"}
                        | {"name": "腰飾り"}
                        | {"name": "左髪１"}
                        | {"name": "右髪１"}
                        | {"name": "前髪１"}
                        | {"name": "前髪２"}
                        | {"name": "前髪３"}
                        | {"name": "左目"}
                        | {"name": "右目"}
                        | {"name": "両目"}
                    ):
                        b["children"].remove(child)
                    case _:
                        self.parent_map[child["name"]] = b
                        traverse(child)

        for root in self.roots:
            traverse(root)

    def get_bone(self, name: str) -> BoneDict | None:

        def traverse(bone: BoneDict) -> Iterator[BoneDict]:
            yield bone
            for child in bone["children"]:
                for x in traverse(child):
                    yield x

        for root in self.roots:
            for x in traverse(root):
                if x["name"] == name:
                    return x

    def set_pose(self, pose: list[vpd.Transform]) -> None:
        for t in pose:
            bone = self.get_bone(t.name)
            if bone:
                bone["transform"] = t

    def columnCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> int:  # type: ignore
        return len(self.headers)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole) -> str | None:  # type: ignore
        match orientation, role:
            case QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole:  # type: ignore
                return self.headers[section]
            case _:
                pass

    def rowCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> int:  # type: ignore
        if parent.isValid():
            parentItem = cast(BoneDict, parent.internalPointer())
            return len(parentItem["children"])
        else:
            return len(self.roots)

    def data(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex, role: QtCore.Qt.ItemDataRole) -> str | None:  # type: ignore
        if not index.isValid():
            return
        item = cast(BoneDict, index.internalPointer())
        match role:
            case QtCore.Qt.ItemDataRole.DisplayRole:
                match index.column():
                    case 0:
                        return item["name"]
                    case 1:
                        return f'{item["type"]}'
                    case 2:
                        t = item.get("transform")
                        if t:
                            return f"{t.pos}"
                    case 3:
                        t = item.get("transform")
                        if t:
                            return f"{t.q}"
                    case _:
                        raise NotImplementedError()
            case _:
                pass

    def index(  # type: ignore
        self,
        row: int,
        column: int,
        parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> QtCore.QModelIndex:
        if parent.isValid():
            parentItem = cast(BoneDict, parent.internalPointer())
            childItem = parentItem["children"][row]
        else:
            childItem = self.roots[row]
        return self.createIndex(row, column, childItem)

    def parent(  # type: ignore
        self,
        child: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> QtCore.QModelIndex:
        if child.isValid():
            childItem = cast(BoneDict, child.internalPointer())
            # row, parentItem = self.get_parent(childItem)
            parent = self.parent_map.get(childItem["name"])
            if parent:
                return self.createIndex(0, 0, parent)

        return QtCore.QModelIndex()
