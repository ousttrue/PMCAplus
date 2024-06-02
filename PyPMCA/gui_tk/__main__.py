import logging
import pathlib
from ..color_logger import ColorfulHandler
from . import main_frame as tkinter_gui
from ..app import App


APPNAME = "PMCA v0.0.6r10-tk"


def main(dir: pathlib.Path, cnl_file: pathlib.Path):
    logging.basicConfig(
        format="[%(levelname)s] %(name)s.%(funcName)s:%(lineno)d => %(message)s",
        handlers=[ColorfulHandler()],
        level=logging.DEBUG,
    )

    root_logger = logging.getLogger()
    # module_log_pass_filter = logging.Filter(__name__)

    class DropByNames(logging.Filter):

        def __init__(self, *names: str) -> None:
            super().__init__()
            self.names = names

        def filter(self, record: logging.LogRecord) -> bool:
            for name in self.names:
                if record.name.startswith(name):
                    return False
            return True

    # root_logger.addFilter(module_log_pass_filter)
    root_logger.handlers[0].addFilter(DropByNames("PIL", "glglue"))

    app = App(dir, cnl_file)

    # gui
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
