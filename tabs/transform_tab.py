from typing import Any
import tkinter.ttk
from .listbox import LISTBOX
import pmca_data


class TransformTab(tkinter.ttk.Frame):
    """
    +------+----+
    |groups|info|
    +------+----+
    """

    def __init__(self, master: tkinter.Misc, data: pmca_data.PmcaData):
        super().__init__(master=master)
        self.text = "Transform"

        self.tfgroup = LISTBOX(self, "Groups")
        self.tfgroup.listbox.bind("<ButtonRelease-1>", self.tf_click)
        tmp = []
        for x in data.transform_list:
            tmp.append(x.name)
        self.tfgroup.set_entry(tmp)

        self.info_frame = tkinter.ttk.LabelFrame(self, text="Info")
        self.info_str = tkinter.StringVar()
        self.info_str.set("x=\ny=\nz=\n")
        self.label = tkinter.ttk.Label(
            self.info_frame, textvariable=self.info_str
        ).pack(side=tkinter.LEFT, anchor=tkinter.N)
        self.info_frame.pack(
            padx=3, pady=3, side=tkinter.LEFT, fill=tkinter.BOTH, expand=1
        )

    def tf_click(self, _: Any):
        sel = int(self.tfgroup.listbox.curselection()[0])
        buff = ""
        print(sel)
        for x in self.transform_list:
            print(x.name, len(x.bones))

        for x in self.transform_list[sel].bones:
            buff += "%s %f %f\n" % (x.name, x.length, x.thick)
        print(buff)

        t = self.transform_list[sel]

        root = Toplevel()
        root.fancs = PMCA_dialogs.SCALE_DIALOG_FANC(self, root, sel)

        root.fancs.var = DoubleVar()
        root.fancs.var.set(t.default)
        root.fancs.tvar.set("%.3f" % t.default)

        root.transient(self)
        root.frame1 = Frame(root)
        root.frame2 = Frame(root)

        Label(root, text=buff).grid(row=0, padx=10, pady=5)

        root.frame1.spinbox = Spinbox(
            root.frame1,
            from_=-100,
            to=100,
            increment=0.02,
            format="%.3f",
            textvariable=root.fancs.tvar,
            width=5,
            command=root.fancs.change_spinbox,
        )
        root.frame1.spinbox.pack(side="right", padx=5)
        root.frame1.spinbox.bind("<Return>", root.fancs.enter_spinbox)

        Scale(
            root.frame1,
            orient="h",
            from_=t.limit[0],
            to=t.limit[1],
            variable=root.fancs.var,
            length=256,
            command=root.fancs.change_scale,
        ).pack(side="left", padx=5)
        root.frame1.grid(row=1, padx=10, pady=5)

        Button(root.frame2, text="OK", command=root.fancs.OK).pack(side="right", padx=5)
        Button(root.frame2, text="Cancel", command=root.fancs.CANCEL).pack(
            side="left", padx=5
        )
        root.frame2.grid(row=2, sticky="e", padx=10, pady=5)
        root.mainloop()
