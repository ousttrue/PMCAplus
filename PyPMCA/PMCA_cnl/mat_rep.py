import dataclasses
from .. import PMCA_asset
from .. import pmd_type


@dataclasses.dataclass
class MAT_REP_DATA:
    """
    材質置換データ
    """

    num: int
    mat: PMCA_asset.MATS
    sel: PMCA_asset.MATS_ENTRY | None = None


class MAT_REP:
    """
    材質置換
    """

    def __init__(self):
        self.mat: dict[str, MAT_REP_DATA] = {}
        self.toon = pmd_type.TOON()

    def list_to_text(self) -> list[str]:
        lines: list[str] = []

        for x in self.mat.values():
            lines.append("[Name] %s" % (x.mat.name))
            lines.append("[Sel] %s" % (x.sel.name))
            lines.append("NEXT")

        return lines
