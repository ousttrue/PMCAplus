from typing import Sequence
import sys
from PySide6 import QtWidgets, QtCore
from .. import PMCA_data
from .generic_tree_model import GenericTreeModel


# class NodeWrap:
#     def __init__(self, src: PMCA_data.NODE | None, parent: "NodeWrap|None" = None):
#         self.src = src
#         self.parent = parent

#     @property
#     def name(self) -> str:
#         if self.src:
#             return self.src.parts.name
#         else:
#             return "None"

#     @property
#     def children(self) -> Sequence["NodeWrap"]:
#         if self.src:
#             return [NodeWrap(child, self) for child in self.src.children]
#         else:
#             return []


class PmcaNodeModel(GenericTreeModel[NodeWrap]):

    def __init__(self, root: PMCA_data.NODE) -> None:
        super().__init__(NodeWrap(root), ["name"], lambda x, _: x.src.parts.name)


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
        vbox.addWidget(hbox)

        # left
        self.tree = QtWidgets.QTreeView()
        hbox.addWidget(self.tree)
        self.tree.setModel(PmcaNodeModel(data.tree))

        # right
        self.list = QtWidgets.QListView()
        hbox.addWidget(self.list)

        # bottom
        self.comment = QtWidgets.QLabel()
        self.comment.setText("comment:")
        vbox.addWidget(self.comment)


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


class MainWindow(QtWidgets.QTabWidget):
    def __init__(self, title: str, data: PMCA_data.PMCAData):
        super().__init__()
        self.setWindowTitle(title)
        # self.setGeometry(100, 100, 200, 150)

        self.model_tab = ModelTab(data)
        self.addTab(self.model_tab, "Model")

        self.color_tab = ColorTab()
        self.addTab(self.color_tab, "Color")

        self.transform_tab = TransformTab()
        self.addTab(self.transform_tab, "Transform")

        self.info_tab = InfoTab()
        self.addTab(self.info_tab, "Info")


class App:
    def __init__(self, title: str, data: PMCA_data.PMCAData):
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = MainWindow(title, data)
        self.window.show()

    def mainloop(self):
        self.app.exec()

    def on_refresh(self, w: float, h: float, t: float):
        pass
        # self.model_tab.set_tree(self.data.tree, True)
        # self.color_tab.l_tree.set_entry(self.data.mat_entry[0], sel=self.cur_mat)  # type: ignore
        # self.info_tab.refresh()
        # self.transform_tab.info_frame.strvar.set(  # type: ignore
        #     "height     = %f\nwidth      = %f\nthickness = %f\n" % (w, h, t)
        # )


def MainFrame(
    title: str,
    data: PMCA_data.PMCAData,
    name: str,
    name_l: str,
    comment: list[str],
) -> App:
    return App(title, data)
