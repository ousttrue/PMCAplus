import logging
import pathlib
from ..color_logger import ColorfulHandler
from . import main_frame as tkinter_gui
from ..app import App
import PMCA


APPNAME = "PMCA v0.0.6r10-tk"


def main(dir: pathlib.Path, cnl_file: pathlib.Path):
    logging.basicConfig(
        format="[%(levelname)s] %(name)s.%(funcName)s:%(lineno)d => %(message)s",
        handlers=[ColorfulHandler()],
        level=logging.DEBUG,
    )

    app = App(dir, cnl_file)

    # gui
    PMCA.Init_PMD()

    window = tkinter_gui.MainFrame(APPNAME, app)
    app.on_assemble.append(window.update_scene)
    app.assemble()
    window.mainloop()

    # model_info = app.get_info()
    # data.save_CNL_File(
    #     cnl_file, model_info.name, model_info.name_l, model_info.comment
    # )


if __name__ == "__main__":
    main(pathlib.Path(".").absolute(), pathlib.Path("./last.cnl"))
