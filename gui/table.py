from typing import Callable, cast
import pathlib
from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QStyleOptionViewItem,
)
from PySide6.QtCore import (
    Qt,
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    QRect,
)
from PySide6.QtGui import QPixmap, QPainter
from humanoidio import gltf


class GltfMaterialModel(QAbstractTableModel):
    def __init__(
        self,
        items: list[gltf.Material],
        headers: list[str],
        column_from_item: Callable[[gltf.Material, int], str],
    ):
        super().__init__()
        self.headers = headers
        self.column_from_item = column_from_item
        self.items = items

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex) -> int:  # type: ignore
        return len(self.headers)

    def data(self, index: QModelIndex | QPersistentModelIndex, role: Qt.ItemDataRole) -> str | None:  # type: ignore
        if role == Qt.DisplayRole:  # type: ignore
            if index.isValid():
                item: gltf.Material = index.internalPointer()  # type: ignore
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
        assert not parent.isValid()
        childItem = self.items[row]
        return self.createIndex(row, column, childItem)

    def parent(  # type: ignore
        self,
        child: QModelIndex | QPersistentModelIndex,
    ) -> QModelIndex:
        return QModelIndex()

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex) -> int:  # type: ignore
        return len(self.items)


class ImageDelegate(QStyledItemDelegate):
    def __init__(self, loader: gltf.Loader):
        super().__init__()
        self.loader = loader
        self.tex_map: dict[gltf.Texture, QPixmap] = {}
        self.path_map: dict[pathlib.Path, QPixmap] = {}

    def get_or_create(self, item: pathlib.Path | gltf.Texture) -> QPixmap | None:
        match item:
            case pathlib.Path():
                pixmap = self.path_map.get(item)
                if pixmap:
                    return pixmap

                image = QPixmap()
                image.load(str(item))  # type: ignore
                self.path_map[item] = image
                return image

            case gltf.Texture():
                pixmap = self.tex_map.get(item)
                if pixmap:
                    return pixmap

                image = QPixmap()
                image.loadFromData(item.data)  # type: ignore
                self.tex_map[item] = image
                return image

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        if index.column() == 1:
            match index.internalPointer():  # type: ignore
                case gltf.Material() as m:  # type: ignore
                    if m.color_texture != None:
                        pixmap = self.get_or_create(
                            self.loader.textures[m.color_texture]
                        )
                        if pixmap:
                            # scale = 128 / pixmap.height()
                            rect = cast(QRect, option.rect)  # type: ignore
                            painter.drawPixmap(
                                rect.x(),
                                rect.y(),
                                rect.width(),
                                rect.height(),
                                pixmap,
                            )
