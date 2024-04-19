###C-Pythonデータ変換関連


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
