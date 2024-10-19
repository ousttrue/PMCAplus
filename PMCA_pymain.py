#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter
import gui
import pmca_data


TITLE = "PMCA v0.0.6r10"


def main():
    data = pmca_data.PmcaData()
    app = gui.MainFrame(tkinter.Tk(), data)
    data.refresh(0)
    app.mainloop()
    data.shutdown()


if __name__ == "__main__":
    main()
