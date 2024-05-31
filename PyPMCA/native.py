import pathlib
import logging
import sys, shutil
import PMCA  # type: ignore
from . import pmd_type
from . import PMCA_asset
from . import PMCA_cnl
from .assemble import AssembleContext


LOGGER = logging.getLogger(__name__)


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
