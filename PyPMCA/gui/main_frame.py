from typing import List
import os, sys
import shutil
import random
import tkinter.ttk
import logging

import PMCA  # type: ignore
from .main_frame_model import ModelTab
from .main_frame_color import ColorTab
from .main_frame_transform import TransformTab
from .main_frame_info import InfoTab
from ..PMCA_data.parts import PARTS
from ..PMCA_data import PMCAData
from ..PMCA_data.model_transform_data import MODEL_TRANS_DATA
from .. import PyPMCA

LOGGER = logging.getLogger(__name__)


class BONE:
    def __init__(self, name, name_eng, parent, tail, btype, IK, loc):
        if type(name) == type(b""):
            name = name.decode("cp932", "replace")
        if type(name_eng) == type(b""):
            name_eng = name_eng.decode("cp932", "replace")
        self.name = name
        self.name_eng = name_eng
        self.parent = parent
        self.tail = tail
        self.type = btype
        self.IK = IK
        self.loc = loc


class MATERIAL:
    def __init__(
        self,
        diff_col,
        alpha,
        spec,
        spec_col,
        mirr_col,
        toon,
        edge,
        face_count,
        tex,
        sph,
        tex_path,
        sph_path,
    ):
        self.diff_col = diff_col
        self.alpha = alpha
        self.spec = spec
        self.spec_col = spec_col
        self.mirr_col = mirr_col
        self.toon = toon
        self.edge = edge
        self.face_count = face_count
        self.tex = tex.decode("cp932", "replace")
        self.sph = sph.decode("cp932", "replace")
        self.tex_path = tex_path.decode("cp932", "replace")
        self.sph_path = sph_path.decode("cp932", "replace")


class TOON:
    def __init__(self):
        self.name = None
        self.path = None


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
                        for y in self.mat[mat[i].tex].mat.entries:
                            print(y.props)

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


class NODE:  # モデルのパーツツリー
    def __init__(
        self, parts: PARTS, depth: int = 0, child: List["NODE"] = [], list_num: int = -1
    ):
        self.parts = parts
        self.depth = depth
        self.child = child
        self.list_num = list_num

    def assemble(self, num: int, app):
        app.script_fin = []
        PMCA.Create_PMD(num)
        PMCA.Load_PMD(num, self.parts.path.encode(sys.getdefaultencoding(), "replace"))
        info_data = PMCA.getInfo(0)
        info = PyPMCA.INFO(info_data)
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
        PMCA.Load_PMD(4, self.parts.path.encode(sys.getdefaultencoding(), "replace"))

        info_data = PMCA.getInfo(4)
        info = PyPMCA.INFO(info_data)
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

    def create_list(self) -> List["TREE_LIST"]:
        l: List[TREE_LIST] = [
            TREE_LIST(
                node=self, depth=self.depth, text="  " * self.depth + self.parts.name
            )
        ]
        for i, x in enumerate(self.child):
            if x != None:
                l.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text=("  " * (self.depth + 1)) + self.child[i].parts.name,
                        c_num=i,
                    )
                )
                x.list_add(l)
            elif self.parts.joint[i] != "":
                l.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + "#" + self.parts.joint[i],
                        c_num=i,
                    )
                )
        return l

    def list_add(self, List):
        for i, x in enumerate(self.child):
            if x != None:
                List.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + self.child[i].parts.name,
                        c_num=i,
                    )
                )
                x.list_add(List)
            elif self.parts.joint[i] != "":
                List.append(
                    TREE_LIST(
                        node=self,
                        depth=self.depth + 1,
                        text="  " * (self.depth + 1) + "#" + self.parts.joint[i],
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


class TREE_LIST:
    def __init__(
        self,
        node: NODE | None = None,
        depth: int = 0,
        text: str = "",
        c_num: int = -1,
        list_num=0,
    ):
        self.node = node
        self.depth = depth
        self.text = text
        self.c_num = c_num


class MainFrame(tkinter.ttk.Frame):
    def __init__(self, title: str, data: PMCAData, master: tkinter.Tk):
        super().__init__(master)
        self.export2folder = False
        self.data = data
        self.root = master
        self.root.title(title)
        self.tree_list = []
        self.tree_entry = []
        self.parts_entry_k = []
        self.parts_entry_p = []
        self.mat_rep = None
        self.transform_data = []
        self.target_dir = "./model/"
        self.cur_parts = 0
        self.cur_mat = 0
        self.pack()
        self.createWidgets()

        # menu
        self.menubar = tkinter.Menu(master)
        master.configure(menu=self.menubar)

        # files
        files = tkinter.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="ファイル", underline=0, menu=files)
        files.add_command(label="新規", underline=0, command=self.clear)
        files.add_command(label="読み込み", underline=0, command=self.load_node)
        files.add_separator
        files.add_command(label="保存", underline=0, command=self.save_node)
        files.add_command(label="モデル保存", underline=0, command=self.dialog_save_PMD)
        files.add_separator
        files.add_command(label="一括組立て", underline=0, command=self.batch_assemble)
        files.add_separator
        files.add_command(
            label="PMDフォーマットチェック", underline=0, command=self.savecheck_PMD
        )
        files.add_command(label="PMD概要確認", underline=0, command=self.check_PMD)
        files.add_command(label="PMD詳細確認", underline=0, command=self.propcheck_PMD)
        files.add_separator

        def quit():
            master.winfo_toplevel().destroy()
            master.quit()

        files.add_command(label="exit", underline=0, command=quit)

        # editing
        editing = tkinter.Menu(self.menubar, tearoff=False)
        self.menubar.add_cascade(label="編集", underline=0, menu=editing)
        editing.add_command(label="体型調整を初期化", underline=0, command=self.init_tf)
        editing.add_command(
            label="材質をランダム選択", underline=0, command=self.rand_mat
        )
        editing.add_command(label="PMCA設定", underline=0, command=self.setting_dialog)

        self.init_tree()
        self.init_mat()

    def init_tree(self):
        LOGGER.info("ツリー初期化")
        node = NODE(parts=PARTS(name="ROOT", joint=["root"]), depth=-1, child=[None])

        self.tree_list = node.create_list()
        self.tree_entry = []
        for x in self.tree_list:
            self.tree_entry.append(x.text)
        self.tree_entry = self.tree_entry[1:]
        self.tab[0].l_tree.set_entry(self.tree_entry, sel=0)

        self.parts_entry_k = []
        self.parts_entry_p = []
        for x in self.data.parts_list:
            for y in x.type:
                if y == "root":
                    self.parts_entry_k.append(x.name)
                    self.parts_entry_p.append(x)
                    break

        self.parts_entry_k.append("#外部モデル読み込み")
        self.parts_entry_p.append("load")
        # app.parts_entry_k.append('#None')
        # app.parts_entry_p.append(None)

        self.tab[0].l_sel.set_entry(self.parts_entry_k)

    def init_mat(self):
        LOGGER.info("材質置換設定初期化")
        self.mat_rep = MAT_REP(app=self)

        self.tab[3].frame.name.set("PMCAモデル")
        self.tab[3].frame.name_l.set("PMCAモデル")
        self.tab[3].frame.comment.delete("1.0", tkinter.END)

        self.transform_data = [MODEL_TRANS_DATA(scale=1.0, bones=[], props={})]
        tmp: List[str] = []
        for x in self.data.transform_list:
            tmp.append(x.name)

        self.tab[2].tfgroup.set_entry(tmp)

    def createWidgets(self):
        """
        self.listbox = Listbox(self, height = 6, exportselection = 0, selectmode = SINGLE)
        self.listbox.yscroll = Scrollbar(self, orient = VERTICAL, command = self.listbox.yview)
        self.listbox.yscroll.pack(side = RIGHT, fill = Y, expand = 0)
        self.listbox["yscrollcommand"] = self.listbox.yscroll.set
        self.listbox.pack(expand = 1, fill = BOTH)
        """

        # タブを作成
        notebook = tkinter.ttk.Notebook(self.root)
        notebook.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.tab = []
        self.tab.append(ModelTab(self.root))
        self.tab.append(ColorTab(self.root))
        self.tab.append(TransformTab(self.root))
        self.tab.append(InfoTab(self.root))

        for x in self.tab:
            notebook.insert(tkinter.END, x, text=x.text)
        ########################################################################################################
        # Buttons

        self.frame_button = tkinter.ttk.Frame(self.root)
        self.QUIT = tkinter.ttk.Button(self.frame_button)
        self.QUIT["text"] = "QUIT"

        def quit():
            self.root.winfo_toplevel().destroy()
            self.root.quit()

        self.QUIT["command"] = quit
        self.QUIT.pack(side=tkinter.RIGHT)
        self.frame_button.pack(padx=5, pady=5, side=tkinter.TOP, fill="x")

    def load_CNL_File(self, name):
        f = open(name, "r", encoding="utf-8-sig")
        lines = f.read()
        f.close
        lines = lines.split("\n")

        self.tab[3].frame.name.set(lines[0])
        self.tab[3].frame.name_l.set(lines[1])
        for line in lines[2:]:
            if line == "PARTS":
                break
            elif line == "":
                pass
            else:
                self.tab[3].frame.comment.insert(END, line)
                self.tab[3].frame.comment.insert(END, "\n")

        else:
            self.tab[3].frame.comment.delete("1.0", END)

        self.tree_list[0].node.text_to_node(self.data.parts_list, lines)
        self.mat_rep.text_to_list(lines, self.data.mats_list)
        self.transform_data[0].text_to_list(lines)
        return True

    ######################################################################################
    def refresh(self, level: int = 0):
        sel_t = int(self.tab[0].l_tree.listbox.curselection()[0])
        self.tree_list = self.tree_list[0].node.create_list()
        self.tree_entry = []

        for x in self.tree_list:
            self.tree_entry.append(x.text)
        self.tree_entry = self.tree_entry[1:]
        self.tab[0].l_tree.set_entry(self.tree_entry, sel=sel_t)

        # モデル組み立て
        PMCA.MODEL_LOCK(1)

        if level < 1:
            print("モデル組立て")

            PMCA.Create_PMD(0)

            # PMCA.Load_PMD(0, "./testmodels/001.pmd")

            x = self.tree_list[0].node
            if x != None:
                x.assemble(0, self)

            PMCA.Copy_PMD(0, 1)
        else:
            PMCA.Copy_PMD(1, 0)

        if level < 2:
            # 材質関連
            print("材質置換")
            self.mat_rep.Get(self.data.mats_list)
            # print("1")
            self.mat_entry = [[], []]
            for v in self.mat_rep.mat.values():
                if v.num >= 0:
                    self.mat_entry[0].append(v.mat.name + "  " + v.sel.name)
                    self.mat_entry[1].append(v.mat.name)
            # print("2")
            self.tab[1].l_tree.set_entry(self.mat_entry[0], sel=self.cur_mat)
            # print("3")
            self.mat_rep.Set()
            # print("4")
            PMCA.Copy_PMD(0, 2)
        else:
            PMCA.Copy_PMD(2, 0)

        if level < 3:
            print("体型調整")
            info_data = PMCA.getInfo(0)
            info = PyPMCA.INFO(info_data)

            tmpbone = []
            for i in range(info_data["bone_count"]):
                tmp = PMCA.getBone(0, i)
                tmpbone.append(
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
            refbone = None
            refbone_index = None
            for i, x in enumerate(tmpbone):
                if x.name == "右足首":
                    refbone = x
                    refbone_index = i
                    break

            for y in self.transform_data:
                PMCA.Resize_Model(0, y.scale)
                for x in y.bones:
                    PMCA.Resize_Bone(
                        0, x.name.encode("cp932", "replace"), x.length, x.thick
                    )
                    PMCA.Move_Bone(
                        0,
                        x.name.encode("cp932", "replace"),
                        x.pos[0],
                        x.pos[1],
                        x.pos[2],
                    )
                    # print("resize_bone %f %f"%(x.length, x.thick))

            if refbone != None:
                newbone = None
                tmp = PMCA.getBone(0, refbone_index)
                newbone = BONE(
                    tmp["name"],
                    tmp["name_eng"],
                    tmp["parent"],
                    tmp["tail"],
                    tmp["type"],
                    tmp["IK"],
                    tmp["loc"],
                )

                dy = refbone.loc[1] - newbone.loc[1]
                for x in tmpbone:
                    i = x.parent
                    count = 0
                    while (
                        i < info_data["bone_count"] and count < info_data["bone_count"]
                    ):
                        if tmpbone[i].name == "センター":
                            PMCA.Move_Bone(
                                0, x.name.encode("cp932", "replace"), 0, dy, 0
                            )
                            break
                        i = tmpbone[i].parent
                        count += 1

                PMCA.Move_Bone(0, "センター".encode("cp932", "replace"), 0, dy, 0)
                PMCA.Move_Bone(0, "+センター".encode("cp932", "replace"), 0, -dy, 0)

            for y in self.transform_data:
                PMCA.Move_Model(0, y.pos[0], y.pos[1], y.pos[2])

            PMCA.Update_Skin(0)
            PMCA.Adjust_Joints(0)
            PMCA.Copy_PMD(0, 3)
        else:
            PMCA.Copy_PMD(3, 0)

        self.tab[3].refresh(level)

        if level < 3:
            PMCA.PMD_view_set(0, "replace")  # テクスチャを変更しない
        else:
            PMCA.PMD_view_set(0, "replace")

        PMCA.MODEL_LOCK(0)

        wht = PMCA.getWHT(0)
        self.tab[2].info_frame.strvar.set(
            "height     = %f\nwidth      = %f\nthickness = %f\n"
            % (wht[1], wht[0], wht[2])
        )

        print("Done")

    ########################################################################################
    # functions menu
    def clear(self):
        init(self)
        self.refresh()

    def savecheck_PMD(self):
        self.refresh(level=3)
        model = PyPMCA.Get_PMD(0)

        errors = []

        if len(model.info.name) > 20:
            errors.append(
                "モデル名の長さが20byteを超えています:"
                + str(len(model.info.name))
                + "byte"
            )
        if len(model.info.comment) > 256:
            errors.append(
                "モデルコメントの長さが256byteを超えています:"
                + str(len(model.info.comment))
                + "byte"
            )
        if len(model.info.name_eng) > 20:
            errors.append(
                "英語モデル名の長さが20byteを超えています:"
                + str(len(model.info.name))
                + "byte"
            )
        if len(model.info.comment_eng) > 256:
            errors.append(
                "英語モデルコメントの長さが256byteを超えています:"
                + str(len(model.info.comment))
                + "byte"
            )
        for x in model.mat:
            if (len(x.tex) + len(x.sph)) > 20:
                errors.append(
                    '材質"'
                    + x.name
                    + '"のテクスチャ+スフィアマップの長さが20byteを超えています:'
                    + str(len(x.tex) + len(x.sph))
                    + "byte"
                )

        for x in model.bone:
            if len(x.name) > 20:
                errors.append(
                    'ボーン"'
                    + x.name
                    + '"の名前の長さが20byteを超えています:'
                    + str(len(x.name))
                    + "byte"
                )
            if len(x.name_eng) > 20:
                errors.append(
                    'ボーン"'
                    + x.name
                    + '"の英語名の長さが20byteを超えています:'
                    + str(len(x.name_eng))
                    + "byte"
                )
            i = x.parent
            count = 0
            bone_count = len(model.bone)
            while count < bone_count:
                if i >= bone_count:
                    break
                print(i)
                i = model.bone[i].parent
                count += 1
            else:
                errors.append("循環依存：%s" % (x.name))

        for x in model.skin:
            if len(x.name) > 20:
                errors.append(
                    '表情"'
                    + x.name
                    + '"の名前の長さが20byteを超えています:'
                    + str(len(x.name))
                    + "byte"
                )
            if len(x.name_eng) > 20:
                errors.append(
                    '表情"'
                    + x.name
                    + '"の英語名の長さが20byteを超えています:'
                    + str(len(x.name_eng))
                    + "byte"
                )

        for x in model.bone_grp:
            if len(x.name) > 50:
                errors.append(
                    'ボーングループ"'
                    + x.name
                    + '"の名前の長さが50byteを超えています:'
                    + str(len(x.name))
                    + "byte"
                )
            if len(x.name_eng) > 50:
                errors.append(
                    'ボーングループ"'
                    + x.name
                    + '"の英語名の長さが50byteを超えています:'
                    + str(len(x.name_eng))
                    + "byte"
                )

        for x in model.rb:
            if len(x.name) > 20:
                errors.append(
                    '剛体"'
                    + x.name
                    + '"の名前の長さが20byteを超えています:'
                    + str(len(x.name))
                    + "byte"
                )

        for x in model.joint:
            if len(x.name) > 20:
                errors.append(
                    'ジョイント"'
                    + x.name
                    + '"の名前の長さが20byteを超えています:'
                    + str(len(x.name))
                    + "byte"
                )

        for i, x in enumerate(model.face):
            for y in x:
                if y >= len(model.vt):
                    errors.append("面%dの頂点インデックスが不正です:%s" % (i, str(x)))

        for i, x in enumerate(model.vt):
            for y in x.bone_num:
                if y >= len(model.bone):
                    errors.append(
                        "頂点%dのボーンインデックスが不正です:%s" % (i, str(x))
                    )

        if len(errors) == 0:
            errors.append("PMDとして正常に保存できます")

        root = Toplevel()
        root.transient(self)
        close = QUIT(root)
        frame = Frame(root)
        frame.log = Text(frame)
        for x in errors:
            frame.log.insert(END, x + "\n")
        frame.log["state"] = "disabled"
        frame.yscroll = Scrollbar(frame, orient=VERTICAL, command=frame.log.yview)
        frame.yscroll.pack(side=RIGHT, fill=Y, expand=0, anchor=E)
        frame.log["yscrollcommand"] = frame.yscroll.set
        frame.log.pack(side=RIGHT, fill=BOTH, expand=1)
        frame.pack(fill=BOTH, expand=1)
        Button(root, text="OK", command=close).pack()
        root.mainloop()

    def check_PMD(self):
        self.refresh(level=3)
        info_data = PMCA.getInfo(0)
        info = PyPMCA.INFO(info_data)
        string = "name :" + info.name
        string += "\ncomment :\n" + info.comment
        string += "\n頂点数 :" + str(info_data["vt_count"])
        string += "\n面数　 :" + str(info_data["face_count"])
        string += "\n材質数 :" + str(info_data["mat_count"])
        string += "\nボーン数 :" + str(info_data["bone_count"])
        string += "\nIK数   :" + str(info_data["IK_count"])
        string += "\n表情数 :" + str(info_data["skin_count"])
        string += "\nボーングループ数 :" + str(info_data["bone_group_count"])
        string += "\nボーン表示数 :" + str(info_data["bone_disp_count"])

        string += "\n\n英語対応 :" + str(info_data["eng_support"])
        string += "\n剛体数 :" + str(info_data["rb_count"])
        string += "\nジョイント数 :" + str(info_data["joint_count"])

        root = Toplevel()
        root.transient(self)
        close = QUIT(root)
        frame = Frame(root)
        frame.log = Text(frame)
        frame.log.insert(END, string)
        frame.log["state"] = "disabled"
        frame.yscroll = Scrollbar(frame, orient=VERTICAL, command=frame.log.yview)
        frame.yscroll.pack(side=RIGHT, fill=Y, expand=0, anchor=E)
        frame.log["yscrollcommand"] = frame.yscroll.set
        frame.log.pack(side=RIGHT, fill=BOTH, expand=1)
        frame.pack(fill=BOTH, expand=1)
        Button(root, text="OK", command=close).pack()
        root.mainloop()

    def propcheck_PMD(self):
        self.refresh(level=3)
        model = PyPMCA.Get_PMD(0)
        string = "name :" + model.info.name
        string += "\ncomment :\n" + model.info.comment
        string += "\n\nname_en :" + model.info.name_eng
        string += "\ncomment_en :\n" + model.info.comment_eng
        string += "\n\n頂点数 :" + str(model.info.data["vt_count"]) + "\n"
        for i, x in enumerate(model.vt):
            string += str(i) + "\n"
            string += "loc:" + str(x.loc) + "\n"
            string += "nor:" + str(x.nor) + "\n"
            string += "uv:" + str(x.uv) + "\n"
            string += "bone:" + str(x.bone_num) + "\n"
            string += "weight:" + str(x.weight) + "\n"
            string += "edge:" + str(x.edge) + "\n\n"

        string += "\n面数　 :" + str(model.info.data["face_count"]) + "\n"
        for i, x in enumerate(model.face):
            string += str(x) + "\n"
        string += "\n材質数 :" + str(model.info.data["mat_count"]) + "\n"
        for i, x in enumerate(model.mat):
            string += str(i) + "\n"
            string += "diff_col:" + str(x.diff_col) + "\n"
            string += "mirr_col:" + str(x.mirr_col) + "\n"
            string += "spec_col:" + str(x.spec_col) + "\n"
            string += "spec:" + str(x.spec) + "\n"
            string += "alpha:" + str(x.alpha) + "\n"
            string += "toon:" + str(x.toon) + "\n"
            string += "edge:" + str(x.edge) + "\n"
            string += "tex:" + x.tex + "\n"
            string += "sph:" + x.sph + "\n"
            string += "face_count:" + str(x.face_count) + "\n\n"

        string += "\nボーン数 :" + str(model.info.data["bone_count"]) + "\n"
        for i, x in enumerate(model.bone):
            string += str(i) + "\n"
            string += "name:" + x.name + "\n"
            string += "name_en:" + x.name_eng + "\n"
            string += "parent:" + str(x.parent) + "\n"
            string += "tail:" + str(x.tail) + "\n"
            string += "type:" + str(x.type) + "\n"
            string += "IK:" + str(x.IK) + "\n"
            string += "loc:" + str(x.loc) + "\n\n"

        string += "\nIK数   :" + str(model.info.data["IK_count"]) + "\n"
        for i, x in enumerate(model.IK_list):
            string += str(i) + "\n"
            string += "index:" + str(x.index) + "\n"
            string += "tail_index:" + str(x.tail_index) + "\n"
            string += "chain_len:" + str(x.chain_len) + "\n"
            string += "iterations:" + str(x.iterations) + "\n"
            string += "weight:" + str(x.weight) + "\n"
            string += "child:" + str(x.child) + "\n\n"

        string += "\n表情数 :" + str(model.info.data["skin_count"]) + "\n"
        for i, x in enumerate(model.skin):
            string += str(i) + "\n"
            string += "name:" + x.name + "\n"
            string += "name_en:" + x.name_eng + "\n"
            string += "count:" + str(x.count) + "\n"
            string += "type:" + str(x.type) + "\n\n"
            # string += 'data:' + x.data + '\n'

        string += (
            "\nボーングループ数 :" + str(model.info.data["bone_group_count"]) + "\n"
        )
        for i, x in enumerate(model.bone_grp):
            string += str(i) + "\n"
            string += "name:" + x.name + "\n"
            string += "name_en:" + x.name_eng + "\n\n"

        string += "\nボーン表示数 :" + str(model.info.data["bone_disp_count"]) + "\n"
        for i, x in enumerate(model.bone_dsp):
            string += str(i) + "\n"
            string += "index:" + str(x.index) + "\n"
            string += "group:" + str(x.group) + "\n\n"

        for i, x in enumerate(model.toon.name):
            string += "%d %s\n" % (i, x)

        string += "\n\n英語対応 :" + str(model.info.data["eng_support"])
        string += "\n\n剛体数 :" + str(model.info.data["rb_count"]) + "\n"
        for i, x in enumerate(model.rb):
            string += str(i) + "\n"
            string += "name:" + x.name + "\n\n"

        string += "\nジョイント数 :" + str(model.info.data["joint_count"]) + "\n"
        for i, x in enumerate(model.joint):
            string += str(i) + "\n"
            string += "name:" + x.name + "\n\n"

        root = Toplevel()
        root.transient(self)
        close = QUIT(root)
        frame = Frame(root)
        frame.log = Text(frame)
        frame.log.insert(END, string)
        frame.log["state"] = "disabled"
        frame.yscroll = Scrollbar(frame, orient=VERTICAL, command=frame.log.yview)
        frame.yscroll.pack(side=RIGHT, fill=Y, expand=0, anchor=E)
        frame.log["yscrollcommand"] = frame.yscroll.set
        frame.log.pack(side=RIGHT, fill=BOTH, expand=1)
        frame.pack(fill=BOTH, expand=1)
        Button(root, text="OK", command=close).pack()
        root.mainloop()

    def init_tf(self):
        self.transform_data = [
            PyPMCA.MODEL_TRANS_DATA(
                scale=1.0, pos=[0.0, 0.0, 0.0], rot=[0.0, 0.0, 0.0], bones=[], props={}
            )
        ]
        self.refresh()

    def rand_mat(self):
        for x in self.mat_rep.mat.items():
            random.seed()
            # print(x)
            # print(x[1].mat)
            x[1].sel = x[1].mat.entries[random.randint(0, len(x[1].mat.entries) - 1)]
        self.refresh()

    def save_node(self):
        x = self.tree_list[0].node.child[0]
        if x != None:
            name = filedialog.asksaveasfilename(
                filetypes=[("キャラクタノードリスト", ".cnl"), ("all", ".*")],
                initialdir=self.target_dir,
                defaultextension=".cnl",
            )
            if name == "":
                # showinfo(text='Error!')
                return None
            self.refresh(level=3)
            self.save_CNL_File(name)
            self.target_dir = name.rsplit("/", 1)[0]

        else:
            showinfo(lavel="ノードが空です")

    def load_node(self):
        name = filedialog.askopenfilename(
            filetypes=[("キャラクタノードリスト", ".cnl"), ("all", ".*")],
            initialdir=self.target_dir,
            defaultextension=".cnl",
        )
        if name == None:
            showinfo(text="Error!")
            return None
        pastnode = self.tree_list[0]
        self.tree_list[0].node = PyPMCA.NODE(
            parts=PyPMCA.PARTS(name="ROOT", joint=["root"]), depth=-1, child=[None]
        )
        self.load_CNL_File(name)
        self.target_dir = name.rsplit("/", 1)[0]
        self.refresh()

    def save_PMD(self, name):
        if self.export2folder:
            dirc = name[0:-4]
            os.mkdir(dirc)
            tmp = name.rsplit("/", 1)
            name = "%s/%s/%s" % (tmp[0], dirc.rsplit("/", 1)[1], tmp[1])

        if PMCA.Write_PMD(0, name.encode(sysenc, "replace")) == 0:
            # テクスチャコピー
            dirc = name.rsplit("/", 1)[0]
            dirc += "/"
            info_data = PMCA.getInfo(0)
            info = PyPMCA.INFO(info_data)
            for i in range(info.data["mat_count"]):
                mat = PyPMCA.MATERIAL(**PMCA.getMat(0, i))
                if mat.tex != "":
                    try:
                        shutil.copy(mat.tex_path, dirc)
                    except IOError:
                        print("コピー失敗:%s" % (mat.tex_path))
                if mat.sph != "":
                    try:
                        shutil.copy(mat.sph_path, dirc)
                    except IOError:
                        print("コピー失敗:%s" % (mat.sph_path))

            toon = PMCA.getToon(0)
            for i, x in enumerate(PMCA.getToonPath(0)):
                toon[i] = toon[i].decode("cp932", "replace")
                print(toon[i], x)
                if toon[i] != "":
                    try:
                        shutil.copy("toon/" + toon[i], dirc)
                    except IOError:
                        try:
                            shutil.copy("parts/" + toon[i], dirc)
                        except IOError:
                            print("コピー失敗:%s" % (toon[i]))

    def dialog_save_PMD(self):
        name = filedialog.asksaveasfilename(
            filetypes=[("Plygon Model Deta(for MMD)", ".pmd"), ("all", ".*")],
            initialdir=self.target_dir,
            defaultextension=".pmd",
        )
        self.refresh()
        self.save_PMD(name)
        self.target_dir = name.rsplit("/", 1)[0]

    def batch_assemble(self):
        names = filedialog.askopenfilename(
            filetypes=[("キャラクタノードリスト", ".cnl"), ("all", ".*")],
            initialdir=self.target_dir,
            defaultextension=".cnl",
            multiple=True,
        )

        self.save_CNL_File("./last.cnl")
        print(type(names))
        if type(names) is str:
            names = names.split(" ")
        for name in names:
            self.load_CNL_File(name)
            self.refresh()

            name_PMD = name
            if name_PMD[-4:] == ".cnl":
                name_PMD = name_PMD[:-4] + ".pmd"
            else:
                name_PMD += ".pmd"
            self.save_PMD(name_PMD)
        self.load_CNL_File("./last.cnl")
        self.refresh()
        self.target_dir = name.rsplit("/", 1)[0]

    def setting_dialog(self):
        root = Toplevel()
        root.transient(self)
        close = QUIT(root)
        frame = Frame(root)
        fancs = PMCA_dialogs.SETTING_DIALOG_FANC(self, root)

        frame.export2folder = Checkbutton(
            root,
            text="個別のフォルダを作成してPMDを保存する",
            variable=fancs.flag_export2folder,
            command=fancs.apply_all,
        )

        frame.export2folder.pack()
        Button(root, text="OK", command=close).pack(padx=5, pady=5, side=RIGHT)
        root.mainloop()
