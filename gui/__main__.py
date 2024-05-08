from typing import Any
import pathlib
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDockWidget,
    QTreeView,
    QTableView,
    QHeaderView,
)
from PySide6.QtCore import (
    Qt,
)
from humanoidio import mmd, gltf
from . import tree, table


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
        vertical_header.setSectionResizeMode(QHeaderView.Fixed)  # type: ignore
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
        tree_model = tree.GltfNodeModel(loader.nodes)
        self.tree.setModel(tree_model)

        self.table.setItemDelegateForColumn(1, table.ImageDelegate(loader))

        def get_col(item: gltf.Material, col: int) -> Any:
            match col:
                case 0:
                    return item.name
                case _:
                    pass

        table_model = table.GltfMaterialModel(
            loader.materials, ["name", "vertex"], get_col
        )
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
