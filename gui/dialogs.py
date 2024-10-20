#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any
import PyPMCA
import tkinter
import PyPMCA.pmca_data as pmca_data


class SCALE_DIALOG_FANC(tkinter.Toplevel):
    def __init__(self, data: pmca_data.PmcaData, sel: int):
        super().__init__()
        self.data = data
        self.sel = sel
        self.title(self.data.assets.transform_list[self.sel].name)

        self.data.transform_data.append(
            PyPMCA.MODEL_TRANS_DATA(
                name=self.data.assets.transform_list[self.sel].name,
            )
        )
        self.transform_data = self.data.transform_data[-1]
        for x in self.data.assets.transform_list[self.sel].bones:
            self.transform_data.bones.append(PyPMCA.BONE_TRANS_DATA(name=x.name))

        t = data.assets.transform_list[sel]
        buff = ""
        for x in t.bones:
            buff += "%s %f %f\n" % (x.name, x.length, x.thick)
        tkinter.Label(self, text=buff).grid(row=0, padx=10, pady=5)

        self.frame1 = tkinter.Frame(self)
        self.tvar = tkinter.StringVar()
        self.tvar.set("%.3f" % t.default)
        self.spinbox = tkinter.Spinbox(
            self.frame1,
            from_=-100,
            to=100,
            increment=0.02,
            format="%.3f",
            textvariable=self.tvar,
            width=5,
            command=self.change_spinbox,
        )
        self.spinbox.pack(side="right", padx=5)
        self.spinbox.bind("<Return>", self.enter_spinbox)

        self.var = tkinter.DoubleVar()
        print(f"{t}")
        self.var.set(t.default)
        min_val, max_val = t.limit
        tkinter.Scale(
            self.frame1,
            orient="horizontal",
            from_=min_val,
            to=max_val,
            variable=self.var,
            length=256,
            command=self.change_scale,
            resolution=0.1,
        ).pack(side="left", padx=5)
        self.frame1.grid(row=1, padx=10, pady=5)

        self.frame2 = tkinter.Frame(self)
        tkinter.Button(self.frame2, text="OK", command=self.OK).pack(
            side="right", padx=5
        )
        tkinter.Button(self.frame2, text="Cancel", command=self.CANCEL).pack(
            side="left", padx=5
        )
        self.frame2.grid(row=2, sticky="e", padx=10, pady=5)

    def CANCEL(self):
        self.data.transform_data.remove(self.transform_data)
        self.data.refresh(level=2)
        self.winfo_toplevel().destroy()
        self.quit()

    def OK(self):
        self.data.transform_data[0].scale = (
            self.transform_data.scale * self.data.transform_data[0].scale
        )
        self.data.transform_data[0].pos += self.transform_data.pos
        self.data.transform_data[0].rot += self.transform_data.rot
        for x in self.transform_data.bones:
            tmp = None
            for y in self.data.transform_data[0].bones:
                if y.name == x.name:
                    tmp = y
                    break
            else:
                self.data.transform_data[0].bones.append(
                    PyPMCA.BONE_TRANS_DATA(name=x.name)
                )
                tmp = self.data.transform_data[0].bones[-1]

            tmp.length = tmp.length * x.length
            tmp.thick = tmp.thick * x.thick
            tmp.pos += x.pos
            tmp.rot += x.rot
        self.data.transform_data.remove(self.transform_data)
        self.data.refresh(level=2)
        # for x in self.app.transform_data[0].bones:
        #     print(x.name)

        self.winfo_toplevel().destroy()
        self.quit()

    def change_scale(self, _: Any):
        var = self.var.get()
        self.tvar.set("%.3f" % var)
        self.change_var(var)

    def change_spinbox(self):
        var = float(self.tvar.get())
        self.var.set(var)
        self.change_var(var)

    def enter_spinbox(self, _: Any):
        try:
            var = float(self.tvar.get())
        except:
            var = self.var.get()
            return None

        self.tvar.set("%.3f" % var)
        self.var.set(var)
        self.change_var(var)

    def change_var(self, var: float):
        weight = self.data.transform_list[self.sel].scale
        self.transform_data.scale = weight * var + 1 - weight

        weight = self.data.transform_list[self.sel].pos
        self.transform_data.pos = self.data.transform_list[self.sel].pos * var

        weight = self.data.transform_list[self.sel].rot
        self.transform_data.rot = weight * var

        for i, x in enumerate(self.data.transform_list[self.sel].bones):
            self.transform_data.bones[i].length = x.length * var + 1 - x.length
            self.transform_data.bones[i].thick = x.thick * var + 1 - x.thick
            self.transform_data.bones[i].pos = x.pos * var
            self.transform_data.bones[i].rot = x.rot * var
        self.data.refresh(level=2)


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
