import dataclasses
import ctypes

from .types import Vertex, Submesh, RigidBody, Joint
from .info import INFO
from .material import TOON
from .bone import BONE, BONE_DISP, BONE_GROUP
from .ik import IK_LIST
from .skin import SKIN


@dataclasses.dataclass
class PMD:
    info: INFO = dataclasses.field(default_factory=INFO)
    vt: ctypes.Array[Vertex] | None = None
    face: ctypes.Array[ctypes.c_uint16] | None = None
    mat: ctypes.Array[Submesh] | None = None
    bone: list[BONE] = dataclasses.field(default_factory=list)
    IK: list[IK_LIST] = dataclasses.field(default_factory=list)
    skin: list[SKIN] = dataclasses.field(default_factory=list)
    bone_group: list[BONE_GROUP] = dataclasses.field(default_factory=list)
    bone_dsp: list[BONE_DISP] = dataclasses.field(default_factory=list)
    toon: TOON = dataclasses.field(default_factory=TOON)
    rb: ctypes.Array[RigidBody] | None = None
    joint: ctypes.Array[Joint] | None = None

    def add(self, parts: "PMD") -> None:
        """
        port from c++

        bool MODEL::add_PMD(const std::shared_ptr<MODEL> &add)
        """
        pre_vt_size = len(self.vt) if self.vt else 0
        pre_face_size = len(self.face) if self.face else 0
        pre_mat_size = len(self.mat) if self.mat else 0
        pre_bone_size = len(self.bone) if self.bone else 0
        # pre_skin_disp_size = len(self.skin_disp) if self.info.skin_index
        pre_bone_group_size = len(self.bone_group)
        pre_rbody_size = len(self.rb) if self.rb else 0

        # 頂点
        assert parts.vt
        vt = (Vertex * (pre_vt_size + len(parts.vt)))()
        if self.vt:
            for i, v in enumerate(self.vt):
                vt[i] = v
        index = pre_vt_size
        for v in parts.vt:
            vt[index] = v
            # fix bone index
            vt[index].bone0 += pre_bone_size
            vt[index].bone1 += pre_bone_size
            index += 1
        self.vt = vt

        # 面頂点
        assert parts.face
        faces = (ctypes.c_uint16 * (pre_face_size + len(parts.face)))()
        if self.face:
            for i, f in enumerate(self.face):
                faces[i] = f
        index = pre_face_size
        for f in parts.face:
            # fix index
            faces[index] = f + pre_face_size
            index += 1
        parts.face = faces

        # 材質
        assert parts.mat
        mat = (Submesh * (pre_mat_size + len(parts.mat)))()
        if self.mat:
            for i, m in enumerate(self.mat):
                mat[i] = m
        index = pre_mat_size
        for m in parts.mat:
            mat[index] = m
            index += 1
        parts.mat = mat

        # ボーン
        for b in parts.bone:
            self.bone.append(BONE(**dataclasses.asdict(b)))
            # fix bone index
            if self.bone[-1].parent_index != 65535:
                self.bone[-1].parent_index += pre_bone_size
            if self.bone[-1].tail_index != 0:
                self.bone[-1].tail_index += pre_bone_size
            if self.bone[-1].ik != 0:
                self.bone[-1].ik += pre_bone_size

        # IKリスト
        for ik in parts.IK:
            self.IK.append(ik)
            self.IK[-1].index += pre_bone_size
            self.IK[-1].target_index += pre_bone_size
            for k in range(len(self.IK[-1].chain)):
                self.IK[-1].chain[k] += pre_bone_size

        # 表情
        if len(parts.skin) == 0:
            pass
        elif len(self.skin) == 0:
            # copy
            for skin in parts.skin:
                self.skin.append(skin)
        else:
            # 0番を合成
            pass
        #     skin[0].skin_vt.reserve(this->skin[0].skin_vt.size() +
        #                             parts.skin[0].skin_vt.size());
        #     for (auto &skin_vt : parts.skin[0].skin_vt) {
        #     this->skin[0].skin_vt.push_back(skin_vt);
        #     // index 補正
        #     this->skin[0].skin_vt.back().index += pre_vt_size;
        #     }

        #     // 1以降追加
        #     this->skin.reserve(this->skin.size() + parts.skin.size() - 1);
        #     for (size_t i = 1; i < parts.skin.size(); i++) {
        #     skin.push_back(parts.skin[i]);
        #     for (size_t k = 0; k < skin.back().skin_vt.size(); k++) {
        #         // index 補正
        #         skin.back().skin_vt[k].index += pre_vt_size;
        #     }
        #     }
        # }

        # // 表情表示
        # skin_disp.reserve(this->skin_disp.size() + parts.skin_disp.size());
        # for (auto &sd : parts.skin_disp) {
        #     skin_disp.push_back(sd + pre_skin_disp_size);
        # }

        # // ボーン表示
        # bone_group.reserve(this->bone_group.size() + parts.bone_group.size());
        # for (auto &bg : parts.bone_group) {
        #     bone_group.push_back(bg);
        # }
        # bone_disp.reserve(this->bone_disp.size() + parts.bone_disp.size());
        # for (auto &bd : parts.bone_disp) {
        #     bone_disp.push_back(bd);
        #     bone_disp.back().index += pre_bone_size;
        #     bone_disp.back().bone_group += pre_bone_group_size;
        # }

        # // 英名
        # this->eng_support = parts.eng_support;

        # // 剛体
        # rbody.reserve(this->rbody.size() + parts.rbody.size());
        # for (auto &rb : parts.rbody) {
        #     rbody.push_back(rb);
        #     rbody.back().bone += pre_bone_group_size;
        # }

        # // ジョイント
        # joint.reserve(this->joint.size() + parts.joint.size());
        # for (auto &j : parts.joint) {
        #     joint.push_back(j);
        #     joint.back().rbody[0] += pre_rbody_size;
        #     joint.back().rbody[1] += pre_rbody_size;
        # }
