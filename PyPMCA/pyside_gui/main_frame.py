from typing import cast
import logging
import sys
from PySide6 import QtWidgets, QtCore
from .. import PMCA_data
from .generic_tree_model import GenericTreeModel
from .gl_scene import GlScene, PmdSrc
import PMCA  # type: ignore

import glglue.pyside6


LOGGER = logging.getLogger(__name__)


class PmcaNodeModel(GenericTreeModel[PMCA_data.NODE]):

    def __init__(self, root: PMCA_data.NODE) -> None:
        def get_col(node: PMCA_data.NODE, col: int) -> str:
            match col:
                case 0:
                    return node.joint
                case 1:
                    if node.parts:
                        return node.parts.name
                    else:
                        return ""
                case _:
                    return "error"

        super().__init__(
            root,
            ["joint", "parts"],
            lambda x: x.parent,
            lambda x: len(x.children),
            lambda x, row: x.children[row],
            get_col,
        )

    def root_index(self) -> QtCore.QModelIndex:
        return self.createIndex(0, 0, self.root.children[0])


class PartsListModel(GenericTreeModel[PMCA_data.PARTS]):

    def __init__(self, header: str, parts_list: list[PMCA_data.PARTS]) -> None:
        super().__init__(
            None,
            [header],
            lambda x: None,
            lambda x: 0 if x else len(parts_list),
            lambda x, row: parts_list[row],
            lambda x, col: x.name,
        )
        self.parts_list = parts_list

    def index_from_item(self, target: PMCA_data.PARTS) -> QtCore.QModelIndex:
        for i, parts in enumerate(self.parts_list):
            if parts == target:
                return self.createIndex(i, 0, parts)

        return QtCore.QModelIndex()


class ModelTab(QtWidgets.QWidget):
    """
    +----+-----+
    |tree|parts|
    +----+-----+
    |comment   |
    +----------+
    """

    def __init__(self, data: PMCA_data.PMCAData):
        super().__init__()

        self.data = data

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        vbox.addWidget(hbox, stretch=2)

        # left
        self.tree = QtWidgets.QTreeView()
        hbox.addWidget(self.tree)
        tree_model = PmcaNodeModel(data.tree)
        self.tree.setModel(tree_model)
        self.tree.expandAll()
        self.tree.selectionModel().selectionChanged.connect(self.onSelectJoint)
        self.tree.setIndentation(12)

        # right
        self.list = QtWidgets.QTreeView()
        hbox.addWidget(self.list)

        # bottom
        self.comment = QtWidgets.QLabel()
        self.comment.setText("comment:")
        vbox.addWidget(self.comment)

        self.tree.selectionModel().setCurrentIndex(
            tree_model.root_index(),
            QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )

    def onSelectJoint(
        self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection
    ) -> None:
        indexes = selected.indexes()
        if len(indexes) > 0:
            index = indexes[0]
            item = cast(PMCA_data.NODE, index.internalPointer())

            parts = [
                parts for parts in self.data.parts_list if item.joint in parts.type
            ]
            list_model = PartsListModel(f"joints for [{item.joint}]", parts)
            self.list.setModel(list_model)

            self.list.selectionModel().setCurrentIndex(
                list_model.index_from_item(item.parts),
                QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )


class ColorTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        pass


class TransformTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        pass


class InfoTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        pass


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, title: str, data: PMCA_data.PMCAData):
        super().__init__()
        self.setWindowTitle(title)

        self.scene = GlScene()
        self.glwidget = glglue.pyside6.Widget(self, render_gl=self.scene.render)
        self.setCentralWidget(self.glwidget)

        self.model_tab = ModelTab(data)
        self.model_dock = QtWidgets.QDockWidget("Model", self)
        self.model_dock.setWidget(self.model_tab)
        self.addDockWidget(
            QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, self.model_dock
        )
        # self.addTab(self.model_tab, "Model")

        # self.color_tab = ColorTab()
        # self.addTab(self.color_tab, "Color")

        # self.transform_tab = TransformTab()
        # self.addTab(self.transform_tab, "Transform")

        # self.info_tab = InfoTab()
        # self.addTab(self.info_tab, "Info")

    def closeEvent(self, _) -> None:  # type: ignore
        self.scene.shutdown()


class App:
    def __init__(self, title: str, data: PMCA_data.PMCAData):
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = MainWindow(title, data)
        self.window.show()

    def mainloop(self):
        self.app.exec()

    def on_refresh(self, w: float, h: float, t: float):
        data = PMCA.Get_PMD(0)
        if data:
            self.window.scene.set_model(PmdSrc(*data))


def MainFrame(
    title: str,
    data: PMCA_data.PMCAData,
    name: str,
    name_l: str,
    comment: list[str],
) -> App:
    return App(title, data)
