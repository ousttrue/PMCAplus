import dataclasses
import logging
from .. import PMCA_asset
from .. import pmd_type


LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class MAT_REP_DATA:
    """
    材質置換データ
    """

    mat: PMCA_asset.MATS
    sel: PMCA_asset.MATS_ENTRY

    def select_entry(self, sel: int) -> None:
        self.sel = self.mat.entries[sel]


class MAT_REP:
    """
    材質置換
    """

    def __init__(self):
        self.mat_map: dict[str, MAT_REP_DATA] = {}
        self.mat_order: list[str] = []
        self.toon = pmd_type.TOON()

    def get_material_entry(self, i: int) -> MAT_REP_DATA:
        return self.mat_map[self.mat_order[i]]

    def get_entries(self) -> list[str]:
        entries: list[str] = []

        # self.material_entries = ([], [])
        for i, tex in enumerate(self.mat_order):
            mat_rep = self.mat_map.get(tex)
            assert mat_rep
            LOGGER.debug(f"[{i}] {tex}: {mat_rep.mat.name} => {mat_rep.sel.name}")
            # self.material_entries[0].append(mat_rep.mat.name + "  " + mat_rep.sel.name)
            # self.material_entries[1].append(mat_rep.mat.name)
            entries.append(f"[{i}] {mat_rep.mat.name} => {mat_rep.sel.name}")

        return entries

    def list_to_text(self) -> list[str]:
        lines: list[str] = []

        for x in self.mat_map.values():
            lines.append("[Name] %s" % (x.mat.name))
            lines.append("[Sel] %s" % (x.sel.name))
            lines.append("NEXT")

        return lines

    @staticmethod
    def parse(
        lines: list[str], mat_list: list[PMCA_asset.MATS]
    ) -> tuple[list[str], dict[str, MAT_REP_DATA]]:
        LOGGER.info("parse material_rep")
        mat_rep: dict[str, MAT_REP_DATA] = {}

        name = ""
        sel_entry_name = ""
        while len(lines) > 0:
            l = lines.pop(0).strip()
            match l:
                case "NEXT":
                    material: PMCA_asset.MATS | None = None
                    for m in mat_list:
                        if m.name == name:
                            material = m
                            break
                    if material:
                        for e in material.entries:
                            if e.name == sel_entry_name:
                                mat_rep[name] = MAT_REP_DATA(material, e)
                                break
                case "TRANSFORM":
                    return lines, mat_rep
                case _:
                    k, v = l.split(" ")
                    match k:
                        case "[Name]":
                            name = v
                        case "[Sel]":
                            sel_entry_name = v
                        case _:
                            RuntimeError()

        raise RuntimeError()
