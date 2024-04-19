from typing import List, NamedTuple
import sys, os.path
import os, io
import tkinter
import tkinter.filedialog
from PMCA_types import *
import PMCA

# インポートパスにカレントディレクトリを加える
sys.path.append(os.getcwd())

sysenc = sys.getfilesystemencoding()


class MAT_REP_DATA:  # 材質置換データ
    def __init__(self, num: int = -1, mat=None, sel=None):
        self.num = num
        self.mat = mat
        self.sel = sel


class PARTS:  # 読み込みパーツデータ
    def __init__(self, name="", comment="", path="", t=[], joint=[], props={}):
        self.name = name
        self.comment = comment
        self.path = path
        self.type = t
        self.joint = joint
        self.props = props


class TREE_LIST:
    def __init__(self, node=None, depth=0, text="", c_num=-1, list_num=0):
        self.node = node
        self.depth = depth
        self.text = text
        self.c_num = c_num


def load_partslist(fp: io.FileIO, parts_list: List[PARTS]) -> List[PARTS]:
    """
    設定ファイル読み込み
    """
    directry = ""
    active = PARTS(props={})
    line = fp.readline()
    while line:
        line = line.rstrip("\n").replace("\t", " ").split(" ", 1)
        # print(line)
        if line[0] == "":
            pass
        if line[0][:1] == "#":
            pass
        elif line[0] == "SETDIR":
            directry = line[1]

        elif line[0] == "NEXT":
            parts_list.append(active)
            active = PARTS(props={})

        elif len(line) < 2:
            pass
        elif line[0] == "[name]":
            active.name = line[1]
        elif line[0] == "[path]":
            active.path = directry + line[1]
        elif line[0] == "[comment]":
            active.comment = line[1]
        elif line[0] == "[type]":
            active.type = active.type + line[1].split(",")
        elif line[0] == "[joint]":
            active.joint = active.joint + line[1].split(",")
        elif line[0][:1] == "[" and line[0][-1:] == "]":
            if line[0][1:-1] in active.props:
                active.props[line[0][1:-1]].append(line[1])
            else:
                active.props[line[0][1:-1]] = [line[1]]
        line = fp.readline()
    parts_list.append(active)
    # for x in parts_list:
    #     print(x.name, x.path)
    return parts_list


def load_translist(fp, trans_list) -> List["MODEL_TRANS_DATA"]:
    trans_list.append(MODEL_TRANS_DATA(bones=[]))

    line = fp.readline()
    mode = 0

    while line:
        line = line.rstrip("\n").replace("\t", " ").split(" ", 1)
        # print(line)
        if line[0] == "":
            pass
        if line[0][:1] == "#":
            pass
        elif line[0] == "NEXT":
            trans_list.append(MODEL_TRANS_DATA(scale=0.0, bones=[]))
            mode = 0

        elif len(line) < 2:
            pass

        elif line[0] == "[ENTRY]":
            trans_list[-1].bones.append(
                BONE_TRANS_DATA(name=line[1], length=0.0, thick=0.0, props={})
            )
            mode = 1
        elif line[0] == "[name]":
            if mode == 0:
                trans_list[-1].name = line[1]
        elif line[0] == "[scale]":
            if mode == 0:
                trans_list[-1].scale = float(line[1])
            elif mode == 1:
                trans_list[-1].bones[-1].length = float(line[1])
                trans_list[-1].bones[-1].thick = float(line[1])
        elif line[0] == "[length]":
            if mode == 1:
                trans_list[-1].bones[-1].length = float(line[1])
        elif line[0] == "[thick]":
            if mode == 1:
                trans_list[-1].bones[-1].thick = float(line[1])
        elif line[0] == "[pos]":
            tmp = line[1].split(" ")
            if mode == 0:
                trans_list[-1].pos = [float(tmp[0]), float(tmp[1]), float(tmp[2])]
            elif mode == 1:
                trans_list[-1].bones[-1].pos = [
                    float(tmp[0]),
                    float(tmp[1]),
                    float(tmp[2]),
                ]
        elif line[0] == "[range]":
            tmp = line[1].split(" ")
            trans_list[-1].limit = [float(tmp[0]), float(tmp[1])]
        elif line[0] == "[default]":
            trans_list[-1].default = float(line[1])
        elif line[0][:1] == "[" and line[0][-1:] == "]":
            if line[0][1:-1] in trans_list[-1].props:
                trans_list[-1].props[line[0][1:-1]].append(line[1])
            else:
                trans_list[-1].props[line[0][1:-1]] = [line[1]]
        line = fp.readline()
    """
	mats_list.append(mats_list[-1])
	if mats_list[-1].entries[-1].__class__.__name__ == 'MATS_ENTRY':
		mats_list[-1].entries.append(mats_list[-1].entries[-1])
	"""

    return trans_list


###PMCA操作関連
def tree_click(event):
    pass


def space(i):
    string = ""
    for x in range(i):
        string = string + "  "
    return string


###データ関連
class NODE:  # モデルのパーツツリー
    def __init__(self, parts, depth=0, child=[], list_num=-1):
        self.parts = parts
        self.depth = depth
        self.child = child
        self.list_num = list_num

    def assemble(self, num: int, app):
        app.script_fin = []
        PMCA.Create_PMD(num)
        PMCA.Load_PMD(num, self.parts.path.encode(sysenc, "replace"))
        info_data = PMCA.getInfo(0)
        info = INFO(info_data)
        line = info.comment.split("\n")

        app.authors = []
        app.licenses = []
        if info.name != "":
            app.authors = ["Unknown"]
            app.licenses = ["Nonfree"]

        pmpy = app
        pmpy.functions = PMCA
        if "script_pre" in self.parts.props:
            for x in self.parts.props["script_pre"]:
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close

        if "script_post" in self.parts.props:
            for x in self.parts.props["script_post"]:
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close

        if "script_fin" in self.parts.props:
            app.script_fin.extend(self.parts.props["script_fin"])

        for x in line:
            tmp = x.split(":", 1)
            if len(tmp) == 1:
                tmp = x.split("：", 1)
            if (
                tmp[0] == "Author"
                or tmp[0] == "author"
                or tmp[0] == "Creator"
                or tmp[0] == "creator"
                or tmp[0] == "モデル制作"
            ):
                print(tmp[1])
                tmp[1] = tmp[1].replace("　", " ")
                app.authors = tmp[1].split(" ")

            elif tmp[0] == "License" or tmp[0] == "license" or tmp[0] == "ライセンス":
                tmp[1] = tmp[1].replace("　", " ")
                app.licenses = tmp[1].split(" ")
        print("パーツのパス:%s" % (self.parts.path))
        for x in self.child:
            if x != None:
                x.assemble_child(num, app)

        PMCA.Sort_PMD(num)

        for x in app.script_fin:
            argv = x.split()
            fp = open(argv[0], "r", encoding="utf-8-sig")
            script = fp.read()
            exec(script)
            fp.close

    def assemble_child(self, num, app):
        pmpy = app
        print("パーツのパス:%s" % (self.parts.path))

        PMCA.Create_PMD(4)
        PMCA.Load_PMD(4, self.parts.path.encode(sysenc, "replace"))

        info_data = PMCA.getInfo(4)
        info = INFO(info_data)
        line = info.comment.split("\n")
        flag_author = False
        flag_license = False
        for x in line:
            tmp = x.split(":", 1)
            if len(tmp) == 1:
                tmp = x.split("：", 1)
            if (
                tmp[0] == "Author"
                or tmp[0] == "author"
                or tmp[0] == "Creator"
                or tmp[0] == "creator"
                or tmp[0] == "モデル制作"
            ):
                if len(tmp) > 1:
                    flag_author = True
                    tmp[1] = tmp[1].replace("　", " ")
                    for x in tmp[1].split(" "):
                        for y in app.authors:
                            if x == y:
                                break
                        else:
                            app.authors.append(x)

            elif tmp[0] == "License" or tmp[0] == "license" or tmp[0] == "ライセンス":
                if len(tmp) > 1:
                    flag_license = True
                    tmp[1] = tmp[1].replace("　", " ")
                    for x in tmp[1].split(" "):
                        for y in app.licenses:
                            if x == y:
                                break
                        else:
                            app.licenses.append(x)
        if info.name != "":
            if flag_author == False:
                for x in app.authors:
                    if x == "Unknown":
                        break
                else:
                    app.authors.append("Unknown")
            if flag_license == False:
                for x in app.licenses:
                    if x == "Nonfree":
                        break
                else:
                    app.licenses.append("Nonfree")

        if "script_pre" in self.parts.props:
            for x in self.parts.props["script_pre"]:
                print("プレスクリプト実行")
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close

        PMCA.Add_PMD(num, 4)
        PMCA.Marge_PMD(num)

        if "script_post" in self.parts.props:
            for x in self.parts.props["script_post"]:
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close
        if "script_fin" in self.parts.props:
            app.script_fin.extend(self.parts.props["script_fin"])

        for x in self.child:
            if x != None:
                x.assemble_child(num, app)

    def create_list(self):
        List = [
            TREE_LIST(
                node=self, depth=self.depth, text=space(self.depth) + self.parts.name
            )
        ]
        for i, x in enumerate(self.child):
            if x != None:
                List.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text=space(self.depth + 1) + self.child[i].parts.name,
                        c_num=i,
                    )
                )
                x.list_add(List)
            elif self.parts.joint[i] != "":
                List.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text=space(self.depth + 1) + "#" + self.parts.joint[i],
                        c_num=i,
                    )
                )
        return List

    def list_add(self, List):
        for i, x in enumerate(self.child):
            if x != None:
                List.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text=space(self.depth + 1) + self.child[i].parts.name,
                        c_num=i,
                    )
                )
                x.list_add(List)
            elif self.parts.joint[i] != "":
                List.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text=space(self.depth + 1) + "#" + self.parts.joint[i],
                        c_num=i,
                    )
                )

    def recalc_depth(self, depth):
        self.depth = depth
        depth = depth + 1
        for x in self.child:
            if x != None:
                x.recalc_depth(depth)

    def node_to_text(self):
        lines = []
        lines.append("[Name] %s" % (self.parts.name))
        lines.append("[Path] %s" % (self.parts.path))
        lines.append("[Child]")
        print(self.parts.path)
        for x in self.child:
            if x != None:
                lines.extend(x.node_to_text())
            else:
                lines.append("None")
        lines.append("[Parent]")
        return lines

    def text_to_node(self, parts_list, lines):
        tmp = [None, None]
        curnode = self
        parents = [self]
        child_nums = [0]
        count = 0
        while lines[count] != "PARTS":
            # print(lines[i])
            count += 1
        count += 1

        while count < len(lines):
            print("count = %d" % (count))
            line = lines[count].split(" ")
            if len(parents) == 0:
                break
            if line[0] == "None":
                tmp = [None, None]
                child_nums[-1] += 1

            elif line[0] == "[Name]":
                tmp[0] = line[1]

            elif line[0] == "[Path]":
                if len(line) == 1:
                    tmp[1] = ""
                else:
                    tmp[1] = line[1]

            elif line[0] == "[Child]":

                tp = None
                print(tmp[0], len(parents))
                if tmp[0] != None:
                    for y in parts_list:
                        if y.name == tmp[0]:
                            tp = y
                            break
                    else:
                        for y in parts_list:
                            if y.path == tmp[1]:
                                tp = y
                                break

                if tp != None:
                    print(curnode.parts.name, len(curnode.child), child_nums[-1])
                    curnode.child[child_nums[-1]] = NODE(
                        parts=y, depth=curnode.depth + 1, child=[]
                    )
                    parents.append(curnode)
                    curnode = curnode.child[child_nums[-1]]
                    child_nums.append(0)
                    for x in curnode.parts.joint:
                        curnode.child.append(None)

                else:
                    depc = 1
                    while depc == 0:
                        count += 1
                        if lines[count] == "[Child]":
                            depc += 1
                        if lines[count] == "[Parent]":
                            depc -= 1
                    parents.pop()
                    child_nums.pop()
                    child_nums[-1] += 1

            elif line[0] == "[Parent]":
                curnode = parents.pop()
                child_nums.pop()
                print("up", len(parents))
                if len(child_nums) > 0:
                    child_nums[-1] += 1
            elif line[0] == "MATERIAL":
                break
            count += 1

        self.recalc_depth

        return lines


class MAT_REP:  # 材質置換
    def __init__(self, app=None):
        self.mat = {}
        self.toon = TOON()
        self.app = app

    def Get(self, mats_list, model=None, info=None, num=0):
        if model == None:
            if info == None:
                info_data = PMCA.getInfo(num)
                info = INFO(info_data)
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
                        for y in self.mat[mat[i].tex].mat.entries:
                            print(y.props)

    def Set(self, model=None, info=None, num=0):
        if model == None:
            if info == None:
                info_data = PMCA.getInfo(num)
                info = INFO(info_data)
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
                        toon = TOON()
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


class MODEL_TRANS_DATA:
    def __init__(
        self,
        name="",
        scale=1.0,
        pos=[0.0, 0.0, 0.0],
        rot=[0.0, 0.0, 0.0],
        bones=[],
        limit=[0.0, 2.0],
        default=1.0,
        gamma=1.0,
        props={},
    ):
        self.name = name
        self.scale = scale
        self.pos = pos
        self.rot = rot
        self.bones = bones
        self.limit = limit
        self.default = default
        self.gamma = gamma
        self.props = props

    def list_to_text(self):
        lines = []
        # lines.append('[Name] %s'%(self.name))
        lines.append("[Scale] %f" % (self.scale))
        lines.append("[Pos] %f %f %f" % (self.pos[0], self.pos[1], self.pos[2]))
        lines.append("[Rot] %f %f %f" % (self.rot[0], self.rot[1], self.rot[2]))
        lines.append("BONES")
        for x in self.bones:
            lines.append("[Name] %s" % (x.name))
            lines.append("[Length] %f" % (x.length))
            lines.append("[Thick] %f" % (x.thick))
            lines.append("[Pos] %f %f %f" % (x.pos[0], x.pos[1], x.pos[2]))
            lines.append("[Rot] %f %f %f" % (x.rot[0], x.rot[1], x.rot[2]))
            lines.append("NEXT")
        lines.pop()

        return lines

    def text_to_list(self, lines):
        tmp = ["", "", None]
        i = 0
        try:
            while lines[i] != "TRANSFORM":
                # print(lines[i])
                i += 1
        except:
            return None

        i += 1
        print("体型調整読み込み")
        for j, x in enumerate(lines[i:]):
            x = x.split(" ")
            print(x)
            if x[0] == "[Name]":
                self.name = x[1]
            elif x[0] == "[Scale]":
                self.scale = float(x[1])
            elif x[0] == "[Pos]":
                self.pos[0] = float(x[1])
                self.pos[1] = float(x[2])
                self.pos[2] = float(x[3])
            elif x[0] == "[Rot]":
                self.rot[0] = float(x[1])
                self.rot[1] = float(x[2])
                self.rot[2] = float(x[3])
            elif x[0] == "BONES":
                break
        self.bones = []
        self.bones.append(BONE_TRANS_DATA())
        for x in lines[i + j :]:
            x = x.split(" ")
            print(x)
            if x[0] == "[Name]":
                self.bones[-1].name = x[1]
            elif x[0] == "[Length]":
                self.bones[-1].length = float(x[1])
            elif x[0] == "[Thick]":
                self.bones[-1].thick = float(x[1])
            elif x[0] == "[Pos]":
                self.bones[-1].pos[0] = float(x[1])
                self.bones[-1].pos[1] = float(x[2])
                self.bones[-1].pos[2] = float(x[3])
            elif x[0] == "[Rot]":
                self.bones[-1].rot[0] = float(x[1])
                self.bones[-1].rot[1] = float(x[2])
                self.bones[-1].rot[2] = float(x[3])
            elif x[0] == "NEXT":
                if self.bones[-1].name != "":
                    self.bones.append(BONE_TRANS_DATA())


class BONE_TRANS_DATA:
    def __init__(
        self,
        name="",
        length=1.0,
        thick=1.0,
        pos=[0.0, 0.0, 0.0],
        rot=[0.0, 0.0, 0.0],
        props={},
    ):
        self.name = name
        self.length = length
        self.thick = thick
        self.pos = pos
        self.rot = rot
        self.props = props


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


def Get_PMD(num, only=None):
    info_data = PMCA.getInfo(num)
    info = INFO(info_data)

    vt = []
    for i in range(info_data["vt_count"]):
        tmp = PMCA.getVt(num, i)
        vt.append(VT(**tmp))

    face = []
    for i in range(info_data["face_count"]):
        face.append(PMCA.getFace(num, i))

    mat = []
    for i in range(info_data["mat_count"]):
        tmp = PMCA.getMat(num, i)
        mat.append(MATERIAL(**tmp))

    bone = []
    for i in range(info_data["bone_count"]):
        tmp = PMCA.getBone(num, i)
        bone.append(
            BONE(
                tmp["name"],
                tmp["name_eng"],
                tmp["parent"],
                tmp["tail"],
                tmp["type"],
                tmp["IK"],
                tmp["loc"],
            )
        )

    ik = []
    for i in range(info_data["IK_count"]):
        tmp = PMCA.getIK(num, i)
        ik.append(
            IK_LIST(
                tmp["index"],
                tmp["tail"],
                tmp["len"],
                tmp["ite"],
                tmp["weight"],
                tmp["child"],
            )
        )

    skin = []
    for i in range(info_data["skin_count"]):
        tmp = PMCA.getSkin(num, i)

        data = []
        for j in range(tmp["count"]):
            data.append(PMCA.getSkindata(num, i, j))
        skin.append(SKIN(tmp["name"], tmp["name_eng"], tmp["count"], tmp["type"], data))

    bone_group = []
    for i in range(info_data["bone_group_count"]):
        tmp = PMCA.getBone_group(num, i)
        bone_group.append(BONE_GROUP(**tmp))

    bone_disp = []
    for i in range(info_data["bone_disp_count"]):
        tmp = PMCA.getBone_disp(num, i)
        bone_disp.append(BONE_DISP(**tmp))

    toon = TOON()
    toon.name = PMCA.getToon(num)
    for i, x in enumerate(toon.name):
        toon.name[i] = x.decode("cp932", "replace")

    toon.path = PMCA.getToonPath(num)
    for i, x in enumerate(toon.path):
        toon.path[i] = x.decode("cp932", "replace")

    rb = []
    for i in range(info_data["rb_count"]):
        tmp = PMCA.getRb(num, i)
        rb.append(RB(**tmp))

    joint = []
    for i in range(info_data["joint_count"]):
        tmp = PMCA.getJoint(num, i)
        joint.append(JOINT(**tmp))

    return PMD(
        info, vt, face, mat, bone, ik, skin, bone_group, bone_disp, toon, rb, joint
    )


def Set_PMD(num, model):
    print("INIT")
    PMCA.Create_FromInfo(
        num,
        bytes(model.info.name.encode("cp932", "replace")),
        bytes(model.info.comment.encode("cp932", "replace")),
        bytes(model.info.name_eng.encode("cp932", "replace")),
        bytes(model.info.comment_eng.encode("cp932", "replace")),
        len(model.vt),
        len(model.face),
        len(model.mat),
        len(model.bone),
        len(model.IK_list),
        len(model.skin),
        len(model.bone_grp),
        len(model.bone_dsp),
        model.info.eng_support,
        len(model.rb),
        len(model.joint),
        len(model.info.skin_index),
        model.info.skin_index,
    )

    print("VT")
    for i, x in enumerate(model.vt):
        PMCA.setVt(
            num, i, x.loc, x.nor, x.uv, x.bone_num[0], x.bone_num[1], x.weight, x.edge
        )

    print("FACE")
    for i, x in enumerate(model.face):
        PMCA.setFace(num, i, x)

    print("MAT")
    for i, x in enumerate(model.mat):
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

    print("BONE")
    for i, x in enumerate(model.bone):
        PMCA.setBone(
            num,
            i,
            bytes(x.name.encode("cp932", "replace")),
            bytes(x.name_eng.encode("cp932", "replace")),
            x.parent,
            x.tail,
            x.type,
            x.IK,
            x.loc,
        )

    print("IK")
    for i, x in enumerate(model.IK_list):
        PMCA.setIK(
            num, i, x.index, x.tail_index, len(x.child), x.iterations, x.weight, x.child
        )

    print("SKIN")
    for i, x in enumerate(model.skin):
        PMCA.setSkin(
            num,
            i,
            bytes(x.name.encode("cp932", "replace")),
            bytes(x.name_eng.encode("cp932", "replace")),
            len(x.data),
            x.type,
        )
        for j, y in enumerate(x.data):
            PMCA.setSkindata(num, i, j, y["index"], y["loc"])

    print("GROUP")
    for i, x in enumerate(model.bone_grp):
        PMCA.setBone_group(
            num,
            i,
            bytes(x.name.encode("cp932", "replace")),
            bytes(x.name_eng.encode("cp932", "replace")),
        )
    for i, x in enumerate(model.bone_dsp):
        PMCA.setBone_disp(num, i, x.index, x.group)

    print("TOON")
    tmp = []
    print(model.toon.name)
    for i, x in enumerate(model.toon.name):
        tmp.append(bytes(x.encode("cp932", "replace")))
    PMCA.setToon(num, tmp)
    for i, x in enumerate(model.toon.path):
        tmp.append(bytes(x.encode("cp932", "replace")))
    PMCA.setToonPath(num, tmp)

    print("RBODY")
    for i, x in enumerate(model.rb):
        PMCA.setRb(
            num,
            i,
            bytes(x.name.encode("cp932", "replace")),
            x.bone,
            x.group,
            x.target,
            x.shape,
            x.size,
            x.loc,
            x.rot,
            x.mass,
            x.damp,
            x.rdamp,
            x.res,
            x.fric,
            x.type,
        )

    print("JOINT")
    for i, x in enumerate(model.joint):
        # print(x.name, x.rb, x.loc, x.rot, x.limit, x.spring)
        PMCA.setJoint(
            num,
            i,
            bytes(x.name.encode("cp932", "replace")),
            x.rb,
            x.loc,
            x.rot,
            x.limit,
            x.spring,
        )


def Set_Name_Comment(num=0, name="", comment="", name_eng="", comment_eng=""):
    PMCA.Set_Name_Comment(
        num,
        name.encode("cp932", "replace"),
        comment.encode("cp932", "replace"),
        name_eng.encode("cp932", "replace"),
        comment_eng.encode("cp932", "replace"),
    )
