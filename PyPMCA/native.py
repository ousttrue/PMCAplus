import pathlib
import logging
import sys, shutil
import PMCA  # type: ignore
from . import pmd_type
from . import PMCA_asset
from . import PMCA_cnl
from .assemble import AssembleContext


LOGGER = logging.getLogger(__name__)


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
        len(model.vertices),
        len(model.indices),
        len(model.submeshes),
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

    for i, x in enumerate(model.vertices):
        PMCA.setVt(
            num, i, x.loc, x.nor, x.uv, x.bone_num0, x.bone_num1, x.weight, x.edge
        )

    for i, x in enumerate(model.indices):
        PMCA.setFace(num, i, x)

    for i, x in enumerate(model.submeshes):
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


def assemble(self: PMCA_cnl.NODE, num: int) -> AssembleContext:
    context = AssembleContext()

    LOGGER.info(f"assemble[{num}]: {self.parts.path if self.parts else 'NO PARTS'}")

    # 空モデル
    ret = PMCA.Load_PMD(
        num, self.parts.path.encode(sys.getdefaultencoding(), "replace")
    )
    assert ret

    pmd0 = pmd_type.PMD.create()

    info_data = PMCA.getInfo(0)

    if self.parts:
        context.pre_process(info_data, self.parts.props)
        context.post_process(self.parts.props)

    # Parts を合体
    for x in self.children:
        if x.parts:
            _assemble_child(pmd0, x, num, context)

    PMCA.Sort_PMD(num)
    context.finalize()

    return context


def _assemble_child(
    root: pmd_type.PMD, current: PMCA_cnl.NODE, num: int, context: AssembleContext
):
    assert current.parts
    LOGGER.info("パーツのパス:%s" % (current.parts.path))

    # 4 にロード
    ret = PMCA.Load_PMD(
        4, current.parts.path.encode(sys.getdefaultencoding(), "replace")
    )
    assert ret

    pmd_parts = pmd_type.parse(pathlib.Path(current.parts.path).read_bytes())
    # LOGGER.debug(pmd_parts)
    if pmd_parts:
        root.add(pmd_parts)

    info_data = PMCA.getInfo(4)
    context.pre_process(info_data, current.parts.props)

    # 0 に 4 を合成
    PMCA.Add_PMD(num, 4)
    ret = PMCA.Marge_PMD(num)
    assert ret

    context.post_process(current.parts.props)

    # 再帰
    for x in current.children:
        if x.parts:
            _assemble_child(root, x, num, context)


def get_material() -> list[pmd_type.MATERIAL]:
    info_data = PMCA.getInfo(0)
    materials: list[pmd_type.MATERIAL] = []
    for i in range(info_data["mat_count"]):
        tmp = PMCA.getMat(0, i)
        assert tmp
        materials.append(pmd_type.MATERIAL(**tmp))
    return materials


def set_material(
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


def get_bones(info_data: pmd_type.InfoData) -> list[pmd_type.BONE]:
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


def save_PMD(name: pathlib.Path):
    name.parent.mkdir(exist_ok=True, parents=True)
    data = PMCA.Get_PMD(0)
    assert data
    name.write_bytes(data)

    dirc = name.parent
    info = PMCA.getInfo(0)
    for i in range(info["mat_count"]):
        mat = pmd_type.MATERIAL(**PMCA.getMat(0, i))
        if mat.tex != "":
            try:
                # テクスチャコピー
                shutil.copy(mat.tex_path, dirc)
            except IOError:
                LOGGER.error("コピー失敗:%s" % (mat.tex_path))
        if mat.sph != "":
            try:
                # テクスチャコピー
                shutil.copy(mat.sph_path, dirc)
            except IOError:
                LOGGER.error("コピー失敗:%s" % (mat.sph_path))

    toon = PMCA.getToon(0)
    for i, x in enumerate(PMCA.getToonPath(0)):
        toon[i] = toon[i].decode("cp932", "replace")
        if toon[i] != "":
            try:
                # テクスチャコピー
                shutil.copy("toon/" + toon[i], dirc)
            except IOError:
                try:
                    # テクスチャコピー
                    shutil.copy("parts/" + toon[i], dirc)
                except IOError:
                    LOGGER.error("コピー失敗:%s" % (toon[i]))
