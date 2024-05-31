import logging
import pathlib

from ..color_logger import ColorfulHandler
from ..app import App
import PMCA
from .. import PMCA_asset
from .. import PMCA_cnl
from .. import native
from . import main_frame as pyside_gui


APPNAME = "PMCA v0.0.6r10-pyside"


def main(dir: pathlib.Path, cnl_file: pathlib.Path):
    logging.basicConfig(handlers=[ColorfulHandler()], level=logging.DEBUG)

    app = App(dir)
    app.cnl_load(cnl_file)

    # gui
    PMCA.Init_PMD()

    # def raise_refresh(c: PMCA_cnl.CnlInfo):
    #     native.refresh(data, c)

    # gui
    window = pyside_gui.MainFrame(APPNAME, app)
    app.on_assemble.append(window.update_scene)
    app.assemble()

    window.mainloop()

    # model_info = app.get_info()
    # data.save_CNL_File(
    #     cnl_file, model_info.name, model_info.name_l, model_info.comment
    # )


if __name__ == "__main__":
    main(pathlib.Path(".").absolute(), cnl_file=pathlib.Path("./last.cnl"))
