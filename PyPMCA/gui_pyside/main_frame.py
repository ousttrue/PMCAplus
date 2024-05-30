import logging
import sys
from PySide6 import QtWidgets, QtCore
from ..app import App
from .. import PMCA_asset
from .. import PMCA_cnl
import PMCA  # type: ignore
import glglue.pyside6
from ..gl_scene import GlScene, PmdSrc
from .model_tab import ModelTab
from .color_tab import ColorTab


LOGGER = logging.getLogger(__name__)


class TransformTab(QtWidgets.QWidget):
    def __init__(self, data: PMCA_asset.PMCAData, cnl: PMCA_cnl.CnlInfo):
        super().__init__()
        pass


class InfoTab(QtWidgets.QWidget):
    def __init__(self, data: PMCA_asset.PMCAData, cnl: PMCA_cnl.CnlInfo):
        super().__init__()
        pass


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, title: str, app: App):
        super().__init__()
        self.app = app

        self.setWindowTitle(title)
        self.resize(800, 800)

        self.scene = GlScene()
        self.glwidget = glglue.pyside6.Widget(self, render_gl=self.scene.render)
        self.setCentralWidget(self.glwidget)

        ## menu
        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu("File")
        self.menu_edit = self.menu.addMenu("Edit")
        self.menu_dock = self.menu.addMenu("Dock")

        ## tabs
        # model
        self.model_tab = ModelTab(self.app)
        self.model_dock = self._add_dock("Model", self.model_tab)

        # color
        self.color_tab = ColorTab(self.app.data, self.app.cnl)
        self.color_dock = self._add_dock("Color", self.color_tab)
        self.tabifyDockWidget(self.model_dock, self.color_dock)

        # transform
        self.transform_tab = TransformTab(self.app.data, self.app.cnl)
        self.transform_dock = self._add_dock("Transform", self.transform_tab)
        self.tabifyDockWidget(self.model_dock, self.transform_dock)

        # info
        self.info_tab = InfoTab(self.app.data, self.app.cnl)
        self.info_dock = self._add_dock("Info", self.info_tab)
        self.tabifyDockWidget(self.model_dock, self.info_dock)

        self.model_dock.raise_()

    def _add_dock(self, name: str, widget: QtWidgets.QWidget) -> QtWidgets.QDockWidget:
        dock = QtWidgets.QDockWidget(name, self)
        dock.setWidget(widget)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        self.menu_dock.addAction(dock.toggleViewAction())  # type: ignore

        return dock

    def closeEvent(self, _) -> None:  # type: ignore
        self.scene.shutdown()

    def on_refresh(self):
        data = PMCA.Get_PMD(0)
        if data:
            self.scene.set_model(PmdSrc(*data))
            self.color_tab.update_list()
            self.glwidget.repaint()


class Gui:
    def __init__(self, title: str, app: App):
        self.gui = QtWidgets.QApplication(sys.argv)
        self.window = MainWindow(title, app)
        self.window.show()

    def mainloop(self):
        self.gui.exec()

    def update_scene(self):
        self.window.on_refresh()


def MainFrame(title: str, app: App) -> Gui:
    return Gui(title, app)
