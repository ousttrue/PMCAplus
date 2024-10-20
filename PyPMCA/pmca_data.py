from typing import Callable
import logging
import pathlib

import PyPMCA
import PMCA

from . import translation
from . import pmca_assets

LOGGER = logging.getLogger(__name__)


class SETTINGS:
    def __init__(self):
        self.export2folder = False


class PmcaData:
    def __init__(self):
        PMCA.Init_PMD()
        LIST = translation.TranslationList.load()
        PMCA.Set_List(
            len(LIST.bone_name_list),
            LIST.bone_name_list,
            LIST.bone_name_english_list,
            len(LIST.skin_name_list),
            LIST.skin_name_list,
            LIST.skin_name_english_list,
            len(LIST.bone_grup_name_list),
            LIST.bone_grup_name_list,
            LIST.bone_grop_name_english_list,
        )

        # assets
        self.assets = pmca_assets.PmcaAssets()
        self.assets.load(pathlib.Path("."))

        # cnl
        node = PyPMCA.NODE(
            parts=PyPMCA.PARTS(name="ROOT", joint=["root"]),
            depth=-1,
            child=[None],
        )

        self.transform_data: list[PyPMCA.MODEL_TRANS_DATA] = [
            PyPMCA.MODEL_TRANS_DATA(scale=1.0, bones=[], props={})
        ]
        self.tree_list = node.create_list()

        self.authors: list[str] = []

        def append_author(author: str):
            for z in self.authors:
                if z == y:
                    return
            else:
                self.authors.append(y)

        self.licenses: list[str] = []

        def append_license(license: str):
            for z in self.licenses:
                if z == y:
                    return

            self.licenses.append(y)

        self.mat_rep = PyPMCA.MAT_REP(append_author, append_license)

        self.cnl_lines: list[str] = []
        last_cnl = pathlib.Path("./last.cnl")
        default_cnl = pathlib.Path("./default.cnl")
        if last_cnl.exists():
            try:
                self.load_CNL_File(last_cnl)
            except:
                print("前回のデータの読み込みに失敗しました")
                self.load_CNL_File(default_cnl)
        else:
            self.load_CNL_File(default_cnl)

        # gui
        self.on_refresh: list[Callable[[float, float, float], None]] = []
        self.parts_entry_k = []
        self.parts_entry_p = []

        self.modelinfo = PyPMCA.MODELINFO()
        self.target_dir = "./model/"
        self.cur_parts = 0
        self.cur_mat = 0
        self.settings = SETTINGS()

        self.tree_entry: list[str] = []
        for x in self.tree_list:
            self.tree_entry.append(x.text)
        self.tree_entry = self.tree_entry[1:]

        self.parts_entry_k: list[str] = []
        self.parts_entry_p: list[PyPMCA.PARTS | str | None] = []
        for x in self.assets.parts_list:
            for y in x.type:
                if y == "root":
                    self.parts_entry_k.append(x.name)
                    self.parts_entry_p.append(x)
                    break

        self.parts_entry_k.append("#外部モデル読み込み")
        self.parts_entry_p.append("load")
        # app.parts_entry_k.append('#None')
        # app.parts_entry_p.append(None)

        self.mat_entry: tuple[list[str], list[str]] = ([], [])

        PMCA.CretateViewerThread()

    def select_tree(self, sel_t: int):
        # sel_t = index + 1
        joint = self.tree_list[sel_t].node.parts.joint[self.tree_list[sel_t].c_num]

        self.parts_entry_k: list[str] = []
        self.parts_entry_p: list[PyPMCA.PARTS | str | None] = []
        for x in self.parts_list:
            for y in x.type:
                if y == joint:
                    self.parts_entry_k.append(x.name)
                    self.parts_entry_p.append(x)
                    break
        self.parts_entry_k.append("#外部モデル読み込み")
        self.parts_entry_p.append("load")
        self.parts_entry_k.append("#None")
        self.parts_entry_p.append(None)

    def select_parts(self, sel_t: int, sel: int) -> str:
        if self.parts_entry_p[sel] == None:  # Noneを選択した場合
            node = None

        elif self.parts_entry_p[sel] == "load":  # 外部モデル読み込み
            path = filedialog.askopenfilename(
                filetypes=[("Plygon Model Deta(for MMD)", ".pmd"), ("all", ".*")],
                defaultextension=".pmd",
            )
            if path != "":
                name = path.split("/")[-1]
                parts = PyPMCA.PARTS(name=name, path=path, props={})
                node = PyPMCA.NODE(
                    parts=parts, depth=self.tree_list[sel_t].node.depth + 1, child=[]
                )
                for x in node.parts.joint:
                    node.child.append(None)
            else:
                node = None

        else:
            # print(self.parts_entry_p[sel].path)
            # print(self.tree_list[sel_t].node.parts.name)

            node = PyPMCA.NODE(
                parts=self.parts_entry_p[sel],
                depth=self.tree_list[sel_t].node.depth + 1,
                child=[],
            )
            p_node = self.tree_list[sel_t].node.child[self.tree_list[sel_t].c_num]

            child_appended = []
            if p_node != None:
                for x in node.parts.joint:
                    node.child.append(None)
                    for j, y in enumerate(p_node.parts.joint):
                        if x == y:
                            for z in child_appended:
                                if z == y:
                                    break
                            else:
                                node.child[-1] = p_node.child[j]
                                child_appended.append(y)
                                break
            else:
                for x in node.parts.joint:
                    node.child.append(None)

            # print(">>", node.parts.name, "\n")
        self.tree_list[sel_t].node.child[self.tree_list[sel_t].c_num] = node
        # self.tree_list[sel_t].node.list_num = sel
        self.refresh(0)

        if node == None:
            return ""
        else:
            return node.parts.comment

    def select_mats(self, sel_t: int) -> str:
        self.cur_mat = sel_t
        return self.mat_rep.mat[self.mat_entry[1][sel_t]].mat.comment

    def select_mats_sel(self, sel: int):
        self.mat_rep.mat[self.mat_entry[1][self.cur_mat]].sel = self.mat_rep.mat[
            self.mat_entry[1][self.cur_mat]
        ].mat.entries[sel]
        self.refresh(level=1)

    def shutdown(self):
        try:
            self.save_CNL_File("./last.cnl")
        except:
            pass

        PMCA.QuitViewerThread()

    def refresh(self, level: int):
        """
        level: 0 full buildF
        """
        assert self.tree_list[0].node
        self.tree_list = self.tree_list[0].node.create_list()
        self.tree_entry = []

        for x in self.tree_list:
            self.tree_entry.append(x.text)
        self.tree_entry = self.tree_entry[1:]

        # モデル組み立て
        PMCA.MODEL_LOCK(1)

        if level < 1:
            LOGGER.info("モデル組立て")

            PMCA.Create_PMD(0)

            x = self.tree_list[0].node
            if x != None:
                x.assemble(0, self)

            PMCA.Copy_PMD(0, 1)
        else:
            PMCA.Copy_PMD(1, 0)

        if level < 2:
            # 材質関連
            print("材質置換")
            self.mat_rep.Get(self.assets.mats_list)
            self.mat_entry = [[], []]
            for v in self.mat_rep.mat.values():
                if v.num >= 0:
                    self.mat_entry[0].append(v.mat.name + "  " + v.sel.name)
                    self.mat_entry[1].append(v.mat.name)
            self.mat_rep.Set()
            PMCA.Copy_PMD(0, 2)
        else:
            PMCA.Copy_PMD(2, 0)

        if level < 3:
            print("体型調整")
            info_data = PMCA.getInfo(0)
            info = PyPMCA.types.INFO(info_data)

            tmpbone = []
            for i in range(info_data["bone_count"]):
                tmp = PMCA.getBone(0, i)
                tmpbone.append(
                    PyPMCA.types.BONE(
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
                        x.pos.x,
                        x.pos.y,
                        x.pos.z,
                    )
                    # print("resize_bone %f %f"%(x.length, x.thick))

            if refbone != None:
                newbone = None
                tmp = PMCA.getBone(0, refbone_index)
                newbone = PyPMCA.types.BONE(
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
                PMCA.Move_Model(0, y.pos.x, y.pos.y, y.pos.z)

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

        w, h, t = PMCA.getWHT(0)
        LOGGER.info("refreshed")
        for callback in self.on_refresh:
            callback(w, h, t)

    def load_CNL_File(self, cnl_file: pathlib.Path):

        self.cnl_lines = cnl_file.read_text(encoding="utf-8-sig").splitlines()

        self.tree_list[0].node.text_to_node(self.assets.parts_list, self.cnl_lines)
        self.mat_rep.text_to_list(self.cnl_lines, self.assets.mats_list)
        self.transform_data[0].text_to_list(self.cnl_lines)

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
