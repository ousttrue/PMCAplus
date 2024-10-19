from typing import Callable
import os
import PyPMCA
import PMCA
import converter


class SETTINGS:
    def __init__(self):
        self.export2folder = False


class PmcaData:
    def __init__(self):
        PMCA.Init_PMD()
        print("list.txt読み込み")
        LIST = PyPMCA.TranslationList.load()
        PMCA.Set_List(
            len(LIST.b[0]),
            LIST.b[0],
            LIST.b[1],
            len(LIST.s[0]),
            LIST.s[0],
            LIST.s[1],
            len(LIST.g[0]),
            LIST.g[0],
            LIST.g[1],
        )

        self.parts_list = []
        self.mats_list = []  # list of class MATS
        self.tree_entry = []
        self.parts_entry_k = []
        self.parts_entry_p = []
        self.mat_rep = None
        self.transform_data: list[PyPMCA.MODEL_TRANS_DATA] = [
            PyPMCA.MODEL_TRANS_DATA(scale=1.0, bones=[], props={})
        ]
        self.transform_list = []
        self.licenses: list[str] = []
        self.authors: list[str] = []
        self.modelinfo = PyPMCA.MODELINFO()
        self.target_dir = "./model/"
        self.cur_parts = 0
        self.cur_mat = 0
        self.settings = SETTINGS()
        print("登録データ読み込み")
        for x in os.listdir("./"):
            if os.path.isfile(x):
                print(x)

                fp = open(x, "r", encoding="cp932")
                try:
                    lines = fp.read()
                    line = lines.split("\n")
                    line = line[0].replace("\n", "")
                    print('"%s"' % (line))
                    if (
                        line == "PMCA Parts list v1.0"
                        or line == "PMCA Materials list v1.1"
                        or line == "PMCA Materials list v1.0"
                        or line == "PMCA Textures list v1.0"
                        or line == "PMCA Bone_Group list v1.0"
                    ):
                        fp.close()

                        if os.name == "posix":
                            fp = open(x, "w", encoding="cp932")
                            fp.write(lines)
                            fp.close()
                            converter.v1_v2("./converter/PMCA_1.0-2.0converter", [x])
                        elif os.name == "nt":
                            converter.v1_v2(
                                ".\\converter\\PMCA_1.0-2.0converter.exe", [x]
                            )
                    if line == "bone":
                        fp = open(x, "r", encoding="cp932")
                        lines = fp.read()
                        fp.close()

                        fp = open(x, "w", encoding="utf-8")
                        fp.write("PMCA list data v2.0\n")
                        fp.write(lines)
                        fp.close()

                except UnicodeDecodeError:
                    fp.close()
                fp = open(x, "r", encoding="utf-8-sig")
                try:
                    line = fp.readline()
                    print(line)

                    if line == "PMCA Parts list v2.0\n":
                        self.parts_list = PyPMCA.load_partslist(fp, self.parts_list)
                    elif line == "PMCA Materials list v2.0\n":
                        self.mats_list = PyPMCA.load_matslist(fp, self.mats_list)
                    elif line == "PMCA Transform list v2.0\n":
                        self.transform_list = PyPMCA.load_translist(
                            fp, self.transform_list
                        )

                    fp.close()
                except UnicodeDecodeError:
                    fp.close()
                except UnicodeEncodeError:
                    fp.close()

        print("ツリー初期化")
        node = PyPMCA.NODE(
            parts=PyPMCA.PARTS(name="ROOT", joint=["root"]), depth=-1, child=[None]
        )

        self.tree_list = node.create_list()
        self.tree_entry = []
        for x in self.tree_list:
            self.tree_entry.append(x.text)
        self.tree_entry = self.tree_entry[1:]

        self.parts_entry_k = []
        self.parts_entry_p = []
        for x in self.parts_list:
            for y in x.type:
                if y == "root":
                    self.parts_entry_k.append(x.name)
                    self.parts_entry_p.append(x)
                    break

        self.parts_entry_k.append("#外部モデル読み込み")
        self.parts_entry_p.append("load")
        # app.parts_entry_k.append('#None')
        # app.parts_entry_p.append(None)

        print("材質置換設定初期化")
        self.mat_rep = PyPMCA.MAT_REP(app=self)

        try:
            self.load_CNL_File("./last.cnl")
        except:
            print("前回のデータの読み込みに失敗しました")
            self.load_CNL_File("./default.cnl")

        PMCA.CretateViewerThread()

    def shutdown(self):
        try:
            self.save_CNL_File("./last.cnl")
        except:
            pass

        PMCA.QuitViewerThread()

    def raise_update(self):
        for callback in self.update_callbacks:
            callback()

    def refresh(self, level: int):
        """
        level: 0 full buildF
        """
        # sel_t = int(self.tab[0].l_tree.listbox.curselection()[0])
        self.tree_list = self.tree_list[0].node.create_list()
        self.tree_entry = []

        for x in self.tree_list:
            self.tree_entry.append(x.text)
        self.tree_entry = self.tree_entry[1:]
        # self.tab[0].l_tree.set_entry(self.tree_entry, sel=sel_t)

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
            self.mat_rep.Get(self.mats_list)
            # print("1")
            self.mat_entry = [[], []]
            for v in self.mat_rep.mat.values():
                if v.num >= 0:
                    self.mat_entry[0].append(v.mat.name + "  " + v.sel.name)
                    self.mat_entry[1].append(v.mat.name)
            # print("2")
            # self.tab[1].l_tree.set_entry(self.mat_entry[0], sel=self.cur_mat)
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
                    PyPMCA.BONE(
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
                newbone = PyPMCA.BONE(
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

        if level < 4:
            str1 = ""
            str2 = ""
            for x in self.authors:
                str1 += "%s " % (x)
            for x in self.licenses:
                str2 += "%s " % (x)
            # self.modelinfo.name = name
            # self.modelinfo.name_l = name_l
            # self.modelinfo.comment = comment
            PyPMCA.Set_Name_Comment(
                name=self.modelinfo.name,
                comment="%s\nAuthor:%s\nLicense:%s\n%s"
                % (self.modelinfo.name_l, str1, str2, self.modelinfo.comment),
                name_eng=self.modelinfo.name_eng,
                comment_eng="%s\nAuthor:%s\nLicense:%s\n%s"
                % (self.modelinfo.name_l_eng, str1, str2, self.modelinfo.comment_eng),
            )

        if level < 3:
            PMCA.PMD_view_set(0, "replace")  # テクスチャを変更しない
        else:
            PMCA.PMD_view_set(0, "replace")

        PMCA.MODEL_LOCK(0)

        wht = PMCA.getWHT(0)
        # app.tab[2].info_str.set(
        #     "height     = %f\nwidth      = %f\nthickness = %f\n" % (wht[1], wht[0], wht[2])
        # )
        # app.tab[3].frame.text.set("Author : %s\nLicense : %s" % (str1, str2))

        print("Done")

    def load_CNL_File(self, name):
        f = open(name, "r", encoding="utf-8-sig")
        lines = f.read()
        f.close
        lines = lines.split("\n")

        # self.raise_update()

        self.tree_list[0].node.text_to_node(self.parts_list, lines)
        self.mat_rep.text_to_list(lines, self.mats_list)
        self.transform_data[0].text_to_list(lines)
        return True

    def save_CNL_File(self, name):
        if self.tree_list[0].node.child[0] == None:
            return False

        print(f"write {name}")
        lines = []
        lines.append(self.modelinfo.name)
        lines.append(self.modelinfo.name_l)
        lines.append(self.modelinfo.comment)

        lines.append("PARTS")
        lines.extend(self.tree_list[0].node.child[0].node_to_text())
        lines.append("MATERIAL")
        lines.extend(self.mat_rep.list_to_text())
        lines.append("TRANSFORM")
        lines.extend(self.transform_data[0].list_to_text())

        fp = open(name, "w", encoding="utf-8")
        for x in lines:
            fp.write(x + "\n")
        fp.close

        return True
