from typing import NamedTuple
import sys
import zipfile
import pathlib
from PySide6 import QtWidgets, QtCore, QtGui


HERE = pathlib.Path(__file__).absolute().parent


class CurrentArchive(NamedTuple):
    path: pathlib.Path
    encoding: str
    zf: zipfile.ZipFile | None = None


class ArchiveModel(QtCore.QAbstractTableModel):
    def __init__(
        self,
        zf: zipfile.ZipFile,
    ):
        super().__init__()
        self.headers = ["name"]
        self.zf = zf
        self.names = zf.namelist()
        # self.column_from_item = column_from_item
        # self.items = items

    def columnCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> int:  # type: ignore
        return len(self.headers)

    def data(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex, role: QtCore.Qt.ItemDataRole) -> str | None:  # type: ignore
        if role == QtCore.Qt.DisplayRole:  # type: ignore
            if index.isValid():
                name = index.internalPointer()  # type: ignore
                return name

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
        assert not parent.isValid()
        childItem = self.names[row]
        return self.createIndex(row, column, childItem)

    def parent(  # type: ignore
        self,
        child: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> QtCore.QModelIndex:
        return QtCore.QModelIndex()

    def rowCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> int:  # type: ignore
        return len(self.names)


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(None)
        self.archive: CurrentArchive | None = None

        self.tree = QtWidgets.QTreeView()
        self.setCentralWidget(self.tree)

        # status bar
        self.sb = self.statusBar()
        self.sb.showMessage("")

        # menu
        self.menubar = self.menuBar()
        self.menubar.setNativeMenuBar(False)

        self.menu_file = self.menubar.addMenu("File")

        open_action = QtGui.QAction("Open", self)
        open_action.triggered.connect(self.open_dialog)
        self.menu_file.addAction(open_action)  # type: ignore

        save_action = QtGui.QAction("Save", self)
        save_action.triggered.connect(self.save_dialog)
        self.menu_file.addAction(save_action)  # type: ignore

        self.menu_docks = self.menubar.addMenu("Docks")

        # left
        self.encodings = QtWidgets.QComboBox()
        self.encodings.addItems(
            [
                "utf-8",
                "cp932",
                "GB18030",
                # "GB2312",
                # "GBK",
                # "BIG5",
                # "EUC-TW",
                # "ISO-2022-CN",
            ]
        )
        self.encodings.currentIndexChanged.connect(self.on_select_encoding)  # type: ignore
        self.encodings_dock = QtWidgets.QDockWidget("encodings", self)
        self.encodings_dock.setWidget(self.encodings)
        self.addDockWidget(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.encodings_dock
        )
        self.menu_docks.addAction(self.encodings_dock.toggleViewAction())  # type: ignore

    def on_select_encoding(self, _) -> None:
        encoding = self.encodings.currentText()
        if self.archive:
            zf = zipfile.ZipFile(self.archive.path, metadata_encoding=encoding)
            self.sb.showMessage(encoding)
            self.set(self.archive.path, zf, encoding)

    def open_dialog(self) -> None:
        file, ok = QtWidgets.QFileDialog.getOpenFileName(
            self,
            filter=";;".join(
                [
                    "zip (*.zip)",
                    "All Files (*.*)",
                ]
            ),
        )
        if not ok:
            return
        self.open(pathlib.Path(file))

    def open(self, path: pathlib.Path) -> None:
        encoding = self.encodings.currentText()
        try:
            zf = zipfile.ZipFile(path, metadata_encoding=encoding)
            self.sb.showMessage(encoding)
            self.set(path, zf, encoding)
        except:
            self.archive = CurrentArchive(path, encoding)

    def set(self, path: pathlib.Path, zf: zipfile.ZipFile, encoding: str) -> None:
        if self.archive:
            if self.archive.zf:
                self.archive.zf.close()
        self.archive = CurrentArchive(path, encoding, zf)
        model = ArchiveModel(zf)
        self.tree.setModel(model)

    def save_dialog(self) -> None:
        if not self.archive:
            return

        dir = ""
        indexes = self.tree.selectionModel().selectedIndexes()
        if indexes:
            dir = pathlib.Path(indexes[0].internalPointer()).stem  # type: ignore
            QtGui.QClipboard().setText(dir)

        save_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            dir=str(self.archive.path.parent / dir),
        )
        if not save_dir:
            return

        self.save(pathlib.Path(save_dir))

    def save(self, dir: pathlib.Path):
        if self.archive:
            if self.archive.zf:
                self.archive.zf.extractall(dir)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = Window()

    if len(sys.argv) > 1:
        window.open(pathlib.Path(sys.argv[1]))

    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
