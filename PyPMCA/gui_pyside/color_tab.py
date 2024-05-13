from PySide6 import QtWidgets, QtCore
from .. import PMCA_asset
from .. import PMCA_cnl
from .generic_tree_model import GenericListModel


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

    def update_list(self):
        list_model = GenericListModel(
            self.cnl.mat_rep.get_entries(), [f"materials"], lambda item, col: item
        )
        self.left.setModel(list_model)
