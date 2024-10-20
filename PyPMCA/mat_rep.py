import dataclasses
import PMCA
from . import types
from . import material
from . import author_license


@dataclasses.dataclass
class MAT_REP_DATA:
    mat: material.MATS
    num: int = -1
    sel: material.MATS_ENTRY | None = None


@dataclasses.dataclass
class MAT_REP:
    """
    材質置換
    """

    mat: dict[str, MAT_REP_DATA] = dataclasses.field(default_factory=dict)
    toon: types.TOON = dataclasses.field(default_factory=types.TOON)

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
                materials.append(types.MATERIAL(**tmp))
        else:
            info = model.info
            materials = model.mat

        for x in self.mat.values():
            x.num = -1

        assert info
        for i, material in enumerate(materials):
            for x in mats_list:
                if material.tex == x.name and x.name != "":
                    if self.mat.get(material.tex) == None:
                        self.mat[material.tex] = MAT_REP_DATA(mat=x, num=i)
                    else:
                        self.mat[material.tex].num = i

                    if self.mat[material.tex].sel == None:
                        self.mat[material.tex].sel = self.mat[material.tex].mat.entries[
                            0
                        ]
                        for y in self.mat[material.tex].mat.entries:
                            print(y.props)

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
                mat.append(types.MATERIAL(**tmp))
        else:
            info = model.info
            mat = model.mat

        for i, x in enumerate(mat):
            if self.mat.get(x.tex) != None:
                rep = self.mat[x.tex].sel
                for k, v in rep.props.items():
                    if k == "tex":
                        print("replace texture", x.tex, "to", v, "num =", i)
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
                        toon = types.TOON()
                        toon.path = PMCA.getToonPath(num)
                        toon.name = PMCA.getToon(num)
                        # print("toon")
                        # print(toon.name)
                        # print(toon.path)
                        tmp = v[-1].split(" ")
                        tmp[0] = int(tmp[0])
                        toon.path[tmp[0]] = ("toon/" + tmp[1]).encode(
                            "cp932", "replace"
                        )
                        toon.name[tmp[0]] = tmp[1].encode("cp932", "replace")

                        # print(toon.name)
                        # print(toon.path)

                        PMCA.setToon(num, toon.name)
                        PMCA.setToonPath(num, toon.path)
                        x.toon = tmp[0]
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

    def text_to_list(self, lines: list[str], mat_list: list[material.MATS]) -> None:
        self.mat = {}
        tmp = ["", "", None]
        i = 0
        while lines[i] != "MATERIAL":
            # print(lines[i])
            i += 1
        i += 1
        print("材質読み込み")
        for x in lines[i:]:
            x = x.split(" ")
            print(x)
            if x[0] == "[Name]":
                tmp[0] = x[1]
            elif x[0] == "[Sel]":
                tmp[1] = x[1]
            elif x[0] == "NEXT":
                print(tmp[0])
                for y in mat_list:
                    if y.name == tmp[0]:
                        tmp[2] = y
                        break
                else:
                    tmp[2] = None
                    print("Not found")
                    continue

                for y in tmp[2].entries:
                    print(y.name)
                    if y.name == tmp[1]:
                        print(tmp[0])
                        self.mat[tmp[0]] = MAT_REP_DATA(num=-1, mat=tmp[2], sel=y)
                        break
