import logging
import pathlib

from ..color_logger import ColorfulHandler
from .. import PMCA_asset
from .. import PMCA_cnl
from .. import native
from . import main_frame as pyside_gui


APPNAME = "PMCA v0.0.6r10-pyside"


def main(dir: pathlib.Path):
    logging.basicConfig(handlers=[ColorfulHandler()], level=logging.DEBUG)
    cnl_file = pathlib.Path("./last.cnl")

    # data
    data = PMCA_asset.PMCAData()
    list_txt = data.load_asset(dir)
    if list_txt:
        native.set_list(*list_txt)

    cnl = PMCA_cnl.CnlInfo()
    cnl.load_CNL_File(cnl_file, data)

    # gui
    with native.Renderer():
        app = pyside_gui.MainFrame(APPNAME, data, cnl)

        app.mainloop()

        # model_info = app.get_info()
        # data.save_CNL_File(
        #     cnl_file, model_info.name, model_info.name_l, model_info.comment
        # )


if __name__ == "__main__":
    main(pathlib.Path(".").absolute())