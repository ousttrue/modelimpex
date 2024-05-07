from typing import TypeVar, Generic, Callable, cast
import pathlib
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDockWidget,
    QScrollArea,
    QLabel,
    QTreeView,
)
from PySide6.QtCore import (
    Qt,
    QAbstractItemModel,
    QModelIndex,
    QPersistentModelIndex,
)
from humanoidio import mmd, gltf


T = TypeVar("T")


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
            parentItem: Node = parent.internalPointer()  # type: ignore
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
        super().__init__(root, ["name"], lambda x, _: x.name)


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

        # bones(tree)
        self.bones = QDockWidget("bones", self)
        self.bones.setWidget(self.tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.bones)

        # materials(list)
        dock2la = QLabel("ドック2")
        # dock2la.setFixedSize(700, 220)
        scar = QScrollArea()
        scar.setWidget(dock2la)
        scar.setStyleSheet("background-color: #a1d4bf")
        self.materials = QDockWidget("dock 2", self)  # 2つ目のドックウィジェット
        self.materials.setWidget(scar)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.materials)

    def set(self, loader: gltf.Loader):
        model = GltfNodeModel(loader.nodes)
        self.tree.setModel(model)


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
