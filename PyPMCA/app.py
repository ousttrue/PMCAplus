from typing import Callable
import logging
import pathlib
import PMCA
from . import pmd_type
from .pmd_type import resize
from . import PMCA_asset
from . import PMCA_cnl
from . import native
from .assemble import AssembleContext


LOGGER = logging.getLogger(__name__)


class App:
    """
    UI 操作 => パーツ組み換え => 描画更新
    """

    def __init__(self, asset_dir: pathlib.Path, cnl_file: pathlib.Path):
        self.data = PMCA_asset.PMCAData()
        list_txt = self.data.load_asset(asset_dir)
        # if list_txt:
        #     native.set_list(*list_txt)

        self.cnl = PMCA_cnl.CnlInfo()
        self.default_cnl_file = cnl_file
        self.on_assemble: list[Callable[[bytes], None]] = []
        self.cnl_reload()

    def cnl_reload(self):
        self.cnl_load(self.default_cnl_file)

    def cnl_load(self, cnl_file: pathlib.Path) -> None:
        assert cnl_file
        self.cnl.load_CNL_File(cnl_file, self.data)
        self.assemble()

        # pastnode = self.tree_list[0]
        # self.tree_list[0].node = pmd.NODE(
        #     parts=pmd.PARTS(name="ROOT", joint=["root"]), depth=-1, child=[None]
        # )
        # self.load_CNL_File(name)
        # self.refresh()

    def pmd_save(self, pmd_file: pathlib.Path) -> None:
        LOGGER.info(f"{pmd_file}")
        # self.assemble()
        native.save_PMD(pmd_file)

    def cnl_save(self, cnl_file: pathlib.Path) -> None:
        assert cnl_file
        x = self.cnl.tree.children[0]
        if not x:
            LOGGER.error("ノードが空です")
            return

        # self.refresh(level=3)
        self.cnl.save_CNL_File(cnl_file, "name", "name_l", "comment")

    def assemble(self):
        """
        cnl の変更を MODEL=0 に反映して描画を更新する
        """
        LOGGER.info("モデル組立て")
        context = AssembleContext()
        data0 = context.process(self.cnl.tree)
        pmd0 = pmd_type.parse(data0)
        assert pmd0

        LOGGER.info("材質置換")
        self.cnl.update_mat_rep(self.data, [x for x in pmd0.submeshes])
        # native.set_material(context, self.cnl.mat_rep)
        # pmd = pmd_type.parse(PMCA.Get_PMD(0))
        # assert pmd

        for i, x in enumerate(pmd0.submeshes):
            rep_mat = self.cnl.mat_rep.mat_map.get(x.tex)
            if rep_mat:
                selected = rep_mat.sel
                context.apply(x, selected)
                # PMCA.setMat(
                #     0,
                #     i,
                #     x.diffuse_rgb,
                #     x.alpha,
                #     x.specularity,
                #     x.specular_rgb,
                #     x.ambient_rgb,
                #     x.toon_index,
                #     x.flag,
                #     x.index_count,
                #     x.texture_file,
                # )

        data0 = pmd_type.to_bytes(pmd0)
        # PMCA.Set_PMD(0, data0)

        LOGGER.info("体型調整")
        refbone = None
        refbone_index = None
        for i, transform_bone in enumerate(pmd0.bones):
            if transform_bone.name == "右足首":
                refbone = transform_bone
                refbone_index = i
                break

        for transform_data in self.cnl.transform_data_list:
            data0 = resize.Resize_Model(data0, transform_data.scale)
            for transform_bone in transform_data.bones:
                data0 = resize.Resize_Bone(
                    data0,
                    transform_bone.name,
                    transform_bone.length,
                    transform_bone.thick,
                )
                assert data0
                data0 = resize.Move_Bone(
                    data0,
                    transform_bone.name,
                    pmd_type.Float3(*transform_bone.pos),
                )

        if refbone:
            assert refbone_index
            newbone = None
            tmp = pmd0.bones[refbone_index]
            assert tmp
            newbone = pmd_type.Bone(
                tmp.name,
                tmp.name_eng,
                tmp.parent_index,
                tmp.tail_index,
                tmp.bone_type,
                tmp.ik,
                tmp.loc,
            )

            # 体型調整による足首の移動量で設置を調整
            dy = refbone.loc.y - newbone.loc.y
            for transform_bone in pmd0.bones:
                i = transform_bone.parent_index
                count = 0
                while i < len(pmd0.bones) and count < len(pmd0.bones):
                    if pmd0.bones[i].name == "センター":
                        data0 = resize.Move_Bone(
                            data0,
                            transform_bone.name.encode("cp932", "replace"),
                            0,
                            dy,
                            0,
                        )
                        break
                    i = pmd0.bones[i].parent_index
                    count += 1

            data0 = resize.Move_Bone(
                data0, "センター".encode("cp932", "replace"), 0, dy, 0
            )
            data0 = resize.Move_Bone(
                data0, "+センター".encode("cp932", "replace"), 0, -dy, 0
            )

        for transform_data in self.cnl.transform_data_list:
            data0 = resize.Move_Model(
                data0,
                transform_data.pos[0],
                transform_data.pos[1],
                transform_data.pos[2],
            )

        data0 = resize.Update_Skin(data0)
        data0 = resize.Adjust_Joints(data0)

        # w, h, t = PMCA.getWHT(0)
        # self.cnl.on_refresh()
        for callback in self.on_assemble:
            callback(data0)

    # static PyObject *getWHT(PyObject *self, PyObject *args) {
    #   int num;
    #   if (!PyArg_ParseTuple(args, "i", &num))
    #     Py_RETURN_NONE;
    #
    #   auto model = g_model[num];
    #   double min[3] = {0.0, 0.0, 0.0};
    #   double max[3] = {0.0, 0.0, 0.0};
    #   for (size_t i = 0; i < model->vt.size(); i++) {
    #     for (size_t j = 0; j < 3; j++) {
    #       if (model->vt[i].loc[j] > max[j]) {
    #         max[j] = model->vt[i].loc[j];
    #       } else if (model->vt[i].loc[j] < min[j]) {
    #         min[j] = model->vt[i].loc[j];
    #       }
    #     }
    #   }
    #
    #   double wht[3];
    #   for (size_t i = 0; i < 3; i++) {
    #     wht[i] = (max[i] - min[i]) * 8;
    #   }
    #
    #   return Py_BuildValue("(fff)", wht[0], wht[1], wht[2]);
    # }

    def batch_assemble(self, cnl_files: list[pathlib.Path]) -> None:
        # backup
        backup = pathlib.Path("./last.cnl")
        self.cnl_save(backup)

        for cnl_file in cnl_files:
            self.cnl_load(cnl_file)
            self.assemble()
            self.pmd_save(cnl_file.parent / (cnl_file.stem + ".pmd"))

        self.cnl_load(backup)
        self.assemble()

    def init_tf(self) -> None:
        self.cnl.transform_data_list = [
            PMCA_asset.MODEL_TRANS_DATA(
                "",
            )
        ]
        self.assemble()

    def rand_mat(self) -> None:
        self.cnl.mat_rep.rand_mat()
        self.assemble()

    def pmd_format_check(self):
        self.assemble()

        model = PMCA.getInfo(0)
        if len(model["name"]) > 20:
            LOGGER.error(
                f"モデル名の長さが20byteを超えています:{len(model['name'])}byte"
            )
        # if len(model.info.comment) > 256:
        #     errors.append(
        #         "モデルコメントの長さが256byteを超えています:"
        #         + str(len(model.info.comment))
        #         + "byte"
        #     )
        # if len(model.info.name_eng) > 20:
        #     errors.append(
        #         "英語モデル名の長さが20byteを超えています:"
        #         + str(len(model.info.name))
        #         + "byte"
        #     )
        # if len(model.info.comment_eng) > 256:
        #     errors.append(
        #         "英語モデルコメントの長さが256byteを超えています:"
        #         + str(len(model.info.comment))
        #         + "byte"
        #     )
        # for x in model.mat:
        #     if (len(x.tex) + len(x.sph)) > 20:
        #         errors.append(
        #             '材質"'
        #             + x.name
        #             + '"のテクスチャ+スフィアマップの長さが20byteを超えています:'
        #             + str(len(x.tex) + len(x.sph))
        #             + "byte"
        #         )

        # for x in model.bone:
        #     if len(x.name) > 20:
        #         errors.append(
        #             'ボーン"'
        #             + x.name
        #             + '"の名前の長さが20byteを超えています:'
        #             + str(len(x.name))
        #             + "byte"
        #         )
        #     if len(x.name_eng) > 20:
        #         errors.append(
        #             'ボーン"'
        #             + x.name
        #             + '"の英語名の長さが20byteを超えています:'
        #             + str(len(x.name_eng))
        #             + "byte"
        #         )
        #     i = x.parent
        #     count = 0
        #     bone_count = len(model.bone)
        #     while count < bone_count:
        #         if i >= bone_count:
        #             break
        #         i = model.bone[i].parent
        #         count += 1
        #     else:
        #         errors.append("循環依存：%s" % (x.name))

        # for x in model.skin:
        #     if len(x.name) > 20:
        #         errors.append(
        #             '表情"'
        #             + x.name
        #             + '"の名前の長さが20byteを超えています:'
        #             + str(len(x.name))
        #             + "byte"
        #         )
        #     if len(x.name_eng) > 20:
        #         errors.append(
        #             '表情"'
        #             + x.name
        #             + '"の英語名の長さが20byteを超えています:'
        #             + str(len(x.name_eng))
        #             + "byte"
        #         )

        # for x in model.bone_grp:
        #     if len(x.name) > 50:
        #         errors.append(
        #             'ボーングループ"'
        #             + x.name
        #             + '"の名前の長さが50byteを超えています:'
        #             + str(len(x.name))
        #             + "byte"
        #         )
        #     if len(x.name_eng) > 50:
        #         errors.append(
        #             'ボーングループ"'
        #             + x.name
        #             + '"の英語名の長さが50byteを超えています:'
        #             + str(len(x.name_eng))
        #             + "byte"
        #         )

        # for x in model.rb:
        #     if len(x.name) > 20:
        #         errors.append(
        #             '剛体"'
        #             + x.name
        #             + '"の名前の長さが20byteを超えています:'
        #             + str(len(x.name))
        #             + "byte"
        #         )

        # for x in model.joint:
        #     if len(x.name) > 20:
        #         errors.append(
        #             'ジョイント"'
        #             + x.name
        #             + '"の名前の長さが20byteを超えています:'
        #             + str(len(x.name))
        #             + "byte"
        #         )

        # for i, x in enumerate(model.face):
        #     for y in x:
        #         if y >= len(model.vt):
        #             errors.append("面%dの頂点インデックスが不正です:%s" % (i, str(x)))

        # for i, x in enumerate(model.vt):
        #     for y in x.bone_num:
        #         if y >= len(model.bone):
        #             errors.append(
        #                 "頂点%dのボーンインデックスが不正です:%s" % (i, str(x))
        #             )

        # if len(errors) == 0:
        #     errors.append("PMDとして正常に保存できます")

        # root = Toplevel()
        # root.transient(self)
        # close = QUIT(root)
        # frame = Frame(root)
        # frame.log = Text(frame)
        # for x in errors:
        #     frame.log.insert(END, x + "\n")
        # frame.log["state"] = "disabled"
        # frame.yscroll = Scrollbar(frame, orient=VERTICAL, command=frame.log.yview)
        # frame.yscroll.pack(side=RIGHT, fill=Y, expand=0, anchor=E)
        # frame.log["yscrollcommand"] = frame.yscroll.set
        # frame.log.pack(side=RIGHT, fill=BOTH, expand=1)
        # frame.pack(fill=BOTH, expand=1)
        # Button(root, text="OK", command=close).pack()
        # root.mainloop()

    def pmd_overview_check(self):
        self.assemble()
        info_data = PMCA.getInfo(0)
        string = "name :" + info_data["name"].decode("cp932")
        string += "\ncomment :\n" + info_data["comment"].decode("cp932")
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

        # root = Toplevel()
        # root.transient(self)
        # close = QUIT(root)
        # frame = Frame(root)
        # frame.log = Text(frame)
        # frame.log.insert(END, string)
        # frame.log["state"] = "disabled"
        # frame.yscroll = Scrollbar(frame, orient=VERTICAL, command=frame.log.yview)
        # frame.yscroll.pack(side=RIGHT, fill=Y, expand=0, anchor=E)
        # frame.log["yscrollcommand"] = frame.yscroll.set
        # frame.log.pack(side=RIGHT, fill=BOTH, expand=1)
        # frame.pack(fill=BOTH, expand=1)
        # Button(root, text="OK", command=close).pack()
        # root.mainloop()

        LOGGER.info(string)

    def pmd_property_check(self):
        self.assemble()
        model = PMCA.getInfo(0)
        string = "name :" + model["name"].decode("cp932")
        string += "\ncomment :\n" + model["comment"].decode("cp932")
        string += "\n\nname_en :" + model["name_eng"].decode("cp932")
        string += "\ncomment_en :\n" + model["comment_eng"].decode("cp932")
        string += "\n\n頂点数 :" + str(model["vt_count"]) + "\n"
        # for i, x in enumerate(model.vt):
        #     string += str(i) + "\n"
        #     string += "loc:" + str(x.loc) + "\n"
        #     string += "nor:" + str(x.nor) + "\n"
        #     string += "uv:" + str(x.uv) + "\n"
        #     string += "bone:" + str(x.bone_num) + "\n"
        #     string += "weight:" + str(x.weight) + "\n"
        #     string += "edge:" + str(x.edge) + "\n\n"

        string += "\n面数　 :" + str(model["face_count"]) + "\n"
        # for i, x in enumerate(model.face):
        #     string += str(x) + "\n"
        string += "\n材質数 :" + str(model["mat_count"]) + "\n"
        # for i, x in enumerate(model.mat):
        #     string += str(i) + "\n"
        #     string += "diff_col:" + str(x.diff_col) + "\n"
        #     string += "mirr_col:" + str(x.mirr_col) + "\n"
        #     string += "spec_col:" + str(x.spec_col) + "\n"
        #     string += "spec:" + str(x.spec) + "\n"
        #     string += "alpha:" + str(x.alpha) + "\n"
        #     string += "toon:" + str(x.toon) + "\n"
        #     string += "edge:" + str(x.edge) + "\n"
        #     string += "tex:" + x.tex + "\n"
        #     string += "sph:" + x.sph + "\n"
        #     string += "face_count:" + str(x.face_count) + "\n\n"

        string += "\nボーン数 :" + str(model["bone_count"]) + "\n"
        # for i, x in enumerate(model.bone):
        #     string += str(i) + "\n"
        #     string += "name:" + x.name + "\n"
        #     string += "name_en:" + x.name_eng + "\n"
        #     string += "parent:" + str(x.parent) + "\n"
        #     string += "tail:" + str(x.tail) + "\n"
        #     string += "type:" + str(x.type) + "\n"
        #     string += "IK:" + str(x.IK) + "\n"
        #     string += "loc:" + str(x.loc) + "\n\n"

        string += "\nIK数   :" + str(model["IK_count"]) + "\n"
        # for i, x in enumerate(model.IK_list):
        #     string += str(i) + "\n"
        #     string += "index:" + str(x.index) + "\n"
        #     string += "tail_index:" + str(x.tail_index) + "\n"
        #     string += "chain_len:" + str(x.chain_len) + "\n"
        #     string += "iterations:" + str(x.iterations) + "\n"
        #     string += "weight:" + str(x.weight) + "\n"
        #     string += "child:" + str(x.child) + "\n\n"

        string += "\n表情数 :" + str(model["skin_count"]) + "\n"
        # for i, x in enumerate(model.skin):
        #     string += str(i) + "\n"
        #     string += "name:" + x.name + "\n"
        #     string += "name_en:" + x.name_eng + "\n"
        #     string += "count:" + str(x.count) + "\n"
        #     string += "type:" + str(x.type) + "\n\n"
        #     # string += 'data:' + x.data + '\n'

        string += "\nボーングループ数 :" + str(model["bone_group_count"]) + "\n"
        # for i, x in enumerate(model.bone_grp):
        #     string += str(i) + "\n"
        #     string += "name:" + x.name + "\n"
        #     string += "name_en:" + x.name_eng + "\n\n"

        string += "\nボーン表示数 :" + str(model["bone_disp_count"]) + "\n"
        # for i, x in enumerate(model.bone_dsp):
        #     string += str(i) + "\n"
        #     string += "index:" + str(x.index) + "\n"
        #     string += "group:" + str(x.group) + "\n\n"

        # for i, x in enumerate(model.toon.name):
        #     string += "%d %s\n" % (i, x)

        string += "\n\n英語対応 :" + str(model["eng_support"])
        string += "\n\n剛体数 :" + str(model["rb_count"]) + "\n"
        # for i, x in enumerate(model.rb):
        #     string += str(i) + "\n"
        #     string += "name:" + x.name + "\n\n"

        string += "\nジョイント数 :" + str(model["joint_count"]) + "\n"
        # for i, x in enumerate(model.joint):
        #     string += str(i) + "\n"
        #     string += "name:" + x.name + "\n\n"

        # root = Toplevel()
        # root.transient(self)
        # close = QUIT(root)
        # frame = Frame(root)
        # frame.log = Text(frame)
        # frame.log.insert(END, string)
        # frame.log["state"] = "disabled"
        # frame.yscroll = Scrollbar(frame, orient=VERTICAL, command=frame.log.yview)
        # frame.yscroll.pack(side=RIGHT, fill=Y, expand=0, anchor=E)
        # frame.log["yscrollcommand"] = frame.yscroll.set
        # frame.log.pack(side=RIGHT, fill=BOTH, expand=1)
        # frame.pack(fill=BOTH, expand=1)
        # Button(root, text="OK", command=close).pack()
        # root.mainloop()
