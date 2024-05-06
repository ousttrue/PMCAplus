import logging
from ..PMCA_data.mats import MATS
import PMCA  # type: ignore
from .. import PyPMCA
from ..material import MATERIAL, TOON


LOGGER = logging.getLogger(__name__)


class MAT_REP_DATA:  # 材質置換データ
    def __init__(self, num: int = -1, mat=None, sel=None):
        self.num = num
        self.mat = mat
        self.sel = sel


class MAT_REP:  # 材質置換
    def __init__(self, app=None):
        self.mat = {}
        self.toon = TOON()
        self.app = app

    def Get(self, mats_list, model=None, info=None, num=0):
        if model == None:
            if info == None:
                info_data = PMCA.getInfo(num)
                info = PyPMCA.INFO(info_data)
            mat = []
            for i in range(info.data["mat_count"]):
                tmp = PMCA.getMat(num, i)
                mat.append(MATERIAL(**tmp))
        else:
            info = model.info
            mat = model.mat

        for x in self.mat.values():
            x.num = -1

        for i in range(info.data["mat_count"]):
            for x in mats_list:
                if mat[i].tex == x.name and x.name != "":
                    if self.mat.get(mat[i].tex) == None:
                        self.mat[mat[i].tex] = MAT_REP_DATA(mat=x, num=i)
                    else:
                        self.mat[mat[i].tex].num = i

                    if self.mat[mat[i].tex].sel == None:
                        self.mat[mat[i].tex].sel = self.mat[mat[i].tex].mat.entries[0]

    def Set(self, model=None, info=None, num=0):
        if model == None:
            if info == None:
                info_data = PMCA.getInfo(num)
                info = PyPMCA.INFO(info_data)
            mat = []
            for i in range(info.data["mat_count"]):
                tmp = PMCA.getMat(num, i)
                mat.append(MATERIAL(**tmp))
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
                        x.spec_col = v
                        for j, y in enumerate(x.spec_col):
                            x.spec_col[j] = float(y)
                    elif k == "mirr_rgb":
                        x.mirr_col = v
                        for j, y in enumerate(x.mirr_col):
                            x.mirr_col[j] = float(y)

                    elif k == "toon":
                        toon = TOON()
                        toon.path = PMCA.getToonPath(num)
                        toon.name = PMCA.getToon(num)
                        tmp = v[-1].split(" ")
                        tmp[0] = int(tmp[0])
                        toon.path[tmp[0]] = ("toon/" + tmp[1]).encode(
                            "cp932", "replace"
                        )
                        toon.name[tmp[0]] = tmp[1].encode("cp932", "replace")

                        PMCA.setToon(num, toon.name)
                        PMCA.setToonPath(num, toon.path)
                        x.toon = tmp[0]
                    elif k == "author":
                        for y in v[-1].split(" "):
                            for z in self.app.authors:
                                if z == y:
                                    break
                            else:
                                self.app.authors.append(y)
                    elif k == "license":
                        for y in v[-1].split(" "):
                            for z in self.app.licenses:
                                if z == y:
                                    break
                            else:
                                self.app.licenses.append(y)

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
                    bytes(x.tex.encode("cp932", "replace")),
                    bytes(x.sph.encode("cp932", "replace")),
                    bytes(x.tex_path.encode("cp932", "replace")),
                    bytes(x.sph_path.encode("cp932", "replace")),
                )

    def list_to_text(self):
        lines = []

        for x in self.mat.values():
            lines.append("[Name] %s" % (x.mat.name))
            lines.append("[Sel] %s" % (x.sel.name))
            lines.append("NEXT")

        return lines

    def text_to_list(self, lines: list[str], mat_list: list[MATS]):
        LOGGER.info("parse material_rep")
        self.mat = {}
        tmp = ["", "", None]
        i = 0
        while lines[i] != "MATERIAL":
            i += 1
        i += 1
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
