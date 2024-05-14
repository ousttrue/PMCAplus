import logging
import tkinter
import tkinter.ttk
from .listbox import LISTBOX
from .. import PMCA_asset
from .. import PMCA_cnl


LOGGER = logging.getLogger(__name__)


class Frame1(tkinter.Frame):
    def __init__(self, parent: "SCALE_DIALOG_FANC", t: PMCA_asset.MODEL_TRANS_DATA):
        super().__init__(parent)

        label = tkinter.Label(self, text=f"{t.scale_min} ~ {t.scale_max}")
        label.pack()
        self._make_spinbox(parent, t)
        self._make_slider(parent, t)

    def _make_spinbox(
        self, parent: "SCALE_DIALOG_FANC", t: PMCA_asset.MODEL_TRANS_DATA
    ) -> None:
        self.tvar = tkinter.StringVar()
        self.tvar.set("%.3f" % t.scale_default)

        def change_spinbox() -> None:
            var = float(self.tvar.get())
            self.var.set(var)
            parent.change_var(var)

        self.spinbox = tkinter.Spinbox(
            self,
            from_=-100,
            to=100,
            increment=0.02,
            format="%.3f",
            textvariable=self.tvar,
            width=5,
            command=change_spinbox,
        )
        self.spinbox.pack(side="right", padx=5)

        def enter_spinbox(event: tkinter.Event) -> None:  # type: ignore
            try:
                var = float(self.tvar.get())
            except:
                var = float(self.var.get())
                return None

            self.tvar.set("%.3f" % var)
            self.var.set(var)
            parent.change_var(var)

        self.spinbox.bind("<Return>", enter_spinbox)  # type: ignore

    def _make_slider(
        self, parent: "SCALE_DIALOG_FANC", t: PMCA_asset.MODEL_TRANS_DATA
    ) -> None:
        self.var = tkinter.DoubleVar()
        self.var.set(t.scale_default)

        def change_scale(event: str) -> None:
            var = float(self.var.get())
            self.tvar.set("%.3f" % var)
            parent.change_var(var)

        tkinter.Scale(
            self,
            orient="horizontal",
            from_=t.scale_min,
            to=t.scale_max,
            variable=self.var,
            length=256,
            command=change_scale,
            resolution=0.01,
        ).pack(side="left", padx=5)
        self.grid(row=1, padx=10, pady=5)


class SCALE_DIALOG_FANC(tkinter.Toplevel):
    def __init__(
        self,
        master: tkinter.Tk,
        data: PMCA_asset.PMCAData,
        sel: int,
        cnl: PMCA_cnl.CnlInfo,
    ):
        super().__init__()
        self.data = data
        self.cnl = cnl
        self.sel = sel
        self.title(data.transform_list[self.sel].name)

        self.cnl.transform_data.append(
            PMCA_asset.MODEL_TRANS_DATA(
                name=data.transform_list[self.sel].name,
                scale=1.0,
                bones=[],
                pos=(0.0, 0.0, 0.0),
                rot=(0.0, 0.0, 0.0),
            )
        )
        self.transform_data = self.cnl.transform_data[-1]
        for x in data.transform_list[self.sel].bones:
            self.transform_data.bones.append(PMCA_asset.BONE_TRANS_DATA(name=x.name))

        t = self.data.transform_list[self.sel]

        self.transient(master)
        # spinbox & slider
        self.frame1 = Frame1(self, t)
        # buttons
        self.frame2 = tkinter.Frame(self)

        buff = ""
        for x in self.data.transform_list[sel].bones:
            buff += "%s %f %f\n" % (x.name, x.length, x.thick)
        tkinter.Label(self, text=buff).grid(row=0, padx=10, pady=5)

        tkinter.Button(self.frame2, text="OK", command=self.OK).pack(
            side="right", padx=5
        )
        tkinter.Button(self.frame2, text="Cancel", command=self.CANCEL).pack(
            side="left", padx=5
        )
        self.frame2.grid(row=2, sticky="e", padx=10, pady=5)
        self.mainloop()

    def CANCEL(self):
        self.cnl.transform_data.remove(self.transform_data)
        self.cnl.raise_refresh()
        self.winfo_toplevel().destroy()
        self.quit()

    def OK(self):
        self.cnl.transform_data[0].scale = (
            self.transform_data.scale * self.cnl.transform_data[0].scale
        )
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

        self.winfo_toplevel().destroy()
        self.quit()

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

        def scale(
            v: tuple[float, float, float], var: float
        ) -> tuple[float, float, float]:
            x, y, z = v
            return (x * var, y * var, z * var)

        for i, bone in enumerate(self.data.transform_list[self.sel].bones):
            self.transform_data.bones[i].length = bone.length * var + 1 - bone.length
            self.transform_data.bones[i].thick = bone.thick * var + 1 - bone.thick
            self.transform_data.bones[i].pos = scale(bone.pos, var)
            self.transform_data.bones[i].rot = scale(bone.rot, var)
        self.cnl.raise_refresh()


class InfoFrame(tkinter.ttk.LabelFrame):
    def __init__(self, parent: tkinter.ttk.Frame):
        super().__init__(parent, text="Info")
        self.strvar = tkinter.StringVar()
        self.strvar.set("x=\ny=\nz=\n")
        self.label = tkinter.ttk.Label(self, textvariable=self.strvar).pack(
            side=tkinter.LEFT, anchor=tkinter.N
        )


class TransformTab(tkinter.ttk.Frame):
    def __init__(
        self, root: tkinter.Tk, data: PMCA_asset.PMCAData, cnl: PMCA_cnl.CnlInfo
    ) -> None:
        super().__init__(root)
        self.root = root
        self.text = "Transform"
        self.data = data
        self.cnl = cnl

        # left
        self.tfgroup_frame = tkinter.ttk.LabelFrame(self, text="Groups")
        self.tfgroup = LISTBOX(self.tfgroup_frame)
        # self.tfgroup.set_entry(tmp)
        self.tfgroup_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )
        self.tfgroup.bind("<ButtonRelease-1>", self.tf_click)  # type: ignore

        # right
        self.info_frame = InfoFrame(self)
        self.info_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )

    def tf_click(self, _: tkinter.Event) -> None:  # type: ignore
        sel = int(self.tfgroup.curselection()[0])  # type: ignore

        SCALE_DIALOG_FANC(self.root, self.data, sel, self.cnl)
