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
        pass
        # auto pre_vt_size = this->vt.size();
        # auto pre_bone_size = this->bone.size();
        # auto pre_skin_disp_size = this->skin_disp.size();
        # auto pre_bone_group_size = this->bone_group.size();
        # auto pre_rbody_size = this->rbody.size();

        # // 頂点
        # this->vt.reserve(this->vt.size() + add->vt.size());
        # for (auto &v : add->vt) {
        #     vt.push_back(v);
        #     // fix bone index
        #     vt.back().bone_num[0] += pre_bone_size;
        #     vt.back().bone_num[1] += pre_bone_size;
        # }

        # // 面頂点
        # this->vt_index.reserve(this->vt_index.size() + add->vt_index.size());
        # for (auto index : add->vt_index) {
        #     // fix index
        #     vt_index.push_back(index + pre_vt_size);
        # }

        # // 材質
        # this->mat.reserve(this->mat.size() + add->mat.size());
        # for (auto &m : add->mat) {
        #     mat.push_back(m);
        # }

        # // ボーン
        # this->bone.reserve(this->bone.size() + add->bone.size());
        # for (auto &b : add->bone) {
        #     bone.push_back(b);
        #     // fix bone index
        #     if (bone.back().PBone_index != USHORT_MAX)
        #     bone.back().PBone_index += pre_bone_size;
        #     if (bone.back().TBone_index != 0)
        #     bone.back().TBone_index += pre_bone_size;
        #     if (bone.back().IKBone_index != 0)
        #     bone.back().IKBone_index += pre_bone_size;
        # }

        # // IKリスト
        # this->IK.reserve(this->IK.size() + add->IK.size());
        # for (auto &ik : add->IK) {
        #     IK.push_back(ik);
        #     IK.back().IKBone_index += pre_bone_size;
        #     IK.back().IKTBone_index += pre_bone_size;
        #     for (size_t k = 0; k < IK.back().IK_chain.size(); k++) {
        #     IK.back().IK_chain[k] += pre_bone_size;
        #     }
        # }

        # // 表情
        # if (add->skin.size() == 0) {
        #     // nothing
        # } else if (this->skin.size() == 0) {
        #     // copy
        #     this->skin.assign(add->skin.begin(), add->skin.end());
        # } else if (this->skin.size() != 0 && add->skin.size() != 0) {
        #     // 0番を合成
        #     skin[0].skin_vt.reserve(this->skin[0].skin_vt.size() +
        #                             add->skin[0].skin_vt.size());
        #     for (auto &skin_vt : add->skin[0].skin_vt) {
        #     this->skin[0].skin_vt.push_back(skin_vt);
        #     // index 補正
        #     this->skin[0].skin_vt.back().index += pre_vt_size;
        #     }

        #     // 1以降追加
        #     this->skin.reserve(this->skin.size() + add->skin.size() - 1);
        #     for (size_t i = 1; i < add->skin.size(); i++) {
        #     skin.push_back(add->skin[i]);
        #     for (size_t k = 0; k < skin.back().skin_vt.size(); k++) {
        #         // index 補正
        #         skin.back().skin_vt[k].index += pre_vt_size;
        #     }
        #     }
        # }

        # // 表情表示
        # skin_disp.reserve(this->skin_disp.size() + add->skin_disp.size());
        # for (auto &sd : add->skin_disp) {
        #     skin_disp.push_back(sd + pre_skin_disp_size);
        # }

        # // ボーン表示
        # bone_group.reserve(this->bone_group.size() + add->bone_group.size());
        # for (auto &bg : add->bone_group) {
        #     bone_group.push_back(bg);
        # }
        # bone_disp.reserve(this->bone_disp.size() + add->bone_disp.size());
        # for (auto &bd : add->bone_disp) {
        #     bone_disp.push_back(bd);
        #     bone_disp.back().index += pre_bone_size;
        #     bone_disp.back().bone_group += pre_bone_group_size;
        # }

        # // 英名
        # this->eng_support = add->eng_support;

        # // 剛体
        # rbody.reserve(this->rbody.size() + add->rbody.size());
        # for (auto &rb : add->rbody) {
        #     rbody.push_back(rb);
        #     rbody.back().bone += pre_bone_group_size;
        # }

        # // ジョイント
        # joint.reserve(this->joint.size() + add->joint.size());
        # for (auto &j : add->joint) {
        #     joint.push_back(j);
        #     joint.back().rbody[0] += pre_rbody_size;
        #     joint.back().rbody[1] += pre_rbody_size;
        # }
