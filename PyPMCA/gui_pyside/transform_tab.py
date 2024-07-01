from typing import cast, Callable
from PySide6 import QtWidgets, QtCore
from .. import PMCA_asset
from ..app import App
import logging
from .generic_tree_model import GenericListModel


LOGGER = logging.getLogger(__name__)


class ListAndSlider(QtWidgets.QWidget):
    def __init__(self, on_value_changed: Callable[[int], None]):
        super().__init__()
        vbox = QtWidgets.QVBoxLayout()

        self.list = QtWidgets.QTreeView()
        vbox.addWidget(self.list, stretch=1)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)

        self.slider.setMinimum(-100)
        self.slider.setMaximum(+100)
        self.slider.setTickInterval(2)
        self.slider.setValue(0)  # set initial position
        self.slider.valueChanged.connect(on_value_changed)
        vbox.addWidget(self.slider)

        self.setLayout(vbox)


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
        self.right = ListAndSlider(self.on_value_changed)
        self.addWidget(self.right)

        self.item: PMCA_asset.MODEL_TRANS_DATA | None = None

    def on_selected(
        self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection
    ) -> None:
        indexes = selected.indexes()
        if len(indexes) == 0:
            return
        self.item = cast(PMCA_asset.MODEL_TRANS_DATA, indexes[0].internalPointer())

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
            self.item.bones, ["bone", "length", "thick", "pos", "rot"], get_col
        )
        self.right.list.setModel(right_model)

    def on_value_changed(self, var: int):
        if not self.item:
            return
        weight = self.item.scale
        self.transform_data.scale = weight * var + 1 - weight

        weight = self.app.data.transform_list[self.sel].pos
        self.transform_data.pos = (
            weight[0] * var,
            weight[1] * var,
            weight[2] * var,
        )

        weight = self.app.data.transform_list[self.sel].rot
        self.transform_data.rot = (
            weight[0] * var,
            weight[1] * var,
            weight[2] * var,
        )

        def scale(
            v: tuple[float, float, float], var: float
        ) -> tuple[float, float, float]:
            x, y, z = v
            return (x * var, y * var, z * var)

        for i, bone in enumerate(self.app.data.transform_list[self.sel].bones):
            self.transform_data.bones[i].length = bone.length * var + 1 - bone.length
            self.transform_data.bones[i].thick = bone.thick * var + 1 - bone.thick
            self.transform_data.bones[i].pos = scale(bone.pos, var)
            self.transform_data.bones[i].rot = scale(bone.rot, var)
        self.app.assemble()
