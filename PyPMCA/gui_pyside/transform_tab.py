from typing import cast
from PySide6 import QtWidgets, QtCore
from .. import PMCA_asset
from ..app import App
import logging
from .generic_tree_model import GenericListModel


LOGGER = logging.getLogger(__name__)


class ListAndSlider(QtWidgets.QWidget):
    def __init__(self, app: App):
        super().__init__()
        self.app = app
        vbox = QtWidgets.QVBoxLayout()

        # top
        self.list = QtWidgets.QTreeView()
        vbox.addWidget(self.list, stretch=1)

        # mid
        hbox = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel("min ~ max")
        hbox.addWidget(self.label)
        # self.spinbox = QtWidgets.QSpinBox()
        # hbox.addWidget(self.spinbox)
        vbox.addLayout(hbox)

        # bottom
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.slider.setMinimum(-100)
        self.slider.setMaximum(+100)
        self.slider.setTickInterval(2)
        self.slider.setValue(0)  # set initial position
        self.slider.valueChanged.connect(self.on_value_changed)
        vbox.addWidget(self.slider)

        self.setLayout(vbox)

        self.item = self.app.data.transform_list[0]

    def set_data(self, data: PMCA_asset.MODEL_TRANS_DATA):
        self.item = data

        self.label.setText(f"{data.scale_min} ~ {data.scale_max}")

        # def int_from_float(data: PMCA_asset.MODEL_TRANS_DATA) -> int:
        #     return (
        #         200
        #         * int(
        #             (data.scale_default - data.scale_min)
        #             / (data.scale_max - data.scale_min)
        #         )
        #         - 100
        #     )
        # self.spinbox.setValue(int_from_float(data))

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
            data.bones, ["bone", "length", "thick", "pos", "rot"], get_col
        )
        self.list.setModel(right_model)

    def float_from_int(self, n: int) -> float:
        assert self.item
        min_val = float(self.item.scale_min)
        max_val = float(self.item.scale_max)
        f = float(n + 50) / 200.0
        return min_val + (max_val - min_val) * f

    def on_value_changed(self, var: int):
        if not self.item:
            return

        val = self.float_from_int(var)
        self.app.assemble(self.item.make_scaled(val))


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
        self.right = ListAndSlider(app)
        self.addWidget(self.right)

        # select
        self.tree.selectionModel().setCurrentIndex(
            left_model.createIndex(0, 0, app.data.transform_list[0]),
            QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )

    def on_selected(
        self, selected: QtCore.QItemSelection, _: QtCore.QItemSelection
    ) -> None:
        indexes = selected.indexes()
        if len(indexes) == 0:
            return
        item = cast(PMCA_asset.MODEL_TRANS_DATA, indexes[0].internalPointer())

        self.right.set_data(item)
