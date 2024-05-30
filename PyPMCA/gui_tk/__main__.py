import logging
import pathlib

from ..color_logger import ColorfulHandler
from .. import PMCA_asset
from .. import PMCA_cnl
from .. import native
from . import main_frame as tkinter_gui

APPNAME = "PMCA v0.0.6r10-tk"


def main(dir: pathlib.Path):
    logging.basicConfig(handlers=[ColorfulHandler()], level=logging.DEBUG)
    cnl_file = pathlib.Path("./last.cnl")

    # data
    data = PMCA_asset.PMCAData()
    list_txt = data.load_asset(dir)
    if list_txt:
        native.set_list(*list_txt)

    def raise_refresh(c: PMCA_cnl.CnlInfo):
        native.refresh(data, c)

    cnl = PMCA_cnl.CnlInfo(raise_refresh)
    cnl.load_CNL_File(cnl_file, data)

    # gui
    with native.Renderer() as r:
        app = tkinter_gui.MainFrame(APPNAME, data, cnl)
        cnl.on_reflesh.append(app.on_refresh)
        native.refresh(data, cnl)

        r.start_thread()

        app.mainloop()

        # model_info = app.get_info()
        # data.save_CNL_File(
        #     cnl_file, model_info.name, model_info.name_l, model_info.comment
        # )


if __name__ == "__main__":
    main(pathlib.Path(".").absolute())
