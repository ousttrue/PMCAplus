from .PMCA_types import *
import PMCA  # type: ignore


class INFO:
    def __init__(self, dic):
        self.name = dic["name"].decode("cp932", "replace")
        self.name_eng = dic["name_eng"].decode("cp932", "replace")
        self.comment = dic["comment"].decode("cp932", "replace")
        self.comment_eng = dic["comment_eng"].decode("cp932", "replace")
        self.eng_support = dic["eng_support"]
        self.skin_index = dic["skin_index"]
        self.data = dic


class PMD:
    def __init__(
        self, info, vt, face, mat, bone, IK, skin, bone_group, bone_dsp, toon, rb, joint
    ):
        self.info = info
        self.vt = vt
        self.face = face
        self.mat = mat
        self.bone = bone
        self.IK_list = IK
        self.skin = skin
        self.bone_grp = bone_group
        self.bone_dsp = bone_dsp
        self.toon = toon
        self.rb = rb
        self.joint = joint

    def Set(self, num):
        pass

    @staticmethod
    def Get(num: int):
        info_data = PMCA.getInfo(num)  # type: ignore
        info = INFO(info_data)

        vt = []
        for i in range(info_data["vt_count"]):
            tmp = PMCA.getVt(num, i)
            vt.append(VT(**tmp))

        face = []
        for i in range(info_data["face_count"]):
            face.append(PMCA.getFace(num, i))

        mat = []
        for i in range(info_data["mat_count"]):
            tmp = PMCA.getMat(num, i)
            mat.append(MATERIAL(**tmp))

        bone = []
        for i in range(info_data["bone_count"]):
            tmp = PMCA.getBone(num, i)
            bone.append(
                BONE(
                    tmp["name"],
                    tmp["name_eng"],
                    tmp["parent"],
                    tmp["tail"],
                    tmp["type"],
                    tmp["IK"],
                    tmp["loc"],
                )
            )

        ik = []
        for i in range(info_data["IK_count"]):
            tmp = PMCA.getIK(num, i)
            ik.append(
                IK_LIST(
                    tmp["index"],
                    tmp["tail"],
                    tmp["len"],
                    tmp["ite"],
                    tmp["weight"],
                    tmp["child"],
                )
            )

        skin = []
        for i in range(info_data["skin_count"]):
            tmp = PMCA.getSkin(num, i)

            data = []
            for j in range(tmp["count"]):
                data.append(PMCA.getSkindata(num, i, j))
            skin.append(
                SKIN(tmp["name"], tmp["name_eng"], tmp["count"], tmp["type"], data)
            )

        bone_group = []
        for i in range(info_data["bone_group_count"]):
            tmp = PMCA.getBone_group(num, i)
            bone_group.append(BONE_GROUP(**tmp))

        bone_disp = []
        for i in range(info_data["bone_disp_count"]):
            tmp = PMCA.getBone_disp(num, i)
            bone_disp.append(BONE_DISP(**tmp))

        toon = TOON()
        toon.name = PMCA.getToon(num)
        for i, x in enumerate(toon.name):
            toon.name[i] = x.decode("cp932", "replace")

        toon.path = PMCA.getToonPath(num)
        for i, x in enumerate(toon.path):
            toon.path[i] = x.decode("cp932", "replace")

        rb = []
        for i in range(info_data["rb_count"]):
            tmp = PMCA.getRb(num, i)
            rb.append(RB(**tmp))

        joint = []
        for i in range(info_data["joint_count"]):
            tmp = PMCA.getJoint(num, i)
            joint.append(JOINT(**tmp))

        return PMD(
            info, vt, face, mat, bone, ik, skin, bone_group, bone_disp, toon, rb, joint
        )


def Set_PMD(num, model):
    print("INIT")
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

    print("VT")
    for i, x in enumerate(model.vt):
        PMCA.setVt(
            num, i, x.loc, x.nor, x.uv, x.bone_num[0], x.bone_num[1], x.weight, x.edge
        )

    print("FACE")
    for i, x in enumerate(model.face):
        PMCA.setFace(num, i, x)

    print("MAT")
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

    print("BONE")
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

    print("IK")
    for i, x in enumerate(model.IK_list):
        PMCA.setIK(
            num, i, x.index, x.tail_index, len(x.child), x.iterations, x.weight, x.child
        )

    print("SKIN")
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

    print("GROUP")
    for i, x in enumerate(model.bone_grp):
        PMCA.setBone_group(
            num,
            i,
            bytes(x.name.encode("cp932", "replace")),
            bytes(x.name_eng.encode("cp932", "replace")),
        )
    for i, x in enumerate(model.bone_dsp):
        PMCA.setBone_disp(num, i, x.index, x.group)

    print("TOON")
    tmp = []
    print(model.toon.name)
    for i, x in enumerate(model.toon.name):
        tmp.append(bytes(x.encode("cp932", "replace")))
    PMCA.setToon(num, tmp)
    for i, x in enumerate(model.toon.path):
        tmp.append(bytes(x.encode("cp932", "replace")))
    PMCA.setToonPath(num, tmp)

    print("RBODY")
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

    print("JOINT")
    for i, x in enumerate(model.joint):
        # print(x.name, x.rb, x.loc, x.rot, x.limit, x.spring)
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
