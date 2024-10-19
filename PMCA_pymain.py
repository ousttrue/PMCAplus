#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter
import gui
import pmca_data
import logging


LOGGER = logging.getLogger(__name__)
TITLE = "PMCA v0.0.6r10"


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


class ColorfulHandler(logging.StreamHandler):
    '''
    https://pod.hatenablog.com/entry/2020/03/01/221715
    '''
    def emit(self, record: logging.LogRecord) -> None:
        record.levelname = mapping[record.levelname]
        super().emit(record)


def main():
    logging.basicConfig(handlers=[ColorfulHandler()], level=logging.DEBUG)
    LOGGER.debug("start")

    data = pmca_data.PmcaData()
    app = gui.MainFrame(tkinter.Tk(), data)
    data.refresh(0)
    app.mainloop()
    data.shutdown()


if __name__ == "__main__":
    main()
