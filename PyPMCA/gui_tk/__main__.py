import logging
import pathlib

from ..color_logger import ColorfulHandler
from .. import native
from . import main_frame as tkinter_gui
from ..app import App


APPNAME = "PMCA v0.0.6r10-tk"


def main(dir: pathlib.Path, cnl_file: pathlib.Path):
    logging.basicConfig(handlers=[ColorfulHandler()], level=logging.DEBUG)

    app = App(dir)
    app.load(cnl_file)

    # gui
    with native.Renderer():
        window = tkinter_gui.MainFrame(APPNAME, app)
        app.cnl.on_reflesh.append(window.on_refresh)
        native.refresh(app.data, app.cnl)
        window.mainloop()

        # model_info = app.get_info()
        # data.save_CNL_File(
        #     cnl_file, model_info.name, model_info.name_l, model_info.comment
        # )


if __name__ == "__main__":
    main(pathlib.Path(".").absolute(), pathlib.Path("./last.cnl"))
