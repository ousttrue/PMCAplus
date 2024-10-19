#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os.path
import os
import tkinter
import tkinter.filedialog

import PMCA

from .translation_list import TranslationList
from .parts import PARTS
from .material import MATS
from .transform import MODEL_TRANS_DATA
from .node import NODE
from . import types


__all__ = ["TranslationList"]


# インポートパスにカレントディレクトリを加える
sys.path.append(os.getcwd())


###PMCA操作関連
def tree_click(event):
    pass


class MAT_REP:  # 材質置換
    def __init__(self, app=None):
        self.mat = {}
        self.toon = types.TOON()
        self.app = app

    def Get(self, mats_list, model=None, info=None, num=0):
        if model == None:
            if info == None:
                info_data = PMCA.getInfo(num)
                info = types.INFO(info_data)
            mat = []
            for i in range(info.data["mat_count"]):
                tmp = PMCA.getMat(num, i)
                mat.append(types.MATERIAL(**tmp))
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
                        for y in self.mat[mat[i].tex].mat.entries:
                            print(y.props)

    def Set(self, model=None, info=None, num=0):
        if model == None:
            if info == None:
                info_data = PMCA.getInfo(num)
                info = types.INFO(info_data)
            mat = []
            for i in range(info.data["mat_count"]):
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

    def text_to_list(self, lines, mat_list):
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


class MAT_REP_DATA:  # 材質置換データ
    def __init__(self, num=-1, mat=None, sel=None):
        self.num = num
        self.mat = mat
        self.sel = sel


class MODELINFO:
    def __init__(
        self,
        name="PMCAモデル",
        name_l="PMCAモデル",
        comment="",
        name_eng="PMCA model",
        name_l_eng="PMCA generated model",
        comment_eng="",
    ):
        self.name = name
        self.name_l = name_l
        self.comment = comment
        self.name_eng = name_eng
        self.name_l_eng = name_l_eng
        self.comment_eng = comment_eng


def Set_Name_Comment(num=0, name="", comment="", name_eng="", comment_eng=""):
    PMCA.Set_Name_Comment(
        num,
        name.encode("cp932", "replace"),
        comment.encode("cp932", "replace"),
        name.encode("cp932", "replace"),
        comment.encode("cp932", "replace"),
    )
