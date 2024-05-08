from typing import TypeVar, Generic, Callable, cast, Protocol, Self, Any
import pathlib
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDockWidget,
    QTreeView,
    QTableView,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QHeaderView,
)
from PySide6.QtCore import (
    Qt,
    QAbstractItemModel,
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    QSize,
    QRect,
)
from PySide6.QtGui import QPixmap, QPainter
from humanoidio import mmd, gltf


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


class GltfNodeModel(GenericModel[gltf.Node]):

    def __init__(self, nodes: list[gltf.Node]) -> None:
        root = gltf.Node("__root__")
        for node in nodes:
            if not node.parent:
                root.add_child(node)
        super().__init__(root, ["name"], lambda x, _: x.name)


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

    def sizeHint(self, option, index):
        if index.column() == 1:
            return QSize(128, 128)  # whatever your dimensions are
        else:
            return super().sizeHint(option, index)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        if index.column() == 1:
            match index.internalPointer():
                case gltf.Material() as m:
                    if m.color_texture != None:
                        pixmap = self.get_or_create(
                            self.loader.textures[m.color_texture]
                        )
                        if pixmap:
                            scale = 128 / pixmap.height()
                            rect = cast(QRect, option.rect)
                            painter.drawPixmap(
                                rect.x(),
                                rect.y(),
                                rect.width(),
                                rect.height(),
                                pixmap,
                            )


class Window(QMainWindow):
    def __init__(self):
        super().__init__(None)
        import glglue.pyside6
        from glglue.scene.sample import SampleScene

        self.scene = SampleScene()

        self.glwidget = glglue.pyside6.Widget(self, render_gl=self.scene.render)
        self.setCentralWidget(self.glwidget)

        self.sb = self.statusBar()
        self.sb.showMessage("ステータスバー")

        self.tree = QTreeView()
        self.table = QTableView()

        vertical_header = self.table.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.Fixed)
        vertical_header.setDefaultSectionSize(64)

        # bones(tree)
        self.bones = QDockWidget("bones", self)
        self.bones.setWidget(self.tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.bones)

        # materials(list)
        self.materials = QDockWidget("materials", self)
        self.materials.setWidget(self.table)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.materials)

    def set(self, loader: gltf.Loader):
        tree_model = GltfNodeModel(loader.nodes)
        self.tree.setModel(tree_model)

        self.table.setItemDelegateForColumn(1, ImageDelegate(loader))

        def get_col(item: gltf.Material, col: int) -> Any:
            match col:
                case 0:
                    return item.name
                case _:
                    pass

        table_model = GltfMaterialModel(loader.materials, ["name", "vertex"], get_col)
        self.table.setModel(table_model)


def main(path: pathlib.Path):
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()

    model = mmd.from_path(path)
    if model:
        window.set(model)

    sys.exit(app.exec())


if __name__ == "__main__":
    main(pathlib.Path(sys.argv[1]))
