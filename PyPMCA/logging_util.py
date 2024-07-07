import logging


mapping = {
    "TRACE": " trace ",
    "DEBUG": "\x1b[0;36m debug \x1b[0m",
    "INFO": "\x1b[0;32m  info \x1b[0m",
    "WARNING": "\x1b[0;33m  warn \x1b[0m",
    "WARN": "\x1b[0;33m  warn \x1b[0m",
    "ERROR": "\x1b[0;31m error \x1b[0m",
    "ALERT": "\x1b[0;37;41m alert \x1b[0m",
    "CRITICAL": "\x1b[0;37;41m alert \x1b[0m",
}


# https://pod.hatenablog.com/entry/2020/03/01/221715
class ColorfulHandler(logging.StreamHandler):  # type: ignore
    def emit(self, record: logging.LogRecord) -> None:
        record.levelname = mapping[record.levelname]
        super().emit(record)


class DropByNames(logging.Filter):

    def __init__(self, *names: str) -> None:
        super().__init__()
        self.names = names

    def filter(self, record: logging.LogRecord) -> bool:
        for name in self.names:
            if record.name.startswith(name):
                return False
        return True


def basicConfig():
    logging.basicConfig(
        format="[%(levelname)s] %(name)s.%(funcName)s:%(lineno)d => %(message)s",
        handlers=[ColorfulHandler()],
        level=logging.DEBUG,
    )
    root_logger = logging.getLogger()
    root_logger.handlers[0].addFilter(DropByNames("PIL", "glglue"))
