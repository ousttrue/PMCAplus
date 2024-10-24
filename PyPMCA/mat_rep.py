import dataclasses
import logging
import PMCA_ctypes as PMCA
import ctypes
from . import types
from . import material
from . import author_license

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class MAT_REP_DATA:
    mat: material.MATS
    num: int = -1
    sel: material.MATS_ENTRY | None = None

    def select(self, sel: int) -> None:
        self.sel = self.mat.entries[sel]


@dataclasses.dataclass
class MAT_REP:
    mat: dict[str, MAT_REP_DATA] = dataclasses.field(default_factory=dict)
    toon: types.TOON = dataclasses.field(default_factory=types.TOON)

    def load(self, lines: list[str], mat_list: list[material.MATS]) -> None:
        self.mat = {}
        i = 0
        while lines[i] != "MATERIAL":
            # print(lines[i])
            i += 1
        i += 1
        tmp = ["", "", None]
        for x in lines[i:]:
            x = x.split(" ")
            if x[0] == "[Name]":
                tmp[0] = x[1]
            elif x[0] == "[Sel]":
                tmp[1] = x[1]
            elif x[0] == "NEXT":
                for y in mat_list:
                    if y.name == tmp[0]:
                        tmp[2] = y
                        break
                else:
                    tmp[2] = None
                    continue

                for y in tmp[2].entries:
                    if y.name == tmp[1]:
                        self.mat[tmp[0]] = MAT_REP_DATA(num=-1, mat=tmp[2], sel=y)
                        break

    def Get(
        self,
        mats_list: list[material.MATS],
        model: types.PMD | None = None,
        info: types.INFO | None = None,
        num: int = 0,
    ):
        materials: list[types.MATERIAL] = []
        if model == None:
            if info == None:
                info_data = PMCA.getInfo(num)
                info = types.INFO.create(info_data)
            for i in range(info.mat_count):
                tmp = PMCA.getMat(num, i)
                materials.append(types.MATERIAL.create(**tmp))
        else:
            info = model.info
            materials = model.mat

        for x in self.mat.values():
            x.num = -1

        assert info
        for i, mat in enumerate(materials):
            for x in mats_list:
                if mat.tex == x.name and x.name != "":
                    if self.mat.get(mat.tex) == None:
                        self.mat[mat.tex] = MAT_REP_DATA(mat=x, num=i)
                    else:
                        self.mat[mat.tex].num = i

                    if self.mat[mat.tex].sel == None:
                        self.mat[mat.tex].sel = self.mat[mat.tex].mat.entries[0]

    def Set(
        self,
        author_license: author_license.AuthorLicense,
        model: types.PMD | None = None,
        info: types.INFO | None = None,
        num: int = 0,
    ):
        mat: list[types.MATERIAL] = []
        if model == None:
            if info == None:
                info_data = PMCA.getInfo(num)
                info = types.INFO.create(info_data)
            for i in range(info.mat_count):
                tmp = PMCA.getMat(num, i)
                mat.append(types.MATERIAL.create(**tmp))
        else:
            info = model.info
            mat = model.mat

        for i, x in enumerate(mat):
            if self.mat.get(x.tex) != None:
                rep = self.mat[x.tex].sel
                for k, v in rep.props.items():
                    if k == "tex":
                        x.tex = v
                    elif k == "tex_path":
                        x.tex_path = v
                    elif k == "sph":
                        x.sph = v
                    elif k == "sph_path":
                        x.sph_path = v
                    elif k == "diff_rgb":
                        x.diff_col = v
                        for j, y in enumerate(x.diff_col):
                            x.diff_col[j] = float(y)
                    elif k == "alpha":
                        x.alpha = float(v)
                    elif k == "spec_rgb":
                        # print(x.spec_col)
                        x.spec_col = v
                        for j, y in enumerate(x.spec_col):
                            x.spec_col[j] = float(y)
                    elif k == "mirr_rgb":
                        x.mirr_col = v
                        for j, y in enumerate(x.mirr_col):
                            x.mirr_col[j] = float(y)

                    elif k == "toon":
                        _toon = (ctypes.c_char_p * 10)()
                        PMCA.getToonPath(num, _toon)
                        _toon_path = (ctypes.c_char_p * 10)()
                        PMCA.getToon(num, _toon_path)

                        toon_name = [ctypes.string_at(p) for p in _toon]
                        toon_path = [ctypes.string_at(p) for p in _toon_path]

                        # print("toon")
                        # print(toon.name)
                        # print(toon.path)
                        _index, name = v[-1].split(" ")
                        index = int(_index)
                        toon_path[index] = ("toon/" + name).encode("cp932", "replace")
                        toon_name[index] = name.encode("cp932", "replace")

                        # print(toon.name)
                        # print(toon.path)

                        PMCA.setToon(num, (ctypes.c_char_p * 10)(*toon_name))
                        PMCA.setToonPath(num, (ctypes.c_char_p * 10)(*toon_path))
                        x.toon = index
                        # print(tmp)
                    elif k == "author":
                        for y in v[-1].split(" "):
                            author_license.append_author(y)
                    elif k == "license":
                        for y in v[-1].split(" "):
                            author_license.append_license(y)

                # print(x.diff_col)
                # print(x.spec_col)
                PMCA.setMat(
                    num,
                    i,
                    x.diff_col,
                    x.alpha,
                    x.spec,
                    x.spec_col,
                    x.mirr_col,
                    x.toon,
                    x.edge,
                    x.face_count,
                    x.tex,
                    x.sph,
                    x.tex_path,
                    x.sph_path,
                )

    def list_to_text(self):
        lines = []

        for x in self.mat.values():
            lines.append("[Name] %s" % (x.mat.name))
            lines.append("[Sel] %s" % (x.sel.name))
            lines.append("NEXT")

        return lines
