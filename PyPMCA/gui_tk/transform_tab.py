from typing import Callable
import logging
import tkinter
import tkinter.ttk
from .listbox import LISTBOX
from .. import PMCA_asset
from ..app import App


LOGGER = logging.getLogger(__name__)


class SpinBoxAndSlider(tkinter.Frame):
    def __init__(
        self,
        parent: tkinter.Toplevel,
        change_var: Callable[[PMCA_asset.MODEL_TRANS_DATA, float], None],
        selected: PMCA_asset.MODEL_TRANS_DATA,
        transform_data: PMCA_asset.MODEL_TRANS_DATA,
    ):
        super().__init__(parent)

        label = tkinter.Label(self, text=f"{selected.scale_min} ~ {selected.scale_max}")
        label.pack()

        self.string_var = tkinter.StringVar()
        self.string_var.set("%.3f" % selected.scale_default)

        def change_spinbox() -> None:
            val = float(self.string_var.get())
            self.var.set(val)
            change_var(transform_data, val)

        self.spinbox = tkinter.Spinbox(
            self,
            from_=-100,
            to=100,
            increment=0.02,
            format="%.3f",
            textvariable=self.string_var,
            width=5,
            command=change_spinbox,
        )
        self.spinbox.pack(side="right", padx=5)

        def enter_spinbox(event: tkinter.Event) -> None:  # type: ignore
            try:
                val = float(self.string_var.get())
            except Exception:
                val = float(self.var.get())
                return None

            self.string_var.set("%.3f" % val)
            self.var.set(val)
            change_var(transform_data, val)

        self.spinbox.bind("<Return>", enter_spinbox)  # type: ignore

        self.var = tkinter.DoubleVar()
        self.var.set(selected.scale_default)

        def change_scale(event: str) -> None:
            val = float(self.var.get())
            self.string_var.set("%.3f" % val)
            change_var(transform_data, val)

        tkinter.Scale(
            self,
            orient="horizontal",
            from_=selected.scale_min,
            to=selected.scale_max,
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
        selected: PMCA_asset.MODEL_TRANS_DATA,
        on_ok: Callable[[PMCA_asset.MODEL_TRANS_DATA], None],
        on_cancel: Callable[[], None],
        change_var: Callable[[PMCA_asset.MODEL_TRANS_DATA, float], None],
    ):
        super().__init__()
        self.title(selected.name)
        transform_data = PMCA_asset.MODEL_TRANS_DATA(
            name=selected.name,
            scale=1.0,
            bones=[PMCA_asset.BONE_TRANS_DATA(name=x.name) for x in selected.bones],
            pos=(0.0, 0.0, 0.0),
            rot=(0.0, 0.0, 0.0),
        )

        self.transient(master)

        # spinbox & slider
        self.frame1 = SpinBoxAndSlider(self, change_var, selected, transform_data)

        # buttons
        self.frame2 = tkinter.Frame(self)

        tkinter.Label(
            self,
            text="".join(
                ["%s %f %f\n" % (x.name, x.length, x.thick) for x in selected.bones]
            ),
        ).grid(row=0, padx=10, pady=5)

        def OK():
            on_ok(transform_data)
            self.winfo_toplevel().destroy()
            self.quit()

        tkinter.Button(self.frame2, text="OK", command=OK).pack(side="right", padx=5)

        def CANCEL():
            on_cancel()
            self.winfo_toplevel().destroy()
            self.quit()

        tkinter.Button(self.frame2, text="Cancel", command=CANCEL).pack(
            side="left", padx=5
        )

        self.frame2.grid(row=2, sticky="e", padx=10, pady=5)
        self.mainloop()


class InfoFrame(tkinter.ttk.LabelFrame):
    def __init__(self, parent: tkinter.ttk.Frame):
        super().__init__(parent, text="Info")
        self.strvar = tkinter.StringVar()
        self.strvar.set("x=\ny=\nz=\n")
        self.label = tkinter.ttk.Label(self, textvariable=self.strvar).pack(
            side=tkinter.LEFT, anchor=tkinter.N
        )


class TransformTab(tkinter.ttk.Frame):
    def __init__(self, root: tkinter.Tk, app: App) -> None:
        super().__init__(root)
        self.root = root
        self.text = "Transform"
        self.app = app

        # left
        self.tfgroup_frame = tkinter.ttk.LabelFrame(self, text="Groups")
        self.tfgroup = LISTBOX(self.tfgroup_frame)
        self.tfgroup_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )
        self.tfgroup.bind("<ButtonRelease-1>", self.tf_click)  # type: ignore
        self.tfgroup.set_entry([x.name for x in self.app.data.transform_list])

        # right
        self.info_frame = InfoFrame(self)
        self.info_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )

    def tf_click(self, _: tkinter.Event) -> None:  # type: ignore
        sel = int(self.tfgroup.curselection()[0])  # type: ignore

        selected = self.app.data.transform_list[sel]

        def on_ok(transform_data: PMCA_asset.MODEL_TRANS_DATA):
            # update target
            target = self.app.cnl.transform_data_list[0]
            target.scale *= transform_data.scale
            for x in transform_data.bones:
                tmp = None
                for y in target.bones:
                    if y.name == x.name:
                        tmp = y
                        break
                else:
                    tmp = PMCA_asset.BONE_TRANS_DATA(name=x.name)
                    target.bones.append(tmp)
                tmp.length = tmp.length * x.length
                tmp.thick = tmp.thick * x.thick
                for i, y in enumerate(tmp.pos):
                    y += x.pos[i]
                for i, y in enumerate(tmp.rot):
                    y += x.rot[i]
            self.app.assemble()

        def on_cancel():
            self.app.assemble()

        def change_var(transform_data: PMCA_asset.MODEL_TRANS_DATA, var: float):
            weight = selected.scale
            transform_data.scale = weight * var + 1 - weight

            weight = selected.pos
            transform_data.pos = (
                weight[0] * var,
                weight[1] * var,
                weight[2] * var,
            )

            weight = selected.rot
            transform_data.rot = (
                weight[0] * var,
                weight[1] * var,
                weight[2] * var,
            )

            def scale(
                v: tuple[float, float, float], var: float
            ) -> tuple[float, float, float]:
                x, y, z = v
                return (x * var, y * var, z * var)

            for i, bone in enumerate(selected.bones):
                transform_data.bones[i].length = bone.length * var + 1 - bone.length
                transform_data.bones[i].thick = bone.thick * var + 1 - bone.thick
                transform_data.bones[i].pos = scale(bone.pos, var)
                transform_data.bones[i].rot = scale(bone.rot, var)

            self.app.assemble(transform_data)

        SCALE_DIALOG_FANC(self.root, selected, on_ok, on_cancel, change_var)
