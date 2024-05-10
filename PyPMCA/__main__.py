import logging
import pathlib

from .pyside_gui import main_frame as pyside_gui
from .gui import main_frame as tkinter_gui
from . import PMCA_data
from . import native


APPNAME = "PMCA v0.0.6r10-mod"
HERE = pathlib.Path(__file__).parent
LOGGER = logging.getLogger(__name__)


mapping = {
    "TRACE": "[ trace ]",
    "DEBUG": "[ \x1b[0;36mdebug\x1b[0m ]",
    "INFO": "[  \x1b[0;32minfo\x1b[0m ]",
    "WARNING": "[  \x1b[0;33mwarn\x1b[0m ]",
    "WARN": "[  \x1b[0;33mwarn\x1b[0m ]",
    "ERROR": "\x1b[0;31m[ error ]\x1b[0m",
    "ALERT": "\x1b[0;37;41m[ alert ]\x1b[0m",
    "CRITICAL": "\x1b[0;37;41m[ alert ]\x1b[0m",
}


# https://pod.hatenablog.com/entry/2020/03/01/221715
class ColorfulHandler(logging.StreamHandler):  # type: ignore
    def emit(self, record: logging.LogRecord) -> None:
        record.levelname = mapping[record.levelname]
        super().emit(record)


def main(dir: pathlib.Path):
    logging.basicConfig(handlers=[ColorfulHandler()], level=logging.DEBUG)
    cnl_file = pathlib.Path("./last.cnl")

    # data
    data = PMCA_data.PMCAData()
    list_txt = data.load_asset(dir)
    if list_txt:
        native.set_list(*list_txt)

    cnl_info = data.load_CNL_File(cnl_file)

    # gui
    with native.Renderer():
        if False:
            app = tkinter_gui.MainFrame(APPNAME, data, *cnl_info)
        else:
            app = pyside_gui.MainFrame(APPNAME, data, *cnl_info)

        data.on_reflesh.append(app.on_refresh)

        # r.start_thread()
        native.refresh(data)

        app.mainloop()

        model_info = app.get_info()
        data.save_CNL_File(
            cnl_file, model_info.name, model_info.name_l, model_info.comment
        )


if __name__ == "__main__":
    main(pathlib.Path(".").absolute())
