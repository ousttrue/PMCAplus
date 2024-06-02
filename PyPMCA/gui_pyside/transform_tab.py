from PySide6 import QtWidgets, QtCore
from ..app import App
from .generic_tree_model import GenericListModel


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

        # right
        self.list = QtWidgets.QTreeView()
        self.addWidget(self.list)
