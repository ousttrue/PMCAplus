###C-Pythonデータ変換関連
class INFO:
    def __init__(self, dic):
        self.name = dic["name"].decode("cp932", "replace")
        self.name_eng = dic["name_eng"].decode("cp932", "replace")
        self.comment = dic["comment"].decode("cp932", "replace")
        self.comment_eng = dic["comment_eng"].decode("cp932", "replace")
        self.eng_support = dic["eng_support"]
        self.skin_index = dic["skin_index"]
        self.data = dic


class VT:
    def __init__(
        self,
        loc=[0, 0, 0],
        nor=[0, 0, 0],
        uv=[0, 0],
        bone_num1=0,
        bone_num2=0,
        weight=1,
        edge=0,
    ):
        self.loc = loc
        self.nor = nor
        self.uv = uv
        self.bone_num = [bone_num1, bone_num2]
        self.weight = weight
        self.edge = edge


class MATERIAL:
    def __init__(
        self,
        diff_col,
        alpha,
        spec,
        spec_col,
        mirr_col,
        toon,
        edge,
        face_count,
        tex,
        sph,
        tex_path,
        sph_path,
    ):
        self.diff_col = diff_col
        self.alpha = alpha
        self.spec = spec
        self.spec_col = spec_col
        self.mirr_col = mirr_col
        self.toon = toon
        self.edge = edge
        self.face_count = face_count
        self.tex = tex.decode("cp932", "replace")
        self.sph = sph.decode("cp932", "replace")
        self.tex_path = tex_path.decode("cp932", "replace")
        self.sph_path = sph_path.decode("cp932", "replace")


class BONE:
    def __init__(self, name, name_eng, parent, tail, btype, IK, loc):
        if type(name) == type(b""):
            name = name.decode("cp932", "replace")
        if type(name_eng) == type(b""):
            name_eng = name_eng.decode("cp932", "replace")
        self.name = name
        self.name_eng = name_eng
        self.parent = parent
        self.tail = tail
        self.type = btype
        self.IK = IK
        self.loc = loc


class IK_LIST:
    def __init__(self, index, t_index, length, ite, weight, c_index):
        self.index = index
        self.tail_index = t_index
        self.chain_len = length
        self.iterations = ite
        self.weight = weight
        self.child = c_index


class SKIN_DATA:
    def __init__(self, index, loc):
        self.index = index
        self.loc = loc


class SKIN:
    def __init__(self, name, name_eng, count, t, data):
        self.name = name.decode("cp932", "replace")
        self.name_eng = name_eng.decode("cp932", "replace")
        self.count = count
        self.type = t
        self.data = data


class BONE_GROUP:
    def __init__(self, name="", name_eng=""):
        self.name = name.decode("cp932", "replace")
        self.name_eng = name_eng.decode("cp932", "replace")


class BONE_DISP:
    def __init__(self, index, bone_group):
        self.index = index
        self.group = bone_group


class TOON:
    def __init__(self):
        self.name = None
        self.path = None


class RB:
    def __init__(
        self,
        name="",
        bone=0,
        group=0,
        target=0,
        shape=0,
        size=[1.0, 1.0, 1.0],
        loc=[0.0, 0.0, 0.0],
        rot=[0.0, 0.0, 0.0],
        prop=[0.0, 0.0, 0.0, 0.0, 0.0],
        t=0,
    ):
        self.name = name.decode("cp932", "replace")
        self.bone = bone
        self.group = group
        self.target = target
        self.shape = shape
        self.size = size
        self.loc = loc
        self.rot = rot
        self.mass = prop[0]
        self.damp = prop[1]
        self.rdamp = prop[2]
        self.res = prop[3]
        self.fric = prop[4]
        self.type = t


class JOINT:
    def __init__(
        self,
        name="",
        rbody=[0, 0],
        loc=[0.0, 0.0, 0.0],
        rot=[0.0, 0.0, 0.0],
        limit=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        spring=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    ):
        self.name = name.decode("cp932", "replace")
        self.rb = rbody
        self.loc = loc
        self.rot = rot
        self.limit = limit
        self.spring = spring


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
