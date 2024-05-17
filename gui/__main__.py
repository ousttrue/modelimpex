from typing import Any
import logging
import pathlib
import os
import sys
from OpenGL import GL
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
from PySide6.QtGui import QAction
from humanoidio import mmd, gltf
from . import tree, table
from .gl_scene import GlScene


class Window(QMainWindow):
    def __init__(self):
        super().__init__(None)
        import glglue.pyside6

        self.scene = GlScene()

        self.glwidget = glglue.pyside6.Widget(self, render_gl=self.scene.render)
        self.setCentralWidget(self.glwidget)

        # menu
        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)

        self.menu_file = self.menubar.addMenu("File")
        open_action = QAction("Open", self)
        self.menu_file.addAction(open_action)  # type: ignore
        open_action.triggered.connect(self.file_open)

        self.menu_docks = self.menubar.addMenu("Docks")

        # status bar
        self.sb = self.statusBar()
        self.sb.showMessage("ステータスバー")

        #
        # docks
        #
        self.tree = QTreeView()
        self.table = QTableView()
        vertical_header = self.table.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.Fixed)  # type: ignore
        vertical_header.setDefaultSectionSize(64)

        # bones(tree)
        self.bones = QDockWidget("bones", self)
        self.bones.setWidget(self.tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.bones)
        self.menu_docks.addAction(self.bones.toggleViewAction())  # type: ignore

        # materials(list)
        self.materials = QDockWidget("materials", self)
        self.materials.setWidget(self.table)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.materials)
        self.menu_docks.addAction(self.materials.toggleViewAction())  # type: ignore

    def file_open(self) -> None:
        print("file_open")

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

        self.scene.set_model(loader)

        # self.setWindowTitle(loade)


def main(path: pathlib.Path):
    import sys

    # app = QApplication(sys.argv)
    # window = Window()
    # window.show()

    model = mmd.from_path(path)
    # if model:
    #     window.set(model)

    # sys.exit(app.exec())

    import glglue.glfw

    scene = GlScene()
    if model:
        scene.set_model(model)

    loop = glglue.glfw.LoopManager(
        title="glfw sample", hint=glglue.glfw.GLContextHint()
    )
    print(GL.glGetString(GL.GL_VENDOR))
    print(GL.glGetString(GL.GL_RENDERER))
    print(GL.glGetString(GL.GL_VERSION))

    while True:
      
        frame = loop.begin_frame()
        if not frame:
            break
        scene.render(frame)
        loop.end_frame()


if __name__ == "__main__":
    print(os.getpid())
    logging.basicConfig(level=logging.DEBUG)
    main(pathlib.Path(sys.argv[1]))
