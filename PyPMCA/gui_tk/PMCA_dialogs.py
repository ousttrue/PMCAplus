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


class SCALE_DIALOG_FANC:
    def __init__(
        self, root: Toplevel, sel: int, data: PMCA_asset.PMCAData, cnl: PMCA_cnl.CnlInfo
    ):
        self.data = data
        self.cnl = cnl
        self.cnl = cnl
        self.root = root
        self.sel = sel
        self.root.title(data.transform_list[self.sel].name)
        self.var = None
        self.tvar = StringVar()
        self.refbone = []
        self.refbone_index = []

        self.cnl.transform_data.append(
            PMCA_asset.MODEL_TRANS_DATA(
                name=data.transform_list[self.sel].name,
                scale=1.0,
                bones=[],
                pos=(0.0, 0.0, 0.0),
                rot=(0.0, 0.0, 0.0),
                props={},
            )
        )
        self.transform_data = self.cnl.transform_data[-1]
        for x in data.transform_list[self.sel].bones:
            self.transform_data.bones.append(PMCA_asset.BONE_TRANS_DATA(name=x.name))

    def CANCEL(self):
        self.cnl.transform_data.remove(self.transform_data)
        self.cnl.raise_refresh()
        self.root.winfo_toplevel().destroy()
        self.root.quit()

    def OK(self):
        self.cnl.transform_data[0].scale = (
            self.transform_data.scale * self.cnl.transform_data[0].scale
        )
        # for i, x in enumerate(self.app.transform_data[0].pos):
        #     x += self.transform_data.pos[i]
        # for i, x in enumerate(self.app.transform_data[0].rot):
        #     x += self.transform_data.rot[i]
        for x in self.transform_data.bones:
            tmp = None
            for y in self.cnl.transform_data[0].bones:
                if y.name == x.name:
                    tmp = y
                    break
            else:
                self.cnl.transform_data[0].bones.append(
                    PMCA_asset.BONE_TRANS_DATA(name=x.name)
                )
                tmp = self.cnl.transform_data[0].bones[-1]

            tmp.length = tmp.length * x.length
            tmp.thick = tmp.thick * x.thick
            for i, y in enumerate(tmp.pos):
                y += x.pos[i]
            for i, y in enumerate(tmp.rot):
                y += x.rot[i]
        self.cnl.transform_data.remove(self.transform_data)
        self.cnl.raise_refresh()

        self.root.winfo_toplevel().destroy()
        self.root.quit()

    def change_scale(self, _):
        var = float(self.var.get())
        self.tvar.set("%.3f" % var)
        self.change_var(var)

    def change_spinbox(self):
        var = float(self.tvar.get())
        self.var.set(var)
        self.change_var(var)

    def enter_spinbox(self, event):
        try:
            var = float(self.tvar.get())
        except:
            var = float(self.var.get())
            return None

        self.tvar.set("%.3f" % var)
        self.var.set(var)
        self.change_var(var)

    def change_var(self, var: float):
        weight = self.data.transform_list[self.sel].scale
        self.transform_data.scale = weight * var + 1 - weight

        weight = self.data.transform_list[self.sel].pos
        self.transform_data.pos = (
            weight[0] * var,
            weight[1] * var,
            weight[2] * var,
        )

        weight = self.data.transform_list[self.sel].rot
        self.transform_data.rot = (
            weight[0] * var,
            weight[1] * var,
            weight[2] * var,
        )

        for i, x in enumerate(self.data.transform_list[self.sel].bones):
            self.transform_data.bones[i].length = x.length * var + 1 - x.length
            self.transform_data.bones[i].thick = x.thick * var + 1 - x.thick
            for j, y in enumerate(x.pos):
                self.transform_data.bones[i].pos[j] = y * var
            for j, y in enumerate(x.rot):
                self.transform_data.bones[i].rot[j] = y * var
        self.cnl.raise_refresh()


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
