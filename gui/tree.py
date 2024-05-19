from typing import Protocol, Self, TypeVar, Generic, Callable
from typing import TypeVar, Generic, Callable, cast, Protocol, Self
from PySide6.QtCore import (
    Qt,
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
)
from humanoidio import gltf


class NodeItem(Protocol):
    parent: "Self|None"
    children: list["Self"]


T = TypeVar("T", bound=NodeItem)


class GenericModel(QAbstractItemModel, Generic[T]):
    def __init__(
        self,
        root: T,
        headers: list[str],
        column_from_item: Callable[[T, int], str],
    ):
        super().__init__()
        self.headers = headers
        self.column_from_item = column_from_item
        self.root = root

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex) -> int:  # type: ignore
        return len(self.headers)

    def data(self, index: QModelIndex | QPersistentModelIndex, role: Qt.ItemDataRole) -> str | None:  # type: ignore
        if role == Qt.DisplayRole:  # type: ignore
            if index.isValid():
                item: T = index.internalPointer()  # type: ignore
                return self.column_from_item(item, index.column())

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole) -> str | None:  # type: ignore
        match orientation, role:
            case Qt.Horizontal, Qt.DisplayRole:  # type: ignore
                return self.headers[section]
            case _:
                pass

    def index(  # type: ignore
        self, row: int, column: int, parent: QModelIndex | QPersistentModelIndex
    ) -> QModelIndex:
        if parent.isValid():
            parentItem: T = parent.internalPointer()  # type: ignore
            childItem = parentItem.children[row]
            return self.createIndex(row, column, childItem)
        else:
            parentItem = self.root
            childItem = parentItem.children[row]
            return self.createIndex(row, column, childItem)

    def parent(  # type: ignore
        self,
        child: QModelIndex | QPersistentModelIndex,
    ) -> QModelIndex:
        if child.isValid():
            childItem = cast(T, child.internalPointer())  # type: ignore
            # row, parentItem = self.get_parent(childItem)
            if childItem and childItem.parent:
                return self.createIndex(0, 0, childItem.parent)

        return QModelIndex()

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex) -> int:  # type: ignore
        if parent.isValid():
            parentItem: T = parent.internalPointer()  # type: ignore
            return len(parentItem.children)
        else:
            parentItem = self.root
            return len(parentItem.children)


class GltfNodeModel(GenericModel[gltf.Node]):

    def __init__(self, nodes: list[gltf.Node]) -> None:
        root = gltf.Node("__root__")
        for node in nodes:
            if not node.parent:
                root.add_child(node)
        super().__init__(root, ["name", "humanoid", "vertex"], self.get_col)

    def get_col(self, item: gltf.Node, col: int) -> str:
        match col:
            case 0:
                if item.humanoid_bone:
                    return "🦴" + item.name
                else:
                    return item.name
            case 1:
                return item.humanoid_bone or ""
            case 2:
                return str(item.vertex_count)
            case _:
                return ""
