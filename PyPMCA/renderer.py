from typing import Any
import logging
import sys

import PMCA  # type: ignore
from . import pmd_type
from . import PMCA_data


LOGGER = logging.getLogger(__name__)


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


def assemble(self: PMCA_data.NODE, num: int, app):
    app.script_fin = []
    PMCA.Create_PMD(num)
    PMCA.Load_PMD(num, self.parts.path.encode(sys.getdefaultencoding(), "replace"))
    info_data = PMCA.getInfo(0)
    info = pmd_type.INFO(info_data)
    line = info.comment.split("\n")

    app.authors = []
    app.licenses = []
    if info.name != "":
        app.authors = ["Unknown"]
        app.licenses = ["Nonfree"]

    app.functions = PMCA
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
            tmp[1] = tmp[1].replace("　", " ")
            app.authors = tmp[1].split(" ")

        elif tmp[0] == "License" or tmp[0] == "license" or tmp[0] == "ライセンス":
            tmp[1] = tmp[1].replace("　", " ")
            app.licenses = tmp[1].split(" ")
    LOGGER.debug("パーツのパス:%s" % (self.parts.path))
    for x in self.children:
        if x != None:
            assemble_child(x, num, app)

    PMCA.Sort_PMD(num)

    for x in app.script_fin:
        argv = x.split()
        with open(argv[0], "r", encoding="utf-8-sig") as fp:
            script = fp.read()
            exec(script)


def assemble_child(self: PMCA_data.NODE, num: int, app):
    pmpy = app
    LOGGER.info("パーツのパス:%s" % (self.parts.path))

    PMCA.Create_PMD(4)
    PMCA.Load_PMD(4, self.parts.path.encode(sys.getdefaultencoding(), "replace"))

    info_data = PMCA.getInfo(4)
    info = pmd_type.INFO(info_data)
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
            LOGGER.debug("プレスクリプト実行")
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

    for x in self.children:
        if x != None:
            assemble_child(x, num, app)
