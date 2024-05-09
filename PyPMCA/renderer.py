from typing import Any
import PMCA  # type: ignore
from .pmd_type.pmd import PMD
from .pmd_type.info import INFO
from .pmd_type.vt import VT
from .pmd_type.material import MATERIAL, TOON
from .pmd_type.bone import BONE, BONE_DISP, BONE_GROUP
from .pmd_type.ik import IK_LIST
from .pmd_type.skin import SKIN
from .pmd_type.rigidbody import RB, JOINT


class Renderer:
    def __init__(self):
        PMCA.Init_PMD()

    def __enter__(self):
        return self

    def __exit__(self, _exception_type: Any, _exception_value: Any, _traceback: Any):
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


def Get(num: int) -> PMD:
    info_data = PMCA.getInfo(num)
    info = INFO(info_data)

    vt: list[VT] = []
    for i in range(info_data["vt_count"]):
        data = PMCA.getVt(num, i)
        assert data
        vt.append(VT(**data))

    face: list[tuple[int, int, int]] = []
    for i in range(info_data["face_count"]):
        data = PMCA.getFace(num, i)
        assert data
        face.append(data)

    mat: list[MATERIAL] = []
    for i in range(info_data["mat_count"]):
        data = PMCA.getMat(num, i)
        assert data
        mat.append(MATERIAL(**data))

    bone: list[BONE] = []
    for i in range(info_data["bone_count"]):
        data = PMCA.getBone(num, i)
        assert data
        bone.append(
            BONE(
                data["name"],
                data["name_eng"],
                data["parent"],
                data["tail"],
                data["type"],
                data["IK"],
                data["loc"],
            )
        )

    ik: list[IK_LIST] = []
    for i in range(info_data["IK_count"]):
        data = PMCA.getIK(num, i)
        assert data
        ik.append(
            IK_LIST(
                data["index"],
                data["tail"],
                data["len"],
                data["ite"],
                data["weight"],
                data["child"],
            )
        )

    skin: list[SKIN] = []
    for i in range(info_data["skin_count"]):
        data = PMCA.getSkin(num, i)
        assert data
        skin_data: list[PMCA.SkinDataData] = []
        for j in range(data["count"]):
            datadata = PMCA.getSkindata(num, i, j)
            assert datadata
            skin_data.append(datadata)
        skin.append(
            SKIN(
                data["name"],
                data["name_eng"],
                data["count"],
                data["type"],
                skin_data,
            )
        )

    bone_group: list[BONE_GROUP] = []
    for i in range(info_data["bone_group_count"]):
        data = PMCA.getBone_group(num, i)
        assert data
        bone_group.append(BONE_GROUP(**data))

    bone_disp: list[BONE_DISP] = []
    for i in range(info_data["bone_disp_count"]):
        data = PMCA.getBone_disp(num, i)
        assert data
        bone_disp.append(BONE_DISP(**data))

    toon_data = PMCA.getToon(num)
    assert toon_data

    toon_path_data = PMCA.getToonPath(num)
    assert toon_path_data

    toon = TOON.from_bytes(toon_data, toon_path_data)

    rb: list[RB] = []
    for i in range(info_data["rb_count"]):
        data = PMCA.getRb(num, i)
        assert data
        rb.append(RB(**data))

    joint: list[JOINT] = []
    for i in range(info_data["joint_count"]):
        data = PMCA.getJoint(num, i)
        assert data
        joint.append(JOINT(**data))

    return PMD(
        info, vt, face, mat, bone, ik, skin, bone_group, bone_disp, toon, rb, joint
    )


def Set_PMD(num: int, model: PMD):
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
            num, i, x.loc, x.nor, x.uv, x.bone_num[0], x.bone_num[1], x.weight, x.edge
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
            bytes(x.tex.encode("cp932", "replace")),
            bytes(x.sph.encode("cp932", "replace")),
            bytes(x.tex_path.encode("cp932", "replace")),
            bytes(x.sph_path.encode("cp932", "replace")),
        )

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

    for i, x in enumerate(model.IK_list):
        PMCA.setIK(
            num, i, x.index, x.tail_index, len(x.child), x.iterations, x.weight, x.child
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

    tmp = []
    for i, x in enumerate(model.toon.name):
        tmp.append(bytes(x.encode("cp932", "replace")))
    PMCA.setToon(num, tmp)
    for i, x in enumerate(model.toon.path):
        tmp.append(bytes(x.encode("cp932", "replace")))
    PMCA.setToonPath(num, tmp)

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
