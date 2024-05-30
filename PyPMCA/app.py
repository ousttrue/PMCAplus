import pathlib
from . import PMCA_asset
from . import PMCA_cnl
from . import native


class App:
    def __init__(self, asset_dir: pathlib.Path):
        # data
        self.data = PMCA_asset.PMCAData()
        list_txt = self.data.load_asset(asset_dir)
        if list_txt:
            native.set_list(*list_txt)

        def raise_refresh(c: PMCA_cnl.CnlInfo):
            native.refresh(self.data, c)

        self.cnl = PMCA_cnl.CnlInfo(raise_refresh)
        self.cnl_file = pathlib.Path()

    def load(self, cnl_file: pathlib.Path | None = None):
        if cnl_file:
            self.cnl_file = cnl_file
        else:
            cnl_file = self.cnl_file
        self.cnl.load_CNL_File(cnl_file, self.data)
        native.refresh(self.data, self.cnl)
