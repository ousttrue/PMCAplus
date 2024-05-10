from typing import Any, NamedTuple
import logging
import sys
import traceback

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


class AssembleContext(NamedTuple):
    script_fin: list[str] = []
    authors: list[str] = []
    licenses: list[str] = []

    def pre_process(self, info_data: pmd_type.InfoData, props: dict[str, str]):
        info = pmd_type.INFO(info_data)
        flag_author = False
        flag_license = False

        line = info.comment.split("\n")
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
                        for y in self.authors:
                            if x == y:
                                break
                        else:
                            self.authors.append(x)

            elif tmp[0] == "License" or tmp[0] == "license" or tmp[0] == "ライセンス":
                if len(tmp) > 1:
                    flag_license = True
                    tmp[1] = tmp[1].replace("　", " ")
                    for x in tmp[1].split(" "):
                        for y in self.licenses:
                            if x == y:
                                break
                        else:
                            self.licenses.append(x)

        if info.name != "":
            if flag_author == False:
                for x in self.authors:
                    if x == "Unknown":
                        break
                else:
                    self.authors.append("Unknown")
            if flag_license == False:
                for x in self.licenses:
                    if x == "Nonfree":
                        break
                else:
                    self.licenses.append("Nonfree")

        if "script_pre" in props:
            for x in props["script_pre"]:
                LOGGER.debug("プレスクリプト実行")
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close

    def post_process(self, props: dict[str, str]):
        if "script_post" in props:
            for x in props["script_post"]:
                argv = x.split()
                fp = open(argv[0], "r", encoding="utf-8-sig")
                script = fp.read()
                exec(script)
                fp.close
        if "script_fin" in props:
            self.script_fin.extend(props["script_fin"])

    def finalize(self):
        for x in self.script_fin:
            argv = x.split()
            with open(argv[0], "r", encoding="utf-8-sig") as fp:
                script = fp.read()
                exec(script)


def assemble(self: PMCA_data.NODE, num: int) -> AssembleContext:
    context = AssembleContext()

    LOGGER.info(f"assemble[{num}]: {self.parts.path}")
    ret = PMCA.Load_PMD(
        num, self.parts.path.encode(sys.getdefaultencoding(), "replace")
    )
    assert ret

    info_data = PMCA.getInfo(0)

    context.pre_process(info_data, self.parts.props)
    context.post_process(self.parts.props)

    for x in self.children:
        if x != None:
            assemble_child(x, num, context)

    PMCA.Sort_PMD(num)
    context.finalize()

    return context


def assemble_child(self: PMCA_data.NODE, num: int, context: AssembleContext):
    LOGGER.info("パーツのパス:%s" % (self.parts.path))

    ret = PMCA.Load_PMD(4, self.parts.path.encode(sys.getdefaultencoding(), "replace"))
    assert ret

    info_data = PMCA.getInfo(4)
    context.pre_process(info_data, self.parts.props)

    PMCA.Add_PMD(num, 4)
    ret = PMCA.Marge_PMD(num)
    assert ret

    context.post_process(self.parts.props)

    for x in self.children:
        if x != None:
            assemble_child(x, num, context)


def _get_material(
    mat_rep: PMCA_data.MAT_REP,
    mats_list: list[PMCA_data.MATS],
    model: pmd_type.PMD | None = None,
    info: pmd_type.INFO | None = None,
    num: int = 0,
):
    if model == None:
        if info == None:
            info_data = PMCA.getInfo(num)
            info = pmd_type.INFO(info_data)
        mat: list[pmd_type.MATERIAL] = []
        for i in range(info.data["mat_count"]):
            tmp = PMCA.getMat(num, i)
            assert tmp
            mat.append(pmd_type.MATERIAL(**tmp))
    else:
        info = model.info
        mat = model.mat

    for x in mat_rep.mat.values():
        x.num = -1

    for i in range(info.data["mat_count"]):
        for x in mats_list:
            if mat[i].tex == x.name and x.name != "":
                if mat_rep.mat.get(mat[i].tex) == None:
                    mat_rep.mat[mat[i].tex] = PMCA_data.MAT_REP_DATA(mat=x, num=i)
                else:
                    mat_rep.mat[mat[i].tex].num = i

                if mat_rep.mat[mat[i].tex].sel == None:
                    mat_rep.mat[mat[i].tex].sel = mat_rep.mat[mat[i].tex].mat.entries[0]


def _set_material(
    context: AssembleContext,
    self: PMCA_data.MAT_REP,
    model: pmd_type.PMD | None = None,
    info: pmd_type.INFO | None = None,
    num: int = 0,
):
    if model == None:
        if info == None:
            info_data = PMCA.getInfo(num)
            assert info_data
            info = pmd_type.INFO(info_data)
        mat: list[pmd_type.MATERIAL] = []
        for i in range(info.data["mat_count"]):
            tmp = PMCA.getMat(num, i)
            mat.append(pmd_type.MATERIAL(**tmp))
    else:
        info = model.info
        mat = model.mat

    for i, x in enumerate(mat):
        if self.mat.get(x.tex) != None:
            rep = self.mat[x.tex].sel
            for k, v in rep.props.items():
                if k == "tex":
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
                    x.spec_col = v
                    for j, y in enumerate(x.spec_col):
                        x.spec_col[j] = float(y)
                elif k == "mirr_rgb":
                    x.mirr_col = v
                    for j, y in enumerate(x.mirr_col):
                        x.mirr_col[j] = float(y)

                elif k == "toon":
                    toon = pmd_type.TOON()
                    toon.path = PMCA.getToonPath(num)
                    toon.name = PMCA.getToon(num)
                    tmp = v[-1].split(" ")
                    tmp[0] = int(tmp[0])
                    toon.path[tmp[0]] = ("toon/" + tmp[1]).encode("cp932", "replace")
                    toon.name[tmp[0]] = tmp[1].encode("cp932", "replace")

                    PMCA.setToon(num, toon.name)
                    PMCA.setToonPath(num, toon.path)
                    x.toon = tmp[0]
                elif k == "author":
                    for y in v[-1].split(" "):
                        for z in context.authors:
                            if z == y:
                                break
                        else:
                            context.authors.append(y)
                elif k == "license":
                    for y in v[-1].split(" "):
                        for z in context.licenses:
                            if z == y:
                                break
                        else:
                            context.licenses.append(y)

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


def refresh(self: PMCA_data.PMCAData):
    PMCA.MODEL_LOCK(1)

    LOGGER.info("モデル組立て(MODEL_LOCK=1)")

    # PMCA.Load_PMD(0, "./testmodels/001.pmd")
    context = assemble(self.tree, 0)

    PMCA.Copy_PMD(0, 1)

    # 材質関連
    LOGGER.info("材質置換")
    _get_material(self.mat_rep, self.mats_list)
    self.mat_entry = ([], [])
    for v in self.mat_rep.mat.values():
        if v.num >= 0:
            self.mat_entry[0].append(v.mat.name + "  " + v.sel.name)
            self.mat_entry[1].append(v.mat.name)
    _set_material(context, self.mat_rep)
    PMCA.Copy_PMD(0, 2)

    LOGGER.info("体型調整")
    info_data = PMCA.getInfo(0)
    # _info = pmd_type.INFO(info_data)

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
            PMCA.Resize_Bone(0, x.name.encode("cp932", "replace"), x.length, x.thick)
            PMCA.Move_Bone(
                0,
                x.name.encode("cp932", "replace"),
                x.pos[0],
                x.pos[1],
                x.pos[2],
            )

    if refbone != None:
        assert refbone_index != None
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

        dy = refbone.loc[1] - newbone.loc[1]
        for x in tmpbone:
            i = x.parent
            count = 0
            while i < info_data["bone_count"] and count < info_data["bone_count"]:
                if tmpbone[i].name == "センター":
                    PMCA.Move_Bone(0, x.name.encode("cp932", "replace"), 0, dy, 0)
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
    PMCA.PMD_view_set(0, "replace")  # テクスチャを変更しない
    PMCA.MODEL_LOCK(0)
    LOGGER.info(f"(MODEL_LOCK=0)")

    w, h, t = PMCA.getWHT(0)
    for callback in self.on_reflesh:
        callback(w, h, t)


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
