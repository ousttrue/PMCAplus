from typing import Callable, cast
import logging
from PySide6 import QtWidgets, QtCore
from .generic_tree_model import GenericTreeModel
from .. import PMCA_asset
from .. import PMCA_cnl


LOGGER = logging.getLogger(__name__)


class PmcaNodeModel(GenericTreeModel[PMCA_cnl.NODE]):
    def __init__(self, root: PMCA_cnl.NODE) -> None:
        def get_col(node: PMCA_cnl.NODE, col: int) -> str:
            match col:
                case 0:
                    # joint
                    if node.parent:
                        return node.parent.joint
                    else:
                        return "no_parent"
                case 1:
                    # parts
                    if node.parts:
                        return node.parts.name
                    else:
                        return ""
                case _:
                    raise RuntimeError()

        super().__init__(
            root,
            ["joint", "parts"],
            lambda x: x.parent.node if x.parent else None,
            lambda x: len(x.children),
            lambda x, row: x.children[row],
            get_col,
        )


class PartsListModel(GenericTreeModel[PMCA_asset.PARTS | None]):
    def __init__(self, header: str, parts_list: list[PMCA_asset.PARTS]) -> None:
        super().__init__(
            None,
            [header],
            lambda x: None,
            lambda x: 0 if x else len(parts_list),
            lambda x, row: parts_list[row],
            lambda x, col: x.name if x else "None",
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
        assert item.parent

        parts = [
            parts for parts in self.data.parts_list if item.parent.joint in parts.type
        ]
        list_model = PartsListModel(f"[{item.parent.joint}] parts", parts)
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
        parts = cast(PMCA_asset.PARTS | None, parts_index.internalPointer())

        tree_index = self.tree.selectionModel().currentIndex()
        if not tree_index.isValid():
            return
        node = cast(PMCA_cnl.NODE, tree_index.internalPointer())

        assert node.parent
        LOGGER.debug(
            f"{node},{node.parent.joint_index} / {len(node.parent.node.children)}"
        )

        match parts:
            case None:
                new_node = PMCA_cnl.NODE(node.parent, None)

            case PMCA_asset.PARTS():
                if parts == node.parts:
                    return

                new_node = PMCA_cnl.NODE(
                    node.parent,
                    parts,
                )
                used: list[PMCA_cnl.NODE] = []
                for i, joint in enumerate(parts.joint):
                    assert joint.strip()
                    for child, _ in node.traverse():
                        assert child.parent
                        if child.parent.joint == joint and child not in used:
                            new_node.connect(i, child)
                            used.append(child)
                            break

            case "load":  # 外部モデル読み込み
                new_node = PMCA_cnl.NODE(node.parent, None)

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

        node.parent.node.children[node.parent.joint_index] = new_node

        self.set_tree_model(new_node)

        for callback in self.data_updated:
            callback()
