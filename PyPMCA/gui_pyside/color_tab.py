from typing import cast
import logging
from PySide6 import QtWidgets, QtCore
from .. import PMCA_asset
from .. import PMCA_cnl
from .generic_tree_model import GenericListModel


LOGGER = logging.getLogger(__name__)


class ColorTab(QtWidgets.QWidget):
    def __init__(self, data: PMCA_asset.PMCAData, cnl: PMCA_cnl.CnlInfo):
        super().__init__()
        self.data = data
        self.cnl = cnl

        vbox = QtWidgets.QVBoxLayout()
        self.setLayout(vbox)

        hbox = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, self)
        vbox.addWidget(hbox, stretch=2)

        # left
        self.left = QtWidgets.QTreeView()
        hbox.addWidget(self.left)

        # right
        self.right = QtWidgets.QTreeView()
        hbox.addWidget(self.right)

        # bottom
        self.comment = QtWidgets.QLabel()
        self.comment.setText("comment:")
        vbox.addWidget(self.comment)

        self.entries: list[PMCA_cnl.MAT_REP_DATA] = []

    def update_list(self):
        entries = self.cnl.mat_rep.get_entries()
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
        self.cnl.raise_refresh()
