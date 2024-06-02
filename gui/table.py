from typing import Callable, cast
from PySide6 import QtWidgets, QtCore, QtGui
from humanoidio import gltf


class GltfTextureModel(QtCore.QAbstractTableModel):
    def __init__(
        self,
        items: list[gltf.Texture],
        headers: list[str],
        column_from_item: Callable[[gltf.Texture, int], str],
    ):
        super().__init__()
        self.headers = headers
        self.column_from_item = column_from_item
        self.items = items

    def columnCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> int:  # type: ignore
        return len(self.headers)

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: QtCore.Qt.ItemDataRole) -> str | None:  # type: ignore
        match orientation, role:
            case QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole:  # type: ignore
                return self.headers[section]
            case _:
                pass

    def data(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex, role: QtCore.Qt.ItemDataRole) -> str | None:  # type: ignore
        if role == QtCore.Qt.DisplayRole:  # type: ignore
            if index.isValid():
                item: gltf.Texture = index.internalPointer()  # type: ignore
                return self.column_from_item(item, index.column())

    def rowCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> int:  # type: ignore
        return len(self.items)

    def index(  # type: ignore
        self,
        row: int,
        column: int,
        parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> QtCore.QModelIndex:
        assert not parent.isValid()
        childItem = self.items[row]
        return self.createIndex(row, column, childItem)

    def parent(  # type: ignore
        self,
        child: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> QtCore.QModelIndex:
        return QtCore.QModelIndex()


class ImageDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, textures: list[gltf.Texture], pixmaps: list[QtGui.QPixmap]):
        super().__init__()
        self.textures = textures
        self.pixmaps = pixmaps

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> None:
        if index.column() == 1:
            item = cast(gltf.Texture, index.internalPointer())
            texture_index = self.textures.index(item)
            if texture_index != -1:
                pixmap = self.pixmaps[texture_index]
                rect = cast(QtCore.QRect, option.rect)  # type: ignore
                painter.drawPixmap(
                    rect.x(),
                    rect.y(),
                    rect.width(),
                    rect.height(),
                    pixmap,
                )
