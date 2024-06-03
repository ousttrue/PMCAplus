from typing import cast
from PySide6 import QtWidgets, QtCore
from .. import PMCA_asset
from ..app import App
import logging
from .generic_tree_model import GenericListModel


LOGGER = logging.getLogger(__name__)


class TransformTab(QtWidgets.QSplitter):
    def __init__(self, app: App):
        super().__init__(QtCore.Qt.Orientation.Horizontal)
        self.app = app

        # left
        self.tree = QtWidgets.QTreeView()
        self.addWidget(self.tree)
        left_model = GenericListModel(
            self.app.data.transform_list, ["transform"], lambda x, _: x.name
        )
        self.tree.setModel(left_model)
        self.tree.selectionModel().selectionChanged.connect(self.on_selected)

        # right
        self.list = QtWidgets.QTreeView()
        self.addWidget(self.list)

    def on_selected(
        self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection
    ) -> None:
        indexes = selected.indexes()
        if len(indexes) == 0:
            return
        item = cast(PMCA_asset.MODEL_TRANS_DATA, indexes[0].internalPointer())
        LOGGER.debug(item)

        # selected = cast(GenericListModel, self.tree.model())
        def get_col(item: PMCA_asset.BONE_TRANS_DATA, col: int) -> str:
            match col:
                case 0:
                    return item.name
                case 1:
                    return str(item.length)
                case 2:
                    return str(item.thick)
                case 3:
                    return str(item.pos)
                case 4:
                    return str(item.rot)
                case _:
                    raise NotImplementedError()

        right_model = GenericListModel(
            item.bones, ["bone", "length", "thick", "pos", "rot"], get_col
        )
        self.list.setModel(right_model)
