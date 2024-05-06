from .info import INFO
from .vt import VT
from .material import MATERIAL, TOON
from .bone import BONE, BONE_DISP, BONE_GROUP
from .ik import IK_LIST
from .skin import SKIN
from .rigidbody import RB, JOINT


class PMD:
    def __init__(
        self,
        info: INFO,
        vt: list[VT],
        face: list[tuple[int, int, int]],
        mat: list[MATERIAL],
        bone: list[BONE],
        IK: list[IK_LIST],
        skin: list[SKIN],
        bone_group: list[BONE_GROUP],
        bone_dsp: list[BONE_DISP],
        toon: TOON,
        rb: list[RB],
        joint: list[JOINT],
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
