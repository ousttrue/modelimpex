from typing import cast
import sys, os, pathlib
import logging
import json
from PySide6 import QtWidgets, QtCore, QtGui
from . import rig
from humanoidio.mmd.pymeshio import vpd


LOGGER = logging.getLogger(__name__)


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

        self.tree = QtWidgets.QTreeView()
        # self.tree.setIndentation(4)
        self.setCentralWidget(self.tree)

    def open_dialog(self) -> None:
        file, ok = QtWidgets.QFileDialog.getOpenFileName(
            self,
            filter=";;".join(
                [
                    "Pose (*.vpd)",
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

        pose = vpd.parse(file.read_text(encoding="cp932"))
        model = cast(rig.RigModel, self.tree.model())
        model.set_pose(pose)
        self.tree.setModel(model)

    def load_rig(self, file: pathlib.Path) -> None:
        roots = cast(list[rig.BoneDict], json.loads(file.read_text(encoding="utf-8")))
        model = rig.RigModel(roots)
        self.tree.setModel(model)


def main(path: pathlib.Path):
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.resize(1024, 768)
    window.show()
    window.load_rig(path)
    sys.exit(app.exec())


if __name__ == "__main__":
    print(os.getpid())
    logging.basicConfig(
        format="[%(levelname)s] %(name)s: %(message)s", level=logging.DEBUG
    )
    main(pathlib.Path(sys.argv[1]))
