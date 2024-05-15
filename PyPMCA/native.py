from typing import Any
import pathlib
import logging
import sys
import traceback

import PMCA  # type: ignore
from . import pmd_type
from . import PMCA_asset
from . import PMCA_cnl
from .assemble import AssembleContext


LOGGER = logging.getLogger(__name__)


class Renderer:
    def __init__(self):
        PMCA.Init_PMD()

    def __enter__(self):
        return self

    def __exit__(self, _exception_type: Any, _exception_value: Any, _traceback: Any):
        if _exception_value:
            traceback.print_tb(_traceback)
            print(_exception_value)
        PMCA.QuitViewerThread()

    def start_thread(self):
        PMCA.CretateViewerThread()


def Set_Name_Comment(
    num: int = 0,
    name: str = "",
    comment: str = "",
    name_eng: str = "",
    comment_eng: str = "",
):
    PMCA.Set_Name_Comment(
        num,
        name.encode("cp932", "replace"),
        comment.encode("cp932", "replace"),
        name_eng.encode("cp932", "replace"),
        comment_eng.encode("cp932", "replace"),
    )


def set_list(
    b: tuple[list[bytes], list[bytes]],
    s: tuple[list[bytes], list[bytes]],
    g: tuple[list[bytes], list[bytes]],
):
    PMCA.Set_List(
        len(b[0]),
        b[0],
        b[1],
        len(s[0]),
        s[0],
        s[1],
        len(g[0]),
        g[0],
        g[1],
    )


def Get(num: int) -> pmd_type.PMD:
    info_data = PMCA.getInfo(num)
    info = pmd_type.INFO(info_data)

    vt: list[pmd_type.VT] = []
    for i in range(info_data["vt_count"]):
        data = PMCA.getVt(num, i)
        assert data
        vt.append(pmd_type.VT(**data))

    face: list[tuple[int, int, int]] = []
    for i in range(info_data["face_count"]):
        data = PMCA.getFace(num, i)
        assert data
        face.append(data)

    mat: list[pmd_type.MATERIAL] = []
    for i in range(info_data["mat_count"]):
        data = PMCA.getMat(num, i)
        assert data
        mat.append(pmd_type.MATERIAL(**data))

    bone: list[pmd_type.BONE] = []
    for i in range(info_data["bone_count"]):
        data = PMCA.getBone(num, i)
        assert data
        bone.append(
            pmd_type.BONE(
                data["name"],
                data["name_eng"],
                data["parent"],
                data["tail"],
                data["type"],
                data["IK"],
                data["loc"],
            )
        )

    ik: list[pmd_type.IK_LIST] = []
    for i in range(info_data["IK_count"]):
        data = PMCA.getIK(num, i)
        assert data
        ik.append(
            pmd_type.IK_LIST(
                data["index"],
                data["tail"],
                data["len"],
                data["ite"],
                data["weight"],
                data["child"],
            )
        )

    skin: list[pmd_type.SKIN] = []
    for i in range(info_data["skin_count"]):
        data = PMCA.getSkin(num, i)
        assert data
        skin_data: list[PMCA.SkinDataData] = []
        for j in range(data["count"]):
            datadata = PMCA.getSkindata(num, i, j)
            assert datadata
            skin_data.append(datadata)
        skin.append(
            pmd_type.SKIN(
                data["name"],
                data["name_eng"],
                data["count"],
                data["type"],
                skin_data,
            )
        )

    bone_group: list[pmd_type.BONE_GROUP] = []
    for i in range(info_data["bone_group_count"]):
        data = PMCA.getBone_group(num, i)
        assert data
        bone_group.append(pmd_type.BONE_GROUP(**data))

    bone_disp: list[pmd_type.BONE_DISP] = []
    for i in range(info_data["bone_disp_count"]):
        data = PMCA.getBone_disp(num, i)
        assert data
        bone_disp.append(pmd_type.BONE_DISP(**data))

    toon_data = PMCA.getToon(num)
    assert toon_data

    toon_path_data = PMCA.getToonPath(num)
    assert toon_path_data

    toon = pmd_type.TOON.from_bytes(toon_data, toon_path_data)

    rb: list[pmd_type.RB] = []
    for i in range(info_data["rb_count"]):
        data = PMCA.getRb(num, i)
        assert data
        rb.append(pmd_type.RB(**data))

    joint: list[pmd_type.JOINT] = []
    for i in range(info_data["joint_count"]):
        data = PMCA.getJoint(num, i)
        assert data
        joint.append(pmd_type.JOINT(**data))

    return pmd_type.PMD(
        info, vt, face, mat, bone, ik, skin, bone_group, bone_disp, toon, rb, joint
    )


def Set_PMD(num: int, model: pmd_type.PMD):
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

    for i, x in enumerate(model.vt):
        PMCA.setVt(
            num, i, x.loc, x.nor, x.uv, x.bone_num0, x.bone_num1, x.weight, x.edge
        )

    for i, x in enumerate(model.face):
        PMCA.setFace(num, i, x)

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
            x.tex.encode("cp932", "replace"),
            x.sph.encode("cp932", "replace"),
            x.tex_path.encode("cp932", "replace"),
            x.sph_path.encode("cp932", "replace"),
        )

    for i, x in enumerate(model.bone):
        PMCA.setBone(
            num,
            i,
            x.name.encode("cp932", "replace"),
            x.name_eng.encode("cp932", "replace"),
            x.parent,
            x.tail,
            x.type,
            x.IK,
            x.loc,
        )

    for i, x in enumerate(model.IK_list):
        PMCA.setIK(
            num,
            i,
            x.index,
            x.target_index,
            len(x.chain),
            x.iterations,
            x.weight,
            x.chain,
        )

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

    for i, x in enumerate(model.bone_grp):
        PMCA.setBone_group(
            num,
            i,
            bytes(x.name.encode("cp932", "replace")),
            bytes(x.name_eng.encode("cp932", "replace")),
        )
    for i, x in enumerate(model.bone_dsp):
        PMCA.setBone_disp(num, i, x.index, x.group)

    PMCA.setToon(num, model.toon.name_cp932())
    PMCA.setToonPath(num, model.toon.path_cp932())

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

    for i, x in enumerate(model.joint):
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


def _assemble(self: PMCA_cnl.NODE, num: int) -> AssembleContext:
    context = AssembleContext()

    LOGGER.info(f"assemble[{num}]: {self.parts.path}")

    # 空モデル
    ret = PMCA.Load_PMD(
        num, self.parts.path.encode(sys.getdefaultencoding(), "replace")
    )
    assert ret

    info_data = PMCA.getInfo(0)

    context.pre_process(info_data, self.parts.props)
    context.post_process(self.parts.props)

    # Parts を合体
    for x in self.children:
        if x.parts:
            _assemble_child(x, num, context)

    PMCA.Sort_PMD(num)
    context.finalize()

    return context


def _assemble_child(self: PMCA_cnl.NODE, num: int, context: AssembleContext):
    assert self.parts
    LOGGER.info("パーツのパス:%s" % (self.parts.path))

    # 4 にロード
    pmd_parts = pmd_type.parse(pathlib.Path(self.parts.path).read_bytes())
    LOGGER.debug(pmd_parts)

    ret = PMCA.Load_PMD(4, self.parts.path.encode(sys.getdefaultencoding(), "replace"))
    assert ret

    info_data = PMCA.getInfo(4)
    context.pre_process(info_data, self.parts.props)

    # 0 に 4 を合成
    PMCA.Add_PMD(num, 4)
    ret = PMCA.Marge_PMD(num)
    assert ret

    context.post_process(self.parts.props)

    # 再帰
    for x in self.children:
        if x.parts:
            _assemble_child(x, num, context)


def _get_material() -> list[pmd_type.MATERIAL]:
    info_data = PMCA.getInfo(0)
    materials: list[pmd_type.MATERIAL] = []
    for i in range(info_data["mat_count"]):
        tmp = PMCA.getMat(0, i)
        assert tmp
        materials.append(pmd_type.MATERIAL(**tmp))
    return materials


def _set_material(
    context: AssembleContext,
    cnl: PMCA_cnl.MAT_REP,
):
    materials: list[pmd_type.MATERIAL] = []
    info_data = PMCA.getInfo(0)
    assert info_data
    for i in range(info_data["mat_count"]):
        tmp = PMCA.getMat(0, i)
        materials.append(pmd_type.MATERIAL(**tmp))

    for i, x in enumerate(materials):
        rep_mat = cnl.mat_map.get(x.tex)
        if rep_mat:
            selected = rep_mat.sel
            selected.apply(x, context)
            PMCA.setMat(
                0,
                i,
                x.diff_col,
                x.alpha,
                x.spec,
                x.spec_col,
                x.mirr_col,
                x.toon,
                x.edge,
                x.face_count,
                x.tex.encode("cp932", "replace"),
                x.sph.encode("cp932", "replace"),
                x.tex_path.encode("cp932", "replace"),
                x.sph_path.encode("cp932", "replace"),
            )


def check_PMD(self) -> None:
    refresh(self, level=3)
    info_data = PMCA.getInfo(0)
    info = pmd.INFO(info_data)
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


def _get_bones(info_data) -> list[pmd_type.BONE]:
    tmpbone: list[pmd_type.BONE] = []
    for i in range(info_data["bone_count"]):
        tmp = PMCA.getBone(0, i)
        assert tmp
        tmpbone.append(
            pmd_type.BONE(
                tmp["name"],
                tmp["name_eng"],
                tmp["parent"],
                tmp["tail"],
                tmp["type"],
                tmp["IK"],
                tmp["loc"],
            )
        )
    return tmpbone


def refresh(data: PMCA_asset.PMCAData, cnl: PMCA_cnl.CnlInfo):
    """
    cnl の変更を MODEL=0 に反映して描画を更新する
    """
    PMCA.MODEL_LOCK(1)
    LOGGER.info("モデル組立て(MODEL_LOCK=1)")
    context = _assemble(cnl.tree, 0)

    # PMCA.Copy_PMD(0, 1)

    LOGGER.info("材質置換")
    materials = _get_material()
    cnl.update_mat_rep(data, materials)
    _set_material(context, cnl.mat_rep)

    # PMCA.Copy_PMD(0, 2)

    LOGGER.info("体型調整")
    info_data = PMCA.getInfo(0)
    tmpbone = _get_bones(info_data)

    refbone = None
    refbone_index = None
    for i, transform_bone in enumerate(tmpbone):
        if transform_bone.name == "右足首":
            refbone = transform_bone
            refbone_index = i
            break

    for transform_data in cnl.transform_data_list:
        PMCA.Resize_Model(0, transform_data.scale)
        for transform_bone in transform_data.bones:
            PMCA.Resize_Bone(
                0,
                transform_bone.name.encode("cp932", "replace"),
                transform_bone.length,
                transform_bone.thick,
            )
            PMCA.Move_Bone(
                0,
                transform_bone.name.encode("cp932", "replace"),
                transform_bone.pos[0],
                transform_bone.pos[1],
                transform_bone.pos[2],
            )

    if refbone:
        assert refbone_index
        newbone = None
        tmp = PMCA.getBone(0, refbone_index)
        assert tmp
        newbone = pmd_type.BONE(
            tmp["name"],
            tmp["name_eng"],
            tmp["parent"],
            tmp["tail"],
            tmp["type"],
            tmp["IK"],
            tmp["loc"],
        )

        # 体型調整による足首の移動量で設置を調整
        dy = refbone.loc[1] - newbone.loc[1]
        for transform_bone in tmpbone:
            i = transform_bone.parent
            count = 0
            while i < info_data["bone_count"] and count < info_data["bone_count"]:
                if tmpbone[i].name == "センター":
                    PMCA.Move_Bone(
                        0, transform_bone.name.encode("cp932", "replace"), 0, dy, 0
                    )
                    break
                i = tmpbone[i].parent
                count += 1

        PMCA.Move_Bone(0, "センター".encode("cp932", "replace"), 0, dy, 0)
        PMCA.Move_Bone(0, "+センター".encode("cp932", "replace"), 0, -dy, 0)

    for transform_data in cnl.transform_data_list:
        PMCA.Move_Model(
            0, transform_data.pos[0], transform_data.pos[1], transform_data.pos[2]
        )

    PMCA.Update_Skin(0)
    PMCA.Adjust_Joints(0)
    # PMCA.Copy_PMD(0, 3)
    PMCA.PMD_view_set(0, "replace")  # テクスチャを変更しない

    PMCA.MODEL_LOCK(0)
    LOGGER.info(f"(MODEL_LOCK=0)")

    w, h, t = PMCA.getWHT(0)
    cnl.on_refresh()


def save_PMD(self, name: str):
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
        info = pmd.INFO(info_data)
        for i in range(info.data["mat_count"]):
            mat = pmd.MATERIAL(**PMCA.getMat(0, i))
            if mat.tex != "":
                try:
                    shutil.copy(mat.tex_path, dirc)
                except IOError:
                    LOGGER.error("コピー失敗:%s" % (mat.tex_path))
            if mat.sph != "":
                try:
                    shutil.copy(mat.sph_path, dirc)
                except IOError:
                    LOGGER.error("コピー失敗:%s" % (mat.sph_path))

        toon = PMCA.getToon(0)
        for i, x in enumerate(PMCA.getToonPath(0)):
            toon[i] = toon[i].decode("cp932", "replace")
            if toon[i] != "":
                try:
                    shutil.copy("toon/" + toon[i], dirc)
                except IOError:
                    try:
                        shutil.copy("parts/" + toon[i], dirc)
                    except IOError:
                        LOGGER.error("コピー失敗:%s" % (toon[i]))
