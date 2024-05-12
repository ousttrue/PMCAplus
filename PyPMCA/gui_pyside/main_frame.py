import logging
import sys
from PySide6 import QtWidgets, QtCore
from .. import PMCA_asset
from .. import PMCA_cnl
from .. import native
import PMCA  # type: ignore
import glglue.pyside6
from .gl_scene import GlScene, PmdSrc
from .model_tab import ModelTab


LOGGER = logging.getLogger(__name__)


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
