from typing import cast, Callable
import logging
import sys
from PySide6 import QtWidgets, QtCore
from .. import PMCA_asset
from .. import PMCA_cnl
from .generic_tree_model import GenericTreeModel
from .gl_scene import GlScene, PmdSrc
import PMCA  # type: ignore
from .. import native

import glglue.pyside6


LOGGER = logging.getLogger(__name__)


class PmcaNodeModel(GenericTreeModel[PMCA_cnl.NODE]):
    def __init__(self, root: PMCA_cnl.NODE) -> None:
        def get_col(node: PMCA_cnl.NODE, col: int) -> str:
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


class PartsListModel(GenericTreeModel[PMCA_asset.PARTS]):
    def __init__(self, header: str, parts_list: list[PMCA_asset.PARTS]) -> None:
        super().__init__(
            None,
            [header],
            lambda x: None,
            lambda x: 0 if x else len(parts_list),
            lambda x, row: parts_list[row],
            lambda x, col: x.name,
        )
        self.parts_list = parts_list

    def index_from_item(self, target: PMCA_asset.PARTS) -> QtCore.QModelIndex:
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

    def __init__(self, data: PMCA_asset.PMCAData, cnl: PMCA_cnl.CnlInfo):
        super().__init__()
        self.data = data
        self.cnl = cnl

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        vbox.addWidget(hbox, stretch=2)

        # left
        self.tree = QtWidgets.QTreeView()
        hbox.addWidget(self.tree)
        self.tree.setIndentation(12)

        # right
        self.list = QtWidgets.QTreeView()
        hbox.addWidget(self.list)

        # bottom
        self.comment = QtWidgets.QLabel()
        self.comment.setText("comment:")
        vbox.addWidget(self.comment)

        self.set_tree_model(self.cnl.tree.children[0])
        self.data_updated: list[Callable[[], None]] = []

    def set_tree_model(self, selected: PMCA_cnl.NODE):
        tree_model = PmcaNodeModel(self.cnl.tree)
        self.tree.setModel(tree_model)
        self.tree.expandAll()
        self.tree.selectionModel().selectionChanged.connect(self.onJointSelected)
        self.tree.selectionModel().setCurrentIndex(
            tree_model.createIndex(0, 0, selected),
            QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )

    def onJointSelected(
        self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection
    ) -> None:
        indexes = selected.indexes()
        if len(indexes) == 0:
            return
        index = indexes[0]
        item = cast(PMCA_cnl.NODE, index.internalPointer())

        parts = [parts for parts in self.data.parts_list if item.joint in parts.type]
        list_model = PartsListModel(f"[{item.joint}] parts", parts)
        self.list.setModel(list_model)
        self.list.selectionModel().selectionChanged.connect(self.onPartsSelected)

        if item.parts:
            self.list.selectionModel().setCurrentIndex(
                list_model.index_from_item(item.parts),
                QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect,
            )

    def onPartsSelected(
        self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection
    ):
        indexes = selected.indexes()
        if len(indexes) == 0:
            return

        parts_index = indexes[0]
        parts = cast(PMCA_asset.PARTS, parts_index.internalPointer())

        tree_index = self.tree.selectionModel().currentIndex()
        if not tree_index.isValid():
            return
        node = cast(PMCA_cnl.NODE, tree_index.internalPointer())

        print(f"{node} => {parts}")
        assert node.parent
        joint, joint_index = node.get_joint()
        assert joint == node.joint

        match parts:
            case None:
                new_node = PMCA_cnl.NODE(node.joint, None, node.parent)

            case PMCA_asset.PARTS():
                if parts == node.parts:
                    return

                new_node = PMCA_cnl.NODE(
                    node.joint,
                    parts,
                    node.parent,
                )
                for joint in parts.joint:
                    assert joint.strip()
                    added = False
                    for child, _ in node.traverse():
                        if child.joint == joint:
                            child.parent = new_node
                            new_node.children.append(child)
                            added = True
                            break
                    if not added:
                        new_node.children.append(PMCA_cnl.NODE(joint, None, new_node))

            case "load":  # 外部モデル読み込み
                new_node = PMCA_cnl.NODE(node.joint, None, node.parent)

                # raise NotImplementedError()
                # path = tkinter.filedialog.askopenfilename(
                #     filetypes=[("Plygon Model Deta(for MMD)", ".pmd"), ("all", ".*")],
                #     defaultextension=".pmd",
                # )
                # if path != "":
                #     name = path.split("/")[-1]
                #     parts = PMCA_data.PARTS(name=name, path=path, props={})
                #     node = PMCA_data.NODE(
                #         parts=parts,
                #         depth=tree_node.node.depth + 1,
                #         children=[None for _ in parts.joint],
                #     )
                #     self.comment.set("comment:%s" % (node.parts.comment))
                # else:
                #     self.comment.set("comment:")
                #     node = None

        node.parent.children[joint_index] = new_node

        self.set_tree_model(new_node)

        for callback in self.data_updated:
            callback()


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
    def __init__(self, title: str, data: PMCA_asset.PMCAData, cnl: PMCA_cnl.CnlInfo):
        super().__init__()
        self.data = data
        self.cnl = cnl
        self.setWindowTitle(title)

        self.scene = GlScene()
        self.glwidget = glglue.pyside6.Widget(self, render_gl=self.scene.render)
        self.setCentralWidget(self.glwidget)

        self.model_tab = ModelTab(data, cnl)
        self.model_dock = QtWidgets.QDockWidget("Model", self)
        self.model_dock.setWidget(self.model_tab)
        self.addDockWidget(
            QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, self.model_dock
        )
        self.model_tab.data_updated.append(self.on_data_updated)
        self.on_data_updated()
        # self.addTab(self.model_tab, "Model")

        # self.color_tab = ColorTab()
        # self.addTab(self.color_tab, "Color")

        # self.transform_tab = TransformTab()
        # self.addTab(self.transform_tab, "Transform")

        # self.info_tab = InfoTab()
        # self.addTab(self.info_tab, "Info")

    def closeEvent(self, _) -> None:  # type: ignore
        self.scene.shutdown()

    def on_data_updated(self):
        native.refresh(self.data, self.cnl)
        data = PMCA.Get_PMD(0)
        if data:
            self.scene.set_model(PmdSrc(*data))
            self.glwidget.repaint()


class App:
    def __init__(self, title: str, data: PMCA_asset.PMCAData, cnl: PMCA_cnl.CnlInfo):
        self.app = QtWidgets.QApplication(sys.argv)
        self.window = MainWindow(title, data, cnl)
        self.window.show()

    def mainloop(self):
        self.app.exec()


def MainFrame(
    title: str,
    data: PMCA_asset.PMCAData,
    cnl: PMCA_cnl.CnlInfo,
) -> App:
    return App(title, data, cnl)
