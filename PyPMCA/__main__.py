from typing import Any
import tkinter
import logging
import pathlib
import PMCA  # type: ignore

from .gui.main_frame import MainFrame
from .PMCA_data import PMCAData

APPNAME = "PMCA v0.0.6r10"
# COMMANDS = {}
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


class PmcaView:
    def __init__(self):
        PMCA.Init_PMD()

    def __enter__(self):
        return self

    def __exit__(self, _exception_type: Any, _exception_value: Any, _traceback: Any):
        PMCA.QuitViewerThread()

    def start_thread(self):
        PMCA.CretateViewerThread()


def main(dir: pathlib.Path):
    logging.basicConfig(handlers=[ColorfulHandler()], level=logging.DEBUG)

    # data
    data = PMCAData()
    data.load(dir)

    cnl_file = pathlib.Path("./last.cnl")

    # gui
    with PmcaView() as view:
        root = tkinter.Tk()
        app = MainFrame(APPNAME, data, master=root)
        app.load_CNL_File(cnl_file)

        view.start_thread()

        app.refresh()
        app.mainloop()

        try:
            data.save_CNL_File(cnl_file)
        except Exception as ex:
            LOGGER.error(ex)


if __name__ == "__main__":
    main(pathlib.Path(".").absolute())
