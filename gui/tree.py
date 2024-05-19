from typing import Protocol, Self, TypeVar, Generic, Callable
from typing import TypeVar, Generic, Callable, cast, Protocol, Self
from PySide6 import QtCore, QtGui
from humanoidio import gltf


class NodeItem(Protocol):
    parent: "Self|None"
    children: list["Self"]


T = TypeVar("T", bound=NodeItem)


class GenericModel(QtCore.QAbstractItemModel, Generic[T]):
    def __init__(
        self,
        root: T,
        headers: list[str],
        display_column_from_item: Callable[[T, int], str],
        fg_column_from_item: Callable[[T, int], QtGui.QBrush] | None = None,
    ):
        super().__init__()
        self.headers = headers
        self.display_column_from_item = display_column_from_item
        self.fg_column_from_item = fg_column_from_item
        self.root = root

    def columnCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> int:  # type: ignore
        return len(self.headers)

    def data(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex, role: QtCore.Qt.ItemDataRole) -> str | None:  # type: ignore
        if not index.isValid():
            return
        item: T = index.internalPointer()  # type: ignore
        match role:
            case QtCore.Qt.ItemDataRole.DisplayRole:
                return self.display_column_from_item(item, index.column())
            case QtCore.Qt.ItemDataRole.BackgroundRole:
                if self.fg_column_from_item:
                    return self.fg_column_from_item(item, index.column())  # type: ignore
            case _:
                pass

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole) -> str | None:  # type: ignore
        match orientation, role:
            case QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole:  # type: ignore
                return self.headers[section]
            case _:
                pass

    def index(  # type: ignore
        self,
        row: int,
        column: int,
        parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> QtCore.QModelIndex:
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
        child: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> QtCore.QModelIndex:
        if child.isValid():
            childItem = cast(T, child.internalPointer())  # type: ignore
            # row, parentItem = self.get_parent(childItem)
            if childItem and childItem.parent:
                return self.createIndex(0, 0, childItem.parent)

        return QtCore.QModelIndex()

    def rowCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> int:  # type: ignore
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
        super().__init__(
            root, ["name", "humanoid", "vertex"], self.get_display, self.get_fg
        )

    def get_display(self, item: gltf.Node, col: int) -> str:
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

    def get_fg(self, item: gltf.Node, col: int) -> QtGui.QColor:
        if item.removable():
            return QtGui.QColor(220, 220, 220)

