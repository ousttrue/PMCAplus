from typing import Callable, Literal
import logging
import pathlib
import dataclasses

import PMCA

from . import translation
from .parts import PARTS, Joint
from .material import MATS
from . import transform
from . import pmca_assets
from .author_license import AuthorLicense
from . import mat_rep
from . import types


LOGGER = logging.getLogger(__name__)


class SETTINGS:
    def __init__(self):
        self.export2folder = False


@dataclasses.dataclass
class MODELINFO:
    name: str = "PMCAモデル"
    name_l: str = "PMCAモデル"
    comment: str = ""
    name_eng: str = "PMCA model"
    name_l_eng: str = "PMCA generated model"
    comment_eng: str = ""


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
        self.tree_root = PARTS(name="ROOT", child_joints=[Joint("root")])

        self.transform_data: list[transform.MODEL_TRANS_DATA] = [
            transform.MODEL_TRANS_DATA(scale=1.0, bones=[], props={})
        ]
        self.author_license = AuthorLicense()
        self.mat_rep = mat_rep.MAT_REP()

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

        self.modelinfo = MODELINFO()
        # self.target_dir = "./model/"
        self.cur_parts = 0
        self.cur_mat = 0
        self.settings = SETTINGS()

        PMCA.CretateViewerThread()

    def get_tree_entry(self) -> list[str]:
        return [joint.make_entry(i) for i, joint in self.tree_root.traverse()]

    def get_parts_entry(self, joint: str = "root") -> list[str]:
        parts_entry_k: list[str] = []
        for x in self.assets.parts_list:
            for y in x.joint_type:
                if y == joint:
                    parts_entry_k.append(x.name)
                    break
        parts_entry_k.append("#外部モデル読み込み")
        return parts_entry_k

    def get_active_materials(self) -> list[MATS]:
        return [v.mat for v in self.mat_rep.mat.values() if v.num >= 0]

    def get_authors_and_licenses(self) -> str:
        return f"Author : {self.author_license.get_authors()}\nLicense : {self.author_license.get_licenses()}"

    def select_tree(self, sel_t: int) -> tuple[list[str], int]:
        tree_list = self.tree_root.create_list()
        joint = tree_list[sel_t].node.parts.child_joints[tree_list[sel_t].c_num]
        parts_entry_k: list[str] = self.get_parts_entry(joint)
        sel = tree_list[sel_t].node.list_num
        return parts_entry_k, sel

    def select_parts(self, sel_t: int, sel: int) -> str:
        tree_list = self.tree_root.create_list()
        joint = tree_list[sel_t].node.parts.child_joints[tree_list[sel_t].c_num]
        parts_entry_p: list[PARTS | Literal["load"] | None] = []
        for x in self.assets.parts_list:
            for y in x.joint_type:
                if y == joint:
                    parts_entry_p.append(x)
                    break
        parts_entry_p.append("load")
        parts_entry_p.append(None)

        match parts_entry_p[sel]:
            case None:  # Noneを選択した場合
                node = None

            case "load":  # 外部モデル読み込み
                path = filedialog.askopenfilename(
                    filetypes=[("Plygon Model Deta(for MMD)", ".pmd"), ("all", ".*")],
                    defaultextension=".pmd",
                )
                if path != "":
                    name = path.split("/")[-1]
                    parts = PARTS(name=name, path=path, props={})
                    node = NODE(
                        parts=parts,
                        depth=self.tree_list[sel_t].node.depth + 1,
                        child=[],
                    )
                    for x in node.parts.child_joints:
                        node.child.append(None)
                else:
                    node = None

            case PARTS() as parts:
                node = NODE(
                    parts=parts,
                    depth=tree_list[sel_t].node.depth + 1,
                    child=[],
                )
                p_node = tree_list[sel_t].node.child[tree_list[sel_t].c_num]

                child_appended: set[PARTS] = set()
                if p_node != None:
                    for x in node.parts.child_joints:
                        node.child.append(None)
                        for j, y in enumerate(p_node.parts.child_joints):
                            if x == y:
                                if y not in child_appended:
                                    node.child[-1] = p_node.child[j]
                                    child_appended.add(y)
                                    break
                else:
                    for x in node.parts.child_joints:
                        node.child.append(None)

        tree_list[sel_t].node.child[tree_list[sel_t].c_num] = node
        tree_list[sel_t].node.list_num = sel
        self.refresh(0)

        if node == None:
            return ""
        else:
            return node.parts.comment

    def get_mats(self, sel_t: int) -> MATS:
        mat_entry = self.get_active_materials()
        selected = mat_entry[sel_t]
        self.cur_mat = sel_t
        return self.mat_rep.mat[selected.name].mat

    def select_mats_sel(self, sel: int):
        mat_entry = self.get_active_materials()
        rep = self.mat_rep.mat[mat_entry[self.cur_mat].name]
        rep.select(sel)
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
        LOGGER.info("モデル組立て")
        PMCA.MODEL_LOCK(1)

        if level < 1:
            PMCA.Create_PMD(0)
            self.author_license = self.tree_root.assemble(0)
            PMCA.Copy_PMD(0, 1)
        else:
            PMCA.Copy_PMD(1, 0)

        if level < 2:
            # 材質関連
            self.mat_rep.Get(self.assets.mats_list)
            self.mat_rep.Set(self.author_license)
            PMCA.Copy_PMD(0, 2)
        else:
            PMCA.Copy_PMD(2, 0)

        if level < 3:
            info_data = PMCA.getInfo(0)
            # info = PyPMCA.types.INFO.create(info_data)

            tmpbone = []
            for i in range(info_data["bone_count"]):
                tmp = PMCA.getBone(0, i)
                tmpbone.append(
                    types.BONE(
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
                newbone = types.BONE(
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
            PMCA.Set_Name_Comment(
                0,
                self.modelinfo.name.encode("cp932", "replace"),
                (
                    "%s\nAuthor:%s\nLicense:%s\n%s"
                    % (
                        self.modelinfo.name_l,
                        self.author_license.get_authors(),
                        self.author_license.get_licenses(),
                        self.modelinfo.comment,
                    )
                ).encode("cp932", "replace"),
                self.modelinfo.name_eng.encode("cp932", "replace"),
                (
                    "%s\nAuthor:%s\nLicense:%s\n%s"
                    % (
                        self.modelinfo.name_l_eng,
                        self.author_license.get_authors(),
                        self.author_license.get_licenses(),
                        self.modelinfo.comment_eng,
                    )
                ).encode("cp932", "replace"),
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
        LOGGER.info(f"load: {cnl_file}")
        self.cnl_lines = cnl_file.read_text(encoding="utf-8-sig").splitlines()
        self.tree_root.load_cnl(self.cnl_lines, self.assets.parts_list)
        self.mat_rep.load(self.cnl_lines, self.assets.mats_list)
        self.transform_data[0].load_cnl(self.cnl_lines)

    def save_CNL_File(self, name: str) -> None:
        if self.tree_root.child[0] == None:
            return

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
