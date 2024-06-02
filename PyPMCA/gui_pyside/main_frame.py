from typing import Callable, NamedTuple
import logging, pathlib, sys
from PySide6 import QtWidgets, QtCore
import glglue.pyside6
from ..gl_scene import GlScene
from ..app import App
from .. import PMCA_asset
from .. import PMCA_cnl
from .. import pmd_type
from .model_tab import ModelTab
from .color_tab import ColorTab
from .transform_tab import TransformTab


LOGGER = logging.getLogger(__name__)


class InfoTab(QtWidgets.QWidget):
    def __init__(self, data: PMCA_asset.PMCAData, cnl: PMCA_cnl.CnlInfo):
        super().__init__()
        pass


class FileFilter(NamedTuple):
    label: str
    ext: str  # ".cnl"


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, title: str, app: App):
        super().__init__()
        self.app = app

        self.setWindowTitle(title)
        self.resize(1280, 768)

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
        self.model_dock = self._add_dock(
            "Model", QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.model_tab
        )

        # color
        self.color_tab = ColorTab(self.app)
        self.color_dock = self._add_dock(
            "Color", QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.color_tab
        )

        # transform
        self.transform_tab = TransformTab(self.app)
        self.transform_dock = self._add_dock(
            "Transform",
            QtCore.Qt.DockWidgetArea.RightDockWidgetArea,
            self.transform_tab,
        )

        # info
        self.info_tab = InfoTab(self.app.data, self.app.cnl)
        self.info_dock = self._add_dock(
            "Info", QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, self.info_tab
        )

        self.model_dock.raise_()
        # self.glwidget.setFocus() # for mouse wheel

        # menu: files
        self.menu_file.addAction("新規(new cnl)", self.app.cnl_reload)  # type: ignore

        self.menu_file.addAction(  # type: ignore
            "読み込み(load cnl)",
            self._make_open_file_dialog(
                self.app.cnl_load, FileFilter("キャラクタノードリスト", ".cnl")
            ),
        )
        self.menu_file.addSeparator()
        self.menu_file.addAction(  # type: ignore
            "保存(save cnl)",
            self._make_save_file_dialog(
                self.app.cnl_save, FileFilter("キャラクタノードリスト", ".cnl")
            ),
        )

        self.menu_file.addAction(  # type: ignore
            "モデル保存(save pmd)",
            self._make_save_file_dialog(
                self.app.pmd_save, FileFilter("Plygon Model Deta(for MMD)", ".pmd")
            ),
        )
        self.menu_file.addSeparator()

        # cnl を連続で pmd 化する
        # names = filedialog.askopenfilename(
        #     filetypes=[("キャラクタノードリスト", ".cnl"), ("all", ".*")],
        #     initialdir=self.target_dir,
        #     defaultextension=".cnl",
        #     multiple=True,
        # )
        # files.add_command(label="一括組立て", underline=0, command=self.batch_assemble)
        # files.add_separator()

        # files.add_command(
        #     label="PMDフォーマットチェック",
        #     underline=0,
        #     command=self.app.pmd_format_check,
        # )
        # files.add_command(
        #     label="PMD概要確認",
        #     underline=0,
        #     command=self.app.pmd_overview_check,
        # )
        # files.add_command(
        #     label="PMD詳細確認",
        #     underline=0,
        #     command=self.app.pmd_property_check,
        # )
        # files.add_separator()

        # def quit():
        #     master.winfo_toplevel().destroy()
        #     master.quit()

        self.menu_file.addAction("exit", self.close)  # type: ignore

        # menu: editing
        self.menu_edit.addAction("体型調整を初期化", self.app.init_tf)  # type: ignore
        self.menu_edit.addAction("材質をランダム選択", self.app.rand_mat)  # type: ignore

    def _make_open_file_dialog(
        self, callback: Callable[[pathlib.Path], None], *filters: FileFilter
    ) -> Callable[[], None]:
        def func() -> None:
            raise NotImplementedError()
            pass

        return func

    def _make_save_file_dialog(
        self, callbck: Callable[[pathlib.Path], None], *filters: FileFilter
    ) -> Callable[[], None]:
        def func() -> None:
            raise NotImplementedError()
            pass

        return func

    def _add_dock(
        self, name: str, area: QtCore.Qt.DockWidgetArea, widget: QtWidgets.QWidget
    ) -> QtWidgets.QDockWidget:
        dock = QtWidgets.QDockWidget(name, self)
        dock.setWidget(widget)
        self.addDockWidget(area, dock)
        self.menu_dock.addAction(dock.toggleViewAction())  # type: ignore
        return dock

    def closeEvent(self, _) -> None:  # type: ignore
        self.scene.shutdown()

    def update_scene(self, data: bytes):
        pmd = pmd_type.parse(data)
        assert pmd
        self.scene.set_model(pmd, pathlib.Path("parts"))
        self.color_tab.update_list()
        self.glwidget.repaint()


class Gui:
    def __init__(self, title: str, app: App):
        self.gui = QtWidgets.QApplication(sys.argv)
        self.window = MainWindow(title, app)
        self.window.show()

    def mainloop(self):
        self.gui.exec()


def MainFrame(title: str, app: App) -> Gui:
    return Gui(title, app)


def run(name: str, app: App) -> None:
    window = MainFrame(name, app)
    app.on_assemble.append(window.window.update_scene)
    app.assemble()
    window.mainloop()
