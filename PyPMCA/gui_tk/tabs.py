from typing import Any
import tkinter.ttk
from .model_tab import ModelTab
from .color_tab import ColorTab
from .transform_tab import TransformTab
from .info_tab import InfoTab, MODELINFO
from ..app import App


class Tabs(tkinter.ttk.Notebook):
    def __init__(
        self,
        root: tkinter.Tk,
        app: App,
    ):
        super().__init__(root)

        self.app = app

        self.model_tab = ModelTab(root, self.app)
        self._add_tab(self.model_tab)

        self.color_tab = ColorTab(root, self.app.cnl)
        self._add_tab(self.color_tab)

        self.transform_tab = TransformTab(root, self.app.data, self.app.cnl)
        self.transform_tab.tfgroup.set_entry([x.name for x in self.app.data.transform_list])  # type: ignore
        self._add_tab(self.transform_tab)

        self.info_tab = InfoTab(root)
        self._add_tab(self.info_tab)

    def _add_tab(self, x: Any) -> None:
        self.insert(tkinter.END, x, text=x.text)  # type: ignore

    def on_refresh(self) -> None:
        self.model_tab.set_tree(self.app.cnl.tree, True)
        if self.color_tab.cur_mat:
            self.color_tab.l_tree.set_entry(self.app.cnl.mat_rep.get_entries(), sel=self.color_tab.sel_t)  # type: ignore
        else:
            self.color_tab.l_tree.set_entry(self.app.cnl.mat_rep.get_entries())
        self.info_tab.refresh()
        # self.transform_tab.info_frame.strvar.set(  # type: ignore
        #     "height     = %f\nwidth      = %f\nthickness = %f\n" % (w, h, t)
        # )

    def get_info(self) -> MODELINFO:
        return self.info_tab.modelinfo
