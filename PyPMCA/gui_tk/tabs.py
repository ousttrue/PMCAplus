from typing import Any
import tkinter.ttk
from .. import PMCA_asset
from .. import PMCA_cnl
from .model_tab import ModelTab
from .color_tab import ColorTab
from .transform_tab import TransformTab
from .info_tab import InfoTab, MODELINFO


class Tabs(tkinter.ttk.Notebook):
    def __init__(
        self,
        root: tkinter.Tk,
        data: PMCA_asset.PMCAData,
        cnl: PMCA_cnl.CnlInfo,
    ):
        super().__init__(root)

        self.data = data
        self.cnl = cnl

        self.model_tab = ModelTab(root, self.data, self.cnl)
        self._add_tab(self.model_tab)

        self.color_tab = ColorTab(root, self.cnl)
        self._add_tab(self.color_tab)

        self.transform_tab = TransformTab(root, self.data, self.cnl)
        self.transform_tab.tfgroup.set_entry([x.name for x in self.data.transform_list])  # type: ignore
        self._add_tab(self.transform_tab)

        self.info_tab = InfoTab(root)
        self._add_tab(self.info_tab)

    def _add_tab(self, x: Any) -> None:
        self.insert(tkinter.END, x, text=x.text)  # type: ignore

    def on_refresh(self) -> None:
        self.model_tab.set_tree(self.cnl.tree, True)
        if self.color_tab.cur_mat:
            self.color_tab.l_tree.set_entry(self.cnl.mat_rep.get_entries(), sel=self.color_tab.cur_mat)  # type: ignore
        else:
            self.color_tab.l_tree.set_entry(self.cnl.mat_rep.get_entries())
        self.info_tab.refresh()
        # self.transform_tab.info_frame.strvar.set(  # type: ignore
        #     "height     = %f\nwidth      = %f\nthickness = %f\n" % (w, h, t)
        # )

    def get_info(self) -> MODELINFO:
        return self.info_tab.modelinfo
