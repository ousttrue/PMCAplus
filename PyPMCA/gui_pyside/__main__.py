import logging
import pathlib

from ..color_logger import ColorfulHandler
from ..app import App
from . import main_frame as pyside_gui


APPNAME = "PMCA v0.0.6r10-pyside"


def main(dir: pathlib.Path, cnl_file: pathlib.Path):
    logging.basicConfig(handlers=[ColorfulHandler()], level=logging.DEBUG)

    app = App(dir, cnl_file)

    # gui
    window = pyside_gui.MainFrame(APPNAME, app)
    app.on_assemble.append(window.window.update_scene)
    app.assemble()

    window.mainloop()

    # model_info = app.get_info()
    # data.save_CNL_File(
    #     cnl_file, model_info.name, model_info.name_l, model_info.comment
    # )


if __name__ == "__main__":
    main(pathlib.Path(".").absolute(), cnl_file=pathlib.Path("./last.cnl"))
