#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

sys.argv = [""]
import os

# インポートパスにカレントディレクトリを加える
sys.path.append(os.getcwd())

import PyPMCA

from tkinter import *
from tkinter.ttk import *
from .. import PMCA_asset
from .. import PMCA_cnl


class QUIT:
    def __init__(self, root):
        self.root = root

    def __call__(self):
        self.root.winfo_toplevel().destroy()
        self.root.quit()




class SETTING_DIALOG_FANC:
    def __init__(self, app, root):
        self.app = app
        self.root = root
        self.root.title("PMCA設定")

        self.flag_export2folder = BooleanVar()
        self.flag_export2folder.set(app.settings.export2folder)

    def apply_all(self):
        self.app.settings.export2folder = self.flag_export2folder.get()

    def OK(self):
        self.root.winfo_toplevel().destroy()
        self.root.quit()
