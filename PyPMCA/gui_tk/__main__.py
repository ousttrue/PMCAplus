import pathlib
from .. import logging_util
from ..app import App
from . import main_frame as tkinter_gui


APPNAME = "PMCA v0.0.6r10-tkinter"


def main(dir: pathlib.Path, cnl_file: pathlib.Path):
    logging_util.basicConfig()

    app = App(dir, cnl_file)

    tkinter_gui.run(APPNAME, app)

    # auto save
    app.cnl_save()


if __name__ == "__main__":
    main(pathlib.Path(".").absolute(), pathlib.Path("./last.cnl"))
