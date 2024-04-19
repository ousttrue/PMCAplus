import tkinter
import PMCA
import logging
import pathlib
from main_frame import MainFrame
from PMCA_data import PMCAData


APPNAME = "PMCA v0.0.6r10"
COMMANDS = {}
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
class ColorfulHandler(logging.StreamHandler):
    def emit(self, record: logging.LogRecord) -> None:
        record.levelname = mapping[record.levelname]
        super().emit(record)


def main(dir: pathlib.Path):
    logging.basicConfig(handlers=[ColorfulHandler()], level=logging.DEBUG)

    # data
    data = PMCAData(dir)
    data.load()

    # gui
    PMCA.Init_PMD()
    root = tkinter.Tk()
    app = MainFrame(APPNAME, data, master=root)
    app.load_CNL_File("./last.cnl")

    PMCA.CretateViewerThread()

    app.refresh()
    app.mainloop()

    try:
        app.save_CNL_File("./last.cnl")
    except Exception as ex:
        LOGGER.error(ex)

    PMCA.QuitViewerThread()


if __name__ == "__main__":
    main(pathlib.Path(".").absolute())
