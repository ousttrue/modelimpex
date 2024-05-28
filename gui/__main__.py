from typing import Any
import logging
import pathlib
import os
import sys
from PySide6 import QtWidgets, QtCore, QtGui
from humanoidio import mmd, gltf
from . import tree, table
from .gl_scene import GlScene


LOGGER = logging.getLogger(__name__)


def texture_to_pixmap(src: gltf.Texture) -> QtGui.QPixmap:
    match src.data:
        case gltf.TextureData():
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(src.data.data)  # type:ignore
            return pixmap
        case pathlib.Path():
            pixmap = QtGui.QPixmap()
            pixmap.load(str(src.data))  # type: ignore
            if src.data.suffix.lower() == ".tga":
                pixmap = pixmap.transformed(QtGui.QTransform().scale(1, -1))
            return pixmap


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(None)

        # menu
        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)

        self.menu_file = self.menubar.addMenu("File")
        open_action = QtGui.QAction("Open", self)
        self.menu_file.addAction(open_action)  # type: ignore
        open_action.triggered.connect(self.open_dialog)

        self.menu_docks = self.menubar.addMenu("Docks")

        # status bar
        self.sb = self.statusBar()
        self.sb.showMessage("ステータスバー")

        # central
        import glglue.pyside6  # type: ignore

        self.scene = GlScene()
        self.glwidget = glglue.pyside6.Widget(self, render_gl=self.scene.render)
        self.setCentralWidget(self.glwidget)

        #
        # docks
        #

        # bones(tree)
        self.tree = QtWidgets.QTreeView()
        self.tree.setIndentation(8)
        self._add_dock("bones", QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.tree)

        # materials(list)
        self.table = QtWidgets.QTableView()
        vertical_header = self.table.verticalHeader()
        vertical_header.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)  # type: ignore
        vertical_header.setDefaultSectionSize(64)
        self._add_dock(
            "textures", QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.table
        )

    def _add_dock(
        self, name: str, area: QtCore.Qt.DockWidgetArea, widget: QtWidgets.QWidget
    ) -> QtWidgets.QDockWidget:
        dock = QtWidgets.QDockWidget(name, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)
        self.menu_docks.addAction(dock.toggleViewAction())  # type: ignore
        return dock

    def open_dialog(self) -> None:
        file, ok = QtWidgets.QFileDialog.getOpenFileName(
            self,
            filter=";;".join(
                [
                    "Models (*.glf *.glb *.vrm *.pmd *.pmx)",
                    "All Files (*.*)",
                ]
            ),
        )
        if not ok:
            return
        self.open_file(pathlib.Path(file))

    def open_file(self, file: pathlib.Path) -> None:
        if not file.exists():
            LOGGER.warning(f"{file} not exists")
            return

        match file.suffix.lower():
            case ".vrm":
                gltf_model, _conversion = gltf.load(
                    file, file.read_bytes(), gltf.Coordinate.BLENDER_ROTATE
                )
                if gltf_model:
                    self.set_model(gltf_model)
            case ".pmd" | ".pmx":
                gltf_model = mmd.load_as_gltf(file)
                if gltf_model:
                    self.set_model(gltf_model)

            case _:
                LOGGER.error(f"unknown: {file}")

    def set_model(self, loader: gltf.Loader):
        loader.guess_human_bones()
        loader.remove_bones()

        self.setWindowTitle(loader.name)
        tree_model = tree.GltfNodeModel(loader.nodes)
        self.tree.setModel(tree_model)
        # self.tree.expandAll()

        pixmaps: list[QtGui.QPixmap] = []
        images: list[QtGui.QImage] = []
        for t in loader.textures:
            pixmap = texture_to_pixmap(t)
            pixmaps.append(pixmap)
            image = pixmap.toImage()
            # if image.format() == QtGui.QImage.Format.Format_ARGB32_Premultiplied:
            #     image.convertToFormat(QtGui.QImage.Format.Format_RGBA8888)
            images.append(image)

        self.table.setItemDelegateForColumn(
            1, table.ImageDelegate(loader.textures, pixmaps)
        )

        def get_col(item: gltf.Texture, col: int) -> Any:
            match col:
                case 0:
                    return item.name
                case 2:
                    index = loader.textures.index(item)
                    image: QtGui.QImage | None = None
                    if index != -1:
                        image = images[index]
                    if image:
                        return str(image.format())
                    else:
                        return ""
                case _:
                    pass

        table_model = table.GltfTextureModel(
            loader.textures, ["name", "texture", "format"], get_col
        )
        self.table.setModel(table_model)

        self.scene.set_model(loader, images)


def main(path: pathlib.Path):
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.resize(1024, 768)
    window.show()
    window.open_file(path)
    sys.exit(app.exec())


if __name__ == "__main__":
    print(os.getpid())
    logging.basicConfig(
        format="[%(levelname)s] %(name)s: %(message)s", level=logging.DEBUG
    )
    main(pathlib.Path(sys.argv[1]))
