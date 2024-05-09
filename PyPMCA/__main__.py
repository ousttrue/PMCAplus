import tkinter
import logging
import pathlib

from .gui.main_frame import MainFrame
from . import PMCA_data
from . import renderer


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
        renderer.set_list(*list_txt)

    cnl_info = data.load_CNL_File(cnl_file)

    # gui
    with renderer.Renderer() as r:
        root = tkinter.Tk()
        app = MainFrame(APPNAME, data, master=root)

        def on_refresh(w: float, h: float, t: float):
            app.model_tab.set_tree(data.tree, True)
            app.color_tab.l_tree.set_entry(data.mat_entry[0], sel=app.cur_mat)  # type: ignore
            app.info_tab.refresh()
            app.transform_tab.info_frame.strvar.set(  # type: ignore
                "height     = %f\nwidth      = %f\nthickness = %f\n" % (w, h, t)
            )

        data.on_reflesh.append(on_refresh)

        app.info_tab.set_info(*cnl_info)

        r.start_thread()
        renderer.refresh(data)

        app.mainloop()

        data.save_CNL_File(cnl_file)


if __name__ == "__main__":
    main(pathlib.Path(".").absolute())
