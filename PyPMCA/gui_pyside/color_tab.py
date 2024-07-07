from typing import cast
import logging
from PySide6 import QtWidgets, QtCore
from .. import PMCA_asset
from .. import PMCA_cnl
from ..app import App
from .generic_tree_model import GenericListModel


LOGGER = logging.getLogger(__name__)


class ColorTab(QtWidgets.QSplitter):
    def __init__(self, app: App):
        super().__init__(QtCore.Qt.Orientation.Horizontal)
        self.app = app

        # left
        self.left = QtWidgets.QTreeView()
        self.addWidget(self.left)

        # right
        self.right = QtWidgets.QTreeView()
        self.addWidget(self.right)

        self.entries: list[PMCA_cnl.MAT_REP_DATA] = []

    def update_list(self):
        entries = self.app.cnl.mat_rep.get_entries()
        if entries == self.entries:
            return
        self.entries = entries

        list_model = GenericListModel(
            entries, [f"materials"], lambda item, col: str(item)
        )
        self.left.setModel(list_model)
        self.left.selectionModel().selectionChanged.connect(self.onLeftSelected)

        # if len(entries) > 0:
        #     self.left.selectionModel().setCurrentIndex(
        #         list_model.index_from_item(entries[0]),
        #         QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect,
        #     )

    def onLeftSelected(
        self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection
    ) -> None:
        indexes = selected.indexes()
        if len(indexes) == 0:
            return

        index = indexes[0]
        item = cast(PMCA_cnl.MAT_REP_DATA, index.internalPointer())
        # LOGGER.debug(item)

        list_model = GenericListModel(
            item.mat.entries, [f"entries"], lambda item, col: item.name
        )
        self.right.setModel(list_model)
        self.right.selectionModel().selectionChanged.connect(self.onRightSelected)

    def onRightSelected(
        self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection
    ) -> None:
        indexes = selected.indexes()
        if len(indexes) == 0:
            return
        index = indexes[0]
        item = cast(PMCA_asset.MATS_ENTRY, index.internalPointer())

        left_index = self.left.selectionModel().currentIndex()
        if not left_index.isValid():
            return
        left_item = cast(PMCA_cnl.MAT_REP_DATA, left_index.internalPointer())

        if left_item.sel == item:
            LOGGER.debug("already selected")
            return

        left_item.sel = item
        self.left.update(left_index)
        self.app.assemble()
